#!/usr/bin/env python3
"""Download the high-resolution original for every image note that names one.

Usage:  python3 _site/fetch_hires.py [--dry-run]

Reads images/*.md. For each note with a `hires url`, downloads it into
attachments/ as <note-slug>.hires.<ext> if that file doesn't exist yet, and
records the local path in the note as `hires file:`. The low-res capture in
`file:` is left alone — both copies are kept.

Run this on a machine with normal internet access (your Mac, not the cloud
session, which can't reach archive.org / museum servers).
"""
import os, re, sys, mimetypes, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
VAULT = os.path.dirname(HERE)
IMAGES = os.path.join(VAULT, "images")
ATT = os.path.join(VAULT, "attachments")
DRY = "--dry-run" in sys.argv
FM = re.compile(r"^---\n(.*?)\n---\n?", re.S)

def field(fm, key):
    m = re.search(rf"^{re.escape(key)}:[ \t]*(.*)$", fm, re.M)
    return m.group(1).strip().strip('"') if m else ""

def set_field(fm, key, value):
    line = f"{key}: {value}"
    if re.search(rf"^{re.escape(key)}:", fm, re.M):
        return re.sub(rf"^{re.escape(key)}:.*$", line, fm, count=1, flags=re.M)
    anchor = re.search(r"^hires url:.*$", fm, re.M)
    if anchor:
        return fm[:anchor.end()] + "\n" + line + fm[anchor.end():]
    return fm.rstrip("\n") + "\n" + line

def slug(name):
    s = re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-").lower()
    return s[:80] or "image"

def main():
    os.makedirs(ATT, exist_ok=True)
    n = 0
    for fn in sorted(os.listdir(IMAGES)):
        if not fn.endswith(".md"): continue
        p = os.path.join(IMAGES, fn)
        text = open(p, encoding="utf-8").read()
        m = FM.match(text)
        if not m: continue
        fm, body = m.group(1), text[m.end():]
        url = field(fm, "hires url")
        if not url or field(fm, "hires file"): continue
        print(f"{fn}\n  <- {url}")
        if DRY: continue
        req = urllib.request.Request(url, headers={"User-Agent": "library-vault/fetch_hires"})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                ctype = r.headers.get("Content-Type", "").split(";")[0].strip()
                ext = mimetypes.guess_extension(ctype) or os.path.splitext(url.split("?")[0])[1] or ".bin"
                if ext == ".jpe": ext = ".jpg"
                out = os.path.join(ATT, f"{slug(fn[:-3])}.hires{ext}")
                with open(out, "wb") as f:
                    while chunk := r.read(1 << 20): f.write(chunk)
        except urllib.error.HTTPError as e:
            print(f"  !! {e.code} {e.reason} — leaving note unchanged"); continue
        except Exception as e:
            print(f"  !! {e} — leaving note unchanged"); continue
        rel = os.path.relpath(out, VAULT)
        print(f"  -> {rel} ({os.path.getsize(out)//1024} KB)")
        fm2 = set_field(fm, "hires file", rel)
        open(p, "w", encoding="utf-8").write(f"---\n{fm2}\n---\n{body}")
        n += 1
    print(f"downloaded {n}")

if __name__ == "__main__":
    main()
