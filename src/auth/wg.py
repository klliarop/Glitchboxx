from flask import Flask, request, jsonify, send_file
import os
import subprocess
import traceback
import ipaddress

app = Flask(__name__)

#maybe not useful now, i dont keep trach of vp users files
CONFIG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "configs"))

SERVER_WG_CONFIG = "/etc/wireguard/wg0.conf"
SERVER_PUBLIC_KEY = "rHrtQ4y6KGYvm5L9Q+8lWdB+1Oj1IXKxyJn4NTcB3Hs="  # Replace this!
SERVER_ENDPOINT = "192.168.1.241:51820"  # Replace this!
BASE_IP = "10.9.0."

if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)


def generate_keypair():
    # Generate private key using 'wg genkey'
    private_key = subprocess.check_output("wg genkey", shell=True).decode().strip()

    # Generate public key using 'wg pubkey' by passing private key into it
    pubkey_proc = subprocess.Popen("wg pubkey", stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    public_key, _ = pubkey_proc.communicate(input=private_key.encode())

    # Return private and public keys as a tuple
    return private_key, public_key.decode().strip()


def get_next_ip():
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

# def get_next_ip():
#     used = set()
#     if os.path.exists(SERVER_WG_CONFIG):
#         with open(SERVER_WG_CONFIG) as f:
#             for line in f:
#                 if "AllowedIPs" in line:
#                     ip = line.strip().split()[1].split("/")[0]
#                     used.add(ip)
#     for i in range(2, 255):
#         ip = BASE_IP + str(i)
#         if ip not in used:
#             return ip
#     raise Exception("No available IPs in subnet")

def generate_wg_config(username):

    remove_existing_peer(username)  # Clean before adding new

    private_key, public_key = generate_keypair()
    client_ip = get_next_ip()

    # Create client config
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

    # Append to server config
    peer_entry = f"""

# user with id: {username}
[Peer]
PublicKey = {public_key}
AllowedIPs = {client_ip}/32
"""
    with open(SERVER_WG_CONFIG, "a") as f:
        f.write(peer_entry)


#### Change hard coded link!!!!!!!!
    #    subprocess.Popen(["/home/user/Desktop/sandbox_db/wireguard/restart_wg.sh"])

        RESTART_WG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "wireguard", "restart_wg.sh"))
        subprocess.Popen([RESTART_WG_PATH])

    return filepath

@app.route('/generate_config', methods=['POST'])
def generate_config():
    data = request.form
    username = data.get("username")
    if not username:
        return jsonify({"message": "Username is required"}), 400
    try:
        path = generate_wg_config(username)
        return jsonify({"message": "Config generated", "path": path}), 200
    # except Exception as e:
    #     return jsonify({"message": str(e)}), 500

    except Exception as e:
        traceback.print_exc()
        return jsonify({"message": str(e)}), 500

@app.route('/download_config', methods=['GET'])
def download_config():
    username = request.args.get("username")
    if not username:
        return jsonify({"message": "Username is required"}), 400
    #path = os.path.join(CONFIG_DIR, f"{username}_wg.conf")
    path = os.path.join(CONFIG_DIR, f"client_wg.conf")   # because it said invalid name in the wireguard mobile app
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    else:
        return jsonify({"message": "No config found for this user"}), 404


@app.route('/remove_config', methods=['POST'])
def remove_config():
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
                continue  # skip next [Peer] tag if it follows
            if skip and line.strip() == "":
                skip = False
                continue
            if not skip:
                new_lines.append(line)

        with open(SERVER_WG_CONFIG, "w") as f:
            f.writelines(new_lines)

        subprocess.Popen(["/home/user/Desktop/sandbox_db/wireguard/restart_wg.sh"])

    config_file = os.path.join(CONFIG_DIR, f"client_wg.conf")  # or use f"{username}_wg.conf" if named like that
    if os.path.exists(config_file):
        os.remove(config_file)
        removed = True

    if removed:
        return jsonify({"message": "Config removed"}), 200
    else:
        return jsonify({"message": "No config found for user"}), 404



if __name__ == '__main__':

    private_key, public_key = generate_keypair()
    print(f"Private Key: {private_key}")
    print(f"Public Key: {public_key}")

    app.run(host='0.0.0.0', port=5003, debug=True)    #this exposes nmap 192.168 port

   # app.run(debug=True, port=5003)      # this doesn't expose the port 