# ADR 0003: Selectable Triage Providers With Rules Fallback

- Status: Accepted
- Date: 2026-09-28

## Context

CivicPulse must be able to use deterministic local classification, simulated CI behavior, a hosted LLM, or Ollama without changing routes or complaint persistence. External model output is untrusted and provider failures must not make complaint submission fail.

## Decision

The service depends on the `TriageProvider` protocol and selects an implementation through `TRIAGE_PROVIDER`. Rules and simulated providers are deterministic. The hosted LLM and Ollama adapters validate responses with the same Pydantic `TriageResult` schema. A failed selected provider is logged and retried through the deterministic rules provider, with `triaged_by=rules:fallback` recorded.

Redis caching, distributed rate limiting, and provider-result caching remain deferred until their designated infrastructure phase.

## Consequences

- Provider choice is configuration-driven and does not leak into HTTP routes.
- CI can use deterministic providers without network credentials.
- Hosted-provider failures are visible in metadata and logs without returning a 500 to a citizen.
- Later phases can add caching and rate limiting around the provider boundary.
