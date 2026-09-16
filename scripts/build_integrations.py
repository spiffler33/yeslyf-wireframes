#!/usr/bin/env python3
"""Generate docs/integrations.html from data/integrations.json (phase 10b; Vatsal, 16 Sep 2026). Never hand-edit docs/.

One row per integration the yeslyf app depends on: vendor, role, the v0.2 screens that need it, whether it gates
launch or only the execution switch, the fallback if it slips, owner, status, dates, docs, cost, notes, cause.
Same tokens and top nav as the other board pages (scripts/build_site.py supplies head(), header() and the CSS).
The list is one compact line per integration (sortable, filterable); a click opens the row's panel with the facts
on the left and the editable fields on the right. Owner, status, the three dates, docs_url, cost, notes and the
per-row comment save in the browser as typed (localStorage key "yeslyf_integrations_v1") and post to the sheet tab
v02_integrations through the endpoint the board pages share ("yeslyf_board_v1"), with the identity picked in the
header and a timestamp, the same mechanism as the v0.2 comments. Screens, gates, fallback and cause are read-only.

Cross-check (printed as the build log; the mark is written back into data/integrations.json as to_be_verified):
for every row, the live v0.2 screens (data/screens_v02.json, not dropped or split) are searched for the vendor name
as a whole-word phrase, case-insensitive, over every string the screen carries. A screen that names the vendor and
is not in the row's list, or a listed screen ID that is not live in v0.2, marks the row "to be verified: screens".
Rows whose vendor is internal or not decided, and rows whose screens are ["all"], skip the vendor search.

Called at the end of scripts/build_site.py (whose TABS and REVIEW_TABS carry the Integrations tab); also runs on
its own. Writes docs/integrations.html and its review copy docs/review/integrations.html (the three review tabs, no
setup link, screen links into the review copy of Wireframes v0.2; Vatsal, 16 Sep 2026).
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

esc = site.esc


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
  .lead{margin-bottom:8px}
  .counts,.pole{display:flex;flex-wrap:wrap;gap:4px 6px;align-items:center;font-size:12px;margin:8px 0 0}
  .counts .k,.pole .k{color:var(--mute);margin-right:4px}
  .pole .k b{color:var(--ink)}
  .chip{display:inline-block;border:1px solid var(--line);border-radius:4px;padding:1px 7px;background:#fff;color:var(--ink);white-space:nowrap;font:inherit;font-size:12px;text-decoration:none;cursor:pointer;font-variant-numeric:tabular-nums}
  .chip b{font-weight:600}
  .chip.on{background:var(--ink);color:#fff;border-color:var(--ink)}
  .chip.static{cursor:default}
  .toolbar{display:flex;gap:6px 12px;flex-wrap:wrap;align-items:center;margin:0 0 10px;font-size:12px}
  .toolbar label{display:flex;gap:5px;align-items:center;white-space:nowrap}
  .toolbar select{padding:5px;border:1px solid var(--line);border-radius:5px;background:#fff}
  .toolbar .sp{flex:1}
  .toolbar button{border:0;background:none;color:var(--mute);text-decoration:underline;cursor:pointer;padding:0;font-size:12px}
  th[data-sort]{cursor:pointer;white-space:nowrap;user-select:none} th .dir{color:var(--mute);font-weight:400;font-size:10px}
  th.c-id{width:44px} th.c-tg{width:22px}
  tr.r1 td{font-variant-numeric:tabular-nums;padding:7px 8px}
  tr.r1{cursor:pointer} tr.r1:hover td{background:#F5F6F8}
  td.v b{font-size:13px} td.v .meta{font-size:11.5px;margin-top:1px}
  td.tg{color:var(--mute);text-align:center;font-size:11px} td.tg:before{content:"\\25B8"} tbody.open td.tg:before{content:"\\25BE"}
  td.dt{white-space:nowrap} td.dt.empty{color:var(--mute)}
  tbody.hidden{display:none} tbody.hi tr.r1 td{background:var(--accent-soft)}
  tr.r2{display:none} tbody.open tr.r2{display:table-row} tbody.open tr.r1 td{border-bottom:0}
  tr.r2 td{padding:2px 8px 14px 52px;background:#FCFCFD}
  .panel{display:grid;grid-template-columns:minmax(0,3fr) minmax(0,2fr);gap:4px 32px;font-size:12.5px;line-height:1.5}
  .panel .f{margin:0 0 8px;max-width:640px} .panel .f b{display:block;font-size:11px;color:var(--mute);font-weight:600;margin-bottom:2px}
  .panel .chips{display:flex;flex-wrap:wrap;gap:3px} .panel .chips .sid{font-size:11px}
  .panel .verify{margin-top:4px}
  .form{display:grid;grid-template-columns:88px minmax(0,1fr);gap:6px 8px;align-items:center}
  .form label{font-size:11px;color:var(--mute)}
  .form input,.form select,.form textarea{width:100%;padding:4px 6px;border:1px solid var(--line);border-radius:5px;background:#fff;font-size:12px}
  .form textarea{min-height:38px;resize:vertical}
  .form .docs{display:flex;gap:6px;align-items:center} .form .docs a{font-size:11px;white-space:nowrap}
  .form .cw{grid-column:2;font-size:11px;color:var(--mute);min-height:12px}
  .tag.tbv{border-color:#C9A800;background:var(--accent-soft);color:var(--ink)}
  .tag.st-sandbox{border-color:#C9A800;background:var(--accent-soft);color:var(--ink)}
  .tag.st-production{background:var(--ink);color:#fff;border-color:var(--ink)}
  .tag.st-dropped{text-decoration:line-through}
  @media (max-width:760px){ th.c-gates,td.c-gates,th.c-date,td.c-date{display:none} .panel{grid-template-columns:1fr} tr.r2 td{padding-left:8px} }
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
  function slug(s){ return String(s||"").split(" ").join("-"); }
  function edits(id){ if(!S.rows[id]) S.rows[id]={}; return S.rows[id]; }
  function val(id,f){ var e=S.rows[id]||{}; if(e[f]!==undefined) return e[f]; var r=byId[id]; return (r&&r[f]!==undefined)?r[f]:""; }
  function post(id,field,value){ var ep=endpoint(); if(!ep) return false;
    var row={kind:"v02_integrations",tab:"v02_integrations",cols:COLS,ts:new Date().toISOString(),who:S.who||"",id:id,vendor:byId[id].vendor,field:field,value:String(value===undefined||value===null?"":value)};
    try{ fetch(ep,{method:"POST",mode:"no-cors",headers:{"Content-Type":"text/plain"},body:JSON.stringify(row)}); }catch(e){} return true; }
  function ownersOf(text){ var out=[]; String(text||"").split(",").forEach(function(p){ p=p.trim(); if(p&&out.indexOf(p)<0) out.push(p); }); return out; }
  function longPole(){ return ROWS.filter(function(r){ var st=val(r.id,"status"); return r.gates==="launch" && st!=="dropped" && (RANK[st]||0) < RANK["sandbox"]; }); }
  function filterStatus(){ var f=document.getElementById("filters"); return f?f.querySelector("[name=status]").value:"All"; }
  function paintCounts(){ var counts={}; STATUSES.forEach(function(s){ counts[s]=0; }); ROWS.forEach(function(r){ var st=val(r.id,"status"); counts[st]=(counts[st]||0)+1; });
    var cur=filterStatus(); var c=document.getElementById("counts");
    if(c) c.innerHTML='<span class="k">'+ROWS.length+' integrations</span>'+STATUSES.map(function(s){ return '<button class="chip'+(cur===s?' on':'')+'" data-status="'+esc(s)+'"><b>'+counts[s]+'</b> '+esc(s)+'</button>'; }).join("");
    var lp=longPole(); var p=document.getElementById("pole");
    if(p) p.innerHTML='<span class="k"><b>Long pole</b> '+lp.length+' of '+ROWS.length+', gates launch and below sandbox</span>'+(lp.length?lp.map(function(r){ return '<a class="chip" href="#row/'+esc(r.id)+'">'+esc(r.id)+' '+esc(r.vendor)+'</a>'; }).join(""):'<span class="k">none</span>'); }
  function paintRow(id){ var tb=document.getElementById("row-"+id); if(!tb) return;
    var f=tb.querySelectorAll("[data-f]"); for(var i=0;i<f.length;i++){ var k=f[i].getAttribute("data-f"); var v=val(id,k); if(f[i].value!==v) f[i].value=v; }
    var sh=tb.querySelectorAll("[data-show]"); for(var j=0;j<sh.length;j++){ var key=sh[j].getAttribute("data-show"); var t=String(val(id,key)||""); sh[j].textContent=t||"-";
      if(key==="status") sh[j].className="tag st-"+slug(t); if(sh[j].className.indexOf("dt")>=0) sh[j].className="dt"+(t?"":" empty"); }
    var link=tb.querySelector("a[data-docs]"); if(link){ var u=String(val(id,"docs_url")||"").trim(); if(u){ link.href=u; link.style.display=""; } else { link.style.display="none"; link.removeAttribute("href"); } }
    var w=tb.querySelector("[data-cwho]"); if(w){ var cw=(S.rows[id]||{}).comment_who||""; w.textContent=cw?("by "+cw):""; }
    tb.setAttribute("data-owners", ownersOf(val(id,"owner")).join("|")); tb.setAttribute("data-status", val(id,"status")); }
  function ownerOptions(){ var seen=[]; ROWS.forEach(function(r){ ownersOf(val(r.id,"owner")).forEach(function(n){ if(seen.indexOf(n)<0) seen.push(n); }); }); return seen.sort(); }
  function applyFilters(){ var f=document.getElementById("filters"); if(!f) return; var g=f.querySelector("[name=gates]").value, o=f.querySelector("[name=owner]").value, s=f.querySelector("[name=status]").value; var shown=0;
    ROWS.forEach(function(r){ var tb=document.getElementById("row-"+r.id); if(!tb) return;
      var ok=(g==="All"||r.gates===g)&&(o==="All"||("|"+tb.getAttribute("data-owners")+"|").indexOf("|"+o+"|")>=0)&&(s==="All"||val(r.id,"status")===s);
      tb.classList.toggle("hidden",!ok); if(ok) shown++; });
    var c=document.getElementById("count"); if(c) c.textContent=shown+" of "+ROWS.length; paintCounts(); }
  function paintAll(){ ROWS.forEach(function(r){ paintRow(r.id); }); var rv=document.getElementById("reviewer"); if(rv&&rv.value!==(S.who||"")) rv.value=S.who||""; pill(); applyFilters(); }
  var sort={key:"id",dir:1};
  function keyOf(r,k){ if(k==="vendor") return String(r.vendor).toLowerCase(); if(k==="gates") return String(GATES.indexOf(r.gates));
    if(k==="status"){ var n=RANK[val(r.id,"status")]; return String(n===undefined?9:n); } if(k==="owner") return String(val(r.id,"owner")).toLowerCase();
    if(k==="sandbox_date"||k==="production_date"||k==="agreement_date"){ var d=String(val(r.id,k)); return d?d:"9999-99-99"; } return r.id; }
  function sortBy(k){ if(sort.key===k) sort.dir=-sort.dir; else { sort.key=k; sort.dir=1; } var tbl=document.getElementById("tbl"); if(!tbl) return;
    var list=ROWS.slice().sort(function(a,b){ var x=keyOf(a,k), y=keyOf(b,k); if(x<y) return -sort.dir; if(x>y) return sort.dir; return a.id<b.id?-1:(a.id>b.id?1:0); });
    list.forEach(function(r){ var tb=document.getElementById("row-"+r.id); if(tb) tbl.appendChild(tb); });
    var ths=tbl.querySelectorAll("th[data-sort]"); for(var i=0;i<ths.length;i++){ var d=ths[i].querySelector(".dir"); if(d) d.textContent=ths[i].getAttribute("data-sort")===sort.key?(sort.dir>0?" \u25B2":" \u25BC"):""; } }
  function openRow(id,on){ var tb=document.getElementById("row-"+id); if(tb) tb.classList.toggle("open",on); }
  function openAll(on){ ROWS.forEach(function(r){ var tb=document.getElementById("row-"+r.id); if(tb&&!tb.classList.contains("hidden")) tb.classList.toggle("open",on); }); }
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
  function deepLink(){ var h=location.hash||""; if(h.indexOf("#row/")!==0) return; var id=h.slice(5); var el=document.getElementById("row-"+id); if(!el) return;
    if(el.classList.contains("hidden")){ var f=document.getElementById("filters"); if(f){ var sels=f.querySelectorAll("select"); for(var k=0;k<sels.length;k++) sels[k].value="All"; } applyFilters(); }
    var old=document.querySelectorAll(".hi"); for(var i=0;i<old.length;i++) old[i].classList.remove("hi"); el.classList.add("hi"); el.classList.add("open"); try{ el.scrollIntoView({block:"start",behavior:"instant"}); }catch(e){ el.scrollIntoView(true); } }
  var tmr={};
  document.addEventListener("DOMContentLoaded",function(){
    captureEndpoint();
    var f=document.getElementById("filters"); if(f){ var os=f.querySelector("[name=owner]"); if(os) os.innerHTML='<option>All</option>'+ownerOptions().map(function(n){ return '<option>'+esc(n)+'</option>'; }).join(""); f.addEventListener("change",applyFilters); }
    var rv=document.getElementById("reviewer"); if(rv){ rv.innerHTML='<option value="">editing as</option>'+IDENTITIES.map(function(n){ return '<option value="'+esc(n)+'">'+esc(n)+'</option>'; }).join(""); rv.value=S.who||"";
      rv.addEventListener("change",function(){ S.who=IDENTITIES.indexOf(rv.value)>=0?rv.value:""; save(); flash(S.who?"Editing as "+S.who:""); }); }
    paintAll(); deepLink(); window.addEventListener("hashchange",deepLink);
    var ex=document.getElementById("export"); if(ex) ex.addEventListener("click",exportBrief);
    var oa=document.getElementById("openall"); if(oa) oa.addEventListener("click",function(){ openAll(true); });
    var ca=document.getElementById("closeall"); if(ca) ca.addEventListener("click",function(){ openAll(false); });
    var cn=document.getElementById("counts"); if(cn) cn.addEventListener("click",function(e){ var b=e.target.closest?e.target.closest("button[data-status]"):null; if(!b||!f) return; var sel=f.querySelector("[name=status]"); sel.value=(sel.value===b.getAttribute("data-status"))?"All":b.getAttribute("data-status"); applyFilters(); });
    var tbl=document.getElementById("tbl"); if(tbl) tbl.addEventListener("click",function(e){ var t=e.target; if(!t.closest) return;
      var th=t.closest("th[data-sort]"); if(th){ sortBy(th.getAttribute("data-sort")); return; }
      if(t.closest("a,input,select,textarea,button,label")) return;
      var r1=t.closest("tr.r1"); if(r1){ var tb=r1.parentNode; tb.classList.toggle("open"); } });
    document.body.addEventListener("input",function(e){ var t=e.target; var id=t.getAttribute("data-id"), k=t.getAttribute("data-f"); if(!id||!k) return; if(t.tagName==="SELECT"||t.type==="date") return;
      var ed=edits(id); ed[k]=t.value; if(k==="comment") ed.comment_who=S.who||""; save(); paintRow(id); if(k==="owner") applyFilters(); flash("Saving...");
      clearTimeout(tmr[id+k]); tmr[id+k]=setTimeout(function(){ post(id,k,val(id,k)); flash(); },1500); });
    document.body.addEventListener("change",function(e){ var t=e.target; var id=t.getAttribute("data-id"), k=t.getAttribute("data-f"); if(!id||!k) return; if(!(t.tagName==="SELECT"||t.type==="date")) return;
      var ed=edits(id); ed[k]=t.value; save(); paintRow(id); applyFilters(); post(id,k,t.value); flash(); });
  });
  // test hook for the checks (and for the console)
  window.yeslyfIntegrations={ exportText: md, longPole: function(){ return longPole().map(function(r){ return r.id; }); }, sortBy: sortBy, value: val, open: openRow, rows: function(){ return ROWS.length; } };
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


def fact(label, body):
    return '<div class="f"><b>%s</b>%s</div>' % (esc(label), body)


def screens_fact(row, check, live_ids):
    listed = row["screens"]
    if listed == ["all"]:
        body = "all screens"
    elif not listed:
        body = "-"
    else:
        body = '<div class="chips">' + "".join(site.sid_link(s, live_ids) for s in listed) + '</div>'
    if check["unlisted"]:
        body += '<div class="meta verify">%s: the vendor is also named on <span class="chips" style="display:inline-flex">%s</span></div>' % (
            esc(MARK), "".join(site.sid_link(s, live_ids) for s in check["unlisted"]))
    if check["missing"]:
        body += '<div class="meta verify">%s: not live in v0.2: %s</div>' % (esc(MARK), esc(", ".join(check["missing"])))
    return body


def render_row(row, check, live_ids):
    rid = esc(row["id"])
    mark = ' <span class="tag tbv" title="%s">to be verified</span>' % esc(MARK) if row.get("to_be_verified") else ""
    line = ('<tr class="r1"><td class="n">%s</td><td class="v"><b>%s</b>%s<div class="meta">%s</div></td><td class="c-gates">%s</td>'
            '<td><span data-show="owner"></span></td><td><span class="tag" data-show="status"></span></td>'
            '<td class="c-date"><span class="dt" data-show="sandbox_date"></span></td><td class="c-date"><span class="dt" data-show="production_date"></span></td>'
            '<td class="tg" title="open"></td></tr>' % (rid, esc(row["vendor"]), mark, esc(row["category"]), esc(row["gates"] or "-")))
    facts = [fact("Role", esc(row["role"])), fact("If it slips", esc(row["fallback"] or "-")), fact("Screens", screens_fact(row, check, live_ids))]
    if row["alternatives"]:
        facts.append(fact("Alternatives", esc(row["alternatives"])))
    facts.append(fact("Cause", '<span class="cause">%s</span>' % esc(row["cause"])))
    form = ('<label>Owner</label>%s<label>Status</label>%s<label>Agreement</label>%s<label>Sandbox</label>%s<label>Production</label>%s'
            '<label>Docs</label><div class="docs">%s<a data-docs target="_blank" rel="noopener" style="display:none">open</a></div>'
            '<label>Cost</label>%s<label>Notes</label>%s<label>Comment</label>%s<span class="cw" data-cwho></span>' % (
                control(row, "owner", "first names"), control(row, "status", "select"), control(row, "agreement_date", "date"),
                control(row, "sandbox_date", "date"), control(row, "production_date", "date"), control(row, "docs_url", "https://..."),
                control(row, "cost", "free, or paid with the model"), control(row, "notes", "textarea"), control(row, "comment", "textarea")))
    panel = '<tr class="r2"><td colspan="8"><div class="panel"><div>%s</div><div class="form">%s</div></div></td></tr>' % ("".join(facts), form)
    return '<tbody id="row-%s" data-id="%s">%s%s</tbody>' % (rid, rid, line, panel)


def build_page(rows, checks, live_ids, review=False):
    """review=True renders the docs/review/ copy: the review tabs only, no setup link, screen links into the review
    copy of Wireframes v0.2 (review/index.html)."""
    n = len(rows)
    who = '<div class="who">Editing as <select id="reviewer"></select></div>'
    intro = ('<section><h1>Integrations</h1>'
             '<p class="lead">One row per integration: what it does, the v0.2 screens that need it, what it gates, and the fallback if it slips. '
             'Open a row to edit owner, status, dates, docs, cost and notes, or to comment. Edits save in this browser and reach the sheet when the endpoint is set.</p>'
             '<div class="counts" id="counts"></div><div class="pole" id="pole"></div></section>')
    toolbar = ('<div class="toolbar" id="filters"><label>Gates <select name="gates"><option>All</option>%s</select></label>'
               '<label>Owner <select name="owner"><option>All</option></select></label>'
               '<label>Status <select name="status"><option>All</option>%s</select></label>'
               '<span id="count" class="meta"></span><span class="sp"></span><button id="openall" type="button">Open all</button><button id="closeall" type="button">Close all</button></div>' % (
                   "".join("<option>%s</option>" % esc(g) for g in GATES), "".join("<option>%s</option>" % esc(s) for s in STATUSES)))
    thead = ('<thead><tr><th class="c-id" data-sort="id">ID<span class="dir"></span></th><th data-sort="vendor">Vendor<span class="dir"></span></th>'
             '<th class="c-gates" data-sort="gates">Gates<span class="dir"></span></th><th data-sort="owner">Owner<span class="dir"></span></th>'
             '<th data-sort="status">Status<span class="dir"></span></th><th class="c-date" data-sort="sandbox_date">Sandbox<span class="dir"></span></th>'
             '<th class="c-date" data-sort="production_date">Production<span class="dir"></span></th><th class="c-tg"></th></tr></thead>')
    table = '<div class="wrap"><table id="tbl">' + thead + "\n".join(render_row(r, checks[r["id"]], live_ids) for r in rows) + '</table></div>'
    if review:
        table = table.replace('href="wireframes_v02.html#', 'href="index.html#')
    blob = ('<script>var ROWS=' + site.js_blob(rows) + ';\nvar IDENTITIES=' + site.js_blob(IDENTITIES) + ';\nvar STATUSES=' + site.js_blob(STATUSES) +
            ';\nvar GATES=' + site.js_blob(GATES) + ';</script>\n')
    return (site.head("yeslyf integrations v0.2", site.CSS + EXTRA_CSS) + '<body>\n' +
            site.header(PAGE, "integrations, %d rows" % n, who_html=who, export_label="Export brief",
                        tabs=site.REVIEW_TABS if review else None, setup_link=not review) +
            '<main class="main" style="max-width:none">' + intro + '<section>' + toolbar + table + '</section></main>\n' +
            blob + '<script>' + JS + '</script>\n</body>\n</html>\n')


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

    pages = {PAGE: build_page(rows, checks, live_ids), "review/" + PAGE: build_page(rows, checks, live_ids, review=True)}
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
        print("wrote docs/%s (%d bytes, %d rows)" % (name, len(page), len(rows)))


if __name__ == "__main__":
    main()
