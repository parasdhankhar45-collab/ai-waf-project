import pandas as pd

df = pd.read_csv("dataset/clean_payloads.csv")

# Normalize type names
label_map = {
    "normal": 0,
    "sqli": 1,
    "xss": 2,
    "traversal": 3,
    "cmd": 4,
    "command": 4
}

df["label"] = df["Type"].map(label_map)
df = df.dropna()

df = df[["Payload", "label"]]
df.to_csv("dataset/waf_data.csv", index=False)

print(df.head())
print("Saved dataset/waf_data.csv")
