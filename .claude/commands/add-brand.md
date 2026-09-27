---
description: Register a brand folder (CGI, a client, a partner) so decks can be built on it
argument-hint: <brand-folder> [slug]
---

Brand folder and optional slug: $ARGUMENTS

1. Confirm the folder exists. If no slug is given, propose a short lowercase slug and confirm it with Mike.
2. Run `python -m deckbuilder brand extract "<folder>" --slug <slug>`. This picks the master template, reads the
   theme colors and fonts, lists layouts, finds logo placements, and lists guideline documents. It writes
   `docs/brands/<slug>/brand.json` and a draft `brand-spec.md`.
3. Confirm the chosen master with Mike when the folder holds more than one template.
4. Add `<slug>: "<folder>"` under `BRANDS` in `config.local.yaml`.
5. Run `python -m deckbuilder library build --only <slug>-` to index and render the brand's decks.
6. Complete `brand-spec.md`:
   - Read the guideline PDFs and docs. Open the rendered sample slides (`library search --source brand:<slug>`).
   - Fill in the palette with roles and text-on-color pairs, chart colors, type sizes, logo rules, layout mapping
     to DeckBuilder layout types, imagery, tone, accessibility, and footer or classification rules.
   - Add `palette_allowed` (every approved hex) and `build_master` to `brand.json` so QA can check colors.
   - Use `docs/brands/cgi/brand-spec.md` as the model.
7. Show the spec to Mike for approval. A brand is not used for builds until Mike approves it.
