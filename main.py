"""Main entry point for the job application bot."""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import settings
from config.portals import verify_selectors
from bot.telegram_bot import TelegramBot, set_main_loop
from tools.notifier_tools import set_bot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    """Main async entry point."""
    logger.info("Starting Job Application Bot...")

    # Get the current event loop
    loop = asyncio.get_event_loop()
    set_main_loop(loop)

    # Initialize Telegram bot
    bot = TelegramBot()

    try:
        # Verify selectors on startup
        logger.info("Verifying portal selectors...")
        try:
            await verify_selectors("hiredly")
        except Exception as e:
            logger.warning(f"Hiredly selector verification failed: {e}")

        try:
            await verify_selectors("jobstreet")
        except Exception as e:
            logger.warning(f"JobStreet selector verification failed: {e}")

        # Start Telegram bot
        logger.info("Starting Telegram bot...")
        await bot.start()

        logger.info("Bot started successfully. Listening for commands...")

        # Keep the bot running
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        try:
            await bot.stop()
        except Exception as e:
            logger.error(f"Error stopping bot: {e}")
        logger.info("Bot stopped.")


if __name__ == "__main__":
    asyncio.run(main())
