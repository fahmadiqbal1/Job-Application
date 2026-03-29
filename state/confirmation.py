"""
Shared confirmation state — the single source of truth for YES/SKIP decisions.

Both bot/telegram_bot.py (Telegram callbacks) and api/routes.py (web UI button)
write into this module. tools/notifier_tools.py reads from it.

This breaks the circular import that existed between telegram_bot.py and
notifier_tools.py.
"""

import asyncio
from typing import Optional


# job_id → asyncio.Event that notifier_tools is waiting on
_pending_confirmations: dict[str, asyncio.Event] = {}

# job_id → "YES" | "SKIP"  (written before the event is fired)
_confirmation_results: dict[str, str] = {}

# The running event loop — set once at startup by main.py
_main_loop: Optional[asyncio.AbstractEventLoop] = None


def set_main_loop(loop: asyncio.AbstractEventLoop) -> None:
    """Called once from main.py after asyncio.get_event_loop()."""
    global _main_loop
    _main_loop = loop


def get_main_loop() -> Optional[asyncio.AbstractEventLoop]:
    """Return the main event loop (set at startup)."""
    return _main_loop


async def _fire_event(job_id: str) -> None:
    """Set the event for job_id so request_telegram_confirmation() unblocks."""
    if job_id in _pending_confirmations:
        _pending_confirmations[job_id].set()


def resolve_confirmation(job_id: str, action: str) -> bool:
    """
    Record an action and fire the asyncio event.
    Can be called from ANY thread (Telegram daemon or FastAPI handler).

    Args:
        job_id: The job identifier waiting for confirmation
        action: "YES" or "SKIP"

    Returns:
        False if job_id is not pending (was already resolved or timed out)
    """
    if job_id not in _pending_confirmations:
        return False

    _confirmation_results[job_id] = action  # write result first

    if _main_loop and not _main_loop.is_closed():
        # Called from Telegram daemon thread — use threadsafe bridge
        asyncio.run_coroutine_threadsafe(_fire_event(job_id), _main_loop)
    else:
        # Already on the main loop (FastAPI request path)
        _pending_confirmations[job_id].set()

    return True


def get_pending_job_ids() -> list[str]:
    """Return job IDs currently waiting for a decision."""
    return list(_pending_confirmations.keys())


def register_pending(job_id: str) -> asyncio.Event:
    """
    Create and register a new Event for job_id.

    Returns:
        The event to wait on in request_telegram_confirmation()
    """
    event = asyncio.Event()
    _pending_confirmations[job_id] = event
    return event


def clear_confirmation(job_id: str) -> None:
    """Clean up after a confirmation is resolved (call from finally block)."""
    _pending_confirmations.pop(job_id, None)
    _confirmation_results.pop(job_id, None)


def get_result(job_id: str) -> str:
    """Return the recorded result, defaulting to SKIP if not found."""
    return _confirmation_results.get(job_id, "SKIP")
