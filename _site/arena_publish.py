#!/usr/bin/env python3
"""Push unpublished quotes and marginalia from this vault to an Are.na channel.

Usage:  ARENA_TOKEN=... python3 _site/arena_publish.py [--dry-run]

Scans quotes/ and marginalia/ for notes with `publish: true` and no `blockid`,
creates one Are.na text block per note (POST /v3/blocks) in the channel below,
and writes the returned id back into the note as `blockid:` so the next run
skips it. Also records `channel:` and `user:` so the Are.na Manager plugin in
Obsidian can update the same block later from the desktop.

Settings come from the environment so the token never lives in the repo:
  ARENA_TOKEN     personal access token (are.na/settings/personal-access-tokens)
  ARENA_CHANNEL   channel slug      (default: reading-notes-kda5p5-rvbw)
  ARENA_USER      your Are.na slug  (default: homo-fugue)
"""
import json, os, re, sys, time, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
VAULT = os.path.dirname(HERE)
FOLDERS = ["quotes", "marginalia"]
API = "https://api.are.na/v3"
CHANNEL = os.environ.get("ARENA_CHANNEL", "reading-notes-kda5p5-rvbw")
USER = os.environ.get("ARENA_USER", "homo-fugue")
TOKEN = os.environ.get("ARENA_TOKEN", "")
DRY = "--dry-run" in sys.argv

FM = re.compile(r"^---\n(.*?)\n---\n?", re.S)

def split(text):
    m = FM.match(text)
    if not m: return None, text
    return m.group(1), text[m.end():]

def field(fm, key):
    m = re.search(rf"^{re.escape(key)}:[ \t]*(.*)$", fm, re.M)
    return (m.group(1).strip().strip('"\'') if m else None)

def set_field(fm, key, value):
    line = f"{key}: {value}"
    if re.search(rf"^{re.escape(key)}:", fm, re.M):
        return re.sub(rf"^{re.escape(key)}:.*$", line, fm, count=1, flags=re.M)
    return fm.rstrip("\n") + "\n" + line

def post(path, body):
    req = urllib.request.Request(API + path, data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json",
                 "Accept": "application/json", "User-Agent": "library-vault/arena_publish"},
        method="POST")
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 2:
                wait = int(e.headers.get("X-RateLimit-Reset", "60") or 60)
                print(f"  rate limited, sleeping {wait}s", file=sys.stderr); time.sleep(wait); continue
            raise RuntimeError(f"{e.code} {e.reason}: {e.read().decode(errors='replace')[:300]}")

def main():
    if not TOKEN and not DRY:
        print("ARENA_TOKEN not set; nothing pushed.", file=sys.stderr); return 0
    pushed = skipped = 0
    for folder in FOLDERS:
        d = os.path.join(VAULT, folder)
        if not os.path.isdir(d): continue
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".md"): continue
            p = os.path.join(d, fn)
            text = open(p, encoding="utf-8").read()
            fm, body = split(text)
            if fm is None: continue
            if (field(fm, "publish") or "").lower() != "true": continue
            if field(fm, "blockid"): skipped += 1; continue
            value = body.strip()
            if not value:
                print(f"skip (empty body): {folder}/{fn}", file=sys.stderr); continue
            title = fn[:-3]
            print(f"push: {folder}/{fn}")
            if DRY: pushed += 1; continue
            block = post("/blocks", {"value": value, "title": title, "channels": [CHANNEL]})
            bid = block.get("id") or (block.get("block") or {}).get("id")
            if not bid: raise RuntimeError(f"no id in response: {json.dumps(block)[:300]}")
            fm2 = set_field(fm, "blockid", bid)
            fm2 = set_field(fm2, "channel", CHANNEL)
            fm2 = set_field(fm2, "user", USER)
            open(p, "w", encoding="utf-8").write(f"---\n{fm2}\n---\n{body}")
            pushed += 1
            time.sleep(0.6)  # stay well under the free-tier limit of 120/min
    print(f"{'would push' if DRY else 'pushed'} {pushed}, already published {skipped}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
