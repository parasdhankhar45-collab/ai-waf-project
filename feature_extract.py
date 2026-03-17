import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

df = pd.read_csv("dataset/preprocessed_payloads.csv")

vectorizer = TfidfVectorizer(max_features=5000)
X = vectorizer.fit_transform(df["Payload"])
y = df["Type"]

print("Feature matrix shape:", X.shape)
