AI-Based Web Application Firewall (WAF).This project is a hybrid Web Application Firewall that combines traditional rule-based detection with machine learning to identify and block malicious HTTP requests in real time.
The idea behind this project was to move beyond static rule-based systems and build something that can adapt to new attack patterns, while still reliably detecting known threats.
features:
Monitors incoming HTTP requests
Extracts request data (URL, query parameters, payload)
Analyzes it using:A trained ML model ,Rule-based detection (regex patterns)
Decides whether to: Allow the request or Block it 
Logs every request for analysis (similar to SOC systems)
