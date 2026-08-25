from __future__ import annotations

import hashlib
import math
import re
from collections import Counter, defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from langchain_core.embeddings import Embeddings

from backend.app.domain.models import Evidence, EvidenceChunk, RankedEvidence, ScoreBreakdown

TOKEN_RE = re.compile(r"[a-z0-9_./-]+")
SYNONYMS = {
    "failures": "error",
    "failure": "error",
    "failed": "error",
    "increase": "spike",
    "increased": "spike",
    "deploy": "deployment",
    "deployed": "deployment",
    "change": "commit",
    "changed": "commit",
    "payments": "payment",
}


def tokenize(text: str) -> list[str]:
    tokens = [SYNONYMS.get(token, token) for token in TOKEN_RE.findall(text.lower())]
    return tokens + [f"{left}::{right}" for left, right in zip(tokens, tokens[1:], strict=False)]


class LocalHashEmbeddings(Embeddings):
    """Small deterministic feature-hash embeddings for local/serverless retrieval."""

    def __init__(self, dimensions: int = 384) -> None:
        self.dimensions = dimensions

    def _embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token, count in Counter(tokenize(text)).items():
            digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
            bucket = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] & 1 else -1.0
            vector[bucket] += sign * (1.0 + math.log(count))
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)


class VectorStore(Protocol):
    async def upsert(self, namespace: str, chunks: Sequence[EvidenceChunk]) -> None: ...
    async def search(self, namespace: str, query: str, limit: int) -> list[tuple[str, float]]: ...
    async def delete_namespace(self, namespace: str) -> None: ...


class InMemoryVectorStore:
    def __init__(self, embeddings: Embeddings | None = None) -> None:
        self.embeddings = embeddings or LocalHashEmbeddings()
        self._vectors: dict[str, dict[str, list[float]]] = {}

    async def upsert(self, namespace: str, chunks: Sequence[EvidenceChunk]) -> None:
        vectors = self.embeddings.embed_documents([chunk.content for chunk in chunks])
        self._vectors[namespace] = {chunk.id: vector for chunk, vector in zip(chunks, vectors, strict=True)}

    async def search(self, namespace: str, query: str, limit: int) -> list[tuple[str, float]]:
        query_vector = self.embeddings.embed_query(query)
        scores = [
            (chunk_id, sum(a * b for a, b in zip(query_vector, vector, strict=True)))
            for chunk_id, vector in self._vectors.get(namespace, {}).items()
        ]
        return sorted(scores, key=lambda item: (-item[1], item[0]))[:limit]

    async def delete_namespace(self, namespace: str) -> None:
        self._vectors.pop(namespace, None)


class BM25Index:
    def __init__(self, chunks: Sequence[EvidenceChunk]) -> None:
        self.chunks = list(chunks)
        self.documents = [tokenize(chunk.content) for chunk in chunks]
        self.term_frequencies = [Counter(tokens) for tokens in self.documents]
        self.document_frequencies = Counter(token for tokens in self.documents for token in set(tokens))
        self.average_length = sum(map(len, self.documents)) / max(len(self.documents), 1)

    def search(self, query: str, limit: int, k1: float = 1.5, b: float = 0.75) -> list[tuple[str, float]]:
        query_tokens = set(tokenize(query))
        count = len(self.documents)
        ranked: list[tuple[str, float]] = []
        for chunk, terms, tokens in zip(self.chunks, self.term_frequencies, self.documents, strict=True):
            score = 0.0
            for token in query_tokens:
                frequency = terms[token]
                if not frequency:
                    continue
                docs_with_term = self.document_frequencies[token]
                inverse = math.log(1 + (count - docs_with_term + 0.5) / (docs_with_term + 0.5))
                denominator = frequency + k1 * (1 - b + b * len(tokens) / max(self.average_length, 1))
                score += inverse * frequency * (k1 + 1) / denominator
            ranked.append((chunk.id, score))
        return sorted(ranked, key=lambda item: (-item[1], item[0]))[:limit]


def reciprocal_rank_fusion(rankings: Sequence[Sequence[tuple[str, float]]], k: int = 60) -> dict[str, float]:
    fused: defaultdict[str, float] = defaultdict(float)
    for ranking in rankings:
        for rank, (item_id, _) in enumerate(ranking, start=1):
            fused[item_id] += 1.0 / (k + rank)
    return dict(fused)


@dataclass(slots=True)
class RetrievalOutput:
    ranked: list[RankedEvidence]
    dense_ids: list[str]
    sparse_ids: list[str]


class HybridRetriever:
    def __init__(self, namespace: str, evidence: Sequence[Evidence], chunks: Sequence[EvidenceChunk]) -> None:
        self.namespace = namespace
        self.evidence = {item.id: item for item in evidence}
        self.chunks = {chunk.id: chunk for chunk in chunks}
        self.vector_store = InMemoryVectorStore()
        self.sparse = BM25Index(chunks)

    async def build(self) -> None:
        await self.vector_store.upsert(self.namespace, list(self.chunks.values()))

    async def retrieve(self, query: str, limit: int = 8, strategy: str = "hybrid") -> RetrievalOutput:
        candidate_limit = min(max(limit * 3, 12), len(self.chunks))
        dense = await self.vector_store.search(self.namespace, query, candidate_limit)
        sparse = self.sparse.search(query, candidate_limit)
        if strategy == "dense":
            fused = {item_id: score for item_id, score in dense}
        elif strategy == "sparse":
            fused = {item_id: score for item_id, score in sparse}
        else:
            fused = reciprocal_rank_fusion([dense, sparse])
        dense_scores = dict(dense)
        sparse_scores = dict(sparse)
        best_by_evidence: dict[str, RankedEvidence] = {}
        for chunk_id, fusion_score in fused.items():
            chunk = self.chunks[chunk_id]
            item = self.evidence[chunk.evidence_id]
            query_terms = set(tokenize(query))
            content_terms = set(tokenize(item.title + " " + item.content))
            coverage = len(query_terms & content_terms) / max(len(query_terms), 1)
            authority = {
                "log": 0.16,
                "commit": 0.15,
                "deployment": 0.14,
                "source_code": 0.13,
                "incident": 0.10,
                "issue": 0.08,
                "release_note": 0.06,
                "documentation": 0.04,
            }[item.kind.value]
            rerank = coverage * 0.45 + authority
            score = fusion_score + rerank if strategy == "hybrid" else fusion_score
            candidate = RankedEvidence(
                evidence=item,
                score=score,
                breakdown=ScoreBreakdown(
                    dense=dense_scores.get(chunk_id, 0),
                    sparse=sparse_scores.get(chunk_id, 0),
                    fusion=fusion_score,
                    rerank=rerank,
                ),
            )
            current = best_by_evidence.get(item.id)
            if current is None or candidate.score > current.score:
                best_by_evidence[item.id] = candidate
        ranked = sorted(best_by_evidence.values(), key=lambda item: (-item.score, item.evidence.id))[:limit]
        return RetrievalOutput(
            ranked=ranked,
            dense_ids=[self.chunks[item_id].evidence_id for item_id, _ in dense],
            sparse_ids=[self.chunks[item_id].evidence_id for item_id, _ in sparse],
        )
