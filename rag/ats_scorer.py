"""ATS scorer — compare resume vs JD, generate score and gap list."""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ATSScorer:
    """Scores resume vs job description for ATS compatibility."""

    async def score(
        self,
        resume_text: str,
        jd_requirements: dict,
        job_title: str,
        company: str,
    ) -> dict:
        """
        Score a resume against JD requirements.

        Args:
            resume_text: Full resume text
            jd_requirements: Extracted JD requirements dict
            job_title: Job title (for context)
            company: Company name (for context)

        Returns:
            dict with keys:
            - score: 0-100 ATS score
            - missing_keywords: list of keywords not found in resume
            - matched_keywords: list of keywords found
            - areas_to_improve: list of suggestions
        """
        try:
            from config.model_factory import get_llm
            from config.settings import settings
            from langchain_core.messages import HumanMessage

            llm = get_llm(settings.model_ats, temperature=0)

            required_skills = jd_requirements.get("required_skills", [])
            years_exp = jd_requirements.get("years_experience", 0)

            prompt = HumanMessage(
                content=f"""Score this resume against the JD.

Return ONLY valid JSON:
{{
  "score": 75,
  "matched_keywords": ["Python", "AWS"],
  "missing_keywords": ["Kubernetes", "Apache Spark"],
  "areas_to_improve": ["Add cloud platform experience"]
}}

JOB:
Title: {job_title}
Company: {company}
Required Skills: {', '.join(required_skills)}
Years Experience: {years_exp}

RESUME (first 1500 chars):
{resume_text[:1500]}"""
            )

            response = await llm.ainvoke([prompt])
            text = response.content.strip()

            import json
            import re

            json_match = re.search(r"\{.*\}", text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return result

            return {"score": 50, "missing_keywords": required_skills, "matched_keywords": []}

        except Exception as e:
            logger.error(f"ATS scoring failed: {e}")
            return {"score": 0, "error": str(e)}

    def color_badge(self, score: int) -> str:
        """Return a badge color for the score (green/yellow/red)."""
        if score >= 90:
            return "green"
        elif score >= 70:
            return "yellow"
        else:
            return "red"
