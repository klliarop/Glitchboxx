import streamlit as st  # Import Streamlit for web UI
import os  # For file and path operations
import subprocess  # For running shell commands (e.g., iptables)
import base64  # For encoding images to base64 for backgrounds
import json  # For saving/loading user progress
import docker  # For Docker container management
import yaml  # For parsing YAML files (docker-compose)
from docker.errors import NotFound  # For handling missing Docker containers
from exercises.user_base import UserExerciseBase  # Import base class for user exercises

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))  # Current directory of this script
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "../../../"))  # Project source directory
PROGRESS_DIR = os.path.join(SRC_DIR, "progress", "ftp", "level2")  # Directory for user progress files
WORDLIST_FILE_PATH = os.path.join(CURRENT_DIR, "500-worst-passwords.txt")  # Path to wordlist file
DOCKER_COMPOSE_PATH = os.path.join(CURRENT_DIR, "docker-compose.yml")  # Path to docker-compose file
start_dir = os.path.join(CURRENT_DIR, "shared")  # Shared directory for exercise files

class FTPLevel2User(UserExerciseBase):
    # User logic for FTP Level 2 exercise

    def set_background(self, image_file):
        # Set the background image for the exercise UI
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
        # Start the Docker container for the user
        client = docker.from_env()
        image = "garethflowers/ftp-server"
        network_name = "ctf_net"
        container_name = f"ftp_level2_{user_id}"
        host_shared_dir = os.path.join(CURRENT_DIR, "shared")
        os.makedirs(host_shared_dir, exist_ok=True)
        try:
            existing = client.containers.get(container_name)
            existing.remove(force=True)
        except NotFound:
            pass

        ftp_username, ftp_password = self.get_ftp_credentials()
        if ftp_username is None or ftp_password is None:
            st.warning("Failed to load FTP credentials. Some features may not work.")

        command = (
            "sh -c \""
            f"echo 'Only user \\\"{ftp_username}\\\" is allowed to access this FTP server.' > /etc/vsftpd.banner && "
            "echo 'banner_file=/etc/vsftpd.banner' >> /etc/vsftpd.conf && "
            "/usr/sbin/vsftpd /etc/vsftpd.conf\""
        )

        container = client.containers.run(
            image=image,
            name=container_name,
            detach=True,
            network=network_name,
            runtime="runsc",
            environment={
                "FTP_USER": ftp_username,
                "FTP_PASS": ftp_password
            },
            volumes={
                host_shared_dir: {
                    'bind': f'/home/{ftp_username}',
                    'mode': 'rw'
                }
            },
            command=command
        )
        container.reload()
        ip = container.attrs["NetworkSettings"]["Networks"][network_name]["IPAddress"]
        return container, ip

    def stop_container_for_user(self, user_id):
        # Stop and remove the Docker container for the user
        client = docker.from_env()
        container_name = f"ftp_level2_{user_id}"
        try:
            container = client.containers.get(container_name)
            container.remove(force=True)
        except docker.errors.NotFound:
            pass

    def get_container_ip(self, user_id):
        # Get the container's IP address for the user
        client = docker.from_env()
        container_name = f"ftp_level2_{user_id}"
        network_name = "ctf_net"
        try:
            container = client.containers.get(container_name)
            return container.attrs["NetworkSettings"]["Networks"][network_name]["IPAddress"]
        except (NotFound, KeyError):
            return None

    def add_firewall_rules(self, vpn_ip, container_ip):
        # Add firewall rules for the user's VPN and container IPs
        subprocess.run(["sudo","/usr/sbin/iptables", "-I", "DOCKER-USER", "-i", "wg0", "-s", vpn_ip, "-d", container_ip, "-j", "ACCEPT"], check=True)
        subprocess.run(["sudo", "/usr/sbin/iptables", "-I", "DOCKER-USER", "-o", "wg0", "-s", container_ip, "-d", vpn_ip, "-j", "ACCEPT"], check=True)
     
    def remove_firewall_rules(self, vpn_ip, container_ip):
        # Remove firewall rules for the user's VPN and container IPs
        subprocess.run(["sudo","/usr/sbin/iptables", "-D", "DOCKER-USER", "-i", "wg0", "-s", vpn_ip, "-d", container_ip, "-j", "ACCEPT"], check=True)
        subprocess.run(["sudo","/usr/sbin/iptables", "-D", "DOCKER-USER", "-o", "wg0", "-s", container_ip, "-d", vpn_ip, "-j", "ACCEPT"], check=True)

    def get_user_progress_file(self, user_id):
        # Get the path to the user's progress file
        return os.path.join(PROGRESS_DIR, f"{user_id}.json")

    def save_progress(self, user_id, user_progress):
        # Save the user's progress data
        user_file = self.get_user_progress_file(user_id)
        try:
            with open(user_file, "w") as f:
                json.dump(user_progress, f, indent=4)
        except Exception as e:
            st.error(f"Error saving progress for {user_id}: {e}")

    def initialize_progress(self, user_id):
        # Initialize the user's progress data
        progress = {f"step{i}": False for i in range(1, 12)}
        progress["completed"] = False
        return progress

    def load_progress(self, user_id):
        # Load the user's progress data
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
        # Validate credentials for a step in the exercise
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
        # Validate and update a step in the exercise
        st.markdown(f"<h5 style='color: white;'><br>{question_text}</h5>", unsafe_allow_html=True)
        with st.form(key=f"user_{user_id}_step{step_num}_form"):
            col1, col2 = st.columns([2, 1])
            with col1:
                user_answer = st.text_input(" ", placeholder=placeholder, key=f"user_{user_id}_step{step_num}_input", autocomplete="off")
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                submit_button = st.form_submit_button("Submit")
            if submit_button:
                normalized_user_answer = user_answer.strip().lower()
                normalized_correct_answer = correct_answer.strip().lower()
                if normalized_user_answer == normalized_correct_answer:
                    st.session_state.user_progress[f"step{step_num}"] = True
                    self.save_progress(user_id, st.session_state.user_progress)
                    st.success("Correct!")
                else:
                    st.error("Wrong answer!")

    def validate_flag_step(self, user_id, step_num, question_text, placeholder, flag_file_relative):
        # Validate a flag step in the exercise
        st.markdown(f"<h5 style='color: white;'><br>{question_text}</h5>", unsafe_allow_html=True)
        with st.form(key=f"user_{user_id}_step{step_num}_form"):
            col1, col2 = st.columns([2, 1])
            with col1:
                user_answer = st.text_input(" ", placeholder=placeholder, key=f"user_{user_id}_step{step_num}_input", autocomplete="off")
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                submit_button = st.form_submit_button("Submit")
            if submit_button:
                flag_file_path = self.find_flag_file(start_dir)
                if flag_file_path and os.path.exists(flag_file_path):
                    with open(flag_file_path, "r") as file:
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
        # Get the VPN IP for the user from the WireGuard config
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

    def get_ftp_credentials(self):
        # Retrieve FTP credentials from docker-compose.yml
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

    def find_flag_file(self, start_dir, target_filename="flag.txt"):
        # Recursively search for the flag file in the shared directory
        for root, dirs, files in os.walk(start_dir):
            if target_filename in files:
                return os.path.join(root, target_filename)
        return None

def main(user_id):
    # Main function to run the FTP Level 2 user exercise
    user = FTPLevel2User()
    user.set_background('back_ftp.jpg')

    if not os.path.exists(PROGRESS_DIR):
        os.makedirs(PROGRESS_DIR)

    if "user_progress" not in st.session_state:
        st.session_state.user_progress = user.load_progress(user_id)

    st.markdown(f"<h1 style='color: white;'>Aftermath: Reverse the Damage</h1>", unsafe_allow_html=True)
    st.markdown("""<p style='font-size:20px; color:white;'>
        You are a security analyst at “NeuroGen Biotech” an organization specializing in biochemical research.
        You were informed about a data breach that happened at the FTP server located within the corporate internal network. Someone logged in and stole a confidential medicine recipe.
        Worse, they changed all the employee passwords, disrupting all the on-going projects.
        However, the intruder wasn't very thorough and used some very basic credentials.
        Your mission is to:
        <br> - Find a way to regain access to the server
        <br> - Find out who compromised the system through reported logs
        </p>""", unsafe_allow_html=True)

    ftp_username, ftp_password = user.get_ftp_credentials()
    if ftp_username is None or ftp_password is None:
        st.warning("Failed to load FTP credentials. Some features may not work.")

    if st.button("Start Exercise", key="start_exercise"):
        # Reset progress and start the Docker container for the user
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
        except subprocess.CalledProcessError as e:
            st.error(f"Error restarting Docker container: {e}")

    if "container_ip" in st.session_state:
        # Show the container IP to the user
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
        # Set a default value if container_ip is not set
        st.session_state.container_ip = "none - Press start exercise to continue"

    # Validate each step of the exercise
    user.validate_and_update_step(user_id, 1, "1. Which tool enables you to see the open services on the target?", "***p ***.***.*.*", f"nmap {st.session_state.container_ip}")
    user.validate_and_update_step(user_id, 2, "2. What username you suspect is the one to login the server?", " ", f"{ftp_username}")
    user.validate_and_update_step(user_id, 3, "3. What type of attack involves repeatedly trying many passwords to gain access?", "b*********", "bruteforce")
    st.markdown("""
    *Hint: Learn about this type of attacks [here](https://www.fortinet.com/resources/cyberglossary/brute-force-attack).* 
    <br>
    *Hint: Learn more about common tools: [here](https://www.infosecinstitute.com/resources/hacking/popular-tools-for-brute-force-attacks/).*
    <br>""", unsafe_allow_html=True)
    user.validate_and_update_step(user_id, 4, "4. Based on the previous question and hint, what tool can you use to crack the password?", "h****", "hydra")
    user.validate_and_update_step(user_id, 5, "5. What is the name of wordlist you can use?", "5**-w****-p********.txt", "500-worst-passwords.txt")

    if os.path.isfile(WORDLIST_FILE_PATH):
        with open(WORDLIST_FILE_PATH, "r") as f:
            st.download_button(
                label="Download Wordlist Here",
                data=f,
                file_name="500-worst-passwords.txt",
                mime="text/plain",
                help="Click to download the leaked password file"
            )
    else:
        st.warning("Wordlist file not found.")

    user.validate_and_update_step(user_id, 6, "6. What command did you use to crack passwords of server?", "h**** -* {suspected_username} -* 500-worst-passwords.txt f**://***.*.*.*:**", f"hydra -l {ftp_username} -P 500-worst-passwords.txt ftp://{st.session_state.container_ip}:21")

  
    if st.button("Get your video hint"):
        # YouTube video URL
        video_url = "https://www.youtube.com/watch?v=wcmpp8IPZOA"
        video_embed = video_url.replace("watch?v=", "embed/")

        # Show the embedded video
        st.markdown(f"""
        <iframe width="720" height="405"
        src="{video_embed}"
        frameborder="0"
        allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture"
        allowfullscreen>
        </iframe>
        """, unsafe_allow_html=True)

        st.markdown("---")

    user.validate_credentials(user_id, 7, "7. What are the credentials for login of server?", ftp_username, ftp_password)
    user.validate_and_update_step(user_id, 8, "8. Which tool can help you analyze PCAP files?", "w********", "wireshark")
    user.validate_and_update_step(user_id, 9,  "9. What username was the one that entered with unauthorized access? ", "a********", "anonymous")
    user.validate_and_update_step(user_id, 10, " 10. What is the suspicious IP found in the pcap file? ", "Enter IP here", "192.168.1.254")
    user.validate_flag_step(user_id, 11, "11. Enter the flag", "FLAG{...}", "flag.txt")

    # Check if all steps are completed
    all_steps_completed = all(st.session_state.user_progress.get(f"step{i}", False) for i in range(1, 12))

    if all_steps_completed and not st.session_state.user_progress["completed"]:
        # Mark the exercise as completed
        st.session_state.user_progress["completed"] = True
        user.save_progress(user_id, st.session_state.user_progress)

    if st.session_state.user_progress["completed"]:
        # Show congratulations message
        st.markdown("""
            <h1 style='text-align: center; color: green; font-size: 50px;'> CONGRATULATIONS! </h1>
            <p style='text-align: center; font-size: 24px;'>You completed this exercise!</p>
        """, unsafe_allow_html=True)

    if st.button("Stop Exercise"):
        # Stop the Docker container and clean up progress
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
    main("test_user")  # Run the main function for a test user