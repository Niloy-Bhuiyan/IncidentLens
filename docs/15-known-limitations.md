# Known Limitations

- The bundled feature-hash embedding is deterministic and deployable but less semantically capable than a modern neural embedding model, especially for paraphrases absent from normalization rules.
- Benchmark data is synthetic and small; metrics demonstrate repeatability and behavior on the seeded incident, not general incident-resolution accuracy.
- The evidence graph is derived from explicit metadata/manifest relationships rather than learned entity resolution.
- Public mock mode produces an evidence-driven structured hypothesis without generative prose variation. OpenAI/Gemini modes require operator keys and are not part of the no-cost public guarantee.
- Serverless demo indexes and investigation memory are process-local. Cold starts rebuild the corpus; arbitrary ingestion and durable multi-user history are out of scope.
- v1 accepts only the built-in demo ID. It intentionally omits uploads, archives, remote URLs, GitHub connectors, authentication, authorization, remediation, and production-system actions.
- Rate limiting is per process/instance and supplements rather than replaces platform protection.
- A cited hypothesis can still be incomplete or wrong; IncidentLens exposes uncertainty and does not guarantee root cause.

