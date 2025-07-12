import streamlit as st  # Import Streamlit for web UI
import os  # For file and path operations
import base64  # For encoding images to base64 for backgrounds
import re  # For regular expressions
from exercises.ftp import admin_ftp  # Import FTP admin config
from exercises.ssh import admin_ssh  # Import SSH admin config
from exercises.http import admin_http  # Import HTTP admin config
from database.admin_db_manager import is_admin_user  # Import admin authentication

#import bcrypt  # For password hashing (used in admin login)

st.set_page_config(
    page_title="Glitchboxx admin panel"
)


# Function to set the background image
def set_background(image_file):
    base_dir = os.path.dirname(os.path.abspath(__file__))  # Get base directory
    wallpapers_dir = os.path.join(base_dir, "wallpapers")  # Path to wallpapers
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

set_background('admin_wallpaper.jpg')  # Set the admin panel background

# --- Admin Login Section ---
if "admin_logged_in" not in st.session_state or not st.session_state["admin_logged_in"]:
    st.title("Admin Login")  # Show login title
    with st.form("admin_login_form"):
        username = st.text_input("Admin Username")  # Input for admin username
        password = st.text_input("Admin Password", type="password")  # Input for admin password
        login_button = st.form_submit_button("Login")  # Login button
        if login_button:
            if is_admin_user(username, password):  # Check admin credentials
                st.session_state["admin_logged_in"] = True  # Set login state
                st.session_state["admin_username"] = username  # Store admin username
                st.success("Login successful!")  # Show success message
                st.rerun()  # Rerun app to show admin panel
            else:
                st.error("Invalid admin credentials")  # Show error message
        st.stop()  # Stop execution if not logged in
else:
    username = st.session_state["admin_username"]  # Get logged-in admin username

# --- Main Admin Panel ---
def edit_files(exercise_type, level, config_func):

    # Extract level number from level string
    match = re.search(r'Level (\d+)', level)
    if not match:
        st.error("Could not determine level number.")  # Show error if level not found
        return
    level_number = f"level{match.group(1)}"  # Format level number

    # Build shared directory path for the exercise and level
    base_path = os.path.dirname(__file__)
    exercise_folder = exercise_type.lower()
    shared_dir = os.path.join(base_path, "exercises", exercise_folder, level_number, "shared")

    # Run the configuration function for the selected exercise and level
    config_func(level, shared_dir)

    # File Editor Section
    st.subheader("📁 Edit Default files")
    st.markdown(""" Here you can edit files that will appear on the server of each exercise.\n
    You are advised to not edit content of flag.txt file as it is used as answer in exercises.
        """, unsafe_allow_html=True)

    if os.path.isdir(shared_dir):
        st.write(f"Path: `{shared_dir}`")  # Show shared directory path

        # Recursively list all files and subfolders in shared_dir
        file_paths = []
        subfolders = set()
        for root, dirs, filenames in os.walk(shared_dir):
            rel_dir = os.path.relpath(root, shared_dir)
            if rel_dir != ".":
                subfolders.add(rel_dir)
            for filename in filenames:
                # Skip hidden files and critical files - This was added for http level3 as a bootstrap 
                if filename.startswith(".") or filename in ("Dockerfile", "app.py"):
                    continue
                full_path = os.path.join(root, filename)
                rel_path = os.path.relpath(full_path, shared_dir)
                file_paths.append(rel_path)
        file_paths.sort()
        subfolders = sorted(list(subfolders))

        if file_paths:
            selected_file = st.selectbox("Choose a file to edit:", file_paths)  # File selection dropdown
            file_path = os.path.join(shared_dir, selected_file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()  # Read file content
                new_content = st.text_area("Edit content", value=content, height=300)  # Text area for editing
                if st.button("Save Changes"):
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(new_content)  # Save edited content
                    st.success(f"'{selected_file}' saved.")  # Show success message
            except UnicodeDecodeError:
                st.warning(f"'{selected_file}' is a binary or non-text file (e.g., PCAP) and cannot be edited here.")
            except Exception as e:
                st.error(f"Could not open file: {e}")

        st.markdown("---")  # Separator

        # Upload Section
        st.markdown("### 📤 Upload a New File")
        st.markdown(""" To upload file chooose existing directory or create new.
            """, unsafe_allow_html=True)
        upload_target = st.selectbox("Choose existing folder (or leave empty for Base directory):", [""] + subfolders)
        new_folder = st.text_input("Or create a new folder:")  # Input for new folder name
        uploaded_file = st.file_uploader("Upload a file")  # File uploader

        # Make upload button visible only when a file is selected
        if uploaded_file:
            upload_button = st.button("Upload File")
            if upload_button:
                # Determine final folder for upload
                if new_folder:
                    upload_dir = os.path.join(shared_dir, new_folder)
                    os.makedirs(upload_dir, exist_ok=True)
                elif upload_target and upload_target != "(root)":
                    upload_dir = os.path.join(shared_dir, upload_target)
                else:
                    upload_dir = shared_dir

                save_path = os.path.join(upload_dir, uploaded_file.name)
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())  # Save uploaded file
                st.success(f"Uploaded '{uploaded_file.name}' to `{os.path.relpath(upload_dir, shared_dir)}`")
    else:
        st.warning("Shared directory not found.")  # Warn if shared directory does not exist

# --- Admin Panel UI ---
st.title("Glitchboxx Admin Panel")  # Set panel title
st.markdown(""" **Choose exercise type and level to configure**
        """, unsafe_allow_html=True)
exercise_type = st.selectbox("Select Exercise Type", ["FTP", "SSH", "HTTP"])  # Exercise type selection

if exercise_type == "FTP":
    level = st.selectbox("Select Level", ["Level 1 - Anonymous FTP", "Level 2 - FTP Bruteforce"])  # FTP levels
    edit_files("FTP", level, admin_ftp.FTPConfig().configure_level)

elif exercise_type == "SSH":
    level = st.selectbox("Select Level", ["Level 1 - SSH Password Recovery", "Level 2 - SSH Root Escalation"])  # SSH levels
    edit_files("SSH", level, admin_ssh.SSHConfig().configure_level)

elif exercise_type == "HTTP":
    level = st.selectbox("Select Level", [
        "Level 1 - HTTP Stolen Credentials from pcap",
        "Level 2 - HTTP Packet Sniffing - Live Capture",
        "Level 3 - HTTP Path Traversal & Fuzzing"
    ])
    edit_files("HTTP", level, admin_http.HTTPConfig().configure_level)
