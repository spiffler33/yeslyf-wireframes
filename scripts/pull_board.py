#!/usr/bin/env python3
"""Export the Supabase table board_entries to data/board_entries.json (phase 11, Vatsal, 16 Sep 2026).

Run it before any v0.3 build: the latest value per page, item and field is the input to the next edit group.
Reads SUPABASE_URL and SUPABASE_ANON_KEY from the environment when both are set, else from docs/config.js
(evaluated in a Node vm context, the way extract_v01.js reads the v0.1 HTML; never parsed by pattern).
Fetches every row 1000 at a time, ordered by id (insertion order), with the key in the apikey header only.
Writes data/board_entries.json:
  pulled_at, source, count
  latest: {page: {item_id: {field: row}}}   the current value per page, item and field (the last row wins)
  rows: [{id, page, item_id, field, value, who, kind, created_at}, ...]   every row, unchanged
Exits 2 when no config is set, 1 when the request fails; nothing is written in either case.
"""
import datetime
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(ROOT, "docs", "config.js")
OUT = os.path.join(ROOT, "data", "board_entries.json")
PAGE_SIZE = 1000
FIELDS = "id,page,item_id,field,value,who,kind,created_at"

NODE_READ_CONFIG = """
const fs = require("fs"), vm = require("vm");
const ctx = {}; vm.createContext(ctx);
vm.runInContext(fs.readFileSync(process.argv[1], "utf8"), ctx);
process.stdout.write(JSON.stringify({url: ctx.SUPABASE_URL || "", key: ctx.SUPABASE_ANON_KEY || ""}));
"""


def load_config():
    url = (os.environ.get("SUPABASE_URL") or "").strip()
    key = (os.environ.get("SUPABASE_ANON_KEY") or "").strip()
    if url and key:
        return url.rstrip("/"), key, "environment"
    if not os.path.exists(CONFIG):
        return "", "", "docs/config.js (missing)"
    proc = subprocess.run(["node", "-e", NODE_READ_CONFIG, CONFIG], capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit("node could not read docs/config.js:\n" + proc.stderr[-2000:])
    cfg = json.loads(proc.stdout)
    return str(cfg.get("url") or "").strip().rstrip("/"), str(cfg.get("key") or "").strip(), "docs/config.js"


def fetch_rows(url, key):
    rows = []
    offset = 0
    while True:
        query = urllib.parse.urlencode({"select": FIELDS, "order": "id.asc", "limit": PAGE_SIZE, "offset": offset})
        req = urllib.request.Request(url + "/rest/v1/board_entries?" + query, headers={"apikey": key, "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            batch = json.loads(resp.read().decode("utf-8"))
        if not isinstance(batch, list):
            raise SystemExit("unexpected response: %r" % (batch,))
        rows.extend(batch)
        if len(batch) < PAGE_SIZE:
            return rows
        offset += PAGE_SIZE


def load_ignore():
    """The test rows (data/board_ignore.json): page, item_id and the minute of created_at in UTC."""
    path = os.path.join(ROOT, "data", "board_ignore.json")
    with open(path) as fh:
        return json.load(fh)["rows"]


def is_ignored(row, ignore):
    minute = str(row.get("created_at", ""))[:16]
    return any(g["page"] == row["page"] and g["item_id"] == row["item_id"] and g["minute"] == minute for g in ignore)


def latest_of(rows):
    latest = {}
    for row in rows:  # rows arrive in id order, so the last write per page, item and field wins
        if row.get("ignored"):
            continue
        latest.setdefault(row["page"], {}).setdefault(row["item_id"], {})[row["field"]] = row
    return latest


def main():
    url, key, source = load_config()
    if not (url and key):
        print("no config: set SUPABASE_URL and SUPABASE_ANON_KEY in docs/config.js or in the environment (%s)" % source)
        return 2
    try:
        rows = fetch_rows(url, key)
    except urllib.error.HTTPError as e:
        print("request refused: HTTP %s %s" % (e.code, e.read().decode("utf-8", "replace")[:300]))
        return 1
    except (urllib.error.URLError, OSError) as e:
        print("request failed: %s" % e)
        return 1
    ignore = load_ignore()
    ignored = 0
    for row in rows:
        if is_ignored(row, ignore):
            row["ignored"] = True
            ignored += 1
    out = {"pulled_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
           "source": "%s, %s/rest/v1/board_entries" % (source, url),
           "note": "Every row of board_entries, unchanged, in id order. latest holds the last row per page, item_id and field; "
                   "that is the current value. Written by scripts/pull_board.py; run it before any v0.3 build. "
                   "Rows carrying ignored true are the test rows of data/board_ignore.json; they are kept here and left out of latest.",
           "count": len(rows), "ignored": ignored, "latest": latest_of(rows), "rows": rows}
    with open(OUT, "w") as fh:
        fh.write(json.dumps(out, indent=1, ensure_ascii=True) + "\n")
    pages = sorted(out["latest"].keys())
    print("wrote data/board_entries.json: %d rows (%d test rows ignored), %d pages%s" % (len(rows), ignored, len(pages), (" (" + ", ".join(pages) + ")") if pages else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
