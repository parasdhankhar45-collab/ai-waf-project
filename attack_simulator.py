import requests
import random
import time

target="http://127.0.0.1:8080"

payloads=[
"/?id=1",
"/?id=2",
"/?id=3",
"/?page=home",
"/?search=test",
"/?id=1 UNION SELECT password",
"/?user=admin' OR 1=1--",
"/?q=<script>alert(1)</script>",
"/?file=../../etc/passwd",
"/?cmd=cat /etc/passwd"
]

for i in range(50):

    payload=random.choice(payloads)

    url=target+payload

    try:
        r=requests.get(url)
        print(i+1,r.status_code)
    except:
        print(i+1,"error")

    time.sleep(0.2)