# ADR-003: Hybrid Retrieval

## Context
Incident evidence mixes exact identifiers/error signatures with natural-language explanations. Either sparse or vector ranking alone misses useful signals.

## Decision
Run BM25 and cosine vector retrieval independently, fuse ranked IDs with Reciprocal Rank Fusion (`k=60`), then apply a bounded deterministic reranker and graph expansion.

## Alternatives considered
Weighted raw-score sums are difficult because score ranges differ; a cross-encoder adds model weight/latency; learned fusion lacks enough unbiased training data.

## Why
RRF is scale-independent, simple, reproducible, and easy to audit.

## Trade-offs
Rank-only fusion discards score magnitude, and heuristic reranking is domain-specific.

## Consequences
Evaluation reports dense, hybrid, and full pipeline separately; no improvement claim is made unless results support it.

