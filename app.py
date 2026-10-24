from flask import Flask, jsonify, request
import joblib
import pandas as pd

app = Flask(__name__)
model = joblib.load("student_result_model.pkl")
FEATURES = ["attendance", "internal_marks", "assignment_marks", "previous_score"]

@app.get("/")
def health():
    return jsonify({"service": "student-result-prediction", "status": "ok"})

@app.post("/predict")
def predict():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Request body must be a JSON object"}), 400
    missing = [feature for feature in FEATURES if feature not in payload]
    if missing:
        return jsonify({"error": "Missing required features", "missing": missing}), 400
    try:
        row = {feature: float(payload[feature]) for feature in FEATURES}
    except (TypeError, ValueError):
        return jsonify({"error": "All features must be numeric"}), 400
    prediction = int(model.predict(pd.DataFrame([row]))[0])
    return jsonify({"prediction": "PASS" if prediction == 1 else "FAIL",
                    "prediction_code": prediction})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
