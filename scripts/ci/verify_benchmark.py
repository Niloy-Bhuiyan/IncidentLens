from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
results = json.loads(
    (ROOT / "evaluation" / "results" / "latest.json").read_text(encoding="utf-8")
)
readme = (ROOT / "README.md").read_text(encoding="utf-8")

for configuration in ("dense", "hybrid", "full_pipeline"):
    for metric in ("recall_at_5", "mrr"):
        value = f"{results['aggregate'][configuration][metric]:.4f}"
        if value not in readme:
            raise SystemExit(
                f"README is missing generated {configuration} {metric} value {value}"
            )

print("README benchmark values match evaluation/results/latest.json")
