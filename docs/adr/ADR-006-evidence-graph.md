# ADR-006: Evidence Graph

## Context
Useful incident connections are relational: a deployment contains a commit, which changes a file used by a service that emits an error signature.

## Decision
Build an in-memory typed weighted adjacency graph from explicit manifest/metadata relationships and use it for post-retrieval expansion, reranking, and evidence navigation.

## Alternatives considered
Neo4j is excessive for a tiny immutable corpus. Pure relational joins hide multi-hop exploration inside storage code. An untyped graph weakens provenance.

## Why
The simple graph makes causal paths observable without external infrastructure.

## Trade-offs
Relationship quality depends on curated metadata and does not infer novel entities.

## Consequences
Edges retain relation type, weight, and provenance; graph contribution is measured independently in full-pipeline evaluation.

