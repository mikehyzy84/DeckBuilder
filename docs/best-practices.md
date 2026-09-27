# DeckBuilder best practices

Status: APPROVED by Mike on 2026-09-27. Written from the slide database built that day.

Source: 11 Slideworks decks, 3,267 slides, all rendered and indexed. Every pattern below cites exemplar slides by
database id, `<deck-id>#<slide>`. To see an exemplar, open
`$SLIDE_LIBRARY_ROOT/thumbs/<deck-id>/<slide>.png`, or run
`python -m deckbuilder library search --category <layout>`. The 210 hand-picked slides in
`claude_design_inputs/selection_index.csv` are flagged `curated` in the database and rank first in every search.

These rules govern structure, layout choice, density, and storyline for every deck. Brand rules
(`docs/brands/<slug>/brand-spec.md`) and the project's `design-guide/` govern color, type, and imagery.

---

## 1. Storyline

### 1.1 Answer first
Open with the conclusion, then give the arguments, then the evidence. Each level of the deck supports the level
above it. The executive summary states the answer in one sentence and lists three to five supporting points.
Exemplars: `sw-business-strategy-template#289` (pyramid structure), `sw-business-strategy-template#12`,
`sw-business-case-template#11`, `sw-proposal-template#31`.

### 1.2 Titles tell the story on their own
Read only the slide titles, in order. They must form a coherent argument with no gaps. If a title can be removed
without breaking the argument, the slide is appendix material. Exemplar: `sw-business-strategy-template#288`.

### 1.3 One message per slide
Each slide makes one claim. If the body supports two claims, split the slide.
Exemplar: `sw-business-strategy-template#285`.

### 1.4 Storyline skeletons
Pick the closest skeleton, then adapt it. Section dividers mark each block.

| Deck type | Sequence | Reference deck |
|---|---|---|
| Strategy | Summary, starting point, purpose and goals, objectives and initiatives, enablers, roadmap, financial impact | `sw-business-strategy-template` (dividers at #14, #24, #48, #54, #100, #104) |
| Business case | Point of departure, vision, solution, business model, financials and scenarios, timeline, risks, next steps | `sw-business-case-template` (#15, #25, #34, #88, #99, #105, #127, #131) |
| Investor style pitch | Vision, problem, solution, competition, growth, financials, delivery, investment, next steps | `sw-business-case-template` #230 to #281 |
| Proposal | Executive summary, situation, objectives and solution, approach, pricing, why us, next steps, appendix | `sw-proposal-template` (#28, #38, #46, #61, #109, #114, #119) |
| Due diligence | Executive summary, process, commercial DD, financial model, risks and synergies, recommendations, next steps | `sw-due-diligence-template` (#29, #36, #48, #73, #101, #105, #110) |
| 100-day plan | Context, priorities, workstreams, timeline, governance, quick wins | `sw-100-day-plan-template` |
| Market entry | Market attractiveness, customer, competition, entry options, business case, roadmap | `sw-market-entry-analysis-template` |
| Product strategy | Vision, customer and problem, portfolio, roadmap, metrics | `sw-product-strategy-template` |

For CGI decks, also run the storyline through the CGI "And, But, Therefore" framing: situation, complication,
resolution. See `docs/brands/cgi/brand-spec.md` section 7.

### 1.5 Transitions
Use a section divider between blocks. Use an agenda slide with the current block highlighted when a deck has four or
more blocks, and repeat it at each block. Exemplar agenda trackers: `sw-market-entry-analysis-template#296`, #300, #308.

---

## 2. Headlines

- Write action titles: a full sentence that states the takeaway, not a topic label.
  Weak: "Market overview". Strong: "The market is large and growing 8% a year, led by digital channels."
  Exemplar: `sw-business-strategy-template#286`.
- In the library, content slide titles have a median of 8 words and 90% have 17 words or fewer. Target 8 to 15
  words and never more than two lines.
- Put the number in the title when the slide is about a number.
- An optional one-line subtitle under the title can state the unit, scope, or source of the data.
- Sentence case. No closing period. No em or en dashes.

---

## 3. Grid, margins, and slide furniture

Measured from the library (16:9, 13.33 x 7.5 in):

| Element | Slideworks convention | Rule for DeckBuilder |
|---|---|---|
| Left and right content margin | 0.51 to 0.61 in | At least 0.5 in. Use the brand master's margins when a brand applies (CGI is 0.84 in). |
| Title | Top left, full content width, about 0.4 in from top | Title placeholder from the layout. Never a free text box. |
| Subtitle or data label line | Directly under the title | Optional, one line |
| Body area | Starts about 1.4 to 1.7 in from top | Align every body element to the same top edge |
| Footer band | Source, footnote, page number in the bottom 0.4 in | Sources go bottom left in small type |
| Columns | 2, 3, 4, or 5 equal columns, equal gutters | Align to the grid; equal widths and gutters |

Other rules:

- Align edges. Elements in a row share a top edge; elements in a column share a left edge.
- Spacing is equal between repeated elements.
- No accent lines under titles and no decorative edge stripes.
- Tracker or section tags at the top right are allowed if the brand master provides them.

---

## 4. Density limits

Library medians for content slides: 79 words, 12 text shapes. 90th percentile is 181 words. The best slides sit
well below the median.

| Slide type | Target words | Hard limit |
|---|---|---|
| Executive summary | 80 to 150 | 190 |
| Chart with takeaways | 40 to 90 | 120 |
| Chart only | 15 to 40 | 60 |
| Framework or matrix | 50 to 110 | 140 |
| Process or timeline | 50 to 110 | 140 |
| Text in columns | 50 to 100 | 130 |
| Section divider | 2 to 8 | 15 |

Additional limits:

- No more than 5 bullets in a block, and no more than 2 levels of indentation.
- Body text no smaller than 12 pt. Footnotes and sources no smaller than 9 pt.
- If a slide breaks a hard limit, split it or move detail to speaker notes or the appendix.

---

## 5. Layout vocabulary

The `category` column in the slide database uses these names. The storyline names one of them for every slide.

| Layout | Use it when | Exemplars |
|---|---|---|
| `cover` | Opening slide: title, subtitle, presenter, date | Use the brand master's cover layout |
| `agenda` | Four or more sections; repeat as a tracker | `sw-market-entry-analysis-template#296` |
| `section-divider` | Start of each storyline block | `sw-proposal-template#201` |
| `executive-summary` | Answer first: the conclusion and three to five supporting points | `sw-business-strategy-template#12`, `sw-business-case-template#11` |
| `chart-plus-text` | The main data slide: a chart on the left two thirds, a takeaway box on the right third | `sw-business-strategy-template#139`, `sw-due-diligence-template#164`, `sw-business-case-template#182` |
| `chart` | A single chart where the title carries the message | `sw-business-case-template#266`, `#235` |
| `table` | Comparing options, vendors, or competitors across the same criteria | `sw-business-strategy-template#221`, `#68` |
| `matrix-2x2` | Prioritizing or positioning on two axes | `sw-business-strategy-template#266`, `sw-business-consulting-toolkit#181` |
| `framework` | A named analytical model: SWOT, PESTEL, five forces, value chain, business model canvas, 7S, scorecard | `sw-business-strategy-template#237`, `sw-market-analysis-template#276` |
| `process-flow` | Sequential steps, a customer journey, an approach, chevrons | `sw-due-diligence-template#39`, `sw-business-strategy-template#81` |
| `timeline-roadmap` | Phases or milestones over time | `sw-business-case-template#278`, `#87`, `sw-due-diligence-template#34` |
| `gantt` | Workstreams against weeks or months | `sw-business-case-template#122`, `sw-proposal-template#186` |
| `text-columns` | Three to five parallel ideas with a header each | `sw-market-analysis-template#150`, `sw-business-strategy-template#19` |
| `text-bullets` | Only when nothing more visual fits | `sw-business-consulting-toolkit#82` |
| `kpi-dashboard` | Several metrics with status | `sw-business-strategy-template#220`, `sw-proposal-template#199` |
| `org-team` | A team, governance, or organization chart | `sw-proposal-template#158` |
| `map` | Geographic spread or regional data | `sw-business-strategy-template#243`, `sw-consulting-maps-bundle` |
| `image-led` | Emotional or scene-setting moments; hero visuals | `sw-business-strategy-template#191` |
| `icon-grid` | Four to eight capabilities or offerings | `sw-business-consulting-toolkit#86`, `#83` |
| `comparison` | Before and after, option A against option B | `sw-due-diligence-template#264` |
| `quote-highlight` | One statement or client quote given full weight | Use the brand master's quote layouts |
| `closing` | Next steps, contact, call to action | `sw-proposal-template#197` |

Selection rules:

1. If the point is a number or a trend, use a chart. Use `chart-plus-text` by default.
2. If the point compares items on the same criteria, use a table or a `matrix-2x2`.
3. If the point is a sequence, use `process-flow`, `timeline-roadmap`, or `gantt`.
4. If the point is a set of parallel ideas, use `text-columns` or `icon-grid`.
5. Use `text-bullets` last.
6. Do not use the same layout on more than three consecutive slides.

---

## 6. Charts and data

- Build charts as native PowerPoint charts so they stay editable. Use images only for chart types PowerPoint cannot
  build.
- One message per chart. Highlight the bar, line, or segment that carries the message in the accent color, and put
  everything else in a neutral color. Exemplars: `sw-business-strategy-template#287`,
  `sw-business-consulting-toolkit#18` (actuals against forecast).
- Label data directly. Remove gridlines and legends when direct labels are clear.
- Growth callouts: a CAGR or percent change in a small bubble between bars
  (`sw-business-consulting-toolkit#16`, #17).
- Waterfalls for bridges between two totals (`sw-business-consulting-toolkit#54` to #56).
- Stacked 100% bars for mix, clustered columns for comparison across categories, lines for trends over more than
  6 points, bubbles for portfolio positioning (`sw-business-strategy-template#41`, #43).
- Takeaway box to the right of the chart with two to four short points (`chart-plus-text`).
- Every chart has a unit line under the title and a source line at the bottom left.

---

## 7. Tables

- Header row in the dark brand color with white text. Body rows are white or a light tint.
- Right-align numbers and use the same number of decimals down a column.
- Use Harvey balls, traffic lights, or a heatmap tint to show assessment at a glance
  (`sw-business-consulting-toolkit#95`, #106).
- No more than 8 rows and 6 columns on one slide. Split or move to the appendix beyond that.

---

## 8. Visual hierarchy and color use

- One accent color carries the message on each slide. Neutrals carry everything else.
  Exemplar: `sw-business-strategy-template#287`.
- Dark filled header boxes over light body boxes group content clearly (`sw-business-case-template#93`).
- Numbered circles or icons lead parallel items (`sw-business-consulting-toolkit#90`).
- Imagery is either full bleed or placed on the grid. Never use floating clip art.
- White space is deliberate. Do not fill a slide to its edges.

---

## 9. Speaker notes

- Every content slide has notes. The notes give what to say, the evidence behind the title, and the likely
  question with its answer.
- 60 to 150 words per slide. Plain sentences. No em dashes.

---

## 10. How to use the library during a build

1. For each storyline slide, choose the layout from section 5.
2. Search: `python -m deckbuilder library search --category chart-plus-text --curated`, or search full text:
   `python -m deckbuilder library search "market growth CAGR"`.
3. Open two or three thumbnails. Copy the structure (grid, element count, hierarchy). Do not copy the text.
4. For branded decks, build on the brand master's layouts, and take structure from Slideworks exemplars.
5. Record the exemplar ids used for each slide in the storyline file so Mike can see them.
