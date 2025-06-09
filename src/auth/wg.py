from flask import Flask, request, jsonify, send_file  # Import Flask and related modules
import os  # For file and path operations
import subprocess  # For running shell commands
import traceback  # For printing stack traces on errors
import json  # For handling JSON data

app = Flask(__name__)  # Initialize Flask app

config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'wireguard', 'wg_config.json')
with open(config_path) as f:
    config = json.load(f)

SERVER_PUBLIC_KEY = config["WG_SERVER_PUB_KEY"]
SERVER_ENDPOINT = f"{config['WG_SERVER_PUBLIC_IP']}:{config['WG_SERVER_PORT']}"


# Directory for storing generated client configs (not used for per-user tracking)
CONFIG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "configs"))
SERVER_WG_CONFIG = "/etc/wireguard/wg0.conf"
BASE_IP = "10.9.0."

# Ensure config directory exists
if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)

def generate_keypair():
    # Generate a WireGuard private key
    private_key = subprocess.check_output("wg genkey", shell=True).decode().strip()
    # Generate the corresponding public key
    pubkey_proc = subprocess.Popen("wg pubkey", stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    public_key, _ = pubkey_proc.communicate(input=private_key.encode())
    return private_key, public_key.decode().strip()

def get_next_ip():
    # Find the next available IP in the subnet by checking used IPs in the server config
    used = set()
    if os.path.exists(SERVER_WG_CONFIG):
        with open(SERVER_WG_CONFIG) as f:
            for line in f:
                if "AllowedIPs" in line:
                    parts = line.strip().split("=")
                    if len(parts) == 2:
                        ip_part = parts[1].strip().split("/")[0]
                        used.add(ip_part)
    for i in range(2, 255):
        ip = BASE_IP + str(i)
        if ip not in used:
            return ip
    raise Exception("No available IPs in subnet")

def remove_existing_peer(username):
    # Remove an existing peer entry for a user from the server config
    if os.path.exists(SERVER_WG_CONFIG):
        with open(SERVER_WG_CONFIG, "r") as f:
            lines = f.readlines()
        new_lines = []
        skip = False
        for line in lines:
            if f"# user with id: {username}" in line:
                skip = True
                continue
            if skip and line.strip().startswith("[Peer]"):
                continue
            if skip and line.strip() == "":
                skip = False
                continue
            if not skip:
                new_lines.append(line)
        with open(SERVER_WG_CONFIG, "w") as f:
            f.writelines(new_lines)


def generate_wg_config(username):
    # Generate a WireGuard config for a user and update server config
    remove_existing_peer(username)  # Remove old peer entry if exists
    private_key, public_key = generate_keypair()
    client_ip = get_next_ip()
    # Create client config file

    config = f"""[Interface]
PrivateKey = {private_key}
Address = {client_ip}/24
DNS = 1.1.1.1

[Peer]
PublicKey = {SERVER_PUBLIC_KEY}
Endpoint = {SERVER_ENDPOINT}
AllowedIPs = 172.18.0.0/16, 172.28.0.0/16, 172.29.0.0/16, 10.9.0.0/24
PersistentKeepalive = 25
"""

    filepath = os.path.join(CONFIG_DIR, f"client_wg.conf")
    with open(filepath, "w") as f:
        f.write(config)
    # Append new peer entry to server config
    peer_entry = f"""

# user with id: {username}
[Peer]
PublicKey = {public_key}
AllowedIPs = {client_ip}/32
"""
    with open(SERVER_WG_CONFIG, "a") as f:
        f.write(peer_entry)
    # Restart WireGuard service using a shell script
    RESTART_WG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "wireguard", "restart_wg.sh"))
    subprocess.Popen([RESTART_WG_PATH])
    return filepath

@app.route('/generate_config', methods=['POST'])
def generate_config():
    # API endpoint to generate a WireGuard config for a user
    data = request.form
    username = data.get("username")
    if not username:
        return jsonify({"message": "Username is required"}), 400
    try:
        path = generate_wg_config(username)
        return jsonify({"message": "Config generated", "path": path}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"message": str(e)}), 500

@app.route('/download_config', methods=['GET'])
def download_config():
    # API endpoint to download the generated config file
    username = request.args.get("username")
    if not username:
        return jsonify({"message": "Username is required"}), 400
    # Always returns the same config file (not per-user)
    path = os.path.join(CONFIG_DIR, f"client_wg.conf")
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    else:
        return jsonify({"message": "No config found for this user"}), 404

@app.route('/remove_config', methods=['POST'])
def remove_config():
    # API endpoint to remove a user's config and peer entry
    username = request.form.get("username")
    if not username:
        return jsonify({"message": "Username is required"}), 400
    removed = False
    if os.path.exists(SERVER_WG_CONFIG):
        with open(SERVER_WG_CONFIG, "r") as f:
            lines = f.readlines()
        new_lines = []
        skip = False
        for line in lines:
            if f"# user with id: {username}" in line:
                skip = True
                removed = True
                continue
            if skip and line.strip().startswith("[Peer]"):
                continue
            if skip and line.strip() == "":
                skip = False
                continue
            if not skip:
                new_lines.append(line)
        with open(SERVER_WG_CONFIG, "w") as f:
            f.writelines(new_lines)
        # Restart WireGuard service using a hardcoded script path
        RESTART_WG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "wireguard", "restart_wg.sh"))
        subprocess.Popen([RESTART_WG_PATH])
    config_file = os.path.join(CONFIG_DIR, f"client_wg.conf")
    if os.path.exists(config_file):
        os.remove(config_file)
        removed = True
    if removed:
        return jsonify({"message": "Config removed"}), 200
    else:
        return jsonify({"message": "No config found for user"}), 404

if __name__ == '__main__':
    # For testing: generate and print a keypair, then run the Flask app
    private_key, public_key = generate_keypair()
    print(f"Private Key: {private_key}")
    print(f"Public Key: {public_key}")
    app.run(host='0.0.0.0', port=5003, debug=True)  # Exposes the app on all interfaces
    # app.run(debug=True, port=5003)  # (Commented out) Only exposes on localhost