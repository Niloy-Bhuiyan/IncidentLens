from pathlib import Path

import pytest
from backend.app.config import Settings


@pytest.fixture
def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


@pytest.fixture
def settings(repository_root: Path) -> Settings:
    return Settings(
        demo_root=repository_root / "demo",
        evaluation_root=repository_root / "evaluation",
        rate_limit_per_minute=200,
    )
