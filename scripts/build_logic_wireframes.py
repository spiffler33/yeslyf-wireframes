#!/usr/bin/env python3
"""Generate the Logic tab: docs/logic_wireframes.html, the logic panel side wireframes (PLAN_logic_panel_v03.md
section 5), drawn from data/logic_screens.json by the shared renderer (scripts/renderer_v02.js and renderer_v02.css)
with the comment box.

A stripped copy of scripts/build_admin_wireframes.py (plan 12.0, phase A0; logic plan, 8 Oct 2026): the board's own
builder cannot draw a second data file. No seed is read, no bundle is written, no screen-specific drawing code is
included. The data keeps sec L and V; the page sets each screen's sec to its group, so the list on the left reads by
what the operator is doing.

The build validates data/logic_screens.json first and writes the page last: any failure is named and stops the
build with docs/logic_wireframes.html untouched. Never hand-edit docs/. Called from scripts/build_site.py
(import build_logic_wireframes; build_logic_wireframes.main()) after build_admin_split.main(); also runs on its own.
"""
import json
import os
import sys

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPTS)
DATA = os.path.join(ROOT, "data")
DOCS = os.path.join(ROOT, "docs")
sys.path.insert(0, SCRIPTS)
import build_site as site  # noqa: E402
import validate_v02  # noqa: E402

# The 39 screens in file order (plan 12.1): 33 panel screens (sec L), then 6 client views (sec V).
IDS = ["L01", "L01a", "L02", "L02a", "L03", "L03a", "L03b", "L14", "L14a", "L04", "L04a", "L04b", "L09", "L07", "L05",
       "L05a", "L05b", "L10", "L10a", "L06", "L06a", "L06b", "L11", "L11a", "L11b", "L08", "L08a", "L15", "L15a", "L15b",
       "L12", "L13", "L00", "V01", "V02", "V03", "V04", "V05", "V06"]
# The ten seats of plan 4.8, in this order everywhere.
SEATS = ["Principal officer", "Logic analyst", "Compliance", "Adviser", "Call centre", "Ops", "Support", "Read only",
         "Marketing", "Finance"]
SEAT_VALUES = {"act", "read", "read, own people", "read masked", "none"}
# The groups of the list on the left (plan 5.2), in this order and with these labels.
GROUPS = [["start", "Start"], ["logic", "Logic"], ["change", "Change"], ["records", "Records"], ["access", "Access"],
          ["reference", "Reference"], ["client", "Client views"]]
KEYS = ("id", "sec", "title", "tier", "frame", "template", "path", "purpose", "ui", "spec", "compliance", "events", "v02",
        "freeze", "role", "writes", "group")


# ---------------------------------------------------------------- data/logic_screens.json validation

def load_logic_screens():
    with open(os.path.join(DATA, "logic_screens.json")) as fh:
        return json.load(fh)


def all_text(obj):
    out = []

    def walk(o):
        if isinstance(o, str):
            out.append(o)
        elif isinstance(o, list):
            for x in o:
                walk(x)
        elif isinstance(o, dict):
            for v in o.values():
                walk(v)

    walk(obj)
    return out


def without_causes(doc):
    """The file with its two cause fields emptied (v02.causes, freeze.cause): they carry "Vatsal, 8 Oct 2026", the
    cause CLAUDE.md asks for, so the team-name check reads everything else (the board's validator never reads causes)."""
    return dict(doc, screens=[dict(s, v02=dict(s.get("v02") or {}, causes=[]), freeze=dict(s.get("freeze") or {}, cause=""))
                              for s in doc.get("screens", [])])


def seats_line(role):
    return "Seats: " + "; ".join("%s %s" % (seat, role.get(seat)) for seat in SEATS)


def writes_line(writes):
    if not writes:
        return "Writes: none"
    return "Writes: " + "; ".join(w["action"] + " (" + w["event"] + "; " + ", ".join(w["seats"]) + ")" for w in writes)


def validate_logic_screens(doc, wireframe_ids, vendor_names, templates, reasons):
    p = []
    screens = doc.get("screens", [])
    ids = [s.get("id") for s in screens]
    if ids != IDS:
        p.append("screen ids are not exactly %s, in that order: got %s" % (", ".join(IDS), ids))
    if doc.get("groups") != GROUPS:
        p.append("groups are not the seven of plan 5.2 in order: got %s" % doc.get("groups"))
    group_codes = [g[0] for g in GROUPS]

    logic_ids = set(ids)
    for s in screens:
        sid = s.get("id", "?")
        for key in KEYS:
            if key not in s:
                p.append("%s: missing %s" % (sid, key))
        panel = str(sid).startswith("L")
        if s.get("sec") != ("L" if panel else "V"):
            p.append("%s: sec %r, not %s" % (sid, s.get("sec"), "L" if panel else "V"))
        if s.get("frame") != ("desktop" if panel else "phone"):
            p.append("%s: frame %r, not %s" % (sid, s.get("frame"), "desktop" if panel else "phone"))
        if s.get("template") not in templates:
            p.append("%s: template %r is not one data/screens_v02.json uses" % (sid, s.get("template")))
        if s.get("path") not in ("both", "aa", "manual"):
            p.append("%s: path %r" % (sid, s.get("path")))
        if s.get("group") not in group_codes:
            p.append("%s: group %r is not one of the seven" % (sid, s.get("group")))
        if not isinstance(s.get("tier"), list):
            p.append("%s: tier is not a list" % sid)
        events = s.get("events") or []
        if not events:
            p.append("%s: no events" % sid)
        c = s.get("compliance") or {}
        if not isinstance(c.get("review"), bool) or not c.get("reasons"):
            p.append("%s: compliance flag incomplete" % sid)
        for r in c.get("reasons") or []:
            if r not in reasons:
                p.append("%s: compliance reason %r is not in data/compliance_reasons.json" % (sid, r))
        f = s.get("freeze") or {}
        if f.get("status") != "open" or not f.get("reason"):
            p.append("%s: freeze is not open with a reason" % sid)
        v = s.get("v02") or {}
        if v.get("status") not in ("changed", "new", "kept"):
            p.append("%s: v02 status %r is not changed, new or kept" % (sid, v.get("status")))
        spec = s.get("spec") or {}
        for key in ("fields", "logic", "branches", "states", "dev"):
            if key not in spec:
                p.append("%s: spec missing %s" % (sid, key))

        role = s.get("role") or {}
        if list(role) != SEATS:
            p.append("%s: role does not name the ten seats in order: got %s" % (sid, list(role)))
        for k, v2 in role.items():
            if v2 not in SEAT_VALUES:
                p.append("%s: role %r value %r is not act, read, 'read, own people', 'read masked' or none" % (sid, k, v2))
        writes = s.get("writes")
        if not isinstance(writes, list):
            p.append("%s: writes is not a list" % sid)
            writes = []
        whole = True
        for w in writes:
            if not w.get("action") or not w.get("event") or not w.get("seats"):
                p.append("%s: writes entry missing action, event or seats: %r" % (sid, w))
                whole = False
                continue
            if w["event"] not in events:
                p.append("%s: writes event %s not listed in events" % (sid, w["event"]))
            for r in w["seats"]:
                if r not in SEATS:
                    p.append("%s: writes seat %r is not one of the ten seats" % (sid, r))
        logic = spec.get("logic") or []
        if logic[:1] != [seats_line(role)]:
            p.append("%s: spec.logic[0] is not %r" % (sid, seats_line(role)))
        if whole and logic[1:2] != [writes_line(writes)]:
            p.append("%s: spec.logic[1] is not %r" % (sid, writes_line(writes)))

        for e in s.get("ui") or []:
            target = e[2] if len(e) > 2 else None
            if e[0] in validate_v02.LINK_TYPES and target not in logic_ids and target not in wireframe_ids:
                p.append("%s: %s %r -> %s is neither a logic screen nor a wireframes screen" % (sid, e[0], e[1], target))
        for label, target in spec.get("branches", []):
            if target not in logic_ids and target not in wireframe_ids:
                p.append("%s: branch %r -> %s is neither a logic screen nor a wireframes screen" % (sid, label, target))

    texts = all_text(doc)
    for txt in all_text(without_causes(doc)):
        for name in validate_v02.NAMES_UI:
            if validate_v02.word_hit(txt, name):
                p.append("data/logic_screens.json: team name %s in text: %r" % (name, txt[:70]))
    for txt in texts:
        for vendor in vendor_names:
            if vendor and vendor in txt:
                p.append("data/logic_screens.json: vendor name %s in text: %r" % (vendor, txt[:70]))
    for txt in texts:
        for ch in txt:
            if ord(ch) > 126:
                p.append("data/logic_screens.json: non-ASCII in %r" % txt[:60])
                break
    return p


# ---------------------------------------------------------------- the page

def build_page(doc, reasons):
    who = '<div class="who">Reviewing as <select id="reviewer"></select></div>'
    bar = ('<div class="bar">' + site.logic_subnav("logic_wireframes.html") + '</div>\n'
           '<div class="banner">side wireframes: proposed, not yet merged into Wireframes v0.2. The design is proposed, '
           'to be confirmed at the logic panel review (to be decided: the review date). Every logic value is a rehearsal '
           'value and every count a typed example.</div>\n')
    layout = site.WIRE_LAYOUT
    wire_opts = {"page": "logic_wireframes", "key": "yeslyf_logic_wire_v01", "version": "logic side v0.1",
                 "exportTitle": "# yeslyf logic panel side wireframes - review comments",
                 "exportFile": "yeslyf_logic_side_review_v01.md"}
    # The page groups the screens by what the operator is doing (plan 12.0); the data keeps sec L and V.
    page_screens = [dict(s, sec=s["group"]) for s in doc["screens"]]
    data = ('<script>var SECTIONS=' + site.js_blob(doc["groups"]) + ';\nvar SCREENS=' + site.js_blob(page_screens) +
            ';\nvar DROPPED=' + site.js_blob([]) + ';\nvar SPLIT=' + site.js_blob([]) + ';\nvar STATES=' + site.js_blob([]) +
            ';\nvar REASONS=' + site.js_blob(reasons) + ';\nvar INTEGRATIONS=' + site.js_blob(site.integrations_blob()) +
            ';\nvar FREEZE=' + site.js_blob(None) + ';\nvar WIRE_OPTS=' + site.js_blob(wire_opts) + ';</script>\n')
    scripts = [site.store_script(), '<script>' + site.read_script("renderer_v02.js") + '</script>\n']
    page = (site.head("yeslyf logic panel side wireframes", site.read_script("renderer_v02.css") + site.SUBNAV_CSS) + '<body>\n' +
            site.header("logic_wireframes.html", "logic panel side wireframes: proposed, not yet merged into Wireframes v0.2",
                        who_html=who, export_label="Export comments") +
            bar + layout + data + "".join(scripts) + '</body>\n</html>\n')
    return page


# ---------------------------------------------------------------- main

def main():
    doc = load_logic_screens()
    v02 = site.load("screens_v02.json")
    wireframe_ids = {s["id"] for s in v02["screens"]}
    templates = {s["template"] for s in v02["screens"]}
    reasons = site.load("compliance_reasons.json")["reasons"]
    integ_rows = site.load("integrations.json")["rows"]
    # Vendor strings to ban from screen text, minus the placeholder-status labels a few rows carry ("internal",
    # "internal (Spinach)", "not decided": I19, I20, I23, I24): those are not vendor names, and "internal" is also the
    # compliance reason category every L screen carries (data/compliance_reasons.json).
    generic_vendor_labels = {"internal", "internal (Spinach)", "not decided"}
    vendor_names = [r["vendor"] for r in integ_rows if r["vendor"] not in generic_vendor_labels]

    problems = validate_logic_screens(doc, wireframe_ids, vendor_names, templates, reasons)
    if problems:
        for x in problems[:60]:
            print("ERROR: " + x)
        if len(problems) > 60:
            print("ERROR: ... %d more" % (len(problems) - 60))
        sys.exit(1)

    page = build_page(doc, reasons)
    site.check_ascii("logic_wireframes.html", page)
    page_problems = []
    if 'name="robots" content="noindex' not in page:
        page_problems.append("logic_wireframes.html lacks noindex")
    for word in site.FORBIDDEN:
        i = page.find(word)
        while i >= 0:
            page_problems.append("logic_wireframes.html contains %r: ...%s..." % (word, page[max(0, i - 50):i + len(word) + 30].replace("\n", " ")))
            i = page.find(word, i + 1)
    if page_problems:
        for x in page_problems:
            print("ERROR: " + x)
        sys.exit(1)

    with open(os.path.join(DOCS, "logic_wireframes.html"), "w") as fh:
        fh.write(page)
    n_panel = sum(1 for s in doc["screens"] if s["sec"] == "L")
    print("logic wireframes: %d screens (%d panel, %d client views), validation PASS" % (
        len(doc["screens"]), n_panel, len(doc["screens"]) - n_panel))


if __name__ == "__main__":
    main()
