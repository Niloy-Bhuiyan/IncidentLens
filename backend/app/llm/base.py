from __future__ import annotations

from typing import Protocol

from backend.app.domain.models import ProviderDraft, RankedEvidence


class ProviderConfigurationError(RuntimeError):
    pass


class ProviderExecutionError(RuntimeError):
    pass


class LLMProvider(Protocol):
    name: str

    async def synthesize(
        self, question: str, evidence: list[RankedEvidence], prompt: str
    ) -> ProviderDraft: ...
