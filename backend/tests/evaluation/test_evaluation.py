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
    assert all("expected" not in row for rows in first["queries"].values() for row in rows)
