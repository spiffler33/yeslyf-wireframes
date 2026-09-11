#!/usr/bin/env python3
"""Validate data/screens_v02.json against plan_v2.md section 7 checks 1 to 7 (the data-level checks).

structural(screens): the checks apply_decisions.py enforces on every build (ids, keys, templates, paths,
compliance flags, events, branch targets, dropped targets, ASCII).
full(screens, data): everything, including the checks that need the phase 4 and 5 data (paths and gate fields,
states and mocks, self-links, orphans, forbidden words, P01 shape). Run `python3 scripts/validate_v02.py` for
the full suite; it prints one line per check and exits 1 if any fails.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

TEMPLATES = {"T-tap", "T-num", "T-split", "T-list", "T-detail", "T-card", "T-card-stack", "T-hub", "T-review",
             "T-chart", "T-source", "T-upload", "T-progress", "T-webview", "T-sheet", "T-video", "T-paywall",
             "T-locked", "T-picker", "T-msg", "T-table"}
PATHS = {"aa", "manual", "both"}
LINK_TYPES = ("btn", "btn2", "link")
# Fixed strings that must not appear on any live v0.2 screen (section 7 check 6 and section 0).
FORBIDDEN = ["founders", "Founders", "recommendation", "Recommendation", "Priya", "Yeslyf", "45-minute", "30-minute",
             "15-minute", "45 minute", "30 minute", "15 minute", "minute call", "one call", "One call", "two calls",
             "three calls", "four calls", "1 call", "2 calls", "3 calls", "4 calls", "60-day", "60 day", "S26"]
# First names that must not appear in drawn ui text (callouts name the item, never a person).
NAMES_UI = ["Bhuvanaa", "Harish", "Gaurav", "Kajal", "Somil", "Vatsal", "spiff", "Priya"]
# Appendix B gate fields, by spine section.
GATE_FIELDS = ["members", "has_dependants", "rpq_answers", "risk_band", "take_home", "total_outgoings",
               "bank_and_deposits", "mutual_funds", "stocks", "epf", "has_loans", "total_emi", "term_status",
               "health_status", "goals", "work_optional_age"]
STATES = ["S1", "S2", "S2b", "S3", "S4", "S5", "S6", "S7", "S8", "S9", "S10", "S11", "S12", "S13", "S14", "S15",
          "S16", "S17", "S18", "S19", "S20", "S21", "S22", "S23", "S24", "S25"]


def live(screens):
    return [s for s in screens if s["v02"]["status"] not in ("dropped", "split")]


def links(s):
    out = []
    for row in s["ui"]:
        if row[0] in LINK_TYPES:
            out.append((row[1], row[2]))
    for br in s["spec"].get("branches", []):
        out.append((br[0], br[1]))
    return out


def texts(s, ui_only=False):
    """Every string drawn on the screen (ui), or everything the page shows for it (ui plus spec and purpose)."""
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

    walk(s["ui"])
    if not ui_only:
        walk(s["title"])
        walk(s["purpose"])
        walk({k: v for k, v in s["spec"].items()})
        walk(s.get("compliance", {}))
    return out


def structural(screens):
    p = []
    ids = [s["id"] for s in screens]
    if len(ids) != len(set(ids)):
        p.append("duplicate ids: %s" % ", ".join(sorted({i for i in ids if ids.count(i) > 1})))
    byid = {s["id"]: s for s in screens}
    for s in screens:
        sid = s.get("id", "?")
        for key in ("id", "sec", "title", "tier", "frame", "purpose", "ui", "spec", "template", "path", "events", "compliance", "v02"):
            if key not in s:
                p.append("%s: missing %s" % (sid, key))
        if s["v02"]["status"] == "dropped":
            if not s["v02"].get("pointer"):
                p.append("%s: dropped without a pointer" % sid)
            continue
        if s["v02"]["status"] == "split":
            if not s["v02"].get("instances"):
                p.append("%s: split without its instances" % sid)
            for inst in s["v02"].get("instances", []):
                t = byid.get(inst)
                if t is None or t["v02"]["status"] in ("dropped", "split"):
                    p.append("%s: split instance %s is not a live screen" % (sid, inst))
            continue
        for key in ("fields", "logic", "branches", "states", "dev"):
            if key not in s["spec"]:
                p.append("%s: spec lacks %s" % (sid, key))
        if s.get("template") not in TEMPLATES:
            p.append("%s: template %r not in appendix F" % (sid, s.get("template")))
        if s.get("path") not in PATHS:
            p.append("%s: path %r" % (sid, s.get("path")))
        if not s.get("events"):
            p.append("%s: no events" % sid)
        c = s.get("compliance") or {}
        if not isinstance(c.get("review"), bool) or not c.get("reasons"):
            p.append("%s: compliance flag incomplete" % sid)
        if not s["v02"].get("causes") and s["v02"]["status"] != "kept":
            p.append("%s: %s without a cause" % (sid, s["v02"]["status"]))
        for label, target in links(s):
            t = byid.get(target)
            if t is None:
                p.append("%s: branch %r -> %s does not exist" % (sid, label, target))
            elif t["v02"]["status"] in ("dropped", "split"):
                p.append("%s: branch %r -> %s points at a %s screen" % (sid, label, target, t["v02"]["status"]))
        for txt in texts(s):
            for ch in txt:
                if ord(ch) > 126:
                    p.append("%s: non-ASCII %r" % (sid, txt[:60]))
                    break
    return p


def check_self_links(screens):
    p = []
    for s in live(screens):
        for row in s["ui"]:
            if row[0] in LINK_TYPES and row[2] == s["id"]:
                if not any(row[1] in line for line in s["spec"]["logic"]):
                    p.append("%s: self-link %r has no logic line naming it" % (s["id"], row[1]))
    return p


def check_orphans(screens):
    """Every phone screen is the target of a branch, a section entry, or a state landing."""
    p = []
    inbound = set()
    for s in live(screens):
        for _, t in links(s):
            if t != s["id"]:
                inbound.add(t)
    for s in live(screens):
        if s["frame"] != "phone":
            continue
        if s["id"] in inbound:
            continue
        if s["template"] in ("T-sheet", "T-msg"):
            continue  # sheets sit over a screen; message mocks are pairs, not flow screens
        if s["spec"].get("states"):
            continue  # reached by state routing (section N)
        p.append("%s: no inbound branch" % s["id"])
    return p


def word_hit(txt, w):
    """True when w occurs in txt as a whole token (no letter or digit touching either end)."""
    i = txt.find(w)
    while i >= 0:
        before = txt[i - 1] if i > 0 else " "
        after = txt[i + len(w)] if i + len(w) < len(txt) else " "
        if not before.isalnum() and not after.isalnum():
            return True
        i = txt.find(w, i + 1)
    return False


def check_words(screens):
    p = []
    for s in live(screens):
        for txt in texts(s):
            for w in FORBIDDEN:
                if word_hit(txt, w):
                    p.append("%s: contains %r in %r" % (s["id"], w, txt[:70]))
        for txt in texts(s, ui_only=True):
            for n in NAMES_UI:
                if n in txt:
                    p.append("%s: name %s drawn on the screen: %r" % (s["id"], n, txt[:70]))
    return p


def check_p01(screens):
    p = []
    byid = {s["id"]: s for s in screens}
    p01 = byid.get("P01")
    if p01 is None:
        return ["P01 missing"]
    cards = [r for r in p01["ui"] if r[0] == "card"]
    toggles = [r for r in p01["ui"] if r[0] == "tabs" and set(r[1]) == {"Monthly", "Quarterly"}]
    if len(cards) != 2:
        p.append("P01 has %d cards, not two" % len(cards))
    if not toggles:
        p.append("P01 has no monthly / quarterly toggle")
    for r in cards:
        if "one time" in r[1].lower() or "one-time" in r[1].lower():
            p.append("P01 still has a one-time card")
    return p


def reach(screens, path):
    """Screens reachable from A05 along branches, on one path (aa or manual), through live screens."""
    byid = {s["id"]: s for s in live(screens)}
    seen, stack = set(), ["A05"]
    while stack:
        sid = stack.pop()
        if sid in seen or sid not in byid:
            continue
        s = byid[sid]
        if s["path"] not in ("both", path):
            continue
        seen.add(sid)
        for _, t in links(s):
            stack.append(t)
    return seen


def check_paths(screens):
    p = []
    byid = {s["id"]: s for s in live(screens)}
    d_ids = [s["id"] for s in live(screens) if s["sec"] == "D" and s["id"][0] == "D" and s["frame"] == "phone"
             and s["template"] not in ("T-sheet", "T-card") or s["id"] in ("D00",)]
    manual = reach(screens, "manual")
    aa = reach(screens, "aa")
    for must in ("D01", "D10", "G01"):
        for name, got in (("manual", manual), ("aa", aa)):
            if must not in got:
                p.append("%s path does not reach %s" % (name, must))
    gate_seen = set()
    for sid in manual:
        for f in byid[sid]["spec"].get("fields", []):
            if isinstance(f, dict) and f.get("gate"):
                gate_seen.add(f["f"])
    for g in GATE_FIELDS:
        if g not in gate_seen:
            p.append("manual path never reaches gate field %s" % g)
    for sid in d_ids:
        if sid not in aa and byid[sid]["template"] != "T-sheet":
            p.append("aa path does not reach %s" % sid)
    return p


def check_states(screens, states):
    p = []
    byid = {s["id"]: s for s in live(screens)}
    if states is None:
        return ["states file data/v02/states.json missing"]
    by = {st["id"]: st for st in states}
    for sid in STATES:
        st = by.get(sid)
        if st is None:
            p.append("state %s missing" % sid)
            continue
        for key in ("who", "lands_on", "primary_action", "ladder", "exit", "mock"):
            if not st.get(key):
                p.append("state %s lacks %s" % (sid, key))
        if st.get("lands_on") and st["lands_on"] not in byid:
            p.append("state %s lands on %s, which does not exist" % (sid, st["lands_on"]))
        if st.get("mock") and st["mock"] not in byid:
            p.append("state %s mock %s does not exist" % (sid, st["mock"]))
    if "S26" in by:
        p.append("S26 is present")
    return p


def full(screens, states=None):
    results = []
    results.append(("1 branches resolve, no dropped targets, no orphans", structural(screens) + check_orphans(screens)))
    results.append(("2 self-links carry a logic line", check_self_links(screens)))
    results.append(("3 manual path reaches every gate field; aa path reaches every D screen; both reach D01, D10, G01", check_paths(screens)))
    results.append(("4 every state S1 to S25 has a landing, a primary action, a ladder, an exit and a mock", check_states(screens, states)))
    results.append(("5 every screen has a template, a path, an event and a compliance flag", [x for x in structural(screens) if "template" in x or "path" in x or "events" in x or "compliance" in x]))
    results.append(("6 causes shown; no names on callouts, no founders or recommendation, no Priya, no drawn call count or length, no capital Yeslyf", check_words(screens) + ["%s: %s without a cause" % (s["id"], s["v02"]["status"]) for s in screens if s["v02"]["status"] != "kept" and not s["v02"].get("causes")]))
    results.append(("7 P01 two cards and a period toggle; no one-time card; no 60-day line; no S26", check_p01(screens) + [x for x in check_words(screens) if "60" in x or "S26" in x]))
    return results


def main():
    with open(os.path.join(DATA, "screens_v02.json")) as fh:
        screens = json.load(fh)["screens"]
    states = None
    path = os.path.join(DATA, "v02", "states.json")
    if os.path.exists(path):
        with open(path) as fh:
            states = json.load(fh)["states"]
    bad = 0
    for name, problems in full(screens, states):
        print("%s: %s" % ("PASS" if not problems else "FAIL", name))
        for x in problems[:40]:
            print("    " + x)
        if len(problems) > 40:
            print("    ... %d more" % (len(problems) - 40))
        bad += 1 if problems else 0
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
