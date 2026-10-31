# Practical 12 — Prometheus and Grafana Monitoring

This monitoring folder follows the Practical-12 procedure. The application in this repository uses **Flask on port 5000**, not FastAPI on port 8000 as described in the handout, so the metrics instrumentation preserves this repository's existing Flask API contract.

## 1. Configure Prometheus target

Edit `prometheus.yml` and replace `REPLACE_WITH_YOUR_RENDER_HOST.onrender.com` with the actual Render service hostname. Do not include `https://` in the target. The repository does not contain a confirmed Render URL, so this must be filled in before Prometheus can show the target as UP.

## 2. Start Prometheus

Run these commands from this folder in a shell that supports `$(pwd)`:

```bash
docker network create mlops-monitoring
docker run -d --name prometheus --network mlops-monitoring -p 9090:9090 \
  -v "$(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml:ro" \
  -v "$(pwd)/student_api_alerts.yml:/etc/prometheus/student_api_alerts.yml:ro" \
  prom/prometheus
```

On Windows PowerShell, replace `$(pwd)` with `(Get-Location).Path` and use the path syntax supported by Docker Desktop.

Open:
- Prometheus: http://localhost:9090
- Targets: http://localhost:9090/targets
- Alerts: http://localhost:9090/alerts

## 3. Start Grafana

```bash
docker run -d --name grafana --network mlops-monitoring -p 3000:3000 grafana/grafana
```

Open http://localhost:3000. Sign in using the initial credentials shown by the Grafana image/setup, then change the password. Add a Prometheus data source with URL `http://prometheus:9090`.

## 4. PromQL dashboard queries

- Model loaded: `student_api_model_loaded`
- Total requests: `sum(student_api_http_requests_total)`
- Request rate: `sum(rate(student_api_http_requests_total[1m]))`
- Successful predictions: `sum(student_api_predictions_total{result="success"})`
- Errors: `sum(rate(student_api_http_requests_total{status=~"4..|5.."}[5m]))`
- P95 latency: `histogram_quantile(0.95, sum by (le) (rate(student_api_http_request_duration_seconds_bucket[5m])))`

## 5. Application endpoints

The current repository uses port 5000:
- `GET /health`
- `POST /predict`
- `GET /metrics`

The GitHub Actions workflow tests the metrics endpoint in Python and in the Docker container before publishing the tested image to GHCR. After CI passes, redeploy that image in Render if a Render service has already been configured.

## Privacy

Metric labels contain only HTTP method, fixed route, status code, and result class. Do not add student names, registration numbers, credentials, or raw request payloads to logs or metrics.
