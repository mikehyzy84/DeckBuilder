"""`python -m deckbuilder check`: verify the machine is ready to build."""
from __future__ import annotations

import os
import shutil
import sqlite3
from pathlib import Path

from . import config as C

KEYS = [
    ("RUNWAY_API_KEY", "Runway images and motion (RUNWAYML_API_SECRET also accepted)"),
    ("GEMINI_API_KEY", "Veo hero video via AI Studio"),
    ("PEXELS_API_KEY", "stock photos"),
    ("PIXABAY_API_KEY", "stock photos"),
    ("ANTHROPIC_API_KEY", "optional; Claude Code itself does not need it"),
]


def run(cfg: dict) -> int:
    ok = True

    def line(good: bool, msg: str) -> None:
        nonlocal ok
        ok &= good
        print(("OK   " if good else "FAIL ") + msg)

    for k in ("TEMPLATE_LIBRARY_ROOT", "SLIDE_LIBRARY_ROOT", "PROJECTS_ROOT"):
        line(Path(cfg[k]).exists(), f"{k}: {cfg[k]}")
    for slug, folder in cfg["BRANDS"].items():
        line(Path(folder).exists(), f"brand {slug}: {folder}")
        line((C.REPO_ROOT / "docs" / "brands" / slug / "brand-spec.md").exists(), f"brand spec docs/brands/{slug}/brand-spec.md")
    line((C.REPO_ROOT / "docs" / "best-practices.md").exists(), "docs/best-practices.md")

    db = Path(cfg["SLIDE_LIBRARY_ROOT"]) / "slides.db"
    if db.exists():
        con = sqlite3.connect(db)
        n, r = con.execute("SELECT count(*), sum(rendered) FROM decks").fetchone()
        s = con.execute("SELECT count(*) FROM slides").fetchone()[0]
        line(n == r, f"slide database: {n} decks, {s} slides, {r} rendered")
    else:
        line(False, "slide database missing. Run: python -m deckbuilder library build")

    try:
        from .render import find_soffice
        line(True, f"LibreOffice: {find_soffice(cfg)}")
    except SystemExit as e:
        line(False, str(e))

    for mod in ("pptx", "yaml", "dotenv", "PIL", "requests", "fitz", "google.genai", "lxml"):
        try:
            __import__(mod)
            line(True, f"python module {mod}")
        except ImportError:
            line(False, f"python module {mod} missing. Run: pip install -r requirements.txt")

    for k, why in KEYS:
        present = bool(os.environ.get(k) or (k == "RUNWAY_API_KEY" and os.environ.get("RUNWAYML_API_SECRET")))
        if k == "ANTHROPIC_API_KEY":
            print(("OK   " if present else "INFO ") + f"{k} ({why})")
        else:
            line(present, f"{k} ({why})")

    line(shutil.which("git") is not None, "git installed")

    # live key checks that cost nothing
    import requests
    rk = os.environ.get("RUNWAY_API_KEY") or os.environ.get("RUNWAYML_API_SECRET")
    if rk:
        try:
            r = requests.get(f"{cfg['RUNWAY']['api_base']}/organization", timeout=20,
                             headers={"Authorization": f"Bearer {rk}", "X-Runway-Version": cfg["RUNWAY"]["api_version"]})
            line(r.ok, f"Runway key live (credit balance: {r.json().get('creditBalance') if r.ok else r.status_code})")
        except Exception as e:
            line(False, f"Runway key check failed: {type(e).__name__} (network or key problem)")
    gk = os.environ.get("GEMINI_API_KEY")
    if gk:
        try:
            r = requests.get("https://generativelanguage.googleapis.com/v1beta/models", params={"pageSize": 1000},
                             headers={"x-goog-api-key": gk}, timeout=20)
            veo = [m["name"].split("/")[-1] for m in r.json().get("models", []) if "veo" in m["name"]] if r.ok else []
            line(r.ok, f"Gemini key live; Veo models visible: {veo or 'none'}")
            if r.ok and veo and cfg["VEO"]["model"] not in veo:
                line(False, f"VEO.model {cfg['VEO']['model']} not in available models; update config.local.yaml")
        except Exception as e:
            line(False, f"Gemini key check failed: {type(e).__name__} (network or key problem)")
    pk = os.environ.get("PEXELS_API_KEY")
    if pk:
        try:
            r = requests.get("https://api.pexels.com/v1/search", params={"query": "office", "per_page": 1},
                             headers={"Authorization": pk}, timeout=20)
            line(r.ok, f"Pexels key live ({r.status_code})")
        except Exception as e:
            line(False, f"Pexels key check failed: {type(e).__name__} (network or key problem)")
    xk = os.environ.get("PIXABAY_API_KEY")
    if xk:
        try:
            r = requests.get("https://pixabay.com/api/", params={"key": xk, "q": "office", "per_page": 3}, timeout=20)
            line(r.ok, f"Pixabay key live ({r.status_code})")
        except Exception as e:
            line(False, f"Pixabay key check failed: {type(e).__name__} (network or key problem)")
    print("\nREADY" if ok else "\nNOT READY: fix the FAIL lines above.")
    return 0 if ok else 1
