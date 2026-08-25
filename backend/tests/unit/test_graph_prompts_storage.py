from pathlib import Path

import pytest
from backend.app.domain.models import RankedEvidence
from backend.app.graph import EvidenceGraph
from backend.app.ingestion import IngestionPipeline
from backend.app.prompts import load_prompt
from backend.app.storage import SQLiteRepository


def test_graph_expands_deployment_to_commit(repository_root: Path) -> None:
    result = IngestionPipeline(repository_root / "demo").ingest_demo("checkout-incident")
    graph = EvidenceGraph(result.evidence, result.manifest.relationships)
    deployment = next(item for item in result.evidence if item.id == "deployment-20260819")
    expanded = graph.expand([RankedEvidence(evidence=deployment, score=1.0)], limit=5)
    ids = {item.evidence.id for item in expanded}

    assert "commit-a81d2c" in ids
    assert any(item.relationship == "deploys" for item in expanded)


def test_prompt_loader_is_versioned_and_traversal_safe() -> None:
    prompt = load_prompt("root_cause", "v1")
    assert "untrusted" in prompt.lower()
    assert "supplied IDs" in prompt
    with pytest.raises(ValueError):
        load_prompt("../root_cause", "v1")


def test_sqlite_migration_creates_required_model_tables(tmp_path: Path) -> None:
    repository = SQLiteRepository(tmp_path / "incidentlens.db")
    try:
        assert repository.migrate() == 1
        assert repository.migrate() == 0
        assert {
            "investigations",
            "evidence_sources",
            "evidence_chunks",
            "entities",
            "evidence_relations",
            "retrieval_runs",
            "agent_runs",
            "agent_steps",
            "claims",
            "claim_evidence",
            "evaluation_runs",
        } <= repository.table_names()
    finally:
        repository.close()
