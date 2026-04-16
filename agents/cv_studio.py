"""CV Studio — keyword injection, HTML generation, PDF output."""

from __future__ import annotations

import re
import uuid
from datetime import date
from pathlib import Path
from typing import Optional

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

from models.schemas import CVGenerateResult
from tools.cv_tools import read_cv, read_profile
from tools.pdf_subprocess import generate_pdf


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


async def extract_keywords(jd_text: str, llm=None) -> list[str]:
    """Extract 15-20 ATS keywords from JD text."""
    llm = llm or _get_llm()
    msg = await llm.ainvoke([
        SystemMessage(content="Extract ATS keywords. Reply with a JSON array only."),
        HumanMessage(content=f"""Extract the 15-20 most important ATS keywords from this job description.
Include: technical skills, tools, methodologies, domain terms, role-specific phrases.
Reply with ONLY a JSON array: ["keyword1", "keyword2", ...]

JD:
{jd_text[:3000]}"""),
    ])
    text = msg.content if isinstance(msg.content, str) else str(msg.content)
    try:
        m = re.search(r"\[.*\]", text, re.DOTALL)
        import json
        return json.loads(m.group()) if m else []
    except Exception:
        return []


async def inject_keywords(cv_md: str, keywords: list[str], profile: dict, llm=None, pdf_prompt: str = "") -> str:
    """Rewrite CV summary and reorder bullets to maximize keyword coverage."""
    llm = llm or _get_llm()
    kw_str = ", ".join(keywords)
    instruction = pdf_prompt or """Optimize this CV for the target keywords:
1. Rewrite the Professional Summary (3-4 lines) to naturally include the top 5-8 keywords
2. Reorder bullet points in each role so the most keyword-relevant bullets come first
3. Add a Core Competencies section with 6-8 keyword chips if not present
4. NEVER fabricate experience, metrics, or skills not in the original CV
5. Keyword integration must sound natural — never keyword-stuffed
Return the full optimized CV in markdown format."""

    msg = await llm.ainvoke([
        SystemMessage(content=instruction),
        HumanMessage(content=f"""Target keywords: {kw_str}

Original CV:
{cv_md}

Return the complete optimized CV in markdown."""),
    ])
    return msg.content if isinstance(msg.content, str) else str(msg.content)


def build_html(cv_md: str, profile: dict, template_path: str, format: str = "a4") -> str:
    """Substitute placeholders in cv-template.html with CV content."""
    template = Path(template_path).read_text(encoding="utf-8")

    page_width = "210mm" if format == "a4" else "8.5in"
    lang = "en"

    # Extract sections from cv_md
    name = profile.get("candidate", {}).get("full_name", "") or _extract_between(cv_md, "# ", "\n")
    email = profile.get("candidate", {}).get("email", "")
    linkedin_url = profile.get("candidate", {}).get("linkedin", "")
    portfolio_url = profile.get("candidate", {}).get("portfolio_url", "")
    location = profile.get("location", {}).get("city", "") + ", " + profile.get("location", {}).get("country", "")

    # Extract sections from markdown
    summary = _extract_section(cv_md, ["Summary", "Professional Summary", "About"])
    experience = _extract_section(cv_md, ["Experience", "Work Experience"])
    projects = _extract_section(cv_md, ["Projects", "Portfolio"])
    education = _extract_section(cv_md, ["Education"])
    skills = _extract_section(cv_md, ["Skills", "Technical Skills"])
    certs = _extract_section(cv_md, ["Certifications", "Certificates"])
    competencies = _extract_section(cv_md, ["Core Competencies", "Competencies"])

    # Convert markdown to basic HTML
    experience_html = _md_to_html(experience)
    projects_html = _md_to_html(projects)
    competencies_html = _md_to_html_competencies(competencies, skills)
    education_html = _md_to_html(education)
    certs_html = _md_to_html(certs)
    skills_html = _md_to_html(skills)

    replacements = {
        "{{LANG}}": lang,
        "{{PAGE_WIDTH}}": page_width,
        "{{NAME}}": name,
        "{{EMAIL}}": email,
        "{{LINKEDIN_URL}}": linkedin_url,
        "{{PORTFOLIO_URL}}": portfolio_url,
        "{{LOCATION}}": location.strip(", "),
        "{{SUMMARY_TEXT}}": summary,
        "{{COMPETENCIES}}": competencies_html,
        "{{EXPERIENCE}}": experience_html,
        "{{PROJECTS}}": projects_html,
        "{{EDUCATION}}": education_html,
        "{{CERTIFICATIONS}}": certs_html,
        "{{SKILLS}}": skills_html,
    }

    html = template
    for key, val in replacements.items():
        html = html.replace(key, val or "")

    return html


def _extract_between(text: str, start: str, end: str) -> str:
    idx = text.find(start)
    if idx == -1:
        return ""
    idx += len(start)
    end_idx = text.find(end, idx)
    return text[idx:end_idx].strip() if end_idx != -1 else text[idx:].strip()


def _extract_section(cv_md: str, headings: list[str]) -> str:
    """Extract content under any matching heading until the next heading."""
    lines = cv_md.splitlines()
    collecting = False
    result = []
    for line in lines:
        if line.startswith("#"):
            heading_text = line.lstrip("#").strip()
            if any(h.lower() in heading_text.lower() for h in headings):
                collecting = True
                continue
            elif collecting:
                break
        if collecting:
            result.append(line)
    return "\n".join(result).strip()


def _md_to_html(md: str) -> str:
    """Convert basic markdown to HTML."""
    if not md:
        return ""
    html = md
    # Bold
    html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
    # Headers h3/h4
    html = re.sub(r"^### (.+)$", r"<h3>\1</h3>", html, flags=re.MULTILINE)
    html = re.sub(r"^## (.+)$", r"<h2>\1</h2>", html, flags=re.MULTILINE)
    # Bullets
    html = re.sub(r"^[-*] (.+)$", r"<li>\1</li>", html, flags=re.MULTILINE)
    html = re.sub(r"(<li>.*</li>)", r"<ul>\1</ul>", html, flags=re.DOTALL)
    # Paragraphs
    html = re.sub(r"\n{2,}", "</p><p>", html)
    return f"<p>{html}</p>"


def _md_to_html_competencies(competencies: str, skills: str) -> str:
    """Convert competencies section to keyword chips."""
    source = competencies or skills
    if not source:
        return ""
    # Extract items from bullets or comma-separated
    items = []
    for line in source.splitlines():
        line = line.strip().lstrip("-*•").strip()
        if "|" in line:
            items.extend([i.strip() for i in line.split("|")])
        elif "," in line:
            items.extend([i.strip() for i in line.split(",")])
        elif line:
            items.append(line)
    chips = "".join(f'<span class="competency-chip">{item}</span>' for item in items[:12] if item)
    return f'<div class="competencies-grid">{chips}</div>'


async def generate_cv_pdf(
    jd_text: Optional[str],
    report_id: Optional[str],
    format: str,
    data_dir: str,
    scripts_dir: str,
    prompts_dir: str,
    templates_dir: str,
    node_path: str,
) -> CVGenerateResult:
    """Full pipeline: extract keywords → inject → build HTML → generate PDF."""
    llm = _get_llm()
    pdf_prompt = _read_prompt(prompts_dir, "modes/pdf.md")

    # Get JD text
    if not jd_text and report_id:
        reports_dir = Path(data_dir) / "reports"
        matches = list(reports_dir.glob(f"{report_id}-*.md"))
        if matches:
            report_content = matches[0].read_text(encoding="utf-8")
            # Extract JD from report
            jd_text = report_content[:3000]

    cv_md = read_cv(data_dir)
    profile = read_profile(data_dir)

    # Extract keywords
    keywords = await extract_keywords(jd_text or "", llm) if jd_text else []

    # Inject keywords
    injected_cv = await inject_keywords(cv_md, keywords, profile, llm, pdf_prompt) if keywords else cv_md

    # Calculate coverage
    injected_lower = injected_cv.lower()
    matched = [kw for kw in keywords if kw.lower() in injected_lower]
    coverage_pct = round(len(matched) / len(keywords) * 100) if keywords else 0

    # Build HTML
    template_path = Path(templates_dir) / "cv-template.html"
    html = build_html(injected_cv, profile, str(template_path), format)

    # Generate PDF
    cv_id = str(uuid.uuid4())[:8]
    output_dir = Path(data_dir) / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    company_slug = "cv"
    today = date.today().isoformat()
    pdf_filename = f"cv-{company_slug}-{today}-{cv_id}.pdf"
    pdf_path = str(output_dir / pdf_filename)
    html_path = str(output_dir / pdf_filename.replace(".pdf", ".html"))

    # Save HTML for preview
    Path(html_path).write_text(html, encoding="utf-8")

    pdf_result = generate_pdf(
        html_content=html,
        output_path=pdf_path,
        format=format,
        scripts_dir=scripts_dir,
        node_path=node_path,
    )

    if not pdf_result.success:
        raise RuntimeError(f"PDF generation failed: {pdf_result.error}")

    return CVGenerateResult(
        cv_id=cv_id,
        pdf_path=pdf_path,
        html_path=html_path,
        keywords_injected=matched,
        keyword_coverage_pct=coverage_pct,
        pages=pdf_result.pages,
    )


async def build_preview_html(
    jd_text: Optional[str],
    report_id: Optional[str],
    keywords: Optional[list[str]],
    data_dir: str,
    prompts_dir: str,
    templates_dir: str,
) -> str:
    """Build HTML preview without generating PDF."""
    llm = _get_llm()
    cv_md = read_cv(data_dir)
    profile = read_profile(data_dir)

    if not keywords and jd_text:
        keywords = await extract_keywords(jd_text, llm)

    injected_cv = await inject_keywords(cv_md, keywords or [], profile, llm) if keywords else cv_md

    template_path = Path(templates_dir) / "cv-template.html"
    return build_html(injected_cv, profile, str(template_path))
