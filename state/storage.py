"""File-based state storage for job application runs."""

import orjson
from pathlib import Path

RUNS_DIR = Path("D:/Projects/Job Application/state/runs")


def save_state(state: dict) -> None:
    """Save application state to JSON file atomically."""
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    path = RUNS_DIR / f"{state['run_id']}.json"
    tmp = path.with_suffix(".tmp")
    tmp.write_bytes(orjson.dumps(state, option=orjson.OPT_INDENT_2))
    tmp.replace(path)


def load_state(run_id: str) -> dict | None:
    """Load application state from JSON file, or None if not found."""
    path = RUNS_DIR / f"{run_id}.json"
    if not path.exists():
        return None
    return orjson.loads(path.read_bytes())


def load_latest_state() -> dict | None:
    """Load the most recently modified state file."""
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    files = list(RUNS_DIR.glob("*.json"))
    if not files:
        return None
    latest = max(files, key=lambda p: p.stat().st_mtime)
    return orjson.loads(latest.read_bytes())
