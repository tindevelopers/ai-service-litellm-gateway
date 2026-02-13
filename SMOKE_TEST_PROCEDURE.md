# Smoke Test Procedure — AI Service LiteLLM Gateway

This document describes a minimal smoke test procedure to verify the application starts correctly and core endpoints respond as expected. **No code changes are required** — follow these steps manually.

---

## 1. Minimal Required Environment Variables

The application loads configuration at startup via `src.core.config.Settings` (`src/core/config.py`). The following variables are **required** (no defaults in config):

| Variable       | Required | Purpose                          | Smoke Test Value (minimal)                    |
|----------------|----------|----------------------------------|-----------------------------------------------|
| `SECRET_KEY`   | Yes      | Security / session signing       | `smoke-test-secret-key`                       |
| `DATABASE_URL` | Yes      | PostgreSQL connection string     | `postgresql+asyncpg://user:pass@localhost:5432/ai_gateway` |
| `REDIS_URL`    | Yes      | Redis connection string          | `redis://localhost:6379/0`                    |

**Important:** Database and Redis initialization are **skipped** in `main.py` lifespan (lines 38–44). The app will start with placeholder URLs; real DB/Redis are only needed for full functionality.

**Critical for smoke test:** Set `CACHE_ENABLED=false`. The LiteLLM service calls `get_redis()` when cache is enabled, which raises `RuntimeError` because `init_redis()` is never called. Without this, `/v1/models` and `/v1/chat/completions` will fail.

### Optional (for LLM endpoints)

| Variable           | Purpose                    |
|--------------------|----------------------------|
| `OPENAI_API_KEY`   | OpenAI models              |
| `ANTHROPIC_API_KEY`| Anthropic models           |
| `GOOGLE_API_KEY`   | Google models              |

At least one LLM provider key is needed for `/v1/chat/completions` and for `/v1/models` to return real models. Without keys, `/v1/models` falls back to a default list; chat will fail with provider errors.

### Dependency note

`DATABASE_URL` uses the `postgresql+asyncpg://` scheme, which requires the `asyncpg` package. If `requirements.txt` does not include it, use `requirements-simple.txt` or run `pip install asyncpg`.

### Minimal `.env` for smoke test

```bash
# Required (config validation)
SECRET_KEY=smoke-test-secret-key
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/ai_gateway
REDIS_URL=redis://localhost:6379/0

# Required for smoke test (Redis init is skipped)
CACHE_ENABLED=false

# Optional: for full API testing
# OPENAI_API_KEY=sk-your-key
# ANTHROPIC_API_KEY=sk-ant-your-key
```

---

## 2. Verify App Startup

### Prerequisites

- Python 3.11+
- Virtual environment with dependencies installed

### Steps

1. **Navigate to project directory**
   ```bash
   cd ai-service-litellm-gateway
   ```

2. **Create/activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables**
   ```bash
   export SECRET_KEY=smoke-test-secret-key
   export DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/ai_gateway
   export REDIS_URL=redis://localhost:6379/0
   export CACHE_ENABLED=false
   ```
   Or use a `.env` file in the project root (loaded via `python-dotenv`).

5. **Start the application**
   ```bash
   python -m uvicorn src.main:app --host 0.0.0.0 --port 8080
   ```
   Default port from config is **8080** (see `src.core.config.Settings.PORT`).

6. **Confirm startup success**
   - No `ValidationError` or import errors
   - Log line similar to: `"AI Gateway application started successfully (database/redis skipped)"`
   - Server listening on `http://0.0.0.0:8080`

---

## 3. Test Main API Endpoints

Run these from a separate terminal while the app is running.

### Root endpoint

```bash
curl -s http://localhost:8080/
```

**Expected:** JSON with `message`, `version`, `docs`, `health`.

### Health check

```bash
curl -s http://localhost:8080/health
```

**Expected:** JSON with `status: "healthy"`, `timestamp`, `version`, `environment`.

### Readiness check

```bash
curl -s http://localhost:8080/ready
```

**Expected:** JSON with `status: "ready"` and `checks` object.

### Models list (OpenAI-compatible)

```bash
curl -s http://localhost:8080/v1/models
```

**Expected:** JSON with `object: "list"` and `data` array of models (fallback list if no API keys).

### Chat completions (optional, requires LLM API key)

```bash
curl -s -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

**Expected:** JSON with `choices`, `usage`; or provider error if no valid API key.

---

## 4. Confirm Expected Response Status

| Endpoint              | Method | Expected Status |
|-----------------------|--------|-----------------|
| `/`                   | GET    | 200             |
| `/health`             | GET    | 200             |
| `/ready`              | GET    | 200             |
| `/v1/models`          | GET    | 200             |
| `/v1/chat/completions`| POST   | 200 (with key) or 500 (no key) |
| `/docs`               | GET    | 200             |
| `/metrics`            | GET    | 200             |

### Quick status check

```bash
for path in / /health /ready /v1/models /docs /metrics; do
  status=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8080$path")
  echo "$path -> $status"
done
```

---

## 5. Logs to Confirm System Health

### Startup logs

Look for:

- `"Starting AI Gateway application..."`
- `"AI Gateway application started successfully (database/redis skipped)"`
- No stack traces or `ValidationError`

### Request logs (per request)

- `"Request started"` with `method`, `url`, `client_ip`
- `"Request completed"` with `status_code`, `duration`

### Error logs (if any)

- `"HTTP exception occurred"` or `"Unexpected error occurred"` with `status_code`, `detail`

### Log level

Controlled by `LOG_LEVEL` (default: `INFO`). Set `LOG_LEVEL=DEBUG` for more detail.

---

## Quick One-Liner Smoke Test

```bash
# From project root (ai-service-litellm-gateway/)
export SECRET_KEY=smoke-test-secret-key
export DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/ai_gateway
export REDIS_URL=redis://localhost:6379/0
export CACHE_ENABLED=false
python -m uvicorn src.main:app --host 0.0.0.0 --port 8080 &
sleep 3
curl -s http://localhost:8080/health | grep -q '"status":"healthy"' && echo "PASS: Health OK" || echo "FAIL: Health check"
curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/v1/models | grep -q 200 && echo "PASS: Models OK" || echo "FAIL: Models endpoint"
# Kill background server: pkill -f "uvicorn src.main:app"
```

---

## Docker Compose Alternative

If PostgreSQL and Redis are available via Docker:

```bash
cd ai-service-litellm-gateway
docker-compose up -d db redis
# Wait for services to be ready, then:
docker-compose up app
```

Then run the same curl commands against `http://localhost:8080` (mapped from container port 8080).

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `ValidationError` on startup | Missing required env var | Set `SECRET_KEY`, `DATABASE_URL`, `REDIS_URL` |
| `RuntimeError: Redis not initialized` | Cache enabled, Redis init skipped | Set `CACHE_ENABLED=false` |
| `ModuleNotFoundError: No module named 'asyncpg'` | asyncpg not installed | `pip install asyncpg` or use `requirements-simple.txt` |
| `/v1/models` returns 500 | LiteLLM service init fails (often Redis) | Ensure `CACHE_ENABLED=false` |
| Port 8080 in use | Another process on 8080 | Use `--port 8081` or set `PORT=8081` |
