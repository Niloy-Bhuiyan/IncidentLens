from __future__ import annotations

from typing import TypedDict

from backend.app.domain.models import InvestigationReport, ProviderDraft, RankedEvidence, TraceStep


class InvestigationState(TypedDict, total=False):
    question: str
    query: str
    provider_name: str
    force_corrective: bool
    attempt: int
    analysis: dict[str, object]
    plan: list[str]
    retrieved: list[RankedEvidence]
    sufficient: bool
    missing: list[str]
    draft: ProviderDraft
    report: InvestigationReport
    trace: list[TraceStep]
