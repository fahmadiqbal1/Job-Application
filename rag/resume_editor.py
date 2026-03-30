"""Resume editor — rewrite resume sections to match JD keywords."""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ResumeEditor:
    """Edits resume to improve ATS score by naturally incorporating missing keywords."""

    async def generate_edits(
        self,
        resume_text: str,
        missing_keywords: list[str],
        jd_requirements: dict,
        job_title: str,
    ) -> dict:
        """
        Generate resume edits to incorporate missing keywords.

        Returns a dict of edit suggestions:
        {
            "edits": [
                {"original": "...", "edited": "...", "reason": "..."},
                ...
            ],
            "edited_resume": "full edited resume text"
        }

        Args:
            resume_text: Full resume text
            missing_keywords: Keywords not found in resume
            jd_requirements: JD requirements dict
            job_title: Job title for context

        Returns:
            dict with edits and full edited resume
        """
        try:
            if not missing_keywords:
                return {
                    "edits": [],
                    "edited_resume": resume_text,
                    "score_before": 100,
                    "score_after": 100,
                }

            from config.model_factory import get_llm
            from config.settings import settings
            from langchain_core.messages import HumanMessage

            llm = get_llm(settings.model_ats, temperature=0.5)

            keywords_str = ", ".join(missing_keywords[:5])  # Top 5 most critical

            prompt = HumanMessage(
                content=f"""Edit this resume to naturally incorporate missing keywords.
DO NOT:
- Add keywords as a list
- Use keywords in awkward ways
- Change the person's actual experience
- Make things up

DO:
- Rewrite sentences to include keywords naturally
- Keep professional tone
- Each edit should be a full sentence replacement
- Total edits: 3-5 top sentences

Return JSON:
{{
  "edits": [
    {{"original": "...", "edited": "...", "reason": "added Kubernetes"}}
  ],
  "edited_full_resume": "full resume text with edits applied"
}}

RESUME:
{resume_text[:1500]}

MISSING KEYWORDS (add these naturally):
{keywords_str}

JOB TITLE: {job_title}"""
            )

            response = await llm.ainvoke([prompt])
            text = response.content.strip()

            import json
            import re

            json_match = re.search(r"\{.*\}", text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return result

            return {
                "edits": [],
                "edited_resume": resume_text,
                "error": "Could not generate edits",
            }

        except Exception as e:
            logger.error(f"Resume editing failed: {e}")
            return {
                "edits": [],
                "edited_resume": resume_text,
                "error": str(e),
            }

    async def apply_edits(self, resume_text: str, edits: list[dict]) -> str:
        """
        Apply a list of edits to resume text.

        Args:
            resume_text: Original resume text
            edits: List of {"original": "...", "edited": "..."} dicts

        Returns:
            Edited resume text
        """
        edited = resume_text
        for edit in edits:
            original = edit.get("original", "")
            new = edit.get("edited", "")
            if original and new and original in edited:
                edited = edited.replace(original, new, 1)  # Replace first occurrence
        return edited
