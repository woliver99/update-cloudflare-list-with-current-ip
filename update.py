from datetime import datetime
import json
from time import sleep
import requests
import os

secrets_file = "./secrets.json"
last_list_file = "./last_list.json"

def get_ip() -> str:
    url = "https://api.ipify.org/"

    try:
        response = requests.request("GET", url)
    except:
        raise Exception("Failed to get IP. Check your internet connection and try again.")

    if response.status_code != 200:
        raise Exception("Failed to get IP with status code: " + str(response.status_code))
    
    return response.text

def get_secrets() -> dict:
    secrets_file = "./secrets.json"

    if not os.path.exists(secrets_file):
        # Create secrets file with default values
        default_secrets = {
            "email": "your_email@example.com",
            "key": "your_api_key",
            "account_id": "your_account_id",
            "list_id": "your_list_id"
        }
        with open(secrets_file, "w") as f:
            json.dump(default_secrets, f)
        print("Secrets file created with default values. Now is the time to enter your email, key, account_id, and list_id into the file.")
        input("Press Enter to continue... ")

    # Read secrets from file
    try:
        with open(secrets_file, "r") as f:
            secrets = json.load(f)
            f.close()
    except:
        raise Exception("Failed to read secrets file. Try deleting it and running the script again for default configuration")

    required_keys = ["email", "key", "account_id", "list_id"]
    for key in required_keys:
        if key not in secrets:
            raise Exception(f"{key} not found in secrets file. Try deleting it and running the script again for default configuration")
    
    return secrets

def update_ip(ip: str) -> bool:
    secrets = get_secrets()
    account_id = secrets["account_id"]
    list_id = secrets["list_id"]
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/rules/lists/{list_id}/items"

    payload = [
        {
            "ip": f"{ip}",
        }
    ]

    headers = {
        "Content-Type": "application/json",
        "X-Auth-Email": secrets["email"],
        "X-Auth-Key": secrets["key"]
    }

    response = requests.request("PUT", url, json=payload, headers=headers)
    updated = response.json()["success"]

    if updated == True:
        print(f'IP updated to "{ip}" at {datetime.now()}')
    else:
        print(f'Failed to update IP to "{ip}" with response: {response.text}')
    
    return updated

def store_last_list(new_list: set) -> None:
    with open(last_list_file, "w") as f:
        json.dump(list(new_list), f)
        f.close()

def get_last_list() -> set:
    if not os.path.exists(last_list_file):
        return set()
    
    with open(last_list_file, "r") as f:
        last_list = set(json.load(f))
        f.close()
        return last_list

print("Started IP update script...")
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
