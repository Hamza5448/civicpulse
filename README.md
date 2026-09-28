# CivicPulse

## Problem Statement

Residents need a clear way to submit civic complaints, while operations teams need a consistent and transparent way to review, triage, and track those complaints.

## Project Purpose

CivicPulse will provide a civic complaint intake and operations workflow. Later phases will add complaint submission, AI-assisted triage, operational dashboards, persistence, and deployment automation.

## Technology Stack

- Frontend: React 18, Vite, and TypeScript
- Backend: FastAPI and Pydantic v2
- Database: PostgreSQL 16
- Cache and rate limiting: Redis 7
- Future AI providers: LLM, Ollama, RuleBased, and Simulated
- Future deployment: Docker Compose, Kubernetes, and CI/CD

## High-Level Architecture

The backend follows a one-way dependency direction:

```text
routes -> services -> repositories
             |
             v
         providers
```

- `routes` will contain HTTP concerns only.
- `services` will contain business rules and orchestration.
- `repositories` will contain persistence and SQL access.
- `providers` will contain external integrations such as AI and Redis abstractions.
- Routes will not access the database directly, and business rules will not be duplicated in the frontend.

The provider abstraction is recorded in [ADR 0001](docs/adr/0001-provider-interface.md).

## Repository Structure

```text
civicpulse/
├── backend/       # FastAPI application, persistence, providers, and tests
├── frontend/      # React/Vite/TypeScript application and tests
├── k8s/           # Kubernetes base and environment overlays (later phase)
├── load/          # Load-test assets (later phase)
├── docs/          # Architecture decisions and evidence
├── .github/       # CI workflows (later phase)
├── compose.yaml   # Local service foundation (later phase)
├── compose.prod.yaml
├── .env.example
└── README.md
```

## Development Prerequisites

- Git
- Python 3.11 or newer
- Node.js 20 or newer and npm
- PostgreSQL 16 for later backend development
- Redis 7 for later cache and rate-limiting development
- Docker Desktop for later containerized development

## Quickstart

> **To be completed in a later phase.** Local service orchestration, database migrations, backend startup, frontend startup, and test commands will be documented when those implementations are added.

Never commit a real `.env` file or credentials. Start from `.env.example` and use local, untracked values.

## Phase 2 Backend Development

The backend core can be tested locally with an isolated SQLite database while production configuration targets PostgreSQL 16:

```powershell
cd backend
python -m pip install -e ".[dev]"
$env:DATABASE_URL = "sqlite+aiosqlite:///./civicpulse-dev.db"
alembic upgrade head
cd ..
python scripts/seed.py
cd backend
pytest -q
uvicorn app.main:app --reload
```

Phase 3 adds selectable Rules, Simulated, hosted LLM, and Ollama triage providers with structured validation and rules fallback. Phase 4 adds Redis-backed statistics caching and distributed complaint rate limiting. The scope assumptions are recorded in [ADR 0002](docs/adr/0002-phase2-backend-scope.md), [ADR 0003](docs/adr/0003-triage-provider-strategy.md), and [ADR 0005](docs/adr/0005-redis-cache-and-rate-limit.md).

The backend also exposes Prometheus-compatible request counters and latency summaries at `/metrics`. The seed command is idempotent and loads 30 demonstration complaints after migrations have run.

## Phase 5 Frontend Development

The frontend provides Submit, Dashboard, and Stats workflows using the existing backend contracts. Install dependencies and run the checks with:

```powershell
cd frontend
npm install
npm test -- --run
npm run build
npm run dev
```

The public runtime configuration lives in `frontend/public/config.js` and contains only the API base URL. The development server proxies `/api` to `http://localhost:8000`; see [ADR 0006](docs/adr/0006-frontend-runtime-api-config.md).
