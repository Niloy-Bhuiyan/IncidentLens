# Release Checklist

## Requirements and implementation

- [ ] PRD acceptance criteria and architecture match code.
- [ ] Seed ingestion, vector/BM25/hybrid search, graph, LangGraph correction, providers, API, and UI work end to end.
- [ ] Evidence mutation changes the result.
- [ ] All important claims cite retrievable evidence.

## Quality and security

- [ ] Backend unit/integration/API/evaluation suites pass.
- [ ] Ruff and mypy pass.
- [ ] Frontend lint, typecheck, tests, and build pass.
- [ ] Playwright local and production smoke suites pass at desktop/mobile.
- [ ] Benchmark regenerated and README values match JSON.
- [ ] Secret/history scans and dependency audits pass or findings are resolved/documented.
- [ ] Threat-model controls and hostile audit are verified.

## Release

- [ ] Actual screenshots are captured from the running app.
- [ ] Reports, README, limitations, CONTEXT, and deployment URLs are current.
- [ ] Commits use `Niloy Bhuiyan <niloybhuiyann@gmail.com>` with no co-author metadata.
- [ ] Private origin is correct, branch pushed, CI passing, worktree clean.
- [ ] Backend and frontend production deployments work; direct routes, 404, health, demo, evidence, evaluation, console, network, and responsive UI checked.

