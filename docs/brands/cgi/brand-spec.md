# Brand spec: CGI

Status: DRAFT for Mike's approval. Extracted on 2026-09-27 from the CGI brand folder.

Brand folder: `/Users/mike.hyzy/Documents/CGI Business Development/CGI Stock`
Machine-readable companion: `docs/brands/cgi/brand.json` (theme, the full layout list with placeholders, the allowed
palette, and gradient stops; `deckbuilder qa --brand cgi` reads it).

## 1. Files in the brand folder

| File | Role |
|---|---|
| `Standard Presentation Template - 2025.pptx` | **Build master.** 89 layouts, 49 sample slides, dated January 2025. Every CGI deck is built from it. |
| `EN-CGI-Standard-presentation-template.potx` | The same template as a .potx (same 49 slides and 89 layouts). Excluded from the slide database as a duplicate. |
| `EN-CGI-Timesaver-template.potx` | Slide library: 426 ready-made CGI diagrams, icons, and layouts. Copy structures from it. Not a build master. |
| `Template_Jan 2025.pptx` | Slide library: 540 starter slides, including stock photo covers and dividers. 21 masters, so do not build from it. |
| `cgi-business-storytelling-worksheet.docx` | CGI storytelling framework. See section 7. |

Both slide libraries are in the slide database under source `brand:cgi`
(`library search --source brand:cgi`).

## 2. Slide size

16:9, 13.333 x 7.5 in.

## 3. Color

Source: sample slides 5 and 6 of the build master (`cgi-standard-presentation-template-2025#5`, `#6`).

### Primary colors

| Name | Hex | Text on it |
|---|---|---|
| Red | `#E31937` | White |
| Purple | `#5236AB` | White |
| White | `#FFFFFF` | Black |
| Black | `#000000` | White |
| Gradient A | `#E31937` > `#A82465` (60%) > `#5236AB` | White |
| Gradient B | `#FFCDD2` > `#FF6A00` (33%) > `#E31937` (66%) > `#991F3D` | White |

### Chart and diagram colors (only for charts and diagrams)

| Family | Shades, dark to light |
|---|---|
| Purple | `#200A58` `#5236AB` `#6E3FED` `#9E83F5` `#BFB5F9` `#CBC3E6` `#E6E3F3` |
| Red | `#650A21` `#991F3D` `#E31937` `#FF6A00` `#FF7362` `#FF978A` `#FFCDD2` |
| Gray | `#000000` `#333333` `#555555` `#777777` `#999999` `#CCCCCC` `#EEEEEE` |
| Magenta | `#7E1B4C` `#A82465` `#CB7CA3` |
| Data status | `#128354` green, `#F1A425` amber, `#B00020` red. Use only for performance, success, warning, error. |

Use white text on the first two or three shades of each family and black text on the lighter shades, as marked on
slide 5.

### Color rules

- Use purple, red, and gray first. Magenta is secondary.
- Pick colors from the CGI custom colors. Never use PowerPoint's Standard colors. The template tells users not to
  pick from Theme colors either. DeckBuilder sets explicit hex values from the table above.
- Theme slots in the master: dk1 `#000000`, lt1 `#FFFFFF`, dk2 `#200A58`, lt2 `#EEEEEE`, accent1 `#5236AB`,
  accent2 `#9E83F5`, accent3 `#CBC3E6`, accent4 `#E31937`, accent5 `#991F3D`, accent6 `#650A21`.
- Native chart series order: `#5236AB`, `#E31937`, `#9E83F5`, `#991F3D`, `#555555`, `#CBC3E6`. Highlight the
  message series in `#E31937` and put the rest in purple and gray shades.

## 4. Type

- Font: Arial for both headings and body. Theme fonts are Arial.
- Master defaults: title 28 pt; body level 1 and level 2 20 pt, level 3 18 pt, level 4 16 pt.
- Sample content slides use 12 to 16 pt body text. DeckBuilder rules: slide body 14 to 16 pt, minimum 12 pt,
  sources and footnotes minimum 9 pt.
- Titles are sentence case and sit in the title placeholder (0.84 in from the left, 0.75 in from the top,
  11.66 in wide, one or two lines).
- Use bold to highlight key phrases in body text, as the samples do. Do not use underline or italics for emphasis.

## 5. Logo

- The logo lives on the layouts, not the slide master. It appears only on:
  - Title slide layouts 1, 2A, 2B: bottom left, 0.84 in from the left, 5.88 in from the top, 1.69 x 0.79 in.
  - Closing layouts (Logo+Cornerstone, Preset tagline+description): bottom right, 10.82 in from the left,
    5.88 in from the top.
  - CV/Resume 2A and 2B: small version, bottom right.
- Never add, move, recolor, or resize the logo. Never put the logo on content slides. It comes with the layout.

## 6. Layouts in the build master

All layout names are in `brand.json`. Skip the "Read Only" separator layouts. DeckBuilder layout types map to
CGI layouts as follows:

| DeckBuilder layout | CGI layout (index) |
|---|---|
| cover | Title slide Layout 1 (1), 2A (2), 2B (3), 3A (4), 3B (5). Use 3A or 3B with a photo, 2A or 2B with gradient, and 1 with cornerstone. |
| agenda | Agenda slide Layout 1 to 5 (6 to 10) |
| executive-summary, text-bullets | Title and Content (12), Title + top subtitle (15) |
| chart-plus-text, chart, table, framework, process-flow, timeline, gantt, matrix, kpi | Title only slide (36), with native content built on the grid; Title + lower subtitle/heading (14) when a subtitle line is needed |
| text-columns, comparison | Title and content two (19), Two content+1 heading (20), Comparison x2 to x5 (21 to 25) |
| image-led | Large image right+content (26), Large image left+content (29), Large title +right image (27), Large title +left image (30), Content + right side image (16) |
| graphic device accent | Content+preset gradient A GD (17), B GD (18), Large title+right graphic device (28), Large graphic device left+content (31) |
| device mockups | Computer, Laptop, Tablet, Mobile + editable screen (32 to 35) |
| split layouts | Vertical split left gradient + content or image (54, 55), Vertical split right gradient (56), Horizontal split top gradient (57) |
| quote-highlight | Content/quote highlight layouts (58 to 66) |
| section-divider | Section header A or B, with background image, plain, or Cornerstone versions (68 to 75) |
| org-team, profile-cv | Team 1 to 10B (42 to 52), CV/Resume layouts (38 to 41) |
| closing | Closing slide A or B: Cornerstone, Contact us, Logo+Cornerstone, Preset tagline (77 to 82, 85 to 87); Q&A Cornerstone (84) |

Content area on the standard layouts: left 0.84 in, top 1.67 in, width 11.66 in, height about 5.0 in. Footer and
slide number sit at 7.62 in from the top. Keep content above 6.9 in.

## 7. Storytelling and tone (from the CGI storytelling worksheet)

- Frame the story as "And, But, Therefore": the conventional world, the trigger or complication, and the new world or
  CGI point of view.
- Write the "Therefore" first, then work back to the problem and the evidence.
- For solution presentations, use the "Professor" layer: audience, thesis, opposition, why this, implications, and
  point of view backed by evidence. For thought leadership, use the "Poet" layer: hero, constriction, desire,
  resistance, relationships, challenges, truth.
- Make the client the hero of the story, with CGI as the guide.
- Use active voice and plain, outcome-focused language.

## 8. Imagery and graphic devices

- Photography: real people at work, architecture, and nature, bright and natural. See the cover and section samples
  (`cgi-standard-presentation-template-2025#10` to `#15`, `#22` to `#25`, `#31`, `#32`).
- Signature device: the "cornerstone" L-shaped gradient block, supplied by layouts. Use the layouts that include it.
  Do not redraw it.
- Ready-made components: symbols, connectors, number bubbles, highlight boxes (`#7`) and buttons (`#8`). Copy them
  from the master instead of drawing new ones.
- Diagrams: take structure from `EN-CGI-Timesaver-template.potx`.

## 9. Accessibility

- Give every slide a unique title (it can be visually hidden only when a layout requires it).
- Add alt text to every picture and chart.
- Keep text contrast at least 4.5:1. `deckbuilder qa` checks this.
- Set the document title in File, Properties.

## 10. Footer

- The build master prints a copyright line ("© 2025 CGI Inc.") and a classification label ("Internal") in the footer
  band.
- Every CGI deck uses **Confidential**. Mike decided this on 2026-09-27. Replace "Internal" with "Confidential"
  wherever it appears on the slide master and layouts before adding slides, then confirm in the QA renders that no
  slide shows "Internal".
