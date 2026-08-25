# Data Architecture

## Normalized evidence

Every item has `id`, `source_id`, `kind`, `title`, `content`, `source_path`, `metadata`, `content_hash`, and optional `occurred_at`. Chunk records add parent ID, zero-based chunk index, line range, and embedding vector outside relational serialization.

## Relational model

| Entity | Purpose | Principal relations |
|---|---|---|
| Investigation | Question, status, report, timestamps | has retrieval/agent runs and claims |
| EvidenceSource | Original normalized artifact | has chunks; refers to entities |
| EvidenceChunk | Searchable unit and metadata | belongs to source; backs claims |
| Entity | Service/file/symbol/commit/deployment/signature/issue/incident/event | participates in evidence relations |
| EvidenceRelation | Typed directed edge with weight/provenance | connects entities/evidence |
| RetrievalRun | Query, strategy, timing, ranked IDs | belongs to investigation |
| AgentRun | Workflow execution and prompt/provider version | belongs to investigation; has steps |
| AgentStep | Node, transition, duration, safe summary | belongs to agent run |
| Claim | Text, confidence, verification state | belongs to investigation |
| ClaimEvidence | Claim-to-evidence support/contradiction edge | joins claim and chunk/source |
| EvaluationRun | Dataset/configuration/metrics/commit | independent reproducibility record |

## Indexes and lifecycle

SQLite migrations create identifiers, foreign keys, timestamps, and indexes on investigation status, source kind/hash, chunk source, relation endpoints, and run ownership. Demo evidence indexes are process-local and immutable after construction. Re-ingestion replaces a namespace atomically and deduplicates by SHA-256 content hash.

## Vector abstraction

`VectorStore` defines asynchronous upsert, search, and namespace deletion. The local implementation stores normalized computed vectors and performs cosine similarity. A pgvector adapter can retain the same contract. PostgreSQL + pgvector remains the recommended durable target when multi-user persistence is added.

## Trust and provenance

Content is never executable. Source path is a normalized repository-relative identifier, not a read primitive exposed to the client. All graph edges name their derivation (`manifest`, `metadata`, or retrieval expansion). Claims refer to evidence IDs that must exist in the current namespace.

