# Release Checklist

## Requirements and implementation

- [x] PRD acceptance criteria and architecture match code.
- [x] Seed ingestion, dense/BM25/hybrid search, graph, LangGraph correction, providers, API, and UI work end to end.
- [x] Evidence mutation changes the result and unsupported questions abstain.
- [x] Every report claim cites retrievable evidence and every major evidence item is clickable.

## Quality and security

- [x] Backend unit, integration, API, provider, security, and evaluation suites pass (23 tests).
- [x] Ruff and strict mypy pass.
- [x] Frontend lint, typecheck, tests (8), coverage, and production build pass.
- [x] Playwright demo/error journeys pass locally and in production at desktop/mobile (4/4 each).
- [x] The 32-query benchmark is regenerated and README values match JSON.
- [x] Secret/history scans and Python/JavaScript dependency audits pass.
- [x] Prompt injection, XSS, path traversal, body limits, provider failures, headers, and CORS are tested.
- [x] Hostile audit is complete and residual risks are documented.

## Release

- [x] Screenshots are captured from the actual running production app.
- [x] Reports, README, limitations, `CONTEXT.md`, and stable deployment URLs are current.
- [x] Commits use `Niloy Bhuiyan <145592285+Niloy-Bhuiyan@users.noreply.github.com>` with no co-author metadata.
- [x] Private origin and `main` are pushed; CI/Security/Evaluation workflows pass.
- [x] Frontend and API production deployments work; direct routes, 404, health, demo, evidence, evaluation, console, network, headers, CORS, and responsive UI are checked.
- [x] Working tree is clean at handoff.
