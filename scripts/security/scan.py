from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEXT_SUFFIXES = {
    ".css",
    ".env",
    ".example",
    ".html",
    ".js",
    ".json",
    ".jsonl",
    ".md",
    ".mjs",
    ".py",
    ".sql",
    ".svg",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
}
SECRET_PATTERNS = {
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "GitHub token": re.compile(r"gh[opsu]_[A-Za-z0-9]{30,}"),
    "OpenAI-style key": re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    "assigned credential": re.compile(
        r"(?i)(?:api[_-]?key|client[_-]?secret|access[_-]?token|password)\s*[:=]\s*['\"][A-Za-z0-9_./+=-]{16,}['\"]"
    ),
}


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-co", "--exclude-standard"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [ROOT / value for value in result.stdout.splitlines() if value]


def scan_text(label: str, text: str) -> list[str]:
    return [
        f"{label}: possible {name}"
        for name, pattern in SECRET_PATTERNS.items()
        if pattern.search(text)
    ]


def main() -> int:
    findings: list[str] = []
    for path in tracked_files():
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        relative = path.relative_to(ROOT).as_posix()
        if relative in {".env", ".env.local", ".env.production"}:
            findings.append(f"{relative}: secret-bearing environment file is tracked")
        text = path.read_text(encoding="utf-8", errors="ignore")
        findings.extend(scan_text(relative, text))
        if relative.startswith("frontend/") and path.suffix in {".ts", ".tsx"}:
            unsafe_html_token = "dangerously" + "SetInnerHTML"
            if unsafe_html_token in text:
                findings.append(f"{relative}: unsafe React HTML escape hatch present")

    history = subprocess.run(
        ["git", "log", "-p", "--all", "--no-ext-diff", "--no-color"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        errors="ignore",
    ).stdout
    findings.extend(scan_text("Git history", history))

    if findings:
        print("IncidentLens security scan: FAIL")
        for finding in sorted(set(findings)):
            print(f"- {finding}")
        return 1
    print(
        f"IncidentLens security scan: PASS ({len(tracked_files())} files + Git history)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
