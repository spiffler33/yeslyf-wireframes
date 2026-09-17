#!/usr/bin/env python3
"""Import Spinach's field-level questions from an Excel file into the board table (phase 12, pass 3; Vatsal,
17 Sep 2026): one board row per line under the identity "Spinach (Ankur)", page wireframes_v02, item_id the screen
ID, field "question", value "<field>: <question>", kind comment. The questions then show under the screen's comment
box on the Wireframes v0.2 tab and in the Tracker's question list; an answer is a later row on the same screen with
field "answer".

Usage:
  python3 scripts/import_questions.py <file.xlsx>            dry run: prints every row it would write, and the problems
  python3 scripts/import_questions.py <file.xlsx> --send     writes the rows (after a clean dry run only)
  options: --who "Spinach (Ankur)"   --sheet 1   --columns screen,field,question   (header names, case-insensitive)

The workbook is read with the standard library only (an xlsx is a zip of XML: xl/sharedStrings.xml and
xl/worksheets/sheetN.xml). The first row is the header; the three columns are found by name (screen, field,
question; an ID column reading A10b also counts as screen). A screen ID must be a live v0.2 screen. Nothing is
written on a dry run, and nothing is written when any line has a problem. The config comes from docs/config.js
or the environment, as in scripts/pull_board.py; the key is the public anon key and the insert is the same one the
pages make.
"""
import json
import os
import sys
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPTS)
sys.path.insert(0, SCRIPTS)
import pull_board  # noqa: E402

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
WHO = "Spinach (Ankur)"
PAGE = "wireframes_v02"
FIELD = "question"


def col_index(ref):
    """The 0-based column of a cell reference like C7."""
    n = 0
    for ch in ref:
        if ch.isalpha():
            n = n * 26 + (ord(ch.upper()) - 64)
        else:
            break
    return n - 1


def read_sheet(path, sheet=1):
    """Rows of the sheet as lists of strings (shared strings and inline strings resolved; numbers as typed)."""
    with zipfile.ZipFile(path) as z:
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            root = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in root.findall("m:si", NS):
                shared.append("".join(t.text or "" for t in si.iter("{%s}t" % NS["m"])))
        name = "xl/worksheets/sheet%d.xml" % sheet
        if name not in z.namelist():
            raise SystemExit("%s has no %s" % (path, name))
        root = ET.fromstring(z.read(name))
    rows = []
    for row in root.iter("{%s}row" % NS["m"]):
        cells = {}
        for c in row.findall("m:c", NS):
            ref = c.get("r", "")
            kind = c.get("t", "")
            v = c.find("m:v", NS)
            if kind == "s" and v is not None:
                text = shared[int(v.text)]
            elif kind == "inlineStr":
                text = "".join(t.text or "" for t in c.iter("{%s}t" % NS["m"]))
            else:
                text = v.text if v is not None else ""
            cells[col_index(ref)] = (text or "").strip()
        if cells:
            width = max(cells) + 1
            rows.append([cells.get(i, "") for i in range(width)])
    return rows


def find_columns(header, wanted):
    """The column index per wanted name; a header cell matches when it equals the name or contains it as a word."""
    low = [h.strip().lower() for h in header]
    out = {}
    for name in wanted:
        hit = None
        for i, h in enumerate(low):
            if h == name or name in h.replace("_", " ").split():
                hit = i
                break
        if hit is None and name == "screen":
            for i, h in enumerate(low):
                if h in ("id", "screen id", "screen_id"):
                    hit = i
                    break
        out[name] = hit
    return out


def live_screen_ids():
    with open(os.path.join(ROOT, "data", "screens_v02.json")) as fh:
        screens = json.load(fh)["screens"]
    return {s["id"] for s in screens if s["v02"]["status"] not in ("dropped", "split")}


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    path = args[0]
    send = "--send" in argv
    who = WHO
    sheet = 1
    columns = ["screen", "field", "question"]
    for i, a in enumerate(argv):
        if a == "--who" and i + 1 < len(argv):
            who = argv[i + 1]
        if a == "--sheet" and i + 1 < len(argv):
            sheet = int(argv[i + 1])
        if a == "--columns" and i + 1 < len(argv):
            columns = [c.strip().lower() for c in argv[i + 1].split(",")]
    if not (who == "Spinach" or who.startswith("Spinach (")):
        print("the identity must be Spinach or Spinach (name); got %r" % who)
        return 2
    rows = read_sheet(path, sheet)
    if not rows:
        print("no rows in sheet %d" % sheet)
        return 1
    cols = find_columns(rows[0], columns)
    missing = [n for n, i in cols.items() if i is None]
    if missing:
        print("header row %r has no column for: %s" % (rows[0], ", ".join(missing)))
        return 1
    live = live_screen_ids()
    out, problems = [], []
    for n, r in enumerate(rows[1:], start=2):
        def cell(name):
            i = cols[name]
            return r[i] if i < len(r) else ""
        sid, field, question = cell(columns[0]), cell(columns[1]), cell(columns[2])
        if not (sid or field or question):
            continue
        if sid not in live:
            problems.append("line %d: screen %r is not a live v0.2 screen" % (n, sid))
        if not question:
            problems.append("line %d: no question" % n)
        value = ("%s: %s" % (field, question)) if field else question
        out.append({"page": PAGE, "item_id": sid, "field": FIELD, "value": value, "who": who, "kind": "comment"})
    print("%d lines read from %s (sheet %d); %d rows to write as %s" % (len(rows) - 1, os.path.basename(path), sheet, len(out), who))
    for row in out:
        print("  %s  %s" % (row["item_id"], row["value"][:110]))
    for p in problems:
        print("PROBLEM: " + p)
    if problems:
        print("nothing written: fix the lines above first")
        return 1
    if not send:
        print("dry run; add --send to write these %d rows" % len(out))
        return 0
    url, key, source = pull_board.load_config()
    if not (url and key):
        print("no config: set SUPABASE_URL and SUPABASE_ANON_KEY in docs/config.js or in the environment (%s)" % source)
        return 2
    req = urllib.request.Request(url + "/rest/v1/board_entries", data=json.dumps(out).encode("utf-8"), method="POST",
                                 headers={"apikey": key, "Content-Type": "application/json", "Prefer": "return=representation"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        written = json.loads(resp.read().decode("utf-8"))
    print("wrote %d rows (ids %s to %s); run scripts/pull_board.py to copy them into data/board_entries.json" % (
        len(written), written[0]["id"] if written else "-", written[-1]["id"] if written else "-"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
