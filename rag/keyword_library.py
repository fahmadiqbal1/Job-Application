"""Keyword library — persist and track keywords per job type."""

import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class KeywordLibrary:
    """
    Maintains a persistent library of keywords by job type.

    Learns from every JD processed, building a growing pool of
    keywords per role type (e.g. "AI Program Manager", "DevOps", etc).
    """

    def __init__(self, library_path: str = "state/keyword_library.json"):
        """
        Initialize keyword library.

        Args:
            library_path: Path to persist keywords JSON
        """
        self.library_path = Path(library_path)
        self._keywords = self._load()

    def _load(self) -> dict:
        """Load keyword library from disk."""
        if self.library_path.exists():
            try:
                import orjson
                return orjson.loads(self.library_path.read_bytes())
            except Exception as e:
                logger.warning(f"Failed to load keyword library: {e}")
        return {}

    def _save(self):
        """Save keyword library to disk."""
        try:
            import orjson
            self.library_path.parent.mkdir(parents=True, exist_ok=True)
            self.library_path.write_bytes(
                orjson.dumps(self._keywords, option=orjson.OPT_INDENT_2)
            )
        except Exception as e:
            logger.warning(f"Failed to save keyword library: {e}")

    def add_keywords(self, role_type: str, keywords: list[str]) -> None:
        """
        Add keywords for a role type.

        Args:
            role_type: e.g. "AI Program Manager", "DevOps Engineer"
            keywords: List of keywords to add
        """
        if role_type not in self._keywords:
            self._keywords[role_type] = {"keywords": [], "frequency": {}}

        lib = self._keywords[role_type]
        for kw in keywords:
            if kw not in lib["keywords"]:
                lib["keywords"].append(kw)
            lib["frequency"][kw] = lib["frequency"].get(kw, 0) + 1

        self._save()
        logger.info(f"Added keywords for {role_type}: {len(keywords)} keywords")

    def get_keywords(self, role_type: str) -> list[str]:
        """
        Get all keywords for a role type, sorted by frequency.

        Args:
            role_type: e.g. "AI Program Manager"

        Returns:
            List of keywords (most frequent first)
        """
        if role_type not in self._keywords:
            return []

        lib = self._keywords[role_type]
        keywords = lib["keywords"]
        freq = lib["frequency"]

        # Sort by frequency descending
        sorted_kw = sorted(keywords, key=lambda k: freq.get(k, 0), reverse=True)
        return sorted_kw

    def get_top_keywords(self, role_type: str, n: int = 10) -> list[str]:
        """Get the top N keywords for a role type."""
        return self.get_keywords(role_type)[:n]

    def infer_role_type(self, job_title: str) -> Optional[str]:
        """
        Try to infer a role type from job title.

        Args:
            job_title: e.g. "Senior AI Program Manager"

        Returns:
            Matching role type from library, or None
        """
        title_lower = job_title.lower()
        for role_type in self._keywords:
            if role_type.lower() in title_lower or title_lower in role_type.lower():
                return role_type
        return None
