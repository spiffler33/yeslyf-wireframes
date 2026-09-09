#!/usr/bin/env python3
"""Parse the five markdown review exports into data/inputs.json.

The export format is fixed by exportNotes() in inputs/v01/yeslyf_wireframes_v0.1.html:
  "## <section>", then "- **<ID> <title>**[ [<Verdict>]]", then comment lines indented by two spaces.
Each comment is mapped to its row number in the v0.1 review log (data/review_rows_v01.json, rows 1 to 73)
by (reviewer, screen). The log split two comments across two rows and merged a few comments on one
row; those cases are listed explicitly below, not guessed.
Phase 1b (scripts/assign_inputs.py) adds workstream, owner and status.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REVIEWS = os.path.join(ROOT, "inputs", "reviews")
DATA = os.path.join(ROOT, "data")

REVIEWERS = ["Bhuvanaa", "Gaurav", "Harish", "Kajal", "Somil"]

# Comments the log filed under a different screen id than the export used.
RELOCATED = {
    ("Somil", "A08"): 27,   # logged on row 27 with Gaurav's A07 note
    ("Somil", "H02"): 41,   # logged as one row "H02-H04"
    ("Somil", "H03"): 41,
    ("Somil", "H04"): 41,
}
# Comments the log split in two: the last paragraph went to the second row.
SPLIT_LAST_PARAGRAPH = {
    ("Gaurav", "R02"): (8, 9),
    ("Bhuvanaa", "O01"): (24, 25),
}
# Verdict-only entries (no comment text) are summarised by the log on one row per reviewer.
KEEP_ONLY_ROW = {"Somil": 56}


def reviewer_of(filename):
    low = filename.lower()
    hits = [r for r in REVIEWERS if r.lower() in low]
    if len(hits) != 1:
        raise SystemExit("cannot tell the reviewer of " + filename)
    return hits[0]


def parse_file(path):
    reviewer = reviewer_of(os.path.basename(path))
    entries = []
    section = ""
    current = None
    with open(path, encoding="ascii") as fh:
        for raw in fh.read().split("\n"):
            line = raw.rstrip()
            if line.startswith("## "):
                section = line[3:].strip()
                current = None
            elif line.startswith("- **"):
                head = line[4:]
                close = head.index("**")
                id_title = head[:close]
                rest = head[close + 2:]
                screen, _, title = id_title.partition(" ")
                verdict = ""
                if rest.startswith(" [") and rest.endswith("]"):
                    verdict = rest[2:-1]
                current = {"reviewer": reviewer, "section": section, "screen": screen, "title": title,
                           "verdict": verdict, "lines": [], "file": os.path.basename(path)}
                entries.append(current)
            elif current is not None:
                if line.startswith("  "):
                    current["lines"].append(line[2:])
                elif line == "":
                    current["lines"].append("")
                else:
                    current["lines"].append(line)
    for e in entries:
        lines = e.pop("lines")
        while lines and lines[-1] == "":
            lines.pop()
        while lines and lines[0] == "":
            lines.pop(0)
        e["text"] = "\n".join(lines)
    return entries


def paragraphs(text):
    out, cur = [], []
    for line in text.split("\n"):
        if line.strip() == "":
            if cur:
                out.append("\n".join(cur))
                cur = []
        else:
            cur.append(line)
    if cur:
        out.append("\n".join(cur))
    return out


def main():
    with open(os.path.join(DATA, "review_rows_v01.json")) as fh:
        log_rows = json.load(fh)["rows"]
    by_n = {r["n"]: r for r in log_rows}

    comments = []
    for name in sorted(os.listdir(REVIEWS)):
        if name.endswith(".md"):
            comments.extend(parse_file(os.path.join(REVIEWS, name)))

    sources = {n: [] for n in by_n}
    keep_only = {}
    problems = []
    for c in comments:
        key = (c["reviewer"], c["screen"])
        if not c["text"]:
            if c["verdict"] and c["reviewer"] in KEEP_ONLY_ROW:
                keep_only.setdefault(c["reviewer"], []).append((c["screen"], c["verdict"]))
                continue
            problems.append("empty comment without a summary row: %s %s" % key)
            continue
        src = {"reviewer": c["reviewer"], "screen": c["screen"], "title": c["title"], "verdict": c["verdict"],
               "text": c["text"], "file": c["file"]}
        if key in SPLIT_LAST_PARAGRAPH:
            first_n, last_n = SPLIT_LAST_PARAGRAPH[key]
            paras = paragraphs(c["text"])
            head, tail = dict(src), dict(src)
            head["text"] = "\n\n".join(paras[:-1])
            head["part"] = "first part of the %s comment" % c["screen"]
            tail["text"] = paras[-1]
            tail["part"] = "last paragraph of the %s comment" % c["screen"]
            sources[first_n].append(head)
            sources[last_n].append(tail)
            continue
        if key in RELOCATED:
            sources[RELOCATED[key]].append(src)
            continue
        matches = [r["n"] for r in log_rows if c["reviewer"] in r["who"].split(", ") and r["scr"] == c["screen"]]
        if len(matches) != 1:
            problems.append("no unique log row for %s %s: %s" % (key[0], key[1], matches))
            continue
        sources[matches[0]].append(src)

    for reviewer, n in KEEP_ONLY_ROW.items():
        items = keep_only.get(reviewer, [])
        verdicts = sorted(set(v for _, v in items))
        ids = [s for s, _ in items]
        text = "[%s] with no comment on %d screens: %s" % ("/".join(verdicts), len(ids), ", ".join(ids))
        sources[n].append({"reviewer": reviewer, "screen": "All", "title": "All screens", "verdict": "/".join(verdicts),
                           "text": text, "file": "", "screens": ids})

    rows = []
    for n in sorted(by_n):
        log = by_n[n]
        src = sources[n]
        if not src:
            problems.append("log row %d (%s, %s) has no source comment" % (n, log["who"], log["scr"]))
            continue
        names = [s["reviewer"] for s in src]
        for who in log["who"].split(", "):
            if who not in names:
                problems.append("log row %d names %s but no comment of theirs maps to it" % (n, who))
        row = {"n": n, "reviewer": log["who"], "screen": log["scr"],
               "verdict": src[0]["verdict"] if len(src) == 1 else "",
               "text": src[0]["text"] if len(src) == 1 else "\n\n".join("%s (%s): %s" % (s["reviewer"], s["screen"], s["text"]) for s in src),
               "sources": src, "log_say": log["say"]}
        rows.append(row)

    if problems:
        for p in problems:
            print("PROBLEM: " + p)
        sys.exit(1)

    out = {"source": "inputs/reviews/*.md mapped to the row numbers of inputs/v01/yeslyf_review_log_v0.1.html",
           "rows": rows}
    text = json.dumps(out, indent=1, ensure_ascii=True) + "\n"
    with open(os.path.join(DATA, "inputs.json"), "w") as fh:
        fh.write(text)
    per = {}
    for c in comments:
        per[c["reviewer"]] = per.get(c["reviewer"], 0) + 1
    print("comments parsed per reviewer:", per)
    print("keep-only entries:", {k: len(v) for k, v in keep_only.items()})
    print("rows written:", len(rows))
    for r in rows:
        print("%2d | %-22s | %-7s | %s" % (r["n"], r["reviewer"], r["screen"], ", ".join("%s:%s%s" % (s["reviewer"], s["screen"], "(" + s["part"][:4] + ")" if "part" in s else "") for s in r["sources"])))


if __name__ == "__main__":
    main()
