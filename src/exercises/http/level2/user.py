import streamlit as st
import os
import subprocess
import time
import base64
import yaml
import json
import docker
from docker.errors import NotFound
from exercises.user_base import UserExerciseBase
import shutil


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "../../../"))
PROGRESS_DIR = os.path.join(SRC_DIR, "progress", "http", "level2")
start_dir = os.path.join(CURRENT_DIR, "shared")
DOCKER_COMPOSE_PATH = os.path.join(CURRENT_DIR, "docker-compose.yml")

USERS_FILE = os.path.join(CURRENT_DIR, "state", "users.json")
os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)


class HTTPLevel2User(UserExerciseBase):
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
        users = self._load_users()

        if not users:
            subprocess.run(["docker", "compose", "build"], cwd=CURRENT_DIR, check=True)
            subprocess.run(["docker", "compose", "up", "-d"], cwd=CURRENT_DIR, check=True)
      
       # ip = self.get_container_ip(user_id)

        users.add(user_id)
        self._save_users(users)
        time.sleep(15)  # Less sleep if startup is fast

        return '172.29.0.1'  # actual container and IP


    def stop_container_for_user(self, user_id):
        users = self._load_users()
        users.discard(user_id)

        if not users:
            subprocess.run(["docker", "compose", "down"], cwd=CURRENT_DIR, check=True)
        

        self._save_users(users)



    def get_container_ip(self, user_id):
        try:
            # Step 1: Load the docker-compose.yml
            with open(DOCKER_COMPOSE_PATH, 'r') as f:
                compose_data = yaml.safe_load(f)

            # Step 2: Try to get network name from top-level networks
            network_name = None
            networks = compose_data.get('networks', {})
            if networks:
                network_name = list(networks.keys())[0]
            else:
                # Fallback: try to find network from services section
                services = compose_data.get('services', {})
                for service in services.values():
                    service_networks = service.get('networks')
                    if service_networks:
                        if isinstance(service_networks, list):
                            network_name = service_networks[0]
                        elif isinstance(service_networks, dict):
                            network_name = list(service_networks.keys())[0]
                        break

            if not network_name:
                print("No network found in docker-compose.yml")
                return None

            # Step 3: Use docker network inspect to get gateway
            result = subprocess.run(
                ["docker", "network", "inspect", network_name],
                capture_output=True,
                text=True,
                check=True
            )
            network_info = json.loads(result.stdout)
            return network_info[0]["IPAM"]["Config"][0].get("Gateway")

        except Exception as e:
            print(f"Error getting network gateway: {e}")
            return None




    def add_firewall_rules(self, vpn_ip, container_ip):
        subprocess.run(["sudo","/usr/sbin/iptables", "-I", "DOCKER-USER", "-i", "wg0", "-s", vpn_ip, "-d", container_ip, "-j", "ACCEPT"], check=True)
        subprocess.run(["sudo", "/usr/sbin/iptables", "-I", "DOCKER-USER", "-o", "wg0", "-s", container_ip, "-d", vpn_ip, "-j", "ACCEPT"], check=True)
        subprocess.run(["sudo", "/usr/sbin/iptables", "-I", "INPUT", "-i", "wg0", "-s", vpn_ip, "-d", container_ip, "-j", "ACCEPT"], check=True)
        subprocess.run(["sudo", "/usr/sbin/iptables", "-t", "raw", "-I", "PREROUTING", "-i", "wg0", "-s", vpn_ip, "-d", container_ip, "-j", "ACCEPT"], check=True)

    def remove_firewall_rules(self, vpn_ip, container_ip):
        subprocess.run(["sudo", "/usr/sbin/iptables","-D", "DOCKER-USER", "-i", "wg0", "-s", vpn_ip, "-d", container_ip, "-j", "ACCEPT"], check=True)
        subprocess.run(["sudo", "/usr/sbin/iptables","-D", "DOCKER-USER", "-o", "wg0", "-s", container_ip, "-d", vpn_ip, "-j", "ACCEPT"],check=True)
        subprocess.run(["sudo", "/usr/sbin/iptables","-D", "INPUT", "-i", "wg0", "-s", vpn_ip, "-d", container_ip, "-j", "ACCEPT"],check=True)
        subprocess.run(["sudo", "/usr/sbin/iptables","-t", "raw", "-D", "PREROUTING", "-i", "wg0", "-s", vpn_ip, "-d", container_ip, "-j", "ACCEPT"],check=True)
        subprocess.run(["sudo", "/usr/sbin/iptables","-D", "FORWARD", "-i", "wg0", "-s", vpn_ip, "-d", container_ip, "-j", "ACCEPT"],check=True)
        subprocess.run(["sudo", "/usr/sbin/iptables", "-D", "FORWARD", "-o", "wg0", "-s", container_ip, "-d", vpn_ip, "-j", "ACCEPT"],check=True)
    

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
        progress = {f"step{i}": False for i in range(1, 10)}
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


    def validate_flag_step(self, user_id, step_num, question_text, placeholder, flag_file_relative):
        pass

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

    # Helper functions for managing the list of currently active users 
    def _load_users(self):
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r") as f:
                return set(json.load(f))
        return set()

    def _save_users(self, users):
        with open(USERS_FILE, "w") as f:
            json.dump(list(users), f)


    # def get_container_for_user(self, user_id):
    #     pass




def main(user_id):
    user = HTTPLevel2User()
    user.set_background('back_http.jpg')

    if not os.path.exists(PROGRESS_DIR):
        os.makedirs(PROGRESS_DIR)

    if "user_progress" not in st.session_state:
        st.session_state.user_progress = user.load_progress(user_id)

    st.markdown(f"<h1 style='color: white;'>BankSploit</h1>", unsafe_allow_html=True)

    # st.markdown("""
    #     <p style='font-size:20px; color:white;'>
    #     You have successfully entered a restricted internal network believed 
    #     to host a bank’s private servers. The bank's defenses are outdated exposing 
    #     sensitive data in plaintext. Your mission is to intercept communication 
    #     between clients and the server and find some way to steal money. 
    #     </p>
    # """, unsafe_allow_html=True)
#generational wealth, one packet at a time. ......retirement from a life of crime.

    st.markdown("""
        <p style='font-size:20px; color:white;'>
        You’ve infiltrated a private network long rumored to launder high-value Renaissance artworks — including a few allegedly painted by Da Vinci himself —
        through "state-of-the-art" banking channels that haven’t been updated since the Renaissance. Their defenses are outdated and unencrypted and sensitive data flows through in plaintext.
        <br> Your mission: <br>
        - Intercept communications between clients and the bank’s server to retrieve exploitable information<br>
        - Enter the system and reroute funds to secure your spot in the history books (next to Da Vinci).
        </p>
    """, unsafe_allow_html=True)


    if st.button("Start Exercise", key="start_exercise"):
        status_placeholder = st.empty()
        status_placeholder.info("This process might take a moment...  ")

        st.session_state.user_progress = user.initialize_progress(user_id)
        user.save_progress(user_id, st.session_state.user_progress)
        try:
            container_ip = user.start_container_for_user(user_id)
            vpn_ip = user.get_vpn_ip_for_user(user_id)
            print(vpn_ip, container_ip)
            if not vpn_ip:
                st.error("VPN IP for your session could not be found. Contact admin.")
                return
            st.session_state["container_ip"] = container_ip
            st.session_state["vpn_ip"] = vpn_ip
            user.add_firewall_rules(vpn_ip, container_ip)
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


    # Question and answer validation for each step with placeholders
    user.validate_and_update_step(user_id, 1, "1. How many open ports are on the server?", "*", "2")
    user.validate_and_update_step(user_id, 2, "2. What tool allows you to capture raw network packets, visualize traffic flow in real time, and apply filters to analyze protocols?", "w********", "wireshark")
    user.validate_and_update_step(user_id, 3, "3. What network protocol is used together with HTTP to provide reliable communication and handle acknowledgments, as seen in the server's communication?", "***", "tcp")
    user.validate_and_update_step(user_id, 4, "4. What term or code in communication indicates the acknowledgment of received packets?", "***", "ack")
    user.validate_and_update_step(user_id, 5, "5. Based on the open port analysis, what filter can you apply to isolate traffic to the bank's service?", "***.**** == ****", "tcp.port == 8080")
    user.validate_and_update_step(user_id, 6, "6. What HTTP status code indicates that a login attempt was unauthorized?", "*** U***********", "401 unauthorized")
    user.validate_and_update_step(user_id, 7, "7. What type of HTTP methods are being used in this network?", "***,****", "get,post")
    user.validate_and_update_step(user_id, 8, "8. What is the name of the bank you entered?", "**********", "septemtica")
    user.validate_and_update_step(user_id, 9, "9. If you made a successful transfer, enter the flag:5", "Flag here...", "7a5f8d3e1c9b24680a42d59")
   
    # --- Completion Check and Message ---

    all_steps_completed = all(st.session_state.user_progress.get(f"step{i}", False) for i in range(1, 10))

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

