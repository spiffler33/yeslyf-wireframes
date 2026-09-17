#!/usr/bin/env python3
"""Generate docs/tracker.html and docs/review/tracker.html from data/tracker.json (phase 12, pass 3; Vatsal, 17 Sep
2026). Never hand-edit docs/.

The Tracker: project management on the page, for the daily update Spinach asked for (minutes 16 Sep 2026, item 21).
- A milestone strip on top (data/tracker.json milestones; the last one reads the date every integrations row is
  final from the Integrations tab's board row).
- One row per item (W01 onwards; W01 to W09 moved here from the Integrations tab with their saved rows): item,
  direction, owner, due, status, blocked by, source, lands at, notes. Owner, due, status, blocked by and notes are
  edited on the page; every edit is one row in board_entries (page "tracker", item_id the W id) through
  scripts/board_store.js; rows written before the move (page "integrations", the same W ids) are read too, so the
  history is whole. Overdue rows say so in words. No write without an identity.
- Spinach's questions: every comment written under the identity Spinach (or "Spinach (name)" from the import script)
  on any page: screen or row, age, open or answered. An answer is a row on the same item with field "answer"; a
  question is answered once an answer row follows it.
- "Copy today's update": plain text for WhatsApp from the last 24 hours of the board table plus the build data; the
  page copies it and shows it. No messaging API.
Same tokens and top nav as the other board pages (scripts/build_site.py supplies head(), header() and the CSS).
Called at the end of scripts/build_site.py (TABS and REVIEW_TABS carry the Tracker tab); also runs on its own.
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
import build_integrations as integ  # noqa: E402

PAGE = "tracker.html"
DATA_FILE = os.path.join(DATA, "tracker.json")
IDENTITIES = ["Bhuvanaa", "Harish", "Gaurav", "Kajal", "Somil", "Vatsal", "Spinach", "Compliance"]
STATUSES = ["not started", "in progress", "delivered", "blocked"]
DIRECTIONS = ["HoA to Spinach", "Spinach to HoA", "HoA internal"]
FIELDS = ["id", "item", "direction", "owner", "due_date", "due_about", "status", "blocked_by", "source", "lands_at", "notes"]
esc = site.esc


def is_date(d):
    return len(d) == 10 and d[4] == "-" and d[7] == "-" and d.replace("-", "").isdigit()


def validate(doc):
    problems = []
    rows = doc.get("rows", [])
    seen = set()
    ids = [r.get("id", "") for r in rows]
    for i, row in enumerate(rows):
        rid = row.get("id", "")
        for f in FIELDS:
            if f not in row:
                problems.append("%s: missing field %s" % (rid or ("row %d" % i), f))
        if not (len(rid) == 3 and rid[0] == "W" and rid[1:].isdigit()):
            problems.append("row %d: id %r is not W plus two digits" % (i, rid))
        if rid in seen:
            problems.append("%s: duplicate id" % rid)
        seen.add(rid)
        if row.get("status") not in STATUSES:
            problems.append("%s: status %r is not one of %s" % (rid, row.get("status"), ", ".join(STATUSES)))
        if row.get("direction") not in DIRECTIONS:
            problems.append("%s: direction %r is not one of %s" % (rid, row.get("direction"), ", ".join(DIRECTIONS)))
        for f in ("item", "source"):
            if not str(row.get(f, "")).strip():
                problems.append("%s: %s is empty" % (rid, f))
        d = str(row.get("due_date", ""))
        if d and not is_date(d):
            problems.append("%s: due_date %r is not yyyy-mm-dd" % (rid, d))
        b = row.get("blocked_by", "")
        if b and b not in ids:
            problems.append("%s: blocked_by %r is not a tracker row" % (rid, b))
    expected = ["W%02d" % n for n in range(1, len(rows) + 1)]
    if ids != expected:
        problems.append("ids are not W01 to W%02d in order (the W series is never renumbered)" % len(rows))
    for m in doc.get("milestones", []):
        if m.get("final_by"):
            continue
        if not is_date(str(m.get("date", ""))):
            problems.append("milestone %r: date is not yyyy-mm-dd" % m.get("label"))
        for rid in m.get("rows", []):
            if rid not in ids:
                problems.append("milestone %r names %s, not a tracker row" % (m.get("label"), rid))
    if not str(doc.get("board_link", "")).startswith("https://"):
        problems.append("board_link must be the https review link")
    return problems


EXTRA_CSS = integ.EXTRA_CSS + """
  .strip{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0 0}
  .ms{border:1px solid var(--line);border-radius:6px;padding:5px 9px;background:#fff;font-size:12px;font-variant-numeric:tabular-nums}
  .ms b{font-weight:600;margin-right:6px} .ms.past{color:var(--mute)} .ms.next{border-color:var(--ink)}
  th.c-dir{width:120px} td.dir{color:var(--mute);white-space:nowrap}
  td.due .late{display:block;font-size:11px;color:#8A2E2E}
  td.due .about{color:var(--mute);font-size:11px;margin-left:4px}
  .tag.st-blocked{border-color:#8A2E2E;color:#8A2E2E}
  .qs{margin:8px 0 0} .q{padding:8px 0;border-top:1px solid var(--line);font-size:12.5px} .q:first-child{border-top:0}
  .q .h{display:flex;gap:10px;flex-wrap:wrap;align-items:baseline;color:var(--mute);font-size:12px;margin-bottom:3px}
  .q .h b{color:var(--ink);font-size:12.5px} .q .t{white-space:pre-wrap} .q .a{margin-top:5px;padding-left:10px;border-left:3px solid var(--accent);white-space:pre-wrap}
  .q .a .w{color:var(--mute);font-size:11.5px;margin-right:6px}
  .upd{margin-top:8px;display:none} .upd.on{display:block}
  .upd pre{margin:6px 0 0;font-size:12.5px;line-height:1.5;background:#fff;border:1px solid var(--line);border-radius:6px;padding:10px 12px;white-space:pre-wrap;max-width:720px}
  .updrow{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-top:8px}
  .updrow button{border:1px solid var(--ink);background:#fff;padding:6px 12px;border-radius:6px;cursor:pointer;font-weight:600}
  .updrow .meta{font-size:12px}
  .empty{font-size:12.5px;color:var(--mute)}
"""

JS = r"""
(function(){
  var KEY="yeslyf_tracker_v1";
  var EDITABLE=["owner","due_date","status","blocked_by","notes"];
  var byId={}; ROWS.forEach(function(r){ byId[r.id]=r; });
  var S={}; try{ S=JSON.parse(localStorage.getItem(KEY)||"{}")||{}; }catch(e){ S={}; }
  if(!S.rows) S.rows={}; if(!S.who) S.who="";
  var ALL=null;       // every row of the board table, once read (questions, the daily update)
  var FINAL_BY="";    // the date every integrations row is final (Integrations tab, board row integrations / final_by)
  var CHOICES={};     // the latest final or open row per integrations row
  var MONTHS=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  function save(){ try{ localStorage.setItem(KEY, JSON.stringify(S)); }catch(e){} }
  var ft; function flash(t){ var s=document.getElementById("saved"); if(!s) return; s.textContent=t||"Saved in this browser"; clearTimeout(ft); ft=setTimeout(function(){ s.textContent=""; },1800); }
  function esc(s){ return String(s===undefined||s===null?"":s).split("&").join("&amp;").split("<").join("&lt;").split(">").join("&gt;").split('"').join("&quot;"); }
  function slug(s){ return String(s||"").split(" ").join("-"); }
  function edits(id){ if(!S.rows[id]) S.rows[id]={}; return S.rows[id]; }
  function val(id,f){ var e=S.rows[id]||{}; if(e[f]!==undefined) return e[f]; var r=byId[id]; return (r&&r[f]!==undefined)?r[f]:""; }
  function put(id,field,value){ if(!window.yeslyfBoard) return true; var ok=yeslyfBoard.write({item_id:id,field:field,value:value,who:S.who||"",kind:"field_edit"}); if(!ok) setTimeout(function(){ flash(yeslyfBoard.noIdentity); },0); return ok; }
  function today(){ var d=new Date(); return d.getFullYear()+"-"+two(d.getMonth()+1)+"-"+two(d.getDate()); }
  function two(n){ return (n<10?"0":"")+n; }
  function dmy(iso){ if(!iso||iso.length<10) return ""; return parseInt(iso.slice(8,10),10)+" "+MONTHS[parseInt(iso.slice(5,7),10)-1]+" "+iso.slice(0,4); }
  function daysBetween(a,b){ return Math.round((new Date(b.slice(0,10)+"T00:00:00Z")-new Date(a.slice(0,10)+"T00:00:00Z"))/86400000); }
  function ago(ts){ var ms=Date.now()-new Date(String(ts||"").slice(0,19)+"Z").getTime(); if(isNaN(ms)) return ""; var h=Math.floor(ms/3600000); if(h<1) return "just now"; if(h<24) return h+"h ago"; var d=Math.floor(h/24); return d+(d===1?" day ago":" days ago"); }
  function isSpinach(who){ var w=String(who||""); return w==="Spinach"||w.indexOf("Spinach (")===0; }
  function applyRemote(rows){ rows.forEach(function(r){
      if(r.item_id===INTEG_ITEM&&r.field==="final_by"){ FINAL_BY=r.value||""; return; }
      if(r.field==="choice"&&(r.value==="final"||r.value==="open")){ CHOICES[r.item_id]=r; return; }
      if(!byId[r.item_id]||EDITABLE.indexOf(r.field)<0) return; var ed=edits(r.item_id); ed[r.field]=r.value||""; }); save(); paintAll(); }
  function overdue(r){ var d=val(r.id,"due_date"), st=val(r.id,"status"); if(!d||st==="delivered") return 0; var n=daysBetween(d,today()); return n>0?n:0; }
  function paintRow(id){ var tb=document.getElementById("row-"+id); if(!tb) return;
    var f=tb.querySelectorAll("[data-f]"); for(var i=0;i<f.length;i++){ var k=f[i].getAttribute("data-f"); var v=val(id,k); if(f[i].value!==v) f[i].value=v; }
    var sh=tb.querySelectorAll("[data-show]"); for(var j=0;j<sh.length;j++){ var key=sh[j].getAttribute("data-show"); var t=String(val(id,key)||""); sh[j].textContent=t||"-"; if(key==="status") sh[j].className="tag st-"+slug(t); }
    var due=tb.querySelector("[data-due]"); if(due){ var d=val(id,"due_date"); var n=overdue(byId[id]); var about=byId[id].due_about?'<span class="about">about</span>':'';
      due.innerHTML=d?(esc(dmy(d))+about+(n?'<span class="late">overdue by '+n+(n===1?' day':' days')+'</span>':(daysBetween(today(),d)===0&&val(id,"status")!=="delivered"?'<span class="late">due today</span>':''))):'<span class="meta">-</span>'; }
    tb.setAttribute("data-status", val(id,"status")); tb.setAttribute("data-owners", String(val(id,"owner")||"").split(",").map(function(p){ return p.trim(); }).filter(Boolean).join("|")); }
  function paintCounts(){ var c={}; STATUSES.forEach(function(s){ c[s]=0; }); ROWS.forEach(function(r){ c[val(r.id,"status")]=(c[val(r.id,"status")]||0)+1; });
    var late=ROWS.filter(function(r){ return overdue(r)>0; });
    var el=document.getElementById("counts"); if(el) el.innerHTML='<span class="k">'+ROWS.length+' items</span>'+STATUSES.map(function(s){ return '<span class="chip"><b>'+c[s]+'</b> '+esc(s)+'</span>'; }).join("")+'<span class="chip"><b>'+late.length+'</b> overdue</span>'; }
  function paintMilestones(){ var el=document.getElementById("strip"); if(!el) return; var t=today(); var nextSeen=false;
    el.innerHTML=MILESTONES.map(function(m){ var date=m.final_by?FINAL_BY:m.date; var past=!!date&&date<t; var cls="ms"+(past?" past":"");
      if(!past&&date&&!nextSeen&&!m.final_by){ cls+=" next"; nextSeen=true; }
      var label=m.final_by?"every integrations row final":m.label; var when=date?((m.about?"about ":"")+dmy(date)):"date not set";
      return '<span class="'+cls+'"><b>'+esc(when)+'</b>'+esc(label)+(past?" (passed)":"")+'</span>'; }).join(""); }
  function ownerOptions(){ var seen=[]; ROWS.forEach(function(r){ String(val(r.id,"owner")||"").split(",").forEach(function(p){ p=p.trim(); if(p&&seen.indexOf(p)<0) seen.push(p); }); }); return seen.sort(); }
  function applyFilters(){ var f=document.getElementById("filters"); if(!f) return; var d=f.querySelector("[name=direction]").value, o=f.querySelector("[name=owner]").value, s=f.querySelector("[name=status]").value; var shown=0;
    ROWS.forEach(function(r){ var tb=document.getElementById("row-"+r.id); if(!tb) return;
      var ok=(d==="All"||r.direction===d)&&(o==="All"||("|"+tb.getAttribute("data-owners")+"|").indexOf("|"+o+"|")>=0)&&(s==="All"||val(r.id,"status")===s||(s==="overdue"&&overdue(r)>0));
      tb.classList.toggle("hidden",!ok); if(ok) shown++; });
    var c=document.getElementById("count"); if(c) c.textContent=shown+" of "+ROWS.length; paintCounts(); }
  function paintAll(){ ROWS.forEach(function(r){ paintRow(r.id); }); var rv=document.getElementById("reviewer"); if(rv&&rv.value!==(S.who||"")) rv.value=S.who||""; paintMilestones(); applyFilters(); }
  // ---- Spinach's questions: every comment under the identity Spinach on any page; answered when an answer row follows
  function questions(){ if(!ALL) return []; var qs=[]; var answers={};
    ALL.forEach(function(r){ if(r.field==="answer"&&r.kind==="comment"&&String(r.value||"").trim()){ (answers[r.page+"|"+r.item_id]=answers[r.page+"|"+r.item_id]||[]).push(r); } });
    ALL.forEach(function(r){ if(r.kind!=="comment"||!isSpinach(r.who)||!String(r.value||"").trim()) return; if(r.field!=="text"&&r.field!=="question"&&r.field!=="comment"&&r.field!=="note") return;
      var after=(answers[r.page+"|"+r.item_id]||[]).filter(function(a){ return a.id>r.id; });
      qs.push({row:r, answers:after, answered:after.length>0}); });
    qs.sort(function(a,b){ return b.row.id-a.row.id; }); return qs; }
  function pageLink(r){ var p=r.page; var id=r.item_id;
    if(p==="wireframes_v02") return REVIEW?'index.html#'+encodeURIComponent(id):'wireframes_v02.html#'+encodeURIComponent(id);
    if(p==="integrations") return 'integrations.html#row/'+encodeURIComponent(id);
    if(p==="tracker") return '#row/'+encodeURIComponent(id); return ''; }
  function paintQuestions(){ var el=document.getElementById("qs"); if(!el) return; var qs=questions();
    var c=document.getElementById("qcount"); var open=qs.filter(function(q){ return !q.answered; }).length;
    if(c) c.textContent=ALL?(qs.length+" questions, "+open+" open, "+(qs.length-open)+" answered"):"reading the board";
    if(!qs.length){ el.innerHTML='<p class="empty">'+(ALL?"No question from Spinach yet. A comment under the identity Spinach on any screen or row lands here.":"")+'</p>'; return; }
    el.innerHTML=qs.map(function(q){ var r=q.row; var link=pageLink(r);
      return '<div class="q"><div class="h">'+(link?'<a class="sid" href="'+esc(link)+'">'+esc(r.item_id)+'</a>':'<span class="sid">'+esc(r.item_id)+'</span>')+'<b>'+esc(r.who)+'</b><span>'+esc(ago(r.created_at))+'</span><span>'+(q.answered?"answered":"open")+'</span></div>'+
        '<div class="t">'+esc(r.value)+'</div>'+q.answers.map(function(a){ return '<div class="a"><span class="w">'+esc(a.who||"(no identity)")+', '+esc(ago(a.created_at))+'</span>'+esc(a.value)+'</div>'; }).join("")+'</div>'; }).join(""); }
  // ---- the daily update: plain text for WhatsApp from the last 24 hours of the table plus the build data
  function headline(item){ var i=item.indexOf(":"); var j=item.indexOf(";"); var cut=item.length; if(i>0&&i<cut) cut=i; if(j>0&&j<cut) cut=j; return item.slice(0,cut); }
  function update(){ var t=today(); var since=Date.now()-86400000; var L=["yeslyf board, "+dmy(t)];
    var rows=ALL||[]; function recent(r){ return new Date(String(r.created_at||"").slice(0,19)+"Z").getTime()>=since; }
    var delivered=[]; ROWS.forEach(function(r){ var last=null; rows.forEach(function(x){ if(x.item_id===r.id&&x.field==="status"&&(x.page==="tracker"||x.page==="integrations")) last=x; }); if(last&&last.value==="delivered"&&recent(last)) delivered.push(r.id+" "+headline(r.item)); });
    if(delivered.length) L.push("Delivered: "+delivered.join("; "));
    var nowFinal=[]; INTEG.forEach(function(r){ var row=CHOICES[r.id]; if(row&&row.value==="final"&&recent(row)) nowFinal.push(r.id+" "+r.vendor); else if(!row&&r.choice==="final"&&r.final_since&&daysBetween(r.final_since,t)<=1&&daysBetween(r.final_since,t)>=0) nowFinal.push(r.id+" "+r.vendor); });
    if(nowFinal.length) L.push("Now final: "+nowFinal.join("; "));
    var unfrozen=COUNTS.unfreeze_log.filter(function(x){ return x.date&&daysBetween(x.date,t)<=1&&daysBetween(x.date,t)>=0; }).map(function(x){ return x.screen; });
    L.push("Frozen: "+COUNTS.frozen+" screens, "+COUNTS.templates+" templates. Open: "+COUNTS.open+", reasons on the Changelog"+(unfrozen.length?". Unfrozen: "+unfrozen.join(", "):""));
    var qs=questions(); var newQ=qs.filter(function(q){ return recent(q.row); }); var ans=qs.filter(function(q){ return q.answers.some(recent); });
    if(newQ.length||ans.length) L.push("Spinach questions: "+newQ.length+" new"+(newQ.length?" ("+newQ.map(function(q){ return q.row.item_id; }).join(", ")+")":"")+"; "+ans.length+" answered"+(ans.length?" ("+ans.map(function(q){ return q.row.item_id; }).join(", ")+")":""));
    var late=ROWS.filter(function(r){ return overdue(r)>0; }).map(function(r){ var n=overdue(r); return r.id+" ("+(val(r.id,"owner")||"no owner")+", "+n+(n===1?" day":" days")+")"; });
    L.push("Overdue: "+(late.length?late.join("; "):"none"));
    var next=null; MILESTONES.forEach(function(m){ var d=m.final_by?FINAL_BY:m.date; if(d&&d>=t&&(!next||d<next.d)) next={d:d, label:m.final_by?"every integrations row final":m.label, about:!!m.about}; });
    if(next) L.push("Next: "+(next.about?"about ":"")+dmy(next.d)+", "+next.label);
    L.push(BOARD_LINK); return L.join("\n"); }
  function copyUpdate(){ var text=update(); var box=document.getElementById("upd"); if(box){ box.className="upd on"; box.querySelector("pre").textContent=text; }
    var done=false; try{ if(navigator.clipboard&&navigator.clipboard.writeText){ navigator.clipboard.writeText(text).then(function(){ flash("Copied"); }, function(){ flash("Shown below; copy it by hand"); }); done=true; } }catch(e){}
    if(!done) flash("Shown below; copy it by hand"); }
  function deepLink(){ var h=location.hash||""; if(h.indexOf("#row/")!==0) return; var id=h.slice(5); var el=document.getElementById("row-"+id); if(!el) return;
    if(el.classList.contains("hidden")){ var f=document.getElementById("filters"); if(f){ var sels=f.querySelectorAll("select"); for(var k=0;k<sels.length;k++) sels[k].value="All"; } applyFilters(); }
    var old=document.querySelectorAll(".hi"); for(var i=0;i<old.length;i++) old[i].classList.remove("hi"); el.classList.add("hi"); el.classList.add("open"); try{ el.scrollIntoView({block:"start",behavior:"instant"}); }catch(e){ el.scrollIntoView(true); } }
  var tmr={};
  document.addEventListener("DOMContentLoaded",function(){
    if(window.yeslyfBoard){ Array.prototype.forEach.call(document.querySelectorAll("textarea[data-f=notes]"),function(t){ yeslyfBoard.attach(t,t.getAttribute("data-id")); });
      yeslyfBoard.init({page:"tracker",also:["integrations"],apply:applyRemote});
      yeslyfBoard.read({page:"",apply:function(latest,rows,ok){ ALL=ok?rows:[]; paintQuestions(); }}); }
    else { ALL=[]; paintQuestions(); }
    var f=document.getElementById("filters"); if(f){ var os=f.querySelector("[name=owner]"); if(os) os.innerHTML='<option>All</option>'+ownerOptions().map(function(n){ return '<option>'+esc(n)+'</option>'; }).join(""); f.addEventListener("change",applyFilters); }
    var rv=document.getElementById("reviewer"); if(rv){ rv.innerHTML='<option value="">editing as</option>'+IDENTITIES.map(function(n){ return '<option value="'+esc(n)+'">'+esc(n)+'</option>'; }).join(""); rv.value=S.who||"";
      rv.addEventListener("change",function(){ S.who=IDENTITIES.indexOf(rv.value)>=0?rv.value:""; save(); flash(S.who?"Editing as "+S.who:""); }); }
    paintAll(); paintQuestions(); deepLink(); window.addEventListener("hashchange",deepLink);
    var up=document.getElementById("update"); if(up) up.addEventListener("click",copyUpdate);
    var oa=document.getElementById("openall"); if(oa) oa.addEventListener("click",function(){ ROWS.forEach(function(r){ var tb=document.getElementById("row-"+r.id); if(tb&&!tb.classList.contains("hidden")) tb.classList.add("open"); }); });
    var ca=document.getElementById("closeall"); if(ca) ca.addEventListener("click",function(){ ROWS.forEach(function(r){ var tb=document.getElementById("row-"+r.id); if(tb) tb.classList.remove("open"); }); });
    var tbl=document.getElementById("tbl"); if(tbl) tbl.addEventListener("click",function(e){ var t=e.target; if(!t.closest) return; if(t.closest("a,input,select,textarea,button,label")) return; var r1=t.closest("tr.r1"); if(r1) r1.parentNode.classList.toggle("open"); });
    document.body.addEventListener("input",function(e){ var t=e.target; var id=t.getAttribute("data-id"), k=t.getAttribute("data-f"); if(!id||!k||!byId[id]) return; if(t.tagName==="SELECT"||t.type==="date") return;
      var ed=edits(id); ed[k]=t.value; save(); paintRow(id); if(k==="owner") applyFilters(); flash("Saving...");
      clearTimeout(tmr[id+k]); tmr[id+k]=setTimeout(function(){ if(put(id,k,val(id,k))) flash(); },1500); });
    document.body.addEventListener("change",function(e){ var t=e.target; var id=t.getAttribute("data-id"), k=t.getAttribute("data-f"); if(!id||!k||!byId[id]) return; if(!(t.tagName==="SELECT"||t.type==="date")) return;
      var ed=edits(id); ed[k]=t.value; save(); paintRow(id); applyFilters(); if(put(id,k,t.value)) flash(); });
  });
  // test hook for the checks (and for the console)
  window.yeslyfTracker={ update: update, questions: questions, rows: function(){ return ROWS.length; }, value: val, setRows: function(rows){ ALL=rows; paintQuestions(); } };
})();
"""


def control(row, field, kind, options=None):
    rid = esc(row["id"])
    v = esc(row.get(field, ""))
    if kind == "select":
        return '<select data-id="%s" data-f="%s">%s</select>' % (rid, field, "".join(
            '<option value="%s"%s>%s</option>' % (esc(s), " selected" if s == row.get(field) else "", esc(s)) for s in options))
    if kind == "date":
        return '<input type="date" data-id="%s" data-f="%s" value="%s">' % (rid, field, v)
    if kind == "textarea":
        return '<textarea data-id="%s" data-f="%s">%s</textarea>' % (rid, field, v)
    return '<input data-id="%s" data-f="%s" value="%s" placeholder="%s">' % (rid, field, v, esc(kind))


def fact(label, body):
    return '<div class="f"><b>%s</b>%s</div>' % (esc(label), body)


def render_row(row):
    rid = esc(row["id"])
    line = ('<tr class="r1"><td class="n">%s</td><td class="it"><b>%s</b></td><td class="dir c-dir">%s</td><td><span data-show="owner"></span></td>'
            '<td class="due c-due"><span data-due></span></td><td><span class="tag" data-show="status"></span></td><td class="tg" title="open"></td></tr>' % (
                rid, esc(row["item"]), esc(row["direction"])))
    facts = [fact("Source", '<span class="cause">%s</span>' % esc(row["source"])), fact("Lands at", esc(row["lands_at"] or "-"))]
    form = ('<label>Owner</label>%s<label>Due</label>%s<label>Status</label>%s<label>Blocked by</label>%s<label>Notes</label>%s' % (
        control(row, "owner", "first names, or Spinach"), control(row, "due_date", "date"), control(row, "status", "select", STATUSES),
        control(row, "blocked_by", "a row ID, W19"), control(row, "notes", "textarea")))
    panel = '<tr class="r2"><td colspan="7"><div class="panel"><div>%s</div><div class="form">%s</div></div></td></tr>' % ("".join(facts), form)
    return '<tbody id="row-%s" data-id="%s">%s%s</tbody>' % (rid, rid, line, panel)


def build_page(doc, counts, integ_rows, review=False):
    rows = doc["rows"]
    who = '<div class="who">Editing as <select id="reviewer"></select></div>'
    intro = ('<section><h1>Tracker</h1>'
             '<p class="lead">What HoA owes Spinach, what Spinach owes HoA, and what HoA settles inside. One row per item, the W series; '
             'open a row to set owner, due date, status, blocked by and notes. Every edit is recorded as it happens and shows on every device; '
             'overdue rows say so in words. Copy today\'s update composes the WhatsApp text from the last 24 hours of the board.</p>'
             '<div class="strip" id="strip"></div><div class="counts" id="counts"></div>'
             '<div class="updrow"><button id="update" type="button">Copy today\'s update</button><span class="meta">plain text, about 15 lines, first names, no costs; anyone can press it</span></div>'
             '<div class="upd" id="upd"><pre></pre></div></section>')
    toolbar = ('<div class="toolbar" id="filters"><label>Direction <select name="direction"><option>All</option>%s</select></label>'
               '<label>Owner <select name="owner"><option>All</option></select></label>'
               '<label>Status <select name="status"><option>All</option>%s<option value="overdue">overdue</option></select></label>'
               '<span id="count" class="meta"></span><span class="sp"></span><button id="openall" type="button">Open all</button><button id="closeall" type="button">Close all</button></div>' % (
                   "".join("<option>%s</option>" % esc(d) for d in DIRECTIONS), "".join("<option>%s</option>" % esc(s) for s in STATUSES)))
    thead = ('<thead><tr><th class="c-id">ID</th><th>Item</th><th class="c-dir">Direction</th><th>Owner</th><th class="c-due">Due</th><th>Status</th><th class="c-tg"></th></tr></thead>')
    table = '<div class="wrap"><table id="tbl">' + thead + "\n".join(render_row(r) for r in rows) + '</table></div>'
    qsec = ('<section><h2>Spinach\'s questions</h2><p class="meta lead">Every comment written under the identity Spinach, on any page, newest first: where, how old, open or answered. '
            'An answer is written under the question on the screen (the Answer box on the Wireframes v0.2 tab) and shows here.</p>'
            '<div class="counts"><span class="k" id="qcount">reading the board</span></div><div class="qs" id="qs"></div></section>')
    blob = ('<script>var ROWS=' + site.js_blob(rows) + ';\nvar MILESTONES=' + site.js_blob(doc["milestones"]) + ';\nvar BOARD_LINK=' + site.js_blob(doc["board_link"]) +
            ';\nvar COUNTS=' + site.js_blob(counts) + ';\nvar INTEG=' + site.js_blob(integ_rows) + ';\nvar INTEG_ITEM=' + site.js_blob(integ.PAGE_ITEM) +
            ';\nvar IDENTITIES=' + site.js_blob(IDENTITIES) + ';\nvar STATUSES=' + site.js_blob(STATUSES) + ';\nvar REVIEW=' + site.js_blob(bool(review)) + ';</script>\n')
    return (site.head("yeslyf tracker", site.CSS + EXTRA_CSS, config="../config.js" if review else "config.js") + '<body>\n' +
            site.header(PAGE, "tracker, %d items" % len(rows), who_html=who, show_export=False, tabs=site.REVIEW_TABS if review else None, setup_link=not review) +
            '<main class="main" style="max-width:none">' + intro + '<section>' + toolbar + table + '</section>' + qsec + '</main>\n' +
            blob + site.store_script() + '<script>' + JS + '</script>\n</body>\n</html>\n')


def main():
    with open(DATA_FILE) as fh:
        raw = fh.read()
    site.check_ascii("data/tracker.json", raw)
    doc = json.loads(raw)
    problems = validate(doc)
    if problems:
        for p in problems:
            print("ERROR: " + p)
        sys.exit(1)
    chg = site.load("changelog.json")
    fz = chg.get("freeze") or {}
    counts = {"screens": chg["counts"]["total"], "frozen": fz.get("frozen", 0), "open": fz.get("open", 0),
              "templates": chg["counts"]["unique_templates"], "since": fz.get("since", ""), "unfreeze_log": fz.get("unfreeze_log", [])}
    integ_rows = [{"id": r["id"], "vendor": r["vendor"], "choice": r.get("choice", "open"), "final_since": r.get("final_since", "")} for r in site.load("integrations.json")["rows"]]
    pages = {PAGE: build_page(doc, counts, integ_rows), "review/" + PAGE: build_page(doc, counts, integ_rows, review=True)}
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
        print("wrote docs/%s (%d bytes, %d tracker rows)" % (name, len(page), len(doc["rows"])))


if __name__ == "__main__":
    main()
