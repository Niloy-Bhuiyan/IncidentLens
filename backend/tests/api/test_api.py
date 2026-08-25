from backend.app.main import app
from fastapi.testclient import TestClient


def test_health_demo_investigation_evidence_and_trace() -> None:
    with TestClient(app) as client:
        health = client.get("/api/v1/health")
        assert health.status_code == 200
        assert health.json()["providers"]["mock"] is True
        assert health.headers["x-content-type-options"] == "nosniff"
        assert health.headers["x-request-id"]

        demo = client.get("/api/v1/demo")
        assert demo.status_code == 200
        assert demo.json()["source_count"] == 10

        created = client.post(
            "/api/v1/investigations",
            json={"question": demo.json()["suggested_question"], "provider": "mock"},
        )
        assert created.status_code == 201
        payload = created.json()
        assert payload["report"]["supporting_evidence"]

        identifier = payload["id"]
        assert client.get(f"/api/v1/investigations/{identifier}").status_code == 200
        trace = client.get(f"/api/v1/investigations/{identifier}/trace")
        assert trace.status_code == 200
        assert any(step["node"] == "synthesize_root_cause" for step in trace.json()["trace"])

        evidence_id = payload["report"]["supporting_evidence"][0]["evidence_id"]
        evidence = client.get(f"/api/v1/evidence/{evidence_id}")
        assert evidence.status_code == 200
        assert evidence.json()["evidence"]["content"]


def test_typed_errors_and_provider_configuration() -> None:
    with TestClient(app) as client:
        invalid = client.post("/api/v1/investigations", json={"question": "x", "extra": True})
        assert invalid.status_code == 422
        assert invalid.json()["error"]["code"] == "validation_error"
        assert invalid.json()["error"]["request_id"]

        missing = client.get("/api/v1/evidence/..-secret")
        assert missing.status_code == 404
        assert missing.json()["error"]["code"] == "evidence_not_found"

        provider = client.post(
            "/api/v1/investigations",
            json={"question": "Why did checkout fail?", "provider": "openai"},
        )
        assert provider.status_code == 503
        assert provider.json()["error"]["code"] == "provider_not_configured"


def test_security_boundaries_and_cors() -> None:
    with TestClient(app) as client:
        wrong_content_type = client.post(
            "/api/v1/ingestion", content="{}", headers={"content-type": "text/plain"}
        )
        assert wrong_content_type.status_code == 415

        too_large = client.post(
            "/api/v1/investigations",
            content=b"x" * 20_000,
            headers={"content-type": "application/json"},
        )
        assert too_large.status_code == 413

        cors = client.options(
            "/api/v1/demo",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert cors.status_code == 200
        assert cors.headers["access-control-allow-origin"] == "http://localhost:3000"

        denied = client.options(
            "/api/v1/demo",
            headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "GET"},
        )
        assert "access-control-allow-origin" not in denied.headers
