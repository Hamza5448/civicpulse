from collections import deque
from dataclasses import dataclass


@dataclass(frozen=True)
class TriageOutcome:
    provider: str
    latency_ms: int
    fallback: bool


class TriageObservability:
    def __init__(self, limit: int = 20) -> None:
        self._outcomes: deque[TriageOutcome] = deque(maxlen=limit)

    def record(self, outcome: TriageOutcome) -> None:
        self._outcomes.append(outcome)

    def recent(self) -> list[TriageOutcome]:
        return list(reversed(self._outcomes))
