from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.models.llm_model import LLMProviderConfig


class ResumeReference(BaseModel):
    resume_id: str
    candidate_id: Optional[str] = Field(default=None, description="Optional candidate identifier to enrich context")


class JobMetadata(BaseModel):
    title: Optional[str] = None
    code: Optional[str] = None
    level: Optional[str] = None
    salary_band: Optional[str] = None
    summary: Optional[str] = None


class RecruiterWorkflowRequest(BaseModel):
    job_description: str
    resumes: List[ResumeReference]
    job_metadata: JobMetadata = Field(default_factory=JobMetadata)
    step_overrides: Dict[str, LLMProviderConfig] = Field(default_factory=dict)


class CoreSkill(BaseModel):
    name: str
    reason: str


class SkillAlignment(BaseModel):
    skill: str
    status: str
    evidence: str


class CandidateAnalysis(BaseModel):
    candidate_id: str
    name: Optional[str] = None
    match_score: Optional[float] = None
    bias_free_score: Optional[float] = None
    summary: Optional[str] = None
    highlights: List[str] = Field(default_factory=list)
    skill_alignment: List[SkillAlignment] = Field(default_factory=list)


class RankedCandidateItem(BaseModel):
    candidate_id: str
    rank: int
    priority: Optional[str] = None
    status: Optional[str] = None
    availability: Optional[str] = None
    notes: Optional[str] = None


class CandidateReadout(BaseModel):
    candidate_id: str
    strengths: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    recommended_actions: List[str] = Field(default_factory=list)


class InsightItem(BaseModel):
    label: str
    value: str
    helper: Optional[str] = None


class InterviewQuestion(BaseModel):
    question: str
    rationale: str


class RecruiterWorkflowResponse(BaseModel):
    job: JobMetadata
    core_skills: List[CoreSkill]
    ai_analysis_markdown: str
    candidate_analysis: List[CandidateAnalysis]
    ranked_shortlist: List[RankedCandidateItem]
    detailed_readout: List[CandidateReadout]
    engagement_plan: List[InsightItem]
    fairness_guidance: List[InsightItem]
    interview_preparation: List[InterviewQuestion]