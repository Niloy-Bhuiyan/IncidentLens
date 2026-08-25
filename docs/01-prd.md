# Product Requirements Document

## Problem statement

Production-incident evidence lives in incompatible tools and formats. Responders must reconstruct causal order while under time pressure, and generative summaries may obscure missing or contradictory evidence. IncidentLens must produce an inspectable, evidence-backed hypothesis—not an assertion of guaranteed root cause.

## Users

Primary users are software engineers, SREs, DevOps engineers, and technical leads. Engineering managers and QA/release engineers are secondary users who need an understandable record of what was checked and why the hypothesis is credible.

## User goals

- Identify the service and change most closely associated with a failure spike.
- Find relevant logs without manually searching every source.
- Connect runtime errors to changed files, deployments, and prior incidents.
- Inspect raw evidence before accepting a conclusion.
- See contradictions and confidence, not only confirming evidence.

## v1 scope

The product ingests controlled local source, JSON/text logs, Markdown/text documents, release/commit/issue metadata, deployment metadata, and previous incidents. It normalizes and chunks evidence, computes local embeddings, runs BM25 and vector searches, fuses and reranks results, expands an evidence graph, orchestrates corrective retrieval with LangGraph, and returns a cited report.

## Non-goals

- Executing uploaded source, applying remediations, or changing production systems.
- Replacing logs, tracing, APM, or source-control products.
- Arbitrary enterprise connectors or unrestricted public-repository ingestion.
- Remote URL/archive ingestion, where SSRF and archive traversal broaden risk.
- Guaranteeing a root cause or presenting provider output as fact.
- Multi-tenant authorization, durable cloud storage, or real-time streaming in v1.

## Success criteria

1. The seeded demo runs without provider keys and returns a report produced from indexed evidence.
2. Dense, sparse, hybrid, graph expansion, evidence grading, corrective retrieval, claim verification, and citations are observable and tested.
3. The deterministic benchmark compares dense-only, hybrid, and full-pipeline retrieval using committed ground truth.
4. The production UI exposes the source behind each supporting claim and works at 390 px and desktop widths.
5. Local and CI quality/security gates are reproducible from documented commands.

## Acceptance criteria

| ID | Given | When | Then |
|---|---|---|---|
| AC-01 | Fresh default setup | `POST /api/v1/investigations` asks the demo question | A completed report includes root-cause hypothesis, confidence, service, timeline, contradictions, cited evidence, and trace. |
| AC-02 | Seed manifest | Demo ingestion runs | Every supported type is normalized and indexed; duplicates are rejected. |
| AC-03 | Known benchmark queries | Evaluation runs | Machine-readable Recall@5, MRR, and evidence coverage exist for all three configurations. |
| AC-04 | A deliberately weak first query | Workflow runs | Trace contains grade, rewrite, and a second retrieve transition. |
| AC-05 | Selected cited evidence | User opens its route | Underlying content and metadata render without unsafe HTML. |
| AC-06 | Missing OpenAI/Gemini key | That provider is requested | API returns a typed safe error; mock mode remains functional. |
| AC-07 | Traversal/oversized/malformed ingestion request | API validates it | Request is rejected without reading outside the allowlisted demo root. |
| AC-08 | Production deployment | Smoke suite and browser inspection run | Landing, demo, investigation, evidence, evaluation, architecture, 404, health, direct refresh, desktop, and mobile checks pass. |

## Risks

Lexical feature-hash embeddings are smaller and cheaper than neural embeddings but understand fewer semantic paraphrases. The seeded dataset is intentionally small and does not establish general production accuracy. Stateless serverless deployment does not retain arbitrary ingestion across cold starts.

