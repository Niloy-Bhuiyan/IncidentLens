# Observability

## Backend signals

Request middleware emits one JSON completion record with timestamp, level, event, method, route template where available, status, duration, and request ID. Investigation logs add investigation ID. LangGraph nodes record start/end duration and safe counts/decisions. Retrieval records strategy, query hash (not full question), top-k, hit count, and duration. Provider logs include provider, model, result, duration, and usage totals—never keys or prompt/evidence bodies.

## Client signals

The UI exposes safe investigation progress/trace, descriptive errors with request IDs, and no third-party analytics in v1. Browser console and network failures are inspected during smoke tests.

## Correlation

Clients may supply a valid `X-Request-ID`; otherwise the API generates one. It echoes the ID in headers/errors and passes it into investigation service context. Evidence IDs and investigation IDs are opaque stable identifiers, not filesystem paths.

## Operational thresholds

The demo flags retrieval over 1 second locally, total deterministic investigation over 5 seconds in production, any 5xx, provider failure, or benchmark regression. No uptime/SLO claim is made for the portfolio deployment.

