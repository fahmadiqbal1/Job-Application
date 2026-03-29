"""Application agent — fills forms, requests confirmation, and submits."""

from langgraph.prebuilt import create_react_agent

from config.model_factory import get_llm
from config.settings import settings
from state.job_state import JobApplicationState
from tools.browser_tools import (
    fill_application_form,
    take_screenshot,
    submit_form,
)
from tools.notifier_tools import request_telegram_confirmation


def make_application_agent():
    """Create application agent."""
    model = get_llm(settings.model_application, temperature=0)

    tools = [
        fill_application_form,
        take_screenshot,
        request_telegram_confirmation,
        submit_form,
    ]

    agent = create_react_agent(
        model=model,
        tools=tools,
        state_schema=JobApplicationState,
        messages_key="messages",
    )

    return agent


application_agent = make_application_agent()
