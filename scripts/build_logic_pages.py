#!/usr/bin/env python3
"""Generate the four logic panel pages (PLAN_logic_panel_v03.md 12.6, phase B0; logic plan, 8 Oct 2026):
docs/logic_tech.html, logic_access.html, logic_walk.html and logic_ops.html, each from its own data file in data/,
inside the board's shell, with one comment box per section. One file per page, json.dumps(indent=1) plus a newline:
  {"page": the board page key (the file's own name), "title", "audience": one line,
   "sections": [{"id": a short anchor such as "t1", "heading", "lines": [strings],
                 "tables": [{"title": optional, "cols": [strings], "rows": [[cell, ...], each as long as cols]}],
                 "open_items": ["LQ17", ...], "derived": "seat_by_screen"}]}
lines, tables, open_items and derived are optional, drawn in the order their keys stand. A cell is a string, a
[text, href] link, or a list of such links joined by ", ". Every heading, line, title and cell passes through
build_brief.tokens() ({I04} -> "I04 <vendor>"); an open item renders as "<id> <item>" from data/logic_gaps.json;
"seat_by_screen" is built from the role and writes fields of data/logic_screens.json, then M03, M07 and M10.
All four pages are built and checked first and written last: every failure is named and no page is written. Never
hand-edit docs/. Called from scripts/build_site.py after build_logic_wireframes.main(); also runs on its own.
"""
import json
import os
import sys

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(os.path.dirname(SCRIPTS), "docs")
sys.path.insert(0, SCRIPTS)
import build_site as site  # noqa: E402
import validate_v02  # noqa: E402
from build_brief import tokens  # noqa: E402
from build_logic_wireframes import SEATS, all_text  # noqa: E402  (the ten seats in the A0 order; every string of a doc)

esc = site.esc
PAGES = ["logic_tech", "logic_access", "logic_walk", "logic_ops"]
FILE_KEYS = {"page", "title", "audience", "sections"}
SECTION_KEYS = {"id", "heading", "lines", "tables", "open_items", "derived"}
TABLE_KEYS = {"title", "cols", "rows"}
ADMIN_IDS = ["M03", "M07", "M10"]
# The placeholder labels build_logic_wireframes.main() exempts from the same vendor check: they are not vendor names.
GENERIC_VENDOR_LABELS = {"internal", "internal (Spinach)", "not decided"}
# renderer_v02.js:19's list minus Spinach (logic plan, 8 Oct 2026): the Tracker lists every comment under the identity Spinach on any page on docs/review/tracker.html, the link Spinach has; section 0 and 12.0 keep the logic work off that link until the merge (the Logic tab gets the same change in its A0 fix).
IDENTITIES = ["Bhuvanaa", "Harish", "Gaurav", "Kajal", "Somil", "Raafiya", "Vatsal", "Compliance"]
# The Logic tab's banner, word for word (plan 12.1 step 2).
BANNER = ("side wireframes: proposed, not yet merged into Wireframes v0.2. The design is proposed, to be confirmed at the "
          "logic panel review (to be decided: the review date). Every logic value is a rehearsal value and every count a "
          "typed example.")

EXTRA_CSS = """
  .banner{padding:6px 18px;background:var(--accent-soft);border-bottom:1px solid #C9A800;font-size:12.5px}
  .who select{padding:6px 8px;border:1px solid var(--line);border-radius:6px;background:#fff;max-width:170px}
"""

# The comment script of scripts/build_seats.py, cut to one note per section: a write with no name is held by the
# shared layer and the page says so; the local cache is overridden by a live board row.
JS = r"""
(function(){
  var P=LOGIC_PAGE, KEY="yeslyf_"+P.key+"_v1";
  var byId={}; P.sections.forEach(function(s){ byId[s.id]=s; });
  var S={}; try{ S=JSON.parse(localStorage.getItem(KEY)||"{}")||{}; }catch(e){ S={}; }
  if(!S.rows) S.rows={}; if(!S.who) S.who="";
  function save(){ try{ localStorage.setItem(KEY, JSON.stringify(S)); }catch(e){} }
  var ft; function flash(t){ var s=document.getElementById("saved"); if(!s) return; s.textContent=t||"Saved in this browser"; clearTimeout(ft); ft=setTimeout(function(){ s.textContent=""; },1800); }
  function esc(s){ return String(s===undefined||s===null?"":s).split("&").join("&amp;").split("<").join("&lt;").split(">").join("&gt;").split('"').join("&quot;"); }
  function row(id){ if(!S.rows[id]) S.rows[id]={}; return S.rows[id]; }
  function noteVal(id){ var e=S.rows[id]; return (e&&e.note!==undefined)?e.note:""; }
  function localRows(){ var out=[]; for(var id in S.rows){ if(byId[id]&&S.rows[id].note!==undefined) out.push({item_id:id,field:"note",value:S.rows[id].note,kind:"comment"}); } return out; }
  function put(id,value){ if(!window.yeslyfBoard) return true; var ok=yeslyfBoard.write({item_id:id,field:"note",value:value,who:S.who||"",kind:"comment"}); if(!ok) setTimeout(function(){ flash(yeslyfBoard.noIdentity); },0); return ok; }
  function paintAll(){ P.sections.forEach(function(s){ var el=document.getElementById("note-"+s.id), v=noteVal(s.id); if(el&&el.value!==v) el.value=v; });
    var rv=document.getElementById("reviewer"); if(rv&&rv.value!==(S.who||"")) rv.value=S.who||""; }
  function applyRemote(rows){ rows.forEach(function(r){ if(r.field==="note"&&byId[r.item_id]) row(r.item_id).note=r.value||""; }); save(); paintAll(); }
  function md(){ var L=[P.exportTitle,"Exported "+new Date().toLocaleString()+(S.who?" by "+S.who:""),"Write-back: "+(window.yeslyfBoard?yeslyfBoard.label():"offline; this file is the record"),""], n=0;
    P.sections.forEach(function(s){ var v=noteVal(s.id); if(!v) return; n++; L.push("- **"+s.id+" "+s.heading+"**"); L.push("  "+String(v).split("\n").join("\n  ")); });
    if(!n) L.push("(no comments yet)"); return L.join("\n"); }
  function exportMd(){ var text=md(); try{ navigator.clipboard&&navigator.clipboard.writeText(text); }catch(e){}
    try{ var b=new Blob([text],{type:"text/markdown"}); var a=document.createElement("a"); a.href=URL.createObjectURL(b); a.download="yeslyf_"+P.key+"_comments.md"; document.body.appendChild(a); a.click(); document.body.removeChild(a); }catch(e){}
    flash("Comments exported and copied"); }
  var tmr={};
  document.addEventListener("DOMContentLoaded",function(){
    if(window.yeslyfBoard){
      Array.prototype.forEach.call(document.querySelectorAll("textarea.secnote"),function(t){ yeslyfBoard.attach(t,t.getAttribute("data-id")); });
      yeslyfBoard.init({page:P.key,apply:applyRemote,who:S.who||"",local:localRows});
    }
    var rv=document.getElementById("reviewer"); if(rv){ rv.innerHTML='<option value="">reviewing as</option>'+IDENTITIES.map(function(n){ return '<option value="'+esc(n)+'">'+esc(n)+'</option>'; }).join("");
      rv.value=S.who||"";
      rv.addEventListener("change",function(){ S.who=IDENTITIES.indexOf(rv.value)>=0?rv.value:""; save(); var n=(window.yeslyfBoard&&S.who)?yeslyfBoard.named(S.who):0;
        flash(S.who?"Reviewing as "+S.who+(n?"; "+n+(n===1?" edit":" edits")+" recorded":""):""); }); }
    paintAll();
    var ex=document.getElementById("export"); if(ex) ex.addEventListener("click",exportMd);
    document.body.addEventListener("input",function(e){ var t=e.target; if(!t||!t.classList||!t.classList.contains("secnote")) return; var id=t.getAttribute("data-id"); if(!id||!byId[id]) return;
      row(id).note=t.value; save(); flash("Saving...");
      clearTimeout(tmr[id]); tmr[id]=setTimeout(function(){ if(put(id,noteVal(id))) flash(); },1500); });
  });
})();
"""


def read(name, problems):
    """data/<name> as JSON, or None with the problem named by its path."""
    try:
        with open(os.path.join(site.DATA, name)) as fh:
            return json.load(fh)
    except (OSError, ValueError) as e:
        problems.append("data/%s is missing or not valid JSON: %s" % (name, e))


def writes_text(writes):
    # "action (event; seat, seat)" per write, joined by "; ": a logic screen's seats, an admin screen's roles, as stored
    return "; ".join("%s (%s; %s)" % (w["action"], w["event"], ", ".join(w.get("seats", w.get("roles", [])))) for w in writes) or "none"


def seat_by_screen(ctx):
    """Every screen of data/logic_screens.json in file order, then M03, M07 and M10 of data/admin_screens.json; one
    column per seat in the A0 order, then the writes (plan section 8 part 4; logic plan, 8 Oct 2026); values as
    stored, a seat an admin screen does not name shown as "-"."""
    admin = {s["id"]: s for s in ctx["admin"]}
    return {"cols": ["Screen"] + SEATS + ["Writes"],
            "rows": [[s["id"]] + [s["role"].get(seat, "-") for seat in SEATS] + [writes_text(s["writes"])]
                     for s in ctx["screens"] + [admin[m] for m in ADMIN_IDS]]}


DERIVED = {"seat_by_screen": seat_by_screen}


def strings(v):
    return isinstance(v, list) and all(isinstance(x, str) for x in v)


def is_link(c):
    return strings(c) and len(c) == 2


def cell_html(c, ctx, where, problems):
    if isinstance(c, str):
        return esc(tokens(c, ctx["integ"]))
    links = [c] if is_link(c) else c
    if isinstance(links, list) and links and all(is_link(x) for x in links):
        return ", ".join('<a href="%s">%s</a>' % (esc(h), esc(tokens(t, ctx["integ"]))) for t, h in links)
    problems.append("%s: cell %s is not a string, a [text, href] or a list of [text, href]" % (where, repr(c)[:100]))
    return ""


def table_html(tb, ctx, where, problems):
    if not (isinstance(tb, dict) and set(tb) <= TABLE_KEYS and strings(tb.get("cols")) and isinstance(tb.get("rows"), list)
            and isinstance(tb.get("title", ""), str)):
        problems.append('%s: a table is {"title": an optional string, "cols": [strings], "rows": [rows]}, got %s' % (where, repr(tb)[:100]))
        return ""
    rows = []
    for r in tb["rows"]:
        if not isinstance(r, list) or len(r) != len(tb["cols"]):
            problems.append("%s: row %s is not a list of %d cells, one per column" % (where, repr(r)[:100], len(tb["cols"])))
            continue
        rows.append([cell_html(c, ctx, where, problems) for c in r])
    title = "<h3>%s</h3>" % esc(tokens(tb["title"], ctx["integ"])) if "title" in tb else ""
    return title + site.table_html([tokens(c, ctx["integ"]) for c in tb["cols"]], rows)


# The parts of a section, drawn in the order their keys stand in it (logic plan, 8 Oct 2026), and the shape of each.
SHAPES = {"lines": "a list of strings", "tables": "a list of tables", "open_items": "a list of distinct ids",
          "derived": "one of: " + ", ".join(DERIVED)}


def part(k, v, ctx, where, problems):
    """One part of a section; a part of the wrong shape is named and draws nothing."""
    if k == "lines" and strings(v):
        return "".join("<p>%s</p>" % esc(tokens(x, ctx["integ"])) for x in v)
    if k == "tables" and isinstance(v, list):
        return "".join(table_html(tb, ctx, where, problems) for tb in v)
    if k == "open_items" and strings(v) and len(set(v)) == len(v):
        gaps = ctx["gaps"]
        problems.extend("%s: open item %r is not in data/logic_gaps.json" % (where, i) for i in v if i not in gaps)
        items = "".join("<li>%s</li>" % esc(tokens("%s %s" % (i, gaps[i]["item"]), ctx["integ"])) for i in v if i in gaps)
        return "<h3>Open items</h3><ul>%s</ul>" % items if v else ""
    if k == "derived" and isinstance(v, str) and v in DERIVED:
        return table_html(DERIVED[v](ctx), ctx, where, problems)
    problems.append("%s: %s %s is not %s" % (where, k, repr(v)[:100], SHAPES[k]))
    return ""


def render_section(sec, key, ctx, problems):
    if not isinstance(sec, dict):
        problems.append("data/%s.json: section %s is not an object" % (key, repr(sec)[:100]))
        return ""
    sid = sec.get("id", "")
    where = "data/%s.json section %r" % (key, sid)
    if not {"id", "heading"} <= set(sec) <= SECTION_KEYS:
        problems.append("%s: keys %s; id and heading are required, the rest from %s" % (where, sorted(sec), sorted(SECTION_KEYS)))
    body = "".join(part(k, v, ctx, where, problems) for k, v in sec.items() if k in SHAPES)
    box = '<textarea class="note secnote" id="note-%s" data-id="%s" placeholder="Comment on this section"></textarea>' % (esc(sid), esc(sid))
    return '<section id="%s"><h2>%s <small><a href="#%s">%s</a></small></h2>%s%s</section>' % (
        esc(sid), esc(tokens(sec.get("heading", ""), ctx["integ"])), esc(sid), esc(sid), body, box)


def build_page(key, doc, ctx, problems):
    sections = doc.get("sections")
    if (set(doc) != FILE_KEYS or doc.get("page") != key or not isinstance(sections, list)
            or not all(isinstance(doc.get(k), str) for k in ("title", "audience"))):
        problems.append("data/%s.json: needs exactly the keys %s: page %r, title and audience strings, a list of sections" % (key, ", ".join(sorted(FILE_KEYS)), key))
        sections = sections if isinstance(sections, list) else []
    ids = [s.get("id") for s in sections if isinstance(s, dict)]
    if not all(isinstance(i, str) and i for i in ids) or len(set(ids)) != len(ids):
        problems.append("data/%s.json: section ids are not unique and non-empty: %s" % (key, ids))
    title, integ = str(doc.get("title", "")), ctx["integ"]
    blob = ('<script>var LOGIC_PAGE=' + site.js_blob({
        "key": key, "exportTitle": "# yeslyf logic panel %s page - review comments" % title,
        "sections": [{"id": s.get("id", ""), "heading": tokens(s.get("heading", ""), integ)} for s in sections if isinstance(s, dict)]}) +
        ';\nvar IDENTITIES=' + site.js_blob(IDENTITIES) + ';</script>\n')
    who = '<div class="who">Reviewing as <select id="reviewer"></select></div>'
    return (site.head("yeslyf logic panel: " + title, site.CSS + site.SUBNAV_CSS + EXTRA_CSS) + '<body>\n' +
            site.header("logic_wireframes.html", title + ": proposed, not yet merged into Wireframes v0.2", who_html=who,
                        export_label="Export comments") +
            site.logic_subnav(key + ".html") + '<div class="banner">%s</div>\n' % esc(BANNER) +
            '<main class="main"><section><h1>%s</h1><p class="lead">%s</p></section>' % (
                esc(tokens(title, integ)), esc(tokens(doc.get("audience", ""), integ))) +
            "".join(render_section(s, key, ctx, problems) for s in sections) + '</main>\n' +
            blob + site.store_script() + '<script>' + JS + '</script>\n</body>\n</html>\n')


def main():
    problems = []
    src = {n: read(n, problems) for n in ("integrations.json", "logic_gaps.json", "logic_screens.json", "admin_screens.json")}
    if problems:
        sys.exit("\n".join("ERROR: " + p for p in problems))
    rows = src["integrations.json"]["rows"]
    ctx = {"integ": {r["id"]: r for r in rows},  # as build_brief.py:716 builds it
           "vendors": [r["vendor"] for r in rows if r["vendor"] and r["vendor"] not in GENERIC_VENDOR_LABELS],
           "gaps": {r["id"]: r for r in src["logic_gaps.json"]["items"]},
           "screens": src["logic_screens.json"]["screens"], "admin": src["admin_screens.json"]["screens"]}
    pages = {}
    for key in PAGES:
        doc = read(key + ".json", problems)
        if not isinstance(doc, dict):
            problems.extend(["data/%s.json is not an object" % key] if doc is not None else [])
            continue
        for txt in all_text(doc):
            problems.extend("data/%s.json: vendor name %r typed in text, write its {I..} token: %r" % (key, v, txt[:70])
                            for v in ctx["vendors"] if v in txt)
            if key == "logic_access":  # section 8: the Access page and its data file carry seat names only
                problems.extend("data/logic_access.json: team name %s in text: %r" % (n, txt[:70])
                                for n in validate_v02.NAMES_UI if validate_v02.word_hit(txt, n))
        name = key + ".html"
        page = build_page(key, doc, ctx, problems)
        try:
            site.check_ascii(name, page)
        except SystemExit as e:
            problems.append(str(e))
        if 'name="robots" content="noindex' not in page:
            problems.append(name + " lacks noindex")
        for word, what in [(w, "contains %r" % w) for w in site.FORBIDDEN] + [("{I", "has an unknown {I..} token left after tokens()")]:
            i = page.find(word)
            while i >= 0:
                problems.append("%s %s: ...%s..." % (name, what, page[max(0, i - 50):i + len(word) + 30].replace("\n", " ")))
                i = page.find(word, i + 1)
        pages[name] = page
    if problems:
        sys.exit("\n".join("ERROR: " + p for p in problems))
    for name, page in pages.items():
        with open(os.path.join(DOCS, name), "w") as fh:
            fh.write(page)
    print("logic pages: %d built" % len(pages))


if __name__ == "__main__":
    main()
