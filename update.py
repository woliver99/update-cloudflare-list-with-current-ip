from datetime import datetime
import json
from time import sleep
import requests
import os

secrets_file = "./secrets.json"
last_list_file = "./last_list.json"

def get_ip() -> str:
    url = "https://api.ipify.org/"

    response = requests.request("GET", url)

    if response.status_code == 200:
        return response.text
    
    raise Exception("Failed to get IP with status code: " + str(response.status_code))

def get_secrets() -> dict:
    secrets_file = "./secrets.json"

    if not os.path.exists(secrets_file):
        # Create secrets file with default values
        default_secrets = {
            "email": "your_email@example.com",
            "key": "your_api_key"
        }
        with open(secrets_file, "w") as f:
            json.dump(default_secrets, f)
        print("Secrets file created with default values. Now is the time to enter your email and key into the file.")
        input("Press Enter to continue... ")

    # Read secrets from file
    try:
        with open(secrets_file, "r") as f:
            secrets = json.load(f)
    except:
        raise Exception("Failed to read secrets file. Try deleting it and running the script again for default configuration")

    if "email" not in secrets or "key" not in secrets:
        raise Exception("Email or key not found in secrets file. Try deleting it and running the script again for default configuration")
    
    return secrets

def update_ip(ip: str) -> bool:
    account_id = "7f43d57de6f3aca69f908ca66f660465"
    list_id = "5ae25761e55640d89721b8cf1df7076e"
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/rules/lists/{list_id}/items"

    payload = [
        {
            "ip": f"{ip}",
        }
    ]

    secrets = get_secrets()
    headers = {
        "Content-Type": "application/json",
        "X-Auth-Email": secrets["email"],
        "X-Auth-Key": secrets["key"]
    }

    response = requests.request("PUT", url, json=payload, headers=headers)
    updated = response.json()["success"]

    if updated == True:
        print(f'IP updated to "{ip}" at {datetime.now()}')
    
    return updated

def store_last_list(new_list: set) -> None:
    with open(last_list_file, "w") as f:
        json.dump(list(new_list), f)

def get_last_list() -> set:
    if not os.path.exists(last_list_file):
        return set()
    
    with open(last_list_file, "r") as f:
        return set(json.load(f))


while True:
    try:
        ip = get_ip()
    except Exception as e:
        print(e)
        ip = None

    if ip != None:
        last_list = get_last_list()

        if ip not in last_list:
            if update_ip(ip):
                last_list.clear()
                last_list.add(ip)
                store_last_list(last_list)
    
    sleep(300)