"""Company research and interview prep."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

from models.schemas import InterviewPrepResult, StoryEntry
from tools.cv_tools import read_cv, read_profile
from tools.story_bank import append_story


def _get_llm():
    from config.settings import settings
    return ChatAnthropic(
        model=settings.default_model,
        anthropic_api_key=settings.anthropic_api_key,
        max_tokens=4096,
    )


def _read_prompt(prompts_dir: str, filename: str) -> str:
    path = Path(prompts_dir) / filename
    return path.read_text(encoding="utf-8") if path.exists() else ""


async def deep_research(company: str, role: str, prompts_dir: str) -> str:
    """6-axis company research framework."""
    llm = _get_llm()
    deep_prompt = _read_prompt(prompts_dir, "modes/deep.md")

    msg = await llm.ainvoke([
        SystemMessage(content=deep_prompt or "You are a company research expert. Provide structured analysis."),
        HumanMessage(content=f"""Research {company} for a {role} application.

Provide a structured analysis across these 6 axes:

## 1. AI Strategy
What AI products/features does this company have? Known tech stack? Engineering blog highlights?

## 2. Recent Moves
Recent hires, acquisitions, product launches, funding rounds, leadership changes.

## 3. Engineering Culture
Deploy cadence, remote policy, Glassdoor signals, tech stack, engineering values.

## 4. Probable Challenges
What scaling, reliability, or transformation challenges is this company likely facing?

## 5. Competition & Moat
Who are their main competitors? What's their differentiation?

## 6. Your Angle
Given a {role} application, what unique value can the candidate highlight? What's the key story to tell?

Be specific and actionable. Use your knowledge but flag uncertainty where relevant."""),
    ])

    return msg.content if isinstance(msg.content, str) else str(msg.content)


async def prepare_interview(
    company: str,
    role: str,
    report_id: Optional[str],
    data_dir: str,
    prompts_dir: str,
) -> InterviewPrepResult:
    """Generate a full interview prep pack."""
    llm = _get_llm()
    prepare_prompt = _read_prompt(prompts_dir, "modes/prepare.md")
    cv_text = read_cv(data_dir)
    profile = read_profile(data_dir)

    # Load report for context
    report_context = ""
    if report_id:
        reports_dir = Path(data_dir) / "reports"
        matches = list(reports_dir.glob(f"{report_id}-*.md"))
        if matches:
            report_context = matches[0].read_text(encoding="utf-8")[:2000]

    candidate_name = profile.get("candidate", {}).get("full_name", "the candidate")

    msg = await llm.ainvoke([
        SystemMessage(content=prepare_prompt or f"""You are an expert interview coach.
Candidate CV:
{cv_text[:3000]}"""),
        HumanMessage(content=f"""Prepare {candidate_name} for an interview at {company} for {role}.

{f'Evaluation context: {report_context}' if report_context else ''}

Generate:
1. 8 most likely interview questions (mix of behavioral + technical)
2. For each question: a tailored answer using real experience from the CV
3. 3 red-flag/trap questions + how to handle them
4. 3 day-of tips specific to this company

Format as structured JSON:
{{
  "questions": [
    {{"question": "...", "answer_guidance": "...", "story_title": "optional STAR story title"}}
  ],
  "red_flags": [
    {{"question": "...", "how_to_handle": "..."}}
  ],
  "day_of_tips": ["tip 1", "tip 2", "tip 3"],
  "stories": [
    {{"title": "...", "situation": "...", "task": "...", "action": "...", "result": "...", "reflection": "...", "archetypes": []}}
  ]
}}"""),
    ])

    text = msg.content if isinstance(msg.content, str) else str(msg.content)
    try:
        import json
        m = re.search(r"\{.*\}", text, re.DOTALL)
        data = json.loads(m.group()) if m else {}
    except Exception:
        data = {}

    questions = data.get("questions", [])
    red_flags = data.get("red_flags", [])
    day_of_tips = data.get("day_of_tips", [])
    stories_data = data.get("stories", [])

    # Save new STAR stories to story bank
    stories: list[StoryEntry] = []
    for s in stories_data:
        story = StoryEntry(
            title=s.get("title", ""),
            situation=s.get("situation", ""),
            task=s.get("task", ""),
            action=s.get("action", ""),
            result=s.get("result", ""),
            reflection=s.get("reflection", ""),
            archetypes=s.get("archetypes", []),
        )
        stories.append(story)
        try:
            append_story(story, data_dir)
        except Exception:
            pass

    return InterviewPrepResult(
        company=company,
        role=role,
        questions=questions,
        stories=stories,
        red_flags=red_flags,
        day_of_tips=day_of_tips,
    )
