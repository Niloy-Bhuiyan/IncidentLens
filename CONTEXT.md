# IncidentLens Continuation Context

Last fully updated: 2026-08-26, Asia/Dhaka. The repository, Git history, GitHub Actions, and deployed responses are the source of truth if they conflict with this checkpoint.

## Project goal

IncidentLens is a recruiter-ready, evidence-first AI incident investigator. A visitor runs one seeded checkout incident; the real backend ingests logs, source, commits, deployment/release records, issues, and prior incidents, then executes hybrid retrieval, evidence-graph expansion, a conditional LangGraph workflow, provider synthesis, citation verification, and an inspectable report.

## Current architecture

```text
Next.js 16 / React 19 frontend (Vercel web project)
  → typed HTTP API
FastAPI 0.141 backend (Vercel Python function via api/index.py)
  → controlled manifest + evidence files
  → LangChain Documents + RecursiveCharacterTextSplitter
  → 384d local feature-hash vectors + cosine AND BM25
  → reciprocal-rank fusion → evidence graph expansion/reranking
  → compiled conditional LangGraph
  → provider protocol: deterministic demo | OpenAI | Gemini
  → citation allowlist + confidence/timeline/report
```

The deployed vector index is real, local, and in-memory. It is not pgvector, a managed vector database, or a neural embedding model. SQLite schema/repository code exists as the relational persistence seam, but serverless investigation state remains process-local in v1.

## Important product and SDLC decisions

- The first viewport explains the human problem before AI terms: broken deployment → investigate evidence → cited root cause.
- The workspace is organized as What failed → Why IncidentLens thinks it failed → Evidence.
- The public hosted demo uses the deterministic provider so visitors never spend paid credits. It does not pretend a hosted model call occurred.
- OpenAI and Gemini are real server-side adapters behind the same provider protocol; OpenAI uses the official SDK, server-only environment key/model, structured Pydantic output, 20-second timeout, two SDK retries, translated errors, and safe logging.
- LangChain is used at runtime for `Document` construction, text splitting, and the embeddings interface; LangGraph compiles and executes the real API investigation state machine.
- The corrective branch is conditional and tested: grade → rewrite → retrieve again → expand → rerank → synthesize → verify → report.
- Evidence is controlled UTF-8 content under `demo/`; benchmark truth is separate under `evaluation/` to prevent direct indexing/leakage.
- No remote URL/archive/user-file ingestion and no evidence execution in v1.
- See `docs/adr/ADR-001` through `ADR-007` for repository, vector, retrieval, workflow, provider, graph, and deployment choices.

## Repository and file structure

```text
api/index.py                         Vercel FastAPI entrypoint
backend/app/
  agents/                            LangGraph state and workflow
  ingestion/                         LangChain preparation/chunking
  retrieval/                         vectors, cosine, BM25, RRF, reranking
  graph/                             typed evidence graph
  llm/                               provider protocol + mock/OpenAI/Gemini
  prompts/                           five versioned prompt families
  api/, services/, security/         HTTP, orchestration, middleware
backend/tests/                       unit, integration, API, provider/security tests
frontend/app/                        landing, investigation, evidence, evaluation,
                                     architecture, Under the Hood, about, 404
frontend/components/                 demo and evidence workspace
demo/checkout-incident/              controlled synthetic evidence corpus
evaluation/datasets/                 32-query v2 benchmark ground truth
evaluation/results/latest.json       actual generated metrics
tests/e2e/                           desktop/mobile journey + failure/retry
scripts/ci/                          benchmark and production-browser verification
scripts/security/                    working-tree and Git-history secret scanner
docs/                                PRD, architecture, ADRs, reports, screenshots
```

## Technologies and versions

- Local: Python 3.13.5 (project supports 3.12–3.14), Node 24.15.0, pnpm 11.19.0.
- Backend: FastAPI 0.141.1, LangChain Core 1.6.0, LangGraph 1.2.11, OpenAI SDK 3.3.1, Google GenAI 2.19.0, Pydantic Settings, pytest, Ruff, strict mypy.
- Frontend: Next.js 16.3.3, React 19.2.8, TypeScript 6.0.2, Vitest 4.1.11, Playwright 1.62.1.
- Deployment: two Git-connected Vercel projects.

## Environment and dependency setup

```powershell
pnpm install
python -m pip install -e "backend[dev]"
Copy-Item .env.example .env
```

Default local/public provider is `mock`. Relevant variables:

- `INCIDENTLENS_LLM_PROVIDER`
- `INCIDENTLENS_OPENAI_API_KEY`, `INCIDENTLENS_OPENAI_MODEL`
- `INCIDENTLENS_GEMINI_API_KEY`, `INCIDENTLENS_GEMINI_MODEL`
- `INCIDENTLENS_ALLOWED_ORIGINS`
- `NEXT_PUBLIC_API_BASE_URL`

Never put provider keys in `NEXT_PUBLIC_*` variables. Do not commit `.env`, `.vercel`, credentials, databases, coverage/build output, or provider responses containing secrets.

## Git state

- Branch: `main`
- Remote: `origin https://github.com/Niloy-Bhuiyan/IncidentLens.git`
- Visibility: private, per the original delivery requirement; do not make public without user approval.
- Identity: `Niloy Bhuiyan <145592285+Niloy-Bhuiyan@users.noreply.github.com>`
- Latest functional commit: `df15e79 fix(ai): lower confidence for unsupported questions`
- This checkpoint is followed by release-evidence/checkpoint-only commits; run `git log -5 --format='%h %an <%ae> %s'` for their exact hashes.
- No history was rewritten and no co-author metadata is present.

Major repair commits before this checkpoint:

```text
cd451a2 fix(delivery): stabilize CI and Vercel builds
5c5d75e fix(ux): clarify and harden the incident demo
a13166b feat(ai): verify model providers and safe abstention
50b7b49 test(eval): expand incident retrieval benchmark
b196f50 feat(docs): expose verified AI architecture
278d4ea docs(readme): present verified engineering proof
df15e79 fix(ai): lower confidence for unsupported questions
```

## Completed features

- Clear five-second homepage and focused, responsive three-column evidence workspace.
- Reliable demo with bounded timeout, real progress labels, error state, and retry.
- Clickable log/code/commit/deployment/history evidence and dedicated evidence route.
- Actual LangChain preparation and actual compiled/conditional LangGraph runtime.
- Dense vectors, BM25, RRF hybrid fusion, evidence-graph expansion, reranking, citation verification, trace, timeline, and confidence.
- Corrective second retrieval branch plus automated test.
- Evidence-mutation test proving retrieval affects synthesis.
- Evidence-driven deterministic provider with unsupported-question abstention and Low confidence.
- OpenAI/Gemini provider adapters; OpenAI mocked contract tests cover SDK, structured output, retry/timeout configuration, bounded evidence, usage, safe errors, and no paid call.
- Versioned prompts and safe prompt loader.
- 32-query benchmark: 30 retrieval cases + 2 insufficient-evidence cases across 12 categories.
- `/evaluation`, `/under-the-hood`, `/architecture`, `/about`, investigation/evidence routes, and custom 404.
- Recruiter-ready README, SDLC documentation, ADRs, threat model, release/security/system/hostile/production reports, and real production screenshots.
- Git-connected frontend/API Vercel production deployments and green GitHub workflows.

## Partially completed or intentionally limited

- OpenAI and Gemini adapters are contract-tested but not quality-tested with live paid tokens.
- Vector storage is an in-memory local implementation; a managed pgvector adapter is only a documented future replacement.
- Corpus/benchmark are synthetic and limited to one checkout scenario. The 32 questions vary retrieval intent but reuse the same evidence set.
- Investigation state and rate limiting are per-process/serverless instance, not durable/global.
- SQLite persistence seam exists but production does not use durable authenticated multi-user storage.
- Repository remains private. Public source access for recruiters requires explicit user approval.
- A 15–30 second GIF was not added; the README uses clean real screenshots because a trustworthy GIF was not necessary for Definition of Done.

## Exact unfinished work

No release-blocking implementation work remains for the bounded portfolio demo. Optional next work, only if requested:

1. Obtain user approval before changing the GitHub repository from private to public.
2. Run a small, budget-capped live OpenAI smoke/evaluation only if the user supplies/authorizes credentials and paid usage.
3. Add a pgvector/Qdrant adapter and neural embedding configuration if managed-vector experience is desired.
4. Add a second independent incident corpus before making broader retrieval-quality claims.
5. Add durable shared investigation state and global rate limiting before arbitrary multi-user/public ingestion.

## Current bugs and errors

- No known release-blocking bug.
- Expected limitation: a generated investigation ID can disappear after a Vercel instance recycle; the demo route can rebuild it.
- Expected limitation: the frontend 25-second timeout protects the UX but a severe platform outage still yields the explicit retry state.
- Historical failed Vercel deployments remain visible in the project history from initial root/dependency experiments; current production deployments are Ready.

## Tests and results

Last complete local/production gate on 2026-08-26:

```text
Ruff                                      PASS
strict mypy                               PASS (35 source files)
pytest                                    PASS (23 tests)
frontend ESLint + TypeScript              PASS
Vitest                                    PASS (8 tests)
frontend coverage                         74.76% statements / 77.41% lines /
                                          71.42% branches / 60% functions
Next production build                     PASS
Playwright local desktop + mobile         PASS (4/4)
Playwright production desktop + mobile    PASS (4/4)
benchmark generation + consistency        PASS
production network/console probe          PASS (GET 200, POST 201, no failures/messages)
```

GitHub Actions for `df15e79`:

- CI run `32933034217`: success
- Security run `32933034231`: success
- The evaluation workflow was green on the benchmark-changing revision `278d4ea` (`32932038817`); CI also runs benchmark consistency.

## Benchmark/evaluation status

Dataset: `evaluation/datasets/incident-retrieval-v2.json`; actual output: `evaluation/results/latest.json`; K=5.

| Pipeline | Recall@5 | Precision@5 | MRR | Evidence hit rate | Root-cause coverage | Abstention |
|---|---:|---:|---:|---:|---:|---:|
| Dense only | 0.6778 | 0.3200 | 0.4359 | 0.9333 | 0.6778 | N/A |
| Hybrid | 0.8167 | 0.3933 | 0.8306 | 1.0000 | 0.8167 | N/A |
| Full pipeline | 0.8389 | 0.4067 | 0.8500 | 1.0000 | 0.8389 | 1.0000 (2/2) |

The full pipeline genuinely invokes `InvestigationWorkflow`/LangGraph. Results are deterministic and reproducible; do not invent, manually improve, or generalize them beyond this synthetic corpus.

## Security status

PASS with documented residual risks. Working tree/Git history secret scan, pip audit, pnpm audit, prompt-injection/XSS/path-traversal/body/provider tests, CORS, CSP/security headers, error handling, and SSRF surface review were completed. There is no URL/archive ingestion. Residual medium risks are per-instance rate limiting and process-local state. Read `docs/reports/security-audit.md` and `docs/10-security-threat-model.md` before expanding input or authentication surfaces.

## Deployment/Vercel status

- Web stable alias: https://incidentlens-nine.vercel.app
- API stable alias: https://incidentlens-api-delta.vercel.app
- Verified frontend deployment for `df15e79`: `dpl_6jtcMp76ojm6ULUfJrmxW4Zw5vH7`
- Verified API deployment for `df15e79`: `dpl_CY9mg9KKnbag9nVNtq7KPyfTsCFb`
- Both are `Ready`, production target, Git-connected to `main`.
- Frontend project root is `frontend`; API project root is repository root using `api/index.py`.
- Production verified: homepage, full demo, click evidence, refresh, direct routes, evaluation, Under the Hood, architecture, about, custom 404, desktop/mobile, network/console, 200 health, 201 investigation, corrective trace, unsupported Low-confidence abstention, exact CORS, hostile-origin denial, and security headers.

## Important commands

```powershell
git status --short --branch
git log -5 --format='%h %an <%ae> %s'
python -m ruff check backend api
python -m mypy backend/app
python -m pytest backend/tests -q
pnpm --dir frontend lint
pnpm --dir frontend typecheck
pnpm --dir frontend test
pnpm --dir frontend build
python -m backend.app.evaluation.runner
python scripts/ci/verify_benchmark.py
python scripts/security/scan.py
python -m pip_audit -r requirements.txt
pnpm audit --audit-level high
pnpm e2e
$env:PLAYWRIGHT_BASE_URL='https://incidentlens-nine.vercel.app'; pnpm e2e
node scripts/ci/production_browser_probe.mjs
gh run list --limit 10
vercel ls incidentlens --yes
vercel ls incidentlens-api --yes
```

## Important files to inspect first

1. `README.md`
2. `docs/reports/recruiter-readiness-audit.md` (pre-change baseline, intentionally preserved)
3. `docs/reports/hostile-final-audit.md`
4. `docs/reports/system-test-report.md`
5. `docs/reports/security-audit.md`
6. `docs/reports/production-smoke-test.md`
7. `backend/app/agents/graph.py`
8. `backend/app/retrieval/engine.py`
9. `backend/app/ingestion/pipeline.py`
10. `backend/app/llm/openai_provider.py`
11. `frontend/components/investigation/workspace.tsx`
12. `evaluation/results/latest.json`

## Architectural decisions/ADRs

- ADR-001: monorepo.
- ADR-002: local in-memory vector store for reproducible demo; managed adapter later.
- ADR-003: dense + BM25 + RRF hybrid retrieval.
- ADR-004: LangGraph conditional corrective workflow.
- ADR-005: provider abstraction with deterministic default and real OpenAI/Gemini adapters.
- ADR-006: explicit weighted evidence graph.
- ADR-007: two Vercel projects, frontend rooted at `frontend`, API rooted at repository root.

## Assumptions and constraints

- This is a bounded portfolio demo, not a multi-tenant production incident platform.
- A real, honest deterministic provider is preferable to fake OpenAI theatrics or uncontrolled paid usage.
- Actual repository/deployment results override docs.
- Preserve existing architecture and meaningful history; do not rewrite/squash or redesign for aesthetics.
- All commits must remain solely under the user identity above.
- Do not weaken vector/provider/benchmark limitation language.
- Do not move benchmark answers into `demo/` or runtime code.

## Definition-of-Done status

All user-requested recruiter-readiness gates pass for the current bounded public demo: five-second clarity, simplified UI, deployed end-to-end demo, pipeline-derived answer, clickable evidence, real LangChain/LangGraph/RAG/vector execution, tested OpenAI provider, visible versioned prompts/providers, substantially expanded real benchmark, frontend/backend/E2E/build/security gates, production verification, recruiter-ready README/docs, pushed user-authored commits, and clean handoff.

The only remaining resume-presentation decision is repository visibility. A recruiter cannot inspect a private GitHub repository without access, so public visibility or explicit collaborator access must be decided by the user.

## Machine-readable checklist

```yaml
branch: main
remote: https://github.com/Niloy-Bhuiyan/IncidentLens.git
repository_visibility: private
functional_revision: df15e79
requirements_docs: complete
backend: complete
frontend: complete
langchain_runtime: verified
langgraph_runtime: verified
corrective_retrieval: verified
openai_contract: verified_mocked_no_paid_call
evaluation_queries: 32
evaluation_retrieval_queries: 30
evaluation_abstention_queries: 2
tests_local: pass
tests_production: pass
security_audit: pass_with_documented_risks
github_push: complete
vercel_deployment: ready
production_smoke: pass
definition_of_done: pass_for_bounded_portfolio_demo
optional_next: [approve_public_repo, live_provider_smoke, managed_vector_adapter, second_corpus]
```

## Anything a fresh agent must not redo or break

- Do not create a new repo/project or replace the architecture.
- Do not call the local vectors neural embeddings or claim pgvector is deployed.
- Do not imply the deterministic demo made a hosted LLM call.
- Do not spend OpenAI/Gemini credits without explicit authorization.
- Do not regenerate benchmark numbers unless code/data changed; if regenerated, commit real output and pass `verify_benchmark.py`.
- Do not overwrite the clean production screenshots with stitched full-page duplicates.
- Do not “fix” process-local state by silently adding an external service or credentials.
- Do not make the private GitHub repository public without user approval.
- Do not change Git identity or add AI/co-author metadata.

# NEXT SESSION START HERE

1. Run `git status --short --branch`, `git log -5 --format='%h %an <%ae> %s'`, and `git remote -v`; verify the tree is clean and the checkpoint-only commit is on `origin/main`.
2. Run `gh run list --limit 10` and confirm the workflows for current HEAD are green; docs-only commits may not trigger every path-filtered workflow.
3. Run `node scripts/ci/production_browser_probe.mjs`, then call `https://incidentlens-api-delta.vercel.app/api/v1/health` to verify stable aliases still point to Ready deployments.
4. Inspect `README.md`, the four reports listed above, `backend/app/agents/graph.py`, and `evaluation/results/latest.json` before changing claims.
5. If the user asks only whether to put it on a resume: recommend yes, but explain that the private repository must be made public or shared with reviewers before source inspection. Do not redo implementation, evaluation, screenshots, or deployment unless actual repository/production evidence has changed.
