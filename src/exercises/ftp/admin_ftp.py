import streamlit as st  # Import Streamlit for web UI
from jinja2 import Template  # For rendering Jinja2 templates
import os  # For file and path operations
import shutil  # For copying files (used for PCAP file handling)
from pathlib import Path  # For object-oriented filesystem paths
from exercises.admin_base import AdminConfig  # Import abstract base class for admin configs

class FTPConfig(AdminConfig):
    # FTP exercise configuration class inheriting from AdminConfig

    def update_docker_files(self, user, password, level):
        # Generate docker-compose.yml dynamically for FTP based on user and password
        current_dir = Path(__file__).parent  # Get current directory
        # Define paths based on level
        level_number = "1" if "Level 1" in level else "2" if "Level 2" in level else "unknown"
        level_dir = current_dir / f"level{level_number}"  # Path for the level directory
        templates_dir = current_dir.parent / "templates"  # Path for templates directory

        # Select the correct template files based on the level
        compose_template_path = templates_dir / f"ftp_docker_compose_{level_number}.j2"

        # Read and render docker-compose template
        if compose_template_path.exists():
            with open(compose_template_path, "r") as f:
                compose_template = Template(f.read())  # Load Jinja2 template
            rendered_compose = compose_template.render(ftp_user=user, ftp_pass=password)  # Render with user/pass
            
            os.makedirs(level_dir, exist_ok=True)  # Ensure level directory exists
            # Write docker-compose.yml
            with open(level_dir / "docker-compose.yml", "w") as f:
                f.write(rendered_compose)  # Save rendered docker-compose
        else:
            st.error(f"Template for docker-compose not found: {compose_template_path}")

        st.success(f"""FTP Docker files updated for **_{level}_**.  
        To run or edit files manually, navigate to: `{level_dir}`""")

    def configure_level(self, level, shared_dir):
        # Configure the FTP exercise level and provide UI for setting credentials

        if level == "Level 1 - Anonymous FTP":
            st.markdown("""  
    **SCENARIO:** <br> **"You are an unethical hacker and you are hired by “Raymond Reddington” for a job.
    Your goal is to steal a confidential file from “NeuroGen Biotech”, which contains the DNA vaccine and give it to 
    the competitor research center before it is launched. Good luck capturing the flag."**  
    This exercise is a Capture the Flag introductory exercise on FTP where the user learns to : 
    <br>    - Scan open ports with **nmap** tool <br>     - Connect to FTP with **anonymous** login 
    <br>    - Download files on ftp (and get a **flag**). 
    <br> Login credentials are set as **anonymous** by default.  
    Press **'Update FTP Settings'** to configure.  
    """, unsafe_allow_html=True)

            ftp_user = "anonymous"  # Default FTP username
            ftp_pass = ""  # Default FTP password

            if st.button("Update FTP Settings"):
                self.update_docker_files(ftp_user, ftp_pass, level)  # Update docker files with default credentials

        elif level == "Level 2 - FTP Bruteforce":
            st.markdown("""  
    **SCENARIO:** <br> **"You are a security analyst at “NeuroGen Biotech”, an organization specializing in biochemical research. 
            You were informed about a data breach that happened at the FTP server. Someone logged in and stole a confidential medicine recipe. 
            Worse, they changed all the employee passwords, disrupting all the on-going projects. 
            However, the intruder wasn't very thorough and used some very basic credentials. 
            Your mission is to regain access to the server using these potentially weak credentials and find out who compromised the system."**
    <br>     This exercise is a Capture the Flag exercise on FTP where login is done by bruteforce.
    After the login the user has to analyze network traffic through a pcap file. The user learns to : 
    <br>    - Use hydra to crack passwords with wordlists (the user will be given the 500-worst-passwords.txt wordlist)
    <br>    - Use wireshark to analyze network packets and their information and tell apart request-response packets 
    <br> You can configure login credentials but you are advised to **set a password from existing wordlist** so that the exercise can be solved by users. Username choice is indifferent to exercise solution.       
    """, unsafe_allow_html=True)
            
            CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))  # Get current directory
            wordlist_path = os.path.join(CURRENT_DIR, "level2", "500-worst-passwords.txt")  # Path to wordlist

            # Check if the file exists and show download button
            if os.path.exists(wordlist_path):
                with open(wordlist_path, "rb") as f:
                    st.download_button( 
                        label="Download Wordlist Here",
                        data=f,
                        file_name="500-worst-passwords.txt",
                        mime="text/plain",
                        help="Click to download the leaked password file"
                    )
            else:
                st.warning("wordlist file not found.")

            with st.form("ftp_config_form", clear_on_submit=False):
                ftp_user = st.text_input("Enter FTP Username", value="hello")  # Input for FTP username
                ftp_pass = st.text_input("Enter FTP Password", type="password", value="access")  # Input for FTP password
                submitted = st.form_submit_button("Update FTP Settings")
                if submitted:
                    self.update_docker_files(ftp_user, ftp_pass, level)  # Update docker files with provided credentials

        # Remove old log and pcap files for Level 1
        if level == "Level 1 - Anonymous FTP":
            ftp_logs = os.path.join(shared_dir, "ftp_access.log")
            reports_pcap = os.path.join(shared_dir, "Logs", "reported_intrusion.pcap")

            for file in [ftp_logs, reports_pcap]:
                if os.path.exists(file):
                    os.remove(file)

        # Extra options for Level 2: add PCAP file to logs directory
        if level == "Level 2 - FTP Bruteforce":
            st.subheader("Level 2 Extras: PCAP File for log analysis")

            pcap_filename = "reported_intrusion.pcap"

            if st.button("Add PCAP File to Logs directory"):
                CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
                source_pcap = os.path.join(CURRENT_DIR, "level2", "reported_intrusion.pcap")
                logs_dir = os.path.join(shared_dir, "Logs")
                destination_pcap = os.path.join(logs_dir, pcap_filename)

                if os.path.exists(source_pcap):
                    os.makedirs(logs_dir, exist_ok=True)
                    shutil.copyfile(source_pcap, destination_pcap)
                    st.success(f"PCAP file '{pcap_filename}' added to Logs directory!")
                else:
                    st.error(f"PCAP file '{source_pcap}' not found!")