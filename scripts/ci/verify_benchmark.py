from __future__ import annotations

import asyncio
import json
from pathlib import Path

from backend.app.evaluation.runner import run_evaluation

ROOT = Path(__file__).resolve().parents[2]
results = json.loads(
    (ROOT / "evaluation" / "results" / "latest.json").read_text(encoding="utf-8")
)
readme = (ROOT / "README.md").read_text(encoding="utf-8")
fresh = asyncio.run(run_evaluation(root=ROOT, write=False))

stable_fields = (
    "schema_version",
    "dataset_version",
    "query_count",
    "retrieval_query_count",
    "insufficient_evidence_query_count",
    "categories",
    "k",
    "embedding",
    "fusion",
    "prompt_configuration",
    "aggregate",
    "queries",
)
for field in stable_fields:
    if fresh[field] != results[field]:
        raise SystemExit(f"Committed benchmark differs from a clean run in field: {field}")

for configuration in ("dense", "hybrid", "full_pipeline"):
    for metric in ("recall_at_5", "mrr"):
        value = f"{results['aggregate'][configuration][metric]:.4f}"
        if value not in readme:
            raise SystemExit(
                f"README is missing generated {configuration} {metric} value {value}"
            )

print("Committed benchmark is reproducible and README values match")
