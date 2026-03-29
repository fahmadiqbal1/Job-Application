"""ATS analysis tools — wrap RAG system for LangChain agents."""

import hashlib
import json
import logging
from typing import Optional

from langchain.tools import tool

from config.settings import settings
from rag.resume_index import ResumeIndex
from rag.jd_analyzer import JDAnalyzer
from rag.ats_scorer import ATSScorer
from rag.resume_editor import ResumeEditor

logger = logging.getLogger(__name__)

# Singleton instances — initialized by orchestrator
_resume_index: Optional[ResumeIndex] = None
_jd_analyzer: Optional[JDAnalyzer] = None
_ats_scorer: Optional[ATSScorer] = None
_resume_editor: Optional[ResumeEditor] = None


async def initialize_ats_tools():
    """Initialize all ATS tools (called by orchestrator at startup)."""
    global _resume_index, _jd_analyzer, _ats_scorer, _resume_editor

    try:
        _resume_index = ResumeIndex(
            resume_path=settings.resume_path,
            workspace_dir=settings.ats_workspace_dir,
        )
        await _resume_index.initialize()

        _jd_analyzer = JDAnalyzer(workspace_dir=settings.ats_workspace_dir)
        await _jd_analyzer.initialize()

        _ats_scorer = ATSScorer()
        _resume_editor = ResumeEditor()

        logger.info("ATS tools initialized")
    except Exception as e:
        logger.error(f"Failed to initialize ATS tools: {e}")


@tool("analyze_job_requirements", parse_docstring=True)
async def analyze_job_requirements(job_description: str) -> str:
    """Extract structured requirements from a job description.

    Args:
        job_description: Full job description text

    Returns:
        JSON string with required_skills, years_experience, education, nice_to_have
    """
    if not _jd_analyzer:
        return json.dumps({"error": "JD analyzer not initialized"})

    try:
        # Hash the JD to avoid re-indexing
        jd_hash = hashlib.md5(job_description.encode()).hexdigest()
        doc_id = await _jd_analyzer.index_jd(job_description, jd_hash)

        if not doc_id:
            return json.dumps({"error": "Failed to index job description"})

        requirements = await _jd_analyzer.extract_requirements(doc_id)
        return json.dumps(requirements)

    except Exception as e:
        logger.error(f"analyze_job_requirements failed: {e}")
        return json.dumps({"error": str(e)})


@tool("score_resume_vs_jd", parse_docstring=True)
async def score_resume_vs_jd(
    job_title: str,
    company: str,
    jd_requirements: str,
) -> str:
    """Score resume against job requirements for ATS compatibility.

    Args:
        job_title: Job title for context
        company: Company name for context
        jd_requirements: JSON string of requirements (from analyze_job_requirements)

    Returns:
        JSON string with score (0-100), matched_keywords, missing_keywords, areas_to_improve
    """
    if not _resume_index or not _ats_scorer:
        return json.dumps({"error": "ATS tools not initialized"})

    try:
        requirements = json.loads(jd_requirements)
        resume_text = await _resume_index.get_resume_text()

        if not resume_text:
            return json.dumps({"error": "Could not read resume"})

        score_result = await _ats_scorer.score(
            resume_text=resume_text,
            jd_requirements=requirements,
            job_title=job_title,
            company=company,
        )

        return json.dumps(score_result)

    except Exception as e:
        logger.error(f"score_resume_vs_jd failed: {e}")
        return json.dumps({"error": str(e)})


@tool("generate_resume_edits", parse_docstring=True)
async def generate_resume_edits(
    job_title: str,
    missing_keywords: str,
    jd_requirements: str,
) -> str:
    """Generate resume edits to incorporate missing keywords naturally.

    Args:
        job_title: Job title for context
        missing_keywords: JSON string of list of missing keywords
        jd_requirements: JSON string of JD requirements

    Returns:
        JSON string with edits list and edited_full_resume
    """
    if not _resume_index or not _resume_editor:
        return json.dumps({"error": "Resume editor not initialized"})

    try:
        resume_text = await _resume_index.get_resume_text()
        if not resume_text:
            return json.dumps({"error": "Could not read resume"})

        missing = json.loads(missing_keywords)
        requirements = json.loads(jd_requirements)

        edits_result = await _resume_editor.generate_edits(
            resume_text=resume_text,
            missing_keywords=missing,
            jd_requirements=requirements,
            job_title=job_title,
        )

        return json.dumps(edits_result)

    except Exception as e:
        logger.error(f"generate_resume_edits failed: {e}")
        return json.dumps({"error": str(e)})


@tool("get_resume_structure", parse_docstring=True)
async def get_resume_structure() -> str:
    """Get resume structure as JSON (for ATS analysis context).

    Returns:
        JSON string of resume structure (sections, content overview)
    """
    if not _resume_index:
        return json.dumps({"error": "Resume index not initialized"})

    try:
        structure = await _resume_index.get_resume_structure()
        if not structure:
            return json.dumps({"error": "Could not get resume structure"})
        return structure
    except Exception as e:
        logger.error(f"get_resume_structure failed: {e}")
        return json.dumps({"error": str(e)})
