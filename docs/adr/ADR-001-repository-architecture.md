# ADR-001: Repository Architecture

## Context
The product combines a TypeScript web UI, Python investigation runtime, fixtures, evaluation, tests, and SDLC artifacts.

## Decision
Use one pnpm-rooted monorepo with `frontend/`, `backend/`, `demo/`, `evaluation/`, `docs/`, `scripts/`, and `tests/e2e/` boundaries.

## Alternatives considered
Separate repositories complicate synchronized releases and evidence; a single Next.js application cannot satisfy the FastAPI/Python runtime requirement cleanly; a heavy workspace framework adds little at this scale.

## Why
One repository provides atomic changes and traceability while preserving runtime ownership.

## Trade-offs
Two language toolchains and two deployment projects require explicit commands and CI jobs.

## Consequences
Frontend never owns reasoning/secrets; backend never owns presentation; demo truth and benchmark truth remain separate from application code.

