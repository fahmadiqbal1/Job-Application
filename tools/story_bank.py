"""Story bank I/O — reads/writes interview-prep/story-bank.md."""

from __future__ import annotations

import re
from pathlib import Path

from models.schemas import StoryEntry


def _story_path(data_dir: str) -> Path:
    return Path(data_dir) / "story-bank.md"


def _ensure_story_bank(data_dir: str) -> None:
    path = _story_path(data_dir)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# Story Bank\n\n", encoding="utf-8")


def read_stories(data_dir: str) -> list[StoryEntry]:
    _ensure_story_bank(data_dir)
    path = _story_path(data_dir)
    text = path.read_text(encoding="utf-8")

    stories: list[StoryEntry] = []
    current: dict = {}

    for line in text.splitlines():
        if line.startswith("## "):
            if current.get("title"):
                stories.append(_dict_to_story(current))
            current = {"title": line[3:].strip()}
        elif line.startswith("**S:**") or line.lower().startswith("**situation"):
            current["situation"] = line.split(":", 1)[-1].strip().strip("*")
        elif line.startswith("**T:**") or line.lower().startswith("**task"):
            current["task"] = line.split(":", 1)[-1].strip().strip("*")
        elif line.startswith("**A:**") or line.lower().startswith("**action"):
            current["action"] = line.split(":", 1)[-1].strip().strip("*")
        elif line.startswith("**R:**") or line.lower().startswith("**result"):
            current["result"] = line.split(":", 1)[-1].strip().strip("*")
        elif line.lower().startswith("**reflection"):
            current["reflection"] = line.split(":", 1)[-1].strip().strip("*")
        elif line.lower().startswith("**archetypes"):
            tags = re.findall(r"[\w\s]+", line.split(":", 1)[-1])
            current["archetypes"] = [t.strip() for t in tags if t.strip()]

    if current.get("title"):
        stories.append(_dict_to_story(current))

    return stories


def _dict_to_story(d: dict) -> StoryEntry:
    return StoryEntry(
        title=d.get("title", ""),
        situation=d.get("situation", ""),
        task=d.get("task", ""),
        action=d.get("action", ""),
        result=d.get("result", ""),
        reflection=d.get("reflection", ""),
        archetypes=d.get("archetypes", []),
    )


def append_story(story: StoryEntry, data_dir: str) -> None:
    _ensure_story_bank(data_dir)
    path = _story_path(data_dir)
    with path.open("a", encoding="utf-8") as f:
        f.write(f"\n## {story.title}\n\n")
        f.write(f"**S:** {story.situation}\n\n")
        f.write(f"**T:** {story.task}\n\n")
        f.write(f"**A:** {story.action}\n\n")
        f.write(f"**R:** {story.result}\n\n")
        f.write(f"**Reflection:** {story.reflection}\n\n")
        if story.archetypes:
            f.write(f"**Archetypes:** {', '.join(story.archetypes)}\n\n")
