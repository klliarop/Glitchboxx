#!/usr/bin/env python3
import json
import os
import subprocess
from pathlib import Path
import sys

import getpass

username = getpass.getuser()
sudoers_entry = f"{username} ALL=(ALL) NOPASSWD: /usr/sbin/iptables -I DOCKER-USER *, /usr/sbin/iptables -D DOCKER-USER *\n"

print("Writing sudoers rule for iptables access...")

try:
    subprocess.run(["sudo", "bash", "-c", f"echo '{sudoers_entry}' > /etc/sudoers.d/99-iptables-rules"], check=True)
    subprocess.run(["sudo", "chmod", "440", "/etc/sudoers.d/99-iptables-rules"], check=True)
    print("Sudoers rule written successfully.")
except subprocess.CalledProcessError as e:
    print("Failed to write sudoers rule:", e)
    sys.exit(1)


# Use the script's directory as the config directory
script_dir = Path(__file__).resolve().parent
config_dir = script_dir
config_dir.mkdir(parents=True, exist_ok=True)

# Paths
config_path = config_dir / "wg_config.json"
priv_key_path = config_dir / "server_private.key"
pub_key_path = config_dir / "server_public.key"
wg_conf_path = Path("/etc/wireguard/wg0.conf")

# Default config
default_config = {
    "WG_SERVER_PUB_KEY": "",
    "WG_SERVER_PRIV_KEY": "",
    "WG_SERVER_PUBLIC_IP": "192.168.1.241",
    "WG_SERVER_PORT": "51820"
}

# Create config file if missing
if not config_path.exists():
    with open(config_path, "w") as f:
        json.dump(default_config, f)

# Install WireGuard
print("Installing WireGuard...")
subprocess.run(["sudo", "apt", "update"], check=True)
subprocess.run(["sudo", "apt", "install", "-y", "wireguard"], check=True)

# Generate keys
print("Generating WireGuard keys...")
priv_key = subprocess.check_output(["wg", "genkey"]).decode().strip()
pub_key = subprocess.check_output(["wg", "pubkey"], input=priv_key.encode()).decode().strip()

priv_key_path.write_text(priv_key)
pub_key_path.write_text(pub_key)

try:
    with open(config_path, "r") as f:
        content = f.read().strip()
        if not content:
            print(f"Error: {config_path} is empty.")
            sys.exit(1)
        cfg = json.loads(content)
except json.JSONDecodeError as e:
    print(f"JSON parse error: {e}")
    print(f"Consider deleting or fixing '{config_path}' manually.")
    sys.exit(1)
except FileNotFoundError:
    print(f"Config file not found at {config_path}")
    sys.exit(1)

# Add generated keys to config
cfg["WG_SERVER_PRIV_KEY"] = priv_key
cfg["WG_SERVER_PUB_KEY"] = pub_key

with open(config_path, "w") as f:
    json.dump(cfg, f, indent=2)

# Write WireGuard config
print("Creating wg0.conf...")
wg_conf = f"""[Interface]
Address = 10.9.0.1/24
ListenPort = {cfg["WG_SERVER_PORT"]}
PrivateKey = {cfg["WG_SERVER_PRIV_KEY"]}

PostUp = iptables -A FORWARD -i wg0 -d 172.118.0.0/16 -j ACCEPT; iptables -A FORWARD -o wg0 -s 172.118.0.0/16 -j ACCEPT; iptables -A FORWARD -i wg0 ! -d 172.118.0.0/16 -j DROP; iptables -t nat -A POSTROUTING -s 10.9.0.0/24 -d 172.118.0.0/16 -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -d 172.118.0.0/16 -j ACCEPT; iptables -D FORWARD -o wg0 -s 172.118.0.0/16 -j ACCEPT; iptables -D FORWARD -i wg0 ! -d 172.118.0.0/16 -j DROP; iptables -t nat -D POSTROUTING -s 10.9.0.0/24 -d 172.118.0.0/16 -j MASQUERADE
"""

subprocess.run(["sudo", "mkdir", "-p", "/etc/wireguard"])
wg_conf_path.write_text(wg_conf)

# Enable IP forwarding
print("Enabling IP forwarding...")
subprocess.run(["sudo", "sed", "-i", "/net.ipv4.ip_forward/d", "/etc/sysctl.conf"])
subprocess.run(["sudo", "bash", "-c", "echo 'net.ipv4.ip_forward=1' >> /etc/sysctl.conf"])
subprocess.run(["sudo", "sysctl", "-p"], check=True)

# Start WireGuard
print("Starting WireGuard (wg0)...")
subprocess.run(["sudo", "systemctl", "enable", "wg-quick@wg0"])
subprocess.run(["sudo", "systemctl", "restart", "wg-quick@wg0"])

print("WireGuard VPN server is up and running!")


# Execute up.sh
up_script = script_dir / "up.sh"
if up_script.exists():
    print("Running up.sh...")
    subprocess.run(["sudo", "bash", str(up_script)], check=True)
else:
    print("up.sh not found at:", up_script)

# allowing adm group to have read access to get vpn ips of users on the user.py files
#sudo chown root:adm /etc/wireguard/wg0.conf
#sudo chmod 640 /etc/wireguard/wg0.conf


sudo chown root:adm /etc/wireguard/
sudo chmod 750 /etc/wireguard/


print("Creating ctf_net Docker network if it doesn't exist...")
try:
    subprocess.run([
        "sudo", "docker", "network", "create",
        "--driver", "bridge",
        "--subnet", "172.118.0.0/16",
        "--internal",
        "ctf_net"
    ], check=True, capture_output=True, text=True) # capture_output to prevent >
    print("ctf_net Docker network created or.")
except subprocess.CalledProcessError as e:
    # Check if the error is specifically because the network already exists
    if "network with name ctf_net already exists" in e.stderr:
        print("ctf_net Docker network already exists.")
    else:
        # If it's another type of error, print it and exit
        print(f"Failed to create ctf_net Docker network: {e.stderr}")
        sys.exit(1)

