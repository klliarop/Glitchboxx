 cat start.py
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
BASE_URL_VPN = f"http://{get_vpn_server_ip()}:5003"

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

