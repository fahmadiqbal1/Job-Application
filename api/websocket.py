"""
WebSocket connection manager.

Any part of the backend calls broadcast() to push events to all connected
web frontends. Events flow through /ws/status (pipeline events) and
/ws/browser (live activity stream).
"""

import asyncio
import json
import logging
from fastapi import WebSocket
from typing import Optional

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and broadcasts events."""

    def __init__(self):
        self._connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self._connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        """Remove a disconnected WebSocket."""
        if websocket in self._connections:
            self._connections.remove(websocket)

    async def broadcast(self, event_type: str, payload: dict) -> None:
        """
        Broadcast an event to all connected clients.

        Args:
            event_type: e.g. "phase_start", "job_found", "error"
            payload: dict of event data
        """
        message = json.dumps({"type": event_type, "data": payload})
        dead = []
        for ws in self._connections:
            try:
                await ws.send_text(message)
            except Exception as e:
                logger.debug(f"WebSocket send failed: {e}")
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


# Global connection manager for /ws/status (pipeline events)
manager = ConnectionManager()

# Global connection manager for /ws/browser (live activity stream)
browser_manager = ConnectionManager()


# ── Convenience helpers called from orchestrator.py ──────────────────────────


async def emit_phase_start(phase: str, detail: str = "") -> None:
    """Emit when a pipeline phase begins."""
    await manager.broadcast("phase_start", {"phase": phase, "detail": detail})


async def emit_job_found(job: dict) -> None:
    """Emit when a job is scraped."""
    await manager.broadcast("job_found", {"job": job})


async def emit_ats_score(job_id: str, score: int, missing_keywords: list[str]) -> None:
    """Emit when ATS analysis completes for a job."""
    await manager.broadcast(
        "ats_score",
        {"job_id": job_id, "score": score, "missing_keywords": missing_keywords},
    )


async def emit_resume_diff(job_id: str, original: str, edited: str) -> None:
    """Emit when ATS suggests resume edits."""
    await manager.broadcast(
        "resume_diff", {"job_id": job_id, "original": original, "edited": edited}
    )


async def emit_cover_letter_done(job_id: str, preview: str) -> None:
    """Emit when cover letter is generated."""
    await manager.broadcast(
        "cover_letter_done", {"job_id": job_id, "preview": preview}
    )


async def emit_confirmation_request(
    job_id: str, job_title: str, company: str, cover_letter_preview: str, ats_score: Optional[int] = None
) -> None:
    """Emit when application needs user confirmation."""
    await manager.broadcast(
        "confirmation_request",
        {
            "job_id": job_id,
            "job_title": job_title,
            "company": company,
            "cover_letter_preview": cover_letter_preview,
            "ats_score": ats_score,
        },
    )


async def emit_job_applied(job_id: str, job_title: str, company: str) -> None:
    """Emit when application is submitted."""
    await manager.broadcast(
        "job_applied",
        {"job_id": job_id, "job_title": job_title, "company": company},
    )


async def emit_pipeline_complete(run_id: str, applied_count: int) -> None:
    """Emit when pipeline finishes."""
    await manager.broadcast(
        "pipeline_complete", {"run_id": run_id, "applied_count": applied_count}
    )


async def emit_error(message: str, job_id: Optional[str] = None) -> None:
    """Emit when an error occurs."""
    await manager.broadcast("error", {"message": message, "job_id": job_id})


async def emit_status_update(
    is_active: bool, run_id: Optional[str], phase: str, pending_confirmations: list[str]
) -> None:
    """Emit periodic status heartbeat."""
    await manager.broadcast(
        "status_update",
        {
            "is_active": is_active,
            "run_id": run_id,
            "phase": phase,
            "pending_confirmations": pending_confirmations,
        },
    )


# ── Browser stream helpers ──────────────────────────────────────────────────


async def emit_screenshot(frame_b64: str, url: str, action: str) -> None:
    """Emit a browser screenshot frame."""
    await browser_manager.broadcast(
        "frame", {"data": frame_b64, "url": url, "action": action}
    )


async def emit_selector_result(
    portal: str, healthy: bool, failed_selector: Optional[str] = None, error_detail: Optional[str] = None
) -> None:
    """Emit selector verification result."""
    await browser_manager.broadcast(
        "selector_result",
        {
            "portal": portal,
            "healthy": healthy,
            "failed_selector": failed_selector,
            "error_detail": error_detail,
        },
    )
