
# Cyber Range Sandbox

This project provides a **Cyber Range Sandbox** for security exercises and an automated **WireGuard VPN server** setup. It includes an admin panel for configuring exercises and see real-time progress of users and a platform panel for users.

---

## Table of Contents

- Project Structure
- Prerequisites
- Setup Instructions
- Running the Application
- 
- WireGuard VPN Management
- Troubleshooting
- License

---

## Project Structure

```
Glitchboxx/
├── data/
│   ├── admin.db
│   └── users.db
├── src/
│   ├── admin.py
│   ├── panel.py
│   ├── start.py
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── login.py
│   │   ├── register.py
│   │   ├── utils.py
│   │   └── wg.py
│   ├── configs/
│   │   └── client_wg.conf
│   ├── database/
│   ├── exercises/
│   │   ├── ftp/
│   │   ├── http/
│   │   ├── ssh/
│   │   ├── templates/
│   │   ├── admin_base.py
|   |   └── user_base.py
│   ├── progress/
│   └── wallpapers/
├── venv/
├── wireguard/
│   ├── restart_wg.sh
│   ├── server_private.key
│   ├── server_public.key
│   ├── setup_wg.py
│   ├── up.sh
│   └── wg_config.json
├── .gitignore
├── README.md
├── requirements.txt
```
---

## Prerequisites

- **Linux-based server** (Ubuntu/Debian recommended)
- **Root or sudo access** for VPN and firewall setup
- **Python 3.6+** (3.8 recommended)
- **Docker** and **Docker Compose**
- **gVisor** (see below for installation)
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

Edit thw wg_config.json file with the Public IP of your machine:

```bash
cd wireguard/
nano wg_config.json # CHANGE PUBLIC IP
```

- **Set your public IP** for `WG_SERVER_PUBLIC_IP`
- ** Do not add anything on private and public keys part. They will be configured automatically.
---

### 6. WireGuard VPN Server Setup

Make scripts executable and run the setup:

```bash
sudo chmod +x setup_wg.py
sudo ./setup_wg.py
```

This will:
- Install WireGuard
- Generate server keys
- Write wg0.conf 
- Enable and start the WireGuard service
- Run all firewall and iptables scripts
- Bring up the interface
- Create need docker networks for exercises

### 7. Installing Docker, Docker Compose & gVisor

#### **Install Docker**

```bash
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```

```bash
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```
To verify install run: 
```bash
sudo docker run hello-world
```

*Needed: Add your user to the docker group to run Docker without sudo (log out and back in for this to take effect):*

```bash
sudo groupadd docker
sudo usermod -aG docker $USER
```

#### **Install gVisor**

```bash
(
  set -e
  ARCH=$(uname -m)
  URL=https://storage.googleapis.com/gvisor/releases/release/latest/${ARCH}
  wget ${URL}/runsc ${URL}/runsc.sha512 \
    ${URL}/containerd-shim-runsc-v1 ${URL}/containerd-shim-runsc-v1.sha512
  sha512sum -c runsc.sha512 \
    -c containerd-shim-runsc-v1.sha512
  rm -f *.sha512
  chmod a+rx runsc containerd-shim-runsc-v1
  sudo mv runsc containerd-shim-runsc-v1 /usr/local/bin
)
```

```bash
sudo /usr/local/bin/runsc install
sudo systemctl reload docker
docker run --rm --runtime=runsc hello-world
```

---

#### **Verify Installation**

```bash
docker --version
docker compose version
runsc --version
```


## Running the Application
Once setup is complete, you can start the Admin and User panels. Ensure your virtual environment is activated (source venv/bin/activate).

### 1. Start the Admin Panel

```bash
streamlit run src/challenges/admin.py 
```
- The admin panel will open in your browser at [http://your_public_ip:port](http://your_public_ip:port) 

### 2. Run backend Services (Crucial for User/VPN Functionality)

```bash
python3 login.py
python3 register.py
sudo python3 wg.py
```

### 3. Access the User Panel

```bash
streamlit run src/start.py 
```
- Users can access the platform at [http://your_public_ip:port](http://your_public_ip:port).

---

## WireGuard VPN Management

- **Reset Firewall:**  
  ```bash
  sudo scripts/a_reset_firewall.sh
  ```
- **Reset iptables:**  
  ```bash
  sudo scripts/iptables_reset.sh
  ```

- **Add Peers:**  
  Edit wg0.conf (/etc/wireguard/wg0.conf) and restart the VPN service.

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

