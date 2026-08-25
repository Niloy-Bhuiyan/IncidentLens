# Security Threat Model

## Scope and trust boundaries

The browser, all questions, manifests, evidence, and provider output are untrusted. The FastAPI validator/middleware boundary protects the deterministic application/index. Provider secrets and system prompts remain server-side. v1 has public demo access but no authenticated personal data.

## Assets

Provider credentials, source/evidence confidentiality, report integrity, availability, Git history, server filesystem, and instruction hierarchy.

## Threats and controls

| Threat | Risk | Controls | Residual risk |
|---|---|---|---|
| Secret committed or bundled | High | `.env*` ignore with example exception, server-only env access, secret/history scans, no key-shaped fixtures | Local developer can still bypass process. |
| Path/archive traversal | High | API accepts a demo ID, not paths/uploads; manifest loader resolves and verifies every path under fixed root; no archives | Future upload feature needs new design. |
| Malformed/oversized content | Medium | extension allowlist, per-file/manifest/body limits, JSON schema validation, fail-closed parsing | Resource exhaustion remains possible under distributed load. |
| XSS/HTML injection | High | React text rendering, no `dangerouslySetInnerHTML`, CSP/security headers, tests with script-shaped evidence | Browser/plugin behavior outside app is out of scope. |
| CSRF/CORS | Medium | No cookie auth/stateful user mutations; exact-origin CORS; JSON content type | Public demo endpoint remains intentionally callable. |
| Injection | High | No SQL string interpolation, shell execution, code execution, or repository-content commands | Provider can still produce poor text; verifier limits citations. |
| SSRF/redirect abuse | High | Remote URL ingestion omitted | None in current feature set. |
| Prompt injection in evidence | High | Versioned prompts identify evidence as quoted untrusted data; no tools/actions/secrets exposed; citations must map to retrieved IDs; injection tests | A model may echo malicious text; UI labels it evidence. |
| API abuse/DoS | Medium | body/question limits, in-process token-bucket/IP rate limit, serverless platform controls, bounded top-k | In-memory limiter is per instance. |
| Sensitive logging | Medium | structured metadata-only logs; key/content redaction; safe errors | Platform request metadata remains subject to provider policy. |
| Dependency compromise | Medium | lockfiles, CI audit, Dependabot, minimal dependencies | Zero-day risk remains. |

## Security invariants

Evidence never selects tools, changes prompts, accesses environment variables, or executes. Citation IDs must belong to retrieved evidence. Client code never reads provider configuration except safe availability booleans. A failed provider call never silently becomes a labeled successful call.

## Verification

Unit/API tests cover traversal-shaped IDs, unsupported/malformed requests, size limits, prompt injection, error disclosure, CORS, and headers. Release scripts scan working files and Git history, run `pip-audit` and `pnpm audit`, and review unsafe HTML patterns.

