from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class EvidenceKind(StrEnum):
    SOURCE_CODE = "source_code"
    LOG = "log"
    COMMIT = "commit"
    DEPLOYMENT = "deployment"
    RELEASE_NOTE = "release_note"
    ISSUE = "issue"
    INCIDENT = "incident"
    DOCUMENTATION = "documentation"


class Evidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{2,79}$")
    source_id: str
    kind: EvidenceKind
    title: str
    content: str
    source_path: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    content_hash: str
    occurred_at: datetime | None = None


class EvidenceChunk(BaseModel):
    id: str
    evidence_id: str
    content: str
    chunk_index: int
    metadata: dict[str, Any]
    vector: list[float] = Field(default_factory=list, exclude=True)


class ScoreBreakdown(BaseModel):
    dense: float = 0.0
    sparse: float = 0.0
    fusion: float = 0.0
    rerank: float = 0.0
    graph: float = 0.0


class RankedEvidence(BaseModel):
    evidence: Evidence
    score: float
    breakdown: ScoreBreakdown = Field(default_factory=ScoreBreakdown)
    relationship: str | None = None


class Citation(BaseModel):
    evidence_id: str
    claim: str
    supports: bool = True


class TimelineEvent(BaseModel):
    occurred_at: datetime
    label: str
    evidence_id: str
    kind: str


class TraceStep(BaseModel):
    node: str
    status: str = "completed"
    duration_ms: float
    summary: str
    attempt: int = 1


class InvestigationReport(BaseModel):
    likely_root_cause: str
    confidence: str
    confidence_score: float = Field(ge=0, le=1)
    affected_service: str
    supporting_evidence: list[Citation]
    contradictions: list[Citation]
    relevant_files: list[str]
    relevant_commits: list[str]
    timeline: list[TimelineEvent]
    limitations: list[str]
    provider: str
    prompt_version: str


class ProviderDraft(BaseModel):
    likely_root_cause: str
    affected_service: str
    citations: list[Citation]
    contradictions: list[Citation]
    provider: str
    usage: dict[str, int] = Field(default_factory=dict)
