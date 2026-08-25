import json
from pathlib import Path

import pytest
from backend.app.ingestion.pipeline import IngestionPipeline, UnsafeSourceError, _resolve_safe


def test_ingests_every_supported_demo_type(repository_root: Path) -> None:
    result = IngestionPipeline(repository_root / "demo").ingest_demo("checkout-incident")

    assert len(result.evidence) == 10
    assert len(result.chunks) >= 10
    assert result.duplicate_count == 0
    assert {item.kind.value for item in result.evidence} == {
        "source_code",
        "log",
        "commit",
        "deployment",
        "release_note",
        "issue",
        "incident",
        "documentation",
    }


def test_extracts_source_and_log_metadata(repository_root: Path) -> None:
    result = IngestionPipeline(repository_root / "demo").ingest_demo("checkout-incident")
    source = next(item for item in result.evidence if item.id == "src-payment-service")
    log = next(item for item in result.evidence if item.id == "log-checkout-errors")

    assert "normalize_currency" in source.metadata["symbols"]
    assert log.metadata["error_signature"] == "invalid_currency_format"
    assert log.metadata["event_count"] == 4
    assert log.occurred_at is not None


def test_rejects_traversal_and_unsupported_suffix(tmp_path: Path) -> None:
    root = tmp_path / "demo"
    root.mkdir()
    with pytest.raises(UnsafeSourceError):
        _resolve_safe(root, "../secret.txt")
    with pytest.raises(UnsafeSourceError):
        _resolve_safe(root, "payload.exe")


def test_rejects_manifest_id_mismatch(tmp_path: Path) -> None:
    demo = tmp_path / "checkout-incident"
    demo.mkdir()
    (demo / "manifest.json").write_text(
        json.dumps(
            {
                "id": "another-demo",
                "title": "bad",
                "suggested_question": "bad",
                "occurred_at": "2026-01-01T00:00:00Z",
                "sources": [],
                "relationships": [],
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="does not match"):
        IngestionPipeline(tmp_path).ingest_demo("checkout-incident")
