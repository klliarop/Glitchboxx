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


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "../../../"))
PROGRESS_DIR = os.path.join(SRC_DIR, "progress", "http", "level1")
start_dir = os.path.join(CURRENT_DIR, "shared")
DOCKER_COMPOSE_PATH = os.path.join(CURRENT_DIR, "docker-compose.yml")

USERS_FILE = os.path.join(CURRENT_DIR, "state", "users.json")
os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)


class HTTPLevel1User(UserExerciseBase):
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
      
        ip = self.get_container_ip(user_id)

        users.add(user_id)
        self._save_users(users)
        time.sleep(15)  # Less sleep if startup is fast

        return ip  # actual container and IP


    def stop_container_for_user(self, user_id):
        users = self._load_users()
        users.discard(user_id)

        if not users:
            subprocess.run(["docker", "compose", "down"], cwd=CURRENT_DIR, check=True)
        
        self._save_users(users)

    
    # def get_container_ip(self, user_id):
    #     try:
    #         # Step 1: Load the docker-compose.yml
    #         with open(DOCKER_COMPOSE_PATH, 'r') as f:
    #             compose_data = yaml.safe_load(f)

    #         # Step 2: Get network name
    #         networks = compose_data.get('networks', {})
    #         if not networks:
    #             print("No networks defined in docker-compose.yml")
    #             return None

    #         network_name = list(networks.keys())[0]
    #         print(f"[DEBUG] Selected Docker network: {network_name}")

    #         # Step 3: Run `docker network inspect`
    #         result = subprocess.run(
    #             ["docker", "network", "inspect", network_name],
    #             capture_output=True,
    #             text=True,
    #             check=True
    #         )

    #         network_info = json.loads(result.stdout)
    #         ipam_config = network_info[0]["IPAM"]["Config"]

    #         if not ipam_config or "Subnet" not in ipam_config[0]:
    #             print("No Subnet found in network config")
    #             return None

    #         subnet = ipam_config[0]["Subnet"]
    #         print(f"[DEBUG] Network subnet: {subnet}")

    #         # Step 4: Derive gateway manually by replacing last octet
    #         base_ip = subnet.split('/')[0]             # e.g., "172.28.0.0"
    #         parts = base_ip.split('.')                 # ['172', '28', '0', '0']
    #         parts[-1] = '1'                            # replace last part
    #         gateway_ip = '.'.join(parts)               # "172.28.0.1"
    #         print(f"[DEBUG] Derived gateway IP: {gateway_ip}")
    #         return gateway_ip

    #     except Exception as e:
    #         print(f"Error deriving gateway IP: {e}")
    #         return None


    # def get_container_ip(self, user_id):
    #     try:
    #         with open(DOCKER_COMPOSE_PATH, 'r') as f:
    #             compose_data = yaml.safe_load(f)

    #         networks = compose_data.get('networks', {})
    #         network_name = list(networks.keys())[0]
    #         client = docker.from_env()
    #         network = client.networks.get(network_name)

    #         ipam_config = network.attrs.get("IPAM", {}).get("Config", [])
    #         if not ipam_config:
    #             print("No IPAM config found in network.")
    #             return None

    #         gateway_ip = ipam_config[0].get("Gateway")
    #         if not gateway_ip:
    #             # Derive gateway IP from subnet as a fallback
    #             subnet = ipam_config[0].get("Subnet")
    #             if not subnet:
    #                 print("No Subnet found in IPAM config.")
    #                 return None
    #             base_ip = subnet.split('/')[0]
    #             parts = base_ip.split('.')
    #             parts[-1] = '1'
    #             gateway_ip = '.'.join(parts)

    #         print(f"[DEBUG] Gateway IP via SDK: {gateway_ip}")
    #         return gateway_ip

    #     except docker.errors.NotFound:
    #         print("Docker network not found.")
    #         return None
    #     except Exception as e:
    #         print(f"Error using Docker SDK: {e}")
    #         return None



    def get_container_ip(self, user_id):
        try:
            with open(DOCKER_COMPOSE_PATH, 'r') as f:
                network_name = list(yaml.safe_load(f).get('networks', {}).keys())[0]

            ipam = docker.from_env().networks.get(network_name).attrs.get("IPAM", {}).get("Config", [])
            if not ipam:
                return None

            gateway_ip = ipam[0].get("Gateway")
            if not gateway_ip:
                subnet = ipam[0].get("Subnet")
                if not subnet:
                    return None
                parts = subnet.split('/')[0].split('.')
                parts[-1] = '1'
                gateway_ip = '.'.join(parts)

            return gateway_ip

        except docker.errors.NotFound:
            return None
        except Exception:
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

    def get_ftp_credentials(self):
        try:
            with open(DOCKER_COMPOSE_PATH, "r") as file:
                docker_compose = yaml.safe_load(file)
            if not docker_compose or "services" not in docker_compose:
                st.error("Invalid docker-compose.yml structure")
                return None, None
            env_vars = {
                var.split("=")[0]: var.split("=")[1]
                for var in docker_compose["services"]["ftp"]["environment"]
            }
            return env_vars.get("FTP_USER"), env_vars.get("FTP_PASS")
        except FileNotFoundError:
            st.error(f"docker-compose.yml not found at: {DOCKER_COMPOSE_PATH}")
            return None, None
        except Exception as e:
            st.error(f"Error reading docker-compose.yml: {str(e)}")
            return None, None


    # def get_container_for_user(self, user_id):
    #     pass

def main(user_id):
    user = HTTPLevel1User()
    user.set_background('back_http.jpg')

    if not os.path.exists(PROGRESS_DIR):
        os.makedirs(PROGRESS_DIR)

    if "user_progress" not in st.session_state:
        st.session_state.user_progress = user.load_progress(user_id)

    st.markdown(f"<h1 style='color: white;'>The Da Vinci Node</h1>", unsafe_allow_html=True)

    st.markdown("""
        <p style='font-size:20px; color:white;'>
    You’re a freelance art thief, always on the lookout for valuable pieces to enrich your personal collection.
    Your latest intel points to a recently acquired Renaissance painting — possibly a long-lost work by Da Vinci — purchased by a private gallery and now scheduled for delivery.
    The gallery uses outdated tech and the gallery's order and delivery system is vulnerable to eavesdropping so your objective is steal intelligence
    related to this transaction and become a node of the network.<br>
    Your mission: <br>
    - Gather intelligence about the artwork’s order <br>
    - Edit the delivery route and make the painting yours
        </p>
    """, unsafe_allow_html=True)




    # You are a freelancer art thief looking for valuable pieces to enrich your artworks collection. 
    # You have just received intel that a unique painting was recently purchased from a gallery and is scheduled for delivery.
    # Hopefully the gallery's order and delivery system is vulnerable to eavesdropping so your objective is 
    # to intercept the network communications related to this transaction and if possible change the delivery address and reroute it to make it yours!

    ftp_username, ftp_password = user.get_ftp_credentials()

    if st.button("Start Exercise", key="start_exercise"):
        status_placeholder = st.empty()
        status_placeholder.info("This process might take a moment...  ")

        # vpnip= user.get_vpn_ip_for_user(user_id)
        # print(f"[DEBUG] VPN IP for user {user_id}: {vpnip}")
        # ipp= user.get_container_ip(user_id)
        # print(f"[DEBUG] Container IP for user {user_id}: {ipp}")

        st.session_state.user_progress = user.initialize_progress(user_id)
        user.save_progress(user_id, st.session_state.user_progress)
        try:
            container_ip = user.start_container_for_user(user_id)
            vpn_ip = user.get_vpn_ip_for_user(user_id)
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
    user.validate_and_update_step(user_id, 1, "1. How many ports are open on the target?", "*", "2")
    user.validate_and_update_step(user_id, 2, "2. Which service is open in port 21?", "***", "ftp")
    user.validate_and_update_step(user_id, 3, "3. What is the username for FTP login?", "********s", f"{ftp_username}")
    user.validate_and_update_step(user_id, 4, "4. You have a file containing network communication between a client and a server. How is this file named?", "j********.****", "juiceshop.pcap")
    user.validate_and_update_step(user_id, 5, "5. Examining the captured network traffic, what network protocol is being used for this communication?", "****/*.*", "http/1.1")
    user.validate_and_update_step(user_id, 6, "6. What type of request method is typically used by a client to send login credentials to a web server?", "****", "post")
    user.validate_and_update_step(user_id, 7, "7. One of main vulnerabilities of HTTP protocol is that communication is not encrypted.Can you identify the username and password submitted by the client?", "email:password", "jkal56@gmail.com:jk246al!")
    user.validate_and_update_step(user_id, 8, "8. What is the order id of which you want to modify the shipping address?", "*", "1")
    user.validate_and_update_step(user_id, 9, "9. Enter the flag:", "Flag here...", "f364ab19372c428cfd46370")
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



