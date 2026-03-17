from flask import Flask, request, abort
import joblib
import datetime
import re
import random
import csv
import os

app = Flask(__name__)

model = joblib.load("waf_model.pkl")
vectorizer = joblib.load("vectorizer.pkl")

LOG_FILE = "attack_logs.csv"

FAKE_GEO = [
    (28.61, 77.20),
    (40.71, -74.00),
    (51.50, -0.12),
    (35.68, 139.69),
    (48.85, 2.35)
]

def rule_based_detect(payload):
    patterns = {
        "SQLi": r"(\bUNION\b|\bSELECT\b|\bINSERT\b|\bDELETE\b|\bUPDATE\b|\bDROP\b|--|#|/\*|\bor\b|\band\b|\b1=1\b)",
        "XSS": r"(<script>|</script>|onerror=|onload=|alert\(|<img|<svg)",
        "PathTraversal": r"\.\./|\.\.\\|/etc/passwd|boot.ini",
        "CommandInjection": r"(;|\|\||&&|\bcat\b|\bwget\b|\bcurl\b)"
    }

    for name, pattern in patterns.items():
        if re.search(pattern, payload, re.IGNORECASE):
            return name

    return "Normal"

def calculate_threat_score(attack_type):

    if attack_type == "SQLi":
        return 9

    if attack_type == "XSS":
        return 8

    if attack_type == "PathTraversal":
        return 7

    if attack_type == "CommandInjection":
        return 10

    return 0

def calculate_severity(score):

    if score >= 9:
        return "CRITICAL"

    if score >= 7:
        return "HIGH"

    if score >= 4:
        return "MEDIUM"

    if score > 0:
        return "LOW"

    return "NONE"

if not os.path.exists(LOG_FILE):

    with open(LOG_FILE,"w",newline="") as f:

        writer = csv.writer(f)

        writer.writerow([
        "timestamp",
        "ip",
        "payload",
        "attack_type",
        "action",
        "score",
        "severity",
        "lat",
        "lon"
        ])

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def waf(path):

    ip = request.remote_addr
    payload = request.query_string.decode() + request.path

    try:
        payload_vec = vectorizer.transform([payload])
        prediction = model.predict(payload_vec)[0]
    except:
        prediction = 0

    attack_type = rule_based_detect(payload)

    if prediction == 1 or attack_type != "Normal":
        action = "BLOCKED"
    else:
        action = "ALLOWED"

    score = calculate_threat_score(attack_type)
    severity = calculate_severity(score)

    lat, lon = random.choice(FAKE_GEO)

    timestamp = datetime.datetime.now()

    with open(LOG_FILE,"a",newline="") as f:

        writer = csv.writer(f)

        writer.writerow([
        timestamp,
        ip,
        payload,
        attack_type,
        action,
        score,
        severity,
        lat,
        lon
        ])

    if action == "BLOCKED":
        abort(403)

    return f"Request {action}"

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=8080,debug=False)