"""Brand extraction.

A brand is any folder Mike points at: CGI, a client, a partner. It can hold a PowerPoint
master (.potx/.pptx), guideline PDFs, logos, fonts. `extract` reads it in place and writes
docs/brands/<slug>/brand.json plus a draft docs/brands/<slug>/brand-spec.md for Claude to
complete and Mike to approve. It also registers the brand's decks in the slide database.
"""
from __future__ import annotations

import json
import re
import zipfile
from pathlib import Path

from . import config as C
from .pptx_utils import emu_to_in, open_presentation

NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
DECKS = {".pptx", ".potx"}
DOCS = {".pdf", ".docx", ".md", ".txt"}
IMAGES = {".png", ".jpg", ".jpeg", ".svg", ".eps", ".ai", ".emf"}
FONTS = {".ttf", ".otf", ".woff", ".woff2"}


def _theme(deck: Path) -> dict:
    from lxml import etree
    with zipfile.ZipFile(deck) as z:
        names = sorted(n for n in z.namelist() if re.fullmatch(r"ppt/theme/theme\d+\.xml", n))
        if not names:
            return {}
        root = etree.fromstring(z.read(names[0]))
    out = {"colors": {}, "fonts": {}}
    scheme = root.find(".//a:clrScheme", NS)
    if scheme is not None:
        out["color_scheme_name"] = scheme.get("name")
        for el in scheme:
            tag = etree.QName(el).localname
            c = el[0]
            val = c.get("val") if etree.QName(c).localname == "srgbClr" else c.get("lastClr")
            out["colors"][tag] = f"#{val}" if val else None
    fs = root.find(".//a:fontScheme", NS)
    if fs is not None:
        maj = fs.find("a:majorFont/a:latin", NS)
        mnr = fs.find("a:minorFont/a:latin", NS)
        out["fonts"] = {"heading": maj.get("typeface") if maj is not None else None,
                        "body": mnr.get("typeface") if mnr is not None else None}
    return out


def _pick_master(decks: list[Path]) -> Path | None:
    """Prefer a file that looks like the standard template: many layouts, few sample slides."""
    best, key = None, None
    for d in decks:
        try:
            prs = open_presentation(d)
        except Exception:
            continue
        layouts = sum(len(m.slide_layouts) for m in prs.slide_masters)
        name = d.name.lower()
        score = (("standard" in name) * 3 + ("master" in name) * 3 + ("template" in name)
                 - ("timesaver" in name) * 2 - ("library" in name) * 2)
        k = (score, -len(prs.slide_masters), layouts, -len(prs.slides), d.stat().st_mtime)
        if key is None or k > key:
            best, key = d, k
    return best


def _layout_table(prs) -> list[dict]:
    rows = []
    for mi, m in enumerate(prs.slide_masters):
        for li, lay in enumerate(m.slide_layouts):
            ph = []
            for p in lay.placeholders:
                try:
                    ph.append(f"{p.placeholder_format.idx}:{str(p.placeholder_format.type).split('.')[-1].split(' ')[0]}")
                except Exception:
                    pass
            rows.append({"master": mi, "index": li, "name": lay.name, "placeholders": ph})
    return rows


def _master_logos(deck: Path) -> list[dict]:
    """Pictures placed on the slide master or layouts are usually the logo."""
    prs = open_presentation(deck)
    found = []
    for m in prs.slide_masters:
        for sh in m.shapes:
            if sh.shape_type == 13:
                found.append({"where": "master", "left_in": emu_to_in(sh.left), "top_in": emu_to_in(sh.top),
                              "width_in": emu_to_in(sh.width), "height_in": emu_to_in(sh.height), "name": sh.name})
        for lay in m.slide_layouts:
            for sh in lay.shapes:
                if sh.shape_type == 13 and "logo" in sh.name.lower():
                    found.append({"where": f"layout:{lay.name}", "left_in": emu_to_in(sh.left), "top_in": emu_to_in(sh.top),
                                  "width_in": emu_to_in(sh.width), "height_in": emu_to_in(sh.height), "name": sh.name})
    return found


def extract(cfg: dict, folder: Path, slug: str, master: str | None = None) -> str:
    folder = Path(folder)
    if not folder.exists():
        raise SystemExit(f"Brand folder not found: {folder}")
    files = [p for p in folder.rglob("*") if p.is_file() and not p.name.startswith(("~$", "."))]
    decks = [p for p in files if p.suffix.lower() in DECKS]
    master_path = (folder / master) if master else _pick_master(decks)
    info: dict = {
        "slug": slug, "folder": str(folder),
        "master_template": str(master_path) if master_path else None,
        "decks": [str(p) for p in decks],
        "guideline_docs": [str(p) for p in files if p.suffix.lower() in DOCS],
        "images": [str(p) for p in files if p.suffix.lower() in IMAGES][:200],
        "font_files": [str(p) for p in files if p.suffix.lower() in FONTS],
    }
    if master_path:
        from .pptx_utils import potx_to_pptx
        src = potx_to_pptx(master_path) if master_path.suffix.lower() == ".potx" else master_path
        info["theme"] = _theme(src)
        prs = open_presentation(src)
        info["slide_size_in"] = [emu_to_in(prs.slide_width), emu_to_in(prs.slide_height)]
        info["layouts"] = _layout_table(prs)
        info["master_logos"] = _master_logos(src)
    out_dir = C.REPO_ROOT / "docs" / "brands" / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "brand.json").write_text(json.dumps(info, indent=1))
    spec = out_dir / "brand-spec.md"
    existed = spec.exists()
    if not existed:
        spec.write_text(_draft(info))
    return f"wrote {out_dir/'brand.json'}\n{'kept existing' if existed else 'wrote draft'} {spec}\n" \
           f"master: {info['master_template']}\nNext: add '{slug}: \"{folder}\"' under BRANDS in config.local.yaml, " \
           f"then run: python -m deckbuilder library build --only {slug}-"


def _draft(info: dict) -> str:
    th = info.get("theme", {})
    colors = "\n".join(f"| {k} | {v} |" for k, v in th.get("colors", {}).items())
    layouts = "\n".join(f"| {l['index']} | {l['name']} |" for l in info.get("layouts", [])
                        if not l["name"].lower().startswith("read only"))
    return f"""# Brand spec: {info['slug']}

Status: DRAFT generated by `deckbuilder brand extract`. Claude completes the sections marked TODO
from the guideline documents and rendered samples, then Mike approves.

Brand folder: `{info['folder']}`
Master template: `{info.get('master_template')}`
Slide size: {info.get('slide_size_in')} inches

## Palette (theme)

| Slot | Hex |
|---|---|
{colors}

TODO: primary, secondary, accent roles; approved tints; text-on-color pairs; colors to avoid.

## Type

Heading: {th.get('fonts', {}).get('heading')}
Body: {th.get('fonts', {}).get('body')}

TODO: sizes per level, weights, case rules.

## Logo

Master logo placements: {json.dumps(info.get('master_logos', []))}

TODO: clear space, minimum size, which slides carry the logo.

## Layouts available

| Index | Name |
|---|---|
{layouts}

## Imagery and tone

TODO

## Guideline documents

{chr(10).join('- `' + d + '`' for d in info.get('guideline_docs', [])) or 'None found.'}
"""
