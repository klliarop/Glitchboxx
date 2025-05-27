import requests
import time
import os
import random

internal_target = os.environ.get("TARGET_URL", "http://web/index.php")

proxy_target = os.environ.get("PROXY_URL", "http://web/index.php")

usernames = ["admin", "georgekon", "marylunar", "alexelef", "guest", "john.doe", "jane.smith"]
passwords = ["admin123", "K0n67jl!", "pa55w0rd!23", "a1ex56@3k", "guest123!", "johnd0e.", "jane5m1th!"]

print(f"Traffic generator started. Main target: {internal_target}", flush=True)
if proxy_target:
    print(f"Proxy target: {proxy_target}", flush=True)

def make_request(url, username, password):
    data = {"username": username, "password": password}
    
    proxies = {
        "http": os.environ.get("PROXY_HTTP", "")
    }
    
    try:
        response = requests.post(url, data=data, timeout=5, proxies=proxies if proxies["http"] else None)
        return response.status_code, response.text
    except Exception as e:
        return None, str(e)

while True:
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
    
    time.sleep(10)

