from flask import Flask, jsonify, request, g
import joblib
import pandas as pd
import logging
import sys
import time
import uuid
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

# Practical 11-style safe application logging to stdout.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True,
)
logger = logging.getLogger("student-result-api")

# Prometheus metrics (Practical 12).
HTTP_REQUESTS = Counter(
    "student_api_http_requests_total",
    "Total HTTP requests received by the Student Result Prediction API",
    ["method", "path", "status"],
)
HTTP_LATENCY = Histogram(
    "student_api_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path"],
)
PREDICTIONS = Counter(
    "student_api_predictions_total",
    "Total Student Result Prediction inference attempts",
    ["result"],
)
MODEL_LOADED = Gauge(
    "student_api_model_loaded",
    "Whether the Student Result Prediction model loaded successfully",
)

MODEL_FILE = "student_result_model.pkl"
FEATURES = ["attendance", "internal_marks", "assignment_marks", "previous_score"]

try:
    model = joblib.load(MODEL_FILE)
    MODEL_LOADED.set(1)
    logger.info("event=model_loaded model_file=%s", MODEL_FILE)
except Exception:
    MODEL_LOADED.set(0)
    logger.exception("event=model_load_failed model_file=%s", MODEL_FILE)
    raise


@app.before_request
def start_request_metrics():
    g.request_started_at = time.perf_counter()
    g.request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))


@app.after_request
def record_request_metrics(response):
    path = request.path
    method = request.method
    duration = time.perf_counter() - getattr(g, "request_started_at", time.perf_counter())
    request_id = getattr(g, "request_id", "unknown")

    # Do not count Prometheus' own scrapes as user traffic.
    if path != "/metrics":
        HTTP_REQUESTS.labels(method=method, path=path, status=str(response.status_code)).inc()
        HTTP_LATENCY.labels(method=method, path=path).observe(duration)

    level = logging.WARNING if response.status_code >= 400 else logging.INFO
    logger.log(
        level,
        "event=http_request request_id=%s method=%s path=%s status=%s duration_ms=%.2f",
        request_id, method, path, response.status_code, duration * 1000,
    )
    response.headers["X-Request-ID"] = request_id
    return response


@app.get("/")
def home():
    return jsonify({"service": "student-result-prediction", "status": "ok"})


@app.get("/health")
def health():
    return jsonify({"status": "healthy", "model_loaded": int(MODEL_LOADED._value.get())}), 200


@app.get("/metrics")
def metrics():
    return app.response_class(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


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

    try:
        prediction = int(model.predict(pd.DataFrame([row]))[0])
        PREDICTIONS.labels(result="success").inc()
        logger.info("event=prediction_succeeded request_id=%s", getattr(g, "request_id", "unknown"))
        return jsonify({
            "prediction": "PASS" if prediction == 1 else "FAIL",
            "prediction_code": prediction,
        })
    except Exception:
        PREDICTIONS.labels(result="error").inc()
        logger.exception("event=prediction_failed request_id=%s", getattr(g, "request_id", "unknown"))
        return jsonify({"error": "Prediction failed"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
