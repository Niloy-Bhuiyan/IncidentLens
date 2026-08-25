# IncidentLens Continuation Context

This file is maintained as a recovery checkpoint. The repository state and Git history are authoritative.

## Project goal

Build and deploy IncidentLens, an evidence-first incident investigator that ingests heterogeneous engineering evidence, executes real dense/sparse/hybrid retrieval and evidence-graph expansion through LangGraph, and returns cited conclusions through a calm Next.js investigation workspace.

## Current state

- Architecture: Next.js frontend and FastAPI backend in a monorepo; deterministic local feature-hash embeddings and BM25/RRF for default no-cost mode; provider and vector-store protocols allow replacement.
- Branch: `main`
- Remote: `https://github.com/Niloy-Bhuiyan/IncidentLens.git` (private)
- Git identity: `Niloy Bhuiyan <niloybhuiyann@gmail.com>`
- Technologies selected: Node 24, pnpm 11, Next.js 16, React 19, TypeScript 7, Python 3.13 locally/3.12+ supported, FastAPI, LangChain Core, LangGraph, pytest, Vitest, Playwright.
- Completed: repository initialized, private GitHub repository created, baseline configuration started.
- Partial: SDLC documentation and implementation.
- Unfinished: all implementation, tests, evaluation, UI verification, security audit, commits/push, Vercel deployment, production smoke test, release report.
- Bugs/errors: none yet; empty implementation.
- Tests: none run yet.
- Benchmark: not run.
- Security: secrets excluded by `.gitignore`; full audit pending.
- Deployment: not started.

## Setup

```powershell
pnpm install
python -m pip install -e "backend[dev]"
```

## Files to inspect first

1. `docs/01-prd.md`
2. `docs/06-system-architecture.md`
3. `backend/app/main.py`
4. `backend/app/agents/graph.py`
5. `frontend/app/page.tsx`
6. `evaluation/results/latest.json`

## Decisions and constraints

- Never execute ingested code or support remote URL ingestion in v1.
- The demo must not depend on a paid API or a frontend hard-coded answer.
- All evidence remains under `demo/checkout-incident` and benchmark truth under `evaluation`.
- Vercel deployment uses separately rooted frontend/backend projects unless Services proves reliable; see ADR-007.
- Do not commit `.env`, credentials, Vercel metadata, databases, or provider secrets.

## Machine-readable checklist

```yaml
requirements_docs: in_progress
backend: pending
frontend: pending
tests: pending
evaluation: pending
security_audit: pending
github_push: pending
vercel_deployment: pending
production_smoke: pending
definition_of_done: failing
```

## Definition-of-Done items still failing

All 40 master-specification items remain pending until explicitly verified.

## Recommended next steps

1. Complete the SDLC documents and ADRs so they match the selected architecture.
2. Add the seeded incident and implement ingestion/retrieval/graph/LangGraph/API.
3. Build the frontend and run local quality gates.
4. Generate the benchmark, audit security, and capture actual screenshots.
5. Push coherent commits, deploy both Vercel projects, smoke-test production, and update this file.

# NEXT SESSION START HERE

Run `git status --short --branch`, `git log -5 --oneline`, and `git remote -v`; compare them with this file. Inspect the six files listed above, then run the narrowest failing validation from the highest-priority unfinished step. Do not recreate the repository, GitHub remote, or Git identity. Never replace generated benchmark values or screenshots with invented artifacts.

