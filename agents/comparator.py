"""Multi-offer comparison — 10-dimension weighted matrix."""

from __future__ import annotations

import json
import re
from pathlib import Path

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

from models.schemas import ComparisonDimension, ComparisonMatrix


DIMENSIONS = [
    ("North Star Alignment", 0.25),
    ("CV Match", 0.15),
    ("Level & Seniority", 0.15),
    ("Compensation", 0.10),
    ("Growth Trajectory", 0.10),
    ("Remote Quality", 0.05),
    ("Company Reputation", 0.05),
    ("Tech Stack Modernity", 0.05),
    ("Speed to Offer", 0.05),
    ("Cultural Signals", 0.05),
]


def _get_llm():
    from config.settings import settings
    return ChatAnthropic(
        model=settings.default_model,
        anthropic_api_key=settings.anthropic_api_key,
        max_tokens=4096,
    )


async def compare_reports(
    report_ids: list[str],
    data_dir: str,
    prompts_dir: str,
) -> ComparisonMatrix:
    """Compare multiple evaluated reports using the 10-dimension matrix."""
    reports_dir = Path(data_dir) / "reports"

    # Load report contents
    offer_contents: dict[str, str] = {}
    offer_meta: list[dict] = []

    for rid in report_ids:
        matches = list(reports_dir.glob(f"{rid}-*.md"))
        if not matches:
            continue
        content = matches[0].read_text(encoding="utf-8")
        offer_contents[rid] = content

        # Extract meta from header
        company = re.search(r"#.*?:\s*(.+?)\s*—", content)
        role = re.search(r"—\s*(.+)", content.split("\n")[0])
        score = re.search(r"\*\*Score:\*\*\s*([\d.]+)", content)
        offer_meta.append({
            "report_id": rid,
            "company": company.group(1).strip() if company else rid,
            "role": role.group(1).strip() if role else "",
            "score": float(score.group(1)) if score else 0.0,
        })

    if len(offer_meta) < 2:
        raise ValueError("Need at least 2 valid report IDs to compare")

    llm = _get_llm()
    dim_names = [d[0] for d in DIMENSIONS]
    dim_str = "\n".join(f"- {name} (weight {int(w*100)}%)" for name, w in DIMENSIONS)
    offers_summary = "\n\n".join(
        f"=== OFFER {meta['report_id']}: {meta['company']} — {meta['role']} ===\n{offer_contents.get(meta['report_id'], '')[:1500]}"
        for meta in offer_meta
    )

    msg = await llm.ainvoke([
        SystemMessage(content="You are a career strategist scoring multiple job offers. Reply with JSON only."),
        HumanMessage(content=f"""Score each job offer on these 10 dimensions (1-5 scale each):
{dim_str}

For each dimension, score each offer. Then provide a recommendation.

{offers_summary}

Reply with ONLY this JSON structure:
{{
  "scores": {{
    "{report_ids[0]}": {{"North Star Alignment": 4.5, "CV Match": 4.0, ...}},
    "{report_ids[1]}": {{"North Star Alignment": 3.5, "CV Match": 4.5, ...}}
  }},
  "recommendation": "Offer X is the strongest choice because..."
}}"""),
    ])

    text = msg.content if isinstance(msg.content, str) else str(msg.content)
    try:
        m = re.search(r"\{.*\}", text, re.DOTALL)
        data = json.loads(m.group()) if m else {}
    except Exception:
        data = {}

    raw_scores: dict[str, dict] = data.get("scores", {})
    recommendation = data.get("recommendation", "See scores above.")

    # Build dimensions with scores
    dimensions: list[ComparisonDimension] = []
    for dim_name, weight in DIMENSIONS:
        scores = {}
        for rid in report_ids:
            rid_scores = raw_scores.get(rid, {})
            scores[rid] = float(rid_scores.get(dim_name, 3.0))
        dimensions.append(ComparisonDimension(name=dim_name, weight=weight, scores=scores))

    # Compute weighted totals
    weighted_totals: dict[str, float] = {}
    for rid in report_ids:
        total = sum(dim.scores.get(rid, 3.0) * dim.weight for dim in dimensions)
        weighted_totals[rid] = round(total, 2)

    ranking = sorted(report_ids, key=lambda r: weighted_totals.get(r, 0), reverse=True)

    return ComparisonMatrix(
        offers=offer_meta,
        dimensions=dimensions,
        weighted_totals=weighted_totals,
        ranking=ranking,
        recommendation=recommendation,
    )
