import streamlit as st  # Import Streamlit for web UI
import json  # For saving/loading JSON config files
from pathlib import Path  # For object-oriented filesystem paths
from exercises.admin_base import AdminConfig  # Import abstract base class for admin configs

class HTTPConfig(AdminConfig):
    # HTTP exercise configuration class inheriting from AdminConfig


    def update_docker_files(self, ftp_user, ftp_pass, ftp_port, http_port, level):
        """Save admin config for HTTP Level 1 or 2."""
        config = {
            "ftp_user": ftp_user,
            "ftp_pass": ftp_pass,
            "ftp_port": ftp_port,
            "http_port": http_port
        }
        # Choose config file based on level
        if "Level 2" in level:
            config_filename = "http_level2.json"
        else:
            config_filename = "http_level1.json"
        config_path = Path(__file__).parent.parent / f"templates/json_configs/{config_filename}"
        with open(config_path, "w") as f:
            json.dump(config, f)
        st.success(f"HTTP config saved for {level}.")

    def configure_level(self, level, shared_dir):
        # Configure the HTTP exercise level and provide UI for setting credentials or ports
        if level == "Level 1 - HTTP Stolen Credentials from pcap":
            st.markdown("""  
                **SCENARIO:** <br> **"You’re a freelance art thief, always on the lookout for valuable pieces to enrich your personal collection.
                Your latest intel points to a recently acquired Renaissance painting — possibly a long-lost work by Da Vinci — purchased by a private gallery and now scheduled for delivery.
                The gallery uses outdated tech and the gallery's order and delivery system is vulnerable to eavesdropping so your objective is steal intelligence
                related to this transaction and become a node of the network."**

                This exercise is a Capture the Flag exercise on http where  user **logs in an ftp server** with anonymous login and finds a pcap file.
                This pcap contains a **live capture from a login session** and the user has to find **login credentials** as well as **order id.** 
                Then the user should **enter a website** with these credentials and change delivery address to this specific order (by order id) and then retrieve the flag.
                <br> This exercise contains 2 exposed containers (ftp and http) and a database container that is not exposed and used to handle http processes.
                
                You can configure login credentials to the ftp server to add difficulty to user (bruteforce attack).
                If so, the users should be hinted by a wordlist that they can use to crack the password.
                Login credentials to the website cannot be configured as they originate from a live capture and are on a pcap file.
                """, unsafe_allow_html=True)
     
            with st.form("http_config_form", clear_on_submit=False):
                ftp_user = st.text_input("FTP Username", value="anonymous")
                ftp_pass = st.text_input("FTP Password", type="password", value="")
                ftp_port = st.number_input("FTP Port", min_value=1, max_value=65535, value=21, step=1)
                http_port = st.number_input("HTTP Port", min_value=1, max_value=65535, value=8080, step=1)
                
                submitted = st.form_submit_button("Update HTTP Settings")
                if submitted:
                    self.update_docker_files(ftp_user, ftp_pass, str(ftp_port), str(http_port), level)


        elif level == "Level 2 - HTTP Packet Sniffing - Live Capture":
            st.markdown("""  
                **SCENARIO:** <br> **"You’ve infiltrated a private network long rumored to launder high-value Renaissance artworks — including a few allegedly painted by Da Vinci himself —
                through "state-of-the-art" banking channels that haven’t been updated since the Renaissance. Their defenses are outdated and unencrypted and sensitive data flows through in plaintext."**   
        
                This exercise is a Capture the Flag exercise on http where the user does live capture of packets on a bank's internal network with wireshark.
                There he can find valid or invalid login credentials to a website, use them to enter the website and then make a money transfer to get the flag.
                <br> This exercise contains 2 exposed containers (ftp and http) and a database container that is not exposed and used to handle http processes.
                The ftp server serves no purpose in this exercise but is there to add difficulty and distract the user.  
                You can configure the ports that the http and ftp server will appear on the nmap scan.
                """, unsafe_allow_html=True)

            with st.form("http_config_form", clear_on_submit=False):
                ftp_user = st.text_input("FTP Username", value="anonymous")
                ftp_pass = st.text_input("FTP Password", type="password", value="")
                ftp_port = st.number_input("FTP Port", min_value=1, max_value=65535, value=21, step=1)
                http_port = st.number_input("HTTP Port", min_value=1, max_value=65535, value=8080, step=1)
                
                submitted = st.form_submit_button("Update Settings")
                if submitted:
                   # self.update_docker_files(ftp_user, ftp_pass, ftp_port, http_port, level)
                    self.update_docker_files(ftp_user, ftp_pass, str(ftp_port), str(http_port), level)

        elif level == "Level 3 - HTTP Path Traversal & Fuzzing":
            st.markdown("""
                **SCENARIO:** <br> **"You were a backend dev at Nexora, a small AI startup you helped build from the ground up. Two weeks ago, the founders sold the company overnight without giving any notice to employees. 
                Your last major contribution, a research project called “Axis” - a launch-ready AI model built from scratch by you and your team is now gone without any credit to the team.
                But you remember something the new owners don’t:
                Nexora always dumped internal dev files into their public-facing test server. You warned them about it but never fixed it. 
                There’s a leftover utility meant to provide access to documentation — pointless to outsiders, but valuable if you know the projects to guide you to valuable files.
                You remember a test utility was used internally at Nexora for file previews."**

                **"This exercise focuses on path traversal and fuzzing vulnerabilities in a web application. 
                The user must discover hidden directories and files, exploit path traversal, and retrieve the flag."**
                <br>
                You can edit the files and folders available to the user in the file editor below.
                """, unsafe_allow_html=True)
            # Optionally, add any Level 3-specific configuration fields here
















# import streamlit as st
# from jinja2 import Template
# import os
# from pathlib import Path
# from exercises.admin_base import AdminConfig
# import json

# class HTTPConfig(AdminConfig):


#     def update_docker_files(self, ftp_user, ftp_pass, level):
#         """Save admin config for HTTP Level."""
#         config = {
#             "ftp_user": ftp_user,
#             "ftp_pass": ftp_pass
#         }
#         config_path = Path(__file__).parent.parent / "templates/json_configs/http_level1.json"
#         with open(config_path, "w") as f:
#             json.dump(config, f)
#         st.success(f"HTTP Level 1 config saved for {level}.")


#     # def update_docker_files(self, user, password, level):
#     #     """Generate docker-compose.yml dynamically for HTTP."""
#     #     # Get the directory where this script is located
#     #     current_dir = Path(__file__).parent
        
#     #     # Define paths based on level
#     #     level_number = "1" if "Level 1" in level else "2" if "Level 2" in level else "unknown"
#     #     level_dir = current_dir / f"level{level_number}"
#     #     templates_dir = current_dir.parent / "templates"
        
#     #     # Ensure directories exist
#     #     level_dir.mkdir(exist_ok=True)
        
#     #     # Select the correct template files based on the level
#     #     compose_template_path = templates_dir / f"http_docker_compose_{level_number}.j2"

#     #     # Read and render docker-compose template
#     #     if compose_template_path.exists():
#     #         if level == "Level 1 - HTTP Stolen Credentials from pcap":
#     #             with open(compose_template_path, "r") as f:
#     #                 compose_template = Template(f.read())
#     #             rendered_compose = compose_template.render(ftp_user=user, ftp_pass=password)
#     #         elif level == "Level 2 - HTTP Packet Sniffing - Live Capture":
#     #             with open(compose_template_path, "r") as f:
#     #                 compose_template = Template(f.read())
#     #             rendered_compose = compose_template.render(http_port=user, ftp_port=password)

#     #         # Write docker-compose.yml
#     #         with open(level_dir / "docker-compose.yml.j2", "w") as f:
#     #             f.write(rendered_compose)
#     #     else:
#     #         st.error(f"Template for docker-compose not found: {compose_template_path}")

#     #     st.success(f"HTTP Exercise Docker files updated for {level}. To run or edit files manually navigate to '{level_dir}' ")


#     def configure_level(self, level, shared_dir):
#         if level == "Level 1 - HTTP Stolen Credentials from pcap":
#             st.markdown("""  
#                 **SCENARIO:** <br> **"You’re a freelance art thief, always on the lookout for valuable pieces to enrich your personal collection.
#                 Your latest intel points to a recently acquired Renaissance painting — possibly a long-lost work by Da Vinci — purchased by a private gallery and now scheduled for delivery.
#                 The gallery uses outdated tech and the gallery's order and delivery system is vulnerable to eavesdropping so your objective is steal intelligence
#                 related to this transaction and become a node of the network."**

#                 This exercise is a Capture the Flag exercise on http where  user **logs in an ftp server** with anonymous login and finds a pcap file.
#                 This pcap contains a **live capture from a login session** and the user has to find **login credentials** as well as **order id.** 
#                 Then the user should **enter a website** with these credentials and change delivery address to this specific order (by order id) and then retrieve the flag.
#                 <br> This exercise contains 2 exposed containers (ftp and http) and a database container that is not exposed and used to handle http processes.
                
#                 You can configure login credentials to the ftp server to add difficulty to user (bruteforce attack).
#                 If so, the users should be hinted by a wordlist that they can use to crack the password.
#                 Login credentials to the website cannot be configured as they originate from a live capture and are on a pcap file.
#                 """, unsafe_allow_html=True)
     
#             with st.form("http_config_form", clear_on_submit=False):
#                 ftp_user = st.text_input("FTP Username", value="anonymous")
#                 ftp_pass = st.text_input("Enter FTP Password", type="password", value="")

#                 submitted = st.form_submit_button("Update HTTP Settings")
#                 if submitted:
#                     self.update_docker_files(ftp_user, ftp_pass, level)


#         elif level == "Level 2 - HTTP Packet Sniffing - Live Capture":
            
#             st.markdown("""  
#                 **SCENARIO:** <br> **"You’ve infiltrated a private network long rumored to launder high-value Renaissance artworks — including a few allegedly painted by Da Vinci himself —
#                 through "state-of-the-art" banking channels that haven’t been updated since the Renaissance. Their defenses are outdated and unencrypted and sensitive data flows through in plaintext."**   
        
#                 This exercise is a Capture the Flag exercise on http where the user does live capture of packets on a bank's internal network with wireshark.
#                 There he can find valid or invalid login credentials to a website, use them to enter the website and then make a money transfer to get the flag.
#                 <br> This exercise contains 2 exposed containers (ftp and http) and a database container that is not exposed and used to handle http processes.
#                 The ftp server serves no purpose in this exercise but is there to add difficulty and distract the user.  
#                 You can configure the ports that the http and ftp server will appear on the nmap scan.
#                 """, unsafe_allow_html=True)

#             with st.form("http_config_form", clear_on_submit=False):
#                 http_port = st.text_input("HTTP Server Port", value=8080)
#                 ftp_port = st.text_input("FTP Server Port", value=21)
#                 submitted = st.form_submit_button("Update Settings")
#                 if submitted:
#                     self.update_docker_files(http_port, ftp_port, level)


#             # with st.form("http2_config_form", clear_on_submit=False):
#             #     ftp_user = st.text_input("FTP Username", value="anonymous")
#             #     ftp_pass = st.text_input("FTP Password", value="")
#             #     submitted = st.form_submit_button("Update Settings")
#             #     if submitted:
#             #        # self.update_docker_files(ftp_user, ftp_pass, level = "Level 1 - HTTP Stolen Credentials from pcap")

#             #         current_dir = Path(__file__).parent
#             #         dir = current_dir.parent / "templates"
        
#             #         compose_template_path = dir / f"http_docker_compose_2.j2"
#             #         with open(compose_template_path, "r") as f:
#             #             compose_template = Template(f.read())
#             #         rendered_compose = compose_template.render(ftp_user=ftp_user, ftp_pass=ftp_pass)
#             #         level_dir = current_dir / f"level2"
#             #         with open(level_dir / "docker-compose.yml", "w") as f:
#             #             f.write(rendered_compose)
#             #         st.success(f"HTTP Exercise Docker files updated for {level}. To run or edit files manually navigate to '{level_dir}' ")






























#     # def configure_level(self, level, shared_dir):
#     #     # Implement HTTP-specific configuration UI and logic here
#     #     pass

#     # def update_docker_files(self, user, password, level):
#     #     # Implement HTTP docker-compose and Dockerfile update logic here
#     #     current_dir = Path(__file__).parent
#     #     level_number = "1" if "Level 1" in level else "2" if "Level 2" in level else "unknown"
#     #     level_dir = current_dir / f"level{level_number}"
#     #     templates_dir = current_dir.parent / "templates"
#     #     compose_template_path = templates_dir / f"http_docker_compose_{level_number}.j2"
#     #     dockerfile_template_path = templates_dir / f"http_dockerfile_{level_number}.j2"

#     #     if compose_template_path.exists():
#     #         with open(compose_template_path, "r") as f:
#     #             compose_template = Template(f.read())
#     #         rendered_compose = compose_template.render(http_user=user, http_pass=password)
#     #         os.makedirs(level_dir, exist_ok=True)
#     #         with open(level_dir / "docker-compose.yml", "w") as f:
#     #             f.write(rendered_compose)
#     #         st.success(f"HTTP Docker files updated for **_{level}_**. To run or edit files manually, navigate to: `{level_dir}`")
#     #     else:
#     #         st.error(f"Template for docker-compose not found: {compose_template_path}")