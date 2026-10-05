---
type: article
kind: journal article
author:
  - "[[]]"
translator:
editor:
in: "[[]]"
volume:
issue:
pages:
publisher:
published year:
doi:
url:
original language:
themes:
  - "[[]]"
tags:
  - "article"
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
    name: Quotes from this work
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
    name: Marginalia on this work
    order:
      - file.name
      - page
      - captured
    sort:
      - property: page
        direction: ASC
```
