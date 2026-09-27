"""Deck assembly helpers used by each project's output/build_deck.py.

Typical use (Claude writes build_deck.py per project from the approved storyline):

    from deckbuilder.build import Deck
    d = Deck.from_master("/path/Standard Presentation Template - 2025.pptx")   # branded
    # or: d = Deck.blank()                                                       # unbranded
    s = d.add("Title only slide", title="Revenue doubles by 2028 on subscription growth")
    d.chart(s, "column_clustered", categories=["2024", "2025"], series={"Revenue": [10, 14]},
            box=(0.84, 1.67, 7.6, 4.9), colors=["5236AB"], highlight={"Revenue": 1})
    d.text(s, "Two points that explain the chart", box=(8.7, 1.67, 3.8, 4.9), size=14)
    d.notes(s, "What to say ...")
    d.save("/path/output/Project.pptx")

All measurements are inches. Colors are hex strings without '#'.
"""
from __future__ import annotations

import copy
from pathlib import Path

from pptx import Presentation
from pptx.chart.data import CategoryChartData, XyChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

from .pptx_utils import potx_to_pptx

CHART_TYPES = {
    "column_clustered": XL_CHART_TYPE.COLUMN_CLUSTERED, "column_stacked": XL_CHART_TYPE.COLUMN_STACKED,
    "column_stacked_100": XL_CHART_TYPE.COLUMN_STACKED_100, "bar_clustered": XL_CHART_TYPE.BAR_CLUSTERED,
    "bar_stacked": XL_CHART_TYPE.BAR_STACKED, "bar_stacked_100": XL_CHART_TYPE.BAR_STACKED_100,
    "line": XL_CHART_TYPE.LINE, "line_markers": XL_CHART_TYPE.LINE_MARKERS, "pie": XL_CHART_TYPE.PIE,
    "doughnut": XL_CHART_TYPE.DOUGHNUT, "area": XL_CHART_TYPE.AREA, "area_stacked": XL_CHART_TYPE.AREA_STACKED,
    "scatter": XL_CHART_TYPE.XY_SCATTER, "bubble": XL_CHART_TYPE.BUBBLE, "radar": XL_CHART_TYPE.RADAR,
}


def _rgb(h: str) -> RGBColor:
    return RGBColor.from_string(h.lstrip("#").upper())


class Deck:
    def __init__(self, prs: Presentation, font: str = "Arial"):
        self.prs = prs
        self.font = font

    # ---------- construction ----------
    @classmethod
    def from_master(cls, master: str | Path, font: str = "Arial") -> "Deck":
        """Open a brand master and remove its sample slides, keeping every layout editable."""
        src = Path(master)
        if src.suffix.lower() == ".potx":
            src = potx_to_pptx(src)
        prs = Presentation(str(src))
        sldIdLst = prs.slides._sldIdLst
        for sldId in list(sldIdLst):
            prs.part.drop_rel(sldId.rId)
            sldIdLst.remove(sldId)
        return cls(prs, font)

    def set_classification(self, label: str = "Confidential") -> int:
        """Replace the footer classification label on the masters and layouts. Returns the count replaced."""
        n = 0
        labels = {"Internal", "Confidential", "Public", "Restricted"}
        for m in self.prs.slide_masters:
            for holder in [m] + list(m.slide_layouts):
                for sh in holder.shapes:
                    if sh.has_text_frame and sh.text_frame.text.strip() in labels and sh.text_frame.text.strip() != label:
                        for p in sh.text_frame.paragraphs:
                            for r in p.runs:
                                if r.text.strip() in labels:
                                    r.text = r.text.replace(r.text.strip(), label)
                                    n += 1
        return n

    @classmethod
    def blank(cls, font: str = "Arial") -> "Deck":
        prs = Presentation()
        prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
        return cls(prs, font)

    def layout(self, name: str):
        names = []
        for m in self.prs.slide_masters:
            for lay in m.slide_layouts:
                names.append(lay.name)
                if lay.name.strip().lower() == name.strip().lower():
                    return lay
        for m in self.prs.slide_masters:  # loose match
            for lay in m.slide_layouts:
                if name.strip().lower() in lay.name.lower():
                    return lay
        raise KeyError(f"layout '{name}' not found. Available: {names}")

    def add(self, layout: str = "Blank", title: str | None = None, subtitle: str | None = None, **ph_text):
        """Add a slide from a layout. ph_text maps placeholder idx (as 'ph17') to text."""
        try:
            lay = self.layout(layout)
        except KeyError:
            if layout != "Blank":
                raise
            lay = self.prs.slide_layouts[6]
        s = self.prs.slides.add_slide(lay)
        for ph in s.placeholders:
            t = ph.placeholder_format.type
            tname = str(t).split(".")[-1].split(" ")[0]
            if title is not None and tname in ("TITLE", "CENTER_TITLE"):
                ph.text_frame.text = title
            elif subtitle is not None and tname == "SUBTITLE":
                ph.text_frame.text = subtitle
            key = f"ph{ph.placeholder_format.idx}"
            if key in ph_text:
                self._fill(ph.text_frame, ph_text[key])
        return s

    def prune_empty_placeholders(self, slide) -> None:
        """Delete unfilled content placeholders so no 'Click to add text' remains."""
        for ph in list(slide.placeholders):
            tname = str(ph.placeholder_format.type).split(".")[-1].split(" ")[0]
            if tname in ("FOOTER", "SLIDE_NUMBER", "DATE"):
                continue
            has_text = ph.has_text_frame and ph.text_frame.text.strip()
            if not has_text and not getattr(ph, "image", None):
                ph._element.getparent().remove(ph._element)

    # ---------- content ----------
    def _fill(self, tf, content, size=None, color=None, bold=None, align=None):
        items = content if isinstance(content, list) else [content]
        tf.clear()
        for i, item in enumerate(items):
            level = 0
            if isinstance(item, tuple):
                level, item = item
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.level = level
            parts = item if isinstance(item, list) else [item]
            for part in parts:
                b = False
                if isinstance(part, dict):
                    b, part = part.get("bold", False), part["text"]
                r = p.add_run()
                r.text = part
                if size:
                    r.font.size = Pt(size)
                if color:
                    r.font.color.rgb = _rgb(color)
                if bold is not None or b:
                    r.font.bold = bool(bold or b)
                r.font.name = self.font
            if align:
                p.alignment = {"left": PP_ALIGN.LEFT, "center": PP_ALIGN.CENTER, "right": PP_ALIGN.RIGHT}[align]

    def text(self, slide, content, box, size=14, color="000000", bold=None, align="left",
             fill=None, anchor="top", inset=0.08):
        """Text box. content: str, or list of str / (level, str) / [runs] where a run can be {'text','bold'}."""
        x, y, w, h = box
        sh = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        tf = sh.text_frame
        tf.word_wrap = True
        for side in ("left", "right", "top", "bottom"):
            setattr(tf, f"margin_{side}", Inches(inset))
        tf.vertical_anchor = {"top": MSO_ANCHOR.TOP, "middle": MSO_ANCHOR.MIDDLE, "bottom": MSO_ANCHOR.BOTTOM}[anchor]
        if fill:
            sh.fill.solid()
            sh.fill.fore_color.rgb = _rgb(fill)
        self._fill(tf, content, size, color, bold, align)
        return sh

    def box(self, slide, box, fill, line=None, shape="rectangle", text=None, size=14, color="FFFFFF", bold=False, align="center"):
        x, y, w, h = box
        kind = {"rectangle": MSO_SHAPE.RECTANGLE, "rounded": MSO_SHAPE.ROUNDED_RECTANGLE, "oval": MSO_SHAPE.OVAL,
                "chevron": MSO_SHAPE.CHEVRON, "pentagon": MSO_SHAPE.PENTAGON, "arrow": MSO_SHAPE.RIGHT_ARROW}[shape]
        sh = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
        sh.fill.solid()
        sh.fill.fore_color.rgb = _rgb(fill)
        if line:
            sh.line.color.rgb = _rgb(line)
        else:
            sh.line.fill.background()
        sh.shadow.inherit = False
        if text is not None:
            sh.text_frame.word_wrap = True
            self._fill(sh.text_frame, text, size, color, bold, align)
        return sh

    def image(self, slide, path, box, crop=True):
        """Place an image in a box. crop=True fills the box and trims the overflow (cover fit)."""
        from PIL import Image
        x, y, w, h = box
        pic = slide.shapes.add_picture(str(path), Inches(x), Inches(y), Inches(w), Inches(h))
        if crop:
            iw, ih = Image.open(path).size
            box_r, img_r = w / h, iw / ih
            if img_r > box_r:
                trim = (1 - box_r / img_r) / 2
                pic.crop_left = pic.crop_right = trim
            else:
                trim = (1 - img_r / box_r) / 2
                pic.crop_top = pic.crop_bottom = trim
        return pic

    def video(self, slide, path, box, poster):
        x, y, w, h = box
        return slide.shapes.add_movie(str(path), Inches(x), Inches(y), Inches(w), Inches(h),
                                      poster_frame_image=str(poster), mime_type="video/mp4")

    def chart(self, slide, kind, categories=None, series=None, box=(0.84, 1.67, 11.66, 4.9), colors=None,
              highlight=None, labels=True, legend=None, number_format='#,##0', font_size=12, gridlines=False,
              xy=None):
        """Native, editable chart. series: {name: [values]}. highlight: {series_name: point_index} recolors one point."""
        x, y, w, h = box
        ct = CHART_TYPES[kind]
        if kind in ("scatter", "bubble"):
            data = XyChartData()
            for name, pts in (xy or {}).items():
                s = data.add_series(name)
                for px, py in pts:
                    s.add_data_point(px, py)
        else:
            data = CategoryChartData()
            data.categories = categories
            for name, vals in series.items():
                data.add_series(name, vals)
        gf = slide.shapes.add_chart(ct, Inches(x), Inches(y), Inches(w), Inches(h), data)
        ch = gf.chart
        ch.font.size = Pt(font_size)
        ch.font.name = self.font
        ch.has_title = False  # the slide title carries the message; put the unit line in a text box
        multi = len(series or xy or {}) > 1
        ch.has_legend = multi if legend is None else legend
        if ch.has_legend:
            ch.legend.position = XL_LEGEND_POSITION.TOP
            ch.legend.include_in_layout = False
        colors = colors or ["5236AB", "E31937", "9E83F5", "991F3D", "555555", "CBC3E6"]
        plot = ch.plots[0]
        if kind not in ("pie", "doughnut"):
            try:
                plot.gap_width = 60
            except Exception:
                pass
            try:
                ch.value_axis.has_major_gridlines = gridlines
                ch.value_axis.format.line.fill.background()
                ch.value_axis.tick_labels.font.size = Pt(font_size - 1)
                ch.category_axis.tick_labels.font.size = Pt(font_size - 1)
                ch.category_axis.format.line.color.rgb = _rgb("CCCCCC")
                if labels:
                    ch.value_axis.visible = False
            except Exception:
                pass
        for i, s in enumerate(plot.series):
            col = colors[i % len(colors)]
            if kind in ("pie", "doughnut"):
                for j, pt in enumerate(s.points):
                    pt.format.fill.solid()
                    pt.format.fill.fore_color.rgb = _rgb(colors[j % len(colors)])
            elif kind.startswith("line"):
                s.format.line.color.rgb = _rgb(col)
                s.format.line.width = Pt(2.25)
                s.smooth = False
            else:
                s.format.fill.solid()
                s.format.fill.fore_color.rgb = _rgb(col)
            if highlight and s.name in highlight:
                idx = highlight[s.name]
                pt = s.points[idx]
                pt.format.fill.solid()
                pt.format.fill.fore_color.rgb = _rgb(colors[1] if len(colors) > 1 else "E31937")
        if labels:
            plot.has_data_labels = True
            dl = plot.data_labels
            dl.number_format = number_format
            dl.number_format_is_linked = False
            dl.font.size = Pt(font_size - 1)
        return gf

    def table(self, slide, rows, box, header_fill="200A58", header_color="FFFFFF", size=12, band=None, col_widths=None,
              align_numbers=True):
        """rows[0] is the header. Numbers (or strings starting with a digit, +, -) are right aligned."""
        x, y, w, h = box
        nr, nc = len(rows), len(rows[0])
        gf = slide.shapes.add_table(nr, nc, Inches(x), Inches(y), Inches(w), Inches(h))
        tbl = gf.table
        tblPr = tbl._tbl.tblPr
        style = tblPr.find("{http://schemas.openxmlformats.org/drawingml/2006/main}tableStyleId")
        if style is not None:
            style.text = "{5940675A-B579-460E-94D1-54222C63F5DA}"  # No Style, Table Grid
        if col_widths:
            for i, cw in enumerate(col_widths):
                tbl.columns[i].width = Inches(cw)
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                cell = tbl.cell(r, c)
                cell.text = str(val)
                cell.margin_left = cell.margin_right = Inches(0.06)
                p = cell.text_frame.paragraphs[0]
                for run in p.runs:
                    run.font.size = Pt(size)
                    run.font.name = self.font
                    run.font.bold = r == 0
                    run.font.color.rgb = _rgb(header_color if r == 0 else "000000")
                s = str(val).strip()
                if align_numbers and r > 0 and s[:1] in "0123456789+-$€£%" and c > 0:
                    p.alignment = PP_ALIGN.RIGHT
                cell.fill.solid()
                cell.fill.fore_color.rgb = _rgb(header_fill if r == 0 else (band if band and r % 2 == 0 else "FFFFFF"))
        return gf

    def notes(self, slide, text: str) -> None:
        if "—" in text or "–" in text:
            raise ValueError("Speaker notes contain an em or en dash. Rewrite the sentence.")
        slide.notes_slide.notes_text_frame.text = text

    def duplicate_from(self, other_pptx: str | Path, slide_number: int):
        """Copy one slide's shapes from another deck onto a new blank-layout slide (structure reuse).
        Pictures and charts that depend on relationships are not copied; rebuild those natively."""
        src = Presentation(str(other_pptx)).slides[slide_number - 1]
        dst = self.add("Title only slide") if self._has_layout("Title only slide") else self.add("Blank")
        for sh in src.shapes:
            if sh.shape_type in (13,) or getattr(sh, "has_chart", False):
                continue
            dst.shapes._spTree.insert_element_before(copy.deepcopy(sh._element), "p:extLst")
        return dst

    def _has_layout(self, name):
        try:
            self.layout(name)
            return True
        except KeyError:
            return False

    def save(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        for s in self.prs.slides:
            for sh in s.shapes:
                if sh.has_text_frame and ("—" in sh.text_frame.text or "–" in sh.text_frame.text):
                    raise ValueError(f"Em or en dash on slide {self.prs.slides.index(s) + 1}: {sh.text_frame.text[:60]}")
        self.prs.save(str(path))
        return path
