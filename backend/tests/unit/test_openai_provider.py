from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast

import httpx
import pytest
from backend.app.domain.models import Citation, Evidence, EvidenceKind, ProviderDraft, RankedEvidence
from backend.app.llm.base import ProviderExecutionError
from backend.app.llm.openai_provider import OpenAIProvider
from openai import APITimeoutError


def _evidence(content: str = "invalid_currency_format currency=USD_US") -> RankedEvidence:
    return RankedEvidence(
        evidence=Evidence(
            id="log-checkout-errors",
            source_id="checkout-incident",
            kind=EvidenceKind.LOG,
            title="Checkout errors",
            content=content,
            source_path="logs/checkout-errors.jsonl",
            content_hash="a" * 64,
        ),
        score=1.0,
    )


class FakeResponses:
    def __init__(self, result: object | None = None, error: Exception | None = None) -> None:
        self.result = result
        self.error = error
        self.request: dict[str, Any] = {}

    async def parse(self, **kwargs: Any) -> object:
        self.request = kwargs
        if self.error:
            raise self.error
        return self.result


@pytest.mark.asyncio
async def test_openai_provider_requests_structured_output_and_records_usage() -> None:
    draft = ProviderDraft(
        likely_root_cause="The currency value violated the adapter contract.",
        affected_service="checkout-api",
        citations=[Citation(evidence_id="log-checkout-errors", claim="Shows the error")],
        contradictions=[],
        provider="untrusted-provider-label",
    )
    responses = FakeResponses(
        SimpleNamespace(
            output_parsed=draft,
            usage=SimpleNamespace(input_tokens=120, output_tokens=45),
        )
    )
    provider = OpenAIProvider("test-key-not-real", model="gpt-test-model")
    provider.client = cast(Any, SimpleNamespace(responses=responses))

    result = await provider.synthesize("Why did checkout fail?", [_evidence("x" * 2_500)], "prompt")

    assert responses.request["model"] == "gpt-test-model"
    assert responses.request["text_format"] is ProviderDraft
    assert len(responses.request["input"][1]["content"]) < 2_100
    assert result.provider == "openai"
    assert result.usage == {"input_tokens": 120, "output_tokens": 45}


@pytest.mark.asyncio
async def test_openai_provider_translates_timeout_without_leaking_details() -> None:
    timeout = APITimeoutError(request=httpx.Request("POST", "https://api.openai.com/v1/responses"))
    responses = FakeResponses(error=timeout)
    provider = OpenAIProvider("test-key-not-real")
    provider.client = cast(Any, SimpleNamespace(responses=responses))

    with pytest.raises(ProviderExecutionError, match="OpenAI request failed") as raised:
        await provider.synthesize("Why did checkout fail?", [_evidence()], "prompt")

    assert "test-key" not in str(raised.value)
