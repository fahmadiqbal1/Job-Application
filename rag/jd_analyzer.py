"""Job Description analyzer — extract requirements via PageIndex."""

import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class JDAnalyzer:
    """Analyzes job descriptions to extract requirements and skills."""

    def __init__(self, workspace_dir: str):
        """
        Initialize JD analyzer.

        Args:
            workspace_dir: PageIndex workspace directory
        """
        self.workspace_dir = workspace_dir
        self._client = None
        self._indexed_jds = {}  # URL → doc_id mapping

    async def initialize(self):
        """Initialize PageIndex client."""
        try:
            from pageindex import PageIndexClient
            from config.settings import settings

            self._client = PageIndexClient(workspace=self.workspace_dir, model=settings.model_ats)
        except ImportError:
            logger.error("PageIndex not installed")
            self._client = None

    async def index_jd(self, jd_text: str, jd_hash: str) -> Optional[str]:
        """
        Index a job description (text, not file).

        Args:
            jd_text: Full job description text
            jd_hash: Hash of JD for caching/dedup

        Returns:
            doc_id or None if failed
        """
        if not self._client:
            return None

        try:
            # Save JD as temp markdown for indexing
            import tempfile
            from pathlib import Path

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".md", delete=False, dir=self.workspace_dir
            ) as f:
                f.write(f"# Job Description\n\n{jd_text}")
                temp_path = f.name

            doc_id = await self._client.index(temp_path)
            self._indexed_jds[jd_hash] = doc_id

            # Clean up temp file
            Path(temp_path).unlink(missing_ok=True)

            logger.info(f"JD indexed: {doc_id}")
            return doc_id

        except Exception as e:
            logger.error(f"JD indexing failed: {e}")
            return None

    async def extract_requirements(self, doc_id: str) -> dict:
        """
        Extract structured requirements from a JD.

        Uses LLM to analyze the JD structure and extract:
        - Required skills
        - Years of experience
        - Education requirements
        - Nice-to-haves

        Args:
            doc_id: PageIndex document ID

        Returns:
            dict with keys: skills, years_experience, education, nice_to_have
        """
        if not self._client:
            return {}

        try:
            # Get JD structure
            structure_json = await self._client.get_document_structure(doc_id)
            jd_text = await self._client.get_page_content(doc_id, "1")

            # Use LLM to extract requirements
            from config.model_factory import get_llm
            from config.settings import settings
            from langchain_core.messages import HumanMessage

            llm = get_llm(settings.model_ats, temperature=0)

            prompt = HumanMessage(
                content=f"""Extract structured requirements from this JD.
Return ONLY valid JSON, no markdown.

{{
  "required_skills": ["skill1", "skill2"],
  "years_experience": 3,
  "education": "Bachelor's",
  "nice_to_have": ["skill3"]
}}

JD TEXT:
{jd_text[:2000]}"""
            )

            response = await llm.ainvoke([prompt])
            text = response.content.strip()

            import re

            json_match = re.search(r"\{.*\}", text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())

            return {}

        except Exception as e:
            logger.error(f"Requirement extraction failed: {e}")
            return {}
