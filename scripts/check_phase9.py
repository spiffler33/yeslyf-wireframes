#!/usr/bin/env python3
"""Phase 9 acceptance checks (Vatsal, 11 Sep 2026): checks 1 to 10 of plan_v2.md section 7 (validate_v02.py and
check_site.py, run first), then checks 11 to 17 of the phase 9 brief. Prints PASS or FAIL per check; exits 1 on any
failure. Needs Python 3 and Node only.

11. A D02 walk with three types ticked opens exactly those three screens; every unticked type is explicit none. D04 too.
12. No live screen carries "assumed" except D07b; no screen mentions income-tier bands or multipliers; L02 has no
    client-data fallback row; fp_react_inputs.json shows "band required" on every field.
13. Exit from any D screen is a silent autosave; O03 is reachable only from the D12 cards and O02.
14. The aa path walks A05 -> A06 -> D01 with no stop at A07; A08 appears as a state on D02.
15. Q06 and Q06a exist; every Q06 chip maps to existing screens; H01, H07, H09 and Q01 link to Q06.
16. Each audience file opens from disk with no network and renders its screen set; the compliance file holds only
    review-true screens and no dev notes; the Spinach file has no compliance checklist and no CRM backlog; no file
    carries an endpoint URL.
17. The Changelog shows D05, D06 and D08 under split; the dropped count is 3.
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
DOCS = os.path.join(ROOT, "docs")
AUD = os.path.join(DOCS, "audiences")
SCRIPTS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS)
import build_site  # noqa: E402
import check_site  # noqa: E402
import validate_v02  # noqa: E402

TIER_WORDS = ["income tier", "income-tier", "band multiplier", "tier multiplier", "multipliers by", "multipliers for", "by income tier"]
L02_BAD = ["multiplier", "tier", "asset mix", "persona"]
TICKS = {"D02": ["Bank balances and deposits", "Mutual funds", "EPF"], "D04": ["Term life", "Health", "Other (accident, critical illness)"]}


def load(name):
    with open(os.path.join(DATA, name)) as fh:
        return json.load(fh)


def check11(screens, byid, order):
    p, notes = [], []
    for sid, ticks in TICKS.items():
        s = byid.get(sid)
        ms = s["spec"].get("multi_select") if s else None
        if not ms:
            p.append("%s: no multi_select contract in the spec" % sid)
            continue
        opens = [scr for label, scr in ms["options"] if label in ticks]
        if len(opens) != 3:
            p.append("%s: %d screens open for three ticks" % (sid, len(opens)))
        for scr in opens:
            t = byid.get(scr)
            if t is None or t["v02"]["status"] in ("dropped", "split"):
                p.append("%s: %s is not a live screen" % (sid, scr))
        pos = [order.index(x) for x in opens if x in order]
        if pos != sorted(pos):
            p.append("%s: the ticked screens do not open in spine order" % sid)
        unticked = [label for label, scr in ms["options"] if label not in ticks]
        if ms.get("unticked") != "explicit none":
            p.append("%s: unticked types are %r, not explicit none" % (sid, ms.get("unticked")))
        chips = [r[1] for r in s["ui"] if r[0] == "chips"]
        if not any(ms["none"] in c for c in chips):
            p.append("%s: the %s chip is not drawn" % (sid, ms["none"]))
        if not any("unticked" in l and "explicit none" in l for l in s["spec"]["logic"]):
            p.append("%s: no logic line stores unticked types as explicit none" % sid)
        if sid == "D02":
            for scr in [x[1] for x in ms["options"]]:
                if not any("not ticked on D02" in st for st in byid[scr]["spec"]["states"]):
                    p.append("%s: no unticked state on the instance" % scr)
        notes.append("%s ticks %s open %s; %d unticked stored %s" % (sid, ", ".join(ticks), ", ".join(opens), len(unticked), ms.get("unticked")))
    return p, "; ".join(notes)


def check12(screens):
    p = []
    fp = load("fp_react_inputs.json")
    for s in validate_v02.live(screens):
        for t in validate_v02.texts(s):
            low = t.lower()
            if "assumed" in low and s["id"] != "D07b":
                p.append("%s: assumed in %r" % (s["id"], t[:70]))
            for w in TIER_WORDS:
                if w in low:
                    p.append("%s: %r in %r" % (s["id"], w, t[:70]))
    l02 = [s for s in screens if s["id"] == "L02"][0]
    for row in l02["ui"][0][2]:
        if any(w in row[0].lower() for w in L02_BAD):
            p.append("L02: client-data fallback row %r" % row[0])
    bad = [f["field"] for f in fp["fields"] if f.get("fallback") != "band required"]
    if bad:
        p.append("fp_react_inputs.json: fallback not band required on %s" % ", ".join(bad))
    if "fallbacks_branch_b" in fp:
        p.append("fp_react_inputs.json still carries fallbacks_branch_b")
    return p, "%d fields band required; L02 %d engine rows" % (len(fp["fields"]), len(l02["ui"][0][2]))


def check13(screens, byid):
    p = []
    d_screens = [s for s in validate_v02.live(screens) if s["id"].startswith("D") and s["frame"] == "phone" and s["template"] != "T-sheet" and s["id"] != "D00"]
    for s in d_screens:
        if not any("silent autosave" in st for st in s["spec"].get("states", [])):
            p.append("%s: no silent-autosave exit line" % s["id"])
    inbound = set()
    for s in validate_v02.live(screens):
        for _, t in validate_v02.links(s):
            if t == "O03":
                inbound.add(s["id"])
    allowed = {"D12a", "D12b", "D12c", "D12d", "D12e", "D12f", "D12g", "D12h", "O02"}
    extra = sorted(inbound - allowed)
    if extra:
        p.append("O03 reachable from %s" % ", ".join(extra))
    if not (inbound & allowed):
        p.append("O03 has no inbound link from a relief card or O02")
    x00 = byid["X00"]
    rules = [r for r in x00["ui"] if r[0] == "card" and r[1] == "Standing rules for every D screen"][0][2]
    if not any(r.startswith("12.") and "silent autosave" in r for r in rules):
        p.append("X00 rule 12 does not say silent autosave")
    return p, "%d D screens carry the exit line; O03 inbound from %s" % (len(d_screens), ", ".join(sorted(inbound)))


def check14(screens, byid):
    p = []
    chain = ["A05"]
    cur = "A05"
    for _ in range(2):
        btns = [r for r in byid[cur]["ui"] if r[0] == "btn"]
        if not btns:
            p.append("%s: no primary button" % cur)
            break
        cur = btns[0][2]
        chain.append(cur)
    if chain != ["A05", "A06", "D01"]:
        p.append("primary chain is %s" % " -> ".join(chain))
    for sid in ("A05", "A06"):
        for r in byid[sid]["ui"]:
            if r[0] in ("btn", "btn2", "link") and r[2] == "A07":
                p.append("%s still stops at A07" % sid)
    if not any("A08" in st for st in byid["D02"]["spec"]["states"]):
        p.append("D02 carries no A08 state")
    for sid in ("A07", "A08", "A09"):
        if byid[sid]["v02"]["status"] != "changed":
            p.append("%s status is %s" % (sid, byid[sid]["v02"]["status"]))
    if byid["A08"]["template"] != "T-sheet":
        p.append("A08 is not a sheet")
    return p, "chain %s; A08 %s on D02" % (" -> ".join(chain), byid["A08"]["template"])


def check15(screens, byid):
    p = []
    for sid in ("Q06", "Q06a"):
        if sid not in byid or byid[sid]["v02"]["status"] in ("dropped", "split"):
            p.append("%s missing" % sid)
    q06 = byid.get("Q06")
    n_map = 0
    if q06:
        for c in q06["spec"].get("chip_map", []):
            for t in c["reopens"]:
                n_map += 1
                if t not in byid or byid[t]["v02"]["status"] in ("dropped", "split"):
                    p.append("Q06 chip %r maps to %s, not a live screen" % (c["chip"], t))
        if len(q06["spec"].get("chip_map", [])) != 7:
            p.append("Q06 has %d chips, not seven" % len(q06["spec"].get("chip_map", [])))
    for sid in ("H01", "H07", "H09", "Q01", "N04"):
        if not any(t == "Q06" for _, t in validate_v02.links(byid[sid])):
            p.append("%s does not link to Q06" % sid)
    states = load("v02/states.json")["states"]
    s11 = [st for st in states if st["id"] == "S11"][0]
    if "Q06" not in s11["exit"]:
        p.append("S11 exit path does not carry Q06")
    return p, "7 chips, %d mapped screens; linked from H01, H07, H09, Q01, N04; S11 exit carries Q06" % n_map


def harness(path):
    env = dict(os.environ)
    env["WIRE_HTML"] = path
    proc = subprocess.run(["node", "-"], input=check_site.HARNESS, capture_output=True, text=True, env=env)
    if proc.returncode != 0:
        return None, proc.stderr[-600:]
    return json.loads(proc.stdout.strip().splitlines()[-1]), ""


def blob_of(html, name):
    start = html.index("var %s=" % name) + len("var %s=" % name)
    end = html.index(";\nvar ", start) if ";\nvar " in html[start:] else html.index(";</script>", start)
    return json.loads(html[start:end])


def check16(screens):
    p, notes = [], []
    live = validate_v02.live(screens)
    expected = {"yeslyf_v02_team.html": len(live), "yeslyf_v02_spinach.html": len(live),
                "yeslyf_v02_compliance.html": len([s for s in live if s["compliance"]["review"]])}
    for name, n in expected.items():
        path = os.path.join(AUD, name)
        if not os.path.exists(path):
            p.append("%s missing" % name)
            continue
        with open(path) as fh:
            html = fh.read()
        if 'name="robots" content="noindex' not in html:
            p.append("%s lacks noindex" % name)
        for bad in ("http://", "https://", "script.google"):
            if bad in html:
                p.append("%s carries %r" % (name, bad))
        for ch in html:
            if ord(ch) > 126:
                p.append("%s is not ASCII" % name)
                break
        out, err = harness(path)
        if out is None:
            p.append("%s: harness failed: %s" % (name, err))
            continue
        bad = [r for r in out["results"] if not r["ok"]]
        if bad:
            p.append("%s: %s" % (name, "; ".join(r["check"] + " " + r["why"] for r in bad[:5])))
        if out["screens"] != n:
            p.append("%s renders %d screens, expected %d" % (name, out["screens"], n))
        if not out["exportOk"]:
            p.append("%s: export %s" % (name, out["exportWhy"]))
        if out["endpoint"]:
            p.append("%s: endpoint not blank" % name)
        emb = blob_of(html, "SCREENS")
        opts = blob_of(html, "WIRE_OPTS")
        if name == "yeslyf_v02_compliance.html":
            if any(not s["compliance"]["review"] for s in emb):
                p.append("compliance file carries a screen not flagged for review")
            if any(s.get("spec", {}).get("dev") for s in emb):
                p.append("compliance file carries dev notes")
            if opts.get("lock") != "Compliance":
                p.append("compliance identity not locked")
            for s in emb:
                if "fees and refunds" in s["compliance"]["reasons"]:
                    for r in s["ui"]:
                        for t in json.dumps(r).split("Rs ")[1:]:
                            if t[:1].isdigit():
                                p.append("compliance file: a price beyond Rs ___ on %s" % s["id"])
            ids = [s["id"] for s in emb]
            order = [s["id"] for s in live if s["compliance"]["review"]]
            if ids != order:
                p.append("compliance file is not in flow order")
        if name == "yeslyf_v02_spinach.html":
            rendered = html.replace(build_site.read_script("renderer_v02.js"), "")  # the renderer source names both blocks; the page must not render them
            if any("compliance" in s for s in emb) or "Compliance checklist" in rendered or 'id="a-backlog"' in rendered or 'data-viewpane="admin"' in rendered:
                p.append("Spinach file carries a compliance checklist or the CRM backlog")
            if any(s["v02"].get("causes") for s in emb):
                p.append("Spinach file carries causes")
            if opts.get("lock") != "Spinach":
                p.append("Spinach identity not locked")
        if name == "yeslyf_v02_team.html":
            if "CRM backlog" not in html or 'data-viewpane="admin"' not in html or 'data-viewpane="changelog"' not in html:
                p.append("team file lacks the admin, CRM backlog or changelog view")
            if opts.get("identities") != ["Bhuvanaa", "Harish", "Gaurav", "Kajal", "Somil", "Spinach", "Compliance"]:
                p.append("team identities are not the seven")
        notes.append("%s %d screens, %d KB" % (name, out["screens"], round(len(html) / 1024)))
    return p, "; ".join(notes)


def check17():
    p = []
    chg = load("changelog.json")
    if [x["id"] for x in chg.get("split", [])] != ["D05", "D06", "D08"]:
        p.append("split is %s" % [x["id"] for x in chg.get("split", [])])
    if [x["id"] for x in chg["dropped"]] != ["R11", "G02", "G08"]:
        p.append("dropped is %s" % [x["id"] for x in chg["dropped"]])
    with open(os.path.join(DOCS, "changelog.html")) as fh:
        html = fh.read()
    if 'id="c-split"' not in html:
        p.append("changelog.html has no split section")
    return p, "split D05, D06, D08; dropped %d" % len(chg["dropped"])


def main():
    failures = 0
    for script in ("validate_v02.py", "check_site.py"):
        proc = subprocess.run([sys.executable, os.path.join(SCRIPTS, script)], capture_output=True, text=True)
        sys.stdout.write(proc.stdout)
        failures += 1 if proc.returncode else 0
    screens = load("screens_v02.json")["screens"]
    byid = {s["id"]: s for s in screens}
    order = [s["id"] for s in screens]
    checks = [
        ("11 D02 and D04 multi-select: three ticks open exactly three screens; unticked types are explicit none", lambda: check11(screens, byid, order)),
        ("12 no assumed outside D07b; no income-tier bands or multipliers; L02 engine rows only; band required on every field", lambda: check12(screens)),
        ("13 exit from any D screen is a silent autosave; O03 only from the D12 cards and O02", lambda: check13(screens, byid)),
        ("14 aa path walks A05 -> A06 -> D01 with no stop at A07; A08 is a state on D02", lambda: check14(screens, byid)),
        ("15 Q06 and Q06a exist; every chip maps to live screens; H01, H07, H09, Q01 link to Q06", lambda: check15(screens, byid)),
        ("16 audience files open from disk, render their screen set, carry no endpoint URL; compliance and Spinach subsets hold", lambda: check16(screens)),
        ("17 changelog shows D05, D06, D08 under split; dropped count is 3", check17),
    ]
    for name, fn in checks:
        problems, note = fn()
        print("%s: %s%s" % ("FAIL" if problems else "PASS", name, (" (%s)" % note) if note else ""))
        for x in problems[:20]:
            print("    " + x)
        failures += 1 if problems else 0
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
