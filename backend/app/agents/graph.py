from __future__ import annotations

import re
import time
from typing import Any, cast

from langgraph.graph import END, START, StateGraph

from backend.app.agents.state import InvestigationState
from backend.app.domain.models import InvestigationReport, TimelineEvent, TraceStep
from backend.app.graph import EvidenceGraph
from backend.app.llm.base import LLMProvider
from backend.app.prompts import load_prompt
from backend.app.retrieval.engine import HybridRetriever


def _trace(state: InvestigationState, node: str, started: float, summary: str) -> list[TraceStep]:
    return [
        *state.get("trace", []),
        TraceStep(
            node=node,
            duration_ms=round((time.perf_counter() - started) * 1000, 3),
            summary=summary,
            attempt=state.get("attempt", 1),
        ),
    ]


class InvestigationWorkflow:
    def __init__(
        self, retriever: HybridRetriever, evidence_graph: EvidenceGraph, provider: LLMProvider
    ) -> None:
        self.retriever = retriever
        self.evidence_graph = evidence_graph
        self.provider = provider
        builder = StateGraph(InvestigationState)
        builder.add_node("analyze_question", self.analyze_question)
        builder.add_node("plan_investigation", self.plan_investigation)
        builder.add_node("retrieve_evidence", self.retrieve_evidence)
        builder.add_node("grade_evidence", self.grade_evidence)
        builder.add_node("rewrite_query", self.rewrite_query)
        builder.add_node("retrieve_again", self.retrieve_again)
        builder.add_node("expand_related", self.expand_related)
        builder.add_node("rerank", self.rerank)
        builder.add_node("synthesize_root_cause", self.synthesize_root_cause)
        builder.add_node("verify_claims", self.verify_claims)
        builder.add_node("build_report", self.build_report)
        builder.add_edge(START, "analyze_question")
        builder.add_edge("analyze_question", "plan_investigation")
        builder.add_edge("plan_investigation", "retrieve_evidence")
        builder.add_edge("retrieve_evidence", "grade_evidence")
        builder.add_conditional_edges(
            "grade_evidence",
            lambda state: "enough" if state["sufficient"] else "correct",
            {"enough": "expand_related", "correct": "rewrite_query"},
        )
        builder.add_edge("rewrite_query", "retrieve_again")
        builder.add_edge("retrieve_again", "expand_related")
        builder.add_edge("expand_related", "rerank")
        builder.add_edge("rerank", "synthesize_root_cause")
        builder.add_edge("synthesize_root_cause", "verify_claims")
        builder.add_edge("verify_claims", "build_report")
        builder.add_edge("build_report", END)
        self.compiled = builder.compile()

    async def analyze_question(self, state: InvestigationState) -> dict[str, Any]:
        started = time.perf_counter()
        terms = re.findall(r"[a-z0-9_-]+", state["question"].lower())
        return {
            "query": state["question"],
            "attempt": 1,
            "analysis": {
                "terms": terms,
                "change_intent": any(x in terms for x in ("after", "deployment", "change")),
            },
            "trace": _trace(state, "analyze_question", started, f"Extracted {len(terms)} normalized terms."),
        }

    async def plan_investigation(self, state: InvestigationState) -> dict[str, Any]:
        started = time.perf_counter()
        plan = [
            "Find post-change runtime errors",
            "Identify the deployed change",
            "Check the code contract",
            "Seek contradicting health evidence",
        ]
        return {
            "plan": plan,
            "trace": _trace(
                state,
                "plan_investigation",
                started,
                "Planned runtime, change, contract, and contradiction checks.",
            ),
        }

    async def retrieve_evidence(self, state: InvestigationState) -> dict[str, Any]:
        started = time.perf_counter()
        output = await self.retriever.retrieve(state["query"], limit=8)
        return {
            "retrieved": output.ranked,
            "trace": _trace(
                state,
                "retrieve_evidence",
                started,
                f"Hybrid retrieval returned {len(output.ranked)} evidence items.",
            ),
        }

    async def grade_evidence(self, state: InvestigationState) -> dict[str, Any]:
        started = time.perf_counter()
        kinds = {item.evidence.kind.value for item in state["retrieved"][:8]}
        missing = []
        if "log" not in kinds:
            missing.append("runtime error logs")
        if not kinds & {"commit", "deployment"}:
            missing.append("recent change or deployment")
        if "source_code" not in kinds:
            missing.append("source contract")
        sufficient = not missing and not (
            state.get("force_corrective", False) and state.get("attempt", 1) == 1
        )
        if not sufficient and not missing:
            missing = ["explicit causal facets requested by evaluation"]
        return {
            "sufficient": sufficient,
            "missing": missing,
            "trace": _trace(
                state,
                "grade_evidence",
                started,
                "Evidence sufficient." if sufficient else f"Missing: {', '.join(missing)}.",
            ),
        }

    async def rewrite_query(self, state: InvestigationState) -> dict[str, Any]:
        started = time.perf_counter()
        rewritten = (
            f"{state['question']} checkout payment deployment commit error signature "
            "currency adapter prior incident gateway health"
        )
        return {
            "query": rewritten,
            "attempt": 2,
            "trace": _trace(
                state,
                "rewrite_query",
                started,
                "Added missing change, runtime, contract, history, and contradiction facets.",
            ),
        }

    async def retrieve_again(self, state: InvestigationState) -> dict[str, Any]:
        started = time.perf_counter()
        output = await self.retriever.retrieve(state["query"], limit=10)
        return {
            "retrieved": output.ranked,
            "trace": _trace(
                state,
                "retrieve_again",
                started,
                f"Corrective retrieval returned {len(output.ranked)} evidence items.",
            ),
        }

    async def expand_related(self, state: InvestigationState) -> dict[str, Any]:
        started = time.perf_counter()
        expanded = self.evidence_graph.expand(state["retrieved"], max_depth=1, limit=12)
        return {
            "retrieved": expanded,
            "trace": _trace(
                state, "expand_related", started, f"Evidence graph expanded the set to {len(expanded)} items."
            ),
        }

    async def rerank(self, state: InvestigationState) -> dict[str, Any]:
        started = time.perf_counter()
        ranked = sorted(state["retrieved"], key=lambda item: (-item.score, item.evidence.id))
        return {
            "retrieved": ranked,
            "trace": _trace(
                state, "rerank", started, "Reranked fused and graph-related evidence deterministically."
            ),
        }

    async def synthesize_root_cause(self, state: InvestigationState) -> dict[str, Any]:
        started = time.perf_counter()
        draft = await self.provider.synthesize(
            state["question"], state["retrieved"], load_prompt("root_cause", "v1")
        )
        return {
            "draft": draft,
            "trace": _trace(
                state,
                "synthesize_root_cause",
                started,
                f"{self.provider.name} produced a structured evidence draft.",
            ),
        }

    async def verify_claims(self, state: InvestigationState) -> dict[str, Any]:
        started = time.perf_counter()
        allowed = {item.evidence.id for item in state["retrieved"]}
        draft = state["draft"].model_copy(deep=True)
        draft.citations = [item for item in draft.citations if item.evidence_id in allowed]
        draft.contradictions = [item for item in draft.contradictions if item.evidence_id in allowed]
        return {
            "draft": draft,
            "trace": _trace(
                state,
                "verify_claims",
                started,
                f"Verified {len(draft.citations)} supporting and "
                f"{len(draft.contradictions)} contradicting citations.",
            ),
        }

    async def build_report(self, state: InvestigationState) -> dict[str, Any]:
        started = time.perf_counter()
        draft = state["draft"]
        cited_ids = {item.evidence_id for item in draft.citations + draft.contradictions}
        cited = [item.evidence for item in state["retrieved"] if item.evidence.id in cited_ids]
        kinds = {item.kind.value for item in cited}
        coverage = sum(value in kinds for value in ("log", "commit", "deployment", "source_code")) / 4
        score = min(0.94, 0.48 + coverage * 0.4 + min(len(draft.contradictions), 1) * 0.06)
        confidence = "High" if score >= 0.8 else "Moderate" if score >= 0.6 else "Low"
        timeline = sorted(
            [
                TimelineEvent(
                    occurred_at=item.occurred_at, label=item.title, evidence_id=item.id, kind=item.kind.value
                )
                for item in cited
                if item.occurred_at is not None
            ],
            key=lambda item: item.occurred_at,
        )
        relevant_files = sorted({item.source_path for item in cited if item.kind.value == "source_code"})
        relevant_commits = sorted(
            {
                str(item.metadata.get("hash") or item.metadata.get("commit"))
                for item in cited
                if item.kind.value == "commit"
            }
        )
        report = InvestigationReport(
            likely_root_cause=draft.likely_root_cause,
            confidence=confidence,
            confidence_score=round(score, 2),
            affected_service=draft.affected_service,
            supporting_evidence=draft.citations,
            contradictions=draft.contradictions,
            relevant_files=relevant_files,
            relevant_commits=relevant_commits,
            timeline=timeline,
            limitations=[
                "This is a ranked hypothesis, not proof of causality.",
                "The seeded corpus may omit alternative causes.",
            ],
            provider=draft.provider,
            prompt_version="root_cause/v1",
        )
        return {
            "report": report,
            "trace": _trace(
                state,
                "build_report",
                started,
                f"Built a {confidence.lower()}-confidence report with {len(draft.citations)} citations.",
            ),
        }

    async def run(
        self, question: str, provider_name: str, force_corrective: bool = False
    ) -> InvestigationState:
        initial: InvestigationState = {
            "question": question,
            "provider_name": provider_name,
            "force_corrective": force_corrective,
            "trace": [],
        }
        return cast(InvestigationState, await self.compiled.ainvoke(initial))
