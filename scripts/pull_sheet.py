#!/usr/bin/env python3
"""Pull the meeting decisions from the "yeslyf decisions" sheet and cross-check them against the brief.

Sources, in order:
  1. .local/sheet.json published_csv_url, when it is filled in (File, Share, Publish to web; one tab as CSV).
  2. CSV exports dropped by spiff in inputs/meeting/, named "yeslyf decisions - <tab>.csv" for the tabs
     decisions, gaps and quick_accepts (whichever exist).
Writes data/decisions_raw.json (every sheet row, unchanged) and data/decisions.json (last write per item).
Then compares the result with data/decisions_brief.json, the hand transcription of the exported brief.
Any disagreement prints the item and exits 1: stop and ask, do not build.
Test rows (who = curl-test, item_id or gap_id = TEST, input_n = 0) are ignored, per .local/sheet.json.
"""
import csv
import io
import json
import os
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
MEETING = os.path.join(ROOT, "inputs", "meeting")
LOCAL = os.path.join(ROOT, ".local", "sheet.json")
TABS = ("decisions", "gaps", "quick_accepts")


def read_csv_text(text):
    return list(csv.DictReader(io.StringIO(text)))


def load_sources():
    """Return {tab: (source label, rows)} for every tab that could be read."""
    out = {}
    url = ""
    if os.path.exists(LOCAL):
        with open(LOCAL) as fh:
            url = (json.load(fh).get("published_csv_url") or "").strip()
    if url:
        text = urllib.request.urlopen(url, timeout=20).read().decode("utf-8")
        rows = read_csv_text(text)
        if rows and "item_id" in rows[0]:
            out["decisions"] = ("published csv", rows)
        elif rows and "gap_id" in rows[0]:
            out["gaps"] = ("published csv", rows)
        elif rows and "input_n" in rows[0]:
            out["quick_accepts"] = ("published csv", rows)
    for tab in TABS:
        if tab in out:
            continue
        path = os.path.join(MEETING, "yeslyf decisions - %s.csv" % tab)
        if os.path.exists(path):
            with open(path, encoding="utf-8") as fh:
                out[tab] = ("inputs/meeting/yeslyf decisions - %s.csv" % tab, read_csv_text(fh.read()))
    return out


def is_test(row):
    return (row.get("who") == "curl-test" or row.get("item_id") == "TEST" or row.get("gap_id") == "TEST"
            or row.get("input_n") == "0")


def choice_keys(text):
    # The site export writes choice keys as "a, b, c"; a closed format written by docs/index.html itself.
    return [k.strip() for k in (text or "").split(",") if k.strip()]


def last_per(rows, key):
    latest = {}
    for row in sorted(rows, key=lambda r: r["ts"]):
        latest[row[key]] = row
    return latest


def main():
    sources = load_sources()
    if not sources:
        print("no sheet source: published_csv_url is blank and no CSV export is in inputs/meeting/")
        return 2
    with open(os.path.join(DATA, "decisions_brief.json")) as fh:
        brief = json.load(fh)

    raw = {"sources": {tab: label for tab, (label, _) in sources.items()},
           "note": "Every row as exported, including superseded writes. data/decisions.json keeps the last write per item.",
           "rows": {tab: rows for tab, (_, rows) in sources.items()}}
    problems = []
    out = {"sources": raw["sources"], "brief": brief["source"], "items": [], "quick_accepts": [], "gaps": []}

    brief_items = {d["item_id"]: d for d in brief["decisions"]}
    if "decisions" in sources:
        rows = [r for r in sources["decisions"][1] if not is_test(r)]
        latest = last_per(rows, "item_id")
        for item_id, row in sorted(latest.items()):
            keys = choice_keys(row.get("choice"))
            note = (row.get("note") or "").strip()
            b = brief_items.get(item_id)
            if b is None:
                problems.append("%s: in the sheet, not in the brief" % item_id)
                continue
            if sorted(keys) != sorted(b["choice"]) or note != b["note"]:
                problems.append("%s: sheet choice %s note %r, brief choice %s note %r" % (item_id, keys, note, b["choice"], b["note"]))
            out["items"].append({"item_id": item_id, "choice": keys, "note": note, "status": b["status"],
                                 "ts": row["ts"], "decided_by": (row.get("who") or "").strip(), "source": "sheet"})
        for item_id in brief_items:
            if item_id not in latest:
                problems.append("%s: in the brief, not in the sheet" % item_id)
    else:
        for b in brief["decisions"]:
            out["items"].append(dict(b, ts="", decided_by="", source="brief"))
        print("decisions tab not available; taken from the brief")

    brief_qa = {q["n"]: q for q in brief["quick_accepts"]}
    if "quick_accepts" in sources:
        rows = [r for r in sources["quick_accepts"][1] if not is_test(r)]
        latest = last_per(rows, "input_n")
        for n_text, row in latest.items():
            n = int(n_text)
            b = brief_qa.get(n)
            accept = (row.get("accept") or "").strip()
            note = (row.get("note") or "").strip()
            if b is None or accept != b["accept"] or note != b["note"]:
                problems.append("row %d: sheet %s %r, brief %s" % (n, accept, note, b))
            out["quick_accepts"].append({"n": n, "screen": b["screen"] if b else "", "accept": accept, "note": note,
                                         "ts": row["ts"], "source": "sheet"})
        for n, b in brief_qa.items():
            if str(n) not in latest:
                out["quick_accepts"].append(dict(b, ts="", source="brief (not ticked)"))
    else:
        out["quick_accepts"] = [dict(b, ts="", source="brief") for b in brief["quick_accepts"]]
        print("quick_accepts tab not available; taken from the brief")

    brief_gaps = {g["id"]: g for g in brief["gaps"]}
    if "gaps" in sources:
        rows = [r for r in sources["gaps"][1] if not is_test(r)]
        latest = last_per(rows, "gap_id")
        for gap_id, row in latest.items():
            b = brief_gaps.get(gap_id)
            status = (row.get("status") or "").strip()
            note = (row.get("note") or "").strip()
            if b is None or status != b["status"] or note != b["note"]:
                problems.append("gap %s: sheet %r %r, brief %s" % (gap_id, status, note, b))
            out["gaps"].append({"id": gap_id, "status": status, "note": note, "ts": row["ts"], "source": "sheet"})
        for gap_id, b in brief_gaps.items():
            if gap_id not in latest:
                out["gaps"].append(dict(b, ts="", source="brief (no status)"))
    else:
        out["gaps"] = [dict(b, ts="", source="brief") for b in brief["gaps"]]
        print("gaps tab not available; taken from the brief")

    for name, obj in (("decisions_raw.json", raw), ("decisions.json", out)):
        text = json.dumps(obj, indent=1, ensure_ascii=True) + "\n"
        with open(os.path.join(DATA, name), "w") as fh:
            fh.write(text)
        print("wrote data/%s" % name)
    if problems:
        print("DISAGREEMENT between the sheet and the brief; stop and ask:")
        for p in problems:
            print("  " + p)
        return 1
    print("sheet and brief agree: %d items, %d quick-accepts, %d gaps" % (len(out["items"]), len(out["quick_accepts"]), len(out["gaps"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
