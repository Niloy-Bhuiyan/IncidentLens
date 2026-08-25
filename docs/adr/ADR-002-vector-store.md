# ADR-002: Vector Store

## Context
The demo needs genuine vector search without a paid service or a serverless-incompatible model/database.

## Decision
Define an async `VectorStore` protocol and ship an in-memory cosine store using deterministic LangChain-compatible feature-hash embeddings. Keep PostgreSQL/pgvector as the documented durable adapter target; provide local Docker pgvector for integration work.

## Alternatives considered
Bundled sentence-transformer models improve semantics but increase function size/startup and model-distribution risk. Chroma/FAISS add native/runtime complexity. Hosted pgvector adds configuration and cost to the recruiter path. SQL keyword search is not vector search.

## Why
Computed fixed-dimensional vectors and cosine similarity meet the behavioral requirement while remaining inspectable, deterministic, fast, and portable.

## Trade-offs
The embedding is lexical/feature-based and has weaker semantic generalization than neural embeddings; memory is process-local.

## Consequences
Benchmarks must describe the embedding honestly. Storage can be replaced without changing the graph or API.

