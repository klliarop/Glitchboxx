# This script generates HTTP traffic by making POST requests to a specified target URL.
# It simulates login attempts using a list of usernames and passwords, optionally through a proxy.

import requests  # For making HTTP requests
import time      # For sleep/delay between requests
import os        # For reading environment variables
import random    # For random selection of usernames/passwords

# Get the internal target URL from environment or use default
internal_target = os.environ.get("TARGET_URL", "http://web/index.php")

# Get the proxy target URL from environment or use default
proxy_target = os.environ.get("PROXY_URL", "http://web/index.php")

# List of possible usernames and passwords to use in requests
usernames = ["admin", "georgekon", "marylunar", "alexelef", "guest", "john.doe", "jane.smith"]
passwords = ["admin123", "K0n67jl!", "pa55w0rd!23", "a1ex56@3k", "guest123!", "johnd0e.", "jane5m1th!"]

# Print startup info for debugging/logging
print(f"Traffic generator started. Main target: {internal_target}", flush=True)
if proxy_target:
    print(f"Proxy target: {proxy_target}", flush=True)

# Function to make a POST request to a given URL with username and password
def make_request(url, username, password):
    data = {"username": username, "password": password}
    
    # Set up HTTP proxy if specified in environment
    proxies = {
        "http": os.environ.get("PROXY_HTTP", "")
    }
    
    try:
        # If proxy is set, use it; otherwise, don't use proxies
        response = requests.post(url, data=data, timeout=5, proxies=proxies if proxies["http"] else None)
        return response.status_code, response.text
    except Exception as e:
        # Return None and error message if request fails
        return None, str(e)

# Main loop: continuously generate traffic
while True:
    # Pick a random username/password pair
    index = random.randint(0, len(usernames) - 1)
    username = usernames[index]
    password = passwords[index]
    
    # Internal request (container-to-container)
    int_status, int_response = make_request(internal_target, username, password)
    print(f"[Internal] {username}/{password} - Status: {int_status}", flush=True)
    
    # Proxy request (if configured)
    if proxy_target:
        proxy_status, proxy_response = make_request(proxy_target, username, password)
        print(f"[Proxy] {username}/{password} - Status: {proxy_status}", flush=True)
    
    # Wait 10 seconds before next round
    time.sleep(10)