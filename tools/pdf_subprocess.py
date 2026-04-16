"""PDF generation via Node.js subprocess (generate-pdf.mjs)."""

from __future__ import annotations

import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PDFResult:
    success: bool
    output_path: str
    pages: int = 0
    size_bytes: int = 0
    error: str = ""


def generate_pdf(
    html_content: str,
    output_path: str,
    format: str = "a4",
    scripts_dir: str = "scripts",
    node_path: str = "node",
) -> PDFResult:
    """Write HTML to a temp file, call generate-pdf.mjs, return result."""
    script = Path(scripts_dir) / "generate-pdf.mjs"
    if not script.exists():
        return PDFResult(success=False, output_path=output_path, error=f"Script not found: {script}")

    # Write HTML to temp file
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".html", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(html_content)
        tmp_path = tmp.name

    try:
        result = subprocess.run(
            [node_path, str(script), tmp_path, output_path, format],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            return PDFResult(
                success=False,
                output_path=output_path,
                error=result.stderr or result.stdout,
            )

        out_file = Path(output_path)
        pages = _extract_pages(result.stdout)
        return PDFResult(
            success=True,
            output_path=output_path,
            pages=pages,
            size_bytes=out_file.stat().st_size if out_file.exists() else 0,
        )
    except subprocess.TimeoutExpired:
        return PDFResult(success=False, output_path=output_path, error="PDF generation timed out")
    except Exception as e:
        return PDFResult(success=False, output_path=output_path, error=str(e))
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def _extract_pages(stdout: str) -> int:
    """Extract page count from generate-pdf.mjs stdout."""
    import re
    m = re.search(r"(\d+)\s+page", stdout, re.IGNORECASE)
    return int(m.group(1)) if m else 1
