"""Scan history dedup — reads/writes data/scan-history.tsv."""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path


def _history_path(data_dir: str) -> Path:
    return Path(data_dir) / "scan-history.tsv"


def _ensure_history(data_dir: str) -> None:
    path = _history_path(data_dir)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("url\tdate\tsource\ttitle\tcompany\tstatus\n", encoding="utf-8")


def is_seen(url: str, data_dir: str) -> bool:
    _ensure_history(data_dir)
    path = _history_path(data_dir)
    with path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            if row.get("url", "").strip() == url.strip():
                return True
    return False


def record(url: str, title: str, company: str, source: str, data_dir: str) -> None:
    _ensure_history(data_dir)
    path = _history_path(data_dir)
    with path.open("a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow([url, date.today().isoformat(), source, title, company, "added"])


def get_history(data_dir: str, limit: int = 100) -> list[dict]:
    _ensure_history(data_dir)
    path = _history_path(data_dir)
    rows = []
    with path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            rows.append(dict(row))
    return rows[-limit:]
