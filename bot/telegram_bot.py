"""Telegram bot with long-polling and command handlers."""

import asyncio
import logging
import uuid

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

from config.settings import settings
from state.confirmation import resolve_confirmation, get_main_loop, set_main_loop
from state.run_status import start_run, get_active_run, clear_run

logger = logging.getLogger(__name__)


class TelegramBot:
    """Telegram bot manager."""

    def __init__(self):
        self.application = None
        self.bot = None

    async def start(self):
        """Initialize and start the bot."""
        self.application = Application.builder().token(settings.telegram_bot_token).build()

        # Store bot reference globally for notifier_tools
        self.bot = self.application.bot
        from tools.notifier_tools import set_bot

        set_bot(self.bot)

        # Register handlers
        self.application.add_handler(CommandHandler("start", self._cmd_start))
        self.application.add_handler(CommandHandler("search", self._cmd_search))
        self.application.add_handler(CommandHandler("status", self._cmd_status))
        self.application.add_handler(CommandHandler("stop", self._cmd_stop))
        self.application.add_handler(CommandHandler("jobs", self._cmd_jobs))
        self.application.add_handler(CommandHandler("apply", self._cmd_apply))
        self.application.add_handler(CallbackQueryHandler(self._handle_callback))

        # Start polling
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling(allowed_updates=Update.ALL_TYPES)

        logger.info("Telegram bot started (polling)")

    async def stop(self):
        """Stop the bot gracefully."""
        await self.application.updater.stop()
        await self.application.stop()
        await self.application.shutdown()

    async def _cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command."""
        await update.message.reply_text(
            "🤖 Job Application Bot Started!\n\n"
            "Commands:\n"
            "/search <keywords> — Find jobs\n"
            "/status — Check current run status\n"
            "/stop — Stop current run\n"
            "/jobs — List jobs from last run\n"
            "/apply <job_id> — Apply to a specific job"
        )

    async def _cmd_search(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /search <keywords> command."""
        chat_id = str(update.effective_chat.id)
        keywords = " ".join(context.args) if context.args else "program manager"

        # Start pipeline in main loop
        main_loop = get_main_loop()
        if main_loop:
            run_id = str(uuid.uuid4())
            active = start_run(run_id, keywords, chat_id)

            # Run pipeline asynchronously without blocking telegram updates
            asyncio.run_coroutine_threadsafe(
                _run_pipeline_wrapper(keywords, chat_id, active.stop_event), main_loop
            )
            await update.message.reply_text(f"🔍 Starting search for: *{keywords}*", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ Bot not fully initialized")

    async def _cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /status command."""
        run = get_active_run()
        if run:
            await update.message.reply_text(
                f"Run in progress:\n"
                f"Keywords: {run.keywords}\n"
                f"Phase: {run.phase}\n"
                f"Run ID: {run.run_id}"
            )
        else:
            await update.message.reply_text("No active run. Use /search to start.")

    async def _cmd_stop(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /stop command."""
        run = get_active_run()
        if run:
            run.stop_event.set()
            await update.message.reply_text("⛔ Stop signal sent to current run.")
        else:
            await update.message.reply_text("No active run to stop.")

    async def _cmd_jobs(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /jobs command — list jobs from last run."""
        from state.storage import load_latest_state

        state = load_latest_state()
        if not state or not state.get("jobs"):
            await update.message.reply_text("No jobs found. Use /search first.")
            return

        jobs_text = "*Jobs from last run:*\n\n"
        for job in state["jobs"][:10]:  # Limit to 10
            status_emoji = {
                "scraped": "📄",
                "ats": "🔍",
                "cover_written": "✍️",
                "confirmed": "✅",
                "applied": "📮",
                "skipped": "⏭",
                "failed": "❌",
            }.get(job.get("status", "unknown"), "❓")

            jobs_text += f"{status_emoji} *{job['title']}* @ {job['company']}\n"
            jobs_text += f"   ID: `{job['job_id']}` | Portal: {job['portal']}\n\n"

        await update.message.reply_text(jobs_text, parse_mode="Markdown")

    async def _cmd_apply(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /apply <job_id> command."""
        if not context.args:
            await update.message.reply_text("Usage: /apply <job_id>")
            return

        job_id = context.args[0]
        chat_id = str(update.effective_chat.id)

        from state.storage import load_latest_state

        state = load_latest_state()
        if not state:
            await update.message.reply_text("No previous run found. Use /search first.")
            return

        job = next((j for j in state.get("jobs", []) if j["job_id"] == job_id), None)
        if not job:
            await update.message.reply_text(f"Job `{job_id}` not found.")
            return

        cover = state.get("cover_letters", {}).get(job_id) if state.get("cover_letters") else None
        if not cover:
            await update.message.reply_text(f"No cover letter for `{job_id}`. Run /search first.")
            return

        # Trigger single-job application in main loop
        main_loop = get_main_loop()
        if main_loop:
            asyncio.run_coroutine_threadsafe(
                _apply_single_job(job_id, chat_id, state), main_loop
            )
            await update.message.reply_text(f"Applying to job `{job_id}`...", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ Bot not fully initialized")

    async def _handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle inline button callbacks (YES/SKIP confirmation)."""
        query = update.callback_query
        await query.answer()

        action, job_id = query.data.split(":", 1)  # "YES:abc123" or "SKIP:abc123"

        # Use shared confirmation state
        resolved = resolve_confirmation(job_id, action)
        if resolved:
            await query.edit_message_text(text=f"Response recorded: {action}")
        else:
            await query.edit_message_text(text="This job is no longer pending confirmation.")


async def _run_pipeline_wrapper(keywords: str, chat_id: str, stop_event: asyncio.Event) -> None:
    """Wrapper to run the pipeline and capture exceptions."""
    try:
        from orchestrator import run_pipeline

        await run_pipeline(keywords, chat_id, stop_event)
        clear_run()
    except Exception as e:
        logger.error(f"Pipeline error: {e}", exc_info=True)
        from tools.notifier_tools import send_telegram_direct

        await send_telegram_direct(chat_id, f"❌ Error: {str(e)}")
        clear_run()


async def _apply_single_job(job_id: str, chat_id: str, state: dict) -> None:
    """Apply to a single job without re-scraping."""
    try:
        from agents.application_agent import application_agent
        from state.storage import save_state

        job = next((j for j in state["jobs"] if j["job_id"] == job_id), None)
        if not job:
            from tools.notifier_tools import send_telegram_direct

            await send_telegram_direct(chat_id, f"Job `{job_id}` not found.")
            return

        # Run ApplicationAgent on this single job
        single_job_state = {**state, "jobs": [job], "chat_id": chat_id}
        config = {"recursion_limit": 50, "configurable": {"thread_id": job_id}}

        result = await application_agent.ainvoke(single_job_state, config=config)
        save_state(result)

        from tools.notifier_tools import send_telegram_direct

        await send_telegram_direct(chat_id, f"✅ Applied to job `{job_id}`")

    except Exception as e:
        logger.error(f"Single job application error: {e}", exc_info=True)
        from tools.notifier_tools import send_telegram_direct

        await send_telegram_direct(chat_id, f"❌ Error applying to job: {str(e)}")
