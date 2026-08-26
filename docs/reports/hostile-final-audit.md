# Hostile Implementation Audit

**Date:** 2026-08-26 (Asia/Dhaka)  
**Method:** Assume each resume claim is decorative, leaked, or misleading until code, tests, benchmark output, and production behavior disprove that hypothesis.

| Audit question | Verification | Result |
|---|---|---|
| Is the root cause hard-coded in the browser? | Runtime frontend contains none of `a81d2c`, `USD_US`, or `invalid_currency_format`; the report arrives from the API. | PASS |
| Does retrieval affect the answer? | Removing `commit-a81d2c` from evidence removes that commit from synthesis. | PASS |
| Does dense retrieval execute? | The 384-dimensional local feature-hash embedder normalizes document/query vectors and cosine scores execute in tests and benchmark. It is explicitly not called neural. | PASS |
| Does BM25 execute? | Corpus TF/DF/document-length scoring runs independently; exact-signature ranking is tested. | PASS |
| Does fusion execute? | Dense and sparse rankings feed reciprocal-rank fusion; exact RRF scores are tested. | PASS |
| Does the evidence graph matter? | Typed weighted links add graph-expanded evidence; deployment→commit behavior and full-pipeline metrics exercise it. | PASS |
| Does LangGraph control runtime? | The API invokes a compiled conditional `StateGraph`; traces show nine normal nodes and eleven corrective nodes. | PASS |
| Is LangChain used at runtime? | Ingestion creates LangChain `Document` objects and calls `RecursiveCharacterTextSplitter.split_documents`; the embedder implements its interface. | PASS |
| Does OpenAI integration exist? | Official OpenAI SDK adapter, environment key/model, structured output, timeout/retry, safe logging, and error translation are contract-tested without paid calls. | PASS |
| Are prompts versioned? | Five prompt families live under versioned directories; traversal is rejected and the report records `root_cause/v1`. | PASS |
| Are benchmark numbers reproducible? | v2 has 32 questions outside `demo/`; two executions produce identical aggregates and the README consistency gate passes. | PASS |
| Does the full pipeline beat simpler retrieval? | Recall@5 is 0.6778 dense, 0.8167 hybrid, and 0.8389 full pipeline; the actual committed output is reported without rounding inflation. | PASS |
| Does the system abstain when evidence is absent? | Two benchmark cases abstain; an API-level unsupported query returns unknown service and Low/0.25 confidence. | PASS |
| Is the deterministic demo misrepresented as an LLM call? | UI/Under the Hood identify it as a free deterministic provider and separately describe real OpenAI/Gemini adapters. | PASS |
| Is production genuinely working? | Desktop/mobile E2E, direct routes, refresh, evidence clicks, console/network probe, API health, corrective trace, headers, and CORS were exercised against stable aliases. | PASS |
| Is README language stronger than implementation? | Managed/neural vector DB, hosted-model quality, production-scale accuracy, and universal security are explicitly not claimed. | PASS |
| Are there obvious security problems? | Secret/history scans, dependency audits, injection/XSS/traversal/body/provider tests and production boundary checks pass; residual serverless risks are documented. | PASS with limitations |
| Is Git attribution correct? | Release commits use only `Niloy Bhuiyan <145592285+Niloy-Bhuiyan@users.noreply.github.com>` and contain no co-author metadata. | PASS |

## Claims deliberately constrained

- The production vector index is genuine but local/in-memory; it is not pgvector or a managed vector database.
- The feature-hash representation is deterministic and similarity-capable; it is weaker than a neural semantic embedding.
- The evidence corpus and benchmark are synthetic and cover one checkout incident, not production-wide accuracy.
- OpenAI and Gemini adapters are real and contract-tested, but no paid live-model quality claim is made.
- Process-local state and rate limiting are portfolio-demo tradeoffs, not production multi-tenant design.

## Verdict

**PASS for a recruiter-facing portfolio demonstration.** The implemented evidence pipeline, evaluation, provider boundary, and deployed interaction support the claims now made. The limitations above remain material and must stay visible.
