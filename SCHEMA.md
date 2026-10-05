# Library vault — schema

This vault is the source of truth for the library. Everything that is published anywhere else (the constellation site, Are.na, social) is generated from these notes. Edit here, never downstream.

## Layout

```
books/        one note per book (the edition you own/read)
quotes/       one note per quotation
marginalia/   one note per marginal thought (your own words, no excerpt)
people/       authors, translators, editors, recommenders
themes/       thematic hubs
templates/    Obsidian core Templates (Cmd/Ctrl-P → "Insert template")
covers/       cover images, referenced from `cover:`
_site/        build.py (constellation page) and arena_publish.py (Are.na push)
.github/      publish.yml — on every push: Are.na push, site build, GitHub Pages deploy
*.base        Bases views over each note type
```

Folders are by **type**, never by subject. Subject lives in `themes:` links, so a book never has to be moved when it turns out to belong to three subjects.

Every note has `type:` in its frontmatter — `book`, `quote`, `marginalia`, `person`, or `theme`. Bases, the site build, and the Are.na export all filter on it.

Wikilink everything that is a thing: people, themes, publishers, places, awards, series. A link to a note that doesn't exist yet is fine — Obsidian shows it as unresolved and it can be created later from the template.

## Book  (`books/<Title>.md`)

| field | meaning |
|---|---|
| `type` | always `book` |
| `author`, `translator`, `editor` | lists of `[[Person]]` links |
| `publisher`, `series` | `[[link]]` |
| `published year` | year of **this edition** (number) |
| `published` | list of `[[Place]]` where this edition was published |
| `first published` | free text: year of first publication, language/original title if different |
| `original language` | the language the work was written in |
| `read in` | the language you read it in — leave blank if same as original |
| `isbn` | string, keep the quotes |
| `awards`, `shortlists` | lists of `[[Award]]` links |
| `themes` | list of `[[theme]]` links |
| `tags` | keep `book` plus genre tags (`poetry`, `fiction`, `short-stories` …) |
| `cover` | `covers/<file>.jpg` or an https URL |
| `first line` | **blank unless verified against the physical book** |
| `summary` | one or two sentences |
| `status` | `unread` · `reading` · `finished` · `abandoned` · `reference` |
| `started`, `finished` | dates, YYYY-MM-DD. This is the reading log. |
| `via` | how the book reached you: `[[Person]]`, `[[another book]]`, or free text (a syllabus, a review) |
| `file` | link to the PDF/EPUB in `~/Dropbox/library`, e.g. `file:///Users/camilleconsidine/Dropbox/library/memory/Morrison_Site-of-Memory.pdf` |

Body: your notes, then two embedded Bases that list this book's quotes and marginalia automatically (the template includes them). Rereads: add a line under Notes like `- 2027-01: reread for …` and update `started`/`finished` to the latest read.

## Quote  (`quotes/<Author surname> — <few words>.md`)

One quotation per file. A book can have as many as you like; they show up on the book's page via backlinks and the embedded Base.

| field | meaning |
|---|---|
| `type` | `quote` |
| `book` | `[[Book title]]` — the edition in `books/` |
| `page` | number |
| `edition year` | copy of the book's `published year`, so the locator is citable on its own |
| `speaker` | optional — character or voice, if not the author's |
| `themes` | `[[theme]]` links. A quote can join themes the book as a whole doesn't have. |
| `captured` | date you logged it |
| `publish` | `true` makes it eligible for the Are.na export; default `false` |
| `blockid` | Are.na block id, written by the Are.na Manager plugin or `_site/arena_publish.py` after the first push; leave blank |
| `channel` | Are.na channel slug, written on push |
| `user` | your Are.na slug (`homo-fugue`); the plugin refuses to update a block unless this matches |

Body: the quotation in a `>` blockquote, verbatim including the original punctuation, then an attribution line `— Author, *Title*, p. N` (the frontmatter doesn't travel to Are.na, so the block needs this line to be citable). Your gloss, if any, goes below that.

## Marginalia  (`marginalia/<Author surname> — <few words>.md`)

Same shape as a quote, minus `speaker` (and no attribution line), and the body is your own writing rather than an excerpt. Use it for a thought pinned to a page. If there is also a passage you want to keep, make a separate quote note and link the two.

## Person  (`people/<Name>.md`)

`type: person`, `role` (list from: `author`, `translator`, `editor`, `recommender`), `aliases` (other spellings, so links resolve), `born`, `died`, `nationality`. Body optional. Books and quotes reach the person through their own `author`/`translator`/`via` fields; the person page collects them as backlinks.

## Theme  (`themes/<theme>.md`)

`type: theme`, `aliases`, `related` (list of `[[theme]]`). The body should be a paragraph on what the theme means in this library — on the site the theme page is the hub, and an empty node with forty backlinks reads badly.

## Rules of thumb

- Data quality over coverage. Leave a field blank rather than guess. `first line` in particular is only ever filled from the book in hand.
- One fact, one place: a book's edition year lives on the book; the quote copies it only so the quote can be cited alone.
- Names are stable identifiers. Renaming a note renames every link (Obsidian handles this) but breaks `arena block` sync and site URLs, so rename early or not at all.
- New note: create the file in the right folder, insert the matching template, fill it in.

## Publishing

Everything leaves the vault through git. `git push` to `main` runs `.github/workflows/publish.yml`, which:

1. runs `_site/arena_publish.py` — every note in `quotes/` or `marginalia/` with `publish: true` and an empty `blockid` becomes one text block in the Are.na channel `reading-notes-kda5p5-rvbw`; the block id is written back and committed (needs the `ARENA_TOKEN` repository secret);
2. runs `_site/build.py` and deploys `_site/` to GitHub Pages.

From Obsidian you can also push a single note immediately with the **Are.na Manager** plugin (command: *Push note to Are.na*); it writes the same `blockid`/`channel` fields, so the two paths never duplicate a block. To revise a published quote, edit the note and run *Push note to Are.na* again — the plugin updates the existing block.

The plugin's token lives in `.obsidian/plugins/arena-manager/data.json`, which is git-ignored. Never commit a token.
