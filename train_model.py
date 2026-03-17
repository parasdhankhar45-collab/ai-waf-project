import random
import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

random.seed(42)
np.random.seed(42)

# ================= LOAD DATA =================

df = pd.read_csv("dataset/clean_payloads.csv")

df["payload"] = df["Payload"].astype(str)
df["label"] = df["Type"].apply(lambda x: 0 if str(x).lower() == "benign" else 1)
df = df[["payload", "label"]].drop_duplicates(subset=["payload"])

# ================= ADD REALISTIC BENIGN TRAFFIC =================

fake_normal_payloads = [
    "/search?q=select jacket",
    "/product?id=12&sort=union",
    "/blog/script-tutorial",
    "/docs/how-to-use-select-command",
    "/category=drop-shoes",
    "/api/query?name=anderson",
    "/shop?filter=script",
    "/products?name=union-jacket",
    "/blog/sql-tips-for-beginners",
    "/tutorials/command-line-basics",
    "/article/how-to-drop-weight-fast",
    "/search?q=command+line+guide",
    "/help/sql-select-statement",
    "/guide/how-to-use-union-in-python",
    "/docs/xss-protection-guide",
    "/products?name=select-shirt",
    "/news/security-update",
    "/docs/database-select-query",
    "/products?name=script-hoodie",
    "/course/command-line-fundamentals",
    "/search?q=dropbox account",
    "/shop?item=union cap",
    "/guide/selecting the right laptop",
    "/docs/javascript basics",
    "/profile?name=orlando",
    "/article/command economy explained",
    "/search?q=script writing tips",
    "/product?brand=union",
    "/download?file=report.txt",
    "/search?q=how to select courses"
] * 1000

fake_df = pd.DataFrame({
    "payload": fake_normal_payloads,
    "label": 0
})

df = pd.concat([df, fake_df], ignore_index=True)

# ================= BALANCE TRAINING BASE =================

attack_df = df[df["label"] == 1]
normal_df = df[df["label"] == 0]

sample_size = min(3000, len(attack_df), len(normal_df))

attack_sample = attack_df.sample(sample_size, random_state=42)
normal_sample = normal_df.sample(sample_size, random_state=42)

base_df = pd.concat([attack_sample, normal_sample], ignore_index=True)
base_df = base_df.sample(frac=1, random_state=42).reset_index(drop=True)

# ================= BUILD HARD HOLDOUT TEST SET =================
# This is the honest way to lower inflated accuracy:
# test on unseen, harder, obfuscated payloads.

hard_attack_payloads = [
    "/?id=1/**/UNION/**/SELECT/**/password",
    "/?user=admin%27%20OR%201%3D1--",
    "/?q=%3Cscript%3Ealert(1)%3C%2Fscript%3E",
    "/?img=%3Cimg%20src%3Dx%20onerror%3Dalert(1)%3E",
    "/?file=..%2F..%2Fetc%2Fpasswd",
    "/?path=..%2F..%2F..%2Fwindows%2Fwin.ini",
    "/?cmd=%3Bcat%20%2Fetc%2Fpasswd",
    "/?exec=ping&&whoami",
    "/login?username=admin'+OR+'1'%3D'1",
    "/?id=10%20UNION%20SELECT%20card_number%20FROM%20users",
    "/?search=%3Csvg%20onload%3Dalert(1)%3E",
    "/?doc=..\\..\\boot.ini",
    "/run?task=ls||whoami",
    "/?page=<script>confirm(1)</script>",
    "/?name=' OR 'a'='a",
    "/?redirect=javascript:alert(1)",
    "/?f=../../../../etc/shadow",
    "/?command=cat%20/etc/hosts",
    "/?id=1+or+1=1",
    "/?query=UNION%20ALL%20SELECT%20NULL,NULL"
] * 80

hard_benign_payloads = [
    "/search?q=union jacket sale",
    "/docs/sql select tutorial",
    "/product?name=script hoodie",
    "/blog/how-to-drop-a-course",
    "/guide/command-line-basics",
    "/profile?name=orlando bloom",
    "/search?q=select best laptop",
    "/article/xss prevention guide",
    "/help/how-to-union-two-dataframes",
    "/news/script writer interview",
    "/shop?item=union-cap",
    "/category=command hooks",
    "/search?q=path traversal explained",
    "/download?file=setup_guide.pdf",
    "/products?name=drop shoulder tee",
    "/docs/javascript-events",
    "/blog/how-to-select-database",
    "/api/user?id=45",
    "/product?id=18&sort=price",
    "/about?section=team"
] * 80

holdout_df = pd.DataFrame({
    "payload": hard_attack_payloads + hard_benign_payloads,
    "label": [1] * len(hard_attack_payloads) + [0] * len(hard_benign_payloads)
})

holdout_df = holdout_df.sample(frac=1, random_state=42).reset_index(drop=True)

# ================= TRAIN / VALID SPLIT =================

X = base_df["payload"]
y = base_df["label"]

X_train, X_valid, y_train, y_valid = train_test_split(
    X,
    y,
    test_size=0.25,
    random_state=42,
    stratify=y
)

# ================= PIPELINE =================

pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(
        max_features=300,
        ngram_range=(1, 1),
        lowercase=True
    )),
    ("clf", LogisticRegression(
        max_iter=250,
        C=0.15,
        random_state=42
    ))
])

# ================= CROSS-VALIDATION =================

cv_scores = cross_val_score(
    pipeline,
    X_train,
    y_train,
    cv=5,
    scoring="accuracy"
)

print("Cross-validation scores:", cv_scores)
print("Mean CV accuracy:", cv_scores.mean())

# ================= TRAIN =================

pipeline.fit(X_train, y_train)

# ================= VALIDATION ON NORMAL SPLIT =================

y_valid_pred = pipeline.predict(X_valid)

print("\n=== Validation Set Results ===")
print("Accuracy:", accuracy_score(y_valid, y_valid_pred))
print(confusion_matrix(y_valid, y_valid_pred))
print(classification_report(y_valid, y_valid_pred))

# ================= HARD HOLDOUT EVALUATION =================

X_holdout = holdout_df["payload"]
y_holdout = holdout_df["label"]

y_holdout_pred = pipeline.predict(X_holdout)

print("\n=== Hard Holdout Test Results ===")
print("Accuracy:", accuracy_score(y_holdout, y_holdout_pred))
print(confusion_matrix(y_holdout, y_holdout_pred))
print(classification_report(y_holdout, y_holdout_pred))

# ================= SAVE MODEL + VECTORIZER =================

vectorizer = pipeline.named_steps["tfidf"]
model = pipeline.named_steps["clf"]

joblib.dump(model, "waf_model.pkl")
joblib.dump(vectorizer, "vectorizer.pkl")

print("\nMODEL SAVED")