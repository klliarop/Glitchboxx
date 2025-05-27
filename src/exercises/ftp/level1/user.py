import streamlit as st
import os
import subprocess
import base64
import json
import docker
from docker.errors import NotFound
from exercises.user_base import UserExerciseBase

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "../../../"))
PROGRESS_DIR = os.path.join(SRC_DIR, "progress", "ftp", "level1")
start_dir = os.path.join(CURRENT_DIR, "shared")

class FTPLevel1User(UserExerciseBase):
    def set_background(self, image_file):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        wallpapers_dir = os.path.join(base_dir, "../../../wallpapers")
        image_path = os.path.abspath(os.path.join(wallpapers_dir, image_file))
        try:
            with open(image_path, "rb") as f:
                img_data = f.read()
            b64_encoded = base64.b64encode(img_data).decode()
            style = f"""
                <style>
                .stApp {{
                background-image: url(data:image/png;base64,{b64_encoded});
                background-size: cover;
                background-position: center center;
                background-attachment: fixed;
                }}
                </style>
            """
            st.markdown(style, unsafe_allow_html=True)
        except FileNotFoundError:
            st.error(f"Background image not found at: {image_path}")

    def start_container_for_user(self, user_id):
        client = docker.from_env()
        image = "garethflowers/ftp-server"
        network_name = "ctf_net"
        container_name = f"ftp_level1_{user_id}"
        host_shared_dir = os.path.join(CURRENT_DIR, "shared")
        os.makedirs(host_shared_dir, exist_ok=True)
        os.chmod(host_shared_dir, 0o777)
        try:
            existing = client.containers.get(container_name)
            existing.remove(force=True)
        except NotFound:
            pass
        container = client.containers.run(
            image=image,
            name=container_name,
            detach=True,
            network=network_name,
            runtime="runsc",
            environment={
                "FTP_USER": "anonymous",
                "FTP_PASS": "",
            },
            volumes={
                host_shared_dir: {
                    'bind': '/home/anonymous',
                    'mode': 'rw'
                }
            },
        )
        container.reload()
        ip = container.attrs["NetworkSettings"]["Networks"][network_name]["IPAddress"]
        return container, ip

    def stop_container_for_user(self, user_id):
        client = docker.from_env()
        container_name = f"ftp_level1_{user_id}"
        try:
            container = client.containers.get(container_name)
            container.remove(force=True)
        except docker.errors.NotFound:
            pass

    def get_container_ip(self, user_id):
        client = docker.from_env()
        container_name = f"ftp_level1_{user_id}"
        try:
            container = client.containers.get(container_name)
            return container.attrs["NetworkSettings"]["IPAddress"]
        except NotFound:
            return None


    def add_firewall_rules(self, vpn_ip, container_ip):
        subprocess.run(["sudo","/usr/sbin/iptables", "-I", "DOCKER-USER", "-i", "wg0", "-s", vpn_ip, "-d", container_ip, "-j", "ACCEPT"], check=True)
        subprocess.run(["sudo", "/usr/sbin/iptables", "-I", "DOCKER-USER", "-o", "wg0", "-s", container_ip, "-d", vpn_ip, "-j", "ACCEPT"], check=True)
        print( f"sudo","/usr/sbin/iptables", "-I", "DOCKER-USER", "-i", "wg0", "-s", {vpn_ip}, "-d", {container_ip}, "-j", "ACCEPT")


    def remove_firewall_rules(self, vpn_ip, container_ip):
        subprocess.run(["sudo","/usr/sbin/iptables", "-D", "DOCKER-USER", "-i", "wg0", "-s", vpn_ip, "-d", container_ip, "-j", "ACCEPT"], check=True)
        subprocess.run(["sudo","/usr/sbin/iptables", "-D", "DOCKER-USER", "-o", "wg0", "-s", container_ip, "-d", vpn_ip, "-j", "ACCEPT"], check=True)


    # def add_firewall_rules(self, vpn_ip, container_ip):
    #     subprocess.run(["sudo","/usr/sbin/iptables", "-I", "FORWARD", "-i", "wg0", "-s", vpn_ip, "-d", container_ip, "-j", "ACCEPT"], check=True)
    #     subprocess.run(["sudo", "/usr/sbin/iptables", "-I", "FORWARD", "-o", "wg0", "-s", container_ip, "-d", vpn_ip, "-j", "ACCEPT"], check=True)

    # def remove_firewall_rules(self, vpn_ip, container_ip):
    #     subprocess.run(["sudo","/usr/sbin/iptables", "-D", "FORWARD", "-i", "wg0", "-s", vpn_ip, "-d", container_ip, "-j", "ACCEPT"], check=True)
    #     subprocess.run(["sudo","/usr/sbin/iptables", "-D", "FORWARD", "-o", "wg0", "-s", container_ip, "-d", vpn_ip, "-j", "ACCEPT"], check=True)

    def get_user_progress_file(self, user_id):
        return os.path.join(PROGRESS_DIR, f"{user_id}.json")

    def save_progress(self, user_id, user_progress):
        user_file = self.get_user_progress_file(user_id)
        try:
            with open(user_file, "w") as f:
                json.dump(user_progress, f, indent=4)
        except Exception as e:
            st.error(f"Error saving progress for {user_id}: {e}")

    def initialize_progress(self, user_id):
        progress = {f"step{i}": False for i in range(1, 7)}
        progress["completed"] = False
        return progress

    def load_progress(self, user_id):
        user_file = self.get_user_progress_file(user_id)
        if os.path.exists(user_file):
            try:
                with open(user_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                st.error(f"Error loading progress for {user_id}: {e}")
                return self.initialize_progress(user_id)
        else:
            return self.initialize_progress(user_id)

    def validate_credentials(self, user_id, step_num, question_text, correct_username, correct_password):
        st.markdown(f"<h5 style='color: white;'><br>{question_text}</h5>", unsafe_allow_html=True)
        with st.form(key=f"user_{user_id}_step{step_num}_form"):
            user_input = st.text_input(
                " ",
                placeholder="username:password",
                key=f"user_{user_id}_step{step_num}_input",
                autocomplete="off"
            )
            submit_button = st.form_submit_button("Submit")
            if submit_button:
                if ":" in user_input:
                    username, password = user_input.split(":", 1)
                    username = username.strip()
                    password = password.strip()
                    if username == correct_username and password == correct_password:
                        st.session_state.user_progress = self.load_progress(user_id)
                        st.session_state.user_progress[f"step{step_num}"] = True
                        self.save_progress(user_id, st.session_state.user_progress)
                        st.success("Correct!")
                    else:
                        st.error("Incorrect username or password!")
                else:
                    st.error("Invalid format! Use 'username:password'")

    def validate_and_update_step(self, user_id, step_num, question_text, placeholder, correct_answer):
        st.markdown(f"<h5 style='color: white;'><br>{question_text}</h5>", unsafe_allow_html=True)
        with st.form(key=f"user_{user_id}_step{step_num}_form"):
            col1, col2 = st.columns([2, 1])
            with col1:
                user_answer = st.text_input(" ", placeholder=placeholder, key=f"user_{user_id}_step{step_num}_input", autocomplete="off")
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                submit_button = st.form_submit_button("Submit")
            if submit_button:
                if user_answer.lower().strip() == correct_answer:
                    st.session_state.user_progress[f"step{step_num}"] = True
                    self.save_progress(user_id, st.session_state.user_progress)
                    st.success("Correct!")
                else:
                    st.error("Wrong answer!")

    # def validate_flag_step(self, user_id, step_num, question_text, placeholder, flag_file_relative):
    #     st.markdown(f"<h5 style='color: white;'><br>{question_text}</h5>", unsafe_allow_html=True)
    #     with st.form(key=f"user_{user_id}_step{step_num}_form"):
    #         col1, col2 = st.columns([2, 1])
    #         with col1:
    #             user_answer = st.text_input(" ", placeholder=placeholder, key=f"user_{user_id}_step{step_num}_input", autocomplete="off")
    #         with col2:
    #             st.markdown("<br>", unsafe_allow_html=True)
    #             submit_button = st.form_submit_button("Submit")
    #         if submit_button:
    #             flag_file_path = os.path.join(start_dir, flag_file_relative)
    #             if flag_file_path and os.path.exists(flag_file_path):
    #                 with open(flag_file_path, "r") as file:
    #                     correct_flag = file.read().strip()
    #                 if user_answer.strip() == correct_flag:
    #                     st.session_state.user_progress[f"step{step_num}"] = True
    #                     self.save_progress(user_id, st.session_state.user_progress)
    #                     st.success("Correct!")
    #                 else:
    #                     st.error("Wrong flag!")
    #             else:
    #                 st.error("Flag file not found.")

    def validate_flag_step(self, user_id, step_num, question_text, placeholder, flag_file_name):
        st.markdown(f"<h5 style='color: white;'><br>{question_text}</h5>", unsafe_allow_html=True)
        with st.form(key=f"user_{user_id}_step{step_num}_form"):
            col1, col2 = st.columns([2, 1])
            with col1:
                user_answer = st.text_input(" ", placeholder=placeholder, key=f"user_{user_id}_step{step_num}_input", autocomplete="off")
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                submit_button = st.form_submit_button("Submit")
            if submit_button:
                # Search for the flag file recursively in the shared directory
                found_flag_path = None
                for root, dirs, files in os.walk(start_dir):
                    if flag_file_name in files:
                        found_flag_path = os.path.join(root, flag_file_name)
                        break

                if found_flag_path:
                    with open(found_flag_path, "r") as file:
                        correct_flag = file.read().strip()
                    if user_answer.strip() == correct_flag:
                        st.session_state.user_progress[f"step{step_num}"] = True
                        self.save_progress(user_id, st.session_state.user_progress)
                        st.success("Correct!")
                    else:
                        st.error("Wrong flag!")
                else:
                    st.error("Flag file not found.")


    def get_vpn_ip_for_user(self, user_id, config_path="/etc/wireguard/wg0.conf"):
        vpn_map = {}
        current_user_id = None
        try:
            with open(config_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("# user with id:"):
                        current_user_id = line.split(":")[1].strip()
                    elif line.startswith("AllowedIPs") and current_user_id:
                        ip = line.split("=")[1].strip().split("/")[0]
                        vpn_map[current_user_id] = ip
                        current_user_id = None
            return vpn_map.get(user_id)
        except Exception as e:
            print(f"Error reading VPN config: {e}")
            return None

def main(user_id):
    user = FTPLevel1User()
    user.set_background('back_ftp.jpg')

    if not os.path.exists(PROGRESS_DIR):
        os.makedirs(PROGRESS_DIR)

    if "user_progress" not in st.session_state:
        st.session_state.user_progress = user.load_progress(user_id)

    st.markdown(f"<h1 style='color: white;'>Dark Contract </h1>", unsafe_allow_html=True)
    st.markdown("""<p style='font-size:20px; color:white;'>
        You are an unethical hacker and you are hired by “Raymond Reddington” for a job. Your goal is to steal a confidential file 
        from “NeuroGen Biotech”, which contains the DNA vaccine and give it to the competitor research center before it is launched.
        <br> Your mission is to:
        <br> - Enumerate open ports of the target and find the way to enter
        <br> - Search for the flag!</p>""", unsafe_allow_html=True)

    if st.button("Start Exercise", key="start_exercise"):
        st.session_state.user_progress = user.initialize_progress(user_id)
        user.save_progress(user_id, st.session_state.user_progress)
        try:
            container, container_ip = user.start_container_for_user(user_id)
            vpn_ip = user.get_vpn_ip_for_user(user_id)
            if not vpn_ip:
                st.error("VPN IP for your session could not be found. Contact admin.")
                return
            st.session_state["container_ip"] = container_ip
            st.session_state["vpn_ip"] = vpn_ip
            user.add_firewall_rules(vpn_ip, container_ip)
            st.success(f"Server up and isolated for {vpn_ip} to {container_ip}")
        except subprocess.CalledProcessError as e:
            st.error(f"Error restarting Docker container: {e}")

    if "container_ip" in st.session_state:
        st.markdown(f"""
        <div style="
            background-color: #000000;
            padding: 20px;
            border-radius: 8px;
            color: #00ff00;
            font-family: 'Courier New', monospace;
            font-size: 20px;
            box-shadow: 0 0 10px #00ff00;
            margin-top: 30px;
        ">
            Server is up at: <code style="
                background-color: #111;
                padding: 2px 6px;
                border-radius: 4px;
                color: #00ff00;
                user-select: all;
            ">{st.session_state.container_ip}</code><br>
        </div>
        """, unsafe_allow_html=True)

    if "container_ip" not in st.session_state:
        st.session_state.container_ip = "none - Press start exercise to continue"

    user.validate_and_update_step(user_id, 1, "1.Which tool should you use to scan for open ports on the target?", "***p", "nmap")
    user.validate_and_update_step(user_id, 2, "2.At what port does the FTP appear?", "**", "21")
    user.validate_and_update_step(user_id, 3, "3.With what command can you connect to the FTP server?", "*** ***.*.*.*", f"ftp {st.session_state.container_ip}")
    user.validate_and_update_step(user_id, 4, "4.What is the default username for FTP login?", "********s", "anonymous")
    user.validate_and_update_step(user_id, 5, "5.What command can you use to download files in ftp?", "***", "get")
    user.validate_flag_step(user_id, 6, "7. Enter the flag", "FLAG{...}", "flag.txt")

    all_steps_completed = all(st.session_state.user_progress.get(f"step{i}", False) for i in range(1, 7))

    if all_steps_completed and not st.session_state.user_progress["completed"]:
        st.session_state.user_progress["completed"] = True
        user.save_progress(user_id, st.session_state.user_progress)

    if st.session_state.user_progress["completed"]:
        st.markdown("""
            <h1 style='text-align: center; color: green; font-size: 50px;'> CONGRATULATIONS! </h1>
            <p style='text-align: center; font-size: 24px;'>You completed this exercise!</p>
        """, unsafe_allow_html=True)

    if st.button("Stop Exercise"):
        try:
            vpn_ip = st.session_state.get("vpn_ip") or user.get_vpn_ip_for_user(user_id)
            container_ip = st.session_state.get("container_ip")
            if not vpn_ip or not container_ip:
                st.warning("No active exercise to stop.")
                return
            try:
                user.remove_firewall_rules(vpn_ip, container_ip)
            except subprocess.CalledProcessError as e:
                print(f"[DEBUG] Failed to remove firewall rules: {e}")
            try:
                user.stop_container_for_user(user_id)
            except Exception as e:
                print(f"[DEBUG] Failed to stop container: {e}")
            st.success("Exercise stopped.")
        except Exception as e:
            print(f"[DEBUG] Unhandled error during exercise stop: {e}")
            st.error("Something went wrong while stopping the exercise. Contact admin.")
        st.session_state.user_progress = user.initialize_progress(user_id)
        user.save_progress(user_id, st.session_state.user_progress)
        user_progress_file = user.get_user_progress_file(user_id)
        if os.path.exists(user_progress_file):
            os.remove(user_progress_file)

if __name__ == "__main__":
    main("test_user")



