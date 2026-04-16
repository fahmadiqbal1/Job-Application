"""CV and profile file I/O."""

from __future__ import annotations

from pathlib import Path

import yaml


def read_cv(data_dir: str) -> str:
    path = Path(data_dir) / "cv.md"
    return path.read_text(encoding="utf-8") if path.exists() else ""


def write_cv(content: str, data_dir: str) -> None:
    Path(data_dir).mkdir(parents=True, exist_ok=True)
    (Path(data_dir) / "cv.md").write_text(content, encoding="utf-8")


def read_profile(data_dir: str) -> dict:
    path = Path(data_dir) / "profile.yml"
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def write_profile(profile_dict: dict, data_dir: str) -> None:
    Path(data_dir).mkdir(parents=True, exist_ok=True)
    with (Path(data_dir) / "profile.yml").open("w", encoding="utf-8") as f:
        yaml.safe_dump(profile_dict, f, allow_unicode=True, default_flow_style=False)


def read_portals(config_dir: str) -> dict:
    path = Path(config_dir) / "portals.yml"
    if not path.exists():
        # Fall back to example
        path = Path(config_dir) / "portals.example.yml"
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def write_portals(portals_dict: dict, config_dir: str) -> None:
    with (Path(config_dir) / "portals.yml").open("w", encoding="utf-8") as f:
        yaml.safe_dump(portals_dict, f, allow_unicode=True, default_flow_style=False)


def read_portals_raw(config_dir: str) -> str:
    path = Path(config_dir) / "portals.yml"
    if not path.exists():
        path = Path(config_dir) / "portals.example.yml"
    return path.read_text(encoding="utf-8") if path.exists() else ""


def write_portals_raw(raw_yaml: str, config_dir: str) -> None:
    yaml.safe_load(raw_yaml)  # validate before writing
    (Path(config_dir) / "portals.yml").write_text(raw_yaml, encoding="utf-8")
