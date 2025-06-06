# WireGuard VPN Server Setup

## Overview
This project provides a complete setup for a WireGuard VPN server. It includes scripts for installation, configuration, and management of the VPN server, as well as necessary configuration files for WireGuard.

## Project Structure
```
wireguard-vpn-server
├── env.example
├── scripts
│   ├── setup_wireguard.sh
│   ├── restart_wg.sh
│   ├── a_reset_firewall.sh
│   └── up.sh
├── wireguard
│   ├── server_private.key
│   ├── server_public.key
│   └── wg0.conf
└── README.md
```

## Prerequisites
- A Linux-based server (Ubuntu, Debian, etc.)
- Root or sudo access to install packages and modify network settings

## Setup Instructions
1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd wireguard-vpn-server
   ```

2. **Configure Environment Variables**
   - Copy the `env.example` file to `.env` and fill in the required values.
   ```bash
   cp env.example .env
   ```

3. **Run the Setup Script**
   - Execute the setup script to install WireGuard and configure the server.
   ```bash
   chmod +x scripts/setup_wireguard.sh
   ./scripts/setup_wireguard.sh
   ```

4. **Start the WireGuard Service**
   - Use the provided scripts to manage the WireGuard service.
   ```bash
   chmod +x scripts/restart_wg.sh
   ./scripts/restart_wg.sh
   ```

5. **Configure Firewall Rules**
   - Reset and configure firewall rules using the provided script.
   ```bash
   chmod +x scripts/a_reset_firewall.sh
   ./scripts/a_reset_firewall.sh
   ```

6. **Bring Up the WireGuard Interface**
   - Use the up script to apply configurations and bring up the interface.
   ```bash
   chmod +x scripts/up.sh
   ./scripts/up.sh
   ```

## Usage
- To generate client configurations, modify the `wg0.conf` file and add peer entries as needed.
- Restart the WireGuard service whenever changes are made to the configuration.

## Troubleshooting
- Ensure that the server's firewall allows traffic on the WireGuard port (default is 51820).
- Check the logs for any errors related to WireGuard using `journalctl -u wg-quick@wg0`.

## License
This project is licensed under the MIT License - see the LICENSE file for details.