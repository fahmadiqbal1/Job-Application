"""Job scraping tools using Playwright."""

import asyncio
import hashlib
import json
import random
from typing import Any

from langchain.tools import tool
from playwright.async_api import async_playwright, Page, TimeoutError as PlaywrightTimeoutError

from config.portals import PORTALS


def _job_id(url: str) -> str:
    """Generate stable short job ID from URL."""
    return hashlib.md5(url.encode()).hexdigest()[:8]


@tool("scrape_hiredly_jobs", parse_docstring=True)
async def scrape_hiredly_jobs(
    keywords: str, location: str = "Malaysia", max_results: int = 15
) -> str:
    """Scrape job listings from Hiredly.my using Playwright.

    Args:
        keywords: Job title keywords, e.g. 'AI Program Manager'.
        location: City or country filter.
        max_results: Maximum listings to return (cap: 20).

    Returns:
        JSON string of job listings or error dict.
    """
    return await _scrape_portal("hiredly", keywords, location, max_results)


@tool("scrape_jobstreet_jobs", parse_docstring=True)
async def scrape_jobstreet_jobs(
    keywords: str, location: str = "Malaysia", max_results: int = 15
) -> str:
    """Scrape job listings from JobStreet Malaysia using Playwright.

    Args:
        keywords: Job title keywords.
        location: City or country filter.
        max_results: Maximum listings to return.

    Returns:
        JSON string of job listings or error dict.
    """
    return await _scrape_portal("jobstreet", keywords, location, min(max_results, 20))


async def _scrape_portal(portal: str, keywords: str, location: str, max_results: int) -> str:
    """Internal scraper for a single portal."""
    portal_config = PORTALS.get(portal)
    if not portal_config:
        return json.dumps({"error": f"Unknown portal: {portal}"})

    search_url = portal_config["search_url"].format(keywords=keywords, location=location)

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
            await page.goto(search_url, wait_until="networkidle")
            await page.wait_for_timeout(random.randint(1000, 2000))

            # Wait for job cards
            try:
                await page.wait_for_selector(
                    portal_config["job_cards"], timeout=15000
                )
            except PlaywrightTimeoutError:
                await page.screenshot(path=f"screenshots/error_{portal}_cards.png")
                return json.dumps(
                    {
                        "error": f"Job cards selector '{portal_config['job_cards']}' not found",
                        "portal": portal,
                    }
                )

            # Scroll to load more if needed
            for _ in range(3):
                await page.evaluate("window.scrollBy(0, window.innerHeight)")
                await page.wait_for_timeout(random.randint(500, 1000))

            # Extract job cards
            jobs = []
            cards = await page.query_selector_all(portal_config["job_cards"])
            for card in cards[: min(max_results, len(cards))]:
                try:
                    title_elem = await card.query_selector(portal_config["title"])
                    company_elem = await card.query_selector(portal_config["company"])
                    url_attr = await card.get_attribute("href")

                    if not all([title_elem, company_elem, url_attr]):
                        continue

                    title = await title_elem.inner_text()
                    company = await company_elem.inner_text()
                    # Ensure absolute URL
                    if not url_attr.startswith("http"):
                        base = "https://hiredly.com" if portal == "hiredly" else "https://jobstreet.com.my"
                        url_attr = base + url_attr

                    # Get description snippet from page
                    await card.click()
                    await page.wait_for_timeout(500)
                    description_text = await page.inner_text("body") or "Job description not available"
                    description_text = description_text[:500]  # Limit to 500 chars

                    jobs.append(
                        {
                            "job_id": _job_id(url_attr),
                            "title": title.strip(),
                            "company": company.strip(),
                            "url": url_attr,
                            "portal": portal,
                            "description": description_text,
                            "location": location,
                            "status": "scraped",
                        }
                    )
                except Exception as e:
                    # Skip this card, continue scraping
                    continue

            return json.dumps(jobs)

        except Exception as e:
            return json.dumps({"error": str(e), "portal": portal})
        finally:
            await browser.close()


@tool("filter_jobs", parse_docstring=True)
def filter_jobs(jobs_json: str, exclude_keywords: str = "") -> str:
    """Deduplicate and filter scraped job listings.

    Args:
        jobs_json: JSON array of raw job listings.
        exclude_keywords: Comma-separated keywords to exclude (case-insensitive).

    Returns:
        JSON string of filtered, deduplicated jobs.
    """
    try:
        jobs = json.loads(jobs_json)
    except json.JSONDecodeError:
        return json.dumps({"error": "Invalid JSON input"})

    if not isinstance(jobs, list):
        return json.dumps({"error": "Expected JSON array"})

    exclude_set = {kw.strip().lower() for kw in exclude_keywords.split(",") if kw.strip()}

    # Deduplicate by job_id
    seen = {}
    for job in jobs:
        if job.get("job_id") not in seen:
            seen[job["job_id"]] = job

    # Filter by exclude keywords
    filtered = []
    for job in seen.values():
        title_lower = (job.get("title") or "").lower()
        if not any(kw in title_lower for kw in exclude_set):
            filtered.append(job)

    return json.dumps(filtered)
