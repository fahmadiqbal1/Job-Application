"""ATS Analysis Agent — scores resumes and suggests edits."""

from langgraph.prebuilt import create_react_agent

from config.model_factory import get_llm
from config.settings import settings
from state.job_state import JobApplicationState
from tools.ats_tools import (
    analyze_job_requirements,
    score_resume_vs_jd,
    generate_resume_edits,
    get_resume_structure,
)


def make_ats_agent():
    """Create ATS analysis agent using PageIndex tools."""

    # Use configured model
    model = get_llm(settings.model_ats, temperature=0)

    # ATS tools for job requirement analysis and resume scoring
    tools = [
        analyze_job_requirements,
        score_resume_vs_jd,
        generate_resume_edits,
        get_resume_structure,
    ]

    agent = create_react_agent(
        model=model,
        tools=tools,
        state_schema=JobApplicationState,
        messages_key="messages",
    )

    return agent


ats_agent = make_ats_agent()
