"""Project folders: create the standard structure and inventory what is inside."""
from __future__ import annotations

from pathlib import Path

import yaml

PROJECT_YAML = """# DeckBuilder project settings. Claude fills blanks by asking Mike, never by assuming.
name: "{name}"
# Absolute path to the brand folder for this deck, or a slug from BRANDS in config.local.yaml.
# Leave blank for an unbranded deck that follows design-guide/ only.
brand: ""
audience: ""
objective: ""
decision_or_takeaway: ""
target_slide_count:
presenter:
date:
"""

CONTEXT_EXT = {".pdf", ".docx", ".doc", ".pptx", ".xlsx", ".csv", ".md", ".txt", ".json", ".png", ".jpg", ".jpeg"}


def new(cfg: dict, name: str) -> Path:
    root = Path(cfg["PROJECTS_ROOT"]) / name
    for sub in ("context", "design-guide", "output/assets", "output/qa"):
        (root / sub).mkdir(parents=True, exist_ok=True)
    y = root / "project.yaml"
    if not y.exists():
        y.write_text(PROJECT_YAML.format(name=name))
    return root


def scan(folder: Path) -> dict:
    folder = Path(folder)
    if not folder.exists():
        raise SystemExit(f"Project folder not found: {folder}")
    out: dict = {"project": str(folder), "missing": []}
    for sub in ("context", "design-guide", "output"):
        if not (folder / sub).exists():
            out["missing"].append(sub)
    settings = folder / "project.yaml"
    out["settings"] = yaml.safe_load(settings.read_text()) if settings.exists() else None
    if out["settings"] is None:
        out["missing"].append("project.yaml")
    for sub in ("context", "design-guide"):
        files = [p for p in (folder / sub).rglob("*") if p.is_file() and not p.name.startswith((".", "~$"))] if (folder / sub).exists() else []
        out[sub] = [{"path": str(p.relative_to(folder)), "kb": round(p.stat().st_size / 1024), "readable": p.suffix.lower() in CONTEXT_EXT}
                    for p in sorted(files)]
    if out["settings"]:
        out["blank_fields"] = [k for k, v in out["settings"].items() if v in (None, "")]
    return out
