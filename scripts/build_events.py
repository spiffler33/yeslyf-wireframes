#!/usr/bin/env python3
"""Generate docs/events.html and docs/review/events.html from data (phase 10b-2; Vatsal, 16 Sep 2026). Never hand-edit docs/.

The event schema of the yeslyf app v0.2, one row per event per screen:
- screen_view for every live v0.2 screen (data/screens_v02.json, not dropped or split); the screen is its screen_id;
- every named event a live screen carries (its events list minus its own <id>_view), with the screen, section, tier
  and path of that screen;
- the core-action events of data/events_extra.json (action_started, action_done, review_opened, review_accepted,
  life_event_reported, nudge_sent, nudge_opened, open_organic), which no single screen carries.
Every event carries the standard properties listed in data/events_extra.json (user_id, screen_id, tier, state, sku,
source_choice, timestamp). The Properties column lists what an event adds beyond them: for named events from
plan_v2.md appendix D (the named_properties map of data/events_extra.json, matched by the exact event name or by the
part after the screen's own "<id>_" prefix for the number-screen set), for core actions from their own entry.
The count line on the page is the check: rows = screens + named events + core actions.
The table filters by section; Export downloads the whole schema as markdown. No comments and no sheet writes.
Same tokens and top nav as the other board pages (scripts/build_site.py supplies head(), header() and the CSS).
Called at the end of scripts/build_site.py after build_integrations (TABS and REVIEW_TABS carry the Events tab);
also runs on its own. Writes docs/events.html and its review copy docs/review/events.html (the review tabs, no
setup link, screen links into the review copy of Wireframes v0.2).
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

PAGE = "events.html"
EXTRA_FILE = os.path.join(DATA, "events_extra.json")
KINDS = ["screen view", "named", "core action"]
CORE = "core"  # section key of a core action that belongs to no section (app-wide)
esc = site.esc


def props_for(name, sid, named_props):
    """What a named event adds (plan_v2.md appendix D): by exact name, else by the part after the screen's own
    "<id>_" prefix (the number-screen set: <id>_set, <id>_skip, ...)."""
    if name in named_props:
        return named_props[name]
    own = sid + "_"
    if name.startswith(own):
        return named_props.get(name[len(own):], "")
    return ""


def validate(v02, extra):
    problems = []
    for key in ("standard_properties", "named_properties", "events"):
        if key not in extra:
            problems.append("events_extra.json: missing key %s" % key)
    if problems:
        return problems
    if not extra["standard_properties"] or not all(isinstance(p, str) and p for p in extra["standard_properties"]):
        problems.append("events_extra.json: standard_properties must be a list of names")
    if not isinstance(extra["named_properties"], dict):
        problems.append("events_extra.json: named_properties must be a map")
    seen = set()
    for i, e in enumerate(extra["events"]):
        name = e.get("name", "")
        for f in ("name", "fires", "properties", "section", "cause"):
            if f not in e:
                problems.append("events_extra.json: event %s (row %d) lacks %s" % (name or "?", i, f))
        if not name or name in seen:
            problems.append("events_extra.json: event row %d has an empty or duplicate name" % i)
        seen.add(name)
        if not str(e.get("fires", "")).strip() or not str(e.get("cause", "")).strip():
            problems.append("events_extra.json: event %s needs fires and cause" % name)
    for s in site.live_screens(v02):
        if s["id"] + "_view" not in s["events"]:
            problems.append("%s: events lack its own %s_view" % (s["id"], s["id"]))
        if len(set(s["events"])) != len(s["events"]):
            problems.append("%s: events list repeats a name" % s["id"])
    return problems


def build_rows(v02, extra):
    sections = dict(v02["sections"])
    live = site.live_screens(v02)
    named_props = extra["named_properties"]
    rows = []
    for s in live:
        base = {"screen": s["id"], "sec": s["sec"], "section": sections.get(s["sec"], s["sec"]),
                "tier": ", ".join(s["tier"]), "path": s["path"], "fires": "", "cause": ""}
        rows.append(dict(base, event="screen_view", kind=KINDS[0], props=""))
        for e in s["events"]:
            if e == s["id"] + "_view":
                continue
            rows.append(dict(base, event=e, kind=KINDS[1], props=props_for(e, s["id"], named_props)))
    for e in extra["events"]:
        sec = e["section"] or CORE
        rows.append({"event": e["name"], "kind": KINDS[2], "screen": "", "sec": sec,
                     "section": "app-wide" if sec == CORE else sections.get(sec, sec), "tier": "ALL", "path": "both",
                     "props": e["properties"], "fires": e["fires"], "cause": e["cause"]})
    counts = {"screens": len(live), "named": sum(len(s["events"]) - 1 for s in live), "core": len(extra["events"]),
              "unique": len(set(r["event"] for r in rows if r["kind"] == KINDS[1]))}
    return rows, live, counts


EXTRA_CSS = """
  .lead{margin-bottom:8px}
  .counts{display:flex;flex-wrap:wrap;gap:4px 6px;align-items:center;font-size:12px;margin:8px 0 0}
  .counts .k{color:var(--mute);margin-right:4px}
  .chip{display:inline-block;border:1px solid var(--line);border-radius:4px;padding:1px 7px;background:#fff;color:var(--ink);white-space:nowrap;font-size:12px;font-variant-numeric:tabular-nums}
  .chip b{font-weight:600}
  .std{font-size:12px;color:var(--mute);margin:8px 0 0;max-width:860px} .std code{font-size:11.5px;color:var(--ink)}
  .toolbar{display:flex;gap:6px 12px;flex-wrap:wrap;align-items:center;margin:0 0 10px;font-size:12px}
  .toolbar label{display:flex;gap:5px;align-items:center;white-space:nowrap}
  .toolbar select{padding:5px;border:1px solid var(--line);border-radius:5px;background:#fff;max-width:280px}
  th.c-kind{width:90px} th.c-screen{width:70px}
  td.ev{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12px;white-space:nowrap}
  td.ev .meta{font-family:var(--sans);white-space:normal;max-width:520px;margin-top:1px}
  td.kd,td.tr,td.pa{white-space:nowrap;color:var(--mute)}
  td.pr{font-size:12px;color:var(--mute)} td.pr code{font-size:11.5px;color:var(--ink)}
  tr.core td{background:#FCFCFD}
  .top .pill{display:none}
  @media (max-width:760px){ th.c-tier,td.c-tier,th.c-path,td.c-path{display:none} td.ev{white-space:normal;word-break:break-all} }
"""

JS = r"""
(function(){
  function esc(s){ return String(s===undefined||s===null?"":s).split("&").join("&amp;").split("<").join("&lt;").split(">").join("&gt;").split('"').join("&quot;"); }
  var ft; function flash(t){ var s=document.getElementById("saved"); if(!s) return; s.textContent=t||""; clearTimeout(ft); ft=setTimeout(function(){ s.textContent=""; },1800); }
  function cellmd(v){ return String(v===undefined||v===null?"":v).split("\n").join(" ").split("|").join("\\|"); }
  function sectionOf(r){ return r.sec==="core"?"-":(r.sec+" "+r.section); }
  function applyFilter(){ var sel=document.getElementById("sec"); var v=sel?sel.value:"All"; var trs=document.querySelectorAll("#etbl tbody tr"); var shown=0;
    for(var i=0;i<trs.length;i++){ var tr=trs[i]; var ok=(v==="All")||(v==="core"?tr.getAttribute("data-kind")==="core action":tr.getAttribute("data-sec")===v); tr.classList.toggle("hidden",!ok); if(ok) shown++; }
    var c=document.getElementById("count"); if(c) c.textContent=shown+" of "+ROWS.length; }
  function md(){ var L=["# yeslyf event schema v0.2","Exported "+new Date().toLocaleString(),
      "Rows: "+ROWS.length+" = "+COUNTS.screens+" screen views + "+COUNTS.named+" named events + "+COUNTS.core+" core actions; "+COUNTS.unique+" unique named events",
      "Standard properties on every event: "+STANDARD.join(", "),"Properties lists what an event adds beyond the standard ones (plan_v2.md appendix D for named events).",""];
    var cols=["Event","Kind","Screen","Section","Tier","Path","Properties","Fires when"]; L.push("| "+cols.join(" | ")+" |"); L.push("|"+cols.map(function(){ return " --- |"; }).join(""));
    ROWS.forEach(function(r){ L.push("| "+[r.event,r.kind,r.screen||"-",sectionOf(r),r.tier,r.path,r.props||"standard only",r.fires?(r.fires+" ("+r.cause+")"):"-"].map(cellmd).join(" | ")+" |"); });
    return L.join("\n"); }
  function exportMd(){ var text=md(); try{ navigator.clipboard&&navigator.clipboard.writeText(text); }catch(e){}
    try{ var b=new Blob([text],{type:"text/markdown"}); var a=document.createElement("a"); a.href=URL.createObjectURL(b); a.download="yeslyf_events_v02.md"; document.body.appendChild(a); a.click(); document.body.removeChild(a); }catch(e){}
    flash("Markdown exported and copied"); }
  document.addEventListener("DOMContentLoaded",function(){
    var sel=document.getElementById("sec"); if(sel) sel.addEventListener("change",applyFilter); applyFilter();
    var ex=document.getElementById("export"); if(ex) ex.addEventListener("click",exportMd); });
  // test hook for the checks (and for the console)
  window.yeslyfEvents={ exportText: md, rows: function(){ return ROWS.length; }, counts: COUNTS, filter: function(v){ var s=document.getElementById("sec"); if(s) s.value=v; applyFilter(); } };
})();
"""


def render_row(r, live_ids):
    core = r["kind"] == KINDS[2]
    ev = ('<b>%s</b>' % esc(r["event"])) if core else esc(r["event"])
    if r["fires"]:
        ev += '<div class="meta">%s <span class="cause">%s</span></div>' % (esc(r["fires"]), esc(r["cause"]))
    screen = site.sid_link(r["screen"], live_ids) if r["screen"] else "-"
    section = "-" if r["sec"] == CORE else "%s %s" % (esc(r["sec"]), esc(r["section"]))
    props = ('<code>%s</code>' % esc(r["props"])) if r["props"] else "standard only"
    return ('<tr%s data-sec="%s" data-kind="%s"><td class="ev">%s</td><td class="kd">%s</td><td>%s</td><td>%s</td>'
            '<td class="tr c-tier">%s</td><td class="pa c-path">%s</td><td class="pr">%s</td></tr>' % (
                ' class="core"' if core else "", "" if r["sec"] == CORE else esc(r["sec"]), esc(r["kind"]), ev, esc(r["kind"]),
                screen, section, esc(r["tier"]), esc(r["path"]), props))


def build_page(rows, live, counts, v02, extra, review=False):
    """review=True renders the docs/review/ copy: the review tabs only, no setup link, screen links into the review
    copy of Wireframes v0.2 (review/index.html)."""
    live_ids = {s["id"] for s in live}
    n = len(rows)
    who = '<span class="who"></span>'
    std = "".join('<code>%s</code>%s' % (esc(p), ", " if i < len(extra["standard_properties"]) - 1 else "")
                  for i, p in enumerate(extra["standard_properties"]))
    intro = ('<section><h1>Event schema</h1>'
             '<p class="lead">One row per event per screen. Every live v0.2 screen fires screen_view with its ID as screen_id; the named events are the ones the screens carry; '
             'the core actions are app-level and belong to no single screen. Properties lists what an event adds beyond the standard set.</p>'
             '<div class="counts"><span class="k">%d rows</span><span class="chip"><b>%d</b> screen views</span><span class="chip"><b>%d</b> named events</span>'
             '<span class="chip"><b>%d</b> core actions</span><span class="k">%d unique named events</span></div>'
             '<p class="std">Standard properties on every event: %s.</p></section>' % (
                 n, counts["screens"], counts["named"], counts["core"], counts["unique"], std))
    options = '<option value="All">All</option>' + "".join('<option value="%s">%s %s</option>' % (esc(k), esc(k), esc(v)) for k, v in v02["sections"]) + '<option value="core">Core actions</option>'
    toolbar = '<div class="toolbar"><label>Section <select id="sec">%s</select></label><span id="count" class="meta"></span></div>' % options
    thead = ('<thead><tr><th>Event</th><th class="c-kind">Kind</th><th class="c-screen">Screen</th><th>Section</th>'
             '<th class="c-tier">Tier</th><th class="c-path">Path</th><th>Properties</th></tr></thead>')
    table = '<div class="wrap"><table id="etbl">' + thead + '<tbody>' + "\n".join(render_row(r, live_ids) for r in rows) + '</tbody></table></div>'
    if review:
        table = table.replace('href="wireframes_v02.html#', 'href="index.html#')
    blob = ('<script>var ROWS=' + site.js_blob(rows) + ';\nvar COUNTS=' + site.js_blob(counts) + ';\nvar STANDARD=' +
            site.js_blob(extra["standard_properties"]) + ';</script>\n')
    return (site.head("yeslyf event schema v0.2", site.CSS + EXTRA_CSS) + '<body>\n' +
            site.header(PAGE, "event schema, %d rows" % n, who_html=who, export_label="Export markdown",
                        tabs=site.REVIEW_TABS if review else None, setup_link=not review) +
            '<main class="main" style="max-width:none">' + intro + '<section>' + toolbar + table + '</section></main>\n' +
            blob + '<script>' + JS + '</script>\n</body>\n</html>\n')


def main():
    with open(EXTRA_FILE) as fh:
        raw = fh.read()
    site.check_ascii("data/events_extra.json", raw)
    extra = json.loads(raw)
    v02 = site.load("screens_v02.json")
    problems = validate(v02, extra)
    if problems:
        for p in problems:
            print("ERROR: " + p)
        sys.exit(1)
    rows, live, counts = build_rows(v02, extra)
    if len(rows) != counts["screens"] + counts["named"] + counts["core"]:
        print("ERROR: events: %d rows, expected %d screens + %d named + %d core" % (len(rows), counts["screens"], counts["named"], counts["core"]))
        sys.exit(1)
    pages = {PAGE: build_page(rows, live, counts, v02, extra), "review/" + PAGE: build_page(rows, live, counts, v02, extra, review=True)}
    errors = []
    for name, page in pages.items():
        site.check_ascii(name, page)
        if 'name="robots" content="noindex' not in page:
            errors.append(name + " lacks noindex")
        for word in site.FORBIDDEN:
            i = page.find(word)
            while i >= 0:
                errors.append("%s contains %r: ...%s..." % (name, word, page[max(0, i - 50):i + len(word) + 30].replace("\n", " ")))
                i = page.find(word, i + 1)
    if errors:
        for e in errors:
            print("ERROR: " + e)
        sys.exit(1)
    os.makedirs(os.path.join(DOCS, "review"), exist_ok=True)
    for name, page in pages.items():
        with open(os.path.join(DOCS, name), "w") as fh:
            fh.write(page)
        print("wrote docs/%s (%d bytes, %d rows: %d screen views, %d named events, %d core actions)" % (
            name, len(page), len(rows), counts["screens"], counts["named"], counts["core"]))


if __name__ == "__main__":
    main()
