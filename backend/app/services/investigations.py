from __future__ import annotations

import asyncio
import uuid
from collections import Counter
from datetime import UTC, datetime

from pydantic import BaseModel

from backend.app.agents import InvestigationWorkflow
from backend.app.config import Settings
from backend.app.domain.models import Evidence, InvestigationReport, RankedEvidence, TraceStep
from backend.app.graph import EvidenceGraph
from backend.app.ingestion import IngestionPipeline, IngestionResult
from backend.app.llm import create_provider
from backend.app.retrieval.engine import HybridRetriever


class InvestigationRecord(BaseModel):
    id: str
    question: str
    status: str
    created_at: datetime
    completed_at: datetime
    report: InvestigationReport
    evidence: list[RankedEvidence]
    trace: list[TraceStep]


class InvestigationService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.pipeline = IngestionPipeline(settings.demo_root, settings.max_file_bytes)
        self._lock = asyncio.Lock()
        self._ingestion: IngestionResult | None = None
        self._retriever: HybridRetriever | None = None
        self._graph: EvidenceGraph | None = None
        self._investigations: dict[str, InvestigationRecord] = {}

    async def ensure_demo(self, rebuild: bool = False) -> IngestionResult:
        if self._ingestion is not None and not rebuild:
            return self._ingestion
        async with self._lock:
            if self._ingestion is not None and not rebuild:
                return self._ingestion
            result = self.pipeline.ingest_demo("checkout-incident")
            retriever = HybridRetriever(result.manifest.id, result.evidence, result.chunks)
            await retriever.build()
            self._ingestion = result
            self._retriever = retriever
            self._graph = EvidenceGraph(result.evidence, result.manifest.relationships)
            return result

    async def investigate(
        self, question: str, provider_name: str, force_corrective: bool = False
    ) -> InvestigationRecord:
        await self.ensure_demo()
        assert self._retriever is not None and self._graph is not None
        provider = create_provider(provider_name, self.settings)
        workflow = InvestigationWorkflow(self._retriever, self._graph, provider)
        created_at = datetime.now(UTC)
        state = await workflow.run(question, provider_name, force_corrective)
        identifier = f"inv-{uuid.uuid4().hex[:12]}"
        record = InvestigationRecord(
            id=identifier,
            question=question,
            status="completed",
            created_at=created_at,
            completed_at=datetime.now(UTC),
            report=state["report"],
            evidence=state["retrieved"],
            trace=state["trace"],
        )
        self._investigations[identifier] = record
        return record

    def get_investigation(self, investigation_id: str) -> InvestigationRecord | None:
        return self._investigations.get(investigation_id)

    async def get_evidence(self, evidence_id: str) -> tuple[Evidence, list[dict[str, object]]] | None:
        result = await self.ensure_demo()
        item = next((value for value in result.evidence if value.id == evidence_id), None)
        if item is None:
            return None
        assert self._graph is not None
        relations = [
            {
                "target": edge.target,
                "type": edge.relation,
                "weight": edge.weight,
                "provenance": edge.provenance,
            }
            for edge in self._graph.relations_for(evidence_id)
        ]
        return item, relations

    async def demo_summary(self) -> dict[str, object]:
        result = await self.ensure_demo()
        return {
            "id": result.manifest.id,
            "title": result.manifest.title,
            "suggested_question": result.manifest.suggested_question,
            "occurred_at": result.manifest.occurred_at,
            "source_count": len(result.evidence),
            "chunk_count": len(result.chunks),
            "source_types": dict(Counter(item.kind.value for item in result.evidence)),
            "relationship_count": len(result.manifest.relationships),
        }
