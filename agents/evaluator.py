"""A-F evaluation pipeline — LangGraph state machine.

Nodes: extract_jd → detect_archetype → block_a → block_b → block_c
       → block_d → block_e → block_f → calc_score → save_report
"""

from __future__ import annotations

import asyncio
import json
import re
import uuid
from datetime import date
from pathlib import Path
from typing import Any, Callable, Optional

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, StateGraph
from typing_extensions import TypedDict

from models.schemas import EvaluationBlock, EvaluationResult, EvaluationStreamEvent
from tools.cv_tools import read_cv, read_profile
from tools.tracker import merge_additions


# ── State ─────────────────────────────────────────────────────────────────────

class EvalState(TypedDict):
    # Input
    raw_input: str
    input_type: str          # "url" | "text"
    generate_pdf: bool
    draft_answers: bool
    # Derived
    jd_text: str
    url: str
    company: str
    role: str
    archetype: str
    # Evaluation blocks
    blocks: dict[str, str]   # phase → content
    score: float
    keywords: list[str]
    # Output
    report_id: str
    report_path: str
    pdf_path: str
    error: str
    # Runtime
    cv_text: str
    profile: dict
    data_dir: str
    scripts_dir: str
    node_path: str
    prompts_dir: str
    stream_cb: Optional[Callable]   # async callback for streaming


# ── Prompt helpers ────────────────────────────────────────────────────────────

def _read_prompt(prompts_dir: str, filename: str) -> str:
    path = Path(prompts_dir) / filename
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _build_system_prompt(state: EvalState) -> str:
    shared = _read_prompt(state["prompts_dir"], "shared.md")
    oferta = _read_prompt(state["prompts_dir"], "modes/oferta.md")
    cv = state.get("cv_text", "")
    profile = json.dumps(state.get("profile", {}), ensure_ascii=False, indent=2)

    return f"""You are an expert career advisor and recruiter.

## CANDIDATE CV
{cv}

## CANDIDATE PROFILE
{profile}

## EVALUATION INSTRUCTIONS
{oferta}

## ARCHETYPES & GLOBAL CONTEXT
{shared}

Rules:
- NEVER fabricate experience or metrics. Only cite what is in the CV.
- Be direct and specific. No generic advice.
- Always cite exact CV bullets when making a match claim.
- Score each section honestly, even if it hurts.
"""


BLOCK_LABELS = {
    "A": "Role Summary",
    "B": "CV Match",
    "C": "Level & Strategy",
    "D": "Comp & Market",
    "E": "Personalization Plan",
    "F": "Interview Prep",
}

BLOCK_PROMPTS = {
    "A": """Analyze the job description and produce Block A — Role Summary.
Include: detected archetype, domain, function, seniority level, remote policy, team size estimate, and a 2-sentence TL;DR of the role.
Format as a compact markdown table.""",

    "B": """Block B — CV Match.
Map each key JD requirement to the closest CV bullet or experience. Identify gaps and propose mitigation.
Format: two sections — (1) Match table: Requirement | CV Evidence | Strength (Strong/Partial/Weak), (2) Gaps table: Gap | Mitigation.""",

    "C": """Block C — Level & Strategy.
Analyze seniority fit: is the candidate overqualified, underqualified, or well-matched?
How should they frame their story for this specific role? Include: level positioning, narrative angle, and what to emphasize vs. downplay.""",

    "D": """Block D — Comp & Market.
Based on the role, company, and location, estimate:
- Market salary range for this role (use your training data; note if uncertain)
- Company reputation signals (funding stage, growth, glassdoor signals if known)
- Demand trend for this archetype
Format as structured markdown.""",

    "E": """Block E — Personalization Plan.
List the top 5 specific CV changes to maximize this application (reorder bullets, add keywords, rewrite summary).
List the top 3 LinkedIn profile changes.
Be specific — name the exact section and the exact change.""",

    "F": """Block F — Interview Prep.
Generate 6-8 STAR+R stories mapped to the JD requirements. For each:
- Story title
- S (Situation), T (Task), A (Action), R (Result with metric), Reflection
- Which JD requirement it addresses
Also: 3 red-flag questions this role likely asks + how to handle them.""",
}


# ── LLM factory ──────────────────────────────────────────────────────────────

def _get_llm(state: EvalState) -> ChatAnthropic:
    from config.settings import settings
    return ChatAnthropic(
        model=settings.default_model,
        anthropic_api_key=settings.anthropic_api_key,
        max_tokens=4096,
        streaming=True,
    )


# ── Nodes ─────────────────────────────────────────────────────────────────────

async def extract_jd(state: EvalState) -> dict:
    """Extract JD text from URL or use raw text directly."""
    raw = state["raw_input"].strip()

    if state["input_type"] == "text" or not raw.startswith("http"):
        return {"jd_text": raw, "url": ""}

    # URL — try Playwright, fall back to httpx
    url = raw
    jd_text = ""
    try:
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, wait_until="networkidle", timeout=15000)
            jd_text = await page.inner_text("body")
            await browser.close()
    except Exception:
        try:
            import httpx
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(url, follow_redirects=True)
                # Strip HTML tags
                jd_text = re.sub(r"<[^>]+>", " ", resp.text)
                jd_text = re.sub(r"\s+", " ", jd_text).strip()
        except Exception as e:
            return {"error": f"Failed to extract JD: {e}", "jd_text": "", "url": url}

    # Trim to 8000 chars — enough for evaluation
    jd_text = jd_text[:8000].strip()
    return {"jd_text": jd_text, "url": url}


async def detect_archetype(state: EvalState) -> dict:
    """Extract company, role, archetype from JD text."""
    jd = state.get("jd_text", "")[:3000]
    if not jd:
        return {"company": "Unknown", "role": "Unknown", "archetype": "General"}

    llm = _get_llm(state)
    msg = await llm.ainvoke([
        SystemMessage(content="Extract structured info from a job description. Reply with JSON only."),
        HumanMessage(content=f"""From this job description, extract:
1. company_name (string)
2. job_title (string)
3. archetype (one of: AI Platform Engineer, Agentic Workflows Engineer, Technical AI Product Manager, AI Solutions Architect, AI Transformation Lead, Operations Manager, Technical Program Manager, Other)

JD:
{jd}

Reply with only valid JSON: {{"company_name": "...", "job_title": "...", "archetype": "..."}}"""),
    ])

    try:
        # Extract JSON from response
        text = msg.content if isinstance(msg.content, str) else str(msg.content)
        m = re.search(r"\{.*\}", text, re.DOTALL)
        data = json.loads(m.group()) if m else {}
        return {
            "company": data.get("company_name", "Unknown"),
            "role": data.get("job_title", "Unknown"),
            "archetype": data.get("archetype", "General"),
        }
    except Exception:
        return {"company": "Unknown", "role": "Unknown", "archetype": "General"}


def _make_block_node(phase: str):
    """Factory: creates an async node for one evaluation block."""
    async def block_node(state: EvalState) -> dict:
        if state.get("error"):
            return {}

        cb = state.get("stream_cb")
        if cb:
            await cb(EvaluationStreamEvent(phase=phase, content="", done=False))

        llm = _get_llm(state)
        system = _build_system_prompt(state)
        jd = state.get("jd_text", "")
        company = state.get("company", "")
        role = state.get("role", "")
        archetype = state.get("archetype", "")
        prev_blocks = state.get("blocks", {})

        context = ""
        if prev_blocks:
            context = "\n\n## Previous evaluation blocks (for context):\n"
            for p, content in prev_blocks.items():
                context += f"\n### Block {p}: {BLOCK_LABELS.get(p, p)}\n{content}\n"

        human_content = f"""## Job Description
Company: {company}
Role: {role}
Archetype: {archetype}

{jd}
{context}

---
{BLOCK_PROMPTS[phase]}"""

        # Stream tokens
        collected = []
        async for chunk in llm.astream([
            SystemMessage(content=system),
            HumanMessage(content=human_content),
        ]):
            token = chunk.content if isinstance(chunk.content, str) else ""
            collected.append(token)
            if cb and token:
                await cb(EvaluationStreamEvent(phase=phase, content=token, done=False))

        content = "".join(collected)
        if cb:
            await cb(EvaluationStreamEvent(phase=phase, content="", done=True))

        blocks = dict(state.get("blocks", {}))
        blocks[phase] = content
        return {"blocks": blocks}

    block_node.__name__ = f"block_{phase.lower()}"
    return block_node


async def extract_keywords(state: EvalState) -> dict:
    """Extract 15-20 ATS keywords from JD."""
    jd = state.get("jd_text", "")[:3000]
    llm = _get_llm(state)
    msg = await llm.ainvoke([
        SystemMessage(content="Extract ATS keywords. Reply with JSON only."),
        HumanMessage(content=f"""Extract the 15-20 most important ATS keywords from this job description.
Include: technical skills, tools, methodologies, role-specific terms.
Reply with only valid JSON: {{"keywords": ["...", "..."]}}

JD: {jd}"""),
    ])
    try:
        text = msg.content if isinstance(msg.content, str) else str(msg.content)
        m = re.search(r"\{.*\}", text, re.DOTALL)
        data = json.loads(m.group()) if m else {}
        return {"keywords": data.get("keywords", [])}
    except Exception:
        return {"keywords": []}


async def calc_score(state: EvalState) -> dict:
    """Calculate weighted score from all blocks."""
    blocks = state.get("blocks", {})
    if not blocks:
        return {"score": 0.0}

    llm = _get_llm(state)
    all_blocks = "\n\n".join(
        f"### Block {p}: {BLOCK_LABELS.get(p, p)}\n{c}"
        for p, c in blocks.items()
    )

    msg = await llm.ainvoke([
        SystemMessage(content="You are scoring a job application evaluation. Reply with JSON only."),
        HumanMessage(content=f"""Based on these evaluation blocks, give an overall score from 1.0 to 5.0.

Scoring dimensions:
- CV Match (30%): How well does the candidate's experience match requirements?
- Role Fit (25%): Archetype alignment, seniority, domain fit
- Growth Potential (20%): Is this role a step up for the candidate?
- Comp Alignment (15%): Does the likely comp match candidate expectations?
- Application Viability (10%): Realistic chance of getting an interview?

{all_blocks}

Reply with only valid JSON: {{"score": 4.2, "reasoning": "..."}}"""),
    ])

    try:
        text = msg.content if isinstance(msg.content, str) else str(msg.content)
        m = re.search(r"\{.*\}", text, re.DOTALL)
        data = json.loads(m.group()) if m else {}
        score = float(data.get("score", 3.0))
        score = max(1.0, min(5.0, score))
        return {"score": score}
    except Exception:
        return {"score": 3.0}


async def save_report(state: EvalState) -> dict:
    """Write report to data/reports/ and create tracker addition."""
    if state.get("error"):
        return {}

    data_dir = state["data_dir"]
    reports_dir = Path(data_dir) / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    # Determine next report number
    existing = sorted(reports_dir.glob("*.md"))
    nums = []
    for f in existing:
        m = re.match(r"(\d+)-", f.name)
        if m:
            nums.append(int(m.group(1)))
    report_num = max(nums) + 1 if nums else 1
    report_id = f"{report_num:03d}"

    company = state.get("company", "unknown")
    role = state.get("role", "unknown")
    archetype = state.get("archetype", "")
    score = state.get("score", 0.0)
    url = state.get("url", "")
    today = date.today().isoformat()

    # Build slug
    slug = re.sub(r"[^\w\s-]", "", company.lower())
    slug = re.sub(r"\s+", "-", slug)[:30]

    filename = f"{report_id}-{slug}-{today}.md"
    report_path = str(reports_dir / filename)

    # Build report markdown
    blocks = state.get("blocks", {})
    blocks_md = ""
    for phase in ["A", "B", "C", "D", "E", "F"]:
        if phase in blocks:
            label = BLOCK_LABELS.get(phase, phase)
            blocks_md += f"\n## {phase}) {label}\n\n{blocks[phase]}\n"

    keywords = state.get("keywords", [])
    keywords_str = ", ".join(keywords) if keywords else "—"

    if state.get("draft_answers") and score >= 4.5:
        blocks_md += "\n## G) Draft Application Answers\n\n*Generated on high-score evaluation. Review before submitting.*\n"

    report_md = f"""# Evaluation: {company} — {role}

**Date:** {today}
**Archetype:** {archetype}
**Score:** {score}/5
**URL:** {url}
**PDF:** pending

---
{blocks_md}

---

## Keywords
{keywords_str}
"""

    Path(report_path).write_text(report_md, encoding="utf-8")

    # Write tracker addition TSV
    additions_dir = Path(data_dir) / "batch" / "tracker-additions"
    additions_dir.mkdir(parents=True, exist_ok=True)
    tsv_path = additions_dir / f"{report_id}-{slug}.tsv"
    score_str = f"{score:.1f}/5"
    pdf_emoji = "❌"
    report_link = f"[{report_id}](reports/{filename})"
    tsv_path.write_text(
        f"{report_num}\t{today}\t{company}\t{role}\tEvaluated\t{score_str}\t{pdf_emoji}\t{report_link}\t{archetype}\n",
        encoding="utf-8",
    )

    return {"report_id": report_id, "report_path": report_path}


# ── Graph ──────────────────────────────────────────────────────────────────────

def build_eval_graph() -> Any:
    g = StateGraph(EvalState)

    g.add_node("extract_jd", extract_jd)
    g.add_node("detect_archetype", detect_archetype)
    g.add_node("extract_keywords", extract_keywords)
    g.add_node("block_a", _make_block_node("A"))
    g.add_node("block_b", _make_block_node("B"))
    g.add_node("block_c", _make_block_node("C"))
    g.add_node("block_d", _make_block_node("D"))
    g.add_node("block_e", _make_block_node("E"))
    g.add_node("block_f", _make_block_node("F"))
    g.add_node("calc_score", calc_score)
    g.add_node("save_report", save_report)

    g.set_entry_point("extract_jd")
    g.add_edge("extract_jd", "detect_archetype")
    g.add_edge("detect_archetype", "extract_keywords")
    g.add_edge("extract_keywords", "block_a")
    g.add_edge("block_a", "block_b")
    g.add_edge("block_b", "block_c")
    g.add_edge("block_c", "block_d")
    g.add_edge("block_d", "block_e")
    g.add_edge("block_e", "block_f")
    g.add_edge("block_f", "calc_score")
    g.add_edge("calc_score", "save_report")
    g.add_edge("save_report", END)

    return g.compile()


# ── Public API ────────────────────────────────────────────────────────────────

async def run_evaluation(
    raw_input: str,
    data_dir: str,
    scripts_dir: str,
    prompts_dir: str,
    node_path: str = "node",
    generate_pdf: bool = False,
    draft_answers: bool = False,
    stream_cb: Optional[Callable] = None,
) -> EvaluationResult:
    """Run the full A-F evaluation pipeline."""
    from config.settings import settings

    cv_text = read_cv(data_dir)
    profile = read_profile(data_dir)

    input_type = "url" if raw_input.strip().startswith("http") else "text"

    graph = build_eval_graph()
    final_state = await graph.ainvoke({
        "raw_input": raw_input,
        "input_type": input_type,
        "generate_pdf": generate_pdf,
        "draft_answers": draft_answers,
        "jd_text": "",
        "url": "",
        "company": "",
        "role": "",
        "archetype": "",
        "blocks": {},
        "score": 0.0,
        "keywords": [],
        "report_id": "",
        "report_path": "",
        "pdf_path": "",
        "error": "",
        "cv_text": cv_text,
        "profile": profile,
        "data_dir": data_dir,
        "scripts_dir": scripts_dir,
        "node_path": node_path,
        "prompts_dir": prompts_dir,
        "stream_cb": stream_cb,
    })

    if final_state.get("error"):
        raise RuntimeError(final_state["error"])

    # Auto-merge tracker additions
    try:
        merge_additions(data_dir, scripts_dir, node_path)
    except Exception:
        pass  # non-fatal

    blocks = [
        EvaluationBlock(
            phase=phase,
            label=BLOCK_LABELS.get(phase, phase),
            content=final_state["blocks"].get(phase, ""),
        )
        for phase in ["A", "B", "C", "D", "E", "F"]
    ]

    return EvaluationResult(
        report_id=final_state["report_id"],
        company=final_state["company"],
        role=final_state["role"],
        archetype=final_state["archetype"],
        score=final_state["score"],
        blocks=blocks,
        keywords=final_state["keywords"],
        pdf_path=final_state.get("pdf_path") or None,
        report_path=final_state["report_path"],
        date=date.today().isoformat(),
        url=final_state.get("url") or None,
    )
