import time
import gzip
import json
import base64
import random
from uuid import uuid4
from httpx import post

def generate_realistic_mouse_data():
    mouse_data = []
    start_time = 0
    
    for i in range(60):
        time_offset = i * 12 + random.randint(-3, 3)
        
        if i < 10:
            x = random.randint(100, 400)
            y = random.randint(100, 400)
        elif i < 30:
            x = random.randint(200, 1700)
            y = random.randint(200, 900)
        else:
            x = random.randint(300, 600)
            y = random.randint(300, 500)
        
        x += random.randint(-20, 20)
        y += random.randint(-20, 20)
        
        mouse_data.append([time_offset, x, y])
    
    return mouse_data

def generate_realistic_key_data():
    key_data = []
    
    key_events = [
        (0, 1), (50, 0), (80, 1), (130, 0), (160, 1),
        (210, 0), (240, 1), (290, 0), (320, 1), (370, 0),
        (400, 1), (450, 0), (480, 1), (530, 0), (560, 1),
        (610, 0), (640, 1), (690, 0), (720, 1), (770, 0)
    ]
    
    for time_offset, key_state in key_events:
        time_offset += random.randint(-5, 5)
        key_data.append([time_offset, key_state])
    
    return key_data

def generate_payload(nonce):
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
    
    json_str = json.dumps(data, separators=(',', ':'))
    json_bytes = json_str.encode('utf-8')
    
    compressed = gzip.compress(json_bytes, compresslevel=9)
    
    b64 = base64.b64encode(compressed).decode('utf-8')
    payload = b64.replace('+', '-').replace('/', '_').replace('=', '')
    
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





