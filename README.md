
# Cyber Range Sandbox & WireGuard VPN Server

This project provides a **Cyber Range Sandbox** for security exercises and a fully automated **WireGuard VPN server** setup. It includes an admin panel for configuring exercises, user panels for students, and scripts for secure VPN deployment.

---

## Table of Contents

- Project Structure
- Features
- Prerequisites
- Setup Instructions
  - 1. Clone the Repository
  - 2. Python Virtual Environment
  - 3. Install Python Dependencies
  - 4. Prepare Database Files
  - 5. Configure Environment Variables
  - 6. WireGuard VPN Server Setup
- Running the Application
- WireGuard VPN Management
- Troubleshooting
- License

---

## Project Structure

```
Glitchboxx/
├── data/
│   ├── users.db
│   └── admins.db
├── src/
│   ├── auth/
│   │   └── wg.py
│   └── challenges/
│       └── admin.py
├── venv/
├── wireguard-vpn-server/
│   ├── .env
│   ├── env.example      
│   ├── scripts/
│   │   ├── setup_wireguard.sh
│   │   ├── restart_wg.sh
│   │   ├── a_reset_firewall.sh
│   │   ├── iptables_reset.sh
│   │   └── up.sh
│   └── wireguard/
│       ├── server_private.key
│       ├── server_public.key
│       └── wg0.conf
├── .gitignore
├── README.md
├── requirements.txt
```

---

## Features

- **WireGuard VPN Server:** Automated installation, configuration, and management scripts.
- **Cyber Range Sandbox:** Admin and user panels for security exercises.
- **Database Integration:** SQLite databases for user and admin management.
- **Firewall & Networking Scripts:** Automated firewall and iptables configuration.
- **Docker & gVisor Ready:** Supports containerized environments for exercises.
- **Python Virtual Environment Support:** Isolated Python dependencies.

---

## Prerequisites

- **Linux-based server** (Ubuntu/Debian recommended)
- **Root or sudo access** for VPN and firewall setup
- **Python 3.6+** (3.8 recommended)
- **Docker** and **Docker Compose**
- **gVisor** (see below for installation)
- **Wireshark** (optional, for PCAP analysis)
- **WireGuard** (installed automatically by setup script)

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/klliarop/Glitchboxx.git
cd Glitchboxx/

```

---

### 2. Python Virtual Environment  (Using Python 3.12)

```bash
sudo apt-get install python3.12 python3.12-venv python3.12-dev
python3 -m venv venv
source venv/bin/activate
```

---

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Prepare Database Files

If you have existing `users.db` and `admins.db`, copy them into the data directory.  
Otherwise, the application will create new ones on first run.

---

### 5. Configure Environment Variables

Copy the example file and edit it:

```bash
cp env.example .env
nano .env
```

- **Set your public IP** for `WG_SERVER_ENDPOINT`
- Leave keys blank; the setup script will generate them if missing.

---

### 6. WireGuard VPN Server Setup

Make scripts executable and run the setup:

```bash
cd wireguard-vpn-server/
chmod +x scripts/*.sh
sudo scripts/setup_wireguard.sh
```

This will:
- Install WireGuard
- Generate server keys if missing and update `.env`
- Write wg0.conf
- Enable and start the WireGuard service
- Run all firewall and iptables scripts
- Bring up the interface

### 7. Installing Docker, Docker Compose & gVisor

#### **Install Docker**

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

*Optional: Add your user to the docker group to run Docker without sudo (log out and back in for this to take effect):*

```bash
sudo usermod -aG docker $USER
```

#### **Install Docker Compose (v2+)**

```bash
sudo apt-get update
sudo apt-get install -y docker-compose-plugin
```

#### **Install gVisor**

```bash
# Download and install runsc (gVisor runtime)
GVISOR_VERSION=$(curl -s https://api.github.com/repos/google/gvisor/releases/latest | grep tag_name | cut -d '"' -f 4)
wget https://storage.googleapis.com/gvisor/releases/release/${GVISOR_VERSION}/runsc
chmod +x runsc
sudo mv runsc /usr/local/bin

# (Optional) Install containerd-shim-runsc-v1 for containerd integration
wget https://storage.googleapis.com/gvisor/releases/release/${GVISOR_VERSION}/containerd-shim-runsc-v1
chmod +x containerd-shim-runsc-v1
sudo mv containerd-shim-runsc-v1 /usr/local/bin
```

---

#### **Verify Installation**

```bash
docker --version
docker compose version
runsc --version
```


## Running the Application

### 1. Start the Admin Panel

```bash
streamlit run src/challenges/admin.py --server.address 127.0.0.1
```

- The admin panel will open in your browser at [http://localhost:8501](http://localhost:8501).

### 2. Access the User Panel

- Users can access the platform at [http://127.0.0.1:8502](http://127.0.0.1:8502).
- To specify a user ID: [http://127.0.0.1:8502/?id=1](http://127.0.0.1:8502/?id=1)

---

## WireGuard VPN Management

- **Restart VPN:**  
  ```bash
  sudo scripts/restart_wg.sh
  ```
- **Reset Firewall:**  
  ```bash
  sudo scripts/a_reset_firewall.sh
  ```
- **Reset iptables:**  
  ```bash
  sudo scripts/iptables_reset.sh
  ```
- **Bring Up Interface:**  
  ```bash
  sudo scripts/up.sh
  ```

- **Add Peers:**  
  Edit wg0.conf and restart the VPN service.

---

## Troubleshooting

- **VPN not working?**  
  - Check WireGuard status: `sudo systemctl status wg-quick@wg0`
  - Show VPN info: `sudo wg show`
  - Check logs: `journalctl -u wg-quick@wg0`
  - Ensure firewall allows UDP port 51820:  
    `sudo ufw allow 51820/udp`

- **Networking issues after updates?**  
  - Check iptables backend: `sudo update-alternatives --config iptables`
  - Ensure IP forwarding: `sudo sysctl -w net.ipv4.ip_forward=1`
  - Reboot if kernel or Docker was updated.

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

**For any issues or contributions, please open an issue or pull request on GitHub.**

---

Let me know if you want to further tailor this README for your specific use case!
