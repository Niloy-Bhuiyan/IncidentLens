import json
from pathlib import Path

import pytest
from backend.app.evaluation.runner import run_evaluation


@pytest.mark.asyncio
async def test_benchmark_is_reproducible_and_full_pipeline_covers_ground_truth(
    repository_root: Path,
) -> None:
    first = await run_evaluation(repository_root, write=False)
    second = await run_evaluation(repository_root, write=False)

    assert first["aggregate"] == second["aggregate"]
    assert first["aggregate"]["full_pipeline"]["evidence_hit_rate"] == 1.0
    assert first["aggregate"]["full_pipeline"]["mrr"] >= first["aggregate"]["dense"]["mrr"]
    assert first["aggregate"]["hybrid"]["recall_at_5"] >= first["aggregate"]["dense"]["recall_at_5"]
    assert first["aggregate"]["full_pipeline"]["abstention_accuracy"] == 1.0
    assert 25 <= first["query_count"] <= 50
    assert first["retrieval_query_count"] == 30
    assert first["insufficient_evidence_query_count"] == 2
    assert all("expected" not in row for rows in first["queries"].values() for row in rows)


def test_ground_truth_is_separate_complete_and_category_balanced(repository_root: Path) -> None:
    dataset_path = repository_root / "evaluation" / "datasets" / "incident-retrieval-v2.json"
    dataset = json.loads(dataset_path.read_text(encoding="utf-8"))
    manifest = json.loads(
        (repository_root / "demo" / "checkout-incident" / "manifest.json").read_text(encoding="utf-8")
    )
    evidence_ids = {source["id"] for source in manifest["sources"]}
    expected_ids = {
        evidence_id for query in dataset["queries"] for evidence_id in query["expected"]
    }
    categories = {query["category"] for query in dataset["queries"]}

    assert dataset_path.parent.parent != repository_root / "demo"
    assert expected_ids <= evidence_ids
    assert len({query["id"] for query in dataset["queries"]}) == len(dataset["queries"])
    assert {
        "exact_error",
        "semantic_failure",
        "source_code",
        "deployment",
        "historical_incident",
        "multi_hop",
        "misleading_evidence",
        "insufficient_evidence",
    } <= categories
    assert sum(query.get("should_abstain", False) for query in dataset["queries"]) == 2
