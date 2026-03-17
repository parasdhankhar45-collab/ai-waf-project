import datetime

def log_request(ip, payload, verdict, attack_type):
    # Format timestamp without microseconds
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Clean payload: remove name= or file= if present
    if '=' in payload:
        payload = payload.split('=', 1)[1]

    # Append to CSV log
    with open("attack_logs.csv", "a", encoding="utf-8") as f:
        f.write(f"{timestamp},{ip},{payload},{attack_type},{verdict}\n")
