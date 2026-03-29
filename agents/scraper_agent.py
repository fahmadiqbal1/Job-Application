"""Scraper agent — scrapes job listings from any portal."""

from langgraph.prebuilt import create_react_agent

from config.model_factory import get_llm
from config.settings import settings
from state.job_state import JobApplicationState
from tools.universal_scraper import scrape_jobs
from tools.scraper_tools import filter_jobs


def make_scraper_agent():
    """Create scraper agent."""
    model = get_llm(settings.model_scraper, temperature=0)

    tools = [
        scrape_jobs,  # Universal scraper — works on any portal
        filter_jobs,  # Deduplication and filtering
    ]

    agent = create_react_agent(
        model=model,
        tools=tools,
        state_schema=JobApplicationState,
        messages_key="messages",
    )

    return agent


scraper_agent = make_scraper_agent()
