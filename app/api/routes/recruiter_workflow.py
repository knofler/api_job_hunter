from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models.recruiter_workflow import RecruiterWorkflowRequest, RecruiterWorkflowResponse
from app.services import recruiter_workflow_service
from app.services.llm_providers.base import ProviderNotConfiguredError

router = APIRouter(prefix="/recruiter-workflow", tags=["recruiter-workflow"])


@router.post("/generate", response_model=RecruiterWorkflowResponse)
async def generate_workflow(payload: RecruiterWorkflowRequest) -> RecruiterWorkflowResponse:
    try:
        return await recruiter_workflow_service.generate_workflow(payload)
    except ProviderNotConfiguredError as exc:  # type: ignore[misc]
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=f"Recruiter workflow generation failed: {exc}") from exc
