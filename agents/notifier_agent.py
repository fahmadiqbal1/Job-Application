"""Notifier agent — sends final summaries and confirmations."""

from langgraph.prebuilt import create_react_agent

from config.model_factory import get_llm
from config.settings import settings
from state.job_state import JobApplicationState
from tools.notifier_tools import send_telegram_message, send_email_confirmation


def make_notifier_agent():
    """Create notifier agent."""
    model = get_llm(settings.model_notifier, temperature=0)

    tools = [
        send_telegram_message,
        send_email_confirmation,
    ]

    agent = create_react_agent(
        model=model,
        tools=tools,
        state_schema=JobApplicationState,
        messages_key="messages",
    )

    return agent


notifier_agent = make_notifier_agent()
