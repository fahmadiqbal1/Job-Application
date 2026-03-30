"""Resume extraction and validation."""

import pdfplumber
from pathlib import Path

from config.settings import settings


def load_resume_text() -> str:
    """
    Load and validate resume from PDF.

    Returns:
        Plain text of all resume pages joined.

    Raises:
        FileNotFoundError: If resume file doesn't exist.
        ValueError: If resume contains no extractable text or <200 chars.
    """
    resume_path = Path(settings.resume_path)

    if not resume_path.exists():
        raise FileNotFoundError(f"Resume not found at {resume_path}")

    try:
        with pdfplumber.open(resume_path) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {e}")

    if not text or len(text.strip()) < 200:
        raise ValueError(
            f"Resume contains insufficient text ({len(text)} chars). "
            "Ensure the PDF is readable and has at least 200 characters."
        )

    return text
