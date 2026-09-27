"""DeckBuilder command line.

  python -m deckbuilder check                         verify config, folders, tools, keys
  python -m deckbuilder library build [--no-render] [--force] [--only <deck-id-part>]
  python -m deckbuilder library stats
  python -m deckbuilder library search [text] [--category C] [--source S] [--chart T] [--curated] [--limit N]
  python -m deckbuilder library tag <slide_id> [--category C] [--tags a,b] [--note N] [--quality 1-5]
  python -m deckbuilder library sheet <deck_id>       print contact sheet paths for a deck
  python -m deckbuilder brand extract <folder> --slug <slug> [--master <file>]
  python -m deckbuilder project new "<Project Name>"
  python -m deckbuilder project scan <project-folder>
  python -m deckbuilder render <deck.pptx> <out_dir>
  python -m deckbuilder qa <deck.pptx> [--brand <slug>]
  python -m deckbuilder stock "<query>" [--n 8] [--download i --out file.jpg]   Pexels then Pixabay, free
  python -m deckbuilder gen image|video|veo --prompt P --out F [--image start.png] --yes   spends credits
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import config as C


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="deckbuilder")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("check")

    lib = sub.add_parser("library").add_subparsers(dest="action", required=True)
    b = lib.add_parser("build")
    b.add_argument("--no-render", action="store_true")
    b.add_argument("--force", action="store_true")
    b.add_argument("--only")
    lib.add_parser("stats")
    s = lib.add_parser("search")
    s.add_argument("text", nargs="?")
    s.add_argument("--category")
    s.add_argument("--source")
    s.add_argument("--chart")
    s.add_argument("--curated", action="store_true")
    s.add_argument("--limit", type=int, default=20)
    s.add_argument("--json", action="store_true")
    t = lib.add_parser("tag")
    t.add_argument("slide_id")
    t.add_argument("--category")
    t.add_argument("--tags")
    t.add_argument("--note")
    t.add_argument("--quality", type=int)
    sh = lib.add_parser("sheet")
    sh.add_argument("deck_id")

    br = sub.add_parser("brand").add_subparsers(dest="action", required=True)
    be = br.add_parser("extract")
    be.add_argument("folder")
    be.add_argument("--slug", required=True)
    be.add_argument("--master")

    pr = sub.add_parser("project").add_subparsers(dest="action", required=True)
    pn = pr.add_parser("new")
    pn.add_argument("name")
    ps = pr.add_parser("scan")
    ps.add_argument("folder")

    r = sub.add_parser("render")
    r.add_argument("deck")
    r.add_argument("out")

    q = sub.add_parser("qa")
    q.add_argument("deck")
    q.add_argument("--brand")
    q.add_argument("--render-dir")

    st = sub.add_parser("stock")
    st.add_argument("query")
    st.add_argument("--n", type=int, default=8)
    st.add_argument("--download", type=int, help="index of the candidate to download")
    st.add_argument("--out")

    g = sub.add_parser("gen")
    g.add_argument("kind", choices=["image", "video", "veo"])
    g.add_argument("--prompt", required=True)
    g.add_argument("--out", required=True)
    g.add_argument("--ratio", default="1920:1080")
    g.add_argument("--image", help="start frame for image-to-video")
    g.add_argument("--duration", type=int, default=5)
    g.add_argument("--yes", action="store_true", help="confirm spend (required)")

    a = ap.parse_args(argv)
    cfg = C.load()

    if a.cmd == "check":
        from .check import run
        return run(cfg)

    if a.cmd == "library":
        from . import library as L
        if a.action == "build":
            L.build(cfg, render=not a.no_render, force=a.force, only=a.only)
            print(L.stats(cfg))
        elif a.action == "stats":
            print(L.stats(cfg))
        elif a.action == "search":
            rows = L.search(cfg, a.text, a.category, a.source, a.chart, a.curated, a.limit)
            if a.json:
                print(json.dumps(rows, indent=1))
            else:
                for r in rows:
                    flag = "*" if r["curated"] else " "
                    print(f"{flag} {r['id']:<60} {r['category']:<18} {r['words']:>4}w  {r['title']}")
                    print(f"    {r['thumb']}")
        elif a.action == "tag":
            L.tag(cfg, a.slide_id, a.category, a.tags, a.note, a.quality)
        elif a.action == "sheet":
            for p in sorted((C.library_root(cfg) / "sheets" / a.deck_id).glob("*.jpg"), key=lambda p: int(p.stem)):
                print(p)
        return 0

    if a.cmd == "brand":
        from .brand import extract
        print(extract(cfg, Path(a.folder), a.slug, a.master))
        return 0

    if a.cmd == "project":
        from . import project as P
        if a.action == "new":
            print(P.new(cfg, a.name))
        else:
            print(json.dumps(P.scan(Path(a.folder)), indent=1))
        return 0

    if a.cmd == "render":
        from .render import contact_sheet, render_deck
        pngs = render_deck(Path(a.deck), Path(a.out), cfg, width=1600)
        contact_sheet(sorted(pngs, key=lambda p: int(p.stem)), Path(a.out) / "contact_sheet.jpg")
        print(f"{len(pngs)} slides rendered to {a.out}")
        return 0

    if a.cmd == "qa":
        from .qa import run as qa_run
        return qa_run(cfg, Path(a.deck), a.brand, a.render_dir)

    if a.cmd == "stock":
        from . import generate as G
        cands = G.stock_search(a.query, a.n)
        if a.download is not None:
            if not a.out:
                print("--out is required with --download")
                return 2
            print(G.stock_download(cands[a.download], Path(a.out)))
        else:
            for i, c in enumerate(cands):
                print(f"[{i}] {c['source']:<8} {c['width']}x{c['height']}  {c['alt'][:70]}\n     preview {c['preview']}")
        return 0

    if a.cmd == "gen":
        from . import generate as G
        if not a.yes:
            print("Refusing to spend credits without --yes. Show Mike the asset list and estimate first.")
            return 2
        if a.kind == "image":
            print(G.runway_image(cfg, a.prompt, Path(a.out), a.ratio))
        elif a.kind == "video":
            print(G.runway_video(cfg, a.prompt, Path(a.out), a.image, a.duration, a.ratio))
        else:
            print(G.veo_video(cfg, a.prompt, Path(a.out), a.image))
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
