"""Cover letter generation tools."""

import asyncio

from langchain.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage

from config.resume import load_resume_text
from config.model_factory import get_llm
from config.settings import settings


@tool("load_resume_context", parse_docstring=True)
def load_resume_context() -> str:
    """Load and validate resume from PDF.

    Returns:
        Structured text of resume content.

    Raises:
        ValueError if PDF is missing or contains insufficient text.
    """
    return load_resume_text()


@tool("generate_cover_letter", parse_docstring=True)
async def generate_cover_letter(
    job_description: str, company_name: str, job_title: str, resume_context: str
) -> str:
    """Generate a tailored cover letter.

    Args:
        job_description: Full job description text.
        company_name: Target company name.
        job_title: Target job title.
        resume_context: Full resume text (from load_resume_context).

    Returns:
        Generated cover letter text.
    """
    llm = get_llm(settings.model_cover_letter, temperature=0.7)

    # Format user contact info for signature
    contact_line = settings.user_name or "Applicant"
    if settings.user_email:
        contact_line += f" | {settings.user_email}"
    if settings.user_phone:
        contact_line += f" | {settings.user_phone}"

    system_prompt = f"""You are writing a cover letter as {settings.user_name or 'the applicant'}.

Guidelines:
- Write short, direct sentences. Avoid clichés like "I am excited to leverage my expertise".
- Use quantified achievements from the resume.
- Address the specific job requirements and company.
- Keep it under 400 words.
- Sign off with: {contact_line}"""

    user_prompt = f"""Job Title: {job_title}
Company: {company_name}

Job Description:
{job_description}

Resume:
{resume_context}

Write a tailored cover letter."""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ]

    response = await llm.ainvoke(messages)
    return response.content
