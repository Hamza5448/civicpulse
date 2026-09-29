# CivicPulse Application Runbook

## Start and verify

Apply migrations before starting the API:

```powershell
cd backend
alembic upgrade head
uvicorn app.main:app
```

Verify `GET /health` first, then `GET /ready`. Liveness must remain successful during a PostgreSQL or Redis outage; readiness should return `503` and name the unavailable dependency.

## Logs and request tracing

Application logs are JSON on stdout. Copy the `X-Request-ID` response header and search stdout for that value to correlate a request. A fallback warning includes the complaint ID, selected provider, and error class.

## Triage failure response

1. Query `/api/meta/providers` and inspect recent provider latency and fallback outcomes.
2. Confirm complaint submission still returns `201` with `triaged_by=rules:fallback`.
3. Check provider configuration without printing API keys.
4. For Ollama, verify its API is reachable and the configured model exists.
5. For a hosted provider, check timeout, `429`, and `5xx` responses before changing retry behavior.
6. Keep deterministic rules fallback active while repairing the selected provider.

## Database and Redis diagnosis

If `/ready` names `postgres`, verify the configured `DATABASE_URL`, connectivity, and the current Alembic revision. If it names `redis`, verify `REDIS_URL` and a Redis `PING`. Do not restart the application repeatedly when a dependency is unavailable; restore the dependency and let readiness recover.

## Shutdown

Send `SIGTERM` to Uvicorn. The server stops accepting new work, drains in-flight requests within its configured grace period, and then triggers FastAPI lifespan cleanup to close PostgreSQL and Redis connections.

## Deployment and rollback

Container, Kubernetes, and CI/CD deployment commands are intentionally deferred until their respective implementation is present and validated. Do not publish placeholder commands as operational evidence.
