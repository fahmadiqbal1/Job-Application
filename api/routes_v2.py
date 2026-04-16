"""API v2 routes — Career Platform endpoints."""

from __future__ import annotations

import asyncio
import json
import uuid
from pathlib import Path
from typing import Any, Optional

import yaml
from fastapi import APIRouter, BackgroundTasks, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

from config.settings import settings
from models.schemas import (
    ApplicationEntry,
    ComparisonRequest,
    CVGenerateRequest,
    CVGenerateResult,
    CVPreviewRequest,
    EvaluationRequest,
    EvaluationResult,
    EvaluationStreamEvent,
    FunnelData,
    MessageRequest,
    NotesUpdateRequest,
    OutreachRequest,
    PortalsConfig,
    PrepareRequest,
    ProfileConfig,
    ProjectEvalRequest,
    ScanRequest,
    ScanJobStatus,
    StatusUpdateRequest,
    StoryEntry,
    TrackerStats,
    TrainingEvalRequest,
)
from tools.cv_tools import (
    read_cv,
    read_portals_raw,
    read_profile,
    write_cv,
    write_portals_raw,
    write_profile,
)
from tools.pipeline_inbox import add_url, get_pipeline_path, read_pending
from tools.tracker import (
    get_funnel,
    get_score_trends,
    get_stats,
    merge_additions,
    read_applications,
    update_entry,
)
from tools.story_bank import append_story, read_stories

router = APIRouter()

# In-memory scan job registry
_scan_jobs: dict[str, ScanJobStatus] = {}


def _paths() -> dict[str, str]:
    return {
        "data_dir": settings.data_dir,
        "scripts_dir": settings.scripts_dir,
        "prompts_dir": settings.prompts_dir,
        "templates_dir": settings.templates_dir,
        "node_path": settings.node_path,
    }


# ── Evaluation ────────────────────────────────────────────────────────────────

@router.post("/evaluate", response_model=EvaluationResult)
async def start_evaluation(req: EvaluationRequest):
    """Run A-F evaluation. Returns when complete (use /evaluate/stream for streaming)."""
    from agents.evaluator import run_evaluation
    p = _paths()
    try:
        result = await run_evaluation(
            raw_input=req.input,
            data_dir=p["data_dir"],
            scripts_dir=p["scripts_dir"],
            prompts_dir=p["prompts_dir"],
            node_path=p["node_path"],
            generate_pdf=req.generate_pdf,
            draft_answers=req.draft_answers,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/evaluate/stream")
async def evaluation_stream(websocket: WebSocket):
    """WebSocket stream: send JSON {input, input_type, generate_pdf} to start evaluation."""
    await websocket.accept()
    try:
        data = await websocket.receive_text()
        req = EvaluationRequest(**json.loads(data))
    except Exception as e:
        await websocket.send_json({"phase": "error", "error": str(e), "done": True})
        await websocket.close()
        return

    async def stream_cb(event: EvaluationStreamEvent):
        try:
            await websocket.send_json(event.model_dump())
        except Exception:
            pass

    from agents.evaluator import run_evaluation
    p = _paths()
    try:
        result = await run_evaluation(
            raw_input=req.input,
            data_dir=p["data_dir"],
            scripts_dir=p["scripts_dir"],
            prompts_dir=p["prompts_dir"],
            node_path=p["node_path"],
            generate_pdf=req.generate_pdf,
            draft_answers=req.draft_answers,
            stream_cb=stream_cb,
        )
        # Send final score event
        await websocket.send_json({
            "phase": "score",
            "score": result.score,
            "archetype": result.archetype,
            "report_id": result.report_id,
            "company": result.company,
            "role": result.role,
            "keywords": result.keywords,
            "pdf_path": result.pdf_path,
            "done": True,
        })
    except Exception as e:
        await websocket.send_json({"phase": "error", "error": str(e), "done": True})
    finally:
        try:
            await websocket.close()
        except Exception:
            pass


@router.get("/evaluate/{report_id}")
async def get_evaluation(report_id: str):
    """Fetch an existing evaluation report by ID."""
    reports_dir = Path(settings.data_dir) / "reports"
    matches = list(reports_dir.glob(f"{report_id}-*.md"))
    if not matches:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")
    return {"report_id": report_id, "content": matches[0].read_text(encoding="utf-8"), "path": str(matches[0])}


@router.post("/evaluate/compare")
async def compare_offers(req: ComparisonRequest):
    """Multi-offer 10-dimension comparison matrix."""
    from agents.comparator import compare_reports
    p = _paths()
    try:
        result = await compare_reports(
            report_ids=req.report_ids,
            data_dir=p["data_dir"],
            prompts_dir=p["prompts_dir"],
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── CV Studio ────────────────────────────────────────────────────────────────

@router.post("/cv/generate", response_model=CVGenerateResult)
async def generate_cv(req: CVGenerateRequest):
    """Keyword-inject CV and generate PDF."""
    from agents.cv_studio import generate_cv_pdf
    p = _paths()
    try:
        result = await generate_cv_pdf(
            jd_text=req.jd_text,
            report_id=req.report_id,
            format=req.format,
            data_dir=p["data_dir"],
            scripts_dir=p["scripts_dir"],
            prompts_dir=p["prompts_dir"],
            templates_dir=p["templates_dir"],
            node_path=p["node_path"],
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cv/preview")
async def preview_cv(req: CVPreviewRequest):
    """Return HTML preview of keyword-injected CV."""
    from agents.cv_studio import build_preview_html
    p = _paths()
    try:
        html = await build_preview_html(
            jd_text=req.jd_text,
            report_id=req.report_id,
            keywords=req.keywords,
            data_dir=p["data_dir"],
            prompts_dir=p["prompts_dir"],
            templates_dir=p["templates_dir"],
        )
        from fastapi.responses import HTMLResponse
        return HTMLResponse(content=html)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cv/download/{cv_id}")
async def download_pdf(cv_id: str):
    """Stream a generated CV PDF file."""
    output_dir = Path(settings.data_dir) / "output"
    matches = list(output_dir.glob(f"*{cv_id}*.pdf"))
    if not matches:
        raise HTTPException(status_code=404, detail="PDF not found")
    return FileResponse(str(matches[0]), media_type="application/pdf", filename=matches[0].name)


# ── Scanner ───────────────────────────────────────────────────────────────────

@router.post("/scan/start")
async def start_scan(req: ScanRequest, background_tasks: BackgroundTasks):
    """Start a portal scan job. Returns job_id for polling."""
    job_id = str(uuid.uuid4())[:8]
    _scan_jobs[job_id] = ScanJobStatus(job_id=job_id, status="running")

    async def run_scan():
        from agents.scanner_v2 import run_portal_scan
        p = _paths()
        try:
            results = await run_portal_scan(
                job_id=job_id,
                levels=req.levels,
                data_dir=p["data_dir"],
                status_registry=_scan_jobs,
            )
            _scan_jobs[job_id].status = "done"
            _scan_jobs[job_id].results = results
        except Exception as e:
            _scan_jobs[job_id].status = "error"
            _scan_jobs[job_id].error = str(e)

    background_tasks.add_task(run_scan)
    return {"job_id": job_id}


@router.websocket("/scan/stream")
async def scan_stream(websocket: WebSocket, job_id: str):
    """Stream scan progress events for a running job."""
    await websocket.accept()
    try:
        last_count = 0
        while True:
            job = _scan_jobs.get(job_id)
            if not job:
                await websocket.send_json({"error": "Job not found"})
                break
            await websocket.send_json(job.model_dump())
            if job.status in ("done", "error"):
                break
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass
    finally:
        try:
            await websocket.close()
        except Exception:
            pass


@router.get("/scan/status/{job_id}", response_model=ScanJobStatus)
async def get_scan_status(job_id: str):
    job = _scan_jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Scan job not found")
    return job


@router.get("/scan/results")
async def get_scan_results(job_id: Optional[str] = None, limit: int = 100):
    if job_id:
        job = _scan_jobs.get(job_id)
        return {"results": job.results if job else [], "job_id": job_id}
    # Return all results from latest job
    if _scan_jobs:
        latest = sorted(_scan_jobs.values(), key=lambda j: j.job_id)[-1]
        return {"results": latest.results[:limit], "job_id": latest.job_id}
    return {"results": [], "job_id": None}


@router.post("/scan/pipeline/add")
async def add_to_pipeline(url: str, company: str = "", title: str = ""):
    add_url(url=url, company=company, title=title, data_dir=settings.data_dir)
    return {"status": "added", "url": url}


@router.get("/scan/pipeline")
async def get_pipeline():
    pending = read_pending(data_dir=settings.data_dir)
    return {"pending": pending, "count": len(pending)}


# ── Tracker ───────────────────────────────────────────────────────────────────

@router.get("/tracker", response_model=list[ApplicationEntry])
async def get_applications(
    status: Optional[str] = None,
    min_score: Optional[float] = None,
    limit: int = 200,
    offset: int = 0,
):
    entries = read_applications(settings.data_dir)
    if status:
        entries = [e for e in entries if e.status.lower() == status.lower()]
    if min_score is not None:
        import re as _re
        def _score(e):
            m = _re.match(r"([\d.]+)/5", e.score)
            return float(m.group(1)) if m else 0.0
        entries = [e for e in entries if _score(e) >= min_score]
    return entries[offset: offset + limit]


@router.get("/tracker/stats", response_model=TrackerStats)
async def get_tracker_stats():
    entries = read_applications(settings.data_dir)
    return get_stats(entries)


@router.get("/tracker/funnel", response_model=FunnelData)
async def get_funnel_data():
    entries = read_applications(settings.data_dir)
    return get_funnel(entries)


@router.get("/tracker/score-trends")
async def get_score_trend_data():
    entries = read_applications(settings.data_dir)
    return {"trends": get_score_trends(entries)}


@router.post("/tracker/{num}/status")
async def update_status(num: int, req: StatusUpdateRequest):
    ok = update_entry(num=num, field="status", value=req.status, data_dir=settings.data_dir)
    if not ok:
        raise HTTPException(status_code=404, detail=f"Entry {num} not found")
    return {"status": "updated"}


@router.post("/tracker/{num}/notes")
async def update_notes(num: int, req: NotesUpdateRequest):
    ok = update_entry(num=num, field="notes", value=req.notes, data_dir=settings.data_dir)
    if not ok:
        raise HTTPException(status_code=404, detail=f"Entry {num} not found")
    return {"status": "updated"}


@router.post("/tracker/merge")
async def trigger_merge():
    result = merge_additions(
        data_dir=settings.data_dir,
        scripts_dir=settings.scripts_dir,
        node_path=settings.node_path,
    )
    return result


# ── Outreach ──────────────────────────────────────────────────────────────────

@router.post("/outreach/find-contacts")
async def find_contacts(req: OutreachRequest):
    from agents.outreach import find_contacts as _find
    p = _paths()
    contacts = await _find(company=req.company, role=req.role)
    return {"contacts": [c.model_dump() for c in contacts]}


@router.post("/outreach/message")
async def generate_message(req: MessageRequest):
    from agents.outreach import generate_message as _gen
    p = _paths()
    result = await _gen(
        contact=req.contact,
        report_id=req.report_id,
        language=req.language,
        data_dir=p["data_dir"],
        prompts_dir=p["prompts_dir"],
    )
    return result.model_dump()


# ── Prepare ───────────────────────────────────────────────────────────────────

@router.post("/prepare/interview")
async def prepare_interview(req: PrepareRequest):
    from agents.researcher import prepare_interview as _prep
    p = _paths()
    result = await _prep(
        company=req.company,
        role=req.role,
        report_id=req.report_id,
        data_dir=p["data_dir"],
        prompts_dir=p["prompts_dir"],
    )
    return result.model_dump()


@router.post("/prepare/company")
async def research_company(req: PrepareRequest):
    from agents.researcher import deep_research
    p = _paths()
    result = await deep_research(
        company=req.company,
        role=req.role,
        prompts_dir=p["prompts_dir"],
    )
    return {"content": result}


@router.get("/prepare/story-bank")
async def get_stories():
    stories = read_stories(settings.data_dir)
    return {"stories": [s.model_dump() for s in stories]}


@router.post("/prepare/story-bank")
async def add_story_endpoint(story: StoryEntry):
    append_story(story=story, data_dir=settings.data_dir)
    return {"status": "added"}


# ── Insights ──────────────────────────────────────────────────────────────────

@router.post("/insights/project")
async def evaluate_project(req: ProjectEvalRequest):
    from agents.portfolio import evaluate_project as _eval
    p = _paths()
    result = await _eval(req=req, prompts_dir=p["prompts_dir"])
    return result.model_dump()


@router.post("/insights/training")
async def evaluate_training(req: TrainingEvalRequest):
    from agents.portfolio import evaluate_training as _eval
    p = _paths()
    result = await _eval(req=req, prompts_dir=p["prompts_dir"])
    return result.model_dump()


@router.get("/insights/analytics")
async def get_analytics():
    entries = read_applications(settings.data_dir)
    stats = get_stats(entries)
    funnel = get_funnel(entries)
    trends = get_score_trends(entries)
    return {
        "stats": stats.model_dump(),
        "funnel": funnel.model_dump(),
        "score_trends": [t.model_dump() for t in trends],
    }


# ── Settings ──────────────────────────────────────────────────────────────────

@router.get("/settings/profile")
async def get_profile():
    profile = read_profile(settings.data_dir)
    return profile


@router.put("/settings/profile")
async def update_profile_endpoint(profile: dict):
    write_profile(profile, settings.data_dir)
    return {"status": "saved"}


@router.get("/settings/cv")
async def get_cv_content():
    return {"content": read_cv(settings.data_dir)}


@router.put("/settings/cv")
async def update_cv_content(body: dict):
    write_cv(body.get("content", ""), settings.data_dir)
    return {"status": "saved"}


@router.get("/settings/portals")
async def get_portals_config():
    return {"raw_yaml": read_portals_raw(str(Path(settings.scripts_dir).parent / "config"))}


@router.put("/settings/portals")
async def update_portals_config(body: PortalsConfig):
    config_dir = str(Path(settings.scripts_dir).parent / "config")
    write_portals_raw(body.raw_yaml, config_dir)
    return {"status": "saved"}


@router.get("/settings/api-keys")
async def get_api_key_status():
    """Return which API providers are configured (without exposing key values)."""
    providers = [
        {"provider": "Anthropic (Claude)", "configured": bool(settings.anthropic_api_key)},
        {"provider": "OpenAI (GPT)", "configured": bool(settings.openai_api_key)},
        {"provider": "Google (Gemini)", "configured": bool(settings.google_api_key)},
        {"provider": "Telegram Bot", "configured": bool(settings.telegram_bot_token)},
    ]
    return providers
