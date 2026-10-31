# Practical 11 — Logging and Error Tracking

## Implementation in `app.py`

The existing Flask application now includes the main logging and error-tracking requirements from the practical handout:

- Logs are written to standard output using Python's `logging` module.
- Model-load success and failure are logged at startup.
- Each request gets an `X-Request-ID` (or reuses a supplied one).
- Request method, path, HTTP status, and elapsed time are logged.
- HTTP responses with status 400 or higher are logged as warnings.
- Successful predictions are logged without writing student identifiers or raw input payloads.
- Prediction exceptions are logged with a stack trace and return a generic error response.
- CI runs application tests and Docker smoke tests, and prints container logs when the job finishes.

This project uses Flask on port 5000 rather than FastAPI on port 8000 from the handout. The implementation preserves the repository's existing API and model.

## Local verification

Install dependencies and ensure the trained model artifact exists, then run:

```bash
python app.py
```

In another terminal:

```bash
curl -i http://localhost:5000/health
curl -i -X POST http://localhost:5000/predict -H "Content-Type: application/json" -d '{"attendance":90,"internal_marks":85,"assignment_marks":88,"previous_score":80}'
curl -i -X POST http://localhost:5000/predict -H "Content-Type: application/json" -d '{}'
```

Check the server terminal for `event=http_request`, `event=prediction_succeeded`, and warning/error events. A response includes the `X-Request-ID` header for tracing.

## Cloud verification

After Practical 10 is deployed, open the Render service's **Logs** view. Send one successful request and one invalid request, then confirm the events appear. If the app is updated, wait for Practical 9's workflow to publish the new image and redeploy that image in Render.

## Privacy

Do not log student names, register numbers, credentials, authorization headers, or complete request bodies. Current request logs use only request metadata and generated/supplied request IDs.