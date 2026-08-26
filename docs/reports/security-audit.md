# Security Audit

**Date:** 2026-08-26 (Asia/Dhaka)  
**Scope:** working tree, Git history, API boundaries, ingestion, rendering, prompts/providers, dependencies, headers/CORS, and deployed Vercel behavior

## Executed checks

| Check | Evidence | Result |
|---|---|---|
| Working-tree and Git-history secret scan | `python scripts/security/scan.py`; credentials, private keys, and token-shaped patterns | PASS |
| Python dependency audit | `python -m pip_audit -r requirements.txt` | PASS; no known vulnerabilities |
| JavaScript dependency audit | `pnpm audit --audit-level high` | PASS; no known vulnerabilities |
| Official OpenAI boundary | Server-only environment key, configurable model, 20-second timeout, two retries, structured Pydantic output, translated errors | PASS via mocked contract tests |
| Safe provider logging | Logs include provider/model/status metadata, never keys, prompts, or evidence text | PASS |
| XSS | No `dangerouslySetInnerHTML`; `<script>`-shaped evidence renders as text | PASS |
| File/path traversal | Literal demo ID only; resolved paths must remain under allowlisted root; unsupported suffixes rejected | PASS |
| Malformed/oversized input | JSONL, manifest, request body, content type, question, and file limits tested | PASS |
| SSRF/archive review | No URL or archive ingestion surface in v1 | NOT APPLICABLE |
| Command/code execution | Evidence is bounded UTF-8 text and is never executed or passed to a subprocess | PASS |
| Prompt injection | Sources are delimited as untrusted; injected citations cannot escape retrieved-ID allowlist | PASS |
| Production CORS | Stable frontend origin returns exact ACAO; an unlisted origin receives no ACAO | PASS |
| Production security headers | HSTS, CSP, no-sniff, frame, referrer, and permissions policies inspected | PASS |
| Error disclosure | Typed safe errors and request IDs; no server path or credential returned | PASS |

## Findings and disposition

| ID | Severity | Finding | Status |
|---|---|---|---|
| SEC-01 | Medium | Rate limiting is process-local, so it is not a global serverless abuse control. | Accepted for the bounded fixed demo; use platform firewall or shared store before arbitrary public ingestion. |
| SEC-02 | Medium | Investigation records are process-local and may disappear across serverless cold starts. | Accepted reliability limitation; UI can rebuild the deterministic demo. Durable authenticated storage remains roadmap work. |
| SEC-03 | Low | Development CSP permits `unsafe-eval` for Next.js development tooling. | Closed: production CSP omits it. |
| SEC-04 | Low | Public deterministic investigations consume CPU within each instance. | Accepted: bounded request size/top-k/corpus plus Vercel controls; no paid model is invoked. |
| SEC-05 | Informational | Real provider correctness was checked without live paid calls. | Explicitly documented; official SDK/provider contract is mocked. |

## Status

**PASS with documented residual risks.** No committed secret, known audited dependency vulnerability, exploitable URL-ingestion surface, client-side provider credential, or material release-blocking finding was found. This is a security review of the current bounded portfolio demo, not a claim of universal security.
