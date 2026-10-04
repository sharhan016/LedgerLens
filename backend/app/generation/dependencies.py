from functools import lru_cache

from app.core.config import get_settings
from app.generation.providers import LLMProvider, OpenAICompatibleProvider


@lru_cache
def get_llm_provider() -> LLMProvider:
    settings = get_settings()
    headers: dict[str, str] = {}
    if settings.llm_provider == "openrouter":
        headers = {
            "HTTP-Referer": "https://github.com/sharhan016/LedgerLens",
            "X-Title": "LedgerLens",
        }
    if settings.llm_provider not in {"openai_compatible", "openrouter", "local_openai"}:
        raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")
    return OpenAICompatibleProvider(
        base_url=settings.llm_base_url,
        model=settings.llm_model,
        api_key=settings.llm_api_key,
        timeout_seconds=settings.llm_timeout_seconds,
        extra_headers=headers,
    )

