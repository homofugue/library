---
type: work
kind: film
field:
  - "[[]]"
author:
  - "[[]]"
publisher:
published year:
runtime:
label:
url:
original language:
themes:
  - "[[]]"
tags:
  - "work"
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
