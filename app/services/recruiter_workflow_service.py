from __future__ import annotations

import asyncio
import json
import logging
from typing import AsyncGenerator, Dict, Iterable, List, Optional

from app.models.llm_model import LLMProviderConfig, LLMWorkflowSettings
from app.models.recruiter_workflow import (
    CandidateAnalysis,
    CandidateReadout,
    CoreSkill,
    InsightItem,
    InterviewQuestion,
    JobMetadata,
    RankedCandidateItem,
    RecruiterWorkflowRequest,
    RecruiterWorkflowResponse,
    ResumeReference,
    SkillAlignment,
)
from app.services import candidate_service, resume_service
from app.services.llm_orchestrator import LLMOrchestrator
from app.services.llm_providers.base import LLMMessage
from app.services.prompt_service import get_prompt_by_name
from app.services import llm_settings_service

_SYSTEM_PROMPT = (
    "You are an impartial AI recruiting copilot. You analyse job descriptions and candidate resumes to help recruiters "
    "decide who should advance. Always ground recommendations in the supplied evidence, avoid inventing facts, and "
    "respond with clean JSON only."
)

logger = logging.getLogger(__name__)


_STEP_ORDER = [
    "core_skills",
    "ai_analysis",
    "ranked_shortlist",
    "detailed_readout",
    "engagement_plan",
    "fairness_guidance",
    "interview_preparation",
]


async def generate_workflow(payload: RecruiterWorkflowRequest) -> RecruiterWorkflowResponse:
    if not payload.job_description.strip():
        raise ValueError("job_description is required")
    if not payload.resumes:
        raise ValueError("At least one resume must be provided")

    orchestrator = LLMOrchestrator()
    workflow_settings = await llm_settings_service.get_settings()

    resume_contexts = await _load_resume_context(payload.resumes)
    context_json = _render_context(payload.job_metadata, payload.job_description, resume_contexts)

    step_configs = _resolve_step_configs(payload, workflow_settings)

    core_result = await _invoke_core_skills(orchestrator, step_configs["core_skills"], context_json)
    analysis_result = await _invoke_ai_analysis(orchestrator, step_configs["ai_analysis"], context_json)
    shortlist_result = await _invoke_ranked_shortlist(orchestrator, step_configs["ranked_shortlist"], context_json)
    readout_result = await _invoke_detailed_readout(orchestrator, step_configs["detailed_readout"], context_json)
    engagement_result = await _invoke_engagement_plan(orchestrator, step_configs["engagement_plan"], context_json)
    fairness_result = await _invoke_fairness_guidance(orchestrator, step_configs["fairness_guidance"], context_json)
    interview_result = await _invoke_interview_pack(orchestrator, step_configs["interview_preparation"], context_json)

    return RecruiterWorkflowResponse(
        job=payload.job_metadata,
        core_skills=core_result,
        ai_analysis_markdown=analysis_result["markdown"],
        candidate_analysis=analysis_result["candidates"],
        ranked_shortlist=shortlist_result,
        detailed_readout=readout_result,
        engagement_plan=engagement_result,
        fairness_guidance=fairness_result,
        interview_preparation=interview_result,
    )


async def generate_workflow_stream(payload: RecruiterWorkflowRequest) -> AsyncGenerator[Dict, None]:
    """Generate workflow with streaming updates for each step."""
    if not payload.job_description.strip():
        raise ValueError("job_description is required")
    if not payload.resumes:
        raise ValueError("At least one resume must be provided")

    orchestrator = LLMOrchestrator()
    workflow_settings = await llm_settings_service.get_settings()

    yield {"type": "status", "step": "loading", "message": "Loading resume contexts..."}
    resume_contexts = await _load_resume_context(payload.resumes)
    context_json = _render_context(payload.job_metadata, payload.job_description, resume_contexts)
    step_configs = _resolve_step_configs(payload, workflow_settings)

    # Step 1: Core Skills
    yield {"type": "status", "step": "core_skills", "message": "Analyzing core must-have skills..."}
    await asyncio.sleep(0.5)  # Small delay for visual feedback
    core_result = await _invoke_core_skills(orchestrator, step_configs["core_skills"], context_json)
    yield {"type": "result", "step": "core_skills", "data": [skill.dict() for skill in core_result]}
    await asyncio.sleep(0.3)

    # Step 2: AI Analysis (with true streaming for markdown)
    yield {"type": "status", "step": "ai_analysis", "message": "Running AI-powered analysis..."}
    
    # First, stream the markdown analysis
    markdown_instruction = (
        "Craft a recruiter-facing markdown summary analyzing the candidates against the job requirements. "
        "Include sections with headers (##), key insights, strengths, concerns, and recommendations. "
        "Make it informative and actionable for a recruiter. Return ONLY markdown text, no JSON."
    )
    markdown_messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": f"{markdown_instruction}\n\nContext:\n{context_json}"},
    ]
    markdown_llm_messages = [LLMMessage(role=msg["role"], content=msg["content"]) for msg in markdown_messages]
    
    # Collect streamed markdown chunks
    accumulated_text = ""
    async for chunk in orchestrator.generate_stream(markdown_llm_messages, step_configs["ai_analysis"]):
        accumulated_text += chunk
        yield {
            "type": "partial",
            "step": "ai_analysis",
            "data": {
                "markdown": accumulated_text,
            },
        }
    
    # If the LLM returned JSON instead of markdown, try to extract the markdown
    if accumulated_text.strip().startswith('{'):
        try:
            parsed = json.loads(accumulated_text)
            if 'markdown' in parsed:
                accumulated_text = parsed['markdown']
            elif 'ai_analysis_markdown' in parsed:
                accumulated_text = parsed['ai_analysis_markdown']
        except json.JSONDecodeError:
            pass  # Keep as is
    
    # Then get structured candidate analysis
    # Initialize with fallback structure
    analysis_result = {
        "markdown": accumulated_text,
        "candidates": [],
    }
    try:
        analysis_result = await _invoke_ai_analysis(orchestrator, step_configs["ai_analysis"], context_json)
        yield {
            "type": "result",
            "step": "ai_analysis",
            "data": {
                "markdown": accumulated_text,  # Use the streamed markdown
                "candidates": [c.dict() for c in analysis_result["candidates"]],
            },
        }
    except Exception as e:
        logger.error(f"Failed to parse AI analysis result: {e}")
        # Fall back to accumulated text as markdown
        yield {
            "type": "result",
            "step": "ai_analysis",
            "data": {
                "markdown": accumulated_text,
                "candidates": [],
            },
        }
    await asyncio.sleep(0.3)

    # Step 3: Ranked Shortlist
    yield {"type": "status", "step": "ranked_shortlist", "message": "Creating ranked shortlist..."}
    await asyncio.sleep(0.5)
    shortlist_result = await _invoke_ranked_shortlist(orchestrator, step_configs["ranked_shortlist"], context_json)
    yield {"type": "result", "step": "ranked_shortlist", "data": [item.dict() for item in shortlist_result]}
    await asyncio.sleep(0.3)

    # Step 4: Detailed Readout
    yield {"type": "status", "step": "detailed_readout", "message": "Generating detailed candidate readouts..."}
    await asyncio.sleep(0.5)
    readout_result = await _invoke_detailed_readout(orchestrator, step_configs["detailed_readout"], context_json)
    yield {"type": "result", "step": "detailed_readout", "data": [item.dict() for item in readout_result]}
    await asyncio.sleep(0.3)

    # Step 5: Engagement Plan (stream items one by one)
    yield {"type": "status", "step": "engagement_plan", "message": "Creating engagement plan..."}
    await asyncio.sleep(0.5)
    engagement_result = await _invoke_engagement_plan(orchestrator, step_configs["engagement_plan"], context_json)
    accumulated_engagement = []
    for item in engagement_result:
        accumulated_engagement.append(item.dict())
        yield {"type": "partial", "step": "engagement_plan", "data": accumulated_engagement}
        await asyncio.sleep(0.2)  # Small delay between items for visual effect
    yield {"type": "result", "step": "engagement_plan", "data": [item.dict() for item in engagement_result]}
    await asyncio.sleep(0.3)

    # Step 6: Fairness Guidance (stream items one by one)
    yield {"type": "status", "step": "fairness_guidance", "message": "Generating fairness & panel guidance..."}
    await asyncio.sleep(0.5)
    fairness_result = await _invoke_fairness_guidance(orchestrator, step_configs["fairness_guidance"], context_json)
    accumulated_fairness = []
    for item in fairness_result:
        accumulated_fairness.append(item.dict())
        yield {"type": "partial", "step": "fairness_guidance", "data": accumulated_fairness}
        await asyncio.sleep(0.2)  # Small delay between items for visual effect
    yield {"type": "result", "step": "fairness_guidance", "data": [item.dict() for item in fairness_result]}
    await asyncio.sleep(0.3)

    # Step 7: Interview Preparation (stream items one by one)
    yield {"type": "status", "step": "interview_preparation", "message": "Preparing interview pack..."}
    await asyncio.sleep(0.5)
    interview_result = await _invoke_interview_pack(orchestrator, step_configs["interview_preparation"], context_json)
    accumulated_interview = []
    for item in interview_result:
        accumulated_interview.append(item.dict())
        yield {"type": "partial", "step": "interview_preparation", "data": accumulated_interview}
        await asyncio.sleep(0.2)  # Small delay between items for visual effect
    yield {"type": "result", "step": "interview_preparation", "data": [item.dict() for item in interview_result]}
    await asyncio.sleep(0.3)

    # Final complete event
    yield {
        "type": "complete",
        "data": {
            "job": payload.job_metadata.dict() if payload.job_metadata else {},
            "core_skills": [skill.dict() for skill in core_result],
            "ai_analysis_markdown": analysis_result["markdown"],
            "candidate_analysis": [c.dict() for c in analysis_result["candidates"]],
            "ranked_shortlist": [item.dict() for item in shortlist_result],
            "detailed_readout": [item.dict() for item in readout_result],
            "engagement_plan": [item.dict() for item in engagement_result],
            "fairness_guidance": [item.dict() for item in fairness_result],
            "interview_preparation": [item.dict() for item in interview_result],
        },
    }


async def _load_resume_context(resume_refs: Iterable[ResumeReference]) -> List[Dict[str, Optional[str]]]:
    contexts: List[Dict[str, Optional[str]]] = []
    candidate_ids: set[str] = set()
    resume_payloads = []

    for reference in resume_refs:
        resume = await resume_service.get_resume(reference.resume_id)
        if not resume:
            raise ValueError(f"Resume {reference.resume_id} not found")
        candidate_id = reference.candidate_id or resume.get("candidate_id")
        if candidate_id:
            candidate_ids.add(candidate_id)
        resume_payloads.append((resume, candidate_id))

    candidate_profiles: Dict[str, Dict[str, Optional[str]]] = {}
    for candidate_id in candidate_ids:
        profile = await candidate_service.get_candidate_profile(candidate_id)
        if profile:
            candidate_profiles[candidate_id] = profile

    for resume, candidate_id in resume_payloads:
        candidate_profile = candidate_profiles.get(candidate_id or "")
        contexts.append(
            {
                "candidate_id": candidate_id,
                "candidate_name": (candidate_profile or {}).get("name") or resume.get("name"),
                "candidate_primary_role": (candidate_profile or {}).get("primary_role"),
                "experience_years": (candidate_profile or {}).get("experience_years"),
                "resume_id": resume.get("id"),
                "resume_name": resume.get("name"),
                "resume_type": resume.get("type"),
                "resume_summary": resume.get("summary"),
                "resume_preview": resume.get("preview"),
                "resume_skills": resume.get("skills", []),
                "candidate_skills": (candidate_profile or {}).get("skills", []),
                "resume_updated_at": resume.get("last_updated"),
                "candidate_preferences": {
                    "locations": (candidate_profile or {}).get("preferred_locations", []),
                    "candidate_type": (candidate_profile or {}).get("candidate_type"),
                },
            }
        )
    return contexts


def _render_context(job_metadata: JobMetadata, job_description: str, resume_contexts: List[Dict[str, Optional[str]]]) -> str:
    payload = {
        "job": {
            "title": job_metadata.title,
            "code": job_metadata.code,
            "level": job_metadata.level,
            "salary_band": job_metadata.salary_band,
            "summary": job_metadata.summary,
            "description": job_description,
        },
        "candidates": resume_contexts,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def _resolve_step_configs(
    payload: RecruiterWorkflowRequest,
    workflow_settings: LLMWorkflowSettings,
) -> Dict[str, LLMProviderConfig]:
    configs: Dict[str, LLMProviderConfig] = {}
    for step in _STEP_ORDER:
        override = payload.step_overrides.get(step)
        if override:
            configs[step] = override
            continue
        step_config = workflow_settings.steps.get(step) if step in workflow_settings.steps else None
        configs[step] = step_config or workflow_settings.default
    return configs


async def _get_prompt_content(prompt_name: str, fallback_content: str) -> str:
    """Get prompt content from database, fallback to provided content if not found."""
    try:
        prompt = await get_prompt_by_name(prompt_name)
        if prompt and prompt.get("content"):
            return prompt["content"]
    except Exception as e:
        logger.warning(f"Failed to load prompt '{prompt_name}': {e}")
    return fallback_content


async def _invoke_core_skills(
    orchestrator: LLMOrchestrator,
    config: LLMProviderConfig,
    context_json: str,
) -> List[CoreSkill]:
    instruction = await _get_prompt_content(
        "core_skills_analysis",
        "Identify the three most critical must-have skills that determine candidate success. "
        "Return JSON with key 'core_skills' containing exactly three objects with fields 'name' and 'reason'."
    )
    data = await _invoke_json(orchestrator, config, instruction, context_json)
    core_skills = data.get("core_skills", [])
    return [CoreSkill(name=item.get("name", ""), reason=item.get("reason", "")) for item in core_skills]
    instruction = (
        "Identify the three most critical must-have skills that determine candidate success."
        " Return JSON with key 'core_skills' containing exactly three objects with fields 'name' and 'reason'."
    )
    data = await _invoke_json(orchestrator, config, instruction, context_json)
    core_skills = data.get("core_skills", [])
    return [CoreSkill(name=item.get("name", ""), reason=item.get("reason", "")) for item in core_skills]


async def _invoke_ai_analysis(
    orchestrator: LLMOrchestrator,
    config: LLMProviderConfig,
    context_json: str,
) -> Dict[str, object]:
    instruction = await _get_prompt_content(
        "candidate_analysis",
        "For each candidate, score the fit versus the job. Provide match_score (0-100), bias_free_score (0-100), "
        "a recruiter summary (<= 400 characters), up to three highlights, and a skill_alignment array with fields "
        "'skill', 'status' (Yes/Partial/No), and 'evidence'. Also craft a recruiter-facing markdown summary and "
        "return it as 'ai_analysis_markdown'. Respond with JSON containing keys 'ai_analysis_markdown' and "
        "'candidate_analysis'."
    )
    data = await _invoke_json(orchestrator, config, instruction, context_json)
    markdown = data.get("ai_analysis_markdown", "")
    candidates_payload = data.get("candidate_analysis", [])
    if isinstance(candidates_payload, str):
        # Some LLM responses double-encode JSON arrays; attempt to decode before proceeding.
        try:
            candidates_payload = json.loads(candidates_payload)
        except json.JSONDecodeError as exc:  # noqa: PERF203
            raise RuntimeError("LLM response returned string for candidate_analysis; expected JSON array") from exc
    if not isinstance(candidates_payload, list):
        logger.warning("LLM candidate_analysis payload malformed: %r", candidates_payload)
        raise RuntimeError("LLM response returned invalid candidate_analysis payload; expected list of objects")
    candidates: List[CandidateAnalysis] = []
    for item in candidates_payload:
        if isinstance(item, str):
            try:
                item = json.loads(item)
            except json.JSONDecodeError as exc:  # noqa: PERF203
                raise RuntimeError("LLM returned string item in candidate_analysis; expected JSON object") from exc
        if not isinstance(item, dict):
            logger.warning("LLM candidate_analysis entry malformed: %r", item)
            raise RuntimeError("LLM returned malformed candidate_analysis entry; expected JSON object")
        skill_alignment = [
            SkillAlignment(
                skill=alignment.get("skill", ""),
                status=alignment.get("status", ""),
                evidence=alignment.get("evidence", ""),
            )
            for alignment in (item.get("skill_alignment", []) if isinstance(item.get("skill_alignment", []), list) else [])
        ]
        candidates.append(
            CandidateAnalysis(
                candidate_id=item.get("candidate_id", ""),
                name=item.get("name"),
                match_score=item.get("match_score"),
                bias_free_score=item.get("bias_free_score"),
                summary=item.get("summary"),
                highlights=item.get("highlights", []),
                skill_alignment=skill_alignment,
            )
        )
    return {"markdown": markdown, "candidates": candidates}


async def _invoke_ranked_shortlist(
    orchestrator: LLMOrchestrator,
    config: LLMProviderConfig,
    context_json: str,
) -> List[RankedCandidateItem]:
    instruction = await _get_prompt_content(
        "ranked_shortlist",
        "Generate a ranked shortlist of candidates. "
        "Return JSON with key 'ranked_shortlist' where each item includes 'candidate_id', 'rank' (1-based), "
        "'priority' (Hot/Warm/Pipeline), 'status', 'availability', and 'notes'."
    )
    data = await _invoke_json(orchestrator, config, instruction, context_json)
    shortlist_payload = data.get("ranked_shortlist", [])
    shortlist: List[RankedCandidateItem] = []
    for item in shortlist_payload:
        shortlist.append(
            RankedCandidateItem(
                candidate_id=item.get("candidate_id", ""),
                rank=item.get("rank", 0),
                priority=item.get("priority"),
                status=item.get("status"),
                availability=item.get("availability"),
                notes=item.get("notes"),
            )
        )
    shortlist.sort(key=lambda entry: entry.rank or 0)
    return shortlist


async def _invoke_detailed_readout(
    orchestrator: LLMOrchestrator,
    config: LLMProviderConfig,
    context_json: str,
) -> List[CandidateReadout]:
    instruction = await _get_prompt_content(
        "detailed_readout",
        "Create a detailed readout for each candidate. "
        "Return JSON with key 'detailed_readout' of objects that include 'candidate_id', "
        "'strengths' (list of strings), 'risks' (list of strings), and 'recommended_actions' (list of strings)."
    )
    data = await _invoke_json(orchestrator, config, instruction, context_json)
    readout_payload = data.get("detailed_readout", [])
    readout: List[CandidateReadout] = []
    for item in readout_payload:
        readout.append(
            CandidateReadout(
                candidate_id=item.get("candidate_id", ""),
                strengths=item.get("strengths", []),
                risks=item.get("risks", []),
                recommended_actions=item.get("recommended_actions", []),
            )
        )
    return readout


async def _invoke_engagement_plan(
    orchestrator: LLMOrchestrator,
    config: LLMProviderConfig,
    context_json: str,
) -> List[InsightItem]:
    instruction = await _get_prompt_content(
        "engagement_plan",
        "Propose an engagement plan for stakeholders. "
        "Return JSON with key 'engagement_plan' where every item has 'label', 'value', and optional 'helper'."
    )
    data = await _invoke_json(orchestrator, config, instruction, context_json)
    plan_payload = data.get("engagement_plan", [])
    return [
        InsightItem(
            label=item.get("label", ""),
            value=item.get("value", ""),
            helper=item.get("helper"),
        )
        for item in plan_payload
    ]


async def _invoke_fairness_guidance(
    orchestrator: LLMOrchestrator,
    config: LLMProviderConfig,
    context_json: str,
) -> List[InsightItem]:
    instruction = await _get_prompt_content(
        "fairness_guidance",
        "Highlight fairness, bias mitigation, and panel guidance actions. "
        "Return JSON with key 'fairness_guidance' where each item includes 'label', 'value', and optional 'helper'."
    )
    data = await _invoke_json(orchestrator, config, instruction, context_json)
    fairness_payload = data.get("fairness_guidance", [])
    return [
        InsightItem(
            label=item.get("label", ""),
            value=item.get("value", ""),
            helper=item.get("helper"),
        )
        for item in fairness_payload
    ]


async def _invoke_interview_pack(
    orchestrator: LLMOrchestrator,
    config: LLMProviderConfig,
    context_json: str,
) -> List[InterviewQuestion]:
    instruction = await _get_prompt_content(
        "interview_preparation",
        "Generate interview preparation pack questions focused on validating must-have skills and risks. "
        "Return JSON with key 'interview_preparation' where each item has 'question' and 'rationale'."
    )
    data = await _invoke_json(orchestrator, config, instruction, context_json)
    questions_payload = data.get("interview_preparation", [])
    return [
        InterviewQuestion(
            question=item.get("question", ""),
            rationale=item.get("rationale", ""),
        )
        for item in questions_payload
    ]


async def _invoke_json(
    orchestrator: LLMOrchestrator,
    config: LLMProviderConfig,
    instruction: str,
    context_json: str,
) -> Dict[str, object]:
    messages = [
        LLMMessage(role="system", content=_SYSTEM_PROMPT),
        LLMMessage(
            role="user",
            content=(
                f"{instruction}\n\nUse the following JSON context."
                " Respond strictly with a single JSON object, no markdown or commentary.\n" + context_json
            ),
        ),
    ]
    raw = await orchestrator.generate(messages, config)
    return _parse_json_response(raw)


def _parse_json_response(raw: str) -> Dict[str, object]:
    stripped = raw.strip()
    if stripped.startswith("```"):
        stripped = stripped.strip("`").strip()
        if stripped.lower().startswith("json"):
            stripped = stripped[4:].strip()
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start == -1 or end == -1:
        raise RuntimeError("LLM response did not contain JSON object")
    json_str = stripped[start : end + 1]
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {e}. Raw response: {raw}")
        raise RuntimeError(f"LLM returned invalid JSON: {e}") from e
