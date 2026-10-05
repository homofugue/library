---
type: book
field:
author:
  - "[[]]"
translator:
editor:
publisher: "[[]]"
series:
published year:
published:
first published:
original language:
isbn:
awards:
shortlists:
themes:
  - "[[]]"
tags:
  - "book"
cover:
first line:
summary:
status: unread
started:
finished:
via:
read in:
file:
---

## Notes


## Quotes

```base
filters:
  and:
    - note.type == "quote"
    - file.hasLink(this.file)
views:
  - type: table
    name: Quotes from this book
    order:
      - file.name
      - page
      - themes
      - publish
    sort:
      - property: page
        direction: ASC
```

## Marginalia

```base
filters:
  and:
    - note.type == "marginalia"
    - file.hasLink(this.file)
views:
  - type: table
    name: Marginalia on this book
    order:
      - file.name
      - page
      - captured
    sort:
      - property: page
        direction: ASC
```
