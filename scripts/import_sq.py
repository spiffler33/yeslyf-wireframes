#!/usr/bin/env python3
"""Import a Spinach questionnaire batch into data/questions.json (phase 14, pass 1; Vatsal, 24 Sep 2026).

Reads the three xlsx files of the batch with the standard library (zipfile plus XML, through
scripts/import_questions.read_sheet) and the answer set SQ1_answers.md next to them, matches every sheet row that
carries a question to exactly one id of the answer set, validates statuses, owners, causes and refs against the
board's data, and writes data/questions.json. The answer text is copied verbatim and never edited here.

Usage:
  python3 scripts/import_sq.py            dry run: prints every row it would write and every problem; writes nothing
  python3 scripts/import_sq.py --write    writes data/questions.json after a clean dry run only

The id scheme is the answer set's (yeslyf_phase14_brief.md, 1.2): FE-01 to FE-80 from the Sr No column of the main
frontend sheet; FE-F1.., FE-N1.., FE-C3.., FE-P1.., FE-S1.., FE-D1.., FE-R1.., FE-M1.., FE-O1.. from the supplementary
sheets by sheet and Sr No; FE-X1 to FE-X5 by order (the Integrations sheet numbers two rows 5); BE-01 to BE-15 in
row order; JD-SUM-1 to JD-SUM-5 the journey rows of the summary sheet (the answer applies to the "Key open area"
cell); JD-<journey>-<block><n> per journey sheet, the blocks being W (the rows after the "Screen / Step" header up
to "Detailed Edge Cases"), E (after the "Edge Case" header up to the screen-sequence or API block), API (after
"API ID"), M (the "Recommendation" row of the screen-sequence block) and H1 (the Onboarding header block, Entry
criteria to Source status, as one item). Journey rows match by their order within the block (Vatsal, 26 Sep 2026:
match by order); the M row is found by its label and the H1 block by its bounds. The answer set's row column quotes
the sheet row, and the importer compares its first three words with the sheet row's (case-insensitive, punctuation
as separators): a quote that differs is reported as a note for the pass report, not a problem, since the position
is the match.

Refs resolve against data/screens_v02.json (live screens), data/v02/states.json, data/integrations.json,
data/tracker.json, the answer set's own ids and a short list of literals. A W ref that is not on the Tracker yet
but is announced in Part F of the answer set is reported as pending (pass 2 adds the rows); the dry run is clean
without it, and a second run after pass 2 must show none pending.

Non-ASCII characters in Spinach's own cells (dashes, arrows, quotes) are kept verbatim in the data and escaped by
json.dump, so the file stays ASCII while the text does not change.
"""
import datetime
import json
import os
import sys
import zipfile
import xml.etree.ElementTree as ET

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPTS)
sys.path.insert(0, SCRIPTS)
from import_questions import read_sheet, NS  # noqa: E402

INPUT_DIR = os.path.join(ROOT, "inputs", "spinach", "2026-09-22")
ANSWERS = "SQ1_answers.md"
OUT = os.path.join(ROOT, "data", "questions.json")
BATCH = {"id": "SQ1", "received": "2026-09-22", "answered": "2026-09-24"}
CHANGED = "2026-09-24"
# original file name, export file name (brief 4.1), id family
FILES = [
    ("2026_Sep_22nd_Frontend_Technical_Questionaire.xlsx", "SQ1_2026_Sep_22nd_Frontend_Technical_Questionaire.xlsx", "FE"),
    ("Yesly Backend Clarifications Questionaire.xlsx", "SQ1_Yesly_Backend_Clarifications_Questionaire.xlsx", "BE"),
    ("2026_Sep_22nd_Yesly_Journey_Description.xlsx", "SQ1_2026_Sep_22nd_Yesly_Journey_Description.xlsx", "JD"),
]
CAUSE_ACCEPTED = "Spinach proposal SQ1, accepted, Vatsal, 24 Sep 2026"
CAUSE_VATSAL = "Vatsal, 24 Sep 2026"
ACCEPTED_OPENING = "Accepted as proposed"
STATUSES = ("frozen", "open", "owed")
MARKERS = {"open": "to be decided:", "owed": "to be verified:"}
OWNER_LABELS = {"Product", "Tech", "Admin", "Compliance", "Financial planning", "Investment advisory", "Copy",
                "Team session (30 Sep 2026)", "Spinach"}
LITERAL_REFS = {"X00", "N01", "N02", "N03", "N04", "Events", "Part D", "Part E", "Wireframes v0.2", "D spine",
                "M01"} | {"L%02d" % i for i in range(10)}
NO_DATE = "no date"

# frontend file: supplementary sheet name (stripped) to id letter; the Integrations sheet numbers by order
MAIN_SHEET = "Frontend Technical"
FE_SHEETS = {"React Native Foundation & Archi": "F", "Navigation & Routing": "N", "Conectivity": "C",
             "Performance & Optimization": "P", "Security & Authentication": "S", "Native Device Features": "D",
             "CI_CD & Release Management": "R", "Analytics & Monitoring": "M", "Integrations (App-Specific)": "X",
             "Open Decisions from Wireframes": "O"}
BY_ORDER = {"X"}
SR_NO = "Sr No"
AREA_HEADERS = {"Area", "Decision"}
QUESTION_HEADERS = {"Technical Question", "Wireframe Note", "Question"}
PROPOSAL_HEADERS = {"Best Practise Proposal", "Best Practice Proposal", "Best Practices", "Best Practise",
                    "Best Practice", "Best practice"}
LINK_HEADERS = {"Link", "Official Doc Link", "Doc Link"}
COMMENT_HEADERS = {"Yesly Comments", "Yesly Comment", "Comments"}
# backend file
BE_HEADER = ["Question", "Comments"]
# journey file
SUMMARY_SHEET = "Journey Summary"
SUMMARY_HEADER = "Journey"
SUMMARY_JOURNEYS = ["Login", "Reveal", "Paywall", "Onboarding", "Account Aggregator"]
KEY_OPEN_AREA = "Key open area"
JD_SHEETS = {"Login": "LOGIN", "Reveal": "REVEAL", "Paywall": "PAY", "Onboarding": "ONB", "Account Aggreviator": "AA"}
W_HEADERS = {"Screen / Step", "Screen/Step"}
E_HEADER = "Edge Case"
API_HEADER = "API ID"
W_END = "Detailed Edge Cases & Unhappy Paths"
BLOCK_END = {"Current screen count", "Screen sequence", "Screen Sequence & Optimisation", "API Requirement Summary"}
M_LABEL = "Recommendation"
H_FIRST, H_LAST = "Entry criteria", "Source status"
H_SHEET = "ONB"
# the answer set's tables, told apart by their header cells
ANSWER_HEADER = ["id", "status", "Yesly comment", "refs", "owner, due"]
JOURNEY_HEADER = ["id", "row", "status", "Yesly comment", "refs", "owner, due"]
PART_D_HEADER = ["template", "screens", "Android back", "loading", "keyboard", "validation"]
PART_E_HEADER = ["group", "screens", "who", "rule"]
PART_F_NEW_HEADER = ["W", "item", "owner (tracker)", "function (tab)", "due", "source"]
PART_F_CHANGE_HEADER = ["W", "change"]
TABS_ROW_TEMPLATES = ("T-table", "T-msg")


def load(name):
    with open(os.path.join(ROOT, "data", name)) as fh:
        return json.load(fh)


# ---------------------------------------------------------------- the workbook

def workbook_sheets(path):
    """(sheet name, sheet number) in workbook order."""
    with zipfile.ZipFile(path) as z:
        wb = ET.fromstring(z.read("xl/workbook.xml"))
        rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    targets = {r.get("Id"): r.get("Target") for r in rels}
    out = []
    for s in wb.iter("{%s}sheet" % NS["m"]):
        rid = s.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
        base = os.path.basename(targets[rid])  # sheetN.xml
        out.append((s.get("name"), int(base[len("sheet"):-len(".xml")])))
    return out


def cell(row, i):
    return row[i] if 0 <= i < len(row) else ""


def find_col(header, names):
    for i, h in enumerate(header):
        if h.strip() in names:
            return i
    return -1


def words(text):
    """Lower-case words; every character that is not a letter or a digit separates words."""
    out, cur = [], []
    for ch in text.lower():
        if ch.isalnum():
            cur.append(ch)
        elif cur:
            out.append("".join(cur))
            cur = []
    if cur:
        out.append("".join(cur))
    return out


def opens_with(sheet_text, quote):
    """True when the sheet text begins with the quote's first three words (fewer when the quote is shorter)."""
    q = words(quote)
    n = min(3, len(q))
    return n > 0 and words(sheet_text)[:n] == q[:n]


# ---------------------------------------------------------------- the answer set

def parse_tables(text):
    """Every pipe table in the markdown: {heading, header, rows}."""
    tables, heading, current = [], "", None
    for line in text.split("\n"):
        if line.startswith("#"):
            heading = line.lstrip("#").strip()
            current = None
            continue
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if current is None:
                current = {"heading": heading, "header": cells, "rows": []}
                tables.append(current)
            elif all(set(c) <= set("-: ") for c in cells):
                continue
            else:
                current["rows"].append(cells)
        else:
            current = None
    return tables


def parse_owner_due(text, problems, rid):
    """'Tech and Compliance, 30 Sep 2026' -> owner label(s), iso date, due_about."""
    if not text:
        return "", "", False
    if ", " not in text:
        problems.append("%s: owner and due %r is not 'owner, date'" % (rid, text))
        return text, "", False
    owner, due_text = text.rsplit(", ", 1)
    for part in owner.split(" and "):
        if part not in OWNER_LABELS:
            problems.append("%s: owner %r is not a function label" % (rid, part))
    if due_text == NO_DATE:
        return owner, "", True
    try:
        due = datetime.datetime.strptime(due_text, "%d %b %Y").date().isoformat()
    except ValueError:
        problems.append("%s: due %r is not a date" % (rid, due_text))
        return owner, "", True
    return owner, due, True  # every date in SQ1 is a proposal (the answer set's header)


def marker_item(answer, status):
    """The 'to be decided: <item>' or 'to be verified: <item>' sentence that opens an open or owed answer."""
    marker = MARKERS[status]
    if not answer.startswith(marker):
        return ""
    rest = answer[len(marker):].strip()
    end = rest.find(". ")
    item = rest if end < 0 else rest[:end]
    return item.rstrip(".")


def parse_answer_set(path):
    """The answer set as records: answers (id -> record, in file order), templates, route_groups, tracker_new,
    tracker_changes, problems."""
    with open(path) as fh:
        text = fh.read()
    tables = parse_tables(text)
    answers, order, problems = {}, [], []
    templates, route_groups, tracker_new, tracker_changes = [], [], [], []
    for t in tables:
        h = t["header"]
        if h in (ANSWER_HEADER, JOURNEY_HEADER):
            has_row = h == JOURNEY_HEADER
            for cells in t["rows"]:
                if len(cells) != len(h):
                    problems.append("answer table under %r: row %r has %d cells, not %d" % (t["heading"], cells[0], len(cells), len(h)))
                    continue
                if has_row:
                    rid, row, status, answer, refs, od = cells
                else:
                    rid, status, answer, refs, od = cells
                    row = ""
                if rid in answers:
                    problems.append("%s: listed twice in the answer set" % rid)
                if status not in STATUSES:
                    problems.append("%s: status %r is not one of frozen, open, owed" % (rid, status))
                owner, due, due_about = parse_owner_due(od, problems, rid)
                if status == "frozen" and (owner or due):
                    problems.append("%s: a frozen row carries an owner or a date" % rid)
                if status != "frozen" and not owner:
                    problems.append("%s: an %s row has no owner" % (rid, status))
                if status == "frozen":
                    cause = [CAUSE_ACCEPTED if answer.startswith(ACCEPTED_OPENING) else CAUSE_VATSAL]
                else:
                    cause = []
                answers[rid] = {"id": rid, "row": row, "status": status, "answer": answer,
                                "refs": [r.strip() for r in refs.split(",") if r.strip()],
                                "owner": owner, "due": due, "due_about": due_about, "cause": cause,
                                "item": marker_item(answer, status) if status != "frozen" else ""}
                order.append(rid)
        elif h == PART_D_HEADER:
            for cells in t["rows"]:
                templates.append(dict(zip(["template", "screens", "back", "loading", "keyboard", "validation"], cells)))
        elif h == PART_E_HEADER:
            for cells in t["rows"]:
                route_groups.append(dict(zip(["group", "screens", "who", "rule"], cells)))
        elif h == PART_F_NEW_HEADER:
            for cells in t["rows"]:
                tracker_new.append(dict(zip(["id", "item", "owner", "function", "due", "source"], cells)))
        elif h == PART_F_CHANGE_HEADER:
            for cells in t["rows"]:
                tracker_changes.append(dict(zip(["id", "change"], cells)))
    return {"answers": answers, "order": order, "templates": templates, "route_groups": route_groups,
            "tracker_new": tracker_new, "tracker_changes": tracker_changes, "problems": problems}


# ---------------------------------------------------------------- the sheets

def sheet_row(sheet, order, block, row_no, header_row, comment_col, **kw):
    rec = {"sheet": sheet, "sheet_order": order, "block": block, "row_no": row_no, "header_row": header_row,
           "comment_col": comment_col, "area": "", "question": "", "proposal": "", "link": "", "sheet_text": ""}
    rec.update(kw)
    return rec


def parse_fe_sheet(rows, name, order, letter, problems):
    """The main frontend sheet (letter '') or a supplementary one: one row per Sr No."""
    hr = next((i for i, r in enumerate(rows, 1) if cell(r, 0) == SR_NO), 0)
    if not hr:
        problems.append("sheet %r: no 'Sr No' header row" % name)
        return []
    header = rows[hr - 1]
    c_area, c_q = find_col(header, AREA_HEADERS), find_col(header, QUESTION_HEADERS)
    c_p, c_l, c_c = find_col(header, PROPOSAL_HEADERS), find_col(header, LINK_HEADERS), find_col(header, COMMENT_HEADERS)
    if c_q < 0 or c_p < 0 or c_c < 0:
        problems.append("sheet %r: header %r lacks a question, proposal or comments column" % (name, header))
        return []
    out, n = [], 0
    for i in range(hr + 1, len(rows) + 1):
        r = rows[i - 1]
        sr = cell(r, 0)
        if not sr:
            continue
        n += 1
        if letter == "":
            rid = sr
        elif letter in BY_ORDER:
            rid = "FE-%s%d" % (letter, n)
        else:
            rid = "FE-%s%s" % (letter, sr)
        out.append(sheet_row(name, order, "main", i, hr, c_c, id=rid, sr_no=sr, area=cell(r, c_area) if c_area >= 0 else "",
                             question=cell(r, c_q), proposal=cell(r, c_p), link=cell(r, c_l) if c_l >= 0 else ""))
    return out


def parse_be_sheet(rows, name, order, problems):
    if not rows or [c for c in rows[0] if c] != BE_HEADER:
        problems.append("sheet %r: the header row is not %r" % (name, BE_HEADER))
        return []
    out = []
    for i in range(2, len(rows) + 1):
        q = cell(rows[i - 1], 0)
        if q:
            out.append(sheet_row(name, order, "main", i, 1, 1, id="BE-%02d" % (len(out) + 1), question=q))
    return out


def parse_summary_sheet(rows, name, order, problems):
    hr = next((i for i, r in enumerate(rows, 1) if cell(r, 0) == SUMMARY_HEADER), 0)
    if not hr:
        problems.append("sheet %r: no 'Journey' header row" % name)
        return []
    header = rows[hr - 1]
    c_key = find_col(header, {KEY_OPEN_AREA})
    out = []
    for i in range(hr + 1, len(rows) + 1):
        r = rows[i - 1]
        if cell(r, 0) in SUMMARY_JOURNEYS:
            n = len(out) + 1
            if cell(r, 0) != SUMMARY_JOURNEYS[n - 1]:
                problems.append("sheet %r row %d: journey %r out of order (expected %r)" % (name, i, cell(r, 0), SUMMARY_JOURNEYS[n - 1]))
            out.append(sheet_row(name, order, "main", i, hr, -1, id="JD-SUM-%d" % n, area=cell(r, 0),
                                 question=cell(r, c_key), sheet_text=" ".join(c for c in r if c)))
    return out


def block_rows(rows, start, stop_at, stop_on_empty):
    """Row numbers from start on, until a row whose first cell is empty (when asked) or a block label."""
    out = []
    for i in range(start, len(rows) + 1):
        first = cell(rows[i - 1], 0)
        if (stop_on_empty and not first) or first in stop_at:
            break
        out.append(i)
    return out


def labelled(header, r, skip):
    """The row's cells as 'Header: cell' lines, the proposal and comment cells left out."""
    lines = []
    for i, c in enumerate(r):
        h = cell(header, i).strip()
        if c and i not in skip:
            lines.append("%s: %s" % (h, c) if h else c)
    return "\n".join(lines)


def parse_journey_sheet(rows, name, order, code, problems):
    out = []
    w_hr = next((i for i, r in enumerate(rows, 1) if cell(r, 0) in W_HEADERS), 0)
    e_hr = next((i for i, r in enumerate(rows, 1) if cell(r, 0) == E_HEADER), 0)
    api_hr = next((i for i, r in enumerate(rows, 1) if cell(r, 0) == API_HEADER), 0)
    if not w_hr or not e_hr:
        problems.append("sheet %r: no %r or %r header row" % (name, W_HEADERS, E_HEADER))
        return []
    w_header = rows[w_hr - 1]
    sheet_comment_col = find_col(w_header, COMMENT_HEADERS)
    if code == H_SHEET:
        first = next((i for i, r in enumerate(rows, 1) if cell(r, 0) == H_FIRST), 0)
        last = next((i for i, r in enumerate(rows, 1) if cell(r, 0) == H_LAST), 0)
        if first and last and last > first:
            text = "\n".join("%s: %s" % (cell(rows[i - 1], 0), cell(rows[i - 1], 1)) for i in range(first, last + 1))
            out.append(sheet_row(name, order, "H", first, first, sheet_comment_col, id="JD-%s-H1" % code,
                                 question=text, sheet_text=cell(rows[first - 1], 0) + " " + cell(rows[first - 1], 1)))
        else:
            problems.append("sheet %r: no header block from %r to %r" % (name, H_FIRST, H_LAST))
    for block, hr, stop_at, stop_on_empty in (("W", w_hr, {W_END}, True), ("E", e_hr, BLOCK_END, True), ("API", api_hr, BLOCK_END, True)):
        if not hr:
            continue
        header = rows[hr - 1]
        c_p, c_c = find_col(header, PROPOSAL_HEADERS), find_col(header, COMMENT_HEADERS)
        for n, i in enumerate(block_rows(rows, hr + 1, stop_at, stop_on_empty), 1):
            r = rows[i - 1]
            out.append(sheet_row(name, order, block, i, hr, c_c if c_c >= 0 else sheet_comment_col,
                                 id="JD-%s-%s%d" % (code, block, n), question=labelled(header, r, {c_p, c_c}),
                                 proposal=cell(r, c_p) if c_p >= 0 else "", sheet_text=" ".join(c for c in r if c)))
    m_rows = [i for i, r in enumerate(rows, 1) if cell(r, 0) == M_LABEL]
    for n, i in enumerate(m_rows, 1):
        r = rows[i - 1]
        out.append(sheet_row(name, order, "M", i, w_hr, sheet_comment_col, id="JD-%s-M%d" % (code, n),
                             question="%s: %s" % (M_LABEL, cell(r, 1)), sheet_text=cell(r, 1)))
    out.sort(key=lambda rec: rec["row_no"])
    return out


def read_file(path, family, problems):
    """Every question row of a workbook, in sheet order, plus the sheet list."""
    rows_out, sheets = [], []
    for order, (name, n) in enumerate(workbook_sheets(path), 1):
        rows = read_sheet(path, n)
        stripped = name.strip()
        if family == "FE":
            if stripped == MAIN_SHEET:
                got = parse_fe_sheet(rows, name, order, "", problems)
            elif stripped in FE_SHEETS:
                got = parse_fe_sheet(rows, name, order, FE_SHEETS[stripped], problems)
            else:
                problems.append("sheet %r of the frontend file is not in the id scheme" % name)
                got = []
        elif family == "BE":
            got = parse_be_sheet(rows, name, order, problems)
        else:
            if stripped == SUMMARY_SHEET:
                got = parse_summary_sheet(rows, name, order, problems)
            elif stripped in JD_SHEETS:
                got = parse_journey_sheet(rows, name, order, JD_SHEETS[stripped], problems)
            else:
                problems.append("sheet %r of the journey file is not in the id scheme" % name)
                got = []
        for rec in got:
            rec["file"] = os.path.basename(path)
        rows_out.extend(got)
        sheets.append({"name": name, "order": order, "rows": len(got)})
    return rows_out, sheets


# ---------------------------------------------------------------- refs and Part D

def parse_screen_id(s):
    """('D', '12', 'a') for D12a; None when the text is not shaped like a screen id."""
    i = 0
    while i < len(s) and s[i].isalpha():
        i += 1
    j = i
    while j < len(s) and s[j].isdigit():
        j += 1
    if i == 0 or j == i:
        return None
    suffix = s[j:]
    if suffix and not (suffix.isalpha() and suffix.islower()):
        return None
    return s[:i], s[i:j], suffix


def expand_range(a, b):
    """'R01 to R07' or 'D12a to D12h' as the ids in between, by the id grammar; None when not a range."""
    pa, pb = parse_screen_id(a), parse_screen_id(b)
    if pa is None or pb is None or pa[0] != pb[0]:
        return None
    if pa[2] and pb[2] and pa[1] == pb[1]:
        return [pa[0] + pa[1] + chr(c) for c in range(ord(pa[2]), ord(pb[2]) + 1)]
    if not pa[2] and not pb[2]:
        return ["%s%0*d" % (pa[0], len(pa[1]), n) for n in range(int(pa[1]), int(pb[1]) + 1)]
    return None


def expand_screens(text, live, notes, where):
    """The screen ids named by a Part D cell: single ids and 'X to Y' ranges, split on commas and 'and'."""
    ids, bad = [], []
    parts = []
    for chunk in text.split(","):
        parts.extend(p.strip() for p in chunk.split(" and ") if p.strip())
    for p in parts:
        if " to " in p:
            a, b = [x.strip() for x in p.split(" to ", 1)]
            got = expand_range(a, b)
            if got is None:
                bad.append(p)
                continue
            skipped = [x for x in got if x not in live]
            if skipped:
                notes.append("%s: %r spans %s, not live, left out" % (where, p, ", ".join(skipped)))
            ids.extend(x for x in got if x in live)
        else:
            ids.append(p)
    return ids, bad


def check_refs(rows, live, states, integrations, trackers, pending_w, ids):
    problems, pending = [], []
    for rec in rows:
        for ref in rec["refs"]:
            if ref in live or ref in states or ref in integrations or ref in trackers or ref in ids or ref in LITERAL_REFS:
                continue
            if ref in pending_w:
                pending.append("%s -> %s" % (rec["id"], ref))
                continue
            problems.append("%s: ref %r does not resolve" % (rec["id"], ref))
    return problems, pending


def check_part_d(templates, live, screens, notes):
    problems, seen = [], {}
    for t in templates:
        if t["template"].startswith(TABS_ROW_TEMPLATES[0]):
            continue
        ids, bad = expand_screens(t["screens"], live, notes, "Part D %s" % t["template"])
        for p in bad:
            problems.append("Part D %s: %r is not a screen id or a range" % (t["template"], p))
        t["screen_ids"] = ids
        for sid in ids:
            if sid not in live:
                problems.append("Part D %s: %s is not a live screen" % (t["template"], sid))
                continue
            if sid in seen:
                problems.append("Part D: %s is under %s and %s" % (sid, seen[sid], t["template"]))
            seen[sid] = t["template"]
            board = screens[sid]
            if board not in t["template"].split(", "):
                notes.append("Part D %s lists %s, whose board template is %s" % (t["template"], sid, board))
    for t in templates:
        if t["template"].startswith(TABS_ROW_TEMPLATES[0]):
            t["screen_ids"] = [sid for sid in screens if screens[sid] in TABS_ROW_TEMPLATES]  # board order
    missing = [sid for sid in screens if sid not in seen and screens[sid] not in TABS_ROW_TEMPLATES]
    return problems, missing


# ---------------------------------------------------------------- main

def build():
    """The questions.json object plus the findings; nothing is written here."""
    problems, notes = [], []
    aset = parse_answer_set(os.path.join(INPUT_DIR, ANSWERS))
    problems.extend(aset["problems"])
    answers = aset["answers"]
    sheet_rows, files = [], []
    for name, export, family in FILES:
        path = os.path.join(INPUT_DIR, name)
        if not os.path.exists(path):
            problems.append("missing input file: %s" % path)
            continue
        got, sheets = read_file(path, family, problems)
        sheet_rows.extend(got)
        files.append({"name": name, "export": export, "family": family, "sheets": sheets})
    # every sheet row lands on exactly one id and every id on exactly one sheet row
    sheet_ids = [r["id"] for r in sheet_rows]
    dup = sorted({i for i in sheet_ids if sheet_ids.count(i) > 1})
    for i in dup:
        problems.append("%s: two sheet rows land on it" % i)
    for r in sheet_rows:
        if r["id"] not in answers:
            problems.append("%s (%s, %r, row %d): no answer in the answer set" % (r["id"], r["file"], r["sheet"], r["row_no"]))
    have = set(sheet_ids)
    for rid in aset["order"]:
        if rid not in have:
            problems.append("%s: in the answer set but no sheet row lands on it" % rid)
    # the journey quotes against their sheet rows (rows match by order; a differing quote is reported, not fatal)
    for r in sheet_rows:
        a = answers.get(r["id"])
        if a and a["row"] and not opens_with(r["sheet_text"], a["row"]):
            notes.append("quote differs %s: sheet %r row %d begins %r; the answer set quotes %r" % (
                r["id"], r["sheet"], r["row_no"], " ".join(words(r["sheet_text"])[:6]), a["row"]))
    # board data for the refs
    screens = {s["id"]: s["template"] for s in load("screens_v02.json")["screens"] if s["v02"]["status"] not in ("dropped", "split")}
    live = set(screens)
    states = {s["id"] for s in load("v02/states.json")["states"]}
    integrations = {r["id"] for r in load("integrations.json")["rows"]}
    trackers = {r["id"] for r in load("tracker.json")["rows"]}
    pending_w = {t["id"] for t in aset["tracker_new"]} - trackers
    rows = []
    for r in sheet_rows:
        a = answers.get(r["id"])
        if a is None:
            continue
        rec = {"id": r["id"], "batch": BATCH["id"], "file": r["file"], "sheet": r["sheet"], "sheet_order": r["sheet_order"],
               "block": r["block"], "row_no": r["row_no"], "header_row": r["header_row"], "comment_col": r["comment_col"],
               "row": a["row"], "area": r["area"], "question": r["question"], "proposal": r["proposal"], "link": r["link"],
               "answer": a["answer"], "status": a["status"], "item": a["item"], "refs": a["refs"], "owner": a["owner"],
               "due": a["due"], "due_about": a["due_about"], "cause": a["cause"],
               "tracker": [x for x in a["refs"] if x in trackers or x in pending_w],
               "changed": CHANGED, "exported": ""}
        if a["status"] != "frozen" and not a["item"]:
            notes.append("%s: an %s row whose answer does not open with %r" % (r["id"], a["status"], MARKERS[a["status"]]))
        rows.append(rec)
    ref_problems, pending = check_refs(rows, live, states, integrations, trackers, pending_w, set(answers))
    problems.extend(ref_problems)
    templates = [dict(t) for t in aset["templates"]]
    d_problems, missing = check_part_d(templates, live, screens, notes)
    problems.extend(d_problems)
    data = {"source": "scripts/import_sq.py over inputs/spinach/2026-09-22/ (the three questionnaire files and SQ1_answers.md); phase 14, pass 1",
            "note": "One row per question Spinach asked; the answer is the Yesly comment, verbatim from the answer set. Fields: id, batch, "
                    "file and sheet (original names), sheet_order, block (main, W, E, API, M, H), row_no and header_row (1-based rows in "
                    "the sheet), comment_col (0-based Yesly Comments column of the row's block, -1 when the sheet has none), row (the "
                    "answer set's quote of the sheet row, journey rows), area, question, proposal and link (their text), answer, status "
                    "(frozen, open, owed), item (the to be decided or to be verified item of an open or owed row), refs, owner and due "
                    "(open and owed rows; due_about true while the date is a proposal), cause (frozen rows), tracker (the W ids among "
                    "the refs), changed, exported. templates is Part D of the answer set, route_groups Part E. Statuses change only by "
                    "a commit (approvals are board rows; scripts/apply_sq_approvals.py, pass 5).",
            "batches": [dict(BATCH, files=files, exported="")],
            "rows": rows, "templates": templates, "route_groups": aset["route_groups"]}
    return data, problems, notes, pending, missing, files


def counts(rows):
    out = {"frozen": 0, "open": 0, "owed": 0}
    for r in rows:
        out[r["status"]] += 1
    return out


def report(data, problems, notes, pending, missing, files):
    rows = data["rows"]
    print("%d rows matched across %d files" % (len(rows), len(files)))
    for f in files:
        frows = [r for r in rows if r["file"] == f["name"]]
        c = counts(frows)
        print("  %s: %d rows; frozen %d, open %d, owed %d" % (f["name"], len(frows), c["frozen"], c["open"], c["owed"]))
        for s in f["sheets"]:
            srows = [r for r in frows if r["sheet"] == s["name"]]
            c = counts(srows)
            ids = [r["id"] for r in srows]
            span = ("%s to %s" % (ids[0], ids[-1])) if ids else "-"
            print("    %d. %-34r %3d rows (%s); frozen %d, open %d, owed %d" % (s["order"], s["name"], len(srows), span, c["frozen"], c["open"], c["owed"]))
    c = counts(rows)
    print("  total: frozen %d, open %d, owed %d" % (c["frozen"], c["open"], c["owed"]))
    for r in rows:
        if r["status"] != "frozen":
            print("  %-14s %-5s %-28s %-11s %s" % (r["id"], r["status"], r["owner"], r["due"] or NO_DATE, r["item"][:90]))
    print("Part D: %d template rows; live screens not in Part D: %s" % (len(data["templates"]), ", ".join(missing) or "none"))
    for n in notes:
        print("NOTE: " + n)
    for p in pending:
        print("PENDING (Part F, pass 2): " + p)
    for p in problems:
        print("PROBLEM: " + p)


def main(argv):
    write = "--write" in argv
    data, problems, notes, pending, missing, files = build()
    report(data, problems, notes, pending, missing, files)
    if problems:
        print("%d problems; nothing written" % len(problems))
        return 1
    if not write:
        print("dry run clean; add --write to write data/questions.json")
        return 0
    with open(OUT, "w") as fh:
        fh.write(json.dumps(data, indent=1, ensure_ascii=True) + "\n")
    print("wrote %s (%d rows)" % (os.path.relpath(OUT, ROOT), len(data["rows"])))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
