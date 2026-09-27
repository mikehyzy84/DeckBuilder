# DeckBuilder
The Best PowerPoint Deck Builder You Will Ever Have, or Need

DeckBuilder turns a project folder into a finished, native, editable PowerPoint deck. It is run from Claude Code.

- A master slide database indexes, classifies, and renders every slide in a best-practice template library and in
  each brand's templates.
- Brand extraction reads any brand folder (a corporate master, a client template) into a spec and palette.
- A build helper assembles decks on the brand master, with native charts and tables, images, video, and speaker
  notes.
- Automated QA checks margins, overflow, overlap, contrast, palette, fonts, dashes, placeholder text, and notes, and
  renders every slide for visual review.
- Visual sourcing uses Pexels and Pixabay stock, Runway images and motion, and Veo hero video.

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
brew install --cask libreoffice
cp config.example.yaml config.local.yaml   # fill in paths
cp .env.example .env                       # add keys
python -m deckbuilder check
python -m deckbuilder library build
```

## Use (in Claude Code)

```
/new-project "Acme Digital Strategy"
/build-deck "Acme Digital Strategy" --brand cgi
/add-brand "/path/to/client brand folder" acme
/setup-library
```

See `CLAUDE.md` for the full operating instructions.
