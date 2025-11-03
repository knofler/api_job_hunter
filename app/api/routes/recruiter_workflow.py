from __future__ import annotations

import json
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

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


@router.post("/generate-stream")
async def generate_workflow_stream(payload: RecruiterWorkflowRequest) -> StreamingResponse:
    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            async for event in recruiter_workflow_service.generate_workflow_stream(payload):
                event_data = f"data: {json.dumps(event)}\n\n"
                print(f"[SSE] Sending event: {event.get('type')} - {event.get('step', '')}")  # Debug logging
                yield event_data
        except ProviderNotConfiguredError as exc:
            error_event = {"type": "error", "message": str(exc)}
            yield f"data: {json.dumps(error_event)}\n\n"
        except ValueError as exc:
            error_event = {"type": "error", "message": str(exc)}
            yield f"data: {json.dumps(error_event)}\n\n"
        except RuntimeError as exc:
            error_event = {"type": "error", "message": f"Workflow generation failed: {exc}"}
            yield f"data: {json.dumps(error_event)}\n\n"
        except Exception as exc:
            error_event = {"type": "error", "message": f"Unexpected error: {exc}"}
            yield f"data: {json.dumps(error_event)}\n\n"
        finally:
            yield "data: {\"type\": \"done\"}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
