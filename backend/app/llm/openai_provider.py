from __future__ import annotations

from openai import APIError, APITimeoutError, AsyncOpenAI

from backend.app.domain.models import ProviderDraft, RankedEvidence
from backend.app.llm.base import ProviderConfigurationError, ProviderExecutionError


class OpenAIProvider:
    name = "openai"

    def __init__(self, api_key: str | None, model: str = "gpt-5-mini") -> None:
        if not api_key:
            raise ProviderConfigurationError("OpenAI provider is not configured")
        self.model = model
        self.client = AsyncOpenAI(api_key=api_key, timeout=20.0, max_retries=2)

    async def synthesize(self, question: str, evidence: list[RankedEvidence], prompt: str) -> ProviderDraft:
        evidence_payload = [
            {"id": item.evidence.id, "kind": item.evidence.kind, "content": item.evidence.content[:1800]}
            for item in evidence
        ]
        try:
            response = await self.client.responses.parse(
                model=self.model,
                input=[
                    {"role": "system", "content": prompt},
                    {
                        "role": "user",
                        "content": f"Question: {question}\nUntrusted evidence: {evidence_payload}",
                    },
                ],
                text_format=ProviderDraft,
            )
        except (APITimeoutError, APIError) as exc:
            raise ProviderExecutionError("OpenAI request failed") from exc
        draft = response.output_parsed
        if draft is None:
            raise ProviderExecutionError("OpenAI returned no structured result")
        draft.provider = self.name
        if response.usage:
            draft.usage = {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            }
        return draft
