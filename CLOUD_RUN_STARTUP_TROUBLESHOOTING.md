# Cloud Run Startup Probe Failure — Troubleshooting

**Error:** `The user-provided container failed the configured startup probe checks`

The image builds and pushes successfully, but the container fails to pass Cloud Run's health checks. Here are the most likely causes and fixes.

---

## 1. Check the logs (do this first)

Cloud Run logs show why the container failed:

**[Logs Explorer for litellm-proxy](https://console.cloud.google.com/logs/viewer?project=api-ai-blog-writer&resource=cloud_run_revision/service_name/litellm-proxy)**

Look for:
- `ValidationError` → missing required env vars (see #2)
- `RuntimeError` / Redis errors → set `CACHE_ENABLED=false` (see #3)
- Port binding errors → ensure app listens on `0.0.0.0` and `$PORT`
- Import/module errors → check build context and dependencies

---

## 2. Required environment variables / secrets

The app **requires** these at startup (no defaults):

| Variable     | Purpose              | Must be set in Cloud Run |
|-------------|----------------------|---------------------------|
| `SECRET_KEY`| Session signing      | Yes                       |
| `DATABASE_URL` | PostgreSQL connection | Yes                    |
| `REDIS_URL` | Redis connection     | Yes                       |

If any are missing, the app raises `ValidationError` and exits before the server starts, so the startup probe fails.

### Fix: Add secrets to the Cloud Run service

**Option A — Console**

1. Open [litellm-proxy service](https://console.cloud.google.com/run/detail/europe-west9/litellm-proxy?project=api-ai-blog-writer)
2. **Edit & deploy new revision**
3. **Variables & Secrets** → **Secrets** → **Reference a secret**
4. Add:
   - `SECRET_KEY` → Secret: `SECRET_KEY`, Version: `latest`
   - `DATABASE_URL` → Secret: `DATABASE_URL`, Version: `latest`
   - `REDIS_URL` → Secret: `REDIS_URL`, Version: `latest`

Create the secrets in [Secret Manager](https://console.cloud.google.com/security/secret-manager?project=api-ai-blog-writer) if they don’t exist.

**Option B — gcloud**

```bash
# Ensure secrets exist, then update the service
gcloud run services update litellm-proxy \
  --region=europe-west9 \
  --project=api-ai-blog-writer \
  --update-secrets=SECRET_KEY=SECRET_KEY:latest,DATABASE_URL=DATABASE_URL:latest,REDIS_URL=REDIS_URL:latest
```

---

## 3. Redis / cache (CACHE_ENABLED)

If Redis is not configured but cache is enabled, the app can fail when handling requests. For a minimal setup without Redis:

Set env var: `CACHE_ENABLED=false`

**Console:** Variables & Secrets → Variables → Add variable: `CACHE_ENABLED` = `false`

**gcloud:**

```bash
gcloud run services update litellm-proxy \
  --region=europe-west9 \
  --project=api-ai-blog-writer \
  --set-env-vars=CACHE_ENABLED=false
```

---

## 4. Startup probe path and timing

- **Default:** Cloud Run uses a TCP startup probe (checks that the port is open).
- If an HTTP startup probe is configured, the path must match an endpoint that returns 2xx/3xx (e.g. `/` or `/health`).

If the app is slow to start, increase the probe’s initial delay:

```bash
gcloud run services update litellm-proxy \
  --region=europe-west9 \
  --project=api-ai-blog-writer \
  --startup-probe-type=http \
  --startup-probe-path=/health \
  --startup-probe-initial-delay=10 \
  --startup-probe-period=5 \
  --startup-probe-timeout=5 \
  --startup-probe-failure-threshold=6
```

---

## 5. One-shot fix (all in one)

If you have the secrets in Secret Manager:

```bash
gcloud run services update litellm-proxy \
  --region=europe-west9 \
  --project=api-ai-blog-writer \
  --update-secrets=SECRET_KEY=SECRET_KEY:latest,DATABASE_URL=DATABASE_URL:latest,REDIS_URL=REDIS_URL:latest \
  --set-env-vars=CACHE_ENABLED=false,ENVIRONMENT=production
```

Then trigger a new deployment (e.g. push to `main` or run the Cloud Build trigger again).

---

## 6. Verify locally

Before redeploying, run the container locally with the same env vars:

```bash
docker run -p 8080:8080 \
  -e SECRET_KEY=test-secret \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -e REDIS_URL=redis://localhost:6379/0 \
  -e CACHE_ENABLED=false \
  europe-west9-docker.pkg.dev/api-ai-blog-writer/litellm-proxy/litellm-proxy:latest
```

Then: `curl http://localhost:8080/health` — should return 200.
