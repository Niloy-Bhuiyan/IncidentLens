# Production Smoke Test

- **Status:** PASS
- **Date:** 2026-08-26 (Asia/Dhaka)
- **Frontend:** https://incidentlens-nine.vercel.app
- **API:** https://incidentlens-api-delta.vercel.app
- **Code revision:** `df15e79` plus release-evidence-only changes
- **Frontend deployment:** `dpl_6jtcMp76ojm6ULUfJrmxW4Zw5vH7`
- **API deployment:** `dpl_CY9mg9KKnbag9nVNtq7KPyfTsCFb`

## Verified behavior

| Area | Production observation | Result |
|---|---|---|
| First viewport | One H1: “Your app broke after a deployment. Find out why.”; problem, output, and demo action are immediately visible | PASS |
| Desktop demo | CTA completes, displays a concise root cause, High confidence, timeline, five claims, and evidence inspector | PASS |
| Mobile demo | Pixel-class 375px viewport; no horizontal overflow; report and all five claims remain usable | PASS |
| Evidence | Commit claim opens `a81d2c` and the actual diff; direct evidence route also renders | PASS |
| Progress/reliability | Real pipeline-stage labels display while waiting; API failure exposes safe retry; local and production error-path E2E pass | PASS |
| Refresh/direct navigation | Generated investigation survives refresh while its instance is warm; direct evaluation, evidence, architecture, Under the Hood, about, and 404 routes work | PASS |
| Evaluation | Page reports 32 total questions, 30 retrieval cases, 2 abstention cases, full recall 0.839, and 2/2 abstentions | PASS |
| Under the Hood | OpenAI/provider distinction, LangChain/LangGraph source proof, and honest local vector-store description render | PASS |
| Browser console | No errors or warnings during the full demo journey | PASS |
| Network | Demo GET 200 and investigation POST 201; reusable probe observed no response ≥400 | PASS |
| API health | `/api/v1/health` returns 200 and identifies production/mock configuration | PASS |
| Corrective workflow | Forced corrective investigation completes with 11 trace nodes including `retrieve_again` | PASS |
| Unsupported query | Absent authentication/database scenario abstains with unknown service and Low confidence | PASS |
| Validation | Invalid investigation request returns 422 | PASS |
| CORS | Frontend origin preflight 200 with exact ACAO; evil origin 400 with no ACAO | PASS |
| Headers | HSTS and `X-Content-Type-Options: nosniff` confirmed at API; CSP and browser security headers confirmed on web | PASS |
| Cold start | Health responded successfully after an idle/cold deployment; bounded frontend timeout remains the user-visible fallback | PASS |

## Automation

```powershell
$env:PLAYWRIGHT_BASE_URL = "https://incidentlens-nine.vercel.app"
pnpm e2e
node scripts/ci/production_browser_probe.mjs
```

The first command ran four Playwright tests across desktop Chromium and Pixel 7 profiles. The second records IncidentLens network responses and browser warnings/errors, executes the real CTA, and fails on any HTTP error or console problem.

## Deployment notes

Both Vercel projects are connected to `Niloy-Bhuiyan/IncidentLens` on `main`. The web project uses root `frontend`; the API project uses repository root and `api/index.py`. Stable aliases were tested instead of relying on preview-only deployment URLs. No client-side model secret is configured or exposed.
