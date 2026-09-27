from app.db.models.complaint import Category, Priority
from app.providers.triage.base import TriageResult


class RuleBasedTriage:
    name = "rules"

    async def triage(self, text: str, location: str) -> TriageResult:
        normalized = f"{text} {location}".lower()
        keywords = {
            Category.WATER: ("water", "flood", "leak", "pipe", "sewer"),
            Category.ELECTRICITY: ("electric", "power", "wire", "transformer"),
            Category.SANITATION: ("garbage", "waste", "drain", "sewage"),
            Category.STREETLIGHTS: ("streetlight", "lamp", "light pole"),
            Category.ROADS: ("road", "pothole", "street", "traffic"),
        }
        category = next(
            (candidate for candidate, terms in keywords.items() if any(term in normalized for term in terms)),
            Category.OTHER,
        )
        urgent_terms = ("flood", "burst", "danger", "fire", "exposed", "emergency")
        priority = Priority.HIGH if any(term in normalized for term in urgent_terms) else Priority.NORMAL
        summary = text.strip().replace("\n", " ")[:140]
        return TriageResult(category=category, priority=priority, summary=summary, confidence=0.75)
