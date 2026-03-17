import requests
import time
import random

URL = "http://127.0.0.1:5000/"

payloads = [
"/?id=1",
"/?id=1 UNION SELECT password",
"/?search=<script>alert(1)</script>",
"/?page=../../etc/passwd",
"/?cmd=;ls",
"/?user=admin' OR '1'='1",
"/?file=../../boot.ini"
]

print("Starting attack replay simulation...")

for i in range(30):

    payload = random.choice(payloads)

    try:
        requests.get(URL + payload)
        print("Sent:", payload)

    except:
        pass

    time.sleep(0.3)

print("Attack replay finished")