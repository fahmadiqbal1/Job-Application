"""Daily job search scheduler — runs at 7 AM (or configured hour) each day."""

import asyncio
import logging
from datetime import datetime

from config.settings import settings
from state.run_status import get_active_run
from orchestrator import run_pipeline

logger = logging.getLogger(__name__)


async def schedule_daily_run():
    """
    Async scheduler that runs the job pipeline at the configured hour each day.

    Checks settings.daily_search_keywords — if blank, skips scheduling.
    Runs at settings.daily_run_hour (default: 7 AM).

    This task runs in the background alongside Telegram bot and FastAPI server.
    """
    if not settings.daily_search_keywords:
        logger.info(
            "Daily scheduling disabled (DAILY_SEARCH_KEYWORDS is empty)"
        )
        return

    target_hour = settings.daily_run_hour
    logger.info(f"Daily scheduler started — will run at {target_hour}:00 each day")

    while True:
        try:
            now = datetime.now()
            next_run = now.replace(hour=target_hour, minute=0, second=0, microsecond=0)

            # If target hour has already passed today, schedule for tomorrow
            if now > next_run:
                next_run = next_run.replace(day=next_run.day + 1)

            wait_seconds = (next_run - now).total_seconds()

            logger.info(
                f"Next daily run scheduled for {next_run.strftime('%Y-%m-%d %H:%M:%S')} (in {wait_seconds:.0f} seconds)"
            )

            # Sleep until the target time
            await asyncio.sleep(wait_seconds)

            # Check if a run is already active
            if get_active_run():
                logger.info("Daily run skipped — pipeline already active")
                continue

            # Run the daily pipeline
            logger.info("⏰ Starting daily job search...")
            keywords = settings.daily_search_keywords
            stop_event = asyncio.Event()

            try:
                run_id = await run_pipeline(
                    keywords=keywords,
                    chat_id="scheduler",  # Mark as scheduler-initiated
                    stop_event=stop_event,
                )
                logger.info(f"✓ Daily run {run_id} completed")

                # Emit daily digest to web dashboard via WebSocket
                try:
                    from api.websocket import manager
                    import json

                    digest = {
                        "type": "daily_digest",
                        "data": {
                            "run_at": now.isoformat(),
                            "keywords": keywords,
                            "run_id": run_id,
                            "status": "completed",
                        },
                    }
                    await manager.broadcast(json.dumps(digest))
                except Exception as e:
                    logger.warning(f"Failed to emit daily digest: {e}")

            except Exception as e:
                logger.error(f"Daily run failed: {e}", exc_info=True)

        except Exception as e:
            logger.error(f"Scheduler error: {e}", exc_info=True)
            # Wait 1 minute before retrying scheduler loop
            await asyncio.sleep(60)
