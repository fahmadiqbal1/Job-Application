"""
Persistent Playwright browser session (singleton).

All scraping and form-filling tools use this shared browser instance,
enabling real-time screenshot streaming and consistent session state.

This replaces the per-call browser creation that existed in browser_tools.py.
"""

import asyncio
import base64
import logging
from pathlib import Path
from typing import Optional

from playwright.async_api import async_playwright, Browser, Page, BrowserContext

from config.settings import settings
from api.websocket import emit_screenshot

logger = logging.getLogger(__name__)


class BrowserSession:
    """Singleton browser session with screenshot streaming."""

    def __init__(self):
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self._screenshot_loop_task: Optional[asyncio.Task] = None
        self._current_action: str = "idle"

    async def initialize(self) -> None:
        """Launch the browser and create the context + page."""
        from playwright.async_api import async_playwright

        p = await async_playwright().start()
        self.browser = await p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        self.context = await self.browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1366, "height": 768},
        )
        self.page = await self.context.new_page()
        logger.info("BrowserSession initialized")

    async def start_screenshot_loop(self) -> None:
        """Start the background screenshot streaming task."""
        if self._screenshot_loop_task is None:
            self._screenshot_loop_task = asyncio.create_task(self._screenshot_loop())
            logger.info("Screenshot loop started")

    async def stop_screenshot_loop(self) -> None:
        """Stop the screenshot streaming task."""
        if self._screenshot_loop_task:
            self._screenshot_loop_task.cancel()
            try:
                await self._screenshot_loop_task
            except asyncio.CancelledError:
                pass
            self._screenshot_loop_task = None
            logger.info("Screenshot loop stopped")

    async def _screenshot_loop(self) -> None:
        """Background task: take screenshots every 1 second and broadcast."""
        while True:
            try:
                if self.page:
                    screenshot_bytes = await self.page.screenshot(
                        type="jpeg", quality=60
                    )
                    frame_b64 = base64.b64encode(screenshot_bytes).decode()
                    url = self.page.url if self.page else "about:blank"
                    await emit_screenshot(frame_b64, url, self._current_action)
                await asyncio.sleep(1.0)  # 1 FPS
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.debug(f"Screenshot loop error: {e}")
                await asyncio.sleep(1.0)

    def set_action(self, label: str) -> None:
        """Set the current action label for the screenshot stream."""
        self._current_action = label

    async def get_page(self) -> Page:
        """Get the current page object."""
        if not self.page:
            raise RuntimeError("BrowserSession not initialized")
        return self.page

    async def close(self) -> None:
        """Close the browser and clean up."""
        await self.stop_screenshot_loop()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        logger.info("BrowserSession closed")


# Global singleton instance
_session: Optional[BrowserSession] = None
_session_lock = asyncio.Lock()


async def get_session() -> BrowserSession:
    """Get or create the global BrowserSession singleton (thread-safe)."""
    global _session
    if _session is not None:
        return _session

    async with _session_lock:
        if _session is None:
            _session = BrowserSession()
            await _session.initialize()
        return _session


async def close_session() -> None:
    """Close the global session (called at shutdown)."""
    global _session
    if _session:
        await _session.close()
        _session = None
