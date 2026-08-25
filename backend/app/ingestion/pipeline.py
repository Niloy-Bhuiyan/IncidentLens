from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path
from typing import Any

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from backend.app.domain.models import Evidence, EvidenceChunk, EvidenceKind

ALLOWED_SUFFIXES = {".py", ".json", ".jsonl", ".md", ".txt"}


class ManifestSource(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    kind: EvidenceKind
    title: str
    path: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ManifestRelation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    from_id: str = Field(alias="from")
    to_id: str = Field(alias="to")
    type: str
    weight: float = Field(ge=0, le=1)


class DemoManifest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    title: str
    suggested_question: str
    occurred_at: datetime
    sources: list[ManifestSource]
    relationships: list[ManifestRelation]


class IngestionResult(BaseModel):
    manifest: DemoManifest
    evidence: list[Evidence]
    chunks: list[EvidenceChunk]
    duplicate_count: int


class UnsafeSourceError(ValueError):
    pass


def _resolve_safe(root: Path, relative_path: str) -> Path:
    candidate = (root / relative_path).resolve()
    root = root.resolve()
    if candidate != root and root not in candidate.parents:
        raise UnsafeSourceError("source path leaves the allowlisted demo root")
    if candidate.suffix.lower() not in ALLOWED_SUFFIXES:
        raise UnsafeSourceError("unsupported evidence type")
    return candidate


def _clean_text(text: str) -> str:
    text = text.replace("\x00", "")
    return "\n".join(line.rstrip() for line in text.replace("\r\n", "\n").split("\n")).strip()


def _parse_content(path: Path, kind: EvidenceKind) -> tuple[str, dict[str, Any], datetime | None]:
    raw = path.read_text(encoding="utf-8")
    extracted: dict[str, Any] = {}
    occurred_at: datetime | None = None
    if path.suffix == ".json":
        value = json.loads(raw)
        if not isinstance(value, dict):
            raise ValueError("JSON evidence must be an object")
        for key in ("timestamp", "opened_at", "completed_at"):
            if isinstance(value.get(key), str):
                occurred_at = datetime.fromisoformat(value[key].replace("Z", "+00:00"))
                break
        extracted.update(
            {
                key: value[key]
                for key in value.keys()
                & {
                    "hash",
                    "message",
                    "changed_files",
                    "commit",
                    "deployment",
                    "service",
                    "diff",
                    "error_signature",
                    "number",
                    "status",
                }
            }
        )
        return json.dumps(value, indent=2, sort_keys=True), extracted, occurred_at
    if path.suffix == ".jsonl":
        rows: list[dict[str, Any]] = []
        for number, line in enumerate(raw.splitlines(), start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"malformed JSON log line {number}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"log line {number} must be an object")
            rows.append(row)
        timestamps: list[str] = []
        for row in rows:
            timestamp = row.get("timestamp")
            if isinstance(timestamp, str):
                timestamps.append(timestamp)
        if timestamps:
            occurred_at = datetime.fromisoformat(timestamps[0].replace("Z", "+00:00"))
        extracted["event_count"] = len(rows)
        extracted["trace_ids"] = [row["trace_id"] for row in rows if "trace_id" in row]
        extracted["severities"] = sorted({str(row.get("severity", "UNKNOWN")) for row in rows})
        signatures = [row.get("error_signature") for row in rows if row.get("error_signature")]
        if signatures:
            extracted["error_signature"] = max(set(signatures), key=signatures.count)
        return "\n".join(json.dumps(row, sort_keys=True) for row in rows), extracted, occurred_at
    if kind == EvidenceKind.SOURCE_CODE:
        symbols = re.findall(r"^(?:async\s+)?(?:def|class)\s+([A-Za-z_]\w*)", raw, re.MULTILINE)
        extracted["symbols"] = symbols
        extracted["language"] = path.suffix.lstrip(".")
    if path.suffix == ".md":
        headings = re.findall(r"^#{1,6}\s+(.+)$", raw, re.MULTILINE)
        extracted["sections"] = headings
    return _clean_text(raw), extracted, occurred_at


class IngestionPipeline:
    def __init__(self, demo_root: Path, max_file_bytes: int = 262_144) -> None:
        self.demo_root = demo_root.resolve()
        self.max_file_bytes = max_file_bytes
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=900,
            chunk_overlap=120,
            separators=["\n\n", "\n", " ", ""],
            add_start_index=True,
        )

    def ingest_demo(self, demo_id: str) -> IngestionResult:
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]{2,39}", demo_id):
            raise UnsafeSourceError("invalid demo identifier")
        demo_dir = (self.demo_root / demo_id).resolve()
        if self.demo_root not in demo_dir.parents:
            raise UnsafeSourceError("invalid demo root")
        manifest_path = demo_dir / "manifest.json"
        if not manifest_path.is_file() or manifest_path.stat().st_size > self.max_file_bytes:
            raise UnsafeSourceError("demo manifest is unavailable or too large")
        try:
            manifest = DemoManifest.model_validate_json(manifest_path.read_text(encoding="utf-8"))
        except (ValidationError, json.JSONDecodeError) as exc:
            raise ValueError("invalid demo manifest") from exc
        if manifest.id != demo_id:
            raise ValueError("manifest id does not match requested demo")

        evidence: list[Evidence] = []
        hashes: set[str] = set()
        duplicate_count = 0
        for source in manifest.sources:
            path = _resolve_safe(demo_dir, source.path)
            if not path.is_file() or path.stat().st_size > self.max_file_bytes:
                raise UnsafeSourceError("evidence file is unavailable or too large")
            content, extracted, occurred_at = _parse_content(path, source.kind)
            digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
            if digest in hashes:
                duplicate_count += 1
                continue
            hashes.add(digest)
            metadata = {**source.metadata, **extracted}
            evidence.append(
                Evidence(
                    id=source.id,
                    source_id=manifest.id,
                    kind=source.kind,
                    title=source.title,
                    content=content,
                    source_path=source.path.replace("\\", "/"),
                    metadata=metadata,
                    content_hash=digest,
                    occurred_at=occurred_at,
                )
            )

        chunks = list(self._chunk(evidence))
        return IngestionResult(
            manifest=manifest, evidence=evidence, chunks=chunks, duplicate_count=duplicate_count
        )

    def _chunk(self, evidence_items: Iterable[Evidence]) -> Iterable[EvidenceChunk]:
        for item in evidence_items:
            documents = self.splitter.split_documents(
                [Document(page_content=item.content, metadata={"evidence_id": item.id, **item.metadata})]
            )
            for index, document in enumerate(documents):
                yield EvidenceChunk(
                    id=f"{item.id}-chunk-{index}",
                    evidence_id=item.id,
                    content=document.page_content,
                    chunk_index=index,
                    metadata={**document.metadata, "kind": item.kind.value, "source_path": item.source_path},
                )
