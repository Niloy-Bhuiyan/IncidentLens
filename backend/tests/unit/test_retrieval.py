import math
from pathlib import Path

import pytest
from backend.app.ingestion import IngestionPipeline
from backend.app.retrieval.engine import (
    BM25Index,
    HybridRetriever,
    LocalHashEmbeddings,
    reciprocal_rank_fusion,
)


def test_embedding_is_real_normalized_and_deterministic() -> None:
    embeddings = LocalHashEmbeddings(dimensions=64)
    first = embeddings.embed_query("checkout deployment failure")
    second = embeddings.embed_query("checkout deployment failure")

    assert first == second
    assert len(first) == 64
    assert math.isclose(math.sqrt(sum(value * value for value in first)), 1.0)
    assert first != embeddings.embed_query("unrelated inventory success")


def test_rrf_uses_independent_ranks() -> None:
    fused = reciprocal_rank_fusion([[("a", 99), ("b", 1)], [("b", 500), ("c", 2)]], k=60)
    assert fused["b"] == pytest.approx(1 / 62 + 1 / 61)
    assert fused["a"] == pytest.approx(1 / 61)


@pytest.mark.asyncio
async def test_dense_sparse_and_hybrid_are_distinct(repository_root: Path) -> None:
    result = IngestionPipeline(repository_root / "demo").ingest_demo("checkout-incident")
    retriever = HybridRetriever(result.manifest.id, result.evidence, result.chunks)
    await retriever.build()

    dense = await retriever.retrieve("latest deployment checkout failures", strategy="dense", limit=5)
    sparse = await retriever.retrieve("latest deployment checkout failures", strategy="sparse", limit=5)
    hybrid = await retriever.retrieve("latest deployment checkout failures", strategy="hybrid", limit=5)

    assert dense.dense_ids
    assert sparse.sparse_ids
    assert any(item.breakdown.dense != 0 for item in hybrid.ranked)
    assert any(item.breakdown.sparse != 0 for item in hybrid.ranked)
    assert {item.evidence.id for item in hybrid.ranked} & {"deployment-20260819", "log-checkout-errors"}


def test_bm25_prefers_exact_error_signature(repository_root: Path) -> None:
    result = IngestionPipeline(repository_root / "demo").ingest_demo("checkout-incident")
    index = BM25Index(result.chunks)
    ranked = index.search("invalid_currency_format", limit=5)
    chunk_map = {chunk.id: chunk for chunk in result.chunks}
    assert chunk_map[ranked[0][0]].evidence_id in {
        "log-checkout-errors",
        "src-stripe-adapter",
        "incident-2025-11",
    }
