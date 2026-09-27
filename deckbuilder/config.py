"""Loads config.local.yaml and .env from the repo root.

DECKBUILDER_CONFIG overrides the config path (used for sandboxed runs).
"""
from __future__ import annotations

import os
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
REQUIRED = ["TEMPLATE_LIBRARY_ROOT", "SLIDE_LIBRARY_ROOT", "PROJECTS_ROOT"]


def load() -> dict:
    path = Path(os.environ.get("DECKBUILDER_CONFIG", REPO_ROOT / "config.local.yaml"))
    if not path.exists():
        raise SystemExit(f"Missing {path}. Copy config.example.yaml to config.local.yaml and fill it in.")
    cfg = yaml.safe_load(path.read_text()) or {}
    missing = [k for k in REQUIRED if not cfg.get(k)]
    if missing:
        raise SystemExit(f"config.local.yaml is missing values for: {', '.join(missing)}")
    cfg["BRANDS"] = cfg.get("BRANDS") or {}
    try:
        from dotenv import load_dotenv
        load_dotenv(REPO_ROOT / ".env")
    except ImportError:
        pass
    return cfg


def library_root(cfg: dict) -> Path:
    p = Path(cfg["SLIDE_LIBRARY_ROOT"])
    p.mkdir(parents=True, exist_ok=True)
    return p


def source_roots(cfg: dict) -> dict[str, Path]:
    """Every folder the slide database indexes, keyed by source name."""
    roots = {"slideworks": Path(cfg["TEMPLATE_LIBRARY_ROOT"])}
    for slug, folder in cfg["BRANDS"].items():
        if folder:
            roots[f"brand:{slug}"] = Path(folder)
    return roots
