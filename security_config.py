"""Anti-detection and human-like behavior configuration for web automation."""

import asyncio
import random
from typing import Any


class SecurityConfig:
    """Centralized configuration for anti-bot detection measures.

    Randomizes user agents, viewport sizes, and provides human-like delay patterns
    to avoid detection by job board security systems.
    """

    # Realistic user agent strings across browsers and OS
    # Updated as of Q1 2026 with current versions
    USER_AGENTS = [
        # Chrome on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        # Chrome on macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        # Chrome on Linux
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        # Firefox on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
        # Firefox on macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:133.0) Gecko/20100101 Firefox/133.0",
        # Edge on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
    ]

    # Common viewport sizes matching real user distributions
    VIEWPORTS = [
        {"width": 1920, "height": 1080},  # 24% of traffic
        {"width": 1366, "height": 768},   # 20% of traffic
        {"width": 1440, "height": 900},   # 12% of traffic
        {"width": 1536, "height": 864},   # 8% of traffic
        {"width": 1280, "height": 720},   # 6% of traffic
        {"width": 1600, "height": 900},   # 5% of traffic
        {"width": 2560, "height": 1440},  # 3% of traffic (4K)
    ]

    @staticmethod
    def get_random_user_agent() -> str:
        """Return a random, realistic user agent string.

        Returns:
            A user agent string matching current browser/OS distribution.
        """
        return random.choice(SecurityConfig.USER_AGENTS)

    @staticmethod
    def get_random_viewport() -> dict[str, int]:
        """Return a random viewport matching common screen resolutions.

        Returns:
            Dict with 'width' and 'height' keys.
        """
        return random.choice(SecurityConfig.VIEWPORTS).copy()

    @staticmethod
    async def human_delay(min_ms: int = 500, max_ms: int = 2000) -> None:
        """Sleep for a randomized duration to simulate human reading time.

        Args:
            min_ms: Minimum delay in milliseconds (default 500ms).
            max_ms: Maximum delay in milliseconds (default 2000ms).
        """
        delay_seconds = random.uniform(min_ms / 1000, max_ms / 1000)
        await asyncio.sleep(delay_seconds)

    @staticmethod
    async def simulate_human_scroll(page: Any) -> None:
        """Simulate human-like scrolling behavior on a page.

        Scrolls in incremental steps with pauses between them, rather than
        jumping to the bottom instantly.

        Args:
            page: Playwright page object.
        """
        # Get page height
        height = await page.evaluate("document.documentElement.scrollHeight")

        # Scroll in random increments
        current_scroll = 0
        while current_scroll < height:
            increment = random.randint(200, 400)
            current_scroll += increment

            # Scroll to position
            await page.evaluate(f"window.scrollBy(0, {increment})")

            # Random pause between scrolls
            await asyncio.sleep(random.uniform(0.3, 0.8))

        # Scroll back to top
        await page.evaluate("window.scrollTo(0, 0)")
