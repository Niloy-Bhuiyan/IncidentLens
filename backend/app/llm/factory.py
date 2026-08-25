from backend.app.config import Settings
from backend.app.llm.base import LLMProvider
from backend.app.llm.gemini_provider import GeminiProvider
from backend.app.llm.mock_provider import DeterministicMockProvider
from backend.app.llm.openai_provider import OpenAIProvider


def create_provider(name: str, settings: Settings) -> LLMProvider:
    if name == "mock":
        return DeterministicMockProvider()
    if name == "openai":
        return OpenAIProvider(settings.openai_api_key)
    if name == "gemini":
        return GeminiProvider(settings.gemini_api_key)
    raise ValueError("unknown provider")
