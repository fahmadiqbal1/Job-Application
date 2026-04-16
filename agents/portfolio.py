"""Portfolio project and training/certification evaluation."""

from __future__ import annotations

import json
import re
from pathlib import Path

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

from models.schemas import ProjectEvalRequest, ProjectEvalResult, TrainingEvalRequest, TrainingEvalResult


def _get_llm():
    from config.settings import settings
    return ChatAnthropic(
        model=settings.default_model,
        anthropic_api_key=settings.anthropic_api_key,
        max_tokens=2048,
    )


def _read_prompt(prompts_dir: str, filename: str) -> str:
    path = Path(prompts_dir) / filename
    return path.read_text(encoding="utf-8") if path.exists() else ""


PROJECT_DIMENSIONS = [
    ("Signal for Target Roles", 0.25),
    ("Uniqueness", 0.20),
    ("Demo-ability", 0.20),
    ("Metrics Potential", 0.15),
    ("Time to MVP", 0.10),
    ("STAR Story Potential", 0.10),
]

TRAINING_DIMENSIONS = [
    ("Alignment to Target Roles", 0.30),
    ("Recruiter Signal", 0.25),
    ("Content Quality Risk", 0.15),
    ("Portfolio Deliverable", 0.15),
    ("Opportunity Cost", 0.15),
]


async def evaluate_project(req: ProjectEvalRequest, prompts_dir: str) -> ProjectEvalResult:
    llm = _get_llm()
    project_prompt = _read_prompt(prompts_dir, "modes/project.md")
    dim_str = "\n".join(f"- {n} ({int(w*100)}%)" for n, w in PROJECT_DIMENSIONS)

    msg = await llm.ainvoke([
        SystemMessage(content=project_prompt or "You are a senior career advisor evaluating portfolio projects."),
        HumanMessage(content=f"""Evaluate this portfolio project for job search value:

Project: {req.name}
Description: {req.description}
Tech Stack: {', '.join(req.tech_stack) if req.tech_stack else 'not specified'}
Status: {req.status}

Score on these dimensions (1-5):
{dim_str}

Reply with ONLY this JSON:
{{
  "scores": {{"Signal for Target Roles": 4.5, "Uniqueness": 3.5, ...}},
  "total": 4.1,
  "verdict": "BUILD",
  "reasoning": "...",
  "action_plan": "Week 1: ... Week 2: ..."
}}

Verdict must be one of: BUILD, SKIP, PIVOT"""),
    ])

    text = msg.content if isinstance(msg.content, str) else str(msg.content)
    try:
        m = re.search(r"\{.*\}", text, re.DOTALL)
        data = json.loads(m.group()) if m else {}
    except Exception:
        data = {}

    scores = data.get("scores", {d[0]: 3.0 for d in PROJECT_DIMENSIONS})
    total = data.get("total") or sum(
        scores.get(n, 3.0) * w for n, w in PROJECT_DIMENSIONS
    )

    return ProjectEvalResult(
        name=req.name,
        scores=scores,
        total=round(float(total), 2),
        verdict=data.get("verdict", "BUILD"),
        reasoning=data.get("reasoning", ""),
        action_plan=data.get("action_plan"),
    )


async def evaluate_training(req: TrainingEvalRequest, prompts_dir: str) -> TrainingEvalResult:
    llm = _get_llm()
    training_prompt = _read_prompt(prompts_dir, "modes/training.md")
    dim_str = "\n".join(f"- {n} ({int(w*100)}%)" for n, w in TRAINING_DIMENSIONS)
    total_hours = req.weeks * req.hours_per_week

    msg = await llm.ainvoke([
        SystemMessage(content=training_prompt or "You are a career advisor evaluating training ROI."),
        HumanMessage(content=f"""Evaluate this training/certification for career ROI:

Name: {req.name}
Provider: {req.provider}
Duration: {req.weeks} weeks × {req.hours_per_week} hours/week = {total_hours} total hours
Description: {req.description or 'Not provided'}

Score on these dimensions (1-5):
{dim_str}

Reply with ONLY this JSON:
{{
  "scores": {{"Alignment to Target Roles": 4.5, "Recruiter Signal": 3.5, ...}},
  "total": 3.8,
  "verdict": "DO IT",
  "timebox_weeks": null,
  "reasoning": "..."
}}

Verdict must be one of: DO IT, SKIP, DO WITH TIMEBOX
If DO WITH TIMEBOX, set timebox_weeks to a number."""),
    ])

    text = msg.content if isinstance(msg.content, str) else str(msg.content)
    try:
        m = re.search(r"\{.*\}", text, re.DOTALL)
        data = json.loads(m.group()) if m else {}
    except Exception:
        data = {}

    scores = data.get("scores", {d[0]: 3.0 for d in TRAINING_DIMENSIONS})
    total = data.get("total") or sum(
        scores.get(n, 3.0) * w for n, w in TRAINING_DIMENSIONS
    )

    return TrainingEvalResult(
        name=req.name,
        scores=scores,
        total=round(float(total), 2),
        verdict=data.get("verdict", "DO IT"),
        timebox_weeks=data.get("timebox_weeks"),
        reasoning=data.get("reasoning", ""),
    )
