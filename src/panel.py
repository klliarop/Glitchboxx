import streamlit as st  # Import Streamlit for web UI
import os  # For file and path operations
import json  # For handling JSON files

st.set_page_config(
    page_title="Glitchboxx progress dashboard"  
)

PROGRESS_ROOT = os.path.join(os.path.dirname(__file__), "progress")  # Root directory for progress files

list_of_protocols_and_user_ids = {
    "ftp": [],
    "ssh": [],
    "http": []
}  # Dictionary to track completed users per protocol

def display_user_progress(data, user_id, protocol, level):
    # Display a user's progress in a styled container
    with st.container():
        st.markdown(
            f"""
            <div style='
                background-color: #86608E;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                margin-bottom: 20px;
            '>
            <h4>User {user_id} </h4>
            """,
            unsafe_allow_html=True
        )

        progress_steps = [key for key in data if key.startswith("step")]  # Find all step keys
        total_steps = len(progress_steps)  # Total number of steps
        completed_steps = sum(1 for step in progress_steps if data[step])  # Count completed steps
        progress_percentage = (completed_steps / total_steps) * 100 if total_steps > 0 else 0  # Calculate progress

        st.write(f"Completed Steps: {completed_steps} / {total_steps}")  # Show completed steps
        st.progress(int(progress_percentage))  # Show progress bar

        if completed_steps == total_steps:
            list_of_protocols_and_user_ids[protocol].append(user_id)  # Track users who completed all steps

        st.markdown("</div>", unsafe_allow_html=True)  # Close the styled container

def load_all_progress_files(selected_service, selected_level):
    """Loads progress files for the selected protocol and level."""
    user_progress_data = []

    level_path = os.path.join(PROGRESS_ROOT, selected_service, selected_level)  # Path to progress files
    if not os.path.isdir(level_path):
        return []

    for filename in os.listdir(level_path):
        if filename.endswith(".json"):
            file_path = os.path.join(level_path, filename)
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)  # Load user progress data
                    user_id = os.path.splitext(filename)[0]  # Extract user ID from filename
                    user_progress_data.append((user_id, data, selected_service, selected_level))
            except Exception as e:
                st.warning(f"Failed to load {file_path}: {e}")  # Warn if file can't be loaded

    return user_progress_data  # Return list of user progress entries

def main():
    st.title("User Progress Dashboard")  # Set the page title

    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))  # Get current directory
    services = ["ftp", "ssh", "http"]  # List of supported services
    levels = ["level1", "level2"]  # List of supported levels

    selected_service = st.selectbox("Choose a service:", services)  # Service selection dropdown
    selected_level = st.selectbox("Choose a level:", levels)  # Level selection dropdown

    if st.button("Select"):
        st.session_state.services = selected_service
        st.session_state.level = selected_level
        st.session_state.exercise_running = True
        st.query_params["exercise"] = selected_service
        st.query_params["level"] = selected_level
        st.rerun()  # Rerun the app with new selections

    SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "../../../../"))  # Calculate source directory
#PROGRESS_DIR = os.path.join(SRC_DIR, "progress", selected_service, selected_level)  # Path to progress directory

    st.subheader(f"Showing progress for  `{selected_service} / {selected_level}` ")  # Show current selection

    progress_entries = load_all_progress_files(selected_service, selected_level)  # Load progress data

    if not progress_entries:
        st.info("No progress data found.")  # Inform if no data
        return

    cols = st.columns(2)  # Two columns for displaying user cards
    for idx, (user_id, data, protocol, level) in enumerate(progress_entries):
        with cols[idx % 2]:
            display_user_progress(data, user_id, protocol, level)  # Show each user's progress

    st.markdown("### ✅ Completed Users Summary")  # Section for completed users

    any_completed = False  # Flag to check if any user completed all steps

    for protocol, user_ids in list_of_protocols_and_user_ids.items():
        if user_ids:
            any_completed = True
            st.write(f"**{protocol.upper()}** - {level}  : {'  ,  '.join(user_ids)} \n")  # List completed users

    if not any_completed:
        st.write("No users have completed all steps yet.")  # Inform if none completed

if __name__ == "__main__":
    main()  # Run the Streamlit app