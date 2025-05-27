import streamlit as st
import os
import json

PROGRESS_ROOT = os.path.join(os.path.dirname(__file__), "progress")

list_of_protocols_and_user_ids = {
    "ftp": [],
    "ssh": [],
    "http": []
}

def display_user_progress(data, user_id, protocol, level):
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

        progress_steps = [key for key in data if key.startswith("step")]
        total_steps = len(progress_steps)
        completed_steps = sum(1 for step in progress_steps if data[step])
        progress_percentage = (completed_steps / total_steps) * 100 if total_steps > 0 else 0

        st.write(f"Completed Steps: {completed_steps} / {total_steps}")
        st.progress(int(progress_percentage))

        if completed_steps == total_steps:
            list_of_protocols_and_user_ids[protocol].append(user_id)

        st.markdown("</div>", unsafe_allow_html=True)


def load_all_progress_files(selected_service, selected_level):
    """Loads progress files for the selected protocol and level."""
    user_progress_data = []

    level_path = os.path.join(PROGRESS_ROOT, selected_service, selected_level)
    if not os.path.isdir(level_path):
        return []

    for filename in os.listdir(level_path):
        if filename.endswith(".json"):
            file_path = os.path.join(level_path, filename)
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                    user_id = os.path.splitext(filename)[0]
                    user_progress_data.append((user_id, data, selected_service, selected_level))
            except Exception as e:
                st.warning(f"Failed to load {file_path}: {e}")

    return user_progress_data



def main():
    st.title("User Progress Dashboard")

    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    services = ["ftp", "ssh", "http"]
    levels = ["level1", "level2"]

    selected_service = st.selectbox("Choose a service:", services)
    selected_level = st.selectbox("Choose a level:", levels)

    if st.button("Select"):
        st.session_state.services = selected_service
        st.session_state.level = selected_level
        st.session_state.exercise_running = True
        st.query_params["exercise"] = selected_service
        st.query_params["level"] = selected_level
        st.rerun()


    SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "../../../../"))
    PROGRESS_DIR = os.path.join(SRC_DIR, "progress", selected_service, selected_level)

    st.subheader(f"Showing progress for  `{selected_service} / {selected_level}` ")

    progress_entries = load_all_progress_files(selected_service, selected_level)

    if not progress_entries:
        st.info("No progress data found.")
        return

    # for user_id, data, protocol, level in progress_entries:
    #     display_user_progress(data, user_id, protocol, level)


    cols = st.columns(2)  # Two cards per row
    for idx, (user_id, data, protocol, level) in enumerate(progress_entries):
        with cols[idx % 2]:
            display_user_progress(data, user_id, protocol, level)


    st.markdown("### ✅ Completed Users Summary")

    any_completed = False

    for protocol, user_ids in list_of_protocols_and_user_ids.items():
        if user_ids:
            any_completed = True
            st.write(f"**{protocol.upper()}** - {level}  : {'  ,  '.join(user_ids)} \n")

    if not any_completed:
        st.write("No users have completed all steps yet.")


if __name__ == "__main__":
    main()
