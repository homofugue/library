#!/usr/bin/env python3
"""Build the Library Constellation site from this Obsidian vault.

Usage:  python3 _site/build.py
Output: _site/index.html   (standalone page — upload this folder to any static host)
        _site/fragment.html (same page without <html>/<head> wrapper, for Claude artifacts)

Reads every book in books/ and every article in articles/. Covers: set `cover:` to a
vault image ("[[covers/olio.jpg]]" or "covers/olio.jpg") and it is embedded,
or to an https:// URL and it is linked.
"""
import base64, json, mimetypes, os, re, sys
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
VAULT = os.path.dirname(HERE)
LINK = re.compile(r"^\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]$")

# field -> (node type, weight used for link strength and book-to-book affinity)
FIELDS = {
    "themes": ("theme", 1.0), "author": ("person", 1.2), "translator": ("person", 0.8),
    "editor": ("person", 0.6), "publisher": ("imprint", 0.5), "series": ("imprint", 0.6),
    "awards": ("honor", 0.6), "shortlists": ("honor", 0.4), "published": ("geo", 0.2),
    "original language": ("geo", 0.5),
}

def as_list(v):
    if v is None or v == "": return []
    return v if isinstance(v, list) else [v]

def unlink(s):
    s = str(s).strip()
    m = LINK.match(s)
    return m.group(1).strip() if m else s

def cover_src(v):
    if not v: return None
    s = unlink(v)
    if s.startswith(("http://", "https://")): return s
    p = os.path.join(VAULT, s)
    if not os.path.isfile(p): return None
    mt = mimetypes.guess_type(p)[0] or "image/jpeg"
    return f"data:{mt};base64," + base64.b64encode(open(p, "rb").read()).decode()

def languages(v):
    out = []
    for part in re.split(r"\s+and\s+|,", str(v or "")):
        part = part.strip()
        if part: out.append(part)
    return out

books = []
SOURCES = [os.path.join(VAULT, d) for d in ("books", "articles") if os.path.isdir(os.path.join(VAULT, d))]
for BOOKS in SOURCES:
  for fn in sorted(os.listdir(BOOKS)):
      if not fn.endswith(".md"): continue
      text = open(os.path.join(BOOKS, fn), encoding="utf-8").read()
      if not text.startswith("---"): continue
      try:
          fm = yaml.safe_load(text.split("---", 2)[1]) or {}
      except yaml.YAMLError as e:
          print("skip (bad YAML):", fn, e, file=sys.stderr); continue
      if fm.get("type") not in ("book", "article") and "book" not in [str(t) for t in as_list(fm.get("tags"))]: continue
      links = []
      for field, (typ, _) in FIELDS.items():
          vals = languages(fm.get(field)) if field == "original language" else [unlink(x) for x in as_list(fm.get(field))]
          for v in vals:
              if v: links.append({"target": v, "field": field, "type": typ})
      books.append({
          "id": "book:" + fn[:-3], "title": fn[:-3],
          "author": [unlink(a) for a in as_list(fm.get("author"))],
          "translator": [unlink(a) for a in as_list(fm.get("translator"))],
          "editor": [unlink(a) for a in as_list(fm.get("editor"))],
          "publisher": unlink(fm.get("publisher") or fm.get("in") or ""), "kind": fm.get("type", "book"),
          "year": fm.get("published year"), "first": str(fm.get("first published") or ""),
          "language": str(fm.get("original language") or ""), "isbn": str(fm.get("isbn") or ""),
          "firstLine": (fm.get("first line") or "").strip("“”\" "), "summary": fm.get("summary") or "",
          "genre": [t for t in as_list(fm.get("tags")) if t in ("poetry", "fiction", "short-stories", "memoir", "epic", "science-fiction", "slave-narrative")],
          "cover": cover_src(fm.get("cover")), "links": links,
      })

data = {"books": books, "fieldWeights": {k: w for k, (_, w) in FIELDS.items()}}
tpl = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
frag = tpl.replace("/*DATA*/null", json.dumps(data, ensure_ascii=False))
open(os.path.join(HERE, "fragment.html"), "w", encoding="utf-8").write(frag)
page = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n</head>\n<body>\n'
        + frag + "\n</body>\n</html>\n")
open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(page)
print(f"built {len(books)} books -> _site/index.html")
