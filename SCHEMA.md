# Library vault — schema

This vault is the source of truth for the library. Everything that is published anywhere else (the constellation site, Are.na, social) is generated from these notes. Edit here, never downstream.

## Layout

```
books/        one note per book (the edition you own/read)
fields/       the handful of central fields everything hangs from (literature, poetry, painting, performance, film, psychoanalysis)
articles/     one note per article, essay or chapter — a work, like a book, but living inside a journal or volume
quotes/       one note per quotation
marginalia/   one note per marginal thought (your own words, no excerpt)
images/       one note per image that is a thing in itself (engraving, painting, photo, diagram)
texts/        whole short texts not excerpted from a book you hold: poems, interview remarks, intertitles, posts
attachments/  the image files themselves (screenshots, crops, hi-res downloads)
people/       authors, translators, editors, recommenders
themes/       thematic hubs
templates/    Obsidian core Templates (Cmd/Ctrl-P → "Insert template")
covers/       cover images, referenced from `cover:`
_site/        build.py (constellation page) and arena_publish.py (Are.na push)
.github/      publish.yml — on every push: Are.na push, site build, GitHub Pages deploy
*.base        Bases views over each note type
```

Folders are by **type**, never by subject. Subject lives in `themes:` links, so a book never has to be moved when it turns out to belong to three subjects.

Every note has `type:` in its frontmatter — `field`, `book`, `article`, `quote`, `marginalia`, `person`, `theme`, `image`, or `text`. **Book and article are the two kinds of *work*.** Quotes, marginalia, texts and images point at a work through a `work:` field; `works.base` lists both kinds together. Bases, the site build, and the Are.na export all filter on it.

Wikilink everything that is a thing: people, themes, publishers, places, awards, series. A link to a note that doesn't exist yet is fine — Obsidian shows it as unresolved and it can be created later from the template.

## Field  (`fields/<name>.md`)

The central tags. There are six and they change rarely: **literature** (with **poetry** inside it), **painting**, **performance**, **film**, **psychoanalysis**. Every other note type carries a `field:` list of `[[field]]` links; a note can sit in several (a sonnet sequence about performers is literature, poetry and performance). Themes are for subjects and are many; fields are for disciplines and are few — when in doubt it's a theme.

| field | meaning |
|---|---|
| `type` | `field` |
| `parent` | `[[field]]` for a sub-field (poetry → literature); blank for the top level |
| `aliases` | other names, lowercase |

Body: one sentence on what belongs here. On the graph, fields are the large ringed anchors.

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
| `field` | list of `[[field]]` links — which of the central fields this belongs to |
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

## Article  (`articles/<Title>.md`)

A work that lives inside something else: a journal article, an essay in a collection, a book chapter. Same reading-log fields as a book (`status`, `started`, `finished`, `via`, `read in`, `file`) and the same embedded Quotes/Marginalia bases in the body.

| field | meaning |
|---|---|
| `type` | `article` |
| `kind` | `journal article` · `chapter` · `essay` · `review` |
| `author`, `translator`, `editor` | `[[Person]]` lists |
| `in` | `[[Journal or volume title]]` |
| `volume`, `issue`, `pages` | as printed; `pages` as a quoted string (`"777–795"`) |
| `publisher`, `published year` | of the issue or volume |
| `doi`, `url` | one stable locator |
| `summary`, `themes`, `tags` | as for books; keep `article` in tags |

## Quote  (`quotes/<Author surname> — <few words>.md`)

One quotation per file. A book can have as many as you like; they show up on the book's page via backlinks and the embedded Base.

| field | meaning |
|---|---|
| `type` | `quote` |
| `work` | `[[title]]` — the book in `books/` or the article in `articles/` |
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
- Names are stable identifiers. Renaming a note renames every link (Obsidian handles this) but breaks `blockid` sync and site URLs, so rename early or not at all.
- New note: create the file in the right folder, insert the matching template, fill it in.

## Publishing

Everything leaves the vault through git. `git push` to `main` runs `.github/workflows/publish.yml`, which:

1. runs `_site/arena_publish.py` — every note in `quotes/` or `marginalia/` with `publish: true` and an empty `blockid` becomes one text block in the Are.na channel `reading-notes-kda5p5-rvbw`; the block id is written back and committed (needs the `ARENA_TOKEN` repository secret);
2. runs `_site/build.py` and deploys `_site/` to GitHub Pages.

From Obsidian you can also push a single note immediately with the **Are.na Manager** plugin (command: *Push note to Are.na*); it writes the same `blockid`/`channel` fields, so the two paths never duplicate a block. To revise a published quote, edit the note and run *Push note to Are.na* again — the plugin updates the existing block.

The plugin's token lives in `.obsidian/plugins/arena-manager/data.json`, which is git-ignored. Never commit a token.

## Image  (`images/<creator or subject> — <title>.md`)

For a thing that *is* a picture: an archival engraving, a painting, a photograph, a diagram, a meme. One note per image; the file itself lives in `attachments/`.

| field | meaning |
|---|---|
| `type` | `image` |
| `kind` | `archival` · `artwork` · `photograph` · `diagram` · `screenshot` · `meme` |
| `title` | the work's title or a plain description |
| `creator` | `[[Person]]` — artist, photographer, engraver; blank if unknown |
| `date` | of the image or work (free text: `c. 1320–1330`, `1907 (this edition)`) |
| `source` | a full citation: book + figure + page, or museum + inventory, or "Source not yet identified" |
| `source url` | where the citation can be checked |
| `hires url` | the best copy online (IIIF, archive.org, publisher's own image). `_site/fetch_hires.py` downloads it |
| `hires file` | filled by `fetch_hires.py` |
| `work` | optional `[[book or article]]` the figure comes from |
| `institution`, `inventory`, `medium`, `rights` | for artworks and archival material |
| `file` | the local copy you actually have (usually the screenshot, cropped) |
| `captured from` | how it reached you: phone screenshot, Instagram, X … |
| `themes`, `captured`, `publish`, `blockid`, `channel`, `user` | as elsewhere |

Body: `![[attachments/…]]` then what you know and don't know. Say explicitly when an identification is probable rather than confirmed.

## Text  (`texts/<author> — <title>.md`)

For a short text that is not an excerpt from a book in `books/`: a whole poem, an interview remark, a film intertitle, a social-media post, a notice in a periodical. The image you captured it from is kept as an associated object in `image:` and embedded at the end of the body.

| field | meaning |
|---|---|
| `type` | `text` |
| `kind` | `poem` · `excerpt` · `interview` · `intertitle` · `post` · `notice` |
| `work` | optional `[[book or article]]` — a text *can* belong to a work (a poem from a collection you hold) but needn't (a tweet, an intertitle) |
| `title`, `author`, `translator` | `[[Person]]` links where the person has or deserves a note |
| `date` | of composition (the poem's date, not the capture date) |
| `source`, `source url` | the book, broadcast or URL it comes from; say "not yet identified" rather than guess |
| `original language`, `read in` | as for books |
| `image` | `attachments/…` — the screenshot or still it was captured from |
| `via` | who/what surfaced it (a handle, a feed, a friend) |

A quotation *from a work you have a note for* is a `quote`. A whole poem is a `text`, whether or not it also links to the collection it comes from — the difference is that a quote is an excerpt and a text is complete in itself.

## Attachments

All image files go in `attachments/` (Obsidian is set to put pasted images there). Name them descriptively in kebab-case: `didron-fig152-thrones.png`, `issa-a-bath-when-youre-born.jpg`. Keep the capture even after the hi-res arrives; the capture is the record of where it came from.

## Proposed themes

Themes created by Claude carry `proposed: true` until you've looked at them. `themes.base` → "Proposed (review me)" lists them; flip the field to `false` to accept, or delete the note (and fix the links) to reject.
