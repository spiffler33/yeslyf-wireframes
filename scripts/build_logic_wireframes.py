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
SPEC_KEYS = ("fields", "logic", "branches", "states", "dev")  # plus the optional forward (plan 12.1 step 3)
# The containers the checks read, with their types: a wrong one is named and ends that screen's checks (no traceback).
SHAPES = (("ui", list), ("spec", dict), ("compliance", dict), ("events", list), ("v02", dict), ("freeze", dict),
          ("role", dict))


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
    cause CLAUDE.md asks for, so the team-name check reads everything else (the board's validator never reads causes).
    A v02 or freeze that is not a dict stays as it is: the validator names it."""
    def blank(s):
        v, f = s.get("v02"), s.get("freeze")
        return dict(s, v02=dict(v, causes=[]) if isinstance(v, dict) else v,
                    freeze=dict(f, cause="") if isinstance(f, dict) else f)
    return dict(doc, screens=[blank(s) for s in doc.get("screens", [])])


def seats_line(role):
    return "Seats: " + "; ".join("%s %s" % (seat, role.get(seat)) for seat in SEATS)


def writes_line(writes):
    if not writes:
        return "Writes: none"
    return "Writes: " + "; ".join(w["action"] + " (" + w["event"] + "; " + ", ".join(w["seats"]) + ")" for w in writes)


def strings(x, n=None):
    """A list of strings, of length n when n is given: a branch [label, target], a link row's label and target, seats."""
    return isinstance(x, list) and all(isinstance(y, str) for y in x) and (n is None or len(x) == n)


def board_rules(s, logic_ids, wireframe_ids, live_ids):
    """The board's screen rules on one screen (validate_v02.structural :103-131 and check_self_links; the causes rule
    of build_admin_wireframes.py :415): field tags, the Moving forward block, causes, link and branch targets,
    self-links. A target resolves first to the logic file, then to the board, and never to a dropped or split board
    screen. It reads the shapes validate_logic_screens checks, so it runs only on a screen with no earlier problem."""
    sid, spec, p = s["id"], s["spec"], []
    kinds = [e[0] for e in s["ui"]]
    if ("in" in kinds or "radio" in kinds or ("chips" in kinds and spec.get("fields"))) and not spec.get("forward"):
        p.append("%s: inputs drawn but no Moving forward block (spec.forward)" % sid)
    for f in spec.get("fields") or []:
        if not isinstance(f, dict) or not f.get("f") or f.get("forward") not in validate_v02.TAGS:
            p.append("%s: field %r is not a dict with f and a forward tag (%s)" % (sid, f, ", ".join(validate_v02.TAGS)))
    if not isinstance(s["v02"].get("causes"), list) or not s["v02"]["causes"]:
        p.append("%s: v02.causes is not a non-empty list" % sid)
    links = [(e[0], e[1], e[2]) for e in s["ui"] if e[0] in validate_v02.LINK_TYPES]
    for kind, label, target in links + [("branch", b[0], b[1]) for b in spec.get("branches") or []]:
        if target in logic_ids:
            continue
        if target not in wireframe_ids:
            p.append("%s: %s %r -> %s is neither a logic screen nor a wireframes screen" % (sid, kind, label, target))
        elif target not in live_ids:
            p.append("%s: %s %r -> %s points at a dropped or split board screen" % (sid, kind, label, target))
    return p + validate_v02.check_self_links([s])


def validate_logic_screens(doc, wireframe_ids, vendor_names, templates, reasons, live_ids):
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
        start = len(p)
        for key in KEYS:
            if key not in s:
                p.append("%s: missing %s" % (sid, key))
        for key in sorted(set(s) - set(KEYS)):
            p.append("%s: unknown key %s" % (sid, key))
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
        spec = s.get("spec") if isinstance(s.get("spec"), dict) else {}
        bad = [(k, t) for k, t in SHAPES if k in s and not isinstance(s[k], t)]
        bad += [("spec." + k, list) for k in SPEC_KEYS if k in spec and not isinstance(spec[k], list)]
        for k, t in bad:
            p.append("%s: %s is not a %s" % (sid, k, t.__name__))
        if bad:
            continue
        # Lists the renderer maps over (renderer_v02.js :206, :262, :326): a string there breaks the whole tab.
        for box, key, optional in (("spec", "forward", True), ("freeze", "owed", False), ("compliance", "checks", False)):
            o = s.get(box) or {}
            if not (optional and key not in o) and not strings(o.get(key)):
                p.append("%s: %s.%s is not a list of strings" % (sid, box, key))
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
        if f.get("status") != "open" or not isinstance(f.get("reason"), list) or not f["reason"]:
            p.append("%s: freeze is not open with a non-empty reason list" % sid)
        v = s.get("v02") or {}
        if v.get("status") not in ("changed", "new", "kept"):
            p.append("%s: v02 status %r is not changed, new or kept" % (sid, v.get("status")))
        for key in SPEC_KEYS:
            if key not in spec:
                p.append("%s: spec missing %s" % (sid, key))
        for key in sorted(set(spec) - set(SPEC_KEYS) - {"forward"}):
            p.append("%s: spec has unknown key %s" % (sid, key))

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
            shaped = isinstance(w, dict) and all(isinstance(w.get(k), str) and w[k] for k in ("action", "event"))
            if not shaped or not strings(w.get("seats")) or not w["seats"]:
                p.append("%s: writes entry is not a dict with action, event and seats: %r" % (sid, w))
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
            row = isinstance(e, list) and e and isinstance(e[0], str)
            if not row or (e[0] in validate_v02.LINK_TYPES and not strings(e[1:3], 2)):
                p.append("%s: ui row %r is empty, does not start with a string, or is a link without a label and a target" % (sid, e))
        for br in spec.get("branches") or []:
            if not strings(br, 2):
                p.append("%s: branch %r is not a two-item list [label, target]" % (sid, br))
        if len(p) == start:
            p += board_rules(s, logic_ids, wireframe_ids, live_ids)

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
                 "exportFile": "yeslyf_logic_side_review_v01.md",
                 # No Spinach (logic plan, 8 Oct 2026): the Tracker lists every comment under the identity Spinach on
                 # any page on docs/review/tracker.html (build_tracker.py questions()), the link Spinach has; section 0
                 # and 12.0 keep the logic work off that link until the merge.
                 "identities": ["Bhuvanaa", "Harish", "Gaurav", "Kajal", "Somil", "Raafiya", "Vatsal", "Compliance"]}
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
    live_ids = {s["id"] for s in validate_v02.live(v02["screens"])}  # the board screens not dropped or split
    templates = {s["template"] for s in v02["screens"]}
    reasons = site.load("compliance_reasons.json")["reasons"]
    integ_rows = site.load("integrations.json")["rows"]
    # Vendor strings to ban from screen text, minus the placeholder-status labels a few rows carry ("internal",
    # "internal (Spinach)", "not decided": I19, I20, I23, I24): those are not vendor names, and "internal" is also the
    # compliance reason category every L screen carries (data/compliance_reasons.json).
    generic_vendor_labels = {"internal", "internal (Spinach)", "not decided"}
    vendor_names = [r["vendor"] for r in integ_rows if r["vendor"] not in generic_vendor_labels]

    problems = validate_logic_screens(doc, wireframe_ids, vendor_names, templates, reasons, live_ids)
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
