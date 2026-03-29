"""Cover letter agent — generates tailored cover letters."""

from langgraph.prebuilt import create_react_agent

from config.model_factory import get_llm
from config.settings import settings
from state.job_state import JobApplicationState
from tools.cover_letter_tools import load_resume_context, generate_cover_letter


def make_cover_letter_agent():
    """Create cover letter agent."""
    model = get_llm(settings.model_cover_letter, temperature=0.7)

    tools = [
        load_resume_context,
        generate_cover_letter,
    ]

    agent = create_react_agent(
        model=model,
        tools=tools,
        state_schema=JobApplicationState,
        messages_key="messages",
    )

    return agent


cover_letter_agent = make_cover_letter_agent()
