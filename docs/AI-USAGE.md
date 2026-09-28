# AI Usage Disclosure

This Phase 2 implementation was developed with assistance from GitHub Copilot.

Copilot helped shape and generate portions of the FastAPI application wiring, SQLAlchemy model, Alembic migration, repository/service code, API routes, triage provider adapters, Redis cache/rate-limiter integration, React workflows, tests, and documentation. The implementation was reviewed and adjusted against the CivicPulse assignment Markdown specification, including the required layering, status transition table, database constraints, endpoint behavior, provider fallback behavior, frontend contracts, and Phase 2/3/4/5 boundaries.

The repository owner is responsible for understanding, testing, and defending the submitted code during the project viva.

The application-compliance audit was completed with assistance from OpenAI Codex. It helped identify and implement missing Prometheus triage metrics, coverage enforcement, route-layer dependency separation, request-context logging, Ollama retry parity, OpenAPI-generated frontend types, tests, and documentation. The changes were reviewed against the assignment and validated locally; infrastructure and deployment evidence remains separate and must come from genuine runs.
