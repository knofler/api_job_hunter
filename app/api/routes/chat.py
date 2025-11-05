from __future__ import annotations

import json
import os
from typing import AsyncGenerator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.models.chat_model import ChatRequest
from app.models.llm_model import LLMProviderConfig
from app.services import chat_service, llm_settings_service
from app.services.llm_orchestrator import LLMOrchestrator
from app.services.llm_providers.base import LLMMessage

router = APIRouter(prefix="/chat", tags=["chat"])


def load_system_prompt() -> str:
    """Load the system prompt from the prompts directory."""
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "..", "prompts", "recruiter_chat_system.md")
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        # Fallback to a basic prompt if file not found
        return (
            "You are a helpful recruiter assistant. "
            "You can help analyze candidates, refine workflow sections, and answer questions about the hiring process."
        )


@router.post("/stream")
async def chat_stream(payload: ChatRequest) -> StreamingResponse:
    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            # Get or create session
            session = await chat_service.get_or_create_session(payload.session_id)
            
            # Update context if provided
            if payload.job_id or payload.resume_ids or payload.workflow_context:
                await chat_service.update_context(
                    payload.session_id,
                    payload.job_id,
                    payload.resume_ids,
                    payload.workflow_context
                )
                session = await chat_service.get_or_create_session(payload.session_id)
            
            # Add user message
            await chat_service.add_message(payload.session_id, "user", payload.message)
            
            # Load system prompt
            base_system_prompt = load_system_prompt()
            
            # Build context-aware system prompt
            context_parts = []
            if session.job_id:
                context_parts.append(f"Job ID: {session.job_id}")
            if session.resume_ids:
                context_parts.append(f"Resume IDs: {', '.join(session.resume_ids)}")
            if session.workflow_context:
                context_parts.append(f"Workflow context available with {len(session.workflow_context)} sections")
            
            system_prompt = base_system_prompt
            if context_parts:
                system_prompt += f"\n\n## Current Context\n{' '.join(context_parts)}\n\nUse this context to provide relevant, specific assistance."
            
            # Build message history
            messages = [LLMMessage(role="system", content=system_prompt)]
            for msg in session.messages[-10:]:  # Last 10 messages for context
                messages.append(LLMMessage(role=msg.role, content=msg.content))
            
            # Get LLM config
            llm_settings = await llm_settings_service.get_settings()
            config = llm_settings.default
            
            # Stream response
            orchestrator = LLMOrchestrator()
            accumulated = ""
            
            async for chunk in orchestrator.generate_stream(messages, config):
                accumulated += chunk
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
            
            # Save assistant message
            await chat_service.add_message(payload.session_id, "assistant", accumulated)
            
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            
        except Exception as exc:
            error_event = {"type": "error", "message": f"Chat error: {exc}"}
            yield f"data: {json.dumps(error_event)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    session = await chat_service.get_or_create_session(session_id)
    return session.dict()
