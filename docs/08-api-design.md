# API Design

Base path: `/api/v1`. JSON responses include `X-Request-ID`; errors use `{error:{code,message,request_id,details?}}`. OpenAPI is available at `/docs` and `/openapi.json`.

| Method | Route | Purpose | Notable responses |
|---|---|---|---|
| GET | `/health` | Liveness/configuration status | 200 |
| GET | `/demo` | Demo metadata, suggested question, source counts | 200 |
| POST | `/ingestion` | Rebuild allowlisted demo namespace | 200, 400, 413, 422, 429 |
| POST | `/investigations` | Run a question through LangGraph | 201, 422, 429, 503 |
| GET | `/investigations/{id}` | Retrieve report and summary | 200, 404 |
| GET | `/investigations/{id}/trace` | Retrieve safe node transitions/timings | 200, 404 |
| GET | `/evidence/{id}` | Retrieve normalized evidence and relations | 200, 404 |
| GET | `/evaluation/latest` | Retrieve committed generated benchmark | 200, 404 |

## Contracts

Investigation requests contain `question` (3–500 characters), optional provider (`mock`, `openai`, `gemini`), and `force_corrective` for evaluation/testing only. Responses include ID, status, question, report, evidence summaries, timeline, and trace. The report schema includes `likely_root_cause`, `confidence`, `affected_service`, `supporting_evidence`, `contradictions`, `relevant_files`, `relevant_commits`, `timeline`, `limitations`, and provider metadata.

Ingestion accepts only `{demo_id:"checkout-incident"}` in v1. It never accepts a filesystem path or URL. This deliberately narrow contract prevents traversal/SSRF/archive issues while still exercising the real parser/index pipeline.

## Validation and compatibility

Pydantic rejects unknown fields. Request bodies are capped, questions are normalized but not interpreted as instructions, route IDs are constrained, and content types must be JSON. Breaking changes require a new API version.

