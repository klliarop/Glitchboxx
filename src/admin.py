import streamlit as st
import os
import base64
import re
from exercises.ftp import admin_ftp
from exercises.ssh import admin_ssh
from exercises.http import admin_http

# Function to set the background image
def set_background(image_file):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    wallpapers_dir = os.path.join(base_dir, "wallpapers")
    image_path = os.path.join(wallpapers_dir, image_file)
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

set_background('admin_wallpaper.jpg')


# Function to extract level and show file editor
def edit_files(exercise_type, level, config_func):
    import re

    # Extract level number
    match = re.search(r'Level (\d+)', level)
    if not match:
        st.error("Could not determine level number.")
        return
    level_number = f"level{match.group(1)}"

    # Build shared directory path
    base_path = os.path.dirname(__file__)
    exercise_folder = exercise_type.lower()
    shared_dir = os.path.join(base_path, "exercises", exercise_folder, level_number, "shared")

    # Run config function
    config_func(level, shared_dir)


    # File Editor
    st.subheader("📁 Edit Default files")
    st.markdown(""" Here you can edit files that will appear on the server of each exercise.\n
    You are advised to not edit content of flag.txt file as it is used as answer in exercises.
        """, unsafe_allow_html=True)

    if os.path.isdir(shared_dir):
        st.write(f"Path: `{shared_dir}`")

        # Recursively list all files
        file_paths = []
        subfolders = set()
        for root, dirs, filenames in os.walk(shared_dir):
            rel_dir = os.path.relpath(root, shared_dir)
            if rel_dir != ".":
                subfolders.add(rel_dir)
            for filename in filenames:
                if not filename.startswith("."):
                    full_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(full_path, shared_dir)
                    file_paths.append(rel_path)
        file_paths.sort()
        subfolders = sorted(list(subfolders))

        # File editor
        # if file_paths:
        #     selected_file = st.selectbox("Choose a file to edit:", file_paths)
        #     file_path = os.path.join(shared_dir, selected_file)
        #     with open(file_path, "r") as f:
        #         content = f.read()

        #     new_content = st.text_area("Edit content", value=content, height=300)
        #     if st.button("Save Changes"):
        #         with open(file_path, "w") as f:
        #             f.write(new_content)
        #         st.success(f"'{selected_file}' saved.")
        # else:
        #     st.info("No files found in shared folder.")

        if file_paths:
            selected_file = st.selectbox("Choose a file to edit:", file_paths)
            file_path = os.path.join(shared_dir, selected_file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                new_content = st.text_area("Edit content", value=content, height=300)
                if st.button("Save Changes"):
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    st.success(f"'{selected_file}' saved.")
            except UnicodeDecodeError:
                st.warning(f"'{selected_file}' is a binary or non-text file (e.g., PCAP) and cannot be edited here.")
            except Exception as e:
                st.error(f"Could not open file: {e}")






        st.markdown("---")

        # Upload Section
        st.markdown("### 📤 Upload a New File")
        st.markdown(""" To upload file chooose existing directory or create new.
            """, unsafe_allow_html=True)
        upload_target = st.selectbox("Choose existing folder (or leave empty for Base directory):", [""] + subfolders)
        new_folder = st.text_input("Or create a new folder:")
        uploaded_file = st.file_uploader("Upload a file")


        # Make upload button visible only when a file is selected
        if uploaded_file:
            upload_button = st.button("Upload File")
            if upload_button:
                # Determine final folder
                if new_folder:
                    upload_dir = os.path.join(shared_dir, new_folder)
                    os.makedirs(upload_dir, exist_ok=True)
                elif upload_target and upload_target != "(root)":
                    upload_dir = os.path.join(shared_dir, upload_target)
                else:
                    upload_dir = shared_dir

                save_path = os.path.join(upload_dir, uploaded_file.name)
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success(f"Uploaded '{uploaded_file.name}' to `{os.path.relpath(upload_dir, shared_dir)}`")
    else:
        st.warning("Shared directory not found.")


# Main Panel
st.title("Glitchbox Admin Panel")
st.markdown(""" **Choose exercise type and level to configure**
        """, unsafe_allow_html=True)
exercise_type = st.selectbox("Select Exercise Type", ["FTP", "SSH", "HTTP"])

if exercise_type == "FTP":
    level = st.selectbox("Select Level", ["Level 1 - Anonymous FTP", "Level 2 - FTP Bruteforce"])
    edit_files("FTP", level, admin_ftp.FTPConfig().configure_level)

elif exercise_type == "SSH":
    level = st.selectbox("Select Level", ["Level 1 - SSH Password Recovery", "Level 2 - SSH Root Escalation"])
    edit_files("SSH", level, admin_ssh.SSHConfig().configure_level)

elif exercise_type == "HTTP":
    level = st.selectbox("Select Level", ["Level 1 - HTTP Stolen Credentials from pcap", "Level 2 - HTTP Packet Sniffing - Live Capture"])
    edit_files("HTTP", level, admin_http.HTTPConfig().configure_level)
