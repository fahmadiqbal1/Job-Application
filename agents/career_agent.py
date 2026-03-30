"""Career automation agent — wraps career tools for interactive use."""

import logging

from langchain.agents import create_react_agent
from langchain_core.prompts import PromptTemplate

from config.model_factory import get_llm
from config.settings import settings
from tools.career_tools import (
    analyze_resume_quality,
    optimize_linkedin_profile,
    search_hiring_managers,
    generate_linkedin_post,
)

logger = logging.getLogger(__name__)


# Create the agent with all career tools
tools = [
    analyze_resume_quality,
    optimize_linkedin_profile,
    search_hiring_managers,
    generate_linkedin_post,
]

prompt_template = PromptTemplate(
    input_variables=["input", "agent_scratchpad"],
    template="""You are a career automation assistant helping job seekers.

Tools available:
- analyze_resume_quality: Score resume bullets and find weak points
- optimize_linkedin_profile: Improve LinkedIn profile content
- search_hiring_managers: Find hiring manager posts in your target role/location
- generate_linkedin_post: Create LinkedIn post options in various categories

User request: {input}

Thought process (use tools as needed):
{agent_scratchpad}""",
)

llm = get_llm(settings.model_ats, temperature=0.5)
career_agent = create_react_agent(llm, tools, prompt_template)

logger.info("Career agent initialized with 4 tools")
