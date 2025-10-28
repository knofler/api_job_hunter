from __future__ import annotations

import json
import logging
from typing import Dict, Iterable, List, Optional

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


async def _invoke_core_skills(
    orchestrator: LLMOrchestrator,
    config: LLMProviderConfig,
    context_json: str,
) -> List[CoreSkill]:
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
    instruction = (
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
    instruction = (
        "Generate a ranked shortlist of candidates."
        " Return JSON with key 'ranked_shortlist' where each item includes 'candidate_id', 'rank' (1-based),"
        " 'priority' (Hot/Warm/Pipeline), 'status', 'availability', and 'notes'."
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
    instruction = (
        "Create a detailed readout for each candidate."
        " Return JSON with key 'detailed_readout' of objects that include 'candidate_id',"
        " 'strengths' (list of strings), 'risks' (list of strings), and 'recommended_actions' (list of strings)."
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
    instruction = (
        "Propose an engagement plan for stakeholders."
        " Return JSON with key 'engagement_plan' where every item has 'label', 'value', and optional 'helper'."
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
    instruction = (
        "Highlight fairness, bias mitigation, and panel guidance actions."
        " Return JSON with key 'fairness_guidance' where each item includes 'label', 'value', and optional 'helper'."
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
    instruction = (
        "Generate interview preparation pack questions focused on validating must-have skills and risks."
        " Return JSON with key 'interview_preparation' where each item has 'question' and 'rationale'."
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
    return json.loads(json_str)
