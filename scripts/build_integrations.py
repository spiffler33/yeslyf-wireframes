#!/usr/bin/env python3
"""Generate docs/integrations.html from data/integrations.json (phase 10b; Vatsal, 16 Sep 2026). Never hand-edit docs/.

One row per integration the yeslyf app depends on: vendor, role, the v0.2 screens that need it, whether it gates
launch or only the execution switch, the fallback if it slips, owner, status, dates, docs, cost, notes, cause.
Same tokens and top nav as the other board pages (scripts/build_site.py supplies head(), header() and the CSS).
Owner, status, the three dates, docs_url, cost, notes and the per-row comment are editable in the page: they save
in the browser as typed (localStorage key "yeslyf_integrations_v1") and post to the sheet tab v02_integrations
through the endpoint the board pages share ("yeslyf_board_v1"), with the identity picked in the header and a
timestamp, the same mechanism as the v0.2 comments. Screens, gates, fallback and cause are read-only.

Cross-check (printed as the build log; the mark is written back into data/integrations.json as to_be_verified):
for every row, the live v0.2 screens (data/screens_v02.json, not dropped or split) are searched for the vendor name
as a whole-word phrase, case-insensitive, over every string the screen carries. A screen that names the vendor and
is not in the row's list, or a listed screen ID that is not live in v0.2, marks the row "to be verified: screens".
Rows whose vendor is internal or not decided, and rows whose screens are ["all"], skip the vendor search.

Run after scripts/build_site.py: build_site.py does not know this page yet, so this script also inserts the
Integrations tab into the top nav of docs/index.html (an exact-string insert, idempotent; the build stops if the
anchor string is not found). No other generated page is touched (Vatsal, 16 Sep 2026).
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

PAGE = "integrations.html"
DATA_FILE = os.path.join(DATA, "integrations.json")
IDENTITIES = ["Bhuvanaa", "Harish", "Gaurav", "Kajal", "Somil", "Vatsal", "Spinach", "Compliance"]
STATUSES = ["not started", "in talks", "agreement signed", "sandbox", "production", "dropped"]
GATES = ["launch", "execution switch", "later"]
FIELDS = ["id", "category", "vendor", "alternatives", "role", "screens", "gates", "fallback", "owner", "status",
          "agreement_date", "sandbox_date", "production_date", "docs_url", "cost", "notes", "cause"]
MARK = "to be verified: screens"
NAV_ANCHOR = '<a href="changelog.html">Changelog</a><a href="setup.html">Setup</a>'
NAV_WITH_TAB = '<a href="changelog.html">Changelog</a><a href="integrations.html">Integrations</a><a href="setup.html">Setup</a>'

esc = site.esc


def tabs_with_integrations():
    tabs = []
    for href, label in site.TABS:
        tabs.append((href, label))
        if href == "changelog.html":
            tabs.append((PAGE, "Integrations"))
    return tabs


# ---- cross-check ---------------------------------------------------------------------------------------------------

def tokens(text):
    """Lower-case alphanumeric words of a text; every other character separates words."""
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


def strings_of(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            for s in strings_of(v):
                yield s
    elif isinstance(obj, list):
        for v in obj:
            for s in strings_of(v):
                yield s


def has_phrase(words, phrase):
    n = len(phrase)
    if not n:
        return False
    for i in range(len(words) - n + 1):
        if words[i:i + n] == phrase:
            return True
    return False


def vendor_searchable(vendor):
    v = vendor.strip().lower()
    return bool(v) and not v.startswith("internal") and v != "not decided"


def cross_check(rows, v02):
    """Per row: {"unlisted": [screens naming the vendor, not listed], "missing": [listed ids not live]}."""
    live = site.live_screens(v02)
    live_ids = {s["id"] for s in live}
    words = [(s["id"], tokens(" ".join(strings_of(s)))) for s in live]
    result = {}
    for row in rows:
        listed = row["screens"]
        every = listed == ["all"]
        missing = [sid for sid in listed if sid != "all" and sid not in live_ids]
        unlisted = []
        if not every and vendor_searchable(row["vendor"]):
            phrase = tokens(row["vendor"])
            unlisted = [sid for sid, w in words if has_phrase(w, phrase) and sid not in listed]
        result[row["id"]] = {"unlisted": unlisted, "missing": missing}
    return result, live_ids


# ---- validation ----------------------------------------------------------------------------------------------------

def validate(rows):
    problems = []
    seen = set()
    for i, row in enumerate(rows):
        rid = row.get("id", "")
        for f in FIELDS:
            if f not in row:
                problems.append("%s: missing field %s" % (rid or ("row %d" % i), f))
        if not (len(rid) == 3 and rid[0] == "I" and rid[1:].isdigit()):
            problems.append("row %d: id %r is not I plus two digits" % (i, rid))
        if rid in seen:
            problems.append("%s: duplicate id" % rid)
        seen.add(rid)
        if row.get("status") not in STATUSES:
            problems.append("%s: status %r is not one of %s" % (rid, row.get("status"), ", ".join(STATUSES)))
        if row.get("gates") not in GATES and not (row.get("gates") == "" and row.get("status") == "dropped"):
            problems.append("%s: gates %r is not one of %s" % (rid, row.get("gates"), ", ".join(GATES)))
        if not isinstance(row.get("screens"), list) or not all(isinstance(s, str) for s in row.get("screens", [])):
            problems.append("%s: screens must be a list of screen IDs" % rid)
        for f in ("vendor", "role", "owner", "cause", "category"):
            if not str(row.get(f, "")).strip():
                problems.append("%s: %s is empty" % (rid, f))
        for f in ("agreement_date", "sandbox_date", "production_date"):
            d = str(row.get(f, ""))
            if d and not (len(d) == 10 and d[4] == "-" and d[7] == "-" and d.replace("-", "").isdigit()):
                problems.append("%s: %s %r is not yyyy-mm-dd" % (rid, f, d))
    return problems


# ---- page ----------------------------------------------------------------------------------------------------------

EXTRA_CSS = """
  .who select{padding:6px 8px;border:1px solid var(--line);border-radius:6px;background:#fff;max-width:170px}
  th[data-sort]{cursor:pointer;white-space:nowrap} th .dir{color:var(--mute);font-weight:400;font-size:10px}
  th.c-id{width:44px} th.c-vendor{min-width:150px} th.c-gates{width:110px} th.c-owner{min-width:130px} th.c-status{min-width:140px} th.c-date{width:140px} th.c-cost{min-width:150px}
  tbody.hidden{display:none} tbody.hi td{background:var(--accent-soft)}
  tr.r1 td{border-bottom:0;padding-bottom:4px} tr.r2 td{padding-top:0}
  td input,td select,td textarea{width:100%;padding:4px 6px;border:1px solid var(--line);border-radius:5px;background:#fff;font-size:12px}
  td textarea{min-height:36px;resize:vertical} td input[type=date]{min-width:128px}
  td.v b{font-size:13px}
  .det{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:6px 14px;font-size:12px;color:#3B4250;padding:2px 0 6px}
  .det b{display:block;font-size:11px;color:var(--mute);font-weight:600;margin-bottom:2px}
  .det .sid{font-size:11px;margin-right:3px}
  .det .meta{margin-top:3px}
  .tag.tbv{border-color:#C9A800;background:var(--accent-soft);color:var(--ink)}
  #pole a{font-weight:600}
"""

JS = r"""
(function(){
  var KEY="yeslyf_integrations_v1", BOARD_KEY="yeslyf_board_v1";
  var COLS=["ts","who","id","vendor","field","value"];
  var RANK={}; STATUSES.forEach(function(s,i){ RANK[s]=i; });
  var byId={}; ROWS.forEach(function(r){ byId[r.id]=r; });
  var S={};
  try{ S=JSON.parse(localStorage.getItem(KEY)||"{}")||{}; }catch(e){ S={}; }
  if(!S.rows) S.rows={}; if(!S.who) S.who="";
  function save(){ try{ localStorage.setItem(KEY, JSON.stringify(S)); }catch(e){} }
  function board(){ try{ return JSON.parse(localStorage.getItem(BOARD_KEY)||"{}")||{}; }catch(e){ return {}; } }
  function endpoint(){ return String(board().endpoint||"").trim(); }
  function captureEndpoint(){ try{ var q=location.search||""; var qi=q.indexOf("endpoint="); if(qi<0) return; var qv=decodeURIComponent(q.slice(qi+9).split("&")[0]).trim();
    if(qv){ var b=board(); b.endpoint=qv; try{ localStorage.setItem(BOARD_KEY, JSON.stringify(b)); }catch(e){} } if(history.replaceState) history.replaceState(null,"",location.pathname+location.hash); }catch(e){} }
  function pill(){ var p=document.getElementById("sheetpill"); if(!p) return; var on=!!endpoint(); p.textContent=on?"sheet: on":"sheet: off"; p.className="pill"+(on?" on":""); }
  var ft; function flash(t){ var s=document.getElementById("saved"); if(!s) return; s.textContent=t||"Saved in this browser"; clearTimeout(ft); ft=setTimeout(function(){ s.textContent=""; },1800); }
  function esc(s){ return String(s===undefined||s===null?"":s).split("&").join("&amp;").split("<").join("&lt;").split(">").join("&gt;").split('"').join("&quot;"); }
  function edits(id){ if(!S.rows[id]) S.rows[id]={}; return S.rows[id]; }
  function val(id,f){ var e=S.rows[id]||{}; if(e[f]!==undefined) return e[f]; var r=byId[id]; return (r&&r[f]!==undefined)?r[f]:""; }
  function post(id,field,value){ var ep=endpoint(); if(!ep) return false;
    var row={kind:"v02_integrations",tab:"v02_integrations",cols:COLS,ts:new Date().toISOString(),who:S.who||"",id:id,vendor:byId[id].vendor,field:field,value:String(value===undefined||value===null?"":value)};
    try{ fetch(ep,{method:"POST",mode:"no-cors",headers:{"Content-Type":"text/plain"},body:JSON.stringify(row)}); }catch(e){} return true; }
  function ownersOf(text){ var t=String(text||""), parts=[], cur="", out=[];
    for(var i=0;i<t.length;i++){ var ch=t.charAt(i); var ok=(ch>="a"&&ch<="z")||(ch>="A"&&ch<="Z")||(ch>="0"&&ch<="9"); if(ok) cur+=ch; else { if(cur) parts.push(cur); cur=""; } }
    if(cur) parts.push(cur); parts.forEach(function(p){ if(IDENTITIES.indexOf(p)>=0&&out.indexOf(p)<0) out.push(p); }); return out; }
  function longPole(){ return ROWS.filter(function(r){ var st=val(r.id,"status"); return r.gates==="launch" && st!=="dropped" && (RANK[st]||0) < RANK["sandbox"]; }); }
  function paintStats(){ var counts={}; STATUSES.forEach(function(s){ counts[s]=0; }); ROWS.forEach(function(r){ var st=val(r.id,"status"); counts[st]=(counts[st]||0)+1; });
    var st=document.getElementById("stats"); if(st) st.innerHTML='<div class="stat"><b>'+ROWS.length+'</b><span>integrations</span></div>'+STATUSES.map(function(s){ return '<div class="stat"><b>'+counts[s]+'</b><span>'+esc(s)+'</span></div>'; }).join("");
    var lp=longPole(); var p=document.getElementById("pole");
    if(p) p.innerHTML='<b>Long pole</b> (gates launch and below sandbox), '+lp.length+' of '+ROWS.length+': '+(lp.length?lp.map(function(r){ return '<a href="#row/'+esc(r.id)+'">'+esc(r.id)+' '+esc(r.vendor)+'</a> ('+esc(val(r.id,"status"))+')'; }).join(", "):"none")+'.'; }
  function paintRow(id){ var tb=document.getElementById("row-"+id); if(!tb) return; var f=tb.querySelectorAll("[data-f]");
    for(var i=0;i<f.length;i++){ var k=f[i].getAttribute("data-f"); var v=val(id,k); if(f[i].value!==v) f[i].value=v; }
    var link=tb.querySelector("a[data-docs]"); if(link){ var u=String(val(id,"docs_url")||"").trim(); if(u){ link.href=u; link.style.display=""; } else { link.style.display="none"; link.removeAttribute("href"); } }
    var w=tb.querySelector("[data-cwho]"); if(w){ var cw=(S.rows[id]||{}).comment_who||""; w.textContent=cw?("by "+cw):""; }
    tb.setAttribute("data-owners", ownersOf(val(id,"owner")).join(" ")); tb.setAttribute("data-status", val(id,"status")); }
  function ownerOptions(){ var seen=[]; ROWS.forEach(function(r){ ownersOf(val(r.id,"owner")).forEach(function(n){ if(seen.indexOf(n)<0) seen.push(n); }); }); return IDENTITIES.filter(function(n){ return seen.indexOf(n)>=0; }); }
  function applyFilters(){ var f=document.getElementById("filters"); if(!f) return; var g=f.querySelector("[name=gates]").value, o=f.querySelector("[name=owner]").value, s=f.querySelector("[name=status]").value; var shown=0;
    ROWS.forEach(function(r){ var tb=document.getElementById("row-"+r.id); if(!tb) return;
      var ok=(g==="All"||r.gates===g)&&(o==="All"||(" "+tb.getAttribute("data-owners")+" ").indexOf(" "+o+" ")>=0)&&(s==="All"||val(r.id,"status")===s);
      tb.className=(ok?"":"hidden")+(tb.className.indexOf("hi")>=0?" hi":""); if(ok) shown++; });
    var c=document.getElementById("count"); if(c) c.textContent=shown+" of "+ROWS.length+" rows"; }
  function paintAll(){ ROWS.forEach(function(r){ paintRow(r.id); }); var rv=document.getElementById("reviewer"); if(rv&&rv.value!==(S.who||"")) rv.value=S.who||""; pill(); paintStats(); applyFilters(); }
  var sort={key:"id",dir:1};
  function keyOf(r,k){ if(k==="vendor") return String(r.vendor).toLowerCase(); if(k==="gates") return String(GATES.indexOf(r.gates));
    if(k==="status"){ var n=RANK[val(r.id,"status")]; return String(n===undefined?9:n); } if(k==="owner") return String(val(r.id,"owner")).toLowerCase();
    if(k==="agreement_date"||k==="sandbox_date"||k==="production_date"){ var d=String(val(r.id,k)); return d?d:"9999-99-99"; } if(k==="cost") return String(val(r.id,"cost")).toLowerCase(); return r.id; }
  function sortBy(k){ if(sort.key===k) sort.dir=-sort.dir; else { sort.key=k; sort.dir=1; } var tbl=document.getElementById("tbl"); if(!tbl) return;
    var list=ROWS.slice().sort(function(a,b){ var x=keyOf(a,k), y=keyOf(b,k); if(x<y) return -sort.dir; if(x>y) return sort.dir; return a.id<b.id?-1:(a.id>b.id?1:0); });
    list.forEach(function(r){ var tb=document.getElementById("row-"+r.id); if(tb) tbl.appendChild(tb); });
    var ths=tbl.querySelectorAll("th[data-sort]"); for(var i=0;i<ths.length;i++){ var d=ths[i].querySelector(".dir"); if(d) d.textContent=ths[i].getAttribute("data-sort")===sort.key?(sort.dir>0?" \u25B2":" \u25BC"):""; } }
  function cellmd(v){ return String(v===undefined||v===null?"":v).split("\n").join(" ").split("|").join("\\|"); }
  function md(){ var lp=longPole(); var counts={}; STATUSES.forEach(function(s){ counts[s]=0; }); ROWS.forEach(function(r){ var st=val(r.id,"status"); counts[st]=(counts[st]||0)+1; });
    var L=["# yeslyf integrations v0.2 - brief for Spinach","Exported "+new Date().toLocaleString()+(S.who?" by "+S.who:""),"Sheet endpoint: "+(endpoint()?"configured":"not configured; this file is the record"),
      "Rows: "+ROWS.length+"; by status: "+STATUSES.map(function(s){ return s+" "+counts[s]; }).join(", "),
      "Long pole (gates launch and below sandbox): "+(lp.length?lp.map(function(r){ return r.id+" "+r.vendor; }).join(", "):"none"),""];
    var cols=["ID","Category","Vendor","Alternatives","Role","Screens","Gates","Fallback","Owner","Status","Agreement","Sandbox","Production","Docs","Cost","Notes","Cause","Comment"];
    L.push("| "+cols.join(" | ")+" |"); L.push("|"+cols.map(function(){ return " --- |"; }).join(""));
    ROWS.forEach(function(r){ var e=S.rows[r.id]||{}; var scr=r.screens.length?(r.screens[0]==="all"?"all screens":r.screens.join(" ")):"-"; var cm=val(r.id,"comment"); if(cm&&e.comment_who) cm+=" ("+e.comment_who+")";
      var cells=[r.id,r.category,r.vendor,r.alternatives||"-",r.role,scr+(r.to_be_verified?" ("+r.to_be_verified+")":""),r.gates||"-",r.fallback||"-",val(r.id,"owner"),val(r.id,"status"),
        val(r.id,"agreement_date")||"-",val(r.id,"sandbox_date")||"-",val(r.id,"production_date")||"-",val(r.id,"docs_url")||"-",val(r.id,"cost")||"-",val(r.id,"notes")||"-",r.cause,cm||"-"];
      L.push("| "+cells.map(cellmd).join(" | ")+" |"); });
    return L.join("\n"); }
  function exportBrief(){ var text=md(); try{ navigator.clipboard&&navigator.clipboard.writeText(text); }catch(e){}
    try{ var b=new Blob([text],{type:"text/markdown"}); var a=document.createElement("a"); a.href=URL.createObjectURL(b); a.download="yeslyf_integrations_v02.md"; document.body.appendChild(a); a.click(); document.body.removeChild(a); }catch(e){}
    flash("Brief exported and copied"); }
  function deepLink(){ var h=location.hash||""; if(h.indexOf("#row/")!==0) return; var el=document.getElementById("row-"+h.slice(5)); if(!el) return;
    var old=document.querySelectorAll(".hi"); for(var i=0;i<old.length;i++) old[i].classList.remove("hi"); el.classList.add("hi"); try{ el.scrollIntoView({block:"start",behavior:"instant"}); }catch(e){ el.scrollIntoView(true); } }
  var tmr={};
  document.addEventListener("DOMContentLoaded",function(){
    captureEndpoint();
    var f=document.getElementById("filters"); if(f){ var os=f.querySelector("[name=owner]"); if(os) os.innerHTML='<option>All</option>'+ownerOptions().map(function(n){ return '<option>'+esc(n)+'</option>'; }).join(""); f.addEventListener("change",applyFilters); }
    var rv=document.getElementById("reviewer"); if(rv){ rv.innerHTML='<option value="">editing as</option>'+IDENTITIES.map(function(n){ return '<option value="'+esc(n)+'">'+esc(n)+'</option>'; }).join(""); rv.value=S.who||"";
      rv.addEventListener("change",function(){ S.who=IDENTITIES.indexOf(rv.value)>=0?rv.value:""; save(); flash(S.who?"Editing as "+S.who:""); }); }
    paintAll(); deepLink(); window.addEventListener("hashchange",deepLink);
    var ex=document.getElementById("export"); if(ex) ex.addEventListener("click",exportBrief);
    var tbl=document.getElementById("tbl"); if(tbl) tbl.addEventListener("click",function(e){ var th=e.target.closest?e.target.closest("th[data-sort]"):null; if(!th) return; sortBy(th.getAttribute("data-sort")); });
    document.body.addEventListener("input",function(e){ var t=e.target; var id=t.getAttribute("data-id"), k=t.getAttribute("data-f"); if(!id||!k) return; if(t.tagName==="SELECT"||t.type==="date") return;
      var ed=edits(id); ed[k]=t.value; if(k==="comment") ed.comment_who=S.who||""; save(); paintRow(id); if(k==="owner") applyFilters(); flash("Saving...");
      clearTimeout(tmr[id+k]); tmr[id+k]=setTimeout(function(){ post(id,k,val(id,k)); flash(); },1500); });
    document.body.addEventListener("change",function(e){ var t=e.target; var id=t.getAttribute("data-id"), k=t.getAttribute("data-f"); if(!id||!k) return; if(!(t.tagName==="SELECT"||t.type==="date")) return;
      var ed=edits(id); ed[k]=t.value; save(); paintRow(id); paintStats(); applyFilters(); post(id,k,t.value); flash(); });
  });
  // test hook for the checks (and for the console)
  window.yeslyfIntegrations={ exportText: md, longPole: function(){ return longPole().map(function(r){ return r.id; }); }, sortBy: sortBy, value: val, rows: function(){ return ROWS.length; } };
})();
"""


def control(row, field, kind):
    rid = esc(row["id"])
    v = esc(row.get(field, ""))
    if kind == "select":
        return '<select data-id="%s" data-f="%s">%s</select>' % (rid, field, "".join(
            '<option value="%s"%s>%s</option>' % (esc(s), " selected" if s == row.get(field) else "", esc(s)) for s in STATUSES))
    if kind == "date":
        return '<input type="date" data-id="%s" data-f="%s" value="%s">' % (rid, field, v)
    if kind == "textarea":
        return '<textarea data-id="%s" data-f="%s">%s</textarea>' % (rid, field, v)
    return '<input data-id="%s" data-f="%s" value="%s" placeholder="%s">' % (rid, field, v, esc(kind))


def screens_cell(row, check, live_ids):
    listed = row["screens"]
    if listed == ["all"]:
        body = "all screens"
    elif not listed:
        body = "-"
    else:
        body = "".join(site.sid_link(s, live_ids) for s in listed)
    if row.get("to_be_verified"):
        body += ' <span class="tag tbv">%s</span>' % esc(row["to_be_verified"])
    if check["unlisted"]:
        body += '<div class="meta">names the vendor, not listed: %s</div>' % " ".join(site.sid_link(s, live_ids) for s in check["unlisted"])
    if check["missing"]:
        body += '<div class="meta">not live in v0.2: %s</div>' % esc(", ".join(check["missing"]))
    return body


def render_row(row, check, live_ids):
    rid = esc(row["id"])
    h = ['<tbody id="row-%s" data-id="%s">' % (rid, rid)]
    h.append('<tr class="r1"><td class="n">%s</td><td class="v"><b>%s</b><div class="meta">%s</div></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
        rid, esc(row["vendor"]), esc(row["category"]), esc(row["gates"] or "-"),
        control(row, "owner", "first name"), control(row, "status", "select"),
        control(row, "agreement_date", "date"), control(row, "sandbox_date", "date"), control(row, "production_date", "date"),
        control(row, "cost", "free, or paid with the model")))
    det = ['<div><b>Role</b>%s</div>' % esc(row["role"])]
    det.append('<div><b>If it slips</b>%s</div>' % esc(row["fallback"] or "-"))
    det.append('<div><b>Screens</b>%s</div>' % screens_cell(row, check, live_ids))
    det.append('<div><b>Alternatives</b>%s</div>' % esc(row["alternatives"] or "-"))
    det.append('<div><b>Docs</b>%s<a data-docs target="_blank" rel="noopener" style="display:none;font-size:11px">open</a></div>' % control(row, "docs_url", "https://..."))
    det.append('<div><b>Notes</b>%s</div>' % control(row, "notes", "textarea"))
    det.append('<div><b>Cause</b><span class="cause">%s</span></div>' % esc(row["cause"]))
    det.append('<div><b>Comment</b>%s<span class="meta" data-cwho></span></div>' % control(row, "comment", "textarea"))
    h.append('<tr class="r2"><td colspan="9"><div class="det">%s</div></td></tr></tbody>' % "".join(det))
    return "\n".join(h)


def build_page(rows, checks, live_ids):
    n = len(rows)
    who = '<div class="who">Editing as <select id="reviewer"></select></div>'
    filters = ('<div class="filters" id="filters"><label>Gates <select name="gates"><option>All</option>%s</select></label>'
               '<label>Owner <select name="owner"><option>All</option></select></label>'
               '<label>Status <select name="status"><option>All</option>%s</select></label>'
               '<span id="count" class="meta"></span><span class="meta">Click a column header to sort.</span></div>' % (
                   "".join("<option>%s</option>" % esc(g) for g in GATES), "".join("<option>%s</option>" % esc(s) for s in STATUSES)))
    intro = ('<section><h1>Integrations: vendors, owners, dates and fallbacks</h1>'
             '<p class="lead">One row per integration the app depends on: what it does, the v0.2 screens that need it, whether it gates launch, '
             'the execution switch or comes later, and what happens if it slips. Owner, status, the three dates, docs, cost, notes and the comment are '
             'editable here: they save in this browser as typed and write to the v02_integrations sheet tab when the endpoint is set, with the name '
             'picked at the top. Screens, gates, fallback and cause come from the data file. Export brief downloads the table as markdown for Spinach.</p>'
             '<p class="meta">Source: data/integrations.json, cause on every row. Status starts at "not started" on every row until its owner sets it. '
             '"to be verified: screens" marks a row where the v0.2 screens name the vendor on a screen the row does not list, or the row lists a screen '
             'that is not live in v0.2.</p><div class="stats" id="stats"></div><div class="rule" id="pole"></div></section>')
    thead = ('<thead><tr><th class="c-id" data-sort="id">ID<span class="dir"></span></th><th class="c-vendor" data-sort="vendor">Vendor<span class="dir"></span></th>'
             '<th class="c-gates" data-sort="gates">Gates<span class="dir"></span></th><th class="c-owner" data-sort="owner">Owner<span class="dir"></span></th>'
             '<th class="c-status" data-sort="status">Status<span class="dir"></span></th><th class="c-date" data-sort="agreement_date">Agreement<span class="dir"></span></th>'
             '<th class="c-date" data-sort="sandbox_date">Sandbox<span class="dir"></span></th><th class="c-date" data-sort="production_date">Production<span class="dir"></span></th>'
             '<th class="c-cost" data-sort="cost">Cost<span class="dir"></span></th></tr></thead>')
    table = '<div class="wrap"><table id="tbl">' + thead + "\n".join(render_row(r, checks[r["id"]], live_ids) for r in rows) + '</table></div>'
    blob = ('<script>var ROWS=' + site.js_blob(rows) + ';\nvar IDENTITIES=' + site.js_blob(IDENTITIES) + ';\nvar STATUSES=' + site.js_blob(STATUSES) +
            ';\nvar GATES=' + site.js_blob(GATES) + ';</script>\n')
    return (site.head("yeslyf integrations v0.2", site.CSS + EXTRA_CSS) + '<body>\n' +
            site.header(PAGE, "integrations, %d rows" % n, who_html=who, export_label="Export brief", tabs=tabs_with_integrations()) +
            '<main class="main" style="max-width:none">' + intro + '<section>' + filters + table + '</section></main>\n' +
            blob + '<script>' + JS + '</script>\n</body>\n</html>\n')


def patch_index_nav():
    path = os.path.join(DOCS, "index.html")
    with open(path) as fh:
        text = fh.read()
    if 'href="integrations.html"' in text:
        return "docs/index.html: Integrations tab already in the top nav"
    if text.count(NAV_ANCHOR) != 1:
        raise SystemExit("docs/index.html: the nav anchor %r was not found exactly once; nothing written" % NAV_ANCHOR)
    with open(path, "w") as fh:
        fh.write(text.replace(NAV_ANCHOR, NAV_WITH_TAB))
    return "docs/index.html: Integrations tab inserted in the top nav (one line)"


def main():
    with open(DATA_FILE) as fh:
        raw = fh.read()
    site.check_ascii("data/integrations.json", raw)
    data = json.loads(raw)
    rows = data["rows"]
    problems = validate(rows)
    if problems:
        for p in problems:
            print("ERROR: " + p)
        sys.exit(1)
    v02 = site.load("screens_v02.json")
    checks, live_ids = cross_check(rows, v02)

    marked = 0
    changed = False
    for row in rows:
        c = checks[row["id"]]
        mark = MARK if (c["unlisted"] or c["missing"]) else ""
        if c["unlisted"]:
            print("cross-check: %s %s names the vendor on screens the row does not list: %s" % (row["id"], row["vendor"], ", ".join(c["unlisted"])))
        if c["missing"]:
            print("cross-check: %s %s lists screens that are not live in v0.2: %s" % (row["id"], row["vendor"], ", ".join(c["missing"])))
        if row.get("to_be_verified", "") != mark:
            row["to_be_verified"] = mark
            changed = True
        marked += 1 if mark else 0
    print("cross-check: %d rows, %d marked %r, %d clean" % (len(rows), marked, MARK, len(rows) - marked))
    if changed:
        with open(DATA_FILE, "w") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=True)
            fh.write("\n")
        print("wrote data/integrations.json (to_be_verified marks updated)")

    page = build_page(rows, checks, live_ids)
    site.check_ascii(PAGE, page)
    errors = []
    if 'name="robots" content="noindex' not in page:
        errors.append(PAGE + " lacks noindex")
    for word in site.FORBIDDEN:
        i = page.find(word)
        while i >= 0:
            errors.append("%s contains %r: ...%s..." % (PAGE, word, page[max(0, i - 50):i + len(word) + 30].replace("\n", " ")))
            i = page.find(word, i + 1)
    if errors:
        for e in errors:
            print("ERROR: " + e)
        sys.exit(1)
    with open(os.path.join(DOCS, PAGE), "w") as fh:
        fh.write(page)
    print("wrote docs/%s (%d bytes, %d rows)" % (PAGE, len(page), len(rows)))
    print(patch_index_nav())


if __name__ == "__main__":
    main()
