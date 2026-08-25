.PHONY: install dev backend frontend test lint eval security

install:
	pnpm install
	python -m pip install -e "backend[dev]"

dev:
	pnpm exec concurrently "pnpm --dir frontend dev" "python -m uvicorn backend.app.main:app --reload --port 8000"

backend:
	python -m uvicorn backend.app.main:app --reload --port 8000

frontend:
	pnpm --dir frontend dev

test:
	python -m pytest backend/tests
	pnpm --dir frontend test

lint:
	python -m ruff check backend
	python -m mypy backend/app
	pnpm --dir frontend lint
	pnpm --dir frontend typecheck

eval:
	python -m backend.app.evaluation.runner

security:
	python scripts/security/scan.py
	python -m pip_audit
	pnpm audit --audit-level high

