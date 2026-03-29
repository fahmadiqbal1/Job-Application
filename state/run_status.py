"""
Single-process shared state for active pipeline runs.

Both bot/telegram_bot.py and api/routes.py read/write here to track
the currently active run across both interfaces (Telegram and web API).
"""

import asyncio
import time
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ActiveRun:
    """Represents an active job application pipeline run."""

    run_id: str
    keywords: str
    chat_id: str  # Telegram chat_id (or "web" for web-started runs)
    stop_event: asyncio.Event = field(default_factory=asyncio.Event)
    phase: str = "starting"  # scraped | ats | cover_letters | apply | notify | done | error
    phase_detail: str = ""  # free-text, e.g. "Scraping Hiredly (5/15 jobs)..."
    started_at: float = field(default_factory=time.time)
    error: Optional[str] = None


# Only one run at a time — enforced at orchestrator level
_active_run: Optional[ActiveRun] = None


def start_run(run_id: str, keywords: str, chat_id: str) -> ActiveRun:
    """Create and activate a new run."""
    global _active_run
    _active_run = ActiveRun(run_id=run_id, keywords=keywords, chat_id=chat_id)
    return _active_run


def get_active_run() -> Optional[ActiveRun]:
    """Get the currently active run, or None if idle."""
    return _active_run


def set_phase(phase: str, detail: str = "") -> None:
    """Update the current phase and optional detail message."""
    if _active_run:
        _active_run.phase = phase
        _active_run.phase_detail = detail


def set_error(error: str) -> None:
    """Mark the run as errored and store the error message."""
    if _active_run:
        _active_run.error = error
        _active_run.phase = "error"


def clear_run() -> None:
    """Clear the active run (call after pipeline completes)."""
    global _active_run
    _active_run = None
