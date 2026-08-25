# System Test Report

**Date:** 2026-08-26 (Asia/Dhaka)  
**Environment:** Windows 11; Python 3.13.5; Node 24.15.0; pnpm 11.19.0; Next.js 16.3.3; Chromium/Playwright 1.62.1  
**Revision tested:** `9e50aad` plus pending release-documentation changes

## Scope

Validate the real seeded flow from manifest parsing through LangChain chunking, vector/BM25 retrieval, RRF, graph expansion, compiled LangGraph orchestration, evidence-driven provider synthesis, citation verification, FastAPI, Next.js rendering, and browser interaction.

## Executed cases

| ID | Test | Evidence | Result |
|---|---|---|---|
| SYS-01 | Ingest all controlled evidence types | `test_ingests_every_supported_demo_type`; 10 sources/11 chunks/10 graph links | PASS |
| SYS-02 | Run vector, sparse, and fused ranking | retrieval unit tests and generated benchmark | PASS |
| SYS-03 | Execute compiled LangGraph sufficient path | integration trace contains analyze/plan/retrieve/grade/expand/rerank/synthesize/verify/build | PASS |
| SYS-04 | Execute corrective retrieval | forced weak run contains grade → rewrite → retrieve-again with attempt 2 | PASS |
| SYS-05 | Produce cited checkout hypothesis | report identifies commit `a81d2c`, `USD_US`, contract violation, service, confidence, timeline | PASS |
| SYS-06 | Prevent hidden answer shortcut | removing the key commit removes `a81d2c` from synthesis | PASS |
| SYS-07 | API success/error/security behavior | TestClient covers health/demo/investigation/trace/evidence, 422/404/503/413/415, CORS, request ID, headers | PASS |
| SYS-08 | Frontend critical render/interaction | 5 Vitest/Testing Library tests; 70% statements and 72.5% lines | PASS |
| SYS-09 | Production frontend compilation | `next build`; all six page groups compiled | PASS |
| SYS-10 | Local end-to-end browser flow | Playwright desktop Chromium and Pixel 7 projects | PASS (2/2) |
| SYS-11 | Visual/accessibility-responsive inspection | In-app browser: 390×844 and desktop; no horizontal overflow; one H1; no unlabeled buttons | PASS |
| SYS-12 | Browser console | In-app browser error/warning log after demo run | PASS (empty) |

## Commands and results

```text
python -m ruff check backend api                PASS
python -m mypy backend/app                      PASS (35 files)
python -m pytest backend/tests -q               PASS (19 tests)
pnpm --dir frontend lint                        PASS
pnpm --dir frontend typecheck                   PASS
pnpm --dir frontend test                        PASS (5 tests)
pnpm --dir frontend build                       PASS
pnpm e2e                                        PASS (2 projects)
python -m backend.app.evaluation.runner         PASS
```

## Failures found and fixed

1. Trailing blank JSONL line was initially treated as malformed. Blank lines are now skipped while malformed nonblank rows fail closed.
2. Initial E2E browser calls were blocked by origin/CSP development boundaries. The suite now uses the allowed localhost origin and development-only `unsafe-eval`; production CSP remains stricter.
3. Deterministic synthesis copied an imperative commit subject into grammatically invalid prose. The provider now converts it into an explicit change phrase using retrieved commit text.
4. A generated TypeScript build-info file entered an intermediate commit. It is removed and ignored in the release cleanup.

## Final local status

All applicable local system gates pass. Production deployment/smoke evidence is recorded separately in `production-smoke-test.md` and remains a release blocker until executed.

