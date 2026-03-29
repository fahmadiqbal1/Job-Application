"""Browser automation tools for form filling and submission."""

import asyncio
import json
import random
from pathlib import Path

from langchain.tools import tool
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

from config.portals import PORTALS
from config.settings import settings


@tool("fill_application_form", parse_docstring=True)
async def fill_application_form(
    job_id: str,
    portal: str,
    job_url: str,
    cover_letter: str,
    resume_path: str = None,
) -> str:
    """Fill an application form on a job portal using Playwright.

    Args:
        job_id: Job identifier (for screenshots).
        portal: Portal name ('hiredly' or 'jobstreet').
        job_url: Direct URL to the job/application page.
        cover_letter: Cover letter text to paste.
        resume_path: Path to resume PDF (uses config default if None).

    Returns:
        JSON string with form fill status.
    """
    if not resume_path:
        resume_path = settings.resume_path

    portal_config = PORTALS.get(portal)
    if not portal_config:
        return json.dumps({"error": f"Unknown portal: {portal}"})

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1366, "height": 768},
        )
        page = await context.new_page()

        try:
            await page.goto(job_url, wait_until="networkidle")
            await page.wait_for_timeout(random.randint(1000, 2000))

            # Fill cover letter field
            cover_letter_field = portal_config.get("cover_letter_field")
            if cover_letter_field:
                try:
                    await page.fill(cover_letter_field, cover_letter)
                    await page.wait_for_timeout(500)
                except Exception as e:
                    return json.dumps(
                        {
                            "error": f"Failed to fill cover letter field: {e}",
                            "job_id": job_id,
                            "portal": portal,
                        }
                    )

            # Upload resume
            resume_upload_field = portal_config.get("resume_upload")
            if resume_upload_field and Path(resume_path).exists():
                try:
                    file_input = await page.query_selector(resume_upload_field)
                    if file_input:
                        await file_input.set_input_files(resume_path)
                        await page.wait_for_timeout(1000)
                except Exception as e:
                    return json.dumps(
                        {
                            "error": f"Failed to upload resume: {e}",
                            "job_id": job_id,
                            "portal": portal,
                        }
                    )

            # Take screenshot for verification
            screenshot_dir = Path(settings.screenshots_dir)
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            await page.screenshot(path=f"{screenshot_dir}/form_{job_id}_{portal}.png")

            return json.dumps(
                {
                    "status": "form_filled",
                    "job_id": job_id,
                    "portal": portal,
                    "screenshot": f"form_{job_id}_{portal}.png",
                }
            )

        except Exception as e:
            return json.dumps(
                {"error": f"Form fill error: {e}", "job_id": job_id, "portal": portal}
            )
        finally:
            await browser.close()


@tool("take_screenshot", parse_docstring=True)
async def take_screenshot(job_id: str, portal: str, label: str = "form") -> str:
    """Take a screenshot of the current page state (for debugging).

    Args:
        job_id: Job identifier.
        portal: Portal name.
        label: Screenshot label (default: 'form').

    Returns:
        JSON string with screenshot path.
    """
    # Note: This tool is informational. In a real scenario, the browser would
    # still be open from fill_application_form. For now, return a placeholder.
    screenshot_dir = Path(settings.screenshots_dir)
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{label}_{job_id}_{portal}.png"

    return json.dumps(
        {
            "screenshot": filename,
            "job_id": job_id,
            "portal": portal,
        }
    )


@tool("submit_form", parse_docstring=True)
async def submit_form(job_id: str, portal: str, job_url: str) -> str:
    """Submit an application form.

    Args:
        job_id: Job identifier.
        portal: Portal name.
        job_url: Job URL (for context).

    Returns:
        JSON string with submission status.
    """
    portal_config = PORTALS.get(portal)
    if not portal_config:
        return json.dumps({"error": f"Unknown portal: {portal}"})

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1366, "height": 768},
        )
        page = await context.new_page()

        try:
            await page.goto(job_url, wait_until="networkidle")
            await page.wait_for_timeout(1000)

            # Click submit button
            submit_button = portal_config.get("submit_button")
            if submit_button:
                try:
                    await page.click(submit_button)
                    await page.wait_for_timeout(2000)
                except PlaywrightTimeoutError:
                    return json.dumps(
                        {
                            "error": f"Submit button selector not found: {submit_button}",
                            "job_id": job_id,
                            "portal": portal,
                        }
                    )

            # Check for confirmation
            confirmation_selector = portal_config.get("confirmation")
            if confirmation_selector:
                try:
                    await page.wait_for_selector(confirmation_selector, timeout=10000)
                    return json.dumps(
                        {
                            "status": "submitted",
                            "job_id": job_id,
                            "portal": portal,
                            "confirmation": True,
                        }
                    )
                except PlaywrightTimeoutError:
                    # Might still have submitted, check URL change
                    return json.dumps(
                        {
                            "status": "submitted_unknown",
                            "job_id": job_id,
                            "portal": portal,
                            "confirmation": False,
                        }
                    )

            return json.dumps(
                {"status": "submitted", "job_id": job_id, "portal": portal}
            )

        except Exception as e:
            return json.dumps(
                {"error": f"Submission error: {e}", "job_id": job_id, "portal": portal}
            )
        finally:
            await browser.close()
