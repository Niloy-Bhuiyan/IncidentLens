# Recruiter-Readiness Baseline Audit

**Audit date:** 2026-08-26 (Asia/Dhaka)  
**Audited revision:** `c5182a5` plus the explicitly listed uncommitted deployment/CI corrections  
**Production:** `https://incidentlens-nine.vercel.app` and `https://incidentlens-api-delta.vercel.app`

## Verified working

- The FastAPI demo endpoint, investigation POST, trace, evidence, and evaluation endpoints execute on Vercel. A forced-corrective production run returned 10 ranked evidence items and an 11-step trace.
- The production desktop and Pixel 7 Playwright journeys pass: landing → investigation → root cause → evidence → evaluation → architecture → custom 404.
- Browser inspection found one `h1`, no horizontal overflow at desktop or 390 px, and no console errors on the landing, investigation, evidence, evaluation, architecture, or 404 paths.
- Runtime ingestion genuinely creates LangChain `Document` objects and uses `RecursiveCharacterTextSplitter`.
- Dense retrieval genuinely computes 384-dimensional feature-hash vectors and cosine similarity. BM25, reciprocal-rank fusion, reranking, and evidence-graph expansion all execute in the request path.
- A compiled LangGraph genuinely controls investigation nodes and its weak-evidence branch performs query rewriting and a second retrieval. Existing integration tests exercise that branch.
- The OpenAI provider uses the official async SDK, environment-only credentials, a configured model, 20-second timeout, two SDK retries, Pydantic structured output, bounded evidence, and safe translated errors. No paid call is required or claimed by the public demo.
- Prompts are versioned by purpose on disk and loaded at runtime. Ground truth is stored outside the indexed demo corpus.
- Baseline backend tests, Ruff, strict mypy, frontend tests, ESLint, TypeScript, production build, local E2E, production E2E, secret scan, and dependency audits had passed in the initial release pass.

## Material gaps to repair

| Area | Verified gap | Repair criterion |
|---|---|---|
| Five-second comprehension | “Find the change behind the failure” is elegant but makes the visitor infer the deployment-incident use case; AI mechanics appear before the concrete outcome. | First viewport explicitly says the app broke after a deployment, what is inspected, and what evidence-backed result the visitor gets. |
| Demo reliability | The browser starts one unbounded fetch. A stalled request can leave “Investigating” indefinitely, and progress is three static technical labels. | Add a bounded request, truthful stage progression, actionable retry, and tests for timeout/API failure without pretending server events exist. |
| Result clarity | The correct root cause is present but rendered as one long heading; concrete reasons are hidden behind generic claim prose. | Separate plain-language cause/explanation/confidence and show clickable “why” statements with their real source titles. |
| Provider clarity | The header says “Deterministic demo,” but the real OpenAI/Gemini provider layer is not explained where a recruiter will find it. | Add a concise provider explanation that distinguishes public deterministic mode from implemented real providers. |
| Architecture proof | `/architecture` explains the flow but does not point each recruiter-relevant technology to exact source files. | Add an “Under the Hood” page with verified implementation links and honest boundaries. |
| OpenAI proof tests | Configuration failure is tested, but the OpenAI adapter lacks mocked contract tests for structured success, usage, timeout/API error translation, and safe request boundaries. | Add zero-credit SDK-mocked provider tests. |
| Evaluation depth | `retrieval-v1.json` contains four synthetic queries. Metrics are reproducible but too small for a strong portfolio claim. | Expand to 25–50 reviewed queries including exact, semantic, source, deployment, commit, history, multi-hop, distractor, and insufficient-evidence cases; regenerate actual numbers. |
| Vector-store wording | Retrieval is real vector search, but storage is an in-process Python vector index—not an external vector database or neural embedding service. | Call it an in-memory vector store everywhere and explicitly state that pgvector is only a documented growth path. |
| Release evidence | Production smoke/security/hostile reports still describe deployment as pending, and the architecture doc says the API project root is `backend/` although deployed root is the monorepo root. | Reconcile docs with actual Vercel project settings and final test evidence. |
| Deployment automation | The API project is Git-connected. The frontend project is deployed and configured with root `frontend`, but its Git link is not yet present. | Connect the existing frontend Vercel project to the same repository and verify a pushed revision deploys correctly. |
| CI | The current committed benchmark gate compares a volatile timestamp, and the leak scanner lacks pull-request read permission. Local fixes exist but are not committed. | Make benchmark comparison semantic, grant least-privilege read access, and obtain green GitHub Actions. |

## Explicit non-findings

- No frontend hard-coded root-cause fixture was found. The visible answer comes from the API report.
- No keyword search is being mislabeled as dense retrieval: cosine search executes over computed vectors, although the embeddings are deterministic lexical feature hashes rather than neural semantic embeddings.
- No arbitrary URL ingestion, archive extraction, shell execution, or client-side provider secret path exists.
- The public demo does not call OpenAI and must not imply that it does.

This audit is the pre-change baseline for the repair pass. Later release reports must distinguish the improvements from these verified starting conditions.
