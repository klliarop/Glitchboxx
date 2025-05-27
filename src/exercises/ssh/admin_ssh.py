import streamlit as st
from jinja2 import Template
import os
from pathlib import Path
import bcrypt
from exercises.exercise_base import ExerciseConfig

class SSHConfig(ExerciseConfig):

    def update_docker_files(self, user, password, level):
        """Generate docker-compose.yml, Dockerfile, and reset_environment.sh dynamically for SSH."""
        # Get the directory where this script is located
        current_dir = Path(__file__).parent
        
        # Define paths based on level
        level_number = "1" if "Level 1" in level else "2" if "Level 2" in level else "unknown"
        level_dir = current_dir / f"level{level_number}"
        templates_dir = current_dir.parent / "templates"
        
        # Ensure directories exist
        level_dir.mkdir(exist_ok=True)
        
        # Select the correct template files based on the level
        compose_template_path = templates_dir / f"ssh_docker_compose_{level_number}.j2"
        dockerfile_template_path = templates_dir / f"ssh_dockerfile_{level_number}.j2"
        reset_template_path = templates_dir / "reset_environment.sh.j2"
    
        # Read and render docker-compose template
        if compose_template_path.exists():
            with open(compose_template_path, "r") as f:
                compose_template = Template(f.read())
            rendered_compose = compose_template.render(ssh_user=user, ssh_pass=password)
            
            # Write docker-compose.yml
            with open(level_dir / "docker-compose.yml", "w") as f:
                f.write(rendered_compose)
        else:
            st.error(f"Template for docker-compose not found: {compose_template_path}")
        
        # Read and render Dockerfile template
        if dockerfile_template_path.exists():
            with open(dockerfile_template_path, "r") as f:
                dockerfile_template = Template(f.read())
            rendered_dockerfile = dockerfile_template.render(ssh_user=user, ssh_pass=password)
            
            # Write Dockerfile
            with open(level_dir / "Dockerfile", "w") as f:
                f.write(rendered_dockerfile)
        else:
            st.error(f"Template for Dockerfile not found: {dockerfile_template_path}")
        
        # Read and render reset_environment.sh template (for Level 2 only)
        if level_number == "2" and reset_template_path.exists():
            with open(reset_template_path, "r") as f:
                reset_template = Template(f.read())
            rendered_reset = reset_template.render(ssh_user=user)
            
            # Write reset_environment.sh
            with open(level_dir / "reset_environment.sh", "w") as f:
                f.write(rendered_reset)
            # Make it executable
            os.chmod(level_dir / "reset_environment.sh", 0o755)
        elif level_number == "2":
            st.error(f"Template for reset_environment.sh not found: {reset_template_path}")
        
        st.success(f"SSH Docker files updated for {level}. To run or edit files manually navigate to '{level_dir}' ")


    def configure_level(self, level, shared_dir):
        if level == "Level 1 - SSH Password Recovery":
            st.markdown("""  
                **SCENARIO:** <br> **"Agent Smith, an AI bot uncontrolled by the Matrix's constraints, has created a server where his friend
                bots are carefully crafting the 'Reality_Override.exe'. This executable is designed to permanently convert all realities into 
                a Smith-controlled Matrix. This process is irreversible so you have to hurry up to delete this file."** 
                <br>
                This exercise is a Capture the Flag exercise on SSH where **login is done after cracking a downloaded hash with john the ripper**.
                After login the user has to **find hidden file** with password of the zip containing the 'Reality_Override.exe' and the flag.
                <br> You can configure login credentials but you are advised to **set a password from the rockyou wordlist** so that the exercise can be solved by users. Username is already set to **"Agent_Smith"**.       
                """, unsafe_allow_html=True)
     
            with st.form("ssh_config_form", clear_on_submit=False):
                ssh_user = st.text_input("SSH Username", value="Agent_Smith", disabled=True)
                ssh_pass = st.text_input("Enter SSH Password", type="password", value="tinkerbell")

                submitted = st.form_submit_button("Update SSH Settings")
                if submitted:
                    self.update_docker_files(ssh_user, ssh_pass, level)

                    generated_hash = generate_bcrypt_hash(ssh_pass)
                    level_number = "1" if "Level 1 - SSH Password Recovery" in level else "unknown"
                    level_dir = Path(__file__).parent / f"level{level_number}"
                    hash_file_path = level_dir / "hash.txt"
                    with open(hash_file_path, "w") as f:
                        f.write(generated_hash)
                    st.info(f"Bcrypt hash saved to: `{hash_file_path}`")
                    self.update_docker_files(ssh_user, ssh_pass, level)


        elif level == "Level 2 - SSH Root Escalation":
            st.markdown("""  **SCENARIO:** <br> **"After his last defeat and the deletion of Reality_Override.exe, Agent Smith reconstructed himself from corrupted backup data
                deep inside the simulation. Learning from his previous mistakes, he crafted a new file: 'Super_Reality_Override.exe' ,
                that is now protected by strict root-level privileges. The new file doesn't just overwrite reality—it merges all simulations
                into one dominant hyperreality under Smith’s control."** <br> 
                **Your objective: <br> - Infiltrate the server.<br> - Escalate to root privileges.<br> - Locate and delete Super_Reality_Override.exe before it boots.<br>**
                This exercise is a Capture the Flag exercise on SSH where **login is done by bruteforce** and then user has to **escalate privileges to root** and get root flag.
                The escalation can be done by executing a c file that is already present in the server after the right privileges are granted.
                <br> You can configure login credentials but you are advised to **set a password from existing wordlist** so that the exercise can be solved by users. Username is already set to **"Smith_bot"**.       
                """, unsafe_allow_html=True)

            with st.form("ssh_config_form", clear_on_submit=False):
                ssh_user = "Smith_bot"
                st.text_input("SSH Username", value="Smith_bot", disabled=True)
                ssh_pass = st.text_input("Enter SSH Password", value="3rJs1la7qE")
                submitted = st.form_submit_button("Update SSH Settings")
                if submitted:
                    self.update_docker_files(ssh_user, ssh_pass, level)


def generate_bcrypt_hash(password):
    """Generates a bcrypt hash for the given password."""
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_password.decode('utf-8')












