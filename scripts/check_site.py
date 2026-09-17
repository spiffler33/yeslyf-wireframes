#!/usr/bin/env python3
"""Site-level acceptance checks 8, 9 and 10 of plan_v2.md section 7, run locally on docs/.

8. Every filter of docs/wireframes_v02.html (tier, path, compliance, template, and each state when the states file
   exists) walks end to end: the page is loaded in a Node vm context with a fake DOM, next is pressed from the
   first screen until the walk wraps, and the visited list must equal the screens in scope, in flow order.
9. Export works with the sheet endpoint blank (the export text is produced without throwing); every docs/*.html
   carries noindex. Pages over HTTPS is checked on the live URL, not here.
10. docs/v01/ files are byte-identical to inputs/v01/.
Needs Python 3 and Node only. Prints PASS or FAIL per check; exits 1 on any failure.
"""
import filecmp
import glob
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
V01_IN = os.path.join(ROOT, "inputs", "v01")

HARNESS = r"""
const fs = require("fs"), vm = require("vm");
const file = process.env.WIRE_HTML;
const h = fs.readFileSync(file, "utf8");
function scriptBodies(s){ const out = []; let i = 0; for(;;){ const a = s.indexOf("<script", i); if(a < 0) break; const b = s.indexOf(">", a); const c = s.indexOf("</script>", b); out.push(s.slice(b + 1, c)); i = c + 9; } return out; }
const els = {}, listeners = {};
function fakeEl(id){ return { id: id || "", innerHTML: "", textContent: "", className: "", value: "", placeholder: "", style: {}, scrollTop: 0, tagName: "DIV",
  addEventListener(){}, removeEventListener(){}, querySelectorAll(){ return []; }, querySelector(){ return null; }, appendChild(){}, removeChild(){}, click(){},
  setAttribute(){}, getAttribute(){ return null; }, scrollIntoView(){}, closest(){ return null; }, classList: { add(){}, remove(){}, toggle(){}, contains(){ return false; } } }; }
const document = { getElementById(id){ if(!els[id]) els[id] = fakeEl(id); return els[id]; }, querySelector(){ return null; }, querySelectorAll(){ return []; },
  createElement(){ return fakeEl(); }, body: fakeEl("body"), addEventListener(t, f){ (listeners[t] = listeners[t] || []).push(f); } };
const storage = {};
const localStorage = { getItem: k => (k in storage ? storage[k] : null), setItem: (k, v) => { storage[k] = String(v); }, removeItem: k => { delete storage[k]; } };
const ctx = { console, document, localStorage, location: { hash: "", search: "", pathname: "/wireframes_v02.html", href: "" }, history: { replaceState(){} },
  navigator: {}, setTimeout(){ return 0; }, clearTimeout(){}, Blob: function(){}, URL: { createObjectURL(){ return ""; } }, alert(){}, fetch(){ return Promise.resolve(); },
  addEventListener(){}, removeEventListener(){} };
ctx.window = ctx; vm.createContext(ctx);
for(const b of scriptBodies(h)) vm.runInContext(b, ctx);
(listeners.DOMContentLoaded || []).forEach(f => f());
const W = ctx.yeslyfWire; const results = [];
function walkCheck(label){
  const list = W.walk();
  if(!list.length){ results.push({ check: label, ok: false, why: "no screen in scope" }); return; }
  W.go(list[0]); const seen = [W.current()]; let guard = 0;
  while(guard++ < 5000){ W.step(1); const c = W.current(); if(c === list[0]) break; seen.push(c); }
  const wrapped = guard < 5000;
  const ok = wrapped && seen.length === list.length && seen.every((id, i) => id === list[i]);
  results.push({ check: label, ok, n: list.length, why: ok ? "" : ("visited " + seen.length + " of " + list.length + (wrapped ? "" : "; never wrapped")) });
}
const F = W.filters();
for(const t of F.tiers){ W.setFilter("tier", t); walkCheck("tier " + t); } W.setFilter("tier", "ALL");
for(const p of F.paths){ W.setFilter("path", p); walkCheck("path " + p); } W.setFilter("path", "both");
for(const c of F.comps){ W.setFilter("comp", c); walkCheck("compliance " + c); } W.setFilter("comp", "all");
for(const t of F.templates){ W.setFilter("tpl", t); walkCheck("template " + t); } W.setFilter("tpl", "all");
for(const z of (F.freeze || [])){ W.setFilter("freeze", z); walkCheck("frozen " + z); } W.setFilter("freeze", "all");
for(const s of F.states){ W.setFilter("state", s); const land = W.landing(s); const ok = !!land && W.current() === land; results.push({ check: "state " + s, ok, why: ok ? "" : ("landed on " + W.current() + ", expected " + land) }); }
let exportOk = true, exportWhy = "";
try { const md = W.exportText(); exportOk = typeof md === "string" && md.indexOf("# yeslyf") === 0; if(!exportOk) exportWhy = "unexpected export text"; } catch(e){ exportOk = false; exportWhy = String(e); }
console.log(JSON.stringify({ results, exportOk, exportWhy, states: F.states.length, screens: ctx.SCREENS.length, endpoint: (function(){ try { return JSON.parse(storage["yeslyf_board_v1"] || "{}").endpoint || ""; } catch(e){ return ""; } })() }));
"""


def run_harness():
    env = dict(os.environ)
    env["WIRE_HTML"] = os.path.join(DOCS, "wireframes_v02.html")
    proc = subprocess.run(["node", "-"], input=HARNESS, capture_output=True, text=True, env=env)
    if proc.returncode != 0:
        raise SystemExit("node harness failed:\n" + proc.stderr[-2000:])
    return json.loads(proc.stdout.strip().splitlines()[-1])


def main():
    failures = 0
    out = run_harness()
    bad = [r for r in out["results"] if not r["ok"]]
    walks = [r for r in out["results"] if not r["check"].startswith("state ")]
    states = [r for r in out["results"] if r["check"].startswith("state ")]
    print("%s: 8 filters walk end to end: %d filter values over %d screens%s" % (
        "FAIL" if bad else "PASS", len(walks), out["screens"],
        ("; %d states land where the contract says" % len(states)) if states else "; state filter pending (no states file)"))
    for r in bad:
        print("    " + r["check"] + ": " + r["why"])
    failures += 1 if bad else 0

    noindex_bad = []
    for path in sorted(glob.glob(os.path.join(DOCS, "*.html"))):
        with open(path) as fh:
            if 'name="robots" content="noindex' not in fh.read():
                noindex_bad.append(os.path.basename(path))
    ok9 = out["exportOk"] and not noindex_bad and out["endpoint"] == ""
    print("%s: 9 export works with the endpoint blank; noindex on every page (HTTPS is checked on the live URL)" % ("PASS" if ok9 else "FAIL"))
    if not out["exportOk"]:
        print("    export: " + out["exportWhy"])
    if out["endpoint"]:
        print("    endpoint was not blank in the harness")
    for name in noindex_bad:
        print("    " + name + " lacks noindex")
    failures += 0 if ok9 else 1

    diffs = []
    for name in sorted(os.listdir(V01_IN)):
        src = os.path.join(V01_IN, name)
        dst = os.path.join(DOCS, "v01", name)
        if not os.path.exists(dst):
            continue
        if not filecmp.cmp(src, dst, shallow=False):
            diffs.append(name)
    served = [n for n in sorted(os.listdir(os.path.join(DOCS, "v01"))) if n.endswith(".html")]
    ok10 = not diffs and all(os.path.exists(os.path.join(V01_IN, n)) for n in served)
    print("%s: 10 docs/v01/ byte-identical to inputs/v01/ (%s)" % ("PASS" if ok10 else "FAIL", ", ".join(served)))
    for name in diffs:
        print("    " + name + " differs")
    failures += 0 if ok10 else 1
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
