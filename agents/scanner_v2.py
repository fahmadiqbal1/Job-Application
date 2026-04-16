"""Portal scanner v2 — 3-level scan strategy."""

from __future__ import annotations

import asyncio
import re
from datetime import date
from typing import Optional

from models.schemas import ScanJobStatus, ScanResult
from tools.cv_tools import read_portals
from tools.fuzzy_match import normalize_company
from tools.scan_history import is_seen, record


async def run_portal_scan(
    job_id: str,
    levels: list[str],
    data_dir: str,
    status_registry: dict[str, ScanJobStatus],
) -> list[ScanResult]:
    """Orchestrate 3-level portal scan."""
    from config.settings import settings

    config_dir = str(__import__("pathlib").Path(settings.scripts_dir).parent / "config")
    portals_config = read_portals(config_dir)

    all_results: list[ScanResult] = []
    job = status_registry.get(job_id)

    companies_my = portals_config.get("tracked_companies_my", [])
    companies_global = portals_config.get("tracked_companies_global", [])
    all_companies = companies_my + companies_global

    if job:
        job.total_companies = len(all_companies)

    title_filter = portals_config.get("title_filter", {})
    positive_kw = [k.lower() for k in title_filter.get("positive", [])]
    negative_kw = [k.lower() for k in title_filter.get("negative", [])]
    boost_kw = [k.lower() for k in title_filter.get("seniority_boost", [])]

    # Level 1: Playwright direct scan
    if "direct" in levels:
        direct_results = await _scan_direct(
            companies=all_companies,
            job_id=job_id,
            status_registry=status_registry,
        )
        all_results.extend(direct_results)

    # Level 2: Greenhouse API
    if "greenhouse" in levels:
        greenhouse_results = await _scan_greenhouse(all_companies)
        all_results.extend(greenhouse_results)

    # Level 3: Web search (LLM-based)
    if "search" in levels:
        search_results = await _scan_search(portals_config)
        all_results.extend(search_results)

    # Deduplicate and filter
    seen_urls: set[str] = set()
    final_results: list[ScanResult] = []

    for result in all_results:
        if result.url in seen_urls:
            continue
        seen_urls.add(result.url)

        # Title filter
        title_lower = result.title.lower()
        if positive_kw and not any(kw in title_lower for kw in positive_kw):
            result.status = "filtered"
        if any(kw in title_lower for kw in negative_kw):
            result.status = "filtered"

        # Priority boost
        if any(kw in title_lower for kw in boost_kw):
            result.priority = True

        # Dedup against scan history
        if is_seen(result.url, data_dir):
            result.status = "seen"
        elif result.status == "new":
            record(result.url, result.title, result.company, result.source, data_dir)

        final_results.append(result)

    # Update job stats
    if job:
        job.found = len(final_results)
        job.filtered = sum(1 for r in final_results if r.status == "filtered")
        job.new = sum(1 for r in final_results if r.status == "new")

    return final_results


async def _scan_direct(
    companies: list,
    job_id: str,
    status_registry: dict,
) -> list[ScanResult]:
    """Level 1: Direct Playwright navigation to company career pages."""
    results: list[ScanResult] = []
    job = status_registry.get(job_id)

    for company_entry in companies:
        if isinstance(company_entry, str):
            company_name = company_entry
            career_url = None
        elif isinstance(company_entry, dict):
            company_name = company_entry.get("name", str(company_entry))
            career_url = company_entry.get("careers_url")
        else:
            continue

        try:
            company_results = await _scrape_career_page(company_name, career_url)
            results.extend(company_results)
        except Exception:
            pass

        if job:
            job.companies_scanned += 1

        # Brief pause to avoid rate limiting
        await asyncio.sleep(0.5)

    return results


async def _scrape_career_page(company_name: str, career_url: Optional[str]) -> list[ScanResult]:
    """Scrape a company's careers page for open roles."""
    if not career_url:
        return []

    try:
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(career_url, wait_until="networkidle", timeout=15000)
            # Look for job listings
            content = await page.content()
            await browser.close()

        # Extract job URLs and titles from page content
        return _extract_jobs_from_html(content, company_name, career_url)
    except Exception:
        return []


def _extract_jobs_from_html(html: str, company: str, base_url: str) -> list[ScanResult]:
    """Heuristic extraction of job listings from HTML."""
    import re
    results = []
    today = date.today().isoformat()

    # Look for common job listing patterns
    job_link_pattern = re.compile(
        r'href=["\']([^"\']*(?:job|career|position|role|opening)[^"\']*)["\']'
        r'[^>]*>([^<]{5,100})',
        re.IGNORECASE,
    )

    for match in job_link_pattern.finditer(html):
        href, title = match.group(1), match.group(2).strip()
        if not href.startswith("http"):
            if href.startswith("/"):
                from urllib.parse import urlparse
                parsed = urlparse(base_url)
                href = f"{parsed.scheme}://{parsed.netloc}{href}"
            else:
                continue

        # Filter out navigation links
        if len(title) < 5 or len(title) > 100:
            continue

        results.append(ScanResult(
            url=href,
            title=title,
            company=company,
            source="playwright",
            priority=False,
            date_found=today,
            status="new",
        ))
        if len(results) >= 20:  # Cap per company
            break

    return results


async def _scan_greenhouse(companies: list) -> list[ScanResult]:
    """Level 2: Greenhouse API for companies on that platform."""
    import httpx
    results: list[ScanResult] = []
    today = date.today().isoformat()

    async with httpx.AsyncClient(timeout=10) as client:
        for company_entry in companies:
            if isinstance(company_entry, dict):
                greenhouse_slug = company_entry.get("greenhouse_slug")
                company_name = company_entry.get("name", "")
            else:
                continue

            if not greenhouse_slug:
                continue

            try:
                resp = await client.get(
                    f"https://boards-api.greenhouse.io/v1/boards/{greenhouse_slug}/jobs",
                    params={"content": "true"},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    for job in data.get("jobs", [])[:20]:
                        results.append(ScanResult(
                            url=job.get("absolute_url", ""),
                            title=job.get("title", ""),
                            company=company_name,
                            source="greenhouse",
                            priority=False,
                            date_found=today,
                            status="new",
                        ))
            except Exception:
                continue

    return results


async def _scan_search(portals_config: dict) -> list[ScanResult]:
    """Level 3: Web search queries from portals config."""
    # Use basic web search via LLM knowledge (Playwright-based search requires heavy setup)
    # In production this would use a real search API
    return []
