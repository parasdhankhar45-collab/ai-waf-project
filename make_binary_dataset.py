import pandas as pd

df = pd.read_csv("dataset/clean_payloads.csv")
df.columns = ["Type", "Payload"]

# Convert to binary labels
df["label"] = df["Type"].apply(lambda x: 0 if str(x).lower()=="normal" else 1)

df = df[["Payload", "label"]]
df.columns = ["payload", "label"]

print(df.head())
print(df["label"].value_counts())

df.to_csv("dataset/waf_binary_dataset.csv", index=False)
print("✅ Binary dataset saved in dataset/waf_binary_dataset.csv")
