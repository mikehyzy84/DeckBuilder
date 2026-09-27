# DeckBuilder

DeckBuilder produces finished, native, editable PowerPoint (.pptx) decks from a project folder. It reads the
project's context and design guide, applies the brand Mike names for that deck, takes layout and storytelling
patterns from the master slide database, sources and generates visuals, and assembles the deck.

Owner: Mike Hyzy. All API usage runs on Mike's CGI keys in `.env`.

Standing goal: every deck is visually striking and is also rigorous consulting work. It has a clear storyline, one
message per slide, native charts, disciplined layout, and strong imagery.

## Storage map

| What | Location | In repo? |
|---|---|---|
| Build code, instructions, docs | This repo (`/Users/mike.hyzy/Documents/DeckBuilder`) | Yes |
| Best-practice template library (no brand), 11 Slideworks decks | `TEMPLATE_LIBRARY_ROOT` = `/Users/mike.hyzy/Documents/Slideworks_full_access_bundle` | No. Read in place. |
| Master slide database: SQLite index, thumbnails, contact sheets | `SLIDE_LIBRARY_ROOT` = `library/` in this repo | No. Gitignored. |
| Brand folders (CGI and any other brand) | Anywhere. Mike names the folder per deck. Known brands are listed under `BRANDS` in `config.local.yaml`. | No. Read in place. |
| Extracted brand specs | `docs/brands/<slug>/brand-spec.md` and `brand.json` | Yes |
| Project folders | `PROJECTS_ROOT` = `projects/` in this repo | No. Gitignored. |
| Rules extracted from the template library | `docs/best-practices.md` | Yes |
| API keys | `.env` | No |
| Local paths | `config.local.yaml` (the template is `config.example.yaml`) | No |

Everything DeckBuilder owns lives in this one folder. `library/` and `projects/` sit inside it, but git ignores
both. Template files, client files, generated decks, images, video, and keys never go to GitHub. `.gitignore` blocks
`/library/`, `/projects/`, `.env`, `config.local.yaml`, and every Office, media, and database file.

## Setup on a new machine

```bash
cd /Users/mike.hyzy/Documents/DeckBuilder
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
brew install --cask libreoffice          # rendering for thumbnails and QA
python -m deckbuilder check              # must print READY
```

## The master slide database

`SLIDE_LIBRARY_ROOT/slides.db` indexes every slide in the template library and in every registered brand folder.
It holds 14 decks and 4,282 slides, and every slide is rendered.

- Tables: `decks`, `slides` (layout category, title, text, notes, word count, charts and chart types, tables,
  pictures, margins, fonts, colors, curated flag, thumbnail path), `layouts` (every master layout with
  placeholder geometry), `overrides` (manual corrections), and `slides_fts` (full text search).
- Slide ids are `<deck-id>#<slide-number>`, for example `sw-business-strategy-template#139`.
- Thumbnails are at `thumbs/<deck-id>/<n>.png`. Contact sheets are at `sheets/<deck-id>/<k>.jpg` (48 slides each)
  and `sheets/curated/`.
- `curated` marks the 210 slides Mike hand-picked in
  `Slideworks_full_access_bundle/claude_design_inputs/selection_index.csv`. Curated slides rank first in searches.

Commands:

```bash
python -m deckbuilder library stats
python -m deckbuilder library search --category chart-plus-text --curated --limit 10
python -m deckbuilder library search "customer journey pain points"
python -m deckbuilder library search --source brand:cgi --category section-divider
python -m deckbuilder library tag <slide_id> --category framework --tags swot --quality 5
python -m deckbuilder library build        # incremental: only new or changed decks are re-indexed
```

Always open the thumbnail before using a slide as an exemplar. Categories come from heuristics, so correct
misclassified slides with `library tag`.

Re-run `library build` whenever decks are added to the template library or a brand folder. It is incremental,
resumes after interruption, renders very large decks in chunks, and writes a placeholder thumbnail for any slide
LibreOffice cannot render.

## Brands

A deck can be CGI-branded, branded for a client or partner, or unbranded. Mike says which brand folder applies to
each deck. Never assume CGI.

1. Brand source, in order: the `--brand` argument to `/build-deck`, then `brand:` in the project's `project.yaml`,
   otherwise ask Mike. If Mike says unbranded, the deck follows `design-guide/` and `best-practices.md` only.
2. `--brand` accepts a slug from `BRANDS` in `config.local.yaml` (for example `cgi`) or an absolute folder path.
3. A folder not seen before is a new brand. Run `/add-brand <folder>`: extract the brand, write
   `docs/brands/<slug>/`, add it to `BRANDS`, index its decks, and get Mike's approval of the spec before building.
4. Brands on file: `cgi`. Its spec is `docs/brands/cgi/brand-spec.md`, and its build master is
   `Standard Presentation Template - 2025.pptx`.

## Rule precedence

1. The project's `design-guide/` governs colors, type, imagery, and tone.
2. The brand spec for the brand Mike named governs anything the design guide does not cover.
3. `docs/best-practices.md` governs structure, layout choice, information density, and storyline for every deck.

A lower-numbered source wins over a higher-numbered one. Report every conflict in the build summary.

## Project folder structure

```
projects/[Project Name]/
  project.yaml    name, brand, audience, objective, decision, slide count, presenter, date
  context/        source material: briefs, notes, data, prior decks
  design-guide/   Claude Design export for this project (optional)
  output/
    storyline.md      approved storyline
    asset-plan.md     approved asset list with sources and credit estimate
    build_deck.py     the build script for this deck (uses deckbuilder.build)
    assets/           images and video, each with a .json sidecar (source, prompt, license)
    qa/               rendered slides, contact sheet, qa_report.json
    [Project Name].pptx
```

Create one with `/new-project "<Name>"` or `python -m deckbuilder project new "<Name>"`.

## Commands

| Command | File | Purpose |
|---|---|---|
| `/build-deck <project-folder> [--brand <slug or folder>]` | `.claude/commands/build-deck.md` | Full build workflow |
| `/new-project "<Name>"` | `.claude/commands/new-project.md` | Scaffold a project folder |
| `/add-brand <folder> [slug]` | `.claude/commands/add-brand.md` | Register and extract a new brand |
| `/setup-library` | `.claude/commands/setup-library.md` | Re-index the slide database and refresh best-practices.md |

## Build workflow (summary; the full steps are in `.claude/commands/build-deck.md`)

1. **Intake.** Run `project scan`. Read every file in `context/` and `design-guide/`. Summarize the audience, the
   objective, the decision or takeaway, the brand, and the design rules found. Ask Mike about anything missing.
   Do not assume.
2. **Storyline.** Write `output/storyline.md` with one headline assertion per slide, supporting points, a named
   layout from `best-practices.md`, one or two exemplar slide ids from the database, the brand layout name, a visual
   brief, and speaker notes. Stop and get Mike's approval.
3. **Assets.** Write `output/asset-plan.md`. For every visual, list the source tier (section Visuals), query or
   prompt, target file, and estimated credits. Stop and get Mike's approval before spending any credits.
4. **Assemble.** Write `output/build_deck.py` using `deckbuilder.build.Deck`. For branded decks, use
   `Deck.from_master(<brand master>)` and brand layouts, so every slide stays editable. For unbranded decks, use
   `Deck.blank()` and follow the design guide. Speaker notes go in the notes field, never on the slide face.
5. **QA.** Run `python -m deckbuilder qa <deck> --brand <slug>`. Then open every rendered slide image and inspect it
   for text overflow, overlap, low contrast, uneven spacing, margins under 0.5 inch, leftover placeholder text,
   visual weight, and alignment. Fix the problems, rebuild, and re-render until QA is clean and every slide passes
   visual inspection.
6. **Report.** Save to `output/`. Report the slide count, assets sourced and generated, credits used, rule
   conflicts, exemplar slides used, and open issues.

## Visuals

Use the first tier that produces a strong result:

1. Native PowerPoint: charts, tables, shapes, icons from the brand master. Free and editable.
2. Stock photography: Pexels first, then Pixabay. Run `python -m deckbuilder stock "<query>"`, review the previews,
   then download with `--download <i> --out <file>`. Free. Record attribution in the sidecar.
3. Runway image (`gen image`) when stock cannot supply the scene, style, or composition needed.
4. Runway image to video (`gen video --image <still>`) for short motion clips of 5 to 10 seconds.
5. Veo through AI Studio (`gen veo`) for hero video only: an opener, a section transition, or a closing moment.

Generation commands refuse to run without `--yes`. Pass `--yes` only after Mike approves the asset plan.

Visual standards:

- Every image serves the slide's message. No generic decoration.
- One visual style per deck. Match the brand imagery rules and the design guide.
- Full-bleed hero images on the cover, the section dividers, and at most one or two emotional moments. Content
  slides use images placed on the grid.
- Video: embedded MP4 with a poster frame. Keep file sizes reasonable. Give every video a still fallback.
- Every image gets alt text in the deck.

## Working rules

- Ask before assuming. Confirm each stage before spending API credits.
- One deliverable at a time.
- Write plain declarative sentences on slides. No filler.
- No em dashes or en dashes in slide text or notes. `Deck.save` and `qa` both enforce this.
- No accent lines under titles and no decorative edge stripes.
- Build charts as native PowerPoint charts, not images, whenever PowerPoint supports the chart type.
- Copy structure from exemplars, never their text.
- Never commit anything marked "No" in the storage map. Run `git status` before every commit and confirm that no
  template, client, output, database, or key file is staged.

## Git

Remote: `https://github.com/mikehyzy84/DeckBuilder` (branch `main`). The remote holds only `README.md`. The first
push from this folder:

```bash
git init -b main
git remote add origin https://github.com/mikehyzy84/DeckBuilder.git
git fetch origin
git reset --soft origin/main        # adopt the remote history; local files stay
git add -A && git status            # confirm no .env, config.local.yaml, pptx, png, db
git commit -m "DeckBuilder: build system, slide database tooling, best practices, CGI brand"
git push -u origin main
```
