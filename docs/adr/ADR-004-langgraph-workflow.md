# ADR-004: LangGraph Workflow

## Context
A single opaque handler cannot demonstrate evidence sufficiency, correction, verification, or inspectable transitions.

## Decision
Use a compiled LangGraph `StateGraph` with analyze, plan, retrieve, grade, rewrite/retrieve-again conditional path, expand, rerank, synthesize, verify, and build nodes.

## Alternatives considered
A manual function chain is simpler but fails the runtime LangGraph requirement and makes branching less observable. A multi-agent swarm is unnecessary and less deterministic.

## Why
Explicit typed state and conditional edges make behavior testable and auditable.

## Trade-offs
Graph state needs careful serialization and node-level tests; the workflow is synchronous from the client perspective in v1.

## Consequences
Every run returns a sanitized trace; tests exercise both branches and evidence changes must affect output.

