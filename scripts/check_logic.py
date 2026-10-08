#!/usr/bin/env python3
"""The content checks of PLAN_logic_panel_v03.md section 11 (phase C1, 12.11; logic plan, 8 Oct 2026) over
data/logic_screens.json and the four page files data/logic_tech.json, logic_access.json, logic_walk.json and
logic_ops.json. Run by hand after the build, like check_phase9.py, never inside build_site.py (plan 12.0). Prints one
"PASS n: <what> (<counts>)" or "FAIL n: <what> (<problems>)" line per check, then at most 20 indented problem lines
under a FAIL, as check_phase9.py does; exits 1 on any FAIL. Read-only: it writes no file (no bytecode, and git status
takes no optional lock), so two runs print the same.

1. schema and targets: build_logic_wireframes.validate_logic_screens(), given the arguments its main() builds,
   returns no problem.
2. seats and writes: every screen's role names the ten seats; every write names seats, each one of the ten, and an
   event listed in that screen's events; every event starts with the screen's base id (the id less its letter).
3. open items both ways: every LQ token ("LQ" and one or more digits, no letter or digit just before it) in any text
   of a screen, or in a page's title, audience, heading, line, table title, column, cell (text and href) or
   open_items entry, is an id in data/logic_gaps.json; every item has a non-empty lands_on and appears where it says:
   a screen id in that screen's spec.dev, a page key in an open_items list of that page, "V" in the spec.dev of at
   least one V screen.
4. walkthroughs: each of w3 to w6 (Y01 to Y04, plan 12.9) carries exactly one table with the five columns of section
   9; in every such table of data/logic_walk.json the seat cell is one of the ten seats or "-", and the screen cell is
   [text, href] or a list of them, each text a screen id and its href "logic_wireframes.html#" plus the text.
5. working days: every "at" cell of those tables parses as "%d %b %Y"; a row whose seat cell is a seat (a staff
   action, section 11) falls Monday to Friday; system, app and client rows carry "-".
6. sums: on every screen every table cell made only of digits and "/", with at least one "/", splits into two or more
   whole numbers summing to 100 (a six-class mix, or sleeve weights).
7. instalments: on L15, L15a and L15b every table cell holding "(" splits on ";" into parts; a part whose last token
   before "(" is a whole number (the sleeve amount, commas stripped) has items inside the brackets split on ", ", each
   ending in its fund amount, and the fund amounts sum to the sleeve amount (12.4: "<sleeve> <amount> (<fund>
   <amount>, ...)", so a fund name carrying digits still reads its amount last).
8. names: no first-cell text of a table row on the board's L04 and L09 (data/screens_v02.json) occurs in any text of
   data/logic_screens.json; build_site.FORBIDDEN is absent from the five pages docs/logic_*.html.
9. protected files: git status --short over the board's protected paths is empty.
"""
import datetime
import json
import os
import string
import subprocess
import sys

sys.dont_write_bytecode = True  # read-only: no __pycache__ beside the scripts it imports
SCRIPTS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPTS)
DOCS = os.path.join(ROOT, "docs")
sys.path.insert(0, SCRIPTS)
import build_site as site  # noqa: E402
import validate_v02  # noqa: E402
from build_logic_pages import GENERIC_VENDOR_LABELS, PAGES  # noqa: E402  (the four page keys)
from build_logic_wireframes import SEATS, all_text, validate_logic_screens  # noqa: E402

HTML_PAGES = ["logic_wireframes.html"] + [key + ".html" for key in PAGES]
WALK_COLS = ["n", "at", "seat", "screen", "action and result"]  # the five columns of section 9
WALK_SECTIONS = ["w3", "w4", "w5", "w6"]  # Y01 to Y04 (plan 12.9)
INSTALMENT_SCREENS = ["L15", "L15a", "L15b"]
PROTECTED = ["data/seed", "docs/seed", "docs/review", "docs/audiences", "data/screens_v02.json",
             "data/admin_screens.json", "data/v02/freeze.json", "data/gaps.json", "data/tracker.json"]
ALNUM = string.ascii_letters + string.digits


def whole(t):
    return t != "" and all(c in string.digits for c in t)


def lq_tokens(text):
    """Every "LQ" followed by one or more digits, with no letter or digit just before it: a plain scan, no regex."""
    out, i = [], text.find("LQ")
    while i >= 0:
        j = i + 2
        while j < len(text) and text[j] in string.digits:
            j += 1
        if j > i + 2 and (i == 0 or text[i - 1] not in ALNUM):
            out.append(text[i:j])
        i = text.find("LQ", i + 2)
    return out


def is_link(c):
    return isinstance(c, list) and len(c) == 2 and all(isinstance(x, str) for x in c)


def table_cells(s):
    """(where, cell) for every row cell of every ui table on screen s; where names the screen, table, row, column."""
    k = 0
    for e in s["ui"]:
        if e[0] != "table":
            continue
        k += 1
        cols = e[1]
        for i, r in enumerate(e[2], 1):
            for j, c in enumerate(r):
                col = cols[j] if j < len(cols) else "column %d" % (j + 1)
                yield "%s table %d (%r) row %d column %r" % (s["id"], k, cols[0] if cols else "", i, col), c


def walk_rows(walk):
    """(problems, rows, steps): a problem for each of w3 to w6 without exactly one table with the five columns of
    section 9; every row of every such table in data/logic_walk.json as (where, row); the step count per section."""
    p, rows, steps = [], [], []
    by = {sec.get("id"): sec for sec in walk["sections"]}
    for w in WALK_SECTIONS:
        k = len([tb for tb in (by.get(w) or {}).get("tables") or [] if tb.get("cols") == WALK_COLS])
        if w not in by:
            p.append("data/logic_walk.json has no section %s" % w)
        elif k != 1:
            p.append("data/logic_walk.json section %s carries %d tables with the five columns of section 9, not 1" % (w, k))
    for sec in walk["sections"]:
        for tb in sec.get("tables") or []:
            if tb.get("cols") == WALK_COLS:
                steps.append("%s %d" % (sec.get("id"), len(tb["rows"])))
                rows += [("data/logic_walk.json section %s step %s" % (sec.get("id"), r[0] if r else "?"), r) for r in tb["rows"]]
    return p, rows, steps


# ---------------------------------------------------------------- the nine checks

def check1(doc, board, integ_rows, reasons):
    """validate_logic_screens with the arguments build_logic_wireframes.main() builds."""
    v02 = board["screens"]
    wireframe_ids = {s["id"] for s in v02}
    live_ids = {s["id"] for s in validate_v02.live(v02)}
    templates = {s["template"] for s in v02}
    vendor_names = [r["vendor"] for r in integ_rows if r["vendor"] not in GENERIC_VENDOR_LABELS]
    p = validate_logic_screens(doc, wireframe_ids, vendor_names, templates, reasons, live_ids)
    return p, "%d screens read; %d board screens as targets" % (len(doc.get("screens", [])), len(wireframe_ids))


def check2(screens):
    p, n_writes, n_events = [], 0, 0
    for s in screens:
        sid = s.get("id")
        role = s.get("role") if isinstance(s.get("role"), dict) else {}
        missing, extra = [x for x in SEATS if x not in role], [x for x in role if x not in SEATS]
        if missing or extra:
            p.append("%s: role misses %s; names %s beyond the ten" % (sid, missing, extra))
        events = s.get("events") if isinstance(s.get("events"), list) else []
        for w in s.get("writes") or []:
            n_writes += 1
            action, seats, event = (w.get("action"), w.get("seats"), w.get("event")) if isinstance(w, dict) else (w, None, None)
            if not isinstance(seats, list) or not seats:
                p.append("%s: write %r names no seats: %r" % (sid, action, seats))
            for x in seats if isinstance(seats, list) else []:
                if x not in SEATS:
                    p.append("%s: write %r: seat %r is not one of the ten" % (sid, action, x))
            if not isinstance(event, str) or not event or event not in events:
                p.append("%s: write %r: event %r is not in its events" % (sid, action, event))
        base = str(sid).rstrip(string.ascii_lowercase)
        for e in events:
            n_events += 1
            if not isinstance(e, str) or not e.startswith(base):
                p.append("%s: event %r does not start with its base id %s" % (sid, e, base))
    return p, "%d screens, %d writes, %d events read" % (len(screens), n_writes, n_events)


def check3(screens, pages, gaps):
    p, found, seen = [], [], set()
    ids = {g["id"] for g in gaps["items"]}
    dev = {}
    for s in screens:
        parts = [(k, v) for k, v in s.items() if k != "spec"] + [("spec." + k, v) for k, v in s["spec"].items()]
        found += [("%s %s" % (s["id"], part), t) for part, v in parts for x in all_text(v) for t in lq_tokens(x)]
        dev[s["id"]] = [t for x in all_text(s["spec"]["dev"]) for t in lq_tokens(x)]
    n_screens = len(found)
    page_items = {}
    for key in PAGES:
        page_items[key] = []
        found += [("data/%s.json %s" % (key, k), t) for k in ("title", "audience")
                  for x in all_text(pages[key].get(k, "")) for t in lq_tokens(x)]
        for sec in pages[key]["sections"]:
            parts = [("heading", sec.get("heading", "")), ("lines", sec.get("lines", []))]
            for tb in sec.get("tables") or []:
                parts += [("table title", tb.get("title", "")), ("table columns", tb.get("cols", [])),
                          ("table cells", tb.get("rows", []))]
            parts.append(("open_items", sec.get("open_items", [])))
            page_items[key] += all_text(sec.get("open_items", []))
            for part, v in parts:
                found += [("data/%s.json section %s %s" % (key, sec.get("id"), part), t) for x in all_text(v) for t in lq_tokens(x)]
    for where, t in found:
        if t not in ids and (where, t) not in seen:
            seen.add((where, t))
            p.append("%s: %s is not an id in data/logic_gaps.json" % (where, t))
    v_screens = [s["id"] for s in screens if s.get("sec") == "V"]
    n_places = 0
    for g in gaps["items"]:
        if not isinstance(g.get("lands_on"), list) or not g["lands_on"]:
            p.append("%s: lands_on %r is empty" % (g["id"], g.get("lands_on")))
            continue
        for place in g["lands_on"]:
            n_places += 1
            if place == "V":
                if not any(g["id"] in dev[v] for v in v_screens):
                    p.append("%s lands on V: no V screen's spec.dev carries it (%s)" % (g["id"], ", ".join(v_screens)))
            elif place in page_items:
                if g["id"] not in page_items[place]:
                    p.append("%s lands on %s: no open_items list of data/%s.json carries it" % (g["id"], place, place))
            elif place in dev:
                if g["id"] not in dev[place]:
                    p.append("%s lands on %s: not in %s's spec.dev" % (g["id"], place, place))
            else:
                p.append("%s: lands_on %r is not a screen id, a page key or V" % (g["id"], place))
    return p, "%d LQ tokens read: %d on screens, %d on pages; %d items, %d places" % (
        len(found), n_screens, len(found) - n_screens, len(gaps["items"]), n_places)


def check4(walk, screen_ids):
    p, rows, steps = walk_rows(walk)
    for where, r in rows:
        if not isinstance(r, list) or len(r) != len(WALK_COLS):
            p.append("%s: row %r is not five cells" % (where, r))
            continue
        if r[2] not in SEATS and r[2] != "-":
            p.append("%s: seat %r is not one of the ten seats or -" % (where, r[2]))
        links = [r[3]] if is_link(r[3]) else r[3]
        if not (isinstance(links, list) and links and all(is_link(x) for x in links)):
            p.append("%s: screen cell %r is not [text, href] or a list of them" % (where, r[3]))
            continue
        for text, href in links:
            if text not in screen_ids:
                p.append("%s: screen %r is not an id in data/logic_screens.json" % (where, text))
            if href != "logic_wireframes.html#" + text:
                p.append("%s: screen %r links to %r, not logic_wireframes.html#%s" % (where, text, href, text))
    return p, "%d steps read: %s" % (len(rows), ", ".join(steps))


def check5(walk):
    p, rows, steps = walk_rows(walk)
    staff = 0
    for where, r in rows:
        at, seat = (r[1], r[2]) if isinstance(r, list) and len(r) == len(WALK_COLS) else (None, None)
        try:
            day = datetime.datetime.strptime(at, "%d %b %Y")
        except (TypeError, ValueError):
            p.append("%s: at %r does not read D Mon YYYY" % (where, at))
            continue
        if seat in SEATS:
            staff += 1
            if day.weekday() > 4:
                p.append("%s: %s, a staff row (%s), falls on a %s" % (where, at, seat, day.strftime("%A")))
    return p, "%d dates read: %s; %d staff rows" % (len(rows), ", ".join(steps), staff)


def check6(screens):
    p, n, on = [], 0, []
    for s in screens:
        for where, c in table_cells(s):
            if not (isinstance(c, str) and "/" in c and all(ch in string.digits + "/" for ch in c)):
                continue
            n += 1
            on += [s["id"]] if s["id"] not in on else []
            parts = c.split("/")
            if not all(whole(x) for x in parts):
                p.append("%s: %r is not two or more whole numbers split by /" % (where, c))
            elif sum(int(x) for x in parts) != 100:
                p.append("%s: %r sums to %d, not 100" % (where, c, sum(int(x) for x in parts)))
    return p, "%d mix and weight cells read on %d screens" % (n, len(on))


def check7(byid):
    p, n = [], 0
    for sid in INSTALMENT_SCREENS:
        if sid not in byid:
            p.append("%s: no such screen" % sid)
            continue
        for where, c in table_cells(byid[sid]):
            if not isinstance(c, str) or "(" not in c:
                continue
            for part in c.split(";"):
                before, _, rest = part.partition("(")
                head = before.split()
                if not rest or not head or not whole(head[-1].replace(",", "")):
                    continue  # no bracket, or no sleeve amount just before it: not an instalment part
                n += 1
                sleeve, items = int(head[-1].replace(",", "")), rest.split(")", 1)[0].split(", ")
                amounts = [(x.split() or [""])[-1].replace(",", "") for x in items]
                if not all(whole(a) for a in amounts):
                    p.append("%s: %r: an item in the brackets does not end in an amount: %s" % (
                        where, part.strip(), [x for x, a in zip(items, amounts) if not whole(a)]))
                elif sum(int(a) for a in amounts) != sleeve:
                    p.append("%s: %r: the fund amounts sum to %d, the sleeve amount is %d" % (
                        where, part.strip(), sum(int(a) for a in amounts), sleeve))
    return p, "%d sleeves read on %s" % (n, ", ".join(INSTALMENT_SCREENS))


def check8(doc, board, html):
    p, names = [], []
    board_by = {s["id"]: s for s in board["screens"]}
    for sid in ("L04", "L09"):
        for e in board_by[sid]["ui"]:
            for r in e[2] if e[0] == "table" else []:
                if r and isinstance(r[0], str) and r[0] and r[0] not in [x for _, x in names]:
                    names.append((sid, r[0]))
    texts = all_text(doc)
    for sid, name in names:
        p += ["data/logic_screens.json: %r (a table row of the board's %s) in %r" % (name, sid, t[:80]) for t in texts if name in t]
    for page in HTML_PAGES:
        for word in site.FORBIDDEN:
            i = html[page].find(word)
            while i >= 0:
                p.append("docs/%s contains %r: ...%s..." % (page, word, html[page][max(0, i - 50):i + len(word) + 30].replace("\n", " ")))
                i = html[page].find(word, i + 1)
    return p, "%d names from the board's L04 and L09; %d pages" % (len(names), len(HTML_PAGES))


def check9(status):
    code, lines, err = status
    if code:
        return ["git status exited %d: %s" % (code, err)], ""
    return ["changed: %s" % x for x in lines], "%d protected paths" % len(PROTECTED)


# ---------------------------------------------------------------- main

def load_all():
    """Everything the checks read, loaded once: the five data files, the gaps, the board, the five pages, and the git
    status of the protected paths (--no-optional-locks: status writes no index, so the run is read-only)."""
    html = {}
    for page in HTML_PAGES:
        with open(os.path.join(DOCS, page)) as fh:
            html[page] = fh.read()
    proc = subprocess.run(["git", "--no-optional-locks", "status", "--short", "--"] + PROTECTED, cwd=ROOT,
                          capture_output=True, text=True)
    return {"doc": site.load("logic_screens.json"), "pages": {key: site.load(key + ".json") for key in PAGES},
            "gaps": site.load("logic_gaps.json"), "board": site.load("screens_v02.json"),
            "integ": site.load("integrations.json")["rows"], "reasons": site.load("compliance_reasons.json")["reasons"],
            "html": html, "status": (proc.returncode, proc.stdout.splitlines(), proc.stderr.strip())}


def run(d):
    """The nine checks over loaded data d (load_all's shape); returns the output lines and the number of checks failed."""
    screens = d["doc"]["screens"]
    byid = {s.get("id"): s for s in screens}
    checks = [
        ("schema and targets", lambda: check1(d["doc"], d["board"], d["integ"], d["reasons"])),
        ("seats and writes", lambda: check2(screens)),
        ("open items both ways", lambda: check3(screens, d["pages"], d["gaps"])),
        ("walkthrough steps name a seat and a screen", lambda: check4(d["pages"]["logic_walk"], set(byid))),
        ("walkthrough dates, staff rows on working days", lambda: check5(d["pages"]["logic_walk"])),
        ("mixes and sleeve weights sum to 100", lambda: check6(screens)),
        ("instalments: a sleeve's funds add up to its amount", lambda: check7(byid)),
        ("names: no board fund name, no FORBIDDEN word", lambda: check8(d["doc"], d["board"], d["html"])),
        ("protected files unchanged", lambda: check9(d["status"])),
    ]
    out, failed = [], 0
    for n, (what, fn) in enumerate(checks, 1):
        try:
            problems, note = fn()
        except Exception as e:  # a shape the check cannot read: named as its FAIL, and the other checks still run
            problems, note = ["raised %s: %s" % (type(e).__name__, e)], ""
        if not problems:
            out.append("PASS %d: %s (%s)" % (n, what, note))
            continue
        failed += 1
        count = "%d problem%s%s" % (len(problems), "" if len(problems) == 1 else "s", ", the first 20 below" if len(problems) > 20 else "")
        out.append("FAIL %d: %s (%s)" % (n, what, count + ("; " + note if note else "")))
        out += ["    " + x for x in problems[:20]]
    return out, failed


def main():
    out, failed = run(load_all())
    print("\n".join(out))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
