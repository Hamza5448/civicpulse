# ADR 0002: Keep Phase 2 Backend Core Provider-Neutral

- Status: Accepted
- Date: 2026-09-28

## Context

The full CivicPulse assignment defines triage metadata, but Phase 2 explicitly defers Redis, LLM, Ollama, and AI triage provider implementations. The backend core still needs a stable complaint schema and API contract for later phases.

## Decision

Phase 2 persists the assignment-defined triage fields without implementing an external provider. Complaint creation uses the conservative `other` category and `normal` priority defaults when those values are not supplied. `ai_summary`, `triaged_by`, and `triage_latency_ms` remain nullable until a later provider phase supplies them.

## Consequences

- The Phase 2 API and database schema are ready for later triage integration.
- No external network, Redis, or provider behavior is hidden in the backend core.
- Provider-backed triage must replace the defaults and populate the nullable metadata in a later phase.

## Current implementation note

Later application phases completed that planned replacement. Complaint input no longer accepts category or priority; the selected provider produces both fields and the service records summary, provider, and latency.
