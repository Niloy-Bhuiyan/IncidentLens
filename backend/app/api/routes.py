from __future__ import annotations

import json
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request, status

from backend.app.api.schemas import (
    EvidenceResponse,
    IngestionRequest,
    IngestionResponse,
    InvestigationRequest,
    InvestigationResponse,
    TraceResponse,
)
from backend.app.config import Settings, get_settings
from backend.app.llm import ProviderConfigurationError, ProviderExecutionError
from backend.app.services import InvestigationService

router = APIRouter(prefix="/api/v1")


def get_service(request: Request) -> InvestigationService:
    return request.app.state.investigation_service


ServiceDependency = Annotated[InvestigationService, Depends(get_service)]
SettingsDependency = Annotated[Settings, Depends(get_settings)]


@router.get("/health", tags=["system"])
async def health(settings: SettingsDependency) -> dict[str, Any]:
    return {
        "status": "ok",
        "service": "incidentlens-api",
        "version": "0.1.0",
        "environment": settings.environment,
        "default_provider": settings.llm_provider,
        "providers": {
            "mock": True,
            "openai": bool(settings.openai_api_key),
            "gemini": bool(settings.gemini_api_key),
        },
    }


@router.get("/demo", tags=["demo"])
async def get_demo(service: ServiceDependency) -> dict[str, object]:
    return await service.demo_summary()


@router.post("/ingestion", response_model=IngestionResponse, tags=["ingestion"])
async def ingest_demo(payload: IngestionRequest, service: ServiceDependency) -> IngestionResponse:
    result = await service.ensure_demo(rebuild=True)
    return IngestionResponse(
        namespace=payload.demo_id,
        source_count=len(result.evidence),
        chunk_count=len(result.chunks),
        duplicate_count=result.duplicate_count,
        relationship_count=len(result.manifest.relationships),
    )


@router.post(
    "/investigations",
    response_model=InvestigationResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["investigations"],
)
async def create_investigation(
    payload: InvestigationRequest, service: ServiceDependency
) -> InvestigationResponse:
    question = " ".join(payload.question.split())
    try:
        record = await service.investigate(question, payload.provider, payload.force_corrective)
    except ProviderConfigurationError as exc:
        raise HTTPException(
            status_code=503, detail={"code": "provider_not_configured", "message": str(exc)}
        ) from exc
    except ProviderExecutionError as exc:
        raise HTTPException(
            status_code=503, detail={"code": "provider_unavailable", "message": str(exc)}
        ) from exc
    return InvestigationResponse.model_validate(record.model_dump())


@router.get(
    "/investigations/{investigation_id}", response_model=InvestigationResponse, tags=["investigations"]
)
async def get_investigation(investigation_id: str, service: ServiceDependency) -> InvestigationResponse:
    record = service.get_investigation(investigation_id)
    if record is None:
        raise HTTPException(
            status_code=404, detail={"code": "investigation_not_found", "message": "Investigation not found"}
        )
    return InvestigationResponse.model_validate(record.model_dump())


@router.get("/investigations/{investigation_id}/trace", response_model=TraceResponse, tags=["investigations"])
async def get_trace(investigation_id: str, service: ServiceDependency) -> TraceResponse:
    record = service.get_investigation(investigation_id)
    if record is None:
        raise HTTPException(
            status_code=404, detail={"code": "investigation_not_found", "message": "Investigation not found"}
        )
    return TraceResponse(investigation_id=record.id, trace=record.trace)


@router.get("/evidence/{evidence_id}", response_model=EvidenceResponse, tags=["evidence"])
async def get_evidence(evidence_id: str, service: ServiceDependency) -> EvidenceResponse:
    if len(evidence_id) > 80 or not all(character.isalnum() or character == "-" for character in evidence_id):
        raise HTTPException(
            status_code=404, detail={"code": "evidence_not_found", "message": "Evidence not found"}
        )
    result = await service.get_evidence(evidence_id)
    if result is None:
        raise HTTPException(
            status_code=404, detail={"code": "evidence_not_found", "message": "Evidence not found"}
        )
    evidence, relations = result
    return EvidenceResponse(evidence=evidence, relations=relations)


@router.get("/evaluation/latest", tags=["evaluation"])
async def latest_evaluation(settings: SettingsDependency) -> dict[str, Any]:
    path = (settings.evaluation_root / "results" / "latest.json").resolve()
    if settings.evaluation_root.resolve() not in path.parents or not path.is_file():
        raise HTTPException(
            status_code=404,
            detail={"code": "evaluation_not_found", "message": "Evaluation has not been generated"},
        )
    return json.loads(path.read_text(encoding="utf-8"))
