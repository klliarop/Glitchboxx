import streamlit as st  # Import Streamlit for web UI
import requests  # For making HTTP requests to backend services
import importlib  # For dynamic module import
import os  # For file and path operations
import base64  # For encoding images to base64 for backgrounds
import sys  # For manipulating the Python path
import json

st.set_page_config(
    page_title="Glitchboxx"   
)
#This process was placed into funcion as it was executed before the import of streamlit, which caused an error
def get_vpn_server_ip():
    try:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'wireguard', 'wg_config.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config.get("WG_SERVER_PUBLIC_IP", "127.0.0.1")
    except Exception as e:
        print(f"[ERROR] Could not read wg_config.json: {e}")
        return "127.0.0.1"


# Base URLs for backend services
BASE_URL_LOGIN = "http://127.0.0.1:5001"  # Login service
BASE_URL_REGISTER = "http://127.0.0.1:5002"  # Registration service
#BASE_URL_VPN = f"http://{get_vpn_server_ip()}:5003"

BASE_URL_VPN = "https://glitchboxx.duckdns.org/vpn"


# Add project root to Python path for module imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Function for fonts and custom styles
def set_custom_styles():
    custom_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Rubik+Mono+One&display=swap');

    .title-text {
        font-family: 'Rubik Mono One', sans-serif;
        font-size: 35px  !important;
        color: #ffffff !important;
        text-shadow: 4px 4px 0px #000000, 
                    6px 6px 5px rgba(0, 0, 0, 0.5);
        text-align: center;
        letter-spacing: 3px;
        text-transform: uppercase;
    }

    .subheader-text {
        font-family: 'Rubik Mono One', sans-serif;
        font-size: 25px !important;
        color: #ffffff;
        text-shadow: 3px 3px 0px #000000;
        text-align: center;
    }

    .stTabs [data-baseweb="tab-list"] {
        background-color: #86608E;  
        border-radius: 10px;
        padding: 5px;
    }

    .stTabs [data-baseweb="tab"] {
        color: #ffffff !important;
        font-size: 18px !important;
        font-weight: bold !important;
        border-radius: 8px;
        padding: 10px 15px;
    }

    .stTabs [aria-selected="true"] {
        background-color: #86608E;  
        color: #ffffff !important;
    }

    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)  # Apply custom CSS styles

# Function to set the background image
def set_background(image_file):
    base_dir = os.path.dirname(os.path.abspath(__file__))  # Get current directory
    wallpapers_dir = os.path.join(base_dir, "wallpapers")  # Path to wallpapers folder
    image_path = os.path.join(wallpapers_dir, image_file)  # Path to the selected image
    with open(image_path, "rb") as f:
        img_data = f.read()  # Read image data
    b64_encoded = base64.b64encode(img_data).decode()  # Encode image to base64
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
    st.markdown(style, unsafe_allow_html=True)  # Set background style

# Login form and logic
def login_user():
    set_background('app_wallpaper.jpg')  # Set background for login page
    st.markdown("<p class='title-text'>Welcome to Glitchboxx</p>", unsafe_allow_html=True)
    st.markdown("<p class='subheader-text'>Login</p>", unsafe_allow_html=True)

    with st.form(key="login_form"):
        username = st.text_input(" ", placeholder="Enter your username", autocomplete="off")
        password = st.text_input(" ", placeholder="Enter your password", type="password", autocomplete="off")
        login_button = st.form_submit_button("Login")

    if login_button:
        response = requests.post(f"{BASE_URL_LOGIN}/login", data={"username": username, "password": password})
        if response.status_code == 200:
            st.success("Login successful!")
            st.session_state.user_id = response.json().get("user_id")
            st.session_state.logged_in = True
            st.query_params["user_id"] = st.session_state.user_id
            st.rerun()
        else:
            st.error("Invalid username or password")

# Registration form and logic
def register_user():
    st.markdown("<p class='title-text'>Welcome to  Glitchboxx</p>", unsafe_allow_html=True)
    st.markdown("<p class='subheader-text'>Register</p>", unsafe_allow_html=True)

    with st.form(key="register_form"):
        username = st.text_input(" ", placeholder="Enter your username", key="reg_username", autocomplete="off")
        password = st.text_input(" ", placeholder="Enter your password", type="password", key="reg_password", autocomplete="off")
        register_button = st.form_submit_button("Register")

    if register_button:
        try:
            response = requests.post(f"{BASE_URL_REGISTER}/register", data={"username": username, "password": password}, timeout=5)
            if response.status_code == 200:
                st.success("Registration successful! You can now log in.")
            else:
                st.error(f"Registration failed: {response.json().get('message', 'Unknown error')}")
        except requests.exceptions.RequestException as e:
            st.error(f"Connection error: {str(e)}")

# Exercise selection page logic
def exercise_selection_page():
    set_background('app_wallpaper.jpg')  # Set background for exercise selection
    st.markdown("<p class='subheader-text'>Select an Exercise</p>", unsafe_allow_html=True)

    # Mapping for user-friendly display
    exercise_labels = {
        "Dark Contract": "ftp",
        "Matrix Alert": "ssh",
        "Da Vinci Node": "http"
    }

    level_options_by_exercise = {
        "ftp": {
            "Level 1 - Beginner": "level1",
            "Level 2 - Intermediate": "level2"
        },
        "ssh": {
            "Level 1 - Beginner": "level1",
            "Level 2 - Intermediate": "level2"
        },
        "http": {
            "Level 1 - Beginner": "level1",
            "Level 2 - Intermediate": "level2",
            "Level 3 - Advanced": "level3"
        }
    }

    # Display exercise selection
    exercise_display = st.selectbox("Choose an Exercise", list(exercise_labels.keys()))
    exercise = exercise_labels[exercise_display]

    # Get level options based on selected exercise
    level_labels = level_options_by_exercise[exercise]
    level_display = st.selectbox("Choose a Level", list(level_labels.keys()))
    level = level_labels[level_display]

    if st.button("Start Exercise"):
        st.session_state.exercise = exercise
        st.session_state.level = level
        st.session_state.exercise_running = True
        st.query_params["user_id"] = st.session_state.user_id
        st.query_params["exercise"] = exercise
        st.query_params["level"] = level
        st.rerun()

# Main app logic
def main():
    set_custom_styles()  # Apply custom styles

    # Initialize session state variables
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "exercise_running" not in st.session_state:
        st.session_state.exercise_running = False

    user_id = st.query_params.get("user_id")
    exercise = st.session_state.get("exercise") or st.query_params.get("exercise")
    level = st.session_state.get("level") or st.query_params.get("level")
    if exercise and level:
        progress_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exercises", exercise, level, "progress")
    else:
        progress_dir = None

    # Show login/register tabs if not logged in
    if not st.session_state.logged_in:
        tab1, tab2 = st.tabs(["Login", "Register"])
        with tab1:
            login_user()
        with tab2:
            register_user()
    else:
        # If exercise is running, show exercise UI and cleanup logic
        if st.session_state.exercise_running or ("exercise" in st.query_params and "level" in st.query_params):
            


            if st.button("Return to exercise selection"):
                # --- Save all needed values BEFORE popping ---
                exercise_val = st.session_state.get("exercise") or st.query_params.get("exercise")
                level_val = st.session_state.get("level") or st.query_params.get("level")
                user_id_val = st.session_state.get("user_id") or st.query_params.get("user_id")
                progress_dir_val = None
                if exercise_val and level_val:
                    progress_dir_val = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exercises", exercise_val, level_val, "progress")

                # Remove user progress file if it exists
                if user_id_val and progress_dir_val and os.path.exists(progress_dir_val):
                    user_file_path = os.path.join(progress_dir_val, f"{user_id_val}.json")
                    if os.path.exists(user_file_path):
                        os.remove(user_file_path)
                        st.success(f"Deleted progress file: {user_file_path}")

                # Clean up Docker containers and firewall rules for the user
                compose_dir = os.path.dirname(os.path.abspath(__file__))
                if exercise_val and level_val:
                    compose_file_path = os.path.join(compose_dir, "exercises", exercise_val, level_val, "docker-compose.yml")
                    module_name = f"exercises.{exercise_val}.{level_val}.user"
                    module = importlib.import_module(module_name)
                    class_name = f"{exercise_val.upper()}Level{level_val[-1]}User"
                    print(f"[DEBUG] class_name: {class_name}")

                    if hasattr(module, class_name):
                        user_obj = getattr(module, class_name)()
                        vpn_ip = user_obj.get_vpn_ip_for_user(user_id_val, config_path="/etc/wireguard/wg0.conf")
                        container_ip = user_obj.get_container_ip(user_id_val)
                        if vpn_ip and container_ip:
                            user_obj.remove_firewall_rules(vpn_ip, container_ip)
                        else:
                            print(f"[WARNING] Skipping firewall rule removal because vpn_ip or container_ip is None. vpn_ip={vpn_ip}, container_ip={container_ip}")
                        user_obj.stop_container_for_user(user_id_val)
                        # Reset progress in session and file
                        st.session_state.user_progress = user_obj.initialize_progress(user_id_val)
                        user_obj.save_progress(user_id_val, st.session_state.user_progress)
                        user_progress_file = user_obj.get_user_progress_file(user_id_val)
                        if os.path.exists(user_progress_file):
                            os.remove(user_progress_file)
                    elif hasattr(module, "stop_container_for_user"):
                        module.stop_container_for_user(user_id_val)
                    if hasattr(module, "get_user_progress_file"):
                        user_progress_file = module.get_user_progress_file(user_id_val)
                        if os.path.exists(user_progress_file):
                            os.remove(user_progress_file)

                # --- Now pop/remove from session/query params ---
                st.session_state.exercise_running = False
                st.query_params.pop("exercise", None)
                st.query_params.pop("level", None)
                st.session_state.pop("exercise", None)
                st.session_state.pop("level", None)

                # Clear session state except for login info
                for key in list(st.session_state.keys()):
                    if key not in ['logged_in', 'user_id']:
                        del st.session_state[key]
                st.rerun()


            
            # if st.button("Return to exercise selection"):
            #     st.session_state.exercise_running = False
            #     st.query_params.pop("exercise", None)
            #     st.query_params.pop("level", None)

            #     # Remove user progress file if it exists
            #     if user_id and os.path.exists(progress_dir):
            #         user_file_path = os.path.join(progress_dir, f"{user_id}.json")
            #         if os.path.exists(user_file_path):
            #             os.remove(user_file_path)
            #             st.success(f"Deleted progress file: {user_file_path}")

            #     # Clean up Docker containers and firewall rules for the user
            #     compose_dir = os.path.dirname(os.path.abspath(__file__))
            #     exercise = st.session_state.get("exercise")
            #     level = st.session_state.get("level")
            #     if exercise and level:
            #         compose_file_path = os.path.join(compose_dir, "exercises", exercise, level, "docker-compose.yml")
                    
            #         module_name = f"exercises.{exercise}.{level}.user"
            #         module = importlib.import_module(module_name)

            #         class_name = f"{exercise.upper()}Level{level[-1]}User"
            #         print(f"[DEBUG] class_name: {class_name}")

            #         if hasattr(module, class_name):
            #             user_obj = getattr(module, class_name)()
                        
            #             vpn_ip = user_obj.get_vpn_ip_for_user(user_id, config_path="/etc/wireguard/wg0.conf")
            #             container_ip = user_obj.get_container_ip(user_id)

            #             if vpn_ip and container_ip:
            #                 user_obj.remove_firewall_rules(vpn_ip, container_ip)
            #             else:
            #                 print(f"[WARNING] Skipping firewall rule removal because vpn_ip or container_ip is None. vpn_ip={vpn_ip}, container_ip={container_ip}")

            #             user_obj.stop_container_for_user(user_id) 
                        
            #             # Reset progress in session and file
            #             st.session_state.user_progress = user_obj.initialize_progress(user_id)
            #             user_obj.save_progress(user_id, st.session_state.user_progress)
            #             user_progress_file = user_obj.get_user_progress_file(user_id)
            #             if os.path.exists(user_progress_file):
            #                 os.remove(user_progress_file)
            #         elif hasattr(module, "stop_container_for_user"):
            #             module.stop_container_for_user(user_id)  
               
            #         if hasattr(module, "get_user_progress_file"):
            #             user_progress_file = module.get_user_progress_file(user_id)
            #             if os.path.exists(user_progress_file):
            #                 os.remove(user_progress_file)
                           

            #     # Clear session state except for login info
            #     for key in list(st.session_state.keys()):
            #         if key not in ['logged_in', 'user_id']:
            #             del st.session_state[key]
            #     st.rerun()

            # Dynamically import and run the user exercise module
            module_name = f"exercises.{st.query_params['exercise']}.{st.query_params['level']}.user"
            module = importlib.import_module(module_name)
            module.main(user_id=st.session_state.user_id)
            
        else:

            st.markdown("<p class='subheader-text'>Welcome!</p>", unsafe_allow_html=True)
            
            # Styled Glitchboxx content usin
            st.markdown(f"""
                <style>
                    .glitchboxx-content {{
                        font-family: 'Courier New', monospace;
                        font-size: 18px;
                        color: #ffffff;
                        background-color: rgba(0, 0, 0, 0.6);
                        padding: 20px;
                        border-radius: 8px;
                        box-shadow: 0 0 10px #86608E;
                        margin-top: 30px;
                        text-align: left;
                    }}

                    a.feedback-link {{
                        color: #ADD8E6;
                        text-decoration: underline;
                    }}
                </style>

                <div class="glitchboxx-content">
                    <strong>Glitchboxx</strong> is a playground to start your journey in the world of cybersecurity,
                    designed to explore and experiment with your offensive skills, safely and without breaking anything real!
                    <br><br>
                    Help us make your Glitchboxx experience even better – please share your feedback below!
                    <br>
                    <a class="feedback-link" href="https://docs.google.com/forms/d/e/1FAIpQLScnhXsmpn5UjhC7fWJtUrEHkLMKHapJdwq2wITpxbW1UpqDtA/viewform?usp=dialog" target="_blank">
                        Give us your feedback
                    </a>
                </div>
            """, unsafe_allow_html=True)


            st.markdown(f"""
                <style>
                    code {{
                        background-color: #111;
                        color: #e0e0e0;  
                        padding: 2px 6px;
                        border-radius: 4px;
                        font-family: 'Courier New', monospace;
                    }}
                </style>
                <div style="
                    background-color: rgba(0, 0, 0, 0.6);
                    padding: 20px;
                    border-radius: 8px;
                    color: #ffffff;
                    font-family: 'Courier New', monospace;
                    font-size: 18px;
                    box-shadow: 0 0 10px #86608E;
                    margin-top: 30px;
                ">
                    To connect to the VPN (Linux Edition): <br>
                    - Press <strong>Generate Config file</strong> <br>
                    - Download generated file <code>client_wg.conf</code> <br>
                    - Connect to VPN: <br> 
                        &emsp;  - Add the downloaded file into the WireGuard app. <br>
                        &emsp;  - Alternatively, you can run: <br>
                    <code>sudo apt install wireguard</code><br>
                    <code>sudo mv ~/Downloads/client_wg.conf /etc/wireguard/wg0.conf</code><br>
                    <code>sudo chmod 600 /etc/wireguard/wg0.conf</code><br>
                    <code>sudo wg-quick up wg0</code><br><br>
                    - To confirm the connection, run: <br>
                    <code>ping 10.9.0.1</code><br><br>
                    - To disconnect, run: <br>
                    <code>sudo wg-quick down wg0</code><br>
                    <code>sudo rm /etc/wireguard/wg0.conf</code><br><br>
                    To connect to the VPN (Windows Edition): <br>
                    <a class="feedback-link" href="https://www.wireguard.com/install/" target="_blank">
                    Install WireGuard App for Windows 
                    </a><br>
                    - Press <strong>Generate Config file</strong> <br>
                    - Download generated file <code>client_wg.conf</code> and insert into "Add Empty Tunnel" in Wireguard App <br>
                </div>
            """, unsafe_allow_html=True)



            # VPN Config section
            st.markdown("---")

            st.markdown("<br>", unsafe_allow_html=True)

            # Button to generate WireGuard config
            if st.button("Generate WireGuard Config"):
                try:
                    response = requests.post(
                        f"{BASE_URL_VPN}/generate_config",
                        data={"username": st.session_state.user_id}
                    )
                    if response.status_code == 200:
                        st.success("WireGuard config generated successfully!")
                        config_url = f"{BASE_URL_VPN}/download_config?username={st.session_state.user_id}"
                        st.markdown(f"[📥 Download Config File]({config_url})", unsafe_allow_html=True)
                    else:
                        st.error("Failed to generate config.")
                except requests.exceptions.RequestException as e:
                    st.error(f"Error contacting VPN service: {e}")

            exercise_selection_page()  # Show exercise selection page

            # Logout button and cleanup
            if st.button("Logout"):
                try:
                    # Remove WireGuard config before logout
                    requests.post(f"{BASE_URL_VPN}/remove_config", data={"username": st.session_state.user_id})
                except requests.exceptions.RequestException as e:
                    st.error(f"Could not contact VPN service for logout cleanup: {e}")

                st.session_state.logged_in = False
                st.session_state.user_id = None
                st.session_state.exercise_running = False
                st.query_params.clear()
                st.rerun()

if __name__ == "__main__":
    main()  # Run the Streamlit app


# def exercise_selection_page():
#     set_background('app_wallpaper.jpg')
#     st.markdown("<p class='subheader-text'>Select an Exercise</p>", unsafe_allow_html=True)

#     # Mapping for user-friendly display
#     exercise_labels = {
#         "Dark Contract": "ftp",
#         "Matrix Alert": "ssh",
#         "Da Vinci Node": "http"
#     }
#     level_labels = {
#         "Level 1 - Beginner": "level1",
#         "Level 2 - Intermediate": "level2",
#         "Level 3 - Advanced": "level3"
#     }

#     # Display friendly labels, store internal values
#     exercise_display = st.selectbox("Choose an Exercise", list(exercise_labels.keys()))
#     level_display = st.selectbox("Choose a Level", list(level_labels.keys()))

#     # Lookup actual internal values
#     exercise = exercise_labels[exercise_display]
#     level = level_labels[level_display]

#     if st.button("Start Exercise"):
#         st.session_state.exercise = exercise
#         st.session_state.level = level
#         st.session_state.exercise_running = True
#         st.query_params["user_id"] = st.session_state.user_id
#         st.query_params["exercise"] = exercise
#         st.query_params["level"] = level
#         st.rerun()



