# --- Imports ---
import streamlit as st  # For web UI
import os  # For file and path operations
import subprocess  # To run shell commands (docker, iptables)
import time  # For sleep/delay
import base64  # For encoding images to base64
import yaml  # For parsing YAML files (docker-compose)
import json  # For JSON config and progress files
import docker  # Docker SDK for Python
from docker.errors import NotFound  # Exception for missing Docker objects
from exercises.user_base import UserExerciseBase  # Base class for exercises
from pathlib import Path  # For path manipulations
from jinja2 import Template  # For templating docker-compose files

# --- Path and Directory Setup ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))  # Current file's directory
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "../../../"))  # Project root
PROGRESS_DIR = os.path.join(SRC_DIR, "progress", "http", "level2")  # Progress files directory

# --- Main Exercise Class ---
class HTTPLevel2User(UserExerciseBase):
    # Set Streamlit background image using a file from wallpapers directory
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

    # Start a Docker container for a user, using a rendered docker-compose template
    def start_container_for_user(self, user_id):
        base_dir = os.path.dirname(__file__)
        # Path to Jinja2 docker-compose template
        template_path = os.path.join(base_dir, "../../templates/http_docker_compose_2.j2")
        # Path for the user's docker-compose file
        compose_path = os.path.join(base_dir, f"docker-compose-{user_id}.yml")

        # Load admin config (FTP/DB credentials, etc.)
        config_path = Path(base_dir).parent.parent / "templates/json_configs/http_level2.json"
        with open(config_path) as f:
            config = json.load(f)

        # Find a free subnet and assign IPs for services
        subnet = self._find_free_subnet()
        print("DEBUG: subnet value:", subnet, type(subnet))
        base_ip = subnet.split('/')[0]  # e.g., "172.28.5.0"
        print(base_ip)
        parts = base_ip.split('.')
        web_ip = f"{parts[0]}.{parts[1]}.{parts[2]}.10"
        db_ip = f"{parts[0]}.{parts[1]}.{parts[2]}.11"
        ftp_ip = f"{parts[0]}.{parts[1]}.{parts[2]}.12"
        traffic_ip = f"{parts[0]}.{parts[1]}.{parts[2]}.13"
        gateway_ip = f"{parts[0]}.{parts[1]}.{parts[2]}.1"

        # Render docker-compose.yml for this user using the template
        with open(template_path) as f:
            template = Template(f.read())
        rendered = template.render(
            user_id=user_id,
            subnet=subnet,
            web_ip=web_ip,
            db_ip=db_ip,
            ftp_ip=ftp_ip,
            traffic_ip=traffic_ip,
            gateway_ip=gateway_ip,
            db_user=config.get("db_user", "ctfuser"),
            db_pass=config.get("db_pass", "ctfpass"),
            ftp_user=config.get("ftp_user", "ftpuser"),
            ftp_pass=config.get("ftp_pass", "ftppass"),
            http_port=config.get("http_port", "8080"),
            ftp_port=config.get("ftp_port", "21")
        )

        print("Gateway IP:", gateway_ip)

        # Write the rendered docker-compose file
        with open(compose_path, "w") as f:
            f.write(rendered)

        # Stop any existing containers for this user (ignore errors)
        subprocess.run([
            "docker", "compose", "-p", f"level2_{user_id}", "-f", compose_path, "down", "-v"
        ], check=False)
        # Start up the containers
        subprocess.run([
            "docker", "compose", "-p", f"level2_{user_id}", "-f", compose_path, "up", "-d"
        ], check=True)

        time.sleep(20)  # Wait for containers to be ready
        
        # Return the gateway IP and subnet for this user's container
        return gateway_ip, subnet

    # Stop and remove the user's Docker container and compose file
    def stop_container_for_user(self, user_id):
        base_dir = os.path.dirname(__file__)
        compose_path = os.path.join(base_dir, f"docker-compose-{user_id}.yml")
        try:
            subprocess.run(["docker", "compose","-p", f"level2_{user_id}","-f", compose_path,"down", "-v"], check=True)
            os.remove(compose_path)
        except subprocess.CalledProcessError as e:
            pass

    # Get the subnet for the user's Docker network
    def get_container_ip(self, user_id):
        try:
            compose_path = os.path.join(os.path.dirname(__file__), f"docker-compose-{user_id}.yml")

            with open(compose_path, 'r') as f:
                compose_data = yaml.safe_load(f)

            # Extract the network name (first one if multiple)
            network_name = list(compose_data.get('networks', {}).keys())[0]

            # Compose project name for this user
            project_name = f"level2_{user_id}"
            full_network_name = f"{project_name}_{network_name}"

            docker_client = docker.from_env()
            network = docker_client.networks.get(full_network_name)
            ipam_config = network.attrs.get("IPAM", {}).get("Config", [])

            if not ipam_config:
                return None

            subnet = ipam_config[0].get("Subnet")
            gateway_ip = ipam_config[0].get("Gateway")

            if not gateway_ip and subnet:
                parts = subnet.split('/')[0].split('.')
                parts[-1] = '1'
                gateway_ip = '.'.join(parts)

            print(f"[DEBUG] Network info for {user_id} → Subnet: {subnet}, Gateway: {gateway_ip}")
            return subnet

        except docker.errors.NotFound:
            print(f"[ERROR] Network not found for user {user_id}")
            return None
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            return None

    # Add iptables rules to allow VPN IP <-> container IP communication
    def add_firewall_rules(self, vpn_ip, container_ip):
        print(f"Adding precise firewall rules for {vpn_ip} → {container_ip}")
        # Allow VPN IP to container IP
        subprocess.run(["sudo", "/usr/sbin/iptables", "-I", "DOCKER-USER", "1","-i", "wg0", "-s", vpn_ip, "-d", container_ip, "-j", "ACCEPT"], check=True)
        # Allow return traffic from container to VPN IP
        subprocess.run(["sudo", "/usr/sbin/iptables", "-I", "DOCKER-USER", "1","-o", "wg0", "-s", container_ip, "-d", vpn_ip, "-j", "ACCEPT"], check=True)


    # Remove iptables rules for VPN IP <-> container IP
    def remove_firewall_rules(self , vpn_ip, container_ip):
        print(f"Removing firewall rules for {vpn_ip} ↔ {container_ip}")
        try:
            # Remove rule: container to VPN
            subprocess.run(["sudo", "/usr/sbin/iptables", "-D", "DOCKER-USER","-s", container_ip, "-d", vpn_ip, "-o", "wg0", "-j", "ACCEPT"], check=True)
            print(f"Removed: -s {container_ip} -d {vpn_ip} -o wg0 -j ACCEPT")
            # Remove rule: VPN to container
            subprocess.run(["sudo", "/usr/sbin/iptables", "-D", "DOCKER-USER","-s", vpn_ip, "-d", container_ip, "-i", "wg0", "-j", "ACCEPT"], check=True)
            print(f"Removed: -s {vpn_ip} -d {container_ip} -i wg0 -j ACCEPT")
        except subprocess.CalledProcessError as e:
            print("Error removing rule:", e)

    # Get the path to the user's progress file
    def get_user_progress_file(self, user_id):
        return os.path.join(PROGRESS_DIR, f"{user_id}.json")

    # Save the user's progress to a file
    def save_progress(self, user_id, user_progress):
        user_file = self.get_user_progress_file(user_id)
        try:
            with open(user_file, "w") as f:
                json.dump(user_progress, f, indent=4)
        except Exception as e:
            st.error(f"Error saving progress for {user_id}: {e}")

    # Initialize a new progress dictionary for a user
    def initialize_progress(self, user_id):
        progress = {f"step{i}": False for i in range(1, 10)}
        progress["completed"] = False
        return progress

    # Load the user's progress from file, or initialize if not found
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

    # Validate username:password input for a step and update progress
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

    # Validate a text answer for a step and update progress
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

    # Placeholder for flag validation step
    def validate_flag_step(self, user_id, step_num, question_text, placeholder, flag_file_relative):
        pass

    # Parse WireGuard config to get VPN IP for a user
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

    # Find a free /24 subnet in the 172.129.X.0/24 range not used by Docker
    def _find_free_subnet(self, base="172.129", start=2, end=255):
        client = docker.from_env()
        used_subnets = set()
        for net in client.networks.list():
            ipam = net.attrs.get("IPAM", {}).get("Config")
            if not ipam:
                continue  # skip if Config is None or empty
            for cfg in ipam:
                subnet = cfg.get("Subnet")
                if subnet:
                    used_subnets.add(subnet)
        for i in range(start, end):
            subnet = f"{base}.{i}.0/24"
            if subnet not in used_subnets:
                return subnet
        raise RuntimeError("No free subnet found in range.")

# --- Main Streamlit App Logic ---
def main(user_id):
    user = HTTPLevel2User()
    user.set_background('back_http.jpg')
#    user_id = st.session_state.user_id  # or wherever you get user_id from

    # Ensure progress directory exists
    if not os.path.exists(PROGRESS_DIR):
        os.makedirs(PROGRESS_DIR)

    # Load user progress into session state
    if "user_progress" not in st.session_state:
        st.session_state.user_progress = user.load_progress(user_id)

    # Display exercise title
    st.markdown(f"<h1 style='color: white;'>BankSploit</h1>", unsafe_allow_html=True)


    #     <p style='font-size:20px; color:white;'>
    # You’re a freelance art thief, always on the lookout for valuable pieces to enrich your personal collection.
    # Your latest intel points to a recently acquired Renaissance painting — possibly a long-lost work by Da Vinci — purchased by a private gallery and now scheduled for delivery.
    # The gallery uses outdated tech and the gallery's order and delivery system is vulnerable to eavesdropping so your objective is steal intelligence
    # related to this transaction and become a node of the network.<br>
    # Your mission: <br>
    # - Gather intelligence about the artwork’s order <br>
    # - Edit the delivery route and make the painting yours

    # Display exercise introduction
    st.markdown("""
        <p style='font-size:20px; color:white;'>
        You’ve infiltrated a private network long rumored to launder high-value Renaissance artworks — including a few allegedly painted by Da Vinci himself —
        through "state-of-the-art" banking channels that haven’t been updated since the Renaissance. Their defenses are outdated and unencrypted and sensitive data flows through in plaintext.
        <br> Your mission: <br>
        - Intercept communications between clients and the bank’s server to retrieve exploitable information<br>
        - Enter the system and reroute funds to secure your spot in the history books (next to Da Vinci).
        </p>
    """, unsafe_allow_html=True)

    # Start Exercise button logic
    if st.button("Start Exercise", key="start_exercise"):
        status_placeholder = st.empty()
        status_placeholder.info("This process might take a moment...  ")

        # Reset user progress
        st.session_state.user_progress = user.initialize_progress(user_id)
        user.save_progress(user_id, st.session_state.user_progress)
        try:
            # Start the user's container and get IPs
            container_ip, subnet = user.start_container_for_user(user_id)
            print("subnett is:" , subnet)


            print("container_ip: (what the start returns - gateway)", container_ip)
            vpn_ip = user.get_vpn_ip_for_user(user_id)
            print("vpn_ip: (what the get_vpn_ip returns)", vpn_ip)


            if not vpn_ip:
                st.error("VPN IP for your session could not be found. Contact admin.")
                return
            st.session_state["container_ip"] = container_ip
            st.session_state["vpn_ip"] = vpn_ip

            # Add firewall rules for this session
            user.add_firewall_rules(vpn_ip, subnet)

        except subprocess.CalledProcessError as e:
            st.error(f"Error restarting Docker container: {e}")

    # Show server IP if container is running
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

    # Set default container_ip if not set
    if "container_ip" not in st.session_state:
        st.session_state.container_ip = "none - Press start exercise to continue"

    # Question and answer validation for each step
    user.validate_and_update_step(user_id, 1, "1. How many open ports are on the server?", "*", "2")
    user.validate_and_update_step(user_id, 2, "2. What tool allows you to capture raw network packets, visualize traffic flow in real time, and apply filters to analyze protocols?", "w********", "wireshark")


    CAPTURE_PATH = os.path.join(os.path.dirname(__file__), "shared", "capture.pcap")


    def get_docker_bridge_interface(container_ip):
        subnet_prefix = '.'.join(container_ip.split('.')[:3]) + '.'

        try:
            output = subprocess.check_output("ip -o -4 addr show", shell=True).decode()
            for line in output.splitlines():
                parts = line.split()
                iface = parts[1]
                ip_addr = parts[3].split('/')[0]

  #              st.write(f" Checking iface: {iface} with IP: {ip_addr}")#for troubleshooting
                if iface.startswith("br-") and ip_addr.startswith(subnet_prefix):
#                    st.write(f" Found docker bridge: {iface} with IP: {ip_addr}")
                    return iface
        except Exception as e:
            st.error(f"Error finding docker bridge interface: {e}")

        st.warning("Docker bridge not found.")
        return None


    if st.button("Start live Capture with tcpdump"):
        container_ip = user.get_container_ip(user_id)  # Make sure user and user_id are in scope here!


        status_placeholder = st.empty()
        status_placeholder.info("Starting live capture of network for 60 seconds...  ")

        if not container_ip:
            st.error("Container IP not found.")
        else:
            iface = get_docker_bridge_interface(container_ip)

            if iface:
                capture_cmd = f"sudo timeout 60 tcpdump -i {iface} tcp port 80 -w {CAPTURE_PATH}"
                try:
                    subprocess.run(capture_cmd, shell=True, check=True)
                    st.success("Capture completed successfully.")
                except subprocess.CalledProcessError as e:
                    if e.returncode == 124:
                        st.success("Capture completed. You can now download the captured traffic.")
                    else:
                        st.error(f"tcpdump failed with exit code {e.returncode}")
            else:
                st.warning("Docker bridge not found.")


    if os.path.exists(CAPTURE_PATH):
        with open(CAPTURE_PATH, "rb") as f:
            st.download_button(
                label="Download the captured traffic",
                data=f,
                file_name="capture.pcap",
                mime="application/octet-stream"
            )
    else:
        st.info("Capture not done yet")


    user.validate_and_update_step(user_id, 3, "3. What network protocol is used together with HTTP to provide reliable communication and handle acknowledgments, as seen in the server's communication?", "***", "tcp")
    user.validate_and_update_step(user_id, 4, "4. What term or code in communication indicates the acknowledgment of received packets?", "***", "ack")
    user.validate_and_update_step(user_id, 5, "5. Based on the open port analysis, what filter can you apply to isolate traffic to the bank's service?", "***.**** == ****", "tcp.port == 8080")
    user.validate_and_update_step(user_id, 6, "6. What HTTP status code indicates that a login attempt was unauthorized?", "*** U***********", "401 unauthorized")
    user.validate_and_update_step(user_id, 7, "7. What type of HTTP methods are being used in this network?", "***,****", "get,post")
    user.validate_and_update_step(user_id, 8, "8. What is the name of the bank you entered?", "**********", "septemtica")
    user.validate_and_update_step(user_id, 9, "9. If you made a successful transfer, enter the flag:", "Flag here...", "7a5f8d3e1c9b24680a42d59")
   
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

    # Stop Exercise button logic
    if st.button("Stop Exercise"):
        try:
            vpn_ip = st.session_state.get("vpn_ip") or user.get_vpn_ip_for_user(user_id)
            container_ip = st.session_state.get("container_ip")
            if not vpn_ip or not container_ip:
                st.warning("No active exercise to stop.")
                return
            try:
                subnet = user.get_container_ip(user_id)
                user.remove_firewall_rules(vpn_ip, subnet)
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

# Run the main function if this file is executed directly
if __name__ == "__main__":
    main("test_user")