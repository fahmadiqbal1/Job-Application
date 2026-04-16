"""LinkedIn outreach — find contacts and generate messages."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

from models.schemas import Contact, OutreachResult
from tools.cv_tools import read_profile


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


async def find_contacts(company: str, role: str) -> list[Contact]:
    """Use web search to find hiring managers and relevant contacts."""
    llm = _get_llm()

    msg = await llm.ainvoke([
        SystemMessage(content="You are a LinkedIn researcher. Reply with JSON only."),
        HumanMessage(content=f"""Find likely LinkedIn contacts for a job application to {company} for a {role} position.

Based on your knowledge, suggest up to 3 contacts:
1. Hiring manager or team lead (most relevant for the role)
2. Recruiter or talent acquisition
3. A peer or senior IC in the team (optional)

For each contact, suggest likely names based on the company's typical team structure.
Note: these are suggested profiles to search for, not guaranteed to exist.

Reply with ONLY this JSON:
{{
  "contacts": [
    {{
      "name": "Suggested Name",
      "title": "Engineering Manager, AI Platform",
      "linkedin_url": null,
      "company": "{company}",
      "search_query": "LinkedIn search query to find this person"
    }}
  ]
}}"""),
    ])

    text = msg.content if isinstance(msg.content, str) else str(msg.content)
    try:
        m = re.search(r"\{.*\}", text, re.DOTALL)
        data = json.loads(m.group()) if m else {}
        return [
            Contact(
                name=c.get("name", ""),
                title=c.get("title", ""),
                linkedin_url=c.get("linkedin_url"),
                company=company,
            )
            for c in data.get("contacts", [])[:3]
        ]
    except Exception:
        return []


async def generate_message(
    contact: Contact,
    report_id: Optional[str],
    language: str,
    data_dir: str,
    prompts_dir: str,
) -> OutreachResult:
    """Generate 3 LinkedIn message variants (≤300 chars each)."""
    llm = _get_llm()
    profile = read_profile(data_dir)
    contacto_prompt = _read_prompt(prompts_dir, "modes/contacto.md")

    candidate_name = profile.get("candidate", {}).get("full_name", "the candidate")
    headline = profile.get("narrative", {}).get("headline", "")
    proof_points = profile.get("narrative", {}).get("proof_points", [])
    proof_str = "; ".join(
        f"{p.get('name', '')}: {p.get('hero_metric', '')}"
        for p in (proof_points or [])[:3]
        if isinstance(p, dict)
    )

    # Load report snippet if available
    report_snippet = ""
    if report_id:
        reports_dir = Path(data_dir) / "reports"
        matches = list(reports_dir.glob(f"{report_id}-*.md"))
        if matches:
            report_snippet = matches[0].read_text(encoding="utf-8")[:500]

    lang_instruction = "Write in English." if language == "en" else f"Write in {language}."

    msg = await llm.ainvoke([
        SystemMessage(content=contacto_prompt or "You are a LinkedIn outreach expert. Write compelling, concise connection messages."),
        HumanMessage(content=f"""Generate 3 LinkedIn connection message variants for:
- Sending to: {contact.name}, {contact.title} at {contact.company}
- From: {candidate_name} — {headline}
- Key proof: {proof_str or 'strong background in the field'}
- Context: {report_snippet or f'Interested in roles at {contact.company}'}

Rules:
- MAXIMUM 300 characters each (hard limit)
- 3-sentence structure: Hook (specific to their work) → Proof (quantified) → Ask (15-min chat)
- No "I hope this finds you well", no corporate-speak
- {lang_instruction}
- Each variant should have a different angle

Reply with ONLY this JSON:
{{"messages": ["variant 1", "variant 2", "variant 3"]}}"""),
    ])

    text = msg.content if isinstance(msg.content, str) else str(msg.content)
    try:
        m = re.search(r"\{.*\}", text, re.DOTALL)
        data = json.loads(m.group()) if m else {}
        messages = data.get("messages", [])[:3]
        # Enforce 300 char limit
        messages = [msg[:300] for msg in messages]
    except Exception:
        messages = [f"Hi {contact.name}, your work at {contact.company} caught my attention. {headline}. Would love a 15-min chat."[:300]]

    return OutreachResult(
        contact=contact,
        messages=messages,
        char_counts=[len(m) for m in messages],
    )
