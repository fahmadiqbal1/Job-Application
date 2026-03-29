"""
Human-like browser interaction utilities.

These functions make form-filling appear human (not like an instant bot),
with realistic typing speed, mouse movement, pauses, etc.
"""

import asyncio
import random
from playwright.async_api import Page


async def human_type(
    page: Page, selector: str, text: str, min_delay: int = 50, max_delay: int = 120
) -> None:
    """
    Type text character-by-character with human-like delays.

    Typing speed: 500-900 CPM (characters per minute).
    Delay: 50-120ms per character by default.

    Args:
        page: Playwright page
        selector: CSS selector of input field
        text: Text to type
        min_delay: Minimum delay in ms between characters
        max_delay: Maximum delay in ms between characters
    """
    await page.focus(selector)
    for char in text:
        await page.keyboard.type(char, delay=random.randint(min_delay, max_delay))


async def human_click(page: Page, selector: str) -> None:
    """
    Click with human-like behavior: hover, slight pause, then click.

    Args:
        page: Playwright page
        selector: CSS selector to click
    """
    # Hover over element first
    await page.hover(selector)
    await asyncio.sleep(random.uniform(0.2, 0.4))  # 200-400ms

    # Move mouse slightly to simulate organic movement
    await page.mouse.move(
        random.randint(-5, 5), random.randint(-5, 5)
    )  # ±5px jitter
    await asyncio.sleep(random.uniform(0.1, 0.2))

    # Click
    await page.click(selector)


async def human_scroll(page: Page, amount: int = 300) -> None:
    """
    Scroll the page with human-like behavior.

    Args:
        page: Playwright page
        amount: Pixels to scroll per increment
    """
    scroll_distance = random.randint(amount - 100, amount + 100)
    await page.evaluate(f"window.scrollBy(0, {scroll_distance})")
    await asyncio.sleep(random.uniform(0.3, 0.6))  # 300-600ms pause


async def section_pause() -> None:
    """
    Pause between form sections to simulate reading time.

    Humans read the form before filling each section.
    """
    await asyncio.sleep(random.uniform(0.8, 2.5))  # 800-2500ms


async def variable_delay(min_secs: float = 0.5, max_secs: float = 2.0) -> None:
    """
    Generic variable delay (for inter-section waits, page loads, etc).

    Args:
        min_secs: Minimum delay in seconds
        max_secs: Maximum delay in seconds
    """
    await asyncio.sleep(random.uniform(min_secs, max_secs))


async def simulate_reading_time(page: Page, duration: float = 5.0) -> None:
    """
    Simulate user reading a page — scroll slightly, pause, repeat.

    Args:
        page: Playwright page
        duration: Total reading simulation time in seconds
    """
    start = asyncio.get_event_loop().time()
    while asyncio.get_event_loop().time() - start < duration:
        if random.random() > 0.5:
            await human_scroll(page, amount=150)
        else:
            await asyncio.sleep(random.uniform(1.0, 3.0))
