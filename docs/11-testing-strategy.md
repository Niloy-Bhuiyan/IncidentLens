# Testing Strategy

## Pyramid

1. **Unit:** parsers, normalization, cleaning, deduplication, chunk metadata, feature embeddings, cosine search, BM25, RRF, reranking, graph links, prompt loader, providers, validation, and utility functions.
2. **Integration:** manifest-to-index, all three retrieval modes, graph expansion, compiled LangGraph including correction, SQLite migrations/repository, and service/provider behavior.
3. **API:** success, invalid/malformed/oversized input, typed 404/503/429 responses, request IDs, CORS, headers, provider configuration, evidence/report/trace/evaluation contracts.
4. **Frontend:** page/component rendering, loading/error states, investigation interaction, evidence selection, timeline, keyboard semantics, and API-client behavior.
5. **E2E/system:** run real frontend/backend, launch demo, investigate, assert cited cause, open evidence/timeline/evaluation/architecture, and check 404/direct routes at desktop/mobile.
6. **Evaluation/security:** deterministic retrieval metrics, ground-truth separation, secret/dependency scans, injection/traversal/XSS/CORS/headers/limits, and hostile implementation audit.

## Environments

Local reference is Windows 11, Node 24/pnpm 11, Python 3.13, Chromium. CI uses pinned supported Node/Python and fresh installs. Production is Vercel Next.js and Python runtimes.

## Gates

All tests, Ruff, mypy, ESLint, TypeScript, production build, benchmark, secret scan, dependency audits, and Playwright must pass or be recorded as a release blocker. Flaky tests are failures; deterministic seeds and fixed demo timestamps avoid sleeps and remote models.

## Evidence mutation audit

A dedicated test removes the key commit/log evidence, rebuilds the index, and asserts the report/citations or confidence changes. This prevents a hidden hard-coded answer path.

