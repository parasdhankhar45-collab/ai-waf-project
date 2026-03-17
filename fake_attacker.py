import requests
import random
import time

TARGET = "http://127.0.0.1:8080"

ATTACKS = [
    "?q=' OR 1=1 --",
    "?q=UNION SELECT * FROM users",
    "?q=<script>alert(1)</script>",
    "?q=../../etc/passwd",
    "?q=../windows/system32/drivers/etc/hosts",
    "?q=cmd=whoami",
    "?q=cmd=ls -la",
    "?q='; DROP TABLE users; --",
    "?q=<img src=x onerror=alert(1)>",
    "?q=cat /etc/shadow"
]

for i in range(100):
    payload = random.choice(ATTACKS)
    url = TARGET + payload

    try:
        r = requests.get(url, timeout=2)
        print(f"[{i}] Sent: {payload} -> {r.status_code}")
    except:
        print(f"[{i}] Blocked/Timeout")

    time.sleep(0.3)   # slow down to avoid freeze
