from app.core.config import Settings
from app.providers.triage.base import TriageProvider
from app.providers.triage.llm import LLMTriage
from app.providers.triage.ollama import OllamaTriage
from app.providers.triage.rules import RuleBasedTriage
from app.providers.triage.simulated import SimulatedTriage


def create_triage_provider(settings: Settings) -> TriageProvider:
    if settings.triage_provider == "rules":
        return RuleBasedTriage()
    if settings.triage_provider == "simulated":
        return SimulatedTriage()
    if settings.triage_provider == "ollama":
        return OllamaTriage(
            settings.triage_ollama_base_url, settings.triage_ollama_model, settings.triage_timeout_seconds
        )
    if settings.triage_provider == "llm":
        if not settings.triage_llm_api_key:
            raise ValueError("TRIAGE_LLM_API_KEY is required when TRIAGE_PROVIDER=llm")
        return LLMTriage(
            settings.triage_llm_base_url,
            settings.triage_llm_model,
            settings.triage_llm_api_key,
            settings.triage_timeout_seconds,
        )
    raise ValueError(f"Unsupported TRIAGE_PROVIDER: {settings.triage_provider}")
