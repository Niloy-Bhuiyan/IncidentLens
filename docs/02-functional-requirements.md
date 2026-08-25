# Functional Requirements

| ID | Requirement | Verification |
|---|---|---|
| FR-001 | Launch the built-in checkout incident from the landing page. | E2E demo-launch test. |
| FR-002 | Parse source, JSON/text logs, Markdown/text docs, releases, commits, deployments, issues, and prior incidents. | Parser parameter tests. |
| FR-003 | Normalize all items to one evidence schema and deduplicate them. | Unit/integration tests. |
| FR-004 | Preserve type-specific file, symbol, timestamp, service, trace, error, commit, and document metadata. | Fixture assertions. |
| FR-005 | Search cosine similarity over real computed dense vectors. | Dense retrieval unit/evaluation tests. |
| FR-006 | Search a BM25 index. | BM25 ranking test. |
| FR-007 | Fuse dense and sparse rankings using reciprocal-rank fusion. | Exact-score unit test. |
| FR-008 | Rerank using query coverage, source authority, and graph adjacency. | Deterministic scoring test. |
| FR-009 | Link services, files, symbols, commits, deployments, signatures, issues, incidents, and events. | Graph expansion test. |
| FR-010 | Execute the investigation as a compiled LangGraph. | Runtime trace/integration test. |
| FR-011 | Grade sufficiency from evidence diversity, scores, and causal coverage. | Sufficient/insufficient tests. |
| FR-012 | Rewrite weak queries and run corrective retrieval. | Forced-correction transition test. |
| FR-013 | Return a cited root-cause report with confidence, contradictions, affected service, files, commits, and timeline. | Schema/API tests. |
| FR-014 | Render full evidence through a direct route. | Frontend/E2E test. |
| FR-015 | Display generated benchmark results. | Evaluation page test. |
| FR-016 | Explain runtime architecture and honest limitations. | Architecture page test. |

## Traceability

The API contract is in `08-api-design.md`, data relationships in `07-data-architecture.md`, controls in `10-security-threat-model.md`, and tests in `11-testing-strategy.md`. Acceptance criteria map to automated test names in the system-test report.

