# ADR 0001: Isolate External Providers Behind Interfaces

- Status: Accepted
- Date: 2026-09-27

## Context

CivicPulse will use external integrations for AI-assisted triage and Redis-backed capabilities. The application must support LLM, Ollama, RuleBased, and Simulated AI providers without coupling HTTP routes or business services to a specific vendor or runtime.

## Decision

Define provider interfaces in the backend provider layer. Services depend on those interfaces, while concrete provider implementations handle external SDKs, network calls, and integration-specific details. Provider selection will be configured outside route handlers and can be replaced for local development, testing, or production.

The package boundary is `backend/app/providers/`, with the protocol and concrete triage implementations under `backend/app/providers/triage/`.

## Consequences

- Business services can remain independent of provider-specific APIs.
- Rule-based and simulated providers can support deterministic development and tests.
- New providers can be added behind the same contract.
- Provider contracts and dependency injection have focused deterministic tests.
