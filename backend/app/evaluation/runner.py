from __future__ import annotations

import argparse
import asyncio
import json
from datetime import UTC, datetime
from pathlib import Path
from statistics import mean
from typing import Any

from backend.app.agents import InvestigationWorkflow
from backend.app.graph import EvidenceGraph
from backend.app.ingestion import IngestionPipeline
from backend.app.llm.mock_provider import DeterministicMockProvider
from backend.app.retrieval.engine import HybridRetriever


def _metrics(ranked_ids: list[str], expected: list[str], k: int = 5) -> dict[str, float]:
    top = ranked_ids[:k]
    expected_set = set(expected)
    if not expected_set:
        return {
            f"recall_at_{k}": 0.0,
            f"precision_at_{k}": 0.0,
            "mrr": 0.0,
            "evidence_hit_rate": 0.0,
            "root_cause_evidence_coverage": 0.0,
        }
    hits = [identifier for identifier in top if identifier in expected_set]
    first_rank = next(
        (index for index, identifier in enumerate(ranked_ids, start=1) if identifier in expected_set), None
    )
    return {
        f"recall_at_{k}": len(set(hits)) / len(expected_set),
        f"precision_at_{k}": len(hits) / k,
        "mrr": 0.0 if first_rank is None else 1.0 / first_rank,
        "evidence_hit_rate": 1.0 if hits else 0.0,
        "root_cause_evidence_coverage": len(set(top) & expected_set) / len(expected_set),
    }


def _load_dataset(root: Path | None) -> tuple[Path, dict[str, Any]]:
    repository_root = root or Path(__file__).resolve().parents[3]
    dataset_path = repository_root / "evaluation" / "datasets" / "incident-retrieval-v2.json"
    return repository_root, json.loads(dataset_path.read_text(encoding="utf-8"))


def _write_result(repository_root: Path, result: dict[str, Any]) -> None:
    output_dir = repository_root / "evaluation" / "results"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "latest.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


async def run_evaluation(root: Path | None = None, write: bool = True) -> dict[str, Any]:
    repository_root, dataset = _load_dataset(root)
    ingestion = IngestionPipeline(repository_root / "demo").ingest_demo("checkout-incident")
    retriever = HybridRetriever(ingestion.manifest.id, ingestion.evidence, ingestion.chunks)
    await retriever.build()
    graph = EvidenceGraph(ingestion.evidence, ingestion.manifest.relationships)
    workflow = InvestigationWorkflow(retriever, graph, DeterministicMockProvider())
    configurations: dict[str, list[dict[str, Any]]] = {"dense": [], "hybrid": [], "full_pipeline": []}
    for query in dataset["queries"]:
        scored_for_retrieval = not query.get("should_abstain", False)
        for strategy in ("dense", "hybrid"):
            output = await retriever.retrieve(query["question"], limit=10, strategy=strategy)
            ids = [item.evidence.id for item in output.ranked]
            configurations[strategy].append(
                {
                    "query_id": query["id"],
                    "category": query["category"],
                    "scored_for_retrieval": scored_for_retrieval,
                    "ranked_ids": ids,
                    **_metrics(ids, query["expected"]),
                }
            )
        state = await workflow.run(query["question"], "mock")
        ids = [item.evidence.id for item in state["retrieved"]]
        abstained = "insufficient" in state["report"].likely_root_cause.lower()
        configurations["full_pipeline"].append(
            {
                "query_id": query["id"],
                "category": query["category"],
                "scored_for_retrieval": scored_for_retrieval,
                "ranked_ids": ids,
                "abstained": abstained,
                **_metrics(ids, query["expected"]),
            }
        )
    aggregate: dict[str, dict[str, float]] = {}
    metric_names = [
        "recall_at_5",
        "precision_at_5",
        "mrr",
        "evidence_hit_rate",
        "root_cause_evidence_coverage",
    ]
    for name, rows in configurations.items():
        scored_rows = [row for row in rows if row["scored_for_retrieval"]]
        aggregate[name] = {
            metric: round(mean(row[metric] for row in scored_rows), 4) for metric in metric_names
        }
        insufficient_rows = [row for row in rows if not row["scored_for_retrieval"]]
        aggregate[name]["abstention_accuracy"] = (
            round(mean(float(row.get("abstained", False)) for row in insufficient_rows), 4)
            if insufficient_rows
            else 0.0
        )
    categories = sorted({query["category"] for query in dataset["queries"]})
    result = {
        "schema_version": "1.0",
        "dataset_version": dataset["version"],
        "generated_at": datetime.now(UTC).isoformat(),
        "query_count": len(dataset["queries"]),
        "retrieval_query_count": sum(not query.get("should_abstain", False) for query in dataset["queries"]),
        "insufficient_evidence_query_count": sum(
            query.get("should_abstain", False) for query in dataset["queries"]
        ),
        "categories": categories,
        "k": 5,
        "embedding": "local-feature-hash-384-v1",
        "fusion": "rrf-k60",
        "prompt_configuration": (
            "root_cause/v1 (full pipeline runs LangGraph; prose is scored only for abstention)"
        ),
        "aggregate": aggregate,
        "queries": configurations,
    }
    if write:
        _write_result(repository_root, result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic IncidentLens retrieval evaluation")
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    result = asyncio.run(run_evaluation(write=not args.no_write))
    print(json.dumps(result["aggregate"], indent=2))


if __name__ == "__main__":
    main()
