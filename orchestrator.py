"""Main orchestration pipeline for job application automation."""

import asyncio
import json
import uuid
import logging

from langchain_core.messages import HumanMessage

from state.job_state import JobApplicationState
from state.storage import save_state
from state.run_status import set_phase
from agents.scraper_agent import scraper_agent
from agents.cover_letter_agent import cover_letter_agent
from agents.ats_agent import ats_agent
from agents.application_agent import application_agent
from agents.notifier_agent import notifier_agent
from tools.notifier_tools import send_telegram_direct
from tools.ats_tools import initialize_ats_tools
from api.websocket import (
    emit_phase_start,
    emit_ats_score,
    emit_resume_diff,
    emit_job_found,
)

logger = logging.getLogger(__name__)


async def run_pipeline(keywords: str, chat_id: str, stop_event: asyncio.Event, run_id: str | None = None) -> str:
    """
    Run the full job application pipeline (5 phases).

    Phases:
    1. Scrape — find jobs from enabled portals
    2. ATS Analysis — score resumes and suggest edits
    3. Cover Letters — generate tailored cover letters
    4. Apply — fill forms and request confirmation
    5. Notify — send Telegram/email summaries

    Args:
        keywords: Job search keywords.
        chat_id: Telegram chat ID to send updates to.
        stop_event: asyncio.Event that can be set to gracefully stop the pipeline.
        run_id: Optional run_id (generated if not provided).

    Returns:
        The run_id of this execution.
    """
    if not run_id:
        run_id = str(uuid.uuid4())

    # Initialize state
    state: JobApplicationState = {
        "messages": [HumanMessage(content=f"Find jobs matching: {keywords}")],
        "jobs": [],
        "cover_letters": {},
        "application_results": {},
        "ats_scores": {},  # New: job_id → {"score": int, "missing_keywords": [], ...}
        "resume_edits": {},  # New: job_id → {"edits": [...], "edited_resume": "..."}
        "errors": [],
        "run_id": run_id,
        "search_keywords": keywords,
        "chat_id": chat_id,
    }

    def cfg(limit: int) -> dict:
        """Config helper with recursion limit and thread ID."""
        return {"recursion_limit": limit, "configurable": {"thread_id": run_id}}

    try:
        # Initialize ATS tools (PageIndex, etc.)
        logger.info(f"[{run_id}] Initializing ATS tools...")
        await initialize_ats_tools()

        # ===== PHASE 1: SCRAPE =====
        logger.info(f"[{run_id}] Phase 1: Starting scrape...")
        set_phase("scrape", "Searching for jobs...")
        await emit_phase_start("scrape", "Searching for jobs...")
        await send_telegram_direct(chat_id, f"🔍 Searching for: *{keywords}*...")

        state = await scraper_agent.ainvoke(state, config=cfg(10))
        save_state(state)

        if stop_event.is_set():
            await send_telegram_direct(chat_id, "⛔ Run stopped after scraping.")
            return run_id

        if not state.get("jobs"):
            await send_telegram_direct(
                chat_id, "❌ No jobs found. Try different keywords."
            )
            return run_id

        job_count = len(state["jobs"])
        logger.info(f"[{run_id}] Phase 1 complete: Found {job_count} jobs")
        for job in state["jobs"]:
            await emit_job_found(job)

        # ===== PHASE 2: ATS ANALYSIS =====
        logger.info(f"[{run_id}] Phase 2: Analyzing ATS compatibility...")
        set_phase("ats", "Analyzing resume vs job requirements...")
        await emit_phase_start("ats", "Analyzing resume vs job requirements...")

        # Prepare ATS agent state with guidance message
        ats_state = {
            **state,
            "messages": state.get("messages", [])
            + [
                HumanMessage(
                    content="""Analyze each job for ATS compatibility:
1. Use analyze_job_requirements() on the job description
2. Use score_resume_vs_jd() to score the resume against requirements
3. If score < 80, use generate_resume_edits() to suggest keyword improvements
4. Update state["ats_scores"] with scores and state["resume_edits"] with edits

Work through all jobs and return updated state."""
                )
            ],
            "ats_scores": state.get("ats_scores", {}),
            "resume_edits": state.get("resume_edits", {}),
        }

        ats_state = await ats_agent.ainvoke(ats_state, config=cfg(30))
        # Selective merge — preserve messages list, only copy ats_scores and resume_edits
        state["ats_scores"] = ats_state.get("ats_scores", state.get("ats_scores", {}))
        state["resume_edits"] = ats_state.get("resume_edits", state.get("resume_edits", {}))
        save_state(state)

        if stop_event.is_set():
            await send_telegram_direct(chat_id, "⛔ Run stopped during ATS analysis.")
            return run_id

        ats_count = len([s for s in state.get("ats_scores", {}).values() if s])
        logger.info(f"[{run_id}] Phase 2 complete: Analyzed {ats_count} jobs")

        # Broadcast ATS scores to web dashboard
        for job_id, score_data in state.get("ats_scores", {}).items():
            if score_data:
                try:
                    await emit_ats_score(
                        job_id,
                        score_data.get("score", 0),
                        score_data.get("missing_keywords", []),
                    )
                except Exception as e:
                    logger.warning(f"Failed to emit ATS score for {job_id}: {e}")

        # Broadcast resume diffs to web dashboard
        for job_id, edits_data in state.get("resume_edits", {}).items():
            if edits_data and edits_data.get("edits"):
                try:
                    await emit_resume_diff(
                        job_id,
                        edits_data.get("original_resume", ""),
                        edits_data.get("edited_resume", ""),
                    )
                except Exception as e:
                    logger.warning(f"Failed to emit resume diff for {job_id}: {e}")

        await send_telegram_direct(
            chat_id,
            f"📊 ATS analysis complete. Generating cover letters...",
        )

        # ===== PHASE 3: COVER LETTERS =====
        logger.info(f"[{run_id}] Phase 3: Generating cover letters...")
        set_phase("cover_letter", "Writing tailored cover letters...")
        await emit_phase_start("cover_letter", "Writing tailored cover letters...")

        state = await cover_letter_agent.ainvoke(state, config=cfg(25))
        save_state(state)

        if stop_event.is_set():
            await send_telegram_direct(chat_id, "⛔ Run stopped after cover letters.")
            return run_id

        cover_count = len([v for v in state.get("cover_letters", {}).values() if v])
        logger.info(f"[{run_id}] Phase 3 complete: Generated {cover_count} cover letters")
        await send_telegram_direct(
            chat_id, f"✍️ Generated {cover_count} cover letters. Starting applications..."
        )

        # ===== PHASE 4: APPLY =====
        logger.info(f"[{run_id}] Phase 4: Starting applications...")
        set_phase("apply", "Filling forms and requesting confirmations...")
        await emit_phase_start("apply", "Filling forms and requesting confirmations...")
        await send_telegram_direct(
            chat_id, "📋 Confirm each application (YES or SKIP):"
        )
        state = await application_agent.ainvoke(state, config=cfg(50))
        save_state(state)

        if stop_event.is_set():
            await send_telegram_direct(chat_id, "⛔ Run stopped during applications.")
            return run_id

        applied_count = len(
            [v for v in state.get("application_results", {}).values() if v]
        )
        logger.info(f"[{run_id}] Phase 4 complete: Applied to {applied_count} jobs")

        # ===== PHASE 5: NOTIFY =====
        logger.info(f"[{run_id}] Phase 5: Sending final notifications...")
        set_phase("notify", "Sending summaries...")
        await emit_phase_start("notify", "Sending summaries...")
        state = await notifier_agent.ainvoke(state, config=cfg(10))
        save_state(state)

        await send_telegram_direct(
            chat_id, f"✅ Pipeline complete. Applied to {applied_count} jobs."
        )

        logger.info(f"[{run_id}] Pipeline complete")

    except Exception as e:
        logger.error(f"[{run_id}] Pipeline error: {e}", exc_info=True)
        await send_telegram_direct(chat_id, f"❌ Error: {str(e)}")
        save_state(state)

    return run_id
