"""Heuristic slide classification for the master slide database.

Categories are the layout vocabulary used in docs/best-practices.md. Heuristics are a first
pass. `python -m deckbuilder library tag <slide_id> <category>` records a manual override that
survives re-indexing.
"""
from __future__ import annotations

import re

CATEGORIES = [
    "cover", "agenda", "section-divider", "executive-summary", "text-bullets", "text-columns",
    "comparison", "chart", "chart-plus-text", "table", "matrix-2x2", "framework", "process-flow",
    "timeline-roadmap", "gantt", "org-team", "profile-cv", "map", "kpi-dashboard", "quote-highlight",
    "image-led", "icon-grid", "closing", "instructions", "other",
]

FRAMEWORK_TERMS = {
    "swot": "swot", "porter": "porters-five-forces", "five forces": "porters-five-forces",
    "pestel": "pestel", "pest ": "pestel", "value chain": "value-chain", "bcg": "bcg-matrix",
    "ansoff": "ansoff", "7s": "mckinsey-7s", "business model canvas": "business-model-canvas",
    "canvas": "canvas", "balanced scorecard": "balanced-scorecard", "raci": "raci",
    "stakeholder": "stakeholder-map", "issue tree": "issue-tree", "driver tree": "driver-tree",
    "mece": "issue-tree", "okr": "okr", "kpi tree": "driver-tree", "customer journey": "customer-journey",
    "persona": "persona", "operating model": "operating-model", "maturity": "maturity-model",
    "capability": "capability-map", "ge-mckinsey": "ge-matrix", "ge mckinsey": "ge-matrix",
    "pyramid": "pyramid", "funnel": "funnel", "tam": "tam-sam-som", "sam": "tam-sam-som",
    "risk": "risk-register", "heat map": "heatmap", "heatmap": "heatmap", "scorecard": "scorecard",
    "benchmark": "benchmark", "prioritization": "prioritization",
}
TIMELINE_TERMS = ["timeline", "roadmap", "milestone", "phase", "100 day", "100-day", "30-60-90",
                  "wave", "horizon", "implementation plan", "workplan", "work plan"]
GANTT_TERMS = ["gantt", "week 1", "wk 1", "jan", "feb", "q1", "q2", "month 1", "sprint"]
TEAM_TERMS = ["team", "organization", "organisation", "org chart", "governance", "steering committee"]
CV_TERMS = ["cv/resume", "resume", "cv ", "biography", "bio"]
MAP_TERMS = ["map", "geograph", "region", "country", "countries", "global presence"]
AGENDA_TERMS = ["agenda", "table of contents", "contents", "overview of the document"]
CLOSING_TERMS = ["thank you", "q&a", "questions", "contact us", "closing", "next steps"]
SUMMARY_TERMS = ["executive summary", "summary", "key takeaways", "key findings", "recommendation"]
INSTRUCTION_TERMS = ["how to use", "brand tip", "instructions", "delete this slide", "template guide",
                     "read me", "readme", "user guide", "about this template"]
KPI_TERMS = ["kpi", "dashboard", "scorecard", "metrics"]
COMPARE_TERMS = [" vs", "versus", "comparison", "compare", "option a", "options", "pros and cons", "before", "after"]
PLACEHOLDER_RE = re.compile(r"\[(?:insert|xx|x+|add|name|date|text|title|sub)[^\]]*\]|lorem ipsum|insert text|slide title|first and last name|placeholder", re.I)


def _has(text: str, terms) -> bool:
    return any(t in text for t in terms)


def is_assertion(title: str) -> bool:
    """Action title: a full sentence stating the takeaway, not a topic label."""
    words = title.split()
    if len(words) < 6:
        return False
    verbs = re.compile(r"\b(is|are|will|can|has|have|drive|drives|enable|enables|grow|grows|show|shows|"
                       r"need|needs|require|requires|remain|remains|expected|should|must|led|leads|"
                       r"increase|increases|decline|declines|reduce|reduces|deliver|delivers|creates?)\b", re.I)
    return bool(verbs.search(title))


def classify(f: dict) -> tuple[str, str, list[str]]:
    """Return (category, subcategory, tags) from the feature dict built in library.py."""
    title = (f.get("title") or "").lower()
    body = (f.get("body_text") or "").lower()
    layout = (f.get("layout_name") or "").lower()
    both = f"{title} {body}"
    tags: list[str] = []
    sub = ""

    words = f.get("word_count", 0)
    charts = f.get("n_charts", 0)
    tables = f.get("n_tables", 0)
    pics = f.get("n_pictures", 0)
    pic_area = f.get("picture_area_pct", 0.0)
    connectors = f.get("n_connectors", 0)
    arrows = f.get("n_arrow_shapes", 0)
    cols = f.get("n_columns_est", 0)
    ashapes = f.get("n_autoshapes", 0)
    freeforms = f.get("n_freeforms", 0)

    if f.get("has_placeholder_text"):
        tags.append("placeholder-text")
    if is_assertion(f.get("title") or ""):
        tags.append("assertion-title")
    for term, fw in FRAMEWORK_TERMS.items():
        if term in both:
            tags.append(fw)
    if f.get("n_smartart"):
        tags.append("smartart")

    if title.startswith(("best practice tip", "slideworks note", "brand tip", "how to use")):
        return "instructions", "", tags
    if _has(both, INSTRUCTION_TERMS) and words > 25 and not charts:
        return "instructions", "", tags
    if "waterfall" in title or "bridge chart" in title:
        return ("chart-plus-text" if words > 60 else "chart"), "waterfall", tags
    if "title slide" in layout or "cover" in layout or (f.get("slide_num") == 1 and words < 30):
        return "cover", "", tags
    if _has(title, AGENDA_TERMS) or "agenda" in layout:
        return "agenda", "", tags
    if "closing" in layout or "q&a" in layout or (_has(title, CLOSING_TERMS[:4]) and words < 60):
        return "closing", "", tags
    if "section" in layout or "divider" in layout or (words <= 12 and not charts and not tables and ashapes < 6 and pics <= 1):
        return "section-divider", "", tags
    if "cv/resume" in layout or _has(title, CV_TERMS):
        return "profile-cv", "", tags
    if layout.startswith("team") or (_has(title, TEAM_TERMS) and (pics >= 2 or ashapes >= 6)):
        return "org-team", "", tags
    if charts:
        sub = ",".join(sorted(set(f.get("chart_types", "").split(",")) - {""}))
        if _has(both, ["waterfall", "bridge"]):
            sub = (sub + ",waterfall").strip(",")
        if _has(both, KPI_TERMS) and charts >= 3:
            return "kpi-dashboard", sub, tags
        if words > 60 or cols >= 2:
            return "chart-plus-text", sub, tags
        return "chart", sub, tags
    if _has(title, ["gantt"]) or (tables and _has(body, GANTT_TERMS)) or (ashapes > 25 and _has(body, GANTT_TERMS)):
        return "gantt", "", tags
    if _has(both, TIMELINE_TERMS):
        return "timeline-roadmap", "", tags
    if _has(both, ["2x2", "matrix", "quadrant", "bcg", "ge-mckinsey", "ge mckinsey", "ansoff"]):
        return "matrix-2x2", "", tags
    if tables:
        return "table", f.get("table_dims", ""), tags
    if _has(title, MAP_TERMS) and (freeforms >= 10 or pics >= 1):
        return "map", "", tags
    if any(t in tags for t in FRAMEWORK_TERMS.values()):
        return "framework", next(t for t in tags if t in FRAMEWORK_TERMS.values()), tags
    if _has(both, KPI_TERMS) and ashapes >= 6:
        return "kpi-dashboard", "", tags
    if connectors >= 3 or arrows >= 3 or _has(both, ["process", "step 1", "steps", "workflow", "approach"]):
        return "process-flow", "", tags
    if _has(title, SUMMARY_TERMS):
        return "executive-summary", "", tags
    if f.get("quote_like"):
        return "quote-highlight", "", tags
    if pic_area >= 35:
        return "image-led", "", tags
    if _has(title, COMPARE_TERMS) and cols >= 2:
        return "comparison", str(cols), tags
    if pics >= 4 and words < 120:
        return "icon-grid", "", tags
    if cols >= 2:
        return "text-columns", str(cols), tags
    if words > 0:
        return "text-bullets", "", tags
    return "other", "", tags
