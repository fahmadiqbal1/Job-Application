"""Pydantic request/response models for FastAPI routes."""

from pydantic import BaseModel
from typing import Optional


class SearchRequest(BaseModel):
    """Request to start a new job search pipeline."""

    keywords: str


class ConfirmRequest(BaseModel):
    """Request to confirm/reject a job application."""

    action: str  # "YES" or "SKIP"


class SettingsUpdate(BaseModel):
    """Request to update environment settings."""

    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    telegram_bot_token: Optional[str] = None
    telegram_allowed_users: Optional[str] = None
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_user: Optional[str] = None
    smtp_pass: Optional[str] = None
    notification_email: Optional[str] = None
    hiredly_email: Optional[str] = None
    hiredly_password: Optional[str] = None
    jobstreet_email: Optional[str] = None
    jobstreet_password: Optional[str] = None
    linkedin_email: Optional[str] = None
    linkedin_password: Optional[str] = None
    resume_path: Optional[str] = None
    screenshots_dir: Optional[str] = None
    max_jobs_per_run: Optional[int] = None
    confirmation_timeout_secs: Optional[int] = None
    model_scraper: Optional[str] = None
    model_ats: Optional[str] = None
    model_cover_letter: Optional[str] = None
    model_application: Optional[str] = None
    model_notifier: Optional[str] = None


class SelectorResult(BaseModel):
    """Health check result for a portal's CSS selectors."""

    portal: str
    healthy: bool
    failed_selector: Optional[str] = None  # human-readable, e.g. "Apply button"
    error_detail: Optional[str] = None
    checked_at: Optional[float] = None


class RunSummary(BaseModel):
    """Summary of a completed or in-progress run."""

    run_id: str
    keywords: str
    started_at: float
    phase: str
    applied_count: int
    total_jobs: int


class JobQuickView(BaseModel):
    """Enriched job listing for confirmation queue view."""

    job_id: str
    job_title: str
    company: str
    portal: str
    cover_letter_preview: str
    ats_score: Optional[int] = None
