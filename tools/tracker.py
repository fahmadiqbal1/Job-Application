"""Application tracker I/O — reads/writes data/applications.md."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Optional

from models.schemas import ApplicationEntry, FunnelData, ScoreTrendPoint, TrackerStats

# Canonical status order for funnel (lowest → highest)
FUNNEL_ORDER = ["Evaluated", "Applied", "Responded", "Interview", "Offer"]
TERMINAL = ["Rejected", "Discarded", "SKIP"]


def _parse_score(score_str: str) -> Optional[float]:
    """Parse '4.2/5' → 4.2, 'N/A' → None."""
    m = re.match(r"([\d.]+)/5", score_str.strip())
    return float(m.group(1)) if m else None


def _parse_bool(val: str) -> bool:
    return "✅" in val or val.strip().lower() in ("true", "yes", "1")


def _apps_path(data_dir: str) -> Path:
    return Path(data_dir) / "applications.md"


def read_applications(data_dir: str) -> list[ApplicationEntry]:
    """Parse the markdown table in applications.md into ApplicationEntry objects."""
    path = _apps_path(data_dir)
    if not path.exists():
        return []

    entries: list[ApplicationEntry] = []
    in_table = False

    for line in path.read_text(encoding="utf-8").splitlines():
        # Detect table start
        if line.startswith("| #") or line.startswith("|#"):
            in_table = True
            continue
        if in_table and line.startswith("|---"):
            continue
        if in_table and line.startswith("|") and line.strip() != "|":
            cols = [c.strip() for c in line.strip("|").split("|")]
            if len(cols) < 8:
                continue
            try:
                # Column order: # | Date | Company | Role | Score | Status | PDF | Report | Notes
                num_str = cols[0].strip()
                if not num_str.isdigit():
                    continue
                num = int(num_str)
                date = cols[1]
                company = cols[2]
                role = cols[3]
                score = cols[4]
                status = cols[5]
                pdf = _parse_bool(cols[6])
                report_col = cols[7]
                notes = cols[8] if len(cols) > 8 else ""

                # Extract report path from markdown link [num](path)
                report_path = None
                m = re.search(r"\]\(([^)]+)\)", report_col)
                if m:
                    report_path = m.group(1)

                entries.append(ApplicationEntry(
                    num=num,
                    date=date,
                    company=company,
                    role=role,
                    score=score,
                    status=status,
                    pdf=pdf,
                    report_path=report_path,
                    notes=notes,
                ))
            except (ValueError, IndexError):
                continue

    return entries


def get_stats(entries: list[ApplicationEntry]) -> TrackerStats:
    """Aggregate tracker entries into KPI stats."""
    by_status: dict[str, int] = {}
    for e in entries:
        by_status[e.status] = by_status.get(e.status, 0) + 1

    scores = [_parse_score(e.score) for e in entries if _parse_score(e.score) is not None]
    avg_score = round(sum(scores) / len(scores), 2) if scores else None

    total = len(entries)
    pdf_count = sum(1 for e in entries if e.pdf)
    report_count = sum(1 for e in entries if e.report_path)

    return TrackerStats(
        total=total,
        by_status=by_status,
        avg_score=avg_score,
        pdf_coverage_pct=round(pdf_count / total * 100) if total else 0,
        report_coverage_pct=round(report_count / total * 100) if total else 0,
    )


def get_funnel(entries: list[ApplicationEntry]) -> FunnelData:
    """Build funnel data (Evaluated → Offer) for visualization."""
    by_status = get_stats(entries).by_status
    total = len(entries)

    # Cumulative funnel: each stage includes all stages above it
    cumulative: list[dict] = []
    running = total
    for stage in FUNNEL_ORDER:
        count = by_status.get(stage, 0)
        cumulative.append({
            "name": stage,
            "count": running,
            "stage_count": count,
            "pct": round(running / total * 100) if total else 0,
        })
        running -= count

    return FunnelData(stages=cumulative)


def get_score_trends(entries: list[ApplicationEntry]) -> list[ScoreTrendPoint]:
    """Return entries sorted by date for score-over-time visualization."""
    points = []
    for e in entries:
        score = _parse_score(e.score)
        if score is None:
            continue
        points.append(ScoreTrendPoint(
            date=e.date,
            score=score,
            company=e.company,
            role=e.role,
            archetype="",  # enriched later by evaluator if needed
        ))
    return sorted(points, key=lambda p: p.date)


def update_entry(num: int, field: str, value: str, data_dir: str) -> bool:
    """Edit a single field in an applications.md row in-place."""
    path = _apps_path(data_dir)
    if not path.exists():
        return False

    lines = path.read_text(encoding="utf-8").splitlines()
    updated = False

    FIELD_COL = {
        "status": 5,
        "notes": 8,
        "pdf": 6,
        "score": 4,
    }
    col_idx = FIELD_COL.get(field)
    if col_idx is None:
        return False

    new_lines = []
    for line in lines:
        if line.startswith("|") and not line.startswith("|---") and not line.startswith("| #"):
            cols = [c.strip() for c in line.strip("|").split("|")]
            if len(cols) >= 2 and cols[0].isdigit() and int(cols[0]) == num:
                cols[col_idx] = value
                line = "| " + " | ".join(cols) + " |"
                updated = True
        new_lines.append(line)

    if updated:
        path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    return updated


def merge_additions(data_dir: str, scripts_dir: str, node_path: str = "node") -> dict:
    """Call node scripts/merge-tracker.mjs to merge TSV additions into applications.md."""
    script = Path(scripts_dir) / "merge-tracker.mjs"
    result = subprocess.run(
        [node_path, str(script)],
        cwd=str(Path(data_dir).parent),
        capture_output=True,
        text=True,
        timeout=30,
    )
    return {
        "success": result.returncode == 0,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }
