# CivicPulse Engineering Notes

These notes distinguish measured application evidence from infrastructure evidence that must be collected during later Docker, Kubernetes, and CI/CD work. Pending measurements are stated plainly rather than estimated.

## Database indexes

`ix_complaints_status_priority` in `backend/alembic/versions/0001_create_complaints.py` supports the operations dashboard query when operators filter the queue by status and priority. `ix_complaints_created_at` supports the repository's newest-first paginated listing in `backend/app/repositories/complaints.py`.

## Cache behavior and measured hit rate

`/api/stats` uses a 30-second read-through cache and explicit invalidation after complaint creation. TTL bounds staleness if invalidation is missed, while invalidation makes newly submitted complaints visible immediately. Either mechanism alone provides only one of those properties.

The deterministic triage-cache test submits identical content twice and measures a hit rate of `0.5`: the first request misses and populates Redis, and the second hits. This is test evidence, not a production traffic claim. A production hit rate will only be reported from genuine workload observations.

## 1. Laptop and CI differences

The current laptop run uses Python 3.14 while the assignment's eventual container runtime is Python 3.12; the future backend Docker base will freeze that version. Local tests use SQLite and `fakeredis` through `backend/tests/conftest.py`, while integration CI must use PostgreSQL and Redis services. Local tests select deterministic providers, and CI will explicitly set `TRIAGE_PROVIDER=simulated` so it never depends on model credentials or network output.

The exact Dockerfile and CI line references will be added when those files exist.

## 2. CI/CD maturity

The repository is currently below continuous integration because no executable CI workflow exists yet. The next rung is automated CI on `dev` pushes and pull requests, covering linting, type checks, tests, coverage, image builds, scanning, manifest validation, and a Compose integration path. Automated deployment belongs to the later CD workflow.

## 3. Build once, deploy many

`frontend/src/api/client.ts` reads `window.__CIVICPULSE_CONFIG__.apiBaseUrl`, and `frontend/public/config.js` supplies the default relative `/api` path. The production container will generate that public file at startup. Without this boundary, Vite would bake an environment URL into the JavaScript bundle and require a different image per environment.

## 4. Correctness for a probabilistic provider

For a live model, correctness means returning schema-valid category, priority, summary, and confidence within the timeout while preserving the service contract when the provider fails. It does not mean identical classifications on every invocation. CI stays deterministic by selecting `SimulatedTriage`, injecting failures and malformed output in tests, validating with Pydantic, and asserting rules fallback still returns `201`.

## 5. HPA lag

Pending a genuine Kubernetes load test. No lag value has been measured.

## 6. VPA Off mode

The planned VPA uses recommendation-only mode because an Auto VPA changing CPU requests would change the denominator used by the CPU HPA. That feedback loop can cause the HPA and VPA to counteract each other. Actual recommendations and request changes remain pending genuine cluster evidence.

## 7. Internal network and model egress

Pending final Compose validation. The intended design places the backend on both the public-facing edge network and the internal data network. That gives the hosted-model client egress while PostgreSQL and Redis remain internal. Ollama model-pull behavior and its final network attachment must be demonstrated rather than assumed.

## 8. The failure

Pending a genuine team incident that consumed more than one hour. No failure story has been invented for this requirement.
