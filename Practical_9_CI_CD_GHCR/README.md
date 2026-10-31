# Practical 9 — GitHub Actions CI/CD and GHCR

## Verification against the practical handout

The repository already has the core Practical 9 automation in `.github/workflows/ml-ci.yml`. On pushes to `main`, the workflow installs dependencies, runs the ML quality gate and tests, builds a Docker image, starts a test container, checks the API, and only then pushes `latest` and `sha-<commit>` tags to GHCR. It uses the built-in `GITHUB_TOKEN` and the minimum `contents: read` / `packages: write` permissions.

This project is Flask on port 5000, so the health check and container mapping intentionally use port 5000 rather than the handout's FastAPI example on port 8000.

## How to verify

1. Open the repository's **Actions** tab.
2. Open the latest run of **Student Result Prediction CI - Practical 12 Monitoring**.
3. Confirm the test steps, Docker build, container smoke tests, and GHCR publish steps succeed.
4. Open the repository owner's **Packages** and confirm `student-result-prediction` has both `latest` and a `sha-<commit>` tag.

Workflow file: [ml-ci.yml](../.github/workflows/ml-ci.yml)

## Important GHCR note

If publishing fails with a package permission error, open the GHCR package settings and grant this repository Actions write access. The image is published only on pushes to `main`, not pull requests.

## Current state

The workflow is committed and its latest run was verified successful on 2026-10-31. Check Actions for the most recent run before recording a new practical result.