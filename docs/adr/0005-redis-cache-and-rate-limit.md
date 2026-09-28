# ADR 0005: Redis Cache and Distributed Rate Limiter

- Status: Accepted
- Date: 2026-09-28

## Context

CivicPulse needs fast aggregate statistics and protection for complaint submission when multiple backend instances are running. An in-process dictionary would not share state between workers or pods.

## Decision

Use Redis 7 for two capabilities: a read-through cache for `/api/stats` with a 30-second TTL and explicit invalidation after complaint creation, and a fixed-window distributed rate limiter keyed by client IP. Redis availability is part of `/ready`; `/health` remains process-only. The Redis adapter is injectable so tests use `fakeredis` without requiring a developer Redis server.

Redis persistence is configured for later container orchestration with AOF on a named volume. Although statistics can be rebuilt, persistence avoids losing rate-limit windows and preserves operational continuity across restarts; cached statistics remain disposable and are regenerated on a miss.

## Consequences

- Stats responses expose `X-Cache: HIT` or `MISS`.
- Rate-limited clients receive `429` and `Retry-After`.
- Redis is a required readiness dependency from Phase 4 onward.
- Redis container volume/network configuration belongs in the Docker/Compose phase and is not hidden in application code.
