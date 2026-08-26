# System Test Report

**Date:** 2026-08-26 (Asia/Dhaka)  
**Environment:** Windows 11; Python 3.13.5; Node 24.15.0; pnpm 11.19.0; Next.js 16.3.3; Chromium/Playwright 1.62.1  
**Revision tested:** `df15e79` plus release-evidence-only changes

## Scope

Validate the seeded flow from manifest parsing through LangChain chunking, dense/BM25 retrieval, reciprocal-rank fusion, evidence-graph expansion, compiled LangGraph orchestration, provider synthesis, citation verification, FastAPI, Next.js, and real browser interaction.

## Executed cases

| ID | Test | Evidence | Result |
|---|---|---|---|
| SYS-01 | Ingest every controlled evidence type | `test_ingests_every_supported_demo_type`; 10 sources, 11 chunks, 10 graph links | PASS |
| SYS-02 | Run dense, sparse, and fused ranking | Retrieval unit tests and the generated v2 benchmark | PASS |
| SYS-03 | Execute the compiled LangGraph normal path | Trace contains analyze, plan, retrieve, grade, expand, rerank, synthesize, verify, and report | PASS |
| SYS-04 | Execute corrective retrieval | Forced weak run contains grade → rewrite → retrieve-again with attempt 2 | PASS |
| SYS-05 | Produce a cited checkout hypothesis | Report identifies commit `a81d2c`, malformed `USD_US`, deployment, service, timeline, and five clickable claims | PASS |
| SYS-06 | Prove evidence changes the answer | Removing the key commit removes `a81d2c` from synthesis | PASS |
| SYS-07 | Abstain outside corpus scope | Unsupported authentication/database question returns unknown service, Low/0.25 confidence, and an insufficient-evidence limitation | PASS |
| SYS-08 | API success/error/security behavior | Health/demo/investigation/trace/evidence plus 422/404/503/413/415, CORS, IDs, and headers | PASS |
| SYS-09 | Frontend render, interaction, timeout, and retry | 8 Vitest/Testing Library tests | PASS |
| SYS-10 | Frontend coverage | 74.76% statements, 77.41% lines, 71.42% branches, 60% functions | PASS |
| SYS-11 | Production frontend compilation | `next build`; seven application routes plus custom not-found | PASS |
| SYS-12 | Local end-to-end journey and API-error recovery | Desktop Chromium and Pixel 7 projects | PASS (4/4) |
| SYS-13 | Production end-to-end journey and API-error recovery | Stable Vercel alias, desktop and Pixel 7 projects | PASS (4/4) |
| SYS-14 | Production console and network | Reusable Playwright probe; no failed requests or console warnings/errors | PASS |
| SYS-15 | Production direct routes and refresh | Investigation, evidence, evaluation, Under the Hood, architecture, about, and 404 | PASS |
| SYS-16 | Production responsive layout | 375px viewport; document width equals viewport and all five claims remain usable | PASS |

## Commands and results

```text
python -m ruff check backend api                PASS
python -m mypy backend/app                      PASS (35 source files)
python -m pytest backend/tests -q               PASS (23 tests)
pnpm --dir frontend lint                        PASS
pnpm --dir frontend typecheck                   PASS
pnpm --dir frontend test                        PASS (8 tests)
pnpm --dir frontend build                       PASS
pnpm e2e                                        PASS (4/4 local)
PLAYWRIGHT_BASE_URL=<production> pnpm e2e       PASS (4/4 production)
python -m backend.app.evaluation.runner         PASS
python scripts/ci/verify_benchmark.py           PASS
node scripts/ci/production_browser_probe.mjs    PASS
```

## Failures found and fixed

1. The original landing page led with AI architecture instead of the incident problem; the first viewport now explains the failure, investigation, output, and demo action.
2. The demo lacked bounded failure handling; requests now time out after 25 seconds and expose a safe retry state.
3. The deterministic provider overfit the checkout corpus and could answer unsupported scenarios; it now abstains, and the workflow assigns Low confidence.
4. The old four-query benchmark overstated evaluation strength; v2 uses 32 questions and executes the real full LangGraph pipeline.
5. Initial Vercel Git builds used the wrong backend root/dependency resolution; both projects are now Git-connected and deploy from the monorepo configuration.
6. Full-page browser capture duplicated stitched sections; release images were recaptured from actual production viewports.

## Status

All local, CI, browser, and production system gates pass for the tested deterministic public-demo configuration. Hosted OpenAI/Gemini quality was deliberately not exercised with paid credentials; their adapter contracts are mocked and covered separately.
