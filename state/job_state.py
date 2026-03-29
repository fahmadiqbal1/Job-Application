from __future__ import annotations

import hashlib
from typing import Annotated, NotRequired, TypedDict

from langgraph.graph.message import add_messages


class JobListing(TypedDict):
    """A single job listing from a portal."""

    job_id: str  # md5(url)[:8] — stable, short, JSON-safe
    title: str
    company: str
    url: str
    portal: str  # "hiredly" | "jobstreet"
    description: str
    location: str
    status: str  # scraped → cover_written → confirmed → applied → skipped | failed


def merge_by_job_id(existing: list, incoming: list) -> list:
    """LangGraph reducer: merge JobListing lists by job_id, incoming wins on conflict."""
    merged = {j["job_id"]: j for j in (existing or [])}
    for job in incoming or []:
        merged[job["job_id"]] = job  # incoming overwrites — preserves status updates
    return list(merged.values())


class JobApplicationState(TypedDict):
    """LangGraph state — no AgentState base (deprecated in LangGraph 1.x)."""

    messages: Annotated[list, add_messages]  # required by create_react_agent
    jobs: Annotated[list[JobListing], merge_by_job_id]
    cover_letters: NotRequired[dict[str, str] | None]  # job_id → letter text
    application_results: NotRequired[dict[str, dict] | None]  # job_id → result dict
    ats_scores: NotRequired[dict[str, dict] | None]  # job_id → {"score": 0-100, "missing_keywords": [...]}
    resume_edits: NotRequired[dict[str, dict] | None]  # job_id → {"edits": [...], "edited_resume": "..."}
    errors: NotRequired[list[dict] | None]
    run_id: NotRequired[str | None]
    search_keywords: NotRequired[str | None]
    chat_id: NotRequired[str | None]  # Telegram chat_id that started the run
