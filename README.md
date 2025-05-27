# Cyber Range Sandbox
This project provides a Cyber Range Sandbox for security concepts and techniques. It includes an admin panel for configuring exercises and user panels for students to interact with.

# Prerequisites (system level requirements)
Before running this project, ensure you have the following installed:

##3.8 or 3.6????????
- Python 3.6: You can download Python from [python.org](https://www.python.org/).
##3.8 or 3.6????????

- Docker and Docker Compose: Required for running the servers. Follow the official Docker installation instructions for your operating system:
    * [Docker Installation](https://docs.docker.com/get-docker/)
    * Note: Please ensure that docker compose is installed as well.

- Wireshark (Optional): Needed to analyze the provided PCAP files. Download it from [wireshark.org](https://www.wireshark.org/).

# Setup

1.  Clone the Repository:

bash:
    git clone [your-repository-url]
    cd [your-repository-directory]


2.  Create and Activate a Virtual Environment (Recommended):

From the project directory run: 
bash:
    python3 -m venv venv  # Linux/macOS
    # or
    python -m venv venv   # Windows

    source venv/bin/activate  # Linux/macOS
    # or
    venv\Scripts\activate   # Windows
    

3.  Install Python Dependencies:

requirements.txt: This file lists the Python packages that the project depends on.

bash:
    > pip install -r requirements.txt

## Running the Application

1. Start the Admin Panel from challenges directory:

   >  streamlit run src/challenges/admin.py --server.address.127.0.0.1
    

2. Access the Admin Panel:
    The tab of the admin panel opens automatically. However, if facing issues you can open your web browser and navigate to the URL provided by Streamlit (`http://localhost:8501`).

3.  Configure Exercises:

Use the admin panel to select exercise types , set credentials, and configure flags.

4.  Launch User Panels:

Use the buttons in the admin panel to launch the user panels for each exercise. The user panels will be created and open automatically.
The users, without admin permission, can also access the platform through this url "http://127.0.0.1:8502". 

Also users with different id can be created when "http://127.0.0.1:8502/?id=1"


