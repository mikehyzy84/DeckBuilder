"""Render a deck to PDF with LibreOffice, then to per-slide PNGs.

Used for library thumbnails and for build QA.
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path


def find_soffice(cfg: dict | None = None) -> str:
    candidates = []
    if cfg and cfg.get("SOFFICE_PATH"):
        candidates.append(cfg["SOFFICE_PATH"])
    candidates += [
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        shutil.which("soffice") or "",
        shutil.which("libreoffice") or "",
    ]
    for c in candidates:
        if c and Path(c).exists():
            return c
    raise SystemExit("LibreOffice not found. Install it (brew install --cask libreoffice) and set SOFFICE_PATH.")


def to_pdf(deck: Path, out_dir: Path, cfg: dict | None = None, timeout: int = 1800) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    profile = Path(tempfile.mkdtemp(prefix="lo_profile_"))
    cmd = [
        find_soffice(cfg), f"-env:UserInstallation=file://{profile}",
        "--headless", "--convert-to", "pdf", "--outdir", str(out_dir), str(deck),
    ]
    subprocess.run(cmd, check=True, timeout=timeout, capture_output=True)
    pdf = out_dir / (Path(deck).stem + ".pdf")
    if not pdf.exists():
        raise RuntimeError(f"LibreOffice produced no PDF for {deck}")
    shutil.rmtree(profile, ignore_errors=True)
    return pdf


def pdf_to_pngs(pdf: Path, out_dir: Path, width: int = 640, pages: list[int] | None = None) -> list[Path]:
    """Write <n>.png (1-based) for each page. Uses PyMuPDF, falls back to pdftoppm."""
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(pdf)
        for i, page in enumerate(doc, 1):
            if pages and i not in pages:
                continue
            zoom = width / page.rect.width
            pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
            p = out_dir / f"{i}.png"
            pix.save(p)
            written.append(p)
        return written
    except ImportError:
        pass
    tool = shutil.which("pdftoppm")
    if not tool:
        raise SystemExit("Install PyMuPDF (pip install pymupdf) or poppler for pdftoppm.")
    tmp = Path(tempfile.mkdtemp())
    subprocess.run([tool, "-png", "-scale-to-x", str(width), "-scale-to-y", "-1", str(pdf), str(tmp / "p")], check=True)
    for f in sorted(tmp.glob("p-*.png")):
        n = int(f.stem.split("-")[-1])
        if pages and n not in pages:
            continue
        dst = out_dir / f"{n}.png"
        shutil.move(str(f), dst)
        written.append(dst)
    shutil.rmtree(tmp, ignore_errors=True)
    return written


def render_deck(deck: Path, out_dir: Path, cfg: dict | None = None, width: int = 640) -> list[Path]:
    work = Path(tempfile.mkdtemp(prefix="render_"))
    src = Path(deck)
    if src.suffix.lower() == ".potx":
        from .pptx_utils import potx_to_pptx
        src = potx_to_pptx(src, work / (src.stem + ".pptx"))
    pdf = to_pdf(src, work, cfg)
    pngs = pdf_to_pngs(pdf, out_dir, width)
    shutil.rmtree(work, ignore_errors=True)
    return pngs


def contact_sheet(pngs: list[Path], out: Path, cols: int = 6, label: bool = True) -> Path:
    """Grid of thumbnails with slide numbers, for fast visual review."""
    from PIL import Image, ImageDraw
    if not pngs:
        raise ValueError("no images")
    ims = [Image.open(p).convert("RGB") for p in pngs]
    w, h = ims[0].size
    tw = 320
    th = int(h * tw / w)
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * (th + 18)), "white")
    d = ImageDraw.Draw(sheet)
    for i, (im, p) in enumerate(zip(ims, pngs)):
        x, y = (i % cols) * tw, (i // cols) * (th + 18)
        sheet.paste(im.resize((tw, th)), (x, y + 18))
        if label:
            d.text((x + 4, y + 3), p.stem, fill="black")
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, quality=80)
    return out
