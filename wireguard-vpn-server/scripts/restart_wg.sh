#!/bin/bash

# Restart the WireGuard service
echo "[*] Restarting WireGuard service..."

#!/bin/bash
sleep 2
systemctl restart wg-quick@wg0

# # Stop the WireGuard interface
# wg-quick down wg0

# # Start the WireGuard interface
# wg-quick up wg0

echo "[✓] WireGuard service restarted successfully."