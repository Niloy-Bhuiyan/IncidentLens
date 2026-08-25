# Use Cases

## UC-01: Investigate the seeded checkout failure

**Actor:** Recruiter or engineer. **Precondition:** Application is available. **Flow:** Open landing page, launch demo, submit the suggested question, inspect root-cause report, timeline, trace, and cited evidence. **Alternate flow:** API error is shown with retry guidance. **Postcondition:** No external system is modified.

## UC-02: Inspect evidence provenance

From a claim, open a cited evidence item. The application requests `/api/v1/evidence/{id}` and renders type, source, metadata, content, and relationships as escaped text. Unknown IDs produce a useful 404.

## UC-03: Correct an underspecified query

The workflow analyzes a vague question, retrieves an insufficient set, records the failed grade, rewrites/decomposes the query using incident context, retrieves again, expands graph neighbors, and continues. The trace makes both passes visible.

## UC-04: Reproduce evaluation

A developer runs the evaluation command. The same committed dataset and ground truth produce a timestamped/latest JSON result with dense, hybrid, and full-pipeline metrics. The UI reads this artifact through the API.

## UC-05: Select an external model provider

An operator sets an environment provider and key. The backend calls only that provider with timeouts/retries/structured expectations. Missing credentials or provider failure return safe typed errors and do not impersonate a successful result. The public demo stays on deterministic mock mode.

## UC-06: Reject unsafe ingestion

A client submits an unsupported extension, path traversal, malformed content, or over-limit item. Validation rejects the whole request before reading or indexing it, emits a request ID, and reveals no filesystem paths.

