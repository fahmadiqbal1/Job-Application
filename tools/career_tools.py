"""Career automation tools — resume optimizer, LinkedIn tools, hiring manager search, post generator."""

import json
import logging
import re
from typing import Optional

from langchain.tools import tool

logger = logging.getLogger(__name__)


@tool("analyze_resume_quality", parse_docstring=True)
async def analyze_resume_quality(resume_text: str) -> str:
    """
    Score each resume bullet for quality using [Verb]+[Did]+[Metric] formula.

    Identifies weak bullets, missing metrics, generic language, and provides recommendations.

    Args:
        resume_text: Full resume text to analyze

    Returns:
        JSON string with overall_score, weak bullets, strong bullets, recommendations
    """
    try:
        from config.model_factory import get_llm
        from config.settings import settings
        from state.prompts import get_prompt
        from langchain_core.messages import HumanMessage

        llm = get_llm(settings.model_ats, temperature=0)
        prompt_template = get_prompt("resume_optimizer_analyze")

        if not prompt_template:
            return json.dumps({"error": "Prompt not found"})

        prompt = HumanMessage(
            content=prompt_template.format(resume_text=resume_text[:3000])
        )

        response = await llm.ainvoke([prompt])
        text = response.content.strip()

        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if json_match:
            return json_match.group()

        return json.dumps({"error": "Could not parse response"})

    except Exception as e:
        logger.error(f"Resume quality analysis failed: {e}")
        return json.dumps({"error": str(e)})


@tool("optimize_linkedin_profile", parse_docstring=True)
async def optimize_linkedin_profile(profile_text: str, goal: str) -> str:
    """
    Analyze LinkedIn profile and provide section-by-section rewrites.

    Checks headline, about, experience bullets, featured section, skills, and CTA.

    Args:
        profile_text: Pasted LinkedIn profile content
        goal: User's goal (e.g., "attract PM roles", "build AI thought leadership")

    Returns:
        JSON string with rewrites for headline, about, experience, skills, etc.
    """
    try:
        from config.model_factory import get_llm
        from config.settings import settings
        from state.prompts import get_prompt
        from langchain_core.messages import HumanMessage

        llm = get_llm(settings.model_ats, temperature=0.5)
        prompt_template = get_prompt("linkedin_optimize")

        if not prompt_template:
            return json.dumps({"error": "Prompt not found"})

        prompt = HumanMessage(
            content=prompt_template.format(
                profile_text=profile_text[:3000], goal=goal
            )
        )

        response = await llm.ainvoke([prompt])
        text = response.content.strip()

        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if json_match:
            return json_match.group()

        return json.dumps({"error": "Could not parse response"})

    except Exception as e:
        logger.error(f"LinkedIn optimization failed: {e}")
        return json.dumps({"error": str(e)})


@tool("search_hiring_managers", parse_docstring=True)
async def search_hiring_managers(role: str, industry: str, location: str) -> str:
    """
    Execute Bing searches for hiring manager posts mentioning the role and location.

    Uses 3 search patterns to find LinkedIn posts from potential hiring managers.

    Args:
        role: Target role (e.g., "Product Manager", "AI Engineer")
        industry: Industry context (e.g., "SaaS", "FinTech")
        location: Geographic location or "remote"

    Returns:
        JSON string with list of hiring manager post contexts [{name, company, post_snippet, url, pattern}]
    """
    try:
        from datetime import datetime, timedelta
        from state.prompts import get_prompt

        # Calculate date 30 days ago for search (recent posts)
        thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        # Get search patterns from prompts
        pattern_a = get_prompt("hiring_manager_search_a")
        pattern_b = get_prompt("hiring_manager_search_b")
        pattern_c = get_prompt("hiring_manager_search_c")

        if not all([pattern_a, pattern_b, pattern_c]):
            return json.dumps({"error": "Search patterns not found"})

        # Format patterns with user inputs
        queries = [
            pattern_a.format(role=role, industry=industry, date=thirty_days_ago),
            pattern_b.format(role=role, location=location, date=thirty_days_ago),
            pattern_c.format(role=role, date=thirty_days_ago),
        ]

        # TODO: Implement actual Bing search via BrowserSession
        # For now, return placeholder with search queries
        results = {
            "status": "search_queries_prepared",
            "queries": queries,
            "note": "Actual search implementation requires BrowserSession Bing integration",
            "results": []
        }

        return json.dumps(results)

    except Exception as e:
        logger.error(f"Hiring manager search failed: {e}")
        return json.dumps({"error": str(e)})


@tool("generate_linkedin_post", parse_docstring=True)
async def generate_linkedin_post(category: str, background: str) -> str:
    """
    Generate 3 LinkedIn post options in a given category.

    Categories: reintroduction, lesson, hot_take, insight, tool.

    Args:
        category: Post category (reintroduction|lesson|hot_take|insight|tool)
        background: User background context (e.g., "AI product manager with 5 years in SaaS")

    Returns:
        JSON string with 3 post options as {"options": ["post1", "post2", "post3"]}
    """
    try:
        from config.model_factory import get_llm
        from config.settings import settings
        from state.prompts import get_prompt
        from langchain_core.messages import HumanMessage

        # Validate category
        valid_categories = ["reintroduction", "lesson", "hot_take", "insight", "tool"]
        if category not in valid_categories:
            return json.dumps({"error": f"Invalid category. Must be one of: {valid_categories}"})

        llm = get_llm(settings.model_ats, temperature=0.7)
        prompt_key = f"linkedin_post_{category}"
        prompt_template = get_prompt(prompt_key)

        if not prompt_template:
            return json.dumps({"error": f"Prompt '{prompt_key}' not found"})

        # Generate 3 variations
        options = []
        for i in range(3):
            # Vary temperature slightly for diversity
            llm_var = get_llm(settings.model_ats, temperature=0.7 + (i * 0.1))

            prompt = HumanMessage(content=prompt_template.format(background=background))
            response = await llm_var.ainvoke([prompt])
            options.append(response.content.strip())

        return json.dumps({"options": options})

    except Exception as e:
        logger.error(f"LinkedIn post generation failed: {e}")
        return json.dumps({"error": str(e)})
