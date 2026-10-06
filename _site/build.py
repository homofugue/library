#!/usr/bin/env python3
"""Build the Library Constellation page from this Obsidian vault.

Usage:  python3 _site/build.py
Output: _site/index.html    standalone page (what GitHub Pages serves)
        _site/fragment.html the same page without the <html>/<head> wrapper (for Claude artifacts)

Every typed note in the vault becomes a node: books and articles (works), quotes,
marginalia, texts, images, people and themes. Wikilinks in frontmatter become edges.
Names that are linked but have no note yet (a publisher, an award, a person you
haven't written up) still appear, drawn hollow. Image notes carry a thumbnail of
their `file:` so the graph can show the picture itself.

Needs: pyyaml, pillow.
"""
import base64, io, json, os, re, sys, unicodedata
NFC = lambda t: unicodedata.normalize("NFC", str(t))
import yaml
try:
    from PIL import Image
except ImportError:
    Image = None

HERE = os.path.dirname(os.path.abspath(__file__))
VAULT = os.path.dirname(HERE)
LINK = re.compile(r"\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]")
FOLDERS = {"fields": "field", "books": "book", "articles": "article", "works": "work", "quotes": "quote", "marginalia": "marginalia",
           "texts": "text", "images": "image", "people": "person", "themes": "theme"}
# field -> (node type of the target, edge weight)
FIELDS = {
    "field": ("field", 1.3), "parent": ("field", 1.5),
    "themes": ("theme", 1.0), "author": ("person", 1.2), "translator": ("person", 0.8),
    "editor": ("person", 0.6), "creator": ("person", 1.0), "via": ("person", 0.5),
    "work": ("work", 1.5), "about": ("work", 1.0), "in": ("imprint", 0.5),
    "publisher": ("imprint", 0.5), "series": ("imprint", 0.6), "institution": ("imprint", 0.5),
    "awards": ("honor", 0.6), "shortlists": ("honor", 0.4), "published": ("geo", 0.2),
    "original language": ("geo", 0.5), "related": ("theme", 0.8),
}
THUMB_W = 420

def as_list(v):
    if v is None or v == "": return []
    return v if isinstance(v, list) else [v]

def links_in(v):
    """All wikilink targets in a scalar or list; bare strings count too for link-typed fields."""
    out = []
    for item in as_list(v):
        s = str(item).strip()
        found = LINK.findall(s)
        if found: out.extend(NFC(t.strip()) for t in found)
        elif s and "://" not in s and len(s) < 80: out.append(NFC(s))
    return out

def languages(v):
    out = []
    for part in re.split(r"\s+and\s+|,|;|\(", str(v or "")):
        part = part.strip().strip(")")
        if part and len(part) < 30 and not any(ch.isdigit() for ch in part): out.append(part)
    return out

def read_note(path):
    text = open(path, encoding="utf-8").read()
    if not text.startswith("---"): return None, ""
    parts = text.split("\n---", 1)
    try: fm = yaml.safe_load(parts[0][4:]) or {}
    except yaml.YAMLError as e:
        print("skip (bad YAML):", path, e, file=sys.stderr); return None, ""
    body = parts[1].lstrip("\n") if len(parts) > 1 else ""
    return fm, body

def strip_bases(body):
    return re.sub(r"```base.*?```", "", body, flags=re.S)

def blockquote(body):
    lines = [l[1:].strip() for l in body.splitlines() if l.startswith(">")]
    return "\n".join(lines).strip()

def plain(body, limit=600):
    b = strip_bases(body)
    b = re.sub(r"!\[\[[^\]]*\]\]", "", b)             # embeds
    b = re.sub(r"\[\[([^\]|]+)(?:\|[^\]]*)?\]\]", r"\1", b)
    b = re.sub(r"^#+\s*", "", b, flags=re.M)
    b = re.sub(r"\n{3,}", "\n\n", b).strip()
    return b[:limit] + ("…" if len(b) > limit else "")

def thumb(rel):
    if not rel or Image is None: return None
    p = os.path.join(VAULT, str(rel).strip())
    if not os.path.isfile(p): return None
    try:
        im = Image.open(p); im.load()
        im = im.convert("RGB")
        w, h = im.size
        if w > THUMB_W:
            im = im.resize((THUMB_W, max(1, round(h * THUMB_W / w))), Image.LANCZOS)
        buf = io.BytesIO(); im.save(buf, "JPEG", quality=72, optimize=True)
        return {"src": "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode(),
                "w": im.size[0], "h": im.size[1], **dominant(im)}
    except Exception as e:
        print("thumb failed:", rel, e, file=sys.stderr); return None

def dominant(im):
    """Dominant hue/saturation/lightness of an image (HSV, 0-360 / 0-1 / 0-1), weighted toward saturated pixels."""
    try:
        small = im.resize((24, 24)).convert("HSV")
        px = list(small.getdata()) if not hasattr(small, 'get_flattened_data') else [tuple(t) for t in small.get_flattened_data()]
        sat = [p for p in px if p[1] > 40 and 20 < p[2] < 240]
        pool = sat if len(sat) >= 20 else px
        import math
        x = sum(math.cos(math.radians(p[0]*360/255)) for p in pool); y = sum(math.sin(math.radians(p[0]*360/255)) for p in pool)
        hue = (math.degrees(math.atan2(y, x)) + 360) % 360
        return {"hue": round(hue), "sat": round(sum(p[1] for p in pool)/len(pool)/255, 2), "light": round(sum(p[2] for p in px)/len(px)/255, 2)}
    except Exception:
        return {}

def cover_src(v):
    if not v: return None
    s = str(v).strip(); m = LINK.search(s)
    if m: s = m.group(1)
    if s.startswith(("http://", "https://")): return s
    t = thumb(s); return t["src"] if t else None

FIELD_NAMES = {NFC(fn[:-3]) for fn in os.listdir(os.path.join(VAULT, "fields"))} if os.path.isdir(os.path.join(VAULT, "fields")) else set()
nodes, edges = {}, []
def node(id_, type_, **kw):
    n = nodes.setdefault(id_, {"id": id_, "type": type_, "title": id_, "stub": True})
    if type_ in ("work", "person", "theme", "field", "imprint", "honor", "geo") and n["type"] in ("imprint", "honor", "geo"):
        n["type"] = type_                      # a name can be promoted (e.g. a journal that is also a work)
    for k, v in kw.items():
        if v not in (None, "", [], {}): n[k] = v
    return n

def edge(a, b, field, w):
    if a == b: return
    edges.append({"source": a, "target": b, "field": field, "w": w})

for folder, kind in FOLDERS.items():
    d = os.path.join(VAULT, folder)
    if not os.path.isdir(d): continue
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".md"): continue
        fm, body = read_note(os.path.join(d, fn))
        if fm is None: continue
        t = fm.get("type") or kind
        name = NFC(fn[:-3])
        ntype = "work" if t in ("book", "article", "work") else t
        n = node(name, ntype, kind=(fm.get("kind") or t) if t == "work" else (t if ntype == "work" else fm.get("kind")), stub=False)
        n["stub"] = False
        n["captured"] = str(fm.get("captured") or "")
        n["publish"] = bool(fm.get("publish"))
        n["themes"] = links_in(fm.get("themes"))
        n["fields"] = links_in(fm.get("field"))
        if ntype == "field":
            n.update({"parent": (links_in(fm.get("parent")) or [""])[0], "text": plain(body, 500),
                      "aliases": [str(a) for a in as_list(fm.get("aliases"))]})
        if ntype == "work":
            n.update({
                "author": links_in(fm.get("author")), "translator": links_in(fm.get("translator")),
                "editor": links_in(fm.get("editor")),
                "publisher": (links_in(fm.get("publisher")) or links_in(fm.get("in")) or [""])[0],
                "year": fm.get("published year"), "first": str(fm.get("first published") or ""),
                "language": str(fm.get("original language") or ""), "isbn": str(fm.get("isbn") or ""),
                "pages": str(fm.get("pages") or ""), "doi": str(fm.get("doi") or ""), "url": str(fm.get("url") or ""),
                "status": str(fm.get("status") or ""), "started": str(fm.get("started") or ""), "finished": str(fm.get("finished") or ""),
                "firstLine": str(fm.get("first line") or "").strip("“”\" "), "summary": str(fm.get("summary") or ""),
                "genre": [x for x in as_list(fm.get("tags")) if x not in ("book", "article")],
                "cover": cover_src(fm.get("cover")), "notes": plain(body, 400),
            })
        elif ntype in ("quote", "marginalia"):
            n.update({"work": (links_in(fm.get("work")) or [""])[0], "page": fm.get("page"),
                      "edition": fm.get("edition year"), "speaker": str(fm.get("speaker") or ""),
                      "quote": blockquote(body) if ntype == "quote" else "",
                      "text": plain(re.sub(r"^>.*$", "", body, flags=re.M), 500),
                      "image": thumb(fm.get("image"))})
            n["title"] = name
        elif ntype == "text":
            n.update({"author": links_in(fm.get("author")), "translator": links_in(fm.get("translator")),
                      "date": str(fm.get("date") or ""), "source": str(fm.get("source") or ""),
                      "sourceUrl": str(fm.get("source url") or ""), "work": (links_in(fm.get("work")) or [""])[0],
                      "language": str(fm.get("original language") or ""), "via": str(fm.get("via") or ""),
                      "text": plain(body, 900), "image": thumb(fm.get("image")),
                      "title": str(fm.get("title") or name)})
        elif ntype == "image":
            n.update({"creator": links_in(fm.get("creator")), "date": str(fm.get("date") or ""),
                      "source": str(fm.get("source") or ""), "sourceUrl": str(fm.get("source url") or ""),
                      "hires": str(fm.get("hires url") or ""), "institution": (links_in(fm.get("institution")) or [""])[0],
                      "inventory": str(fm.get("inventory") or ""), "medium": str(fm.get("medium") or ""),
                      "work": (links_in(fm.get("work")) or [""])[0],
                      "thumb": thumb(fm.get("file") or fm.get("hires file")), "text": plain(body, 700),
                      "title": str(fm.get("title") or name)})
        elif ntype == "person":
            n.update({"roles": [str(r) for r in as_list(fm.get("role"))], "born": str(fm.get("born") or ""),
                      "died": str(fm.get("died") or ""), "nationality": str(fm.get("nationality") or ""),
                      "aliases": [str(a) for a in as_list(fm.get("aliases"))], "text": plain(body, 400)})
        elif ntype == "theme":
            n.update({"proposed": bool(fm.get("proposed")), "text": plain(body, 500), "parent": (links_in(fm.get("parent")) or [""])[0],
                      "aliases": [str(a) for a in as_list(fm.get("aliases"))]})
        # edges from fields
        for field, (ttype, w) in FIELDS.items():
            if field not in fm: continue
            if field == "parent": ttype = ntype          # a theme's parent is a theme (or a field); a field's parent is a field
            vals = languages(fm.get(field)) if field == "original language" else links_in(fm.get(field))
            if field == "via" and not LINK.search(str(fm.get("via") or "")): continue   # free-text via is not a node
            for v in vals:
                tgt = node(v, ttype)
                if field == "parent" and ntype == "theme" and v in FIELD_NAMES: tgt["type"] = "field"
                edge(name, v, field, w)

# ---- trails: ordered walks through the collection ----
trails = []
STOP = re.compile(r"^\s*(\d+)[.)]\s+\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]\s*(?:[—–-]+\s*)?(.*)$", re.M)
tdir = os.path.join(VAULT, "trails")
if os.path.isdir(tdir):
    for fn in sorted(os.listdir(tdir)):
        if not fn.endswith(".md"): continue
        fm, body = read_note(os.path.join(tdir, fn))
        if fm is None: continue
        stops = []
        for line in body.splitlines():
            m = STOP.match(line)
            if m:
                tid = NFC(m.group(2).strip())
                if tid not in nodes: print("trail stop not found:", fn, "->", tid, file=sys.stderr); continue
                stops.append({"id": tid, "note": m.group(3).strip()})
        intro = plain(re.sub(STOP, "", body), 600)
        trails.append({"id": NFC(fn[:-3]), "title": NFC(fm.get("title") or fn[:-3]), "summary": str(fm.get("summary") or ""),
                       "status": str(fm.get("status") or ""), "stops": stops, "intro": intro,
                       "fields": links_in(fm.get("field")), "themes": links_in(fm.get("themes"))})

# any linked-but-unwritten name keeps type from the field that linked it; mark stubs
for n in nodes.values():
    n.setdefault("stub", True)

# ---- semantic level and a deterministic layout from the hierarchy ----
import math, hashlib
def h01(key):  # stable pseudo-random in [0,1)
    return int(hashlib.md5(key.encode("utf-8")).hexdigest()[:8], 16) / 0xFFFFFFFF
nb = {}
for e in edges:
    nb.setdefault(e["source"], []).append(e["target"]); nb.setdefault(e["target"], []).append(e["source"])
def root_field(n):
    """the field a node ultimately hangs from"""
    seen = set(); cur = n
    while cur and cur["id"] not in seen:
        seen.add(cur["id"])
        if cur["type"] == "field": return cur["id"] if not cur.get("parent") else (nodes[cur["parent"]]["id"] if cur["parent"] in nodes else cur["id"])
        if cur["type"] == "theme" and cur.get("parent") and cur["parent"] in nodes: cur = nodes[cur["parent"]]; continue
        if cur.get("fields"): return cur["fields"][0] if cur["fields"][0] in nodes else None
        if cur.get("work") and cur["work"] in nodes: cur = nodes[cur["work"]]; continue
        break
    return None
for n in nodes.values():
    t = n["type"]
    if t == "field": n["level"] = 0
    elif t == "theme": n["level"] = 0 if not n.get("parent") else (1 if nodes.get(n["parent"], {}).get("type") == "field" or not nodes.get(n["parent"], {}).get("parent") else 2)
    elif t == "work": n["level"] = 1
    else: n["level"] = 2
top_fields = [n for n in nodes.values() if n["type"] == "field" and not n.get("parent")]
R0 = 480.0
pos = {}
for i, f in enumerate(sorted(top_fields, key=lambda x: x["id"])):
    a = 2*math.pi*i/max(1, len(top_fields)) - math.pi/2
    pos[f["id"]] = (R0*math.cos(a), R0*math.sin(a))
for f in nodes.values():
    if f["type"] == "field" and f.get("parent") and f["parent"] in pos:
        px, py = pos[f["parent"]]; a = math.atan2(py, px) + .55
        pos[f["id"]] = (px + 170*math.cos(a), py + 170*math.sin(a))
def centroid(ids):
    pts = [pos[i] for i in ids if i in pos]
    if not pts: return None
    return (sum(p[0] for p in pts)/len(pts), sum(p[1] for p in pts)/len(pts))
def jitter(key, r):
    a = 2*math.pi*h01(key); d = r*(.55 + .45*h01(key+"r"))
    return d*math.cos(a), d*math.sin(a)
def place(n, around, r):
    dx, dy = jitter(n["id"], r); pos[n["id"]] = (around[0]+dx, around[1]+dy)
# works near the centroid of their fields
for n in nodes.values():
    if n["type"] == "work":
        c = centroid(n.get("fields") or []) or (0.0, 0.0)
        place(n, c, 150 if n.get("fields") else 90)
# themes: top-level by centroid of connected works/fields, children around parents (two passes for depth)
def theme_anchor(n):
    if n.get("parent") and n["parent"] in pos: return pos[n["parent"]], 95
    c = centroid([i for i in nb.get(n["id"], []) if i in pos and nodes[i]["type"] in ("work", "field")])
    if c: return c, 70
    return (0.0, 0.0), 260
for _ in range(3):
    for n in nodes.values():
        if n["type"] == "theme" and n["id"] not in pos:
            if n.get("parent") and n["parent"] in nodes and n["parent"] not in pos: continue
            c, r = theme_anchor(n); place(n, c, r)
for n in nodes.values():
    if n["type"] == "theme" and n["id"] not in pos: place(n, (0.0, 0.0), 300)
# captures near their work (or field), people / meta near the centroid of what they touch
for n in nodes.values():
    if n["type"] in ("quote", "marginalia", "text", "image"):
        c = pos.get(n.get("work")) or centroid(n.get("fields") or []) or centroid([i for i in nb.get(n["id"], []) if i in pos]) or (0.0, 0.0)
        place(n, c, 48 if n.get("work") in pos else 120)
for n in nodes.values():
    if n["id"] not in pos:
        c = centroid([i for i in nb.get(n["id"], []) if i in pos]) or (0.0, 0.0)
        place(n, c, 60)
for n in nodes.values():
    n["px"], n["py"] = (round(pos[n["id"]][0], 1), round(pos[n["id"]][1], 1))
    n["cluster"] = root_field(n) or ""
    if not n["cluster"]:
        # fall back to the nearest top-level field
        best = min(top_fields, key=lambda f: (pos[f["id"]][0]-n["px"])**2 + (pos[f["id"]][1]-n["py"])**2, default=None)
        n["cluster"] = best["id"] if best else ""

data = {"nodes": list(nodes.values()), "edges": edges, "trails": trails,
        "built": __import__("datetime").date.today().isoformat()}
tpl = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
frag = tpl.replace("/*DATA*/null", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
open(os.path.join(HERE, "fragment.html"), "w", encoding="utf-8").write(frag)
page = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n</head>\n<body>\n'
        + frag + "\n</body>\n</html>\n")
open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(page)
counts = {}
for n in nodes.values(): counts[n["type"]] = counts.get(n["type"], 0) + 1
print("built", counts, "edges", len(edges), "trails", len(trails), "->", f"{os.path.getsize(os.path.join(HERE,'index.html'))//1024} KB")
