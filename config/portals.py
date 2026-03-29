"""Portal-specific CSS selectors and URLs."""

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
import asyncio


PORTALS = {
    # ── Malaysia & SE Asia ──
    "hiredly": {
        "name": "Hiredly",
        "region": "Malaysia/SEA",
        "type": "Playwright",
        "search_url": "https://hiredly.com/jobs?keyword={keywords}&location={location}",
        "job_cards": ".JobCard",
        "title": ".JobCard__title",
        "company": ".JobCard__company",
        "apply_button": "[data-cy='apply-button']",
        "cover_letter_field": "textarea[name='coverLetter']",
        "resume_upload": "input[type='file'][accept='.pdf']",
        "submit_button": "button[type='submit']",
        "confirmation": ".application-success",
        "login_url": "https://hiredly.com/login",
        "email_field": "input[name='email']",
        "password_field": "input[name='password']",
    },
    "jobstreet": {
        "name": "JobStreet",
        "region": "Malaysia/SEA",
        "type": "Playwright",
        "search_url": "https://www.jobstreet.com.my/jobs?q={keywords}&l={location}",
        "job_cards": "[data-automation='job-card']",
        "title": "[data-automation='job-title']",
        "company": "[data-automation='job-company']",
        "apply_button": "[data-automation='apply-button']",
        "cover_letter_field": "[data-automation='coverLetterInput']",
        "resume_upload": "[data-automation='resumeUpload'] input",
        "submit_button": "[data-automation='submit-application']",
        "confirmation": "[data-automation='application-confirmation']",
        "login_url": "https://my.jobstreet.com/login",
        "email_field": "input[id='emailAddress']",
        "password_field": "input[id='password']",
    },
    "jobsdb": {
        "name": "JobsDB",
        "region": "Malaysia/SEA",
        "type": "Playwright",
        "search_url": "https://my.jobsdb.com/jobs?keywords={keywords}&location={location}",
        "job_cards": "[data-automation='job-card']",
        "title": "[data-automation='job-title']",
        "company": "[data-automation='job-company']",
        "apply_button": "[data-automation='apply-button']",
        "cover_letter_field": "[data-automation='coverLetterField']",
        "resume_upload": "[data-automation='resumeUpload'] input",
        "submit_button": "[data-automation='submitBtn']",
        "confirmation": "[data-automation='successMsg']",
        "login_url": "https://my.jobsdb.com/login",
        "email_field": "input[type='email']",
        "password_field": "input[type='password']",
    },
    "kalibrr": {
        "name": "Kalibrr",
        "region": "Malaysia/PH",
        "type": "Playwright",
        "search_url": "https://www.kalibrr.com/search/jobs?title={keywords}",
        "job_cards": "[data-testid='job-card']",
        "title": "[data-testid='job-title']",
        "company": "[data-testid='company-name']",
        "apply_button": "[data-testid='apply-btn']",
        "cover_letter_field": "[data-testid='coverLetterInput']",
        "submit_button": "[data-testid='submitBtn']",
        "confirmation": "[data-testid='appliedMsg']",
        "login_url": "https://www.kalibrr.com/auth/login",
        "email_field": "input[type='email']",
        "password_field": "input[type='password']",
    },
    "maukerja": {
        "name": "MauKerja",
        "region": "Malaysia",
        "type": "Playwright",
        "search_url": "https://www.maukerja.com/seeker/search?keyword={keywords}",
        "job_cards": ".job-card-wrapper",
        "title": ".job-card__title",
        "company": ".job-card__company",
        "apply_button": ".job-card__apply-btn",
        "cover_letter_field": "textarea.cover-letter-input",
        "submit_button": "button.submit-application",
        "confirmation": ".success-msg",
        "login_url": "https://www.maukerja.com/seeker/login",
        "email_field": "input[name='email']",
        "password_field": "input[name='password']",
    },
    # ── Global ──
    "linkedin": {
        "name": "LinkedIn",
        "region": "Global",
        "type": "Playwright",
        "search_url": "https://www.linkedin.com/jobs/search/?keywords={keywords}",
        "job_cards": ".base-card",
        "title": ".base-search-card__title",
        "company": ".base-search-card__subtitle",
        "apply_button": ".jobs-apply-button",
        "cover_letter_field": "textarea[name='coverLetter']",
        "submit_button": "[data-tracking-control-name='apply_submit']",
        "confirmation": ".artdeco-modal__header",
        "login_url": "https://www.linkedin.com/login",
        "email_field": "input[name='session_key']",
        "password_field": "input[name='session_password']",
    },
    "indeed": {
        "name": "Indeed",
        "region": "Global",
        "type": "Playwright",
        "search_url": "https://www.indeed.com/jobs?q={keywords}&l={location}",
        "job_cards": ".jobsearch-ResultsList > li",
        "title": ".jobTitle",
        "company": "[data-company-name]",
        "apply_button": ".apply",
        "cover_letter_field": "textarea[name='coverLetter']",
        "submit_button": "[type='submit']",
        "confirmation": ".confirm-apply",
        "login_url": "https://secure.indeed.com/account/login",
        "email_field": "input[name='email']",
        "password_field": "input[name='password']",
    },
    "glassdoor": {
        "name": "Glassdoor",
        "region": "Global",
        "type": "Playwright",
        "search_url": "https://www.glassdoor.com/Job/jobs.htm?sc.keyword={keywords}&l={location}",
        "job_cards": ".JobCard",
        "title": ".JobCard__title",
        "company": ".JobCard__company",
        "apply_button": "[data-test='applyButton']",
        "cover_letter_field": "textarea[data-test='coverLetter']",
        "submit_button": "[data-test='submitBtn']",
        "confirmation": "[data-test='successMsg']",
        "login_url": "https://www.glassdoor.com/profile/login_input.htm",
        "email_field": "input[type='email']",
        "password_field": "input[type='password']",
    },
    "monster": {
        "name": "Monster",
        "region": "Global",
        "type": "Playwright",
        "search_url": "https://www.monster.com/jobs/search?q={keywords}&where={location}",
        "job_cards": ".job-card",
        "title": ".job-title",
        "company": ".job-company",
        "apply_button": "[data-testid='apply-button']",
        "cover_letter_field": "textarea.cover-letter",
        "submit_button": "button[type='submit']",
        "confirmation": ".success-msg",
        "login_url": "https://sso.monster.com/login",
        "email_field": "input[name='email']",
        "password_field": "input[name='password']",
    },
    "dice": {
        "name": "Dice",
        "region": "US/Tech",
        "type": "Playwright",
        "search_url": "https://www.dice.com/jobs?q={keywords}&l={location}",
        "job_cards": "[data-testid='jobCard']",
        "title": "[data-testid='jobTitle']",
        "company": "[data-testid='companyName']",
        "apply_button": "[data-testid='applyButton']",
        "cover_letter_field": "textarea[data-testid='coverLetter']",
        "submit_button": "[data-testid='submitBtn']",
        "confirmation": "[data-testid='appliedMsg']",
        "login_url": "https://www.dice.com/login",
        "email_field": "input[type='email']",
        "password_field": "input[type='password']",
    },
    # ── Remote/Special ──
    "remotive": {
        "name": "Remotive",
        "region": "Global/Remote",
        "type": "REST_API",
        "api_url": "https://remotive.com/api/remote-jobs",
        "api_method": "GET",
        "search_url": "https://remotive.com/remote-jobs/{keywords}",
    },
    "we-work-remotely": {
        "name": "We Work Remotely",
        "region": "Global/Remote",
        "type": "Playwright",
        "search_url": "https://weworkremotely.com/remote-jobs/search?term={keywords}",
        "job_cards": ".job",
        "title": ".job-title",
        "company": ".company-name",
        "apply_button": ".apply-link",
        "cover_letter_field": "textarea.cover-letter",
        "submit_button": "button[type='submit']",
        "confirmation": ".success-notification",
        "login_url": "https://weworkremotely.com/users/sign_in",
        "email_field": "input[type='email']",
        "password_field": "input[type='password']",
    },
    "reed": {
        "name": "Reed",
        "region": "UK",
        "type": "Playwright",
        "search_url": "https://www.reed.co.uk/jobs?keywords={keywords}&location={location}",
        "job_cards": "[data-qa='jobListing']",
        "title": "[data-qa='jobTitle']",
        "company": "[data-qa='companyName']",
        "apply_button": "[data-qa='applyButton']",
        "cover_letter_field": "textarea[data-qa='coverLetter']",
        "submit_button": "button[data-qa='submitBtn']",
        "confirmation": "[data-qa='successMsg']",
        "login_url": "https://www.reed.co.uk/account/signin",
        "email_field": "input[type='email']",
        "password_field": "input[type='password']",
    },
}

# Test URLs for selector verification
TEST_URLS = {
    "hiredly": "https://hiredly.com/jobs/senior-software-engineer",
    "jobstreet": "https://www.jobstreet.com.my/jobs/view/123456",
    "jobsdb": "https://my.jobsdb.com/jobs/search?keywords=software",
    "kalibrr": "https://www.kalibrr.com/search/jobs?title=engineer",
    "maukerja": "https://www.maukerja.com/seeker/search?keyword=developer",
    "linkedin": "https://www.linkedin.com/jobs/search/?keywords=software",
    "indeed": "https://www.indeed.com/jobs?q=engineer",
    "glassdoor": "https://www.glassdoor.com/Job/jobs.htm?sc.keyword=software",
    "monster": "https://www.monster.com/jobs/search?q=developer",
    "dice": "https://www.dice.com/jobs?q=engineer",
    "we-work-remotely": "https://weworkremotely.com/remote-jobs/search?term=developer",
    "reed": "https://www.reed.co.uk/jobs?keywords=software",
    # remotive uses REST API, no web verification needed
}


def get_enabled_portals() -> list[str]:
    """Return list of all configured portal names."""
    return list(PORTALS.keys())


def is_api_portal(portal: str) -> bool:
    """Check if a portal uses REST API instead of Playwright."""
    return PORTALS.get(portal, {}).get("type") == "REST_API"


def is_playwright_portal(portal: str) -> bool:
    """Check if a portal uses Playwright browser automation."""
    return PORTALS.get(portal, {}).get("type") == "Playwright"


async def verify_selectors(portal: str) -> dict:
    """
    Verify that all selectors for a portal resolve on a live page.

    Returns:
        dict with keys: healthy (bool), failed_selector (str|None), error_detail (str|None)
    """
    if portal not in PORTALS:
        return {
            "healthy": False,
            "failed_selector": None,
            "error_detail": f"Unknown portal: {portal}",
        }

    config = PORTALS[portal]

    # REST API portals don't need selector verification
    if is_api_portal(portal):
        return {"healthy": True, "failed_selector": None, "error_detail": None}

    test_url = TEST_URLS.get(portal)

    if not test_url:
        return {
            "healthy": False,
            "failed_selector": None,
            "error_detail": f"No test URL for {portal}",
        }

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1366, "height": 768},
        )
        page = await context.new_page()

        try:
            await page.goto(test_url, wait_until="load", timeout=15000)
            await page.wait_for_timeout(1000)

            # Verify key selectors
            selectors_to_check = [
                "job_cards",
                "apply_button",
                "cover_letter_field",
                "submit_button",
            ]

            for sel_name in selectors_to_check:
                selector = config.get(sel_name)
                if not selector:
                    continue

                try:
                    await page.wait_for_selector(selector, timeout=10000)
                except PlaywrightTimeoutError:
                    await browser.close()
                    return {
                        "healthy": False,
                        "failed_selector": sel_name,
                        "error_detail": f"Selector '{sel_name}' ({selector}) not found",
                    }

            return {"healthy": True, "failed_selector": None, "error_detail": None}

        except Exception as e:
            await browser.close()
            return {
                "healthy": False,
                "failed_selector": None,
                "error_detail": str(e),
            }
        finally:
            await browser.close()


class SelectorVerificationError(Exception):
    """Raised when a portal selector fails verification."""

    pass
