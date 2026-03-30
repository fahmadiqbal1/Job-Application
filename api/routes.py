"""FastAPI REST routes for the job application dashboard."""

import logging
from typing import Optional
from pathlib import Path
from datetime import datetime

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

from state.run_status import get_active_run, set_phase, clear_run
from state.confirmation import get_pending_job_ids
from state.storage import load_latest_state, load_run_state
from config.settings import settings
from config.portals import PORTALS, get_enabled_portals, verify_selectors
from config.model_factory import AVAILABLE_MODELS
from api.models import SearchRequest, ConfirmRequest, SettingsUpdate
from api.websocket import manager, browser_manager
from orchestrator import run_pipeline
import asyncio
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["job-application"])


# ── Status & Health ──


@router.get("/status")
async def get_status():
    """Get current pipeline status and pending confirmations."""
    run = get_active_run()
    pending = get_pending_job_ids()

    if run:
        started_at_iso = None
        if run.started_at:
            started_at_iso = datetime.fromtimestamp(run.started_at).isoformat()
        return {
            "is_active": True,
            "run_id": run.run_id,
            "phase": run.phase,
            "phase_detail": run.phase_detail,
            "started_at": started_at_iso,
            "pending_confirmations": list(pending),
        }
    else:
        return {
            "is_active": False,
            "run_id": None,
            "phase": None,
            "phase_detail": None,
            "pending_confirmations": [],
        }


@router.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok"}


# ── Pipeline Control ──


@router.post("/search")
async def start_search(request: SearchRequest):
    """Start a new job search pipeline run."""
    run = get_active_run()
    if run:
        raise HTTPException(
            status_code=409, detail="Pipeline already running. Use /stop first."
        )

    run_id = str(uuid.uuid4())
    chat_id = "web"  # Web-initiated runs use 'web' as chat_id

    # Create the run in background
    async def run_bg():
        await run_pipeline(request.keywords, chat_id, asyncio.Event(), run_id=run_id)

    asyncio.create_task(run_bg())

    return {
        "run_id": run_id,
        "keywords": request.keywords,
        "status": "started",
    }


@router.post("/stop")
async def stop_pipeline():
    """Stop the currently active run."""
    run = get_active_run()
    if not run:
        raise HTTPException(status_code=404, detail="No active run to stop")

    run.stop_event.set()
    clear_run()

    return {"status": "stopped", "run_id": run.run_id}


# ── Jobs Management ──


@router.get("/jobs")
async def get_jobs(run_id: Optional[str] = None):
    """Get jobs from latest run or specified run."""
    if run_id:
        state = load_run_state(run_id)
    else:
        state = load_latest_state()

    if not state or not state.get("jobs"):
        return {"jobs": [], "run_id": run_id, "count": 0}

    jobs = state.get("jobs", [])
    ats_scores = state.get("ats_scores", {})
    resume_edits = state.get("resume_edits", {})

    # Enrich jobs with ATS scores
    for job in jobs:
        job_id = job.get("job_id")
        if job_id in ats_scores:
            job["ats_score"] = ats_scores[job_id].get("score")
            job["ats_missing"] = ats_scores[job_id].get("missing_keywords", [])
        if job_id in resume_edits:
            job["has_edits"] = bool(resume_edits[job_id].get("edits"))

    return {
        "jobs": jobs,
        "run_id": run_id or state.get("run_id"),
        "count": len(jobs),
    }


@router.get("/jobs/{job_id}")
async def get_job_detail(job_id: str):
    """Get detailed information about a specific job."""
    state = load_latest_state()
    if not state:
        raise HTTPException(status_code=404, detail="No run state found")

    job = next((j for j in state.get("jobs", []) if j["job_id"] == job_id), None)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    detail = {
        "job": job,
        "cover_letter": state.get("cover_letters", {}).get(job_id),
        "ats_score": state.get("ats_scores", {}).get(job_id),
        "resume_edits": state.get("resume_edits", {}).get(job_id),
        "application_result": state.get("application_results", {}).get(job_id),
    }

    return detail


@router.get("/runs")
async def get_run_history(limit: int = 10):
    """Get list of recent runs."""
    # TODO: Implement run history (requires state storage with timestamps)
    return {"runs": [], "limit": limit}


# ── Confirmations ──


@router.get("/confirm/pending")
async def get_pending_confirmations():
    """Get jobs awaiting user confirmation."""
    state = load_latest_state()
    if not state:
        return {"pending": []}

    pending_ids = get_pending_job_ids()
    pending = []

    for job_id in pending_ids:
        job = next((j for j in state.get("jobs", []) if j["job_id"] == job_id), None)
        if job:
            pending.append(
                {
                    "job_id": job_id,
                    "title": job.get("title"),
                    "company": job.get("company"),
                    "portal": job.get("portal"),
                    "ats_score": state.get("ats_scores", {}).get(job_id, {}).get("score"),
                    "cover_letter_preview": (
                        state.get("cover_letters", {})
                        .get(job_id, "")[:400]
                    ),
                }
            )

    return {"pending": pending, "count": len(pending)}


@router.post("/confirm/{job_id}")
async def confirm_job(job_id: str, request: ConfirmRequest):
    """Record user confirmation (YES/SKIP) for a job."""
    from state.confirmation import resolve_confirmation

    action = request.action
    if action not in ("YES", "SKIP"):
        raise HTTPException(status_code=400, detail="Action must be YES or SKIP")

    resolved = resolve_confirmation(job_id, action)
    if not resolved:
        raise HTTPException(status_code=404, detail="Job not pending confirmation")

    return {"job_id": job_id, "action": action, "status": "recorded"}


# ── Settings ──


@router.get("/settings")
async def get_settings():
    """Get current settings (secrets masked)."""
    return {
        "resume_path": str(settings.resume_path),
        "telegram_bot_token": "***" if settings.telegram_bot_token else None,
        "smtp_host": settings.smtp_host,
        "smtp_port": settings.smtp_port,
        "smtp_user": settings.smtp_user,
        "confirmation_timeout_secs": settings.confirmation_timeout_secs,
        "target_ats_score": settings.target_ats_score,
        "models": {
            "scraper": settings.model_scraper,
            "ats": settings.model_ats,
            "cover_letter": settings.model_cover_letter,
            "application": settings.model_application,
            "notifier": settings.model_notifier,
        },
    }


@router.post("/settings")
async def update_settings(request: SettingsUpdate):
    """Update settings (only certain fields allowed)."""
    # TODO: Implement settings persistence
    return {"status": "updated"}


# ── Models ──


@router.get("/models")
async def get_available_models():
    """Get list of available LLM models."""
    return {
        "models": AVAILABLE_MODELS,
        "agents": [
            "scraper",
            "ats",
            "cover_letter",
            "application",
            "notifier",
        ],
    }


# ── Portals ──


@router.get("/portals")
async def get_portals():
    """Get list of all configured portals."""
    portals_list = []
    for name, config in PORTALS.items():
        portals_list.append(
            {
                "name": name,
                "display_name": config.get("name", name),
                "region": config.get("region"),
                "type": config.get("type"),
                "enabled": True,  # TODO: Track enabled/disabled status per user
            }
        )
    return {"portals": portals_list, "count": len(portals_list)}


@router.post("/portals")
async def add_portal(request: dict):
    """Add a custom portal (with LLM auto-discovery if needed)."""
    # TODO: Implement custom portal addition with selector discovery
    return {"status": "added"}


@router.put("/portals/{portal_name}")
async def update_portal(portal_name: str, request: dict):
    """Update portal selectors."""
    # TODO: Implement portal update
    return {"status": "updated"}


@router.delete("/portals/{portal_name}")
async def delete_portal(portal_name: str):
    """Remove a custom portal."""
    # TODO: Implement portal deletion
    return {"status": "deleted"}


# ── Health Checks ──


@router.get("/health/selectors")
async def get_selector_health():
    """Get health status of selectors for all Playwright portals."""
    health = {}
    for portal_name in get_enabled_portals():
        config = PORTALS.get(portal_name, {})
        if config.get("type") != "Playwright":
            continue  # Skip REST API portals

        health[portal_name] = {
            "portal": portal_name,
            "name": config.get("name"),
            "status": "unknown",  # Will be populated after verification
        }

    return {"health": health}


@router.post("/health/selectors/verify")
async def verify_all_selectors():
    """Trigger fresh selector verification for all portals and emit results via WebSocket."""
    results = {}

    for portal_name in get_enabled_portals():
        config = PORTALS.get(portal_name, {})
        if config.get("type") != "Playwright":
            results[portal_name] = {
                "portal": portal_name,
                "healthy": True,
                "type": "REST_API",
            }
            continue

        logger.info(f"Verifying selectors for {portal_name}...")
        result = await verify_selectors(portal_name)
        results[portal_name] = {
            "portal": portal_name,
            "healthy": result.get("healthy"),
            "failed_selector": result.get("failed_selector"),
            "error_detail": result.get("error_detail"),
        }

        # Broadcast result via WebSocket
        try:
            from api.websocket import emit_selector_result

            await emit_selector_result(
                portal=portal_name,
                healthy=result.get("healthy"),
                failed_selector=result.get("failed_selector"),
                error_detail=result.get("error_detail"),
            )
        except Exception as e:
            logger.warning(f"Failed to emit selector result: {e}")

    return {
        "results": results,
        "healthy_count": sum(
            1 for r in results.values() if r.get("healthy")
        ),
        "total_count": len(results),
    }


# ── Screenshots ──


@router.get("/screenshots/{filename}")
async def get_screenshot(filename: str):
    """Serve a screenshot file (path traversal protected)."""
    # Validate filename to prevent path traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    screenshot_dir = Path(settings.ats_workspace_dir) / "screenshots"
    screenshot_path = screenshot_dir / filename

    if not screenshot_path.exists():
        raise HTTPException(status_code=404, detail="Screenshot not found")

    return FileResponse(screenshot_path, media_type="image/jpeg")


# ── WebSocket Endpoints ──


@router.websocket("/ws/status")
async def websocket_status(websocket: WebSocket):
    """WebSocket for pipeline events (phase changes, job found, ATS scores, etc.)."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive by waiting for messages
            data = await websocket.receive_text()
            # Echo back (optional — could implement subscriptions here)
            await websocket.send_text(f"pong: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket status error: {e}")
        manager.disconnect(websocket)


@router.websocket("/ws/browser")
async def websocket_browser(websocket: WebSocket):
    """WebSocket for live browser stream (screenshots, actions, selectors)."""
    await browser_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Keep connection alive
            await websocket.send_text("frame_ack")
    except WebSocketDisconnect:
        browser_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket browser error: {e}")
        browser_manager.disconnect(websocket)
