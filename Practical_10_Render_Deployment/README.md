# Practical 10 — Deploy GHCR Image to Render

## What is implemented in the repository

Practical 9's workflow publishes the tested image to:

```text
ghcr.io/anilkumargouthakatla-cmd/student-result-prediction:latest
```

The Flask service exposes `/`, `/health`, and `/predict` on port 5000. The app now honours Render's `PORT` environment variable and falls back to port 5000 for local/Docker use.

**Render-side deployment cannot be marked complete from repository code alone.** No confirmed Render service URL or Render account connection is available in this repository. Complete the dashboard steps below, then record the actual URL.

## Deploy steps

1. Open the Render Dashboard and create a **Web Service** using **Existing Image**.
2. Set image to `ghcr.io/anilkumargouthakatla-cmd/student-result-prediction:latest`.
3. If the GHCR package is private, configure a registry credential with package-read permission. Never put the token in this repository.
4. Set the health check path to `/health`.
5. Use port 5000 if Render asks for a port; the application also reads the `PORT` environment variable.
6. Deploy and wait until Render reports the service is live.
7. Copy the real service URL and test:
   - `https://YOUR-SERVICE.onrender.com/`
   - `https://YOUR-SERVICE.onrender.com/health`
   - `https://YOUR-SERVICE.onrender.com/metrics`
8. Test `POST /predict` with JSON:
   ```json
   {
     "attendance": 90,
     "internal_marks": 85,
     "assignment_marks": 88,
     "previous_score": 80
   }
   ```
9. Save the actual URL and deployment timestamp in your practical record.

## Redeploy after a new image

An image-backed Render service may not automatically pull a changed `latest` tag. After Practical 9 publishes a new image, trigger a manual deploy/pull of the latest image in Render and re-test `/health`.

## Status checklist

- [x] CI workflow builds and tests the image before GHCR publication.
- [x] Repository contains the app's health endpoint.
- [ ] Create/confirm the Render service.
- [ ] Record the real Render URL.
- [ ] Verify public HTTPS endpoints after deployment.

Do not report the final three items as complete until they have been tested against your actual Render service.