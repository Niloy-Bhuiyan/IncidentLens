from functools import lru_cache
from pathlib import Path


@lru_cache
def load_prompt(purpose: str, version: str = "v1") -> str:
    if not purpose.replace("_", "").isalnum() or not version.startswith("v") or not version[1:].isdigit():
        raise ValueError("invalid prompt identifier")
    root = Path(__file__).resolve().parent
    path = (root / purpose / f"{version}.md").resolve()
    if root not in path.parents or not path.is_file():
        raise ValueError("prompt version not found")
    return path.read_text(encoding="utf-8")
