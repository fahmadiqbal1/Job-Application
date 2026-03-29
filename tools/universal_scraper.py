"""
Universal job scraper that works on any job portal.

Routes through: known portals → cached selectors → LLM discovery.
Replaces the two separate scraper tools (scrape_hiredly, scrape_jobstreet).
"""

import asyncio
import hashlib
import json
import logging
import random
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from langchain.tools import tool
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from config.portals import PORTALS
from tools.browser_session import get_session

logger = logging.getLogger(__name__)


# Portal cache file — auto-discovered selectors per domain
PORTAL_CACHE_PATH = Path("config/portal_cache.json")


def _job_id(url: str) -> str:
    """Generate stable short job ID from URL."""
    return hashlib.md5(url.encode()).hexdigest()[:8]


def _load_portal_cache() -> dict:
    """Load cached selectors from disk."""
    if PORTAL_CACHE_PATH.exists():
        try:
            import orjson
            return orjson.loads(PORTAL_CACHE_PATH.read_bytes())
        except Exception as e:
            logger.warning(f"Failed to load portal cache: {e}")
    return {}


def _save_portal_cache(cache: dict) -> None:
    """Save cache to disk."""
    try:
        import orjson
        PORTAL_CACHE_PATH.write_bytes(orjson.dumps(cache, option=orjson.OPT_INDENT_2))
    except Exception as e:
        logger.warning(f"Failed to save portal cache: {e}")


def _get_domain(url: str) -> str:
    """Extract domain from URL for caching."""
    return urlparse(url).netloc.lower()


def _domain_to_known_portal(domain: str) -> Optional[str]:
    """Map a domain to a known portal name, or None."""
    domain_lower = domain.lower()
    # Simple heuristic mapping
    portal_mappings = {
        "hiredly": "hiredly",
        "jobstreet": "jobstreet",
        "jobsdb": "jobsdb",
        "kalibrr": "kalibrr",
        "maukerja": "maukerja",
        "linkedin": "linkedin",
        "indeed": "indeed",
        "glassdoor": "glassdoor",
        "monster": "monster",
        "dice": "dice",
        "reed": "reed",
        "remotive": "remotive",
        "weworkremotely": "we-work-remotely",
    }

    for key, portal_name in portal_mappings.items():
        if key in domain_lower:
            return portal_name

    return None


@tool("scrape_jobs", parse_docstring=True)
async def scrape_jobs(
    portal_url: str, keywords: str = "", max_results: int = 15
) -> str:
    """
    Scrape job listings from any portal using smart selector routing.

    This tool attempts to scrape jobs from ANY portal URL:
    1. If it's a known portal (Hiredly, JobStreet, LinkedIn, etc.), use hardcoded selectors
    2. If domain is cached, use previously discovered selectors
    3. Otherwise, use LLM to discover selectors on the fly

    Args:
        portal_url: Full URL to the job search page or portal home
        keywords: Job search keywords (optional for direct URLs)
        max_results: Maximum listings to return (cap: 20)

    Returns:
        JSON string of job listings or error dict
    """
    try:
        domain = _get_domain(portal_url)
        known_portal = _domain_to_known_portal(domain)

        # Route 1: Known portal with hardcoded selectors
        if known_portal and known_portal in PORTALS:
            return await _scrape_with_portal(known_portal, portal_url, keywords, max_results)

        # Route 2: Check cache for domain
        cache = _load_portal_cache()
        if domain in cache:
            selectors = cache[domain]
            return await _scrape_with_selectors(
                portal_url, selectors, domain, max_results
            )

        # Route 3: LLM discovery (expensive, but only happens once per domain)
        logger.info(f"Discovering selectors for {domain} via LLM...")
        selectors = await _llm_discover_selectors(portal_url)
        if selectors:
            cache[domain] = selectors
            _save_portal_cache(cache)
            return await _scrape_with_selectors(
                portal_url, selectors, domain, max_results
            )

        return json.dumps({"error": f"Unable to scrape {domain} — no selectors found"})

    except Exception as e:
        logger.error(f"scrape_jobs error: {e}", exc_info=True)
        return json.dumps({"error": str(e)})


async def _scrape_with_portal(
    portal_name: str, url: str, keywords: str, max_results: int
) -> str:
    """Use hardcoded selectors for a known portal."""
    logger.info(f"Scraping {portal_name}...")
    session = await get_session()
    page = await session.get_page()
    session.set_action(f"Scraping {portal_name}...")

    try:
        await page.goto(url, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(random.randint(1000, 2000))

        config = PORTALS[portal_name]
        cards_selector = config["job_cards"]

        try:
            await page.wait_for_selector(cards_selector, timeout=15000)
        except PlaywrightTimeoutError:
            return json.dumps(
                {"error": f"No job cards found on {portal_name}", "portal": portal_name}
            )

        # Scroll to load more
        for _ in range(3):
            await page.evaluate("window.scrollBy(0, window.innerHeight)")
            await page.wait_for_timeout(random.randint(500, 1000))

        # Extract jobs
        jobs = []
        cards = await page.query_selector_all(cards_selector)
        for card in cards[: min(max_results, len(cards))]:
            try:
                title_elem = await card.query_selector(config["title"])
                company_elem = await card.query_selector(config["company"])

                if not title_elem or not company_elem:
                    continue

                title = await title_elem.inner_text()
                company = await company_elem.inner_text()

                # Try to get URL from card href attribute or data attribute
                url_attr = await card.get_attribute("href")
                if not url_attr:
                    # Try nested link
                    link = await card.query_selector("a")
                    if link:
                        url_attr = await link.get_attribute("href")

                if not url_attr:
                    continue

                if not url_attr.startswith("http"):
                    # Make absolute URL
                    parsed = urlparse(page.url)
                    base = f"{parsed.scheme}://{parsed.netloc}"
                    url_attr = base + url_attr

                jobs.append(
                    {
                        "job_id": _job_id(url_attr),
                        "title": title.strip(),
                        "company": company.strip(),
                        "url": url_attr,
                        "portal": portal_name,
                        "description": "Job description (click to view full details)",
                        "location": "See job page",
                        "status": "scraped",
                    }
                )
            except Exception as e:
                logger.debug(f"Error extracting job card: {e}")
                continue

        logger.info(f"Scraped {len(jobs)} jobs from {portal_name}")
        return json.dumps(jobs)

    except Exception as e:
        logger.error(f"Scraping error for {portal_name}: {e}")
        return json.dumps({"error": str(e), "portal": portal_name})


async def _scrape_with_selectors(
    url: str, selectors: dict, domain: str, max_results: int
) -> str:
    """Scrape using previously discovered or cached selectors."""
    logger.info(f"Scraping {domain} with cached selectors...")
    session = await get_session()
    page = await session.get_page()
    session.set_action(f"Scraping {domain}...")

    try:
        await page.goto(url, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(random.randint(1000, 2000))

        cards_selector = selectors.get("job_cards", "div.job-card")
        try:
            await page.wait_for_selector(cards_selector, timeout=15000)
        except PlaywrightTimeoutError:
            return json.dumps(
                {"error": f"Cached selectors no longer work for {domain}", "domain": domain}
            )

        # Extract jobs
        jobs = []
        cards = await page.query_selector_all(cards_selector)
        for card in cards[: min(max_results, len(cards))]:
            try:
                title_selector = selectors.get("title", "h2")
                company_selector = selectors.get("company", "span.company")

                title_elem = await card.query_selector(title_selector)
                company_elem = await card.query_selector(company_selector)

                if not title_elem or not company_elem:
                    continue

                title = await title_elem.inner_text()
                company = await company_elem.inner_text()

                url_attr = await card.get_attribute("href") or ""
                if not url_attr.startswith("http"):
                    parsed = urlparse(page.url)
                    base = f"{parsed.scheme}://{parsed.netloc}"
                    url_attr = base + url_attr

                jobs.append(
                    {
                        "job_id": _job_id(url_attr),
                        "title": title.strip(),
                        "company": company.strip(),
                        "url": url_attr,
                        "portal": domain,
                        "description": "See job page",
                        "location": "See job page",
                        "status": "scraped",
                    }
                )
            except Exception:
                continue

        return json.dumps(jobs)

    except Exception as e:
        return json.dumps({"error": str(e), "domain": domain})


async def _llm_discover_selectors(url: str) -> Optional[dict]:
    """
    Use GPT-4o to inspect page HTML and discover CSS selectors.

    Returns a dict of selectors or None if discovery fails.
    """
    try:
        from config.model_factory import get_llm
        from config.settings import settings

        session = await get_session()
        page = await session.get_page()

        await page.goto(url, wait_until="load", timeout=30000)
        html = await page.content()
        html_sample = html[:3000]  # First 3000 chars for analysis

        llm = get_llm(settings.model_scraper, temperature=0)

        from langchain_core.messages import HumanMessage

        prompt = HumanMessage(
            content=f"""Analyze this HTML and return JSON with CSS selectors for a job board.
Return ONLY valid JSON, no markdown.

Required fields:
- job_cards: selector for job listing containers
- title: selector for job title within a card
- company: selector for company name within a card
- apply_button: selector for apply button (optional)

Example JSON:
{{"job_cards": "div.job-card", "title": "h2.title", "company": "span.company", "apply_button": "button.apply"}}

HTML sample:
{html_sample}"""
        )

        response = await llm.ainvoke([prompt])
        text = response.content.strip()

        # Try to parse JSON from response
        import re

        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if json_match:
            selectors = json.loads(json_match.group())
            logger.info(f"Discovered selectors: {selectors}")
            return selectors

        return None

    except Exception as e:
        logger.error(f"LLM selector discovery failed: {e}")
        return None
