"""Pydantic v2 schemas for the Career Platform API v2."""

from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field


# ── Evaluation ────────────────────────────────────────────────────────────────

class EvaluationRequest(BaseModel):
    input: str = Field(..., description="Job URL or raw JD text")
    input_type: str = Field(default="auto", description="'url', 'text', or 'auto'")
    generate_pdf: bool = False
    draft_answers: bool = False


class EvaluationBlock(BaseModel):
    phase: str        # "A" through "F"
    label: str        # "Role Summary", "CV Match", etc.
    content: str
    done: bool = True


class EvaluationResult(BaseModel):
    report_id: str
    company: str
    role: str
    archetype: str
    score: float
    blocks: list[EvaluationBlock]
    keywords: list[str]
    pdf_path: Optional[str] = None
    report_path: str
    date: str
    url: Optional[str] = None


class EvaluationStreamEvent(BaseModel):
    phase: str              # "A"-"F", "score", "error"
    content: str = ""
    done: bool = False
    score: Optional[float] = None
    archetype: Optional[str] = None
    report_id: Optional[str] = None
    pdf_path: Optional[str] = None
    error: Optional[str] = None


# ── Comparison ────────────────────────────────────────────────────────────────

class ComparisonRequest(BaseModel):
    report_ids: list[str] = Field(..., min_length=2)


class ComparisonDimension(BaseModel):
    name: str
    weight: float
    scores: dict[str, float]  # report_id → score


class ComparisonMatrix(BaseModel):
    offers: list[dict[str, Any]]   # [{report_id, company, role, score}]
    dimensions: list[ComparisonDimension]
    weighted_totals: dict[str, float]  # report_id → total
    ranking: list[str]               # report_ids ordered best→worst
    recommendation: str


# ── CV Studio ────────────────────────────────────────────────────────────────

class CVGenerateRequest(BaseModel):
    jd_text: Optional[str] = None
    report_id: Optional[str] = None   # link to existing eval for JD
    format: str = "a4"                 # "a4" or "letter"


class CVGenerateResult(BaseModel):
    cv_id: str
    pdf_path: str
    html_path: str
    keywords_injected: list[str]
    keyword_coverage_pct: int
    pages: int


class CVPreviewRequest(BaseModel):
    jd_text: Optional[str] = None
    report_id: Optional[str] = None
    keywords: Optional[list[str]] = None


# ── Scanner ───────────────────────────────────────────────────────────────────

class ScanRequest(BaseModel):
    levels: list[str] = Field(default=["direct", "greenhouse", "search"])
    company_groups: list[str] = Field(default=["all"])


class ScanResult(BaseModel):
    url: str
    title: str
    company: str
    source: str         # "playwright" | "greenhouse" | "websearch"
    priority: bool      # seniority_boost matched
    date_found: str
    status: str = "new" # "new" | "seen" | "filtered"


class ScanJobStatus(BaseModel):
    job_id: str
    status: str          # "running" | "done" | "error"
    companies_scanned: int = 0
    total_companies: int = 0
    found: int = 0
    filtered: int = 0
    new: int = 0
    results: list[ScanResult] = []
    error: Optional[str] = None


# ── Tracker ───────────────────────────────────────────────────────────────────

class ApplicationEntry(BaseModel):
    num: int
    date: str
    company: str
    role: str
    score: str           # "4.2/5" or "N/A"
    status: str
    pdf: bool
    report_path: Optional[str] = None
    notes: str = ""


class TrackerStats(BaseModel):
    total: int
    by_status: dict[str, int]
    avg_score: Optional[float]
    pdf_coverage_pct: int
    report_coverage_pct: int


class FunnelData(BaseModel):
    stages: list[dict[str, Any]]  # [{name, count, pct}]


class ScoreTrendPoint(BaseModel):
    date: str
    score: float
    company: str
    role: str
    archetype: str


class StatusUpdateRequest(BaseModel):
    status: str


class NotesUpdateRequest(BaseModel):
    notes: str


# ── Outreach ──────────────────────────────────────────────────────────────────

class OutreachRequest(BaseModel):
    company: str
    role: str
    report_id: Optional[str] = None


class Contact(BaseModel):
    name: str
    title: str
    linkedin_url: Optional[str] = None
    company: str


class MessageRequest(BaseModel):
    contact: Contact
    report_id: Optional[str] = None
    language: str = "en"


class OutreachResult(BaseModel):
    contact: Contact
    messages: list[str]   # 3 variants
    char_counts: list[int]


# ── Prepare ───────────────────────────────────────────────────────────────────

class PrepareRequest(BaseModel):
    company: str
    role: str
    report_id: Optional[str] = None


class StoryEntry(BaseModel):
    title: str
    situation: str
    task: str
    action: str
    result: str
    reflection: str
    archetypes: list[str] = []


class InterviewPrepResult(BaseModel):
    company: str
    role: str
    questions: list[dict[str, str]]   # [{question, answer_guidance}]
    stories: list[StoryEntry]
    red_flags: list[dict[str, str]]   # [{question, how_to_handle}]
    day_of_tips: list[str]
    output_path: Optional[str] = None


# ── Insights ──────────────────────────────────────────────────────────────────

class ProjectEvalRequest(BaseModel):
    name: str
    description: str
    tech_stack: list[str] = []
    status: str = "idea"  # "idea" | "in-progress" | "done"


class ProjectEvalResult(BaseModel):
    name: str
    scores: dict[str, float]  # dimension → score
    total: float
    verdict: str              # "BUILD" | "SKIP" | "PIVOT"
    reasoning: str
    action_plan: Optional[str] = None


class TrainingEvalRequest(BaseModel):
    name: str
    provider: str
    weeks: int
    hours_per_week: int
    description: str = ""


class TrainingEvalResult(BaseModel):
    name: str
    scores: dict[str, float]
    total: float
    verdict: str    # "DO IT" | "SKIP" | "DO WITH TIMEBOX"
    timebox_weeks: Optional[int] = None
    reasoning: str


# ── Settings ──────────────────────────────────────────────────────────────────

class ProfileConfig(BaseModel):
    full_name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin: str = ""
    portfolio_url: str = ""
    github: str = ""
    target_roles: list[str] = []
    compensation_target: str = ""
    compensation_currency: str = "USD"
    compensation_minimum: str = ""
    visa_status: str = ""
    timezone: str = ""


class PortalsConfig(BaseModel):
    raw_yaml: str  # pass-through; validated on write
