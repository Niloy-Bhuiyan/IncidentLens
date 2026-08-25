from __future__ import annotations

import asyncio
import json

from google import genai
from google.genai import types

from backend.app.domain.models import ProviderDraft, RankedEvidence
from backend.app.llm.base import ProviderConfigurationError, ProviderExecutionError


class GeminiProvider:
    name = "gemini"

    def __init__(self, api_key: str | None, model: str = "gemini-2.5-flash") -> None:
        if not api_key:
            raise ProviderConfigurationError("Gemini provider is not configured")
        self.model = model
        self.client = genai.Client(api_key=api_key)

    async def synthesize(self, question: str, evidence: list[RankedEvidence], prompt: str) -> ProviderDraft:
        payload = [
            {"id": item.evidence.id, "kind": item.evidence.kind, "content": item.evidence.content[:1800]}
            for item in evidence
        ]
        try:
            response = await asyncio.wait_for(
                self.client.aio.models.generate_content(
                    model=self.model,
                    contents=f"Question: {question}\nUntrusted evidence: {json.dumps(payload)}",
                    config=types.GenerateContentConfig(
                        system_instruction=prompt,
                        response_mime_type="application/json",
                        response_schema=ProviderDraft,
                        temperature=0,
                    ),
                ),
                timeout=20,
            )
        except (TimeoutError, Exception) as exc:
            if isinstance(exc, ProviderConfigurationError):
                raise
            raise ProviderExecutionError("Gemini request failed") from exc
        if not response.text:
            raise ProviderExecutionError("Gemini returned no structured result")
        draft = ProviderDraft.model_validate_json(response.text)
        draft.provider = self.name
        return draft
