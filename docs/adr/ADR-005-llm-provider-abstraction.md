# ADR-005: LLM Provider Abstraction

## Context
The public demo cannot require paid calls, but operators need real provider integrations and honest failure behavior.

## Decision
Define one structured async provider protocol with deterministic mock, official OpenAI, and official Gemini implementations. Provider selection is server configuration/request constrained to an enum.

## Alternatives considered
Only one hosted provider creates lock-in/cost. Silent fallback is misleading. Putting provider logic in LangGraph nodes couples orchestration to SDKs.

## Why
The protocol supports testing, clear metadata, and replaceability while the evidence-driven mock preserves a functional demo.

## Trade-offs
Provider SDK updates require adapter maintenance, and mock prose is less flexible.

## Consequences
Missing credentials return explicit 503 responses. Prompts are versioned outside route code.

