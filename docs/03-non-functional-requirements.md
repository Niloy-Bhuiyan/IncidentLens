# Non-Functional Requirements

## Reliability

- Default mock mode is deterministic for identical corpus and question.
- The demo is rebuilt from immutable checked-in evidence after a serverless cold start.
- Provider failures use typed errors and never silently fall back while claiming provider success.
- Partial/malformed input is rejected before indexing.

## Performance targets

- Warm demo retrieval and orchestration: under 1 second locally on the reference machine.
- Production investigation response: under 5 seconds at p95 for the seeded corpus, excluding a remote LLM call.
- Landing-page Largest Contentful Paint target: under 2.5 seconds on a typical broadband mobile profile.
- No evidence item is embedded more than once per process/namespace build.
- Full deterministic benchmark: under 30 seconds locally.

These are targets until the system and production reports record measurements.

## Security and privacy

Only allowlisted local demo paths and controlled JSON payloads are accepted. Code is never executed. Content is rendered as text. CORS is explicit, security headers apply globally, request/file limits are enforced, and logs exclude content and secrets.

## Maintainability

Typed Pydantic/TypeScript boundaries, vector/provider protocols, single-purpose pipeline stages, versioned prompts, and small deterministic fixtures keep the system replaceable and testable. SQLite provides local relational persistence; the vector interface can be backed by pgvector without changing orchestration.

## Observability

JSON logs contain request ID, investigation ID when available, stage, duration, status, and safe error type. The API exposes a sanitized node trace. It never logs provider keys or evidence bodies.

## Accessibility and responsive behavior

Semantic landmarks, heading order, labels, keyboard-accessible controls, visible focus rings, `aria-live` loading state, non-color status text, and contrast meeting WCAG AA are required. Layouts support 390 px mobile, laptop, and wide desktop without horizontal page scrolling.

