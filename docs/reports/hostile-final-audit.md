# Hostile Implementation Audit

**Date:** 2026-08-26 (Asia/Dhaka)  
**Method:** Assume resume-driven/decorative implementation, answer leakage, broken branches, or misleading claims until verified.

| Audit question | Verification | Result |
|---|---|---|
| Does the product solve the seeded incident? | Local API/UI/E2E return a deployment → commit → currency contract violation → error path with citations. | PASS |
| Is the answer hidden in the frontend? | `rg` finds no `a81d2c`, `USD_US`, or `invalid_currency_format` in runtime frontend app/components/lib. | PASS |
| Does evidence affect the output? | Integration test removes `commit-a81d2c`; result no longer names that commit. | PASS |
| Is LangChain decorative? | Ingestion constructs LangChain `Document`, executes `RecursiveCharacterTextSplitter.split_documents`, and retrieval implements LangChain `Embeddings`. | PASS |
| Is LangGraph decorative? | Runtime constructs/compiles `StateGraph`; API/UI trace shows nine nodes; forced test shows rewrite/retrieve-again. | PASS |
| Is vector search real? | 384-dimensional computed vectors are normalized and stored; query vectors are compared with cosine dot product. Determinism/vector difference tests pass. | PASS |
| Is sparse search real? | Corpus DF/TF/document length BM25 formula is executed; exact-signature ranking test passes. | PASS |
| Is hybrid fusion real? | Independent dense and sparse rankings feed scale-independent RRF; exact RRF score test passes. | PASS |
| Does graph contribute? | Explicit typed weighted edges expand ranked evidence and add graph score; deployment→commit test and full benchmark path pass. | PASS |
| Is provider behavior honest? | Mock identifies itself; missing OpenAI returns 503; official OpenAI/Gemini adapters exist behind protocol; no hosted call is claimed/tested without credentials. | PASS with limitation |
| Are prompts versioned/bounded? | Five purpose directories with v1/v2 where specified; loader traversal test; untrusted-data rules in every prompt. | PASS |
| Is benchmark truth leaked into retrieval? | Ground truth is under `evaluation/`; ingestion indexes only `demo/`; expected IDs are not present in ingestion/retrieval/graph modules. | PASS |
| Can metrics be reproduced? | Runner executed twice with identical aggregates; README consistency script passes. | PASS |
| Are security claims measured? | Dedicated tests/scans/audits and explicit residual-risk language. | PASS |
| Is UI fake or generic? | Real API response drives report/evidence/timeline; browser captures show calm evidence workspace, responsive behavior, and source navigation. | PASS |
| Are there obvious dead imports/typing errors? | Ruff and strict mypy pass. | PASS |
| Is Git attribution correct? | All commits list only `Niloy Bhuiyan <niloybhuiyann@gmail.com>`; no co-author metadata. | PASS |
| Is production genuinely working? | Must be filled after actual Vercel smoke run; no inference from local success. | PENDING |

## Claims deliberately constrained

- The local feature embedding is not described as a neural semantic model.
- Synthetic four-query metrics are not generalized to production accuracy.
- Mock provider output is evidence-driven deterministic synthesis, not a successful hosted LLM call.
- PostgreSQL/pgvector is a documented replacement target, not the deployed v1 store.
- Passing tests is not described as proof of universal security.

## Status

Local hostile audit: **PASS**. Overall audit remains **PENDING** until deployed production behavior, CORS, console, network, mobile, and direct routes are inspected.

