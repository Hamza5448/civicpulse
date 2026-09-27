from app.db.models.complaint import Category, Priority
from app.providers.triage.base import TriageResult


class SimulatedTriage:
    name = "simulated"

    def __init__(self, should_fail: bool = False) -> None:
        self.should_fail = should_fail

    async def triage(self, text: str, location: str) -> TriageResult:
        if self.should_fail:
            raise RuntimeError("simulated provider failure")
        return TriageResult(
            category=Category.OTHER,
            priority=Priority.NORMAL,
            summary=f"Simulated: {text.strip()}"[:140],
            confidence=0.5,
        )
