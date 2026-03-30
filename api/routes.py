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


# ── Prompt Library ──


@router.get("/prompts")
async def get_all_prompts():
    """Get all prompts from the library."""
    from state.prompts import load_prompts

    prompts = load_prompts()
    return {"prompts": prompts}


@router.get("/prompts/{prompt_key}")
async def get_prompt(prompt_key: str):
    """Get a single prompt by key."""
    from state.prompts import get_prompt

    prompt_text = get_prompt(prompt_key)
    if not prompt_text:
        raise HTTPException(status_code=404, detail=f"Prompt '{prompt_key}' not found")

    return {"key": prompt_key, "text": prompt_text}


@router.put("/prompts/{prompt_key}")
async def update_prompt(prompt_key: str, request: dict):
    """Update a single prompt."""
    from state.prompts import load_prompts, update_prompt as _update_prompt

    prompts = load_prompts()
    if prompt_key not in prompts:
        raise HTTPException(status_code=404, detail=f"Prompt '{prompt_key}' not found")

    new_text = request.get("text", "")
    if not new_text:
        raise HTTPException(status_code=400, detail="Prompt text cannot be empty")

    _update_prompt(prompt_key, new_text)
    return {"key": prompt_key, "status": "updated"}


@router.post("/prompts/reset")
async def reset_prompts_to_defaults():
    """Reset all prompts to defaults."""
    from state.prompts import _get_defaults, save_prompts

    defaults = _get_defaults()
    save_prompts(defaults)
    return {"status": "reset", "prompt_count": len(defaults)}


# ── Career Tools ──


@router.post("/career/resume/analyze")
async def analyze_resume(request: dict):
    """
    Analyze resume for quality and ATS issues.

    Steps:
    1. Generic check: flag AI-signature phrases, vague metrics, missing context
    2. Quality score: bullet-by-bullet scoring on [Verb]+[Did]+[Metric] formula

    Returns generic check flags + quality scores.
    """
    from tools.career_tools import analyze_resume_quality
    from state.storage import load_latest_state

    resume_text = request.get("resume_text")
    if not resume_text:
        # Try to load from latest state
        state = load_latest_state()
        if not state:
            raise HTTPException(status_code=400, detail="Resume text required or no recent run")
        # For now, return placeholder — full implementation requires resume content
        return {"error": "Resume text required"}

    result_str = await analyze_resume_quality(resume_text)
    try:
        import json
        result = json.loads(result_str)
    except:
        result = {"error": "Could not parse analysis"}

    return result


@router.post("/career/resume/interview-bullet")
async def interview_bullet(request: dict):
    """
    Step-by-step interview mode for improving a weak resume bullet.

    Steps: 1 (project context) → 2 (scope/scale) → 3 (metric/outcome) → compose final bullet.

    Returns:
    - Step 1/2: question for user to answer
    - Step 3: final composed bullet + accept/reject
    """
    from config.model_factory import get_llm
    from config.settings import settings
    from state.prompts import get_prompt
    from langchain_core.messages import HumanMessage
    import json

    bullet = request.get("bullet", "")
    step = request.get("step", 1)  # 1, 2, or 3
    answers = request.get("answers", [])  # Previous answers from steps 1-2

    if not bullet:
        raise HTTPException(status_code=400, detail="Bullet text required")

    try:
        if step in [1, 2, 3]:
            # Steps 1-2: Ask follow-up question
            if step <= 2:
                prompt_template = get_prompt("resume_bullet_interview")
                if not prompt_template:
                    return {"error": "Prompt not found"}

                llm = get_llm(settings.model_ats, temperature=0)
                prompt = HumanMessage(
                    content=prompt_template.format(
                        bullet=bullet, step=step, answers=json.dumps(answers)
                    )
                )
                response = await llm.ainvoke([prompt])
                return {"step": step, "question": response.content.strip()}

            # Step 3: Compose final bullet
            else:
                prompt_template = get_prompt("resume_bullet_compose")
                if not prompt_template:
                    return {"error": "Prompt not found"}

                llm = get_llm(settings.model_ats, temperature=0.5)
                prompt = HumanMessage(
                    content=prompt_template.format(
                        bullet=bullet, answers=json.dumps(answers)
                    )
                )
                response = await llm.ainvoke([prompt])
                final_bullet = response.content.strip()
                return {"step": 3, "final_bullet": final_bullet}
        else:
            raise HTTPException(status_code=400, detail="Step must be 1, 2, or 3")

    except Exception as e:
        logger.error(f"Interview bullet failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/career/linkedin/optimize")
async def optimize_linkedin(request: dict):
    """
    Optimize LinkedIn profile for goal (attract PM roles, build AI authority, etc.).

    Returns section-by-section rewrites: headline, about, experience, skills, featured, CTA.
    """
    from tools.career_tools import optimize_linkedin_profile

    profile_text = request.get("profile_text", "")
    goal = request.get("goal", "")

    if not profile_text or not goal:
        raise HTTPException(status_code=400, detail="profile_text and goal required")

    result_str = await optimize_linkedin_profile(profile_text, goal)
    try:
        import json
        result = json.loads(result_str)
    except:
        result = {"error": "Could not parse optimization results"}

    return result


@router.post("/career/hiring-managers")
async def search_hiring_managers(request: dict):
    """
    Search Bing for LinkedIn posts from hiring managers in target role/location.

    Uses 3 search patterns to find recent posts mentioning "I'm hiring", "DM me", etc.

    Returns list of: [{name, company, post_snippet, url, pattern: A|B|C}]
    """
    from tools.career_tools import search_hiring_managers

    role = request.get("role", "")
    industry = request.get("industry", "")
    location = request.get("location", "")

    if not role:
        raise HTTPException(status_code=400, detail="role required")

    result_str = await search_hiring_managers(role, industry, location)
    try:
        import json
        result = json.loads(result_str)
    except:
        result = {"error": "Could not parse search results"}

    return result


@router.post("/career/hiring-managers/draft-dm")
async def draft_hiring_manager_dm(request: dict):
    """
    Generate a personalized DM for a hiring manager based on their post.

    Args:
        post_snippet: The hiring manager's post text
        user_background: User's background summary
        role: Target role

    Returns:
        Personalized DM text (max 5 sentences)
    """
    from config.model_factory import get_llm
    from config.settings import settings
    from state.prompts import get_prompt
    from langchain_core.messages import HumanMessage

    post_snippet = request.get("post_snippet", "")
    user_background = request.get("user_background", "")
    role = request.get("role", "")

    if not post_snippet or not role:
        raise HTTPException(status_code=400, detail="post_snippet and role required")

    try:
        prompt_template = get_prompt("hiring_manager_dm")
        if not prompt_template:
            return {"error": "Prompt not found"}

        llm = get_llm(settings.model_ats, temperature=0.7)
        prompt = HumanMessage(
            content=prompt_template.format(
                post_snippet=post_snippet,
                user_background=user_background,
                role=role,
            )
        )
        response = await llm.ainvoke([prompt])
        return {"dm": response.content.strip()}

    except Exception as e:
        logger.error(f"DM generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/career/linkedin/post/ideas")
async def get_linkedin_post_ideas():
    """Get categories and starter ideas for LinkedIn posts."""
    categories = [
        {
            "id": "reintroduction",
            "label": "Reintroduction",
            "description": "Introduce yourself with your current role/background",
        },
        {
            "id": "lesson",
            "label": "Lessons Learned",
            "description": "Share a lesson from a recent project or challenge",
        },
        {
            "id": "hot_take",
            "label": "Hot Take",
            "description": "Share a contrarian industry opinion with backing",
        },
        {
            "id": "insight",
            "label": "Industry Insight",
            "description": "Share something non-obvious you've noticed in your field",
        },
        {
            "id": "tool",
            "label": "Tool Tip",
            "description": "Share your experience using an AI tool or technology",
        },
    ]
    return {"categories": categories}


@router.post("/career/linkedin/post")
async def generate_linkedin_post(request: dict):
    """
    Generate 3 LinkedIn post options in a given category.

    Args:
        category: Post category (reintroduction|lesson|hot_take|insight|tool)
        background: User's background/context

    Returns:
        3 editable post options
    """
    from tools.career_tools import generate_linkedin_post

    category = request.get("category", "")
    background = request.get("background", "")

    if not category or not background:
        raise HTTPException(status_code=400, detail="category and background required")

    result_str = await generate_linkedin_post(category, background)
    try:
        import json
        result = json.loads(result_str)
    except:
        result = {"error": "Could not generate posts"}

    return result


@router.post("/career/interview/prep")
async def generate_interview_prep(request: dict):
    """
    Generate interview prep with likely questions, talking points, and human touches.

    Uses job description + resume to create a quick reference card (not a script).

    Args:
        jd: Job description text
        resume_text: User's resume text (or auto-loaded if not provided)

    Returns:
        8 likely interview questions with bullet-point talking points + human touch suggestions
    """
    from config.model_factory import get_llm
    from config.settings import settings
    from state.prompts import get_prompt
    from config.resume import load_resume_text
    from langchain_core.messages import HumanMessage
    import json

    jd = request.get("jd", "")
    resume_text = request.get("resume_text")

    if not jd:
        raise HTTPException(status_code=400, detail="jd (job description) required")

    # Auto-load resume if not provided
    if not resume_text:
        try:
            resume_text = load_resume_text()
        except Exception as e:
            return {"error": f"Could not load resume: {str(e)}"}

    try:
        prompt_template = get_prompt("interview_prep")
        if not prompt_template:
            return {"error": "Prompt not found"}

        llm = get_llm(settings.model_ats, temperature=0.7)
        prompt = HumanMessage(
            content=prompt_template.format(jd=jd[:2000], resume=resume_text[:2000])
        )
        response = await llm.ainvoke([prompt])
        text = response.content.strip()

        # Parse JSON response
        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            return result
        else:
            return {"error": "Could not parse interview prep"}

    except Exception as e:
        logger.error(f"Interview prep generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
