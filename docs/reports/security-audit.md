# Security Audit

**Date:** 2026-08-26 (Asia/Dhaka)  
**Scope:** working tree, Git history, API boundaries, ingestion, rendering, prompt boundary, dependencies, CORS/headers/rate/size controls, deployment configuration

## Executed checks

| Check | Evidence | Result |
|---|---|---|
| Working-tree secret scan | `python scripts/security/scan.py`; 148 files at time of run | PASS |
| Git-history secret scan | same scanner over `git log -p --all` | PASS |
| GitHub token/private-key/key-shaped credential patterns | same scanner | PASS |
| Python dependency audit | `python -m pip_audit -r requirements.txt` | PASS; local project itself skipped as non-PyPI |
| JavaScript dependency audit | `pnpm audit --audit-level high` | PASS; no known vulnerabilities |
| Unsafe React HTML | scanner plus component test; no `dangerouslySetInnerHTML` | PASS |
| XSS-shaped evidence | inspector renders `<script>` content as text; DOM contains no script element | PASS |
| File/path traversal | API accepts only literal demo ID; resolver rejects parent escape and unsupported suffix | PASS |
| Malformed/oversized input | JSONL, manifest, body, content-type, question, and file limits tested | PASS |
| SSRF/archive review | remote URLs and archive ingestion absent from v1 | NOT APPLICABLE |
| Arbitrary code execution/command injection | evidence is read as UTF-8 text; no evidence-controlled shell/subprocess path | PASS |
| Prompt injection | prompts mark sources untrusted; injection-shaped question cannot add a citation; citation allowlist verified | PASS |
| CORS | exact localhost origin allowed, unlisted origin denied; production origin pending deployment setting | PASS locally |
| Security headers | CSP, no-sniff, referrer, frame, permissions policies tested/inspected | PASS |
| CSRF | no cookie authentication or user-scoped state; JSON content type required | LOW/accepted |
| Rate limiting | per-process sliding one-minute window, safe 429 | PASS with residual limitation |
| Error disclosure | typed safe errors and request IDs; no local paths/provider credentials returned | PASS |

## Findings and remediation

| ID | Severity | Finding | Remediation/status |
|---|---|---|---|
| SEC-01 | Medium | In-memory rate limiter is per serverless instance and not a global abuse control. | Documented; platform firewall/global store required before public arbitrary ingestion. Accepted for fixed public demo. |
| SEC-02 | Medium | Investigation state is process-local, so IDs may expire across cold starts. This is reliability rather than confidentiality risk. | UI offers deterministic rebuild; durable authenticated storage is a roadmap item. |
| SEC-03 | Low | Development CSP permits `unsafe-eval` because React/Next development tooling requires it. | Conditional on `NODE_ENV=development`; production build omits it. Closed. |
| SEC-04 | Low | `pip-audit` cannot audit the local unpublished `incidentlens-backend` package name. | All declared third-party dependencies were audited; expected informational skip. Closed. |
| SEC-05 | Low | Public mock endpoint can consume CPU within per-instance limits. | Question/body/top-k bounds, local corpus size, per-instance limiter, and Vercel controls bound cost. Accepted. |

## Threat-model alignment

Secrets, XSS, injection, traversal, SSRF omission, prompt injection, abuse boundaries, logs, dependencies, and provider failure behavior match `docs/10-security-threat-model.md`. No claim of universal security is made. Production CORS/header/network verification must be repeated against deployed URLs.

## Status

Local security gate: **PASS with documented residual risks**. Production security configuration: **pending deployment verification**.

