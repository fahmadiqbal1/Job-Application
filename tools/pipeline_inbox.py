"""URL inbox I/O — reads/writes data/pipeline.md."""

from __future__ import annotations

import re
from pathlib import Path


def _pipeline_path(data_dir: str) -> Path:
    return Path(data_dir) / "pipeline.md"


def get_pipeline_path(data_dir: str) -> str:
    return str(_pipeline_path(data_dir))


def _ensure_pipeline(data_dir: str) -> None:
    path = _pipeline_path(data_dir)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# Pipeline\n\n## Pendientes\n\n## Procesadas\n", encoding="utf-8")


def read_pending(data_dir: str) -> list[dict]:
    _ensure_pipeline(data_dir)
    path = _pipeline_path(data_dir)
    text = path.read_text(encoding="utf-8")

    pending = []
    in_pending = False
    for line in text.splitlines():
        if "## Pendientes" in line or "## Pending" in line:
            in_pending = True
            continue
        if line.startswith("##"):
            in_pending = False
        if in_pending and line.startswith("- [ ]"):
            content = line[5:].strip()
            # Parse "URL | Company | Role" format
            parts = [p.strip() for p in content.split("|")]
            pending.append({
                "url": parts[0] if parts else content,
                "company": parts[1] if len(parts) > 1 else "",
                "role": parts[2] if len(parts) > 2 else "",
            })
    return pending


def add_url(url: str, company: str, title: str, data_dir: str) -> None:
    _ensure_pipeline(data_dir)
    path = _pipeline_path(data_dir)
    text = path.read_text(encoding="utf-8")

    entry = f"- [ ] {url}"
    if company:
        entry += f" | {company}"
    if title:
        entry += f" | {title}"

    # Insert after "## Pendientes" line
    lines = text.splitlines()
    new_lines = []
    inserted = False
    for line in lines:
        new_lines.append(line)
        if not inserted and ("## Pendientes" in line or "## Pending" in line):
            new_lines.append(entry)
            inserted = True

    if not inserted:
        new_lines.append(entry)

    path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")


def mark_processed(url: str, report_num: str, score: str, data_dir: str) -> None:
    path = _pipeline_path(data_dir)
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    # Move matching pending line to processed
    new_lines = []
    processed_entry = None
    for line in text.splitlines():
        if line.startswith("- [ ]") and url in line:
            content = line[5:].strip()
            processed_entry = f"- [x] #{report_num} | {content} | {score}/5"
        else:
            new_lines.append(line)

    if processed_entry:
        # Append to Procesadas section
        final_lines = []
        in_processed = False
        appended = False
        for line in new_lines:
            final_lines.append(line)
            if "## Procesadas" in line or "## Processed" in line:
                in_processed = True
                final_lines.append(processed_entry)
                appended = True
        if not appended:
            final_lines.append("\n## Procesadas")
            final_lines.append(processed_entry)
        path.write_text("\n".join(final_lines) + "\n", encoding="utf-8")
