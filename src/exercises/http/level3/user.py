import streamlit as st  # Streamlit for web UI
import os  # For file and path operations
import subprocess  # For running shell commands (iptables)
import base64  # For encoding images to base64
import json  # For JSON config and progress files
import docker  # Docker SDK for Python
from docker.errors import NotFound  # Exception for missing Docker objects
from exercises.user_base import UserExerciseBase  # Base class for exercises

# Define important directories and paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))  # Current file's directory
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "../../../"))  # Project root
PROGRESS_DIR = os.path.join(SRC_DIR, "progress", "http", "level3")  # Progress files directory
start_dir = os.path.join(CURRENT_DIR, "shared")  # Shared directory for exercise

class HTTPLevel3User(UserExerciseBase):
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

    # Start a Docker container for a user, building the image if needed
    def start_container_for_user(self,user_id):
        client = docker.from_env()
        network_name = "ctf_net"
        image_tag = "cyberrange2_web"
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Path to the web app directory
        web_path = os.path.abspath(os.path.join(current_dir, "./shared"))
        print("Web path resolved to:", web_path)

        container_name = f"http_level3_{user_id}"

        # Ensure Docker network exists
        try:
            client.networks.get(network_name)
        except NotFound:
            client.networks.create(network_name, driver="bridge")

        # Build the Docker image for the web app
        print("Building image...")
        try:
            client.images.build(path=web_path, tag=image_tag)
        except APIError as e:
            print(f"Image build failed: {e}")
            raise

        # Remove old container if it exists
        try:
            old = client.containers.get(container_name)
            old.remove(force=True)
        except NotFound:
            pass

        # Start new container with the built image and attach to the network
        print("Starting container...")
        container = client.containers.run(
            image=image_tag,
            name=container_name,
            detach=True,
            network=network_name,
            runtime="runsc",  # Use gVisor runtime for isolation
            volumes={
                web_path: {
                    'bind': '/app',
                    'mode': 'rw'
                }
            },
            working_dir="/app",
            command=["python", "app.py"]
        )

        # Reload container info and get its IP address
        container.reload()
        ip = container.attrs["NetworkSettings"]["Networks"][network_name]["IPAddress"]
        print(f"Container {container_name} running at {ip}")
        return container, ip

    # Stop and remove the user's Docker container
    def stop_container_for_user(self, user_id):
        client = docker.from_env()
        container_name = f"http_level3_{user_id}"
        try:
            container = client.containers.get(container_name)
            container.remove(force=True)
            print(f"Container {container_name} stopped and removed.")
        except NotFound:
            print(f"No container found for {container_name}")

    # Get the container's IP address for the user
    def get_container_ip(self, user_id):
        client = docker.from_env()
        container_name = f"http_level3_{user_id}"
        try:
            container = client.containers.get(container_name)
            networks = container.attrs["NetworkSettings"]["Networks"]
            if "ctf_net" in networks:
                return networks["ctf_net"]["IPAddress"]
            else:
                # fallback to first available network
                for net_data in networks.values():
                    return net_data["IPAddress"]
        except (NotFound, KeyError):
            return None

    # Add iptables rules to allow VPN IP <-> container IP communication
    def add_firewall_rules(self, vpn_ip, container_ip):
        subprocess.run(["sudo","/usr/sbin/iptables", "-I", "DOCKER-USER", "-i", "wg0", "-s", vpn_ip, "-d", container_ip, "-j", "ACCEPT"], check=True)
        subprocess.run(["sudo", "/usr/sbin/iptables", "-I", "DOCKER-USER", "-o", "wg0", "-s", container_ip, "-d", vpn_ip, "-j", "ACCEPT"], check=True)
     
    # Remove iptables rules for VPN IP <-> container IP
    def remove_firewall_rules(self, vpn_ip, container_ip):
        subprocess.run(["sudo","/usr/sbin/iptables", "-D", "DOCKER-USER", "-i", "wg0", "-s", vpn_ip, "-d", container_ip, "-j", "ACCEPT"], check=True)
        subprocess.run(["sudo","/usr/sbin/iptables", "-D", "DOCKER-USER", "-o", "wg0", "-s", container_ip, "-d", vpn_ip, "-j", "ACCEPT"], check=True)

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
        progress = {f"step{i}": False for i in range(1, 9)}
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

    # Validate a flag answer by reading the flag file from the shared directory
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

# Main Streamlit app logic
def main(user_id):
    user = HTTPLevel3User()
    user.set_background('back_http.jpg')

    # Ensure progress directory exists
    if not os.path.exists(PROGRESS_DIR):
        os.makedirs(PROGRESS_DIR)

    # Load user progress into session state
    if "user_progress" not in st.session_state:
        st.session_state.user_progress = user.load_progress(user_id)

    # Scenario Title and Description
    st.markdown(f"<h1 style='color: white;'>Axis: Last Commit</h1>", unsafe_allow_html=True)
    st.markdown("""
    <p style='font-size:20px; color:white;'>
        You were a backend dev at Nexora, a small AI startup you helped build from the ground up. Two weeks ago, the founders sold the company overnight without giving any notice to employees 
        and your last major contribution, a research project called “Axis”, is now gone without any credit to you and your team.<br><br>
        But you remember something:<br>
        Nexora always dumped internal dev files into their public-facing test server. You warned them about it but it was never fixed. 
        There’s a leftover utility meant to provide access to documentation — pointless to outsiders, but valuable if you know the projects to guide you to valuable files.<br><br>
        You remember a test utility was used internally at Nexora for file previews. The link will appear below:
    <br> Your mission: <br>
        - Find hidden directories on server to strategically find your project.<br>
        - Retrieve the executable you were working on for months.
        </p>


    </p>
    """, unsafe_allow_html=True)

    # Start Exercise button logic
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

            # Show link to the internal file viewer utility
            st.markdown(f"""
                    <div style='margin-top:20px; font-size:18px; color:white;'>
                         <a href="http://{container_ip}:5000/?file=files/readme.txt" target="_blank" 
                            style="color:	#4169E1; font-weight:bold; text-decoration:none;">
                            Click here to access the utility
                        </a>
                    </div>
                    """, unsafe_allow_html=True)

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

    # Scenario Questions
    user.validate_and_update_step(user_id, 1,"1. What is the parameter used in the internal file viewer?", "f***", "file")
    user.validate_and_update_step(user_id, 2,"2. What is the base directory used by the application to serve files?", "f*****", "files")
    user.validate_and_update_step(user_id, 3,"3. What classic vulnerability allows access to parent directories beyond the web root?", "p*** t********", "path traversal")
    user.validate_and_update_step(user_id, 4,"4. What relative path notation is typically used to move one directory up?", "**", "..")
    user.validate_and_update_step(user_id, 5,"5. Which fuzzing tool can you use to discover hidden folders via wordlist?", "f***", "ffuf")
    st.markdown("""
    *Hint: This link will provide you a tool: [here](https://github.com/huntergregal/wordlists/blob/master/common.txt).* 
    <br>""", unsafe_allow_html=True)
    user.validate_and_update_step(user_id, 6,"6. What command would you run to brute-force directories one level above the base directory to find your executable?",
      "f*** -* http://your_ip:your_port/?file=files/../F***/****.*xe -* common.txt",
      f"ffuf -u http://{st.session_state.get('container_ip', 'your_ip_here')}:5000/?file=files/../FUZZ/axis.exe -w common.txt")

    user.validate_and_update_step(user_id, 7,"7. What is the name of the hidden directory storing sensitive project files?", "s*****", "secret")
    user.validate_flag_step(user_id, 8,"8. Submit flag of hidden folder:", "Enter flag here...", "flag.txt")
   
    # Check if all steps are completed
    all_steps_completed = all(st.session_state.user_progress.get(f"step{i}", False) for i in range(1, 9))

    # Mark exercise as completed if all steps are done
    if all_steps_completed and not st.session_state.user_progress["completed"]:
        st.session_state.user_progress["completed"] = True
        user.save_progress(user_id, st.session_state.user_progress)

    # Show congratulations message if completed
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

# Run the main function if this file is executed directly
if __name__ == "__main__":
    main("test_user")