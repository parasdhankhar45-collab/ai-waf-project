import joblib

model = joblib.load("waf_model.pkl")
vectorizer = joblib.load("vectorizer.pkl")

while True:
    payload = input("Enter payload (or exit): ")
    if payload == "exit":
        break
    
    vec = vectorizer.transform([payload])
    pred = model.predict(vec)[0]

    print("Prediction:", pred, " (0=normal, >0=attack)")
