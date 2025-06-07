#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_PATH="$SCRIPT_DIR/../.env"

if [ -f "$ENV_PATH" ]; then
    set -a
    source "$ENV_PATH"
    set +a
else
    echo "Missing .env file!"
    exit 1
fi

# Update package list and install WireGuard
echo "[*] Updating package list..."
sudo apt update

echo "[*] Installing WireGuard..."
sudo apt install -y wireguard

# Generate keys if not present
if [ -z "$WG_SERVER_PRIVATE_KEY" ] || [ -z "$WG_SERVER_PUBLIC_KEY" ]; then
    WG_SERVER_PRIVATE_KEY=$(wg genkey)
    WG_SERVER_PUBLIC_KEY=$(echo "$WG_SERVER_PRIVATE_KEY" | wg pubkey)
    echo "WG_SERVER_PRIVATE_KEY=$WG_SERVER_PRIVATE_KEY" >> "$ENV_PATH"
    echo "WG_SERVER_PUBLIC_KEY=$WG_SERVER_PUBLIC_KEY" >> "$ENV_PATH"
fi

WG_CONFIG="/etc/wireguard/wg0.conf"
sudo bash -c "cat > $WG_CONFIG <<EOF
[Interface]
PrivateKey = $WG_SERVER_PRIVATE_KEY
Address = $WG_SERVER_ADDRESS
ListenPort = $WG_SERVER_PORT
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

# Add your peer configurations here
EOF"

sudo systemctl enable wg-quick@wg0
sudo systemctl restart wg-quick@wg0

# Restart WireGuard service
echo "[*] Restarting WireGuard service..."
sudo bash "$SCRIPT_DIR/restart_wg.sh"

# Reset firewall rules
echo "[*] Resetting firewall rules..."
sudo bash "$SCRIPT_DIR/firewall_reset.sh"

# Reset iptables rules
echo "[*] Resetting iptables rules..."
sudo bash "$SCRIPT_DIR/iptables_reset.sh"

# Bring up the WireGuard interface
echo "[*] Bringing up the WireGuard interface..."
sudo bash "$SCRIPT_DIR/up.sh"

echo "[✓] WireGuard VPN server setup complete."
