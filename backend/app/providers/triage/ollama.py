import httpx

from app.providers.triage.base import TriageResult


class OllamaTriage:
    name = "llm:ollama"

    def __init__(self, base_url: str, model: str, timeout: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    async def triage(self, text: str, location: str) -> TriageResult:
        prompt = (
            "Return JSON with category, priority, summary, confidence. Category must be one of "
            "water, electricity, sanitation, roads, streetlights, other. Priority must be high, "
            "normal, or low. Summary must be at most 140 characters.\n"
            f"Location: {location}\nComplaint: {text}"
        )
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "format": "json", "stream": False},
            )
            response.raise_for_status()
            return TriageResult.model_validate_json(response.json()["response"])
