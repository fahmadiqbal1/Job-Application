"""Main entry point for the job application bot + web dashboard."""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

from config.settings import settings
from config.portals import verify_selectors
from bot.telegram_bot import TelegramBot
from state.confirmation import set_main_loop
from api.routes import router as api_router
from scheduler import schedule_daily_run

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# Create FastAPI app
app = FastAPI(
    title="Job Application Dashboard",
    description="Automated job application bot with web dashboard",
    version="1.0.0",
)

# Include API routes
app.include_router(api_router)


# SPA fallback — serve React from static files
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """Serve React SPA with fallback to index.html for client-side routing."""
    frontend_dist = Path(__file__).parent / "frontend" / "dist"

    # If file exists in dist, serve it
    file_path = frontend_dist / full_path
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)

    # Otherwise serve index.html (SPA routing)
    index_html = frontend_dist / "index.html"
    if index_html.exists():
        return FileResponse(index_html)

    # Fallback if dist doesn't exist
    return {"error": "Frontend not built. Run: cd frontend && npm run build"}


# Mount static files if they exist
frontend_dist = Path(__file__).parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=frontend_dist / "assets"), name="assets")


async def run_telegram_bot():
    """Run Telegram bot on the same event loop."""
    bot = TelegramBot()

    try:
        logger.info("Starting Telegram bot...")
        await bot.start()
        logger.info("Telegram bot started")

        # Keep bot running until cancelled
        while True:
            await asyncio.sleep(1)

    except asyncio.CancelledError:
        logger.info("Telegram bot cancelled")
        raise
    except Exception as e:
        logger.error(f"Telegram bot error: {e}", exc_info=True)
    finally:
        try:
            await bot.stop()
        except Exception as e:
            logger.error(f"Error stopping bot: {e}")
        logger.info("Telegram bot stopped")


async def run_webserver():
    """Run FastAPI web server on the same event loop."""
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        loop="none",  # Use existing event loop instead of creating a new one
    )
    server = uvicorn.Server(config)

    try:
        logger.info("Starting web server on http://0.0.0.0:8000")
        await server.serve()
    except asyncio.CancelledError:
        logger.info("Web server cancelled")
    except Exception as e:
        logger.error(f"Web server error: {e}", exc_info=True)


async def main():
    """Main async entry point — run Telegram bot and web server concurrently."""
    logger.info("Starting Job Application System...")

    # Get and store the event loop for Telegram bot
    loop = asyncio.get_event_loop()
    set_main_loop(loop)

    try:
        # Verify a few key portals on startup
        logger.info("Verifying portal selectors...")
        for portal in ["hiredly", "jobstreet", "linkedin"]:
            try:
                await verify_selectors(portal)
                logger.info(f"✓ {portal} selectors OK")
            except Exception as e:
                logger.warning(f"{portal} selector verification failed: {e}")

        # Run Telegram bot, web server, and daily scheduler concurrently
        logger.info("Starting services...")
        await asyncio.gather(
            run_telegram_bot(),
            run_webserver(),
            schedule_daily_run(),
            return_exceptions=True,
        )

    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        logger.info("System stopped.")


if __name__ == "__main__":
    asyncio.run(main())
