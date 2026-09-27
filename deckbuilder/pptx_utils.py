"""Helpers for opening .pptx and .potx files with python-pptx."""
from __future__ import annotations

import hashlib
import tempfile
import zipfile
from pathlib import Path

from pptx import Presentation

TEMPLATE_CT = b"application/vnd.openxmlformats-officedocument.presentationml.template.main+xml"
PRES_CT = b"application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"
EMU_PER_INCH = 914400


def potx_to_pptx(src: Path, dst: Path | None = None) -> Path:
    """python-pptx cannot open .potx. Rewrite the main content type to make a .pptx copy."""
    src = Path(src)
    dst = Path(dst) if dst else Path(tempfile.mkdtemp()) / (src.stem + ".pptx")
    with zipfile.ZipFile(src) as zin, zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "[Content_Types].xml":
                data = data.replace(TEMPLATE_CT, PRES_CT)
            zout.writestr(item, data)
    return dst


def open_presentation(path: Path) -> Presentation:
    path = Path(path)
    if path.suffix.lower() == ".potx":
        path = potx_to_pptx(path)
    return Presentation(str(path))


def slide_xml_bytes(path: Path) -> list[int]:
    """Uncompressed size of each slide XML, in presentation order."""
    import re
    with zipfile.ZipFile(path) as z:
        order = _slide_order(z)
        sizes = {i.filename: i.file_size for i in z.infolist()}
    return [sizes.get(f"ppt/{t}", 0) for t in order]


def _slide_order(z: zipfile.ZipFile) -> list[str]:
    import re
    pres = z.read("ppt/presentation.xml").decode("utf8")
    rels = z.read("ppt/_rels/presentation.xml.rels").decode("utf8")
    rmap = dict(re.findall(r'<Relationship[^>]*?Id="([^"]+)"[^>]*?Target="([^"]+)"', rels))
    rmap.update({k: v for v, k in re.findall(r'<Relationship[^>]*?Target="([^"]+)"[^>]*?Id="([^"]+)"', rels)})
    ids = re.findall(r'<p:sldId [^>]*?r:id="([^"]+)"', pres)
    return [rmap[i].lstrip("/").replace("ppt/", "") for i in ids]


def subset_deck(src: Path, keep: list[int], dst: Path) -> Path:
    """Write a copy of a deck that contains only the 1-based slide numbers in `keep`.

    Used to process very large decks in chunks so memory stays bounded.
    """
    import re
    keep = set(keep)
    with zipfile.ZipFile(src) as z:
        order = _slide_order(z)
        drop_targets = {t for n, t in enumerate(order, 1) if n not in keep}
        drop_files = set()
        for t in drop_targets:
            drop_files.add(f"ppt/{t}")
            d, f = t.rsplit("/", 1)
            drop_files.add(f"ppt/{d}/_rels/{f}.rels")
        pres = z.read("ppt/presentation.xml").decode("utf8")
        rels = z.read("ppt/_rels/presentation.xml.rels").decode("utf8")
        drop_ids = set()
        for m in re.finditer(r"<Relationship [^>]*/>", rels):
            tag = m.group(0)
            tgt = re.search(r'Target="([^"]+)"', tag).group(1).lstrip("/").replace("ppt/", "")
            if tgt in drop_targets:
                drop_ids.add(re.search(r'Id="([^"]+)"', tag).group(1))
        for rid in drop_ids:
            rels = re.sub(rf'<Relationship [^>]*Id="{rid}"[^>]*/>', "", rels)
            pres = re.sub(rf'<p:sldId [^>]*r:id="{rid}"[^>]*/>', "", pres)
        ct = z.read("[Content_Types].xml").decode("utf8")
        for f in drop_files:
            ct = ct.replace(f'<Override PartName="/{f}" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>', "")
        with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as out:
            for item in z.infolist():
                if item.filename in drop_files:
                    continue
                if item.filename == "ppt/presentation.xml":
                    out.writestr(item, pres)
                elif item.filename == "ppt/_rels/presentation.xml.rels":
                    out.writestr(item, rels)
                elif item.filename == "[Content_Types].xml":
                    out.writestr(item, ct.replace(TEMPLATE_CT.decode(), PRES_CT.decode()))
                elif re.fullmatch(r"ppt/slides/slide\d+\.xml", item.filename):
                    # unhide so LibreOffice exports every slide and page n maps to slide n
                    data = z.read(item.filename)
                    head, rest = data[:2000], data[2000:]
                    head = re.sub(rb'(<p:sld\b[^>]*?)\sshow="0"', rb"\1", head)
                    out.writestr(item, head + rest)
                else:
                    out.writestr(item, z.read(item.filename))
    return dst


def chunk_plan(path: Path, budget_bytes: int = 60_000_000) -> list[list[int]]:
    """Group slide numbers so each chunk's slide XML stays under the budget."""
    sizes = slide_xml_bytes(path)
    chunks, cur, tot = [], [], 0
    for n, s in enumerate(sizes, 1):
        if cur and tot + s > budget_bytes:
            chunks.append(cur)
            cur, tot = [], 0
        cur.append(n)
        tot += s
    if cur:
        chunks.append(cur)
    return chunks


def file_md5(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        while block := f.read(chunk):
            h.update(block)
    return h.hexdigest()


def emu_to_in(v) -> float:
    return round((v or 0) / EMU_PER_INCH, 3)
