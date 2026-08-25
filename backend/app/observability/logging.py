from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import Any


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")


def log_event(event: str, **fields: Any) -> None:
    safe = {key: value for key, value in fields.items() if key not in {"content", "prompt", "api_key"}}
    logging.getLogger("incidentlens").info(
        json.dumps(
            {"timestamp": datetime.now(UTC).isoformat(), "event": event, **safe}, default=str, sort_keys=True
        )
    )
