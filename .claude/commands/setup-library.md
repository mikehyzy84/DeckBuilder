---
description: Re-index the master slide database and refresh best-practices.md after templates change
---

Run this after decks are added to the template library or a brand folder.

1. `python -m deckbuilder library build`. It is incremental: only new or changed decks are re-indexed and rendered.
   Decks that have been removed are dropped from the database.
2. `python -m deckbuilder library stats`. Report the new decks and slide counts to Mike.
3. For each new deck, open its contact sheets (`library sheet <deck-id>`). Correct misclassified slides with
   `library tag`.
4. Update `docs/best-practices.md`:
   - Add new layout patterns, storyline skeletons, and exemplar ids.
   - Keep rules in your own words. Reference template slides by id. Do not copy template text.
5. Update any brand spec whose folder changed.
6. Show Mike the diff of both docs for approval.
