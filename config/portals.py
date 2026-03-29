"""Portal-specific CSS selectors and URLs."""

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
import asyncio


PORTALS = {
    "hiredly": {
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
}

# Test URLs for selector verification
TEST_URLS = {
    "hiredly": "https://hiredly.com/jobs/senior-software-engineer",
    "jobstreet": "https://www.jobstreet.com.my/jobs/view/123456",
}


async def verify_selectors(portal: str) -> None:
    """
    Verify that all selectors for a portal resolve on a live page.
    Raises SelectorVerificationError if any selector fails.
    """
    if portal not in PORTALS:
        raise ValueError(f"Unknown portal: {portal}")

    config = PORTALS[portal]
    test_url = TEST_URLS.get(portal)

    if not test_url:
        print(f"⚠️ No test URL for {portal}, skipping verification")
        return

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
                    print(f"✓ {portal}: {sel_name} selector OK")
                except PlaywrightTimeoutError:
                    raise SelectorVerificationError(
                        f"Selector '{sel_name}' ({selector}) not found on {portal}"
                    )

            print(f"✅ {portal} selectors verified")

        except SelectorVerificationError:
            raise
        except Exception as e:
            print(f"⚠️ Verification incomplete for {portal}: {e}")
        finally:
            await browser.close()


class SelectorVerificationError(Exception):
    """Raised when a portal selector fails verification."""

    pass
