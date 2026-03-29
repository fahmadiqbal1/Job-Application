"""Resume indexing via PageIndex — index once, reuse for ATS analysis."""

import hashlib
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class ResumeIndex:
    """Manages resume indexing via PageIndex."""

    def __init__(self, resume_path: str, workspace_dir: str):
        """
        Initialize resume indexer.

        Args:
            resume_path: Path to resume PDF
            workspace_dir: PageIndex workspace directory for persistence
        """
        self.resume_path = Path(resume_path)
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self._client = None
        self._doc_id = None
        self._file_hash = None

    async def initialize(self):
        """Initialize PageIndex client and index resume if needed."""
        try:
            from pageindex import PageIndexClient

            self._client = PageIndexClient(
                workspace=str(self.workspace_dir),
                model="gpt-4o-mini",
            )

            # Check if resume needs re-indexing
            current_hash = self._compute_file_hash()
            hash_file = self.workspace_dir / "resume_hash.txt"

            if hash_file.exists():
                stored_hash = hash_file.read_text().strip()
                if stored_hash == current_hash:
                    # Resume unchanged — use cached doc_id
                    doc_file = self.workspace_dir / "resume_doc_id.txt"
                    if doc_file.exists():
                        self._doc_id = doc_file.read_text().strip()
                        logger.info(f"Resume already indexed (hash match): {self._doc_id}")
                        return

            # Resume changed or first time — re-index
            logger.info("Indexing resume...")
            self._doc_id = await self._client.index(str(self.resume_path))
            self._file_hash = current_hash

            # Persist hash and doc_id
            hash_file.write_text(current_hash)
            (self.workspace_dir / "resume_doc_id.txt").write_text(self._doc_id)
            logger.info(f"Resume indexed: {self._doc_id}")

        except ImportError:
            logger.error("PageIndex not installed — RAG disabled")
            self._client = None
        except Exception as e:
            logger.error(f"Resume indexing failed: {e}")
            self._client = None

    def _compute_file_hash(self) -> str:
        """Compute MD5 hash of resume file for change detection."""
        if not self.resume_path.exists():
            return ""
        return hashlib.md5(self.resume_path.read_bytes()).hexdigest()

    async def get_resume_structure(self) -> Optional[str]:
        """
        Get resume structure (JSON tree, no text content — token efficient).

        Returns:
            JSON string or None if indexing failed
        """
        if not self._client or not self._doc_id:
            return None

        try:
            return await self._client.get_document_structure(self._doc_id)
        except Exception as e:
            logger.error(f"Failed to get resume structure: {e}")
            return None

    async def get_resume_text(self, pages: str = None) -> Optional[str]:
        """
        Get resume full text or specific pages.

        Args:
            pages: Page range string, e.g. "1-2" (None = all pages)

        Returns:
            Text content or None
        """
        if not self._client or not self._doc_id:
            return None

        try:
            if pages:
                return await self._client.get_page_content(self._doc_id, pages)
            else:
                return await self._client.get_document(self._doc_id)
        except Exception as e:
            logger.error(f"Failed to get resume text: {e}")
            return None
