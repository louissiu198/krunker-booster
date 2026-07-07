import time
import gzip
import json
import base64
import random
from uuid import uuid4
from httpx import post

def generate_realistic_mouse_data(): # removed from preview
    return mouse_data

def generate_realistic_key_data(): # removed from preview
    return key_data

def generate_payload(nonce): # removed from preview
    if not nonce:
        return None
    
    data = {
        'n': nonce,
        'v': 1,
        't': 0,  
        'm': generate_realistic_mouse_data(),
        'k': generate_realistic_key_data()
    }
    
    start_time = int(time.time() * 1000)
    data['t'] = int((time.time() * 1000) - start_time) + random.randint(100, 500)
    compressed = gzip.compress(json_bytes, compresslevel=9)
    b64 = base64.b64encode(compressed).decode('utf-8')
    return payload
# 3 functions above are full AI made, translated through source code, "a" token encryption

def get_auth_token(username: str, password: str) -> dict: # shit handling, no time
    while True:
        try:
            n = post("https://gapi.svc.krunker.io/auth/nonce").json()["data"]["nonce"] # prevent ratelimit
            break
        except:
            continue

    rsp = post(
        "https://gapi.svc.krunker.io/auth/login/username",
        json = {
            "username": username,
            "password": password,
            "a": generate_payload(n)
        },
        headers = {
            "accept": "application/json",
            "accept-encoding": "application/json",
            "accept-language": "en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7",
            "content-type": "application/json",
            "origin": "https://krunker.io",
            "priority": "u=1, i",
            "referer": "https://krunker.io/",
            "sec-ch-ua": '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
            "x-idempotency-key": str(uuid4())
        }
    )
    if "login_ok" in rsp.text:
        return rsp.json()["data"]["access_token"]
retry = 3
account_path = "./input/accounts.txt"
accounts = open(account_path).read().splitlines()
open(account_path, "w+") # overwrite

for acc in accounts:
    success = False
    u, p = acc.split(":")[0], acc.split(":")[1]
    for i in range(retry):
        token = get_auth_token(u, p)
        if token:
            print(f"[+] Generated: {u}-{p}-{token[:12]}")
            with open(account_path, "a") as f:
                f.write(f"{u}:{p}:{token}\n")
            success = True
            break
        continue
    if not success:
        print(f"[-] Failed: {u}:{p}")





