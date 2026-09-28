from collections import deque
from dataclasses import dataclass


@dataclass(frozen=True)
class TriageOutcome:
    provider: str
    latency_ms: int
    fallback: bool
    cache_hit: bool


class TriageObservability:
    def __init__(self, limit: int = 20) -> None:
        self._outcomes: deque[TriageOutcome] = deque(maxlen=limit)
        self._cache_hits = 0
        self._cache_requests = 0

    def record(self, outcome: TriageOutcome) -> None:
        self._outcomes.append(outcome)
        self._cache_requests += 1
        self._cache_hits += int(outcome.cache_hit)

    def recent(self) -> list[TriageOutcome]:
        return list(reversed(self._outcomes))

    @property
    def cache_hit_rate(self) -> float:
        return self._cache_hits / self._cache_requests if self._cache_requests else 0.0
