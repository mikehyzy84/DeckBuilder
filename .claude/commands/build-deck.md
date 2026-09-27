---
description: Build a finished, editable PowerPoint deck from a DeckBuilder project folder
argument-hint: <path-to-project-folder> [--brand <slug-or-folder>]
---

Build a deck for: $ARGUMENTS

Follow CLAUDE.md. Stop at every gate marked STOP and wait for Mike. Never spend API credits before approval.

## 0. Preflight
- `python -m deckbuilder check`. If it is not READY, report what failed and stop.
- Resolve the project folder. A bare name resolves under `PROJECTS_ROOT`.
- `python -m deckbuilder project scan <folder>`.

## 1. Intake
- Read every file in `context/` and `design-guide/`. For .pptx files, extract the text and render thumbnails.
  Open PDFs and images.
- Resolve the brand: the `--brand` argument, then `project.yaml` `brand:`, otherwise ask. If it is a folder not in
  `BRANDS`, run the `/add-brand` steps first.
- Read `docs/brands/<slug>/brand-spec.md` (if branded) and `docs/best-practices.md`.
- Write a summary for Mike: the audience, the objective, the decision or takeaway, the brand, target length,
  classification (for CGI), the design rules found, and conflicts between sources.
- List every missing or unclear item as a question. STOP until Mike answers. Write the answers into `project.yaml`.

## 2. Storyline
- Choose the storyline skeleton from best-practices section 1.4. Adapt it to the objective.
- For each slide, search the database for exemplars: `library search --category <layout> --curated`, or search
  full text. Open the thumbnails.
- Write `output/storyline.md` as a table with one row per slide:
  `# | headline assertion | supporting points | layout | exemplar ids | brand layout | visual brief | speaker notes`
- Check the storyline: read the headlines alone, confirm they make a complete argument, check that no layout
  repeats more than three times in a row, check the density limits, and confirm there are no dashes.
- STOP and get approval. Revise until Mike approves.

## 3. Asset plan
- For each visual brief, pick a tier: native, stock (Pexels or Pixabay), Runway image, Runway video, or Veo.
- Run stock searches now. They are free. Review the preview URLs and shortlist candidates.
- Write `output/asset-plan.md`: slide, tier, query or prompt, output file, and estimated credits. Include total
  estimated credits for Runway and Veo.
- STOP and get approval of the plan and the spend.

## 4. Generate and download
- Download the approved stock images into `output/assets/`. Run the approved generation with `--yes`.
- Open every asset. Reject weak ones and regenerate only within the approved budget. Ask before exceeding it.
- Keep a running tally of credits used.

## 5. Assemble
- Write `output/build_deck.py` using `deckbuilder.build.Deck`:
  - Branded: `Deck.from_master(<brand build master>)`, and `d.add("<brand layout name>", title=...)`.
    If `brand.json` has `footer_classification`, call `d.set_classification(<value>)` right after opening the
    master. CGI is always "Confidential".
  - Unbranded: `Deck.blank()`, with the grid, colors, and type from the design guide.
- Build charts with `d.chart`, tables with `d.table`, text with `d.text` or placeholders, images with `d.image`
  (cover crop), and video with `d.video` (plus a poster frame). Add notes with `d.notes`.
- Call `d.prune_empty_placeholders(slide)` on every slide.
- Set alt text on pictures (`pic._element.nvPicPr.cNvPr.set("descr", "...")`).
- Save to `output/<Project Name>.pptx`.

## 6. QA loop
- `python -m deckbuilder qa "output/<Project Name>.pptx" --brand <slug>`.
- Open `output/qa/contact_sheet.jpg`, then open every slide image in `output/qa/slides/`. Check for overflow,
  overlap, contrast, alignment to the grid, even spacing, margins, visual balance, image quality, and
  placeholder text left behind.
- Fix `build_deck.py`, rebuild, and rerun QA. Repeat until the automated findings are zero, or each remaining
  finding is justified in writing, and every slide passes visual inspection.
- Confirm the file opens cleanly: python-pptx reloads it, and LibreOffice renders every slide.

## 7. Report
Give Mike:
- Path to the deck
- Slide count
- Assets: stock, generated images, and video, with credits used against the estimate
- Rule conflicts and how each was resolved
- Exemplar slides used
- Open issues and suggested next edits
