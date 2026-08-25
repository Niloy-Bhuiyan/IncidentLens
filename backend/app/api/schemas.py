from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from backend.app.domain.models import Evidence, InvestigationReport, RankedEvidence, TraceStep


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class IngestionRequest(StrictModel):
    demo_id: Literal["checkout-incident"] = "checkout-incident"


class IngestionResponse(StrictModel):
    namespace: str
    source_count: int
    chunk_count: int
    duplicate_count: int
    relationship_count: int


class InvestigationRequest(StrictModel):
    question: str = Field(min_length=3, max_length=500)
    provider: Literal["mock", "openai", "gemini"] = "mock"
    force_corrective: bool = False


class InvestigationResponse(StrictModel):
    id: str
    question: str
    status: str
    created_at: datetime
    completed_at: datetime
    report: InvestigationReport
    evidence: list[RankedEvidence]
    trace: list[TraceStep]


class TraceResponse(StrictModel):
    investigation_id: str
    trace: list[TraceStep]


class EvidenceResponse(StrictModel):
    evidence: Evidence
    relations: list[dict[str, Any]]


class ErrorBody(StrictModel):
    code: str
    message: str
    request_id: str
    details: list[dict[str, Any]] | None = None


class ErrorResponse(StrictModel):
    error: ErrorBody
