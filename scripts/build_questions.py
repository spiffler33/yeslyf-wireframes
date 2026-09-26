#!/usr/bin/env python3
"""The Spinach Questions tab (phase 14, pass 3; Vatsal, 24 Sep 2026): docs/spinach_questions.html from data/questions.json.
HoA's working view (Vatsal, 26 Sep 2026): the tab is not on the review link and Spinach never sees it; Spinach receives
the questionnaire files back, filled (scripts/export_sq.py, pass 4).

One page, three sub-tabs (Frontend, Backend, Journey; one per file of the batch), the rows grouped by sheet in sheet
order with the sheet's own name as the heading; the Journey sub-tab shows the summary sheet first, then the five
journeys with their blocks (header block, workflow, edge cases, API summary, merge suggestion) as sub-headings; Part D
and Part E of the answer set open the Frontend sub-tab as two tables. Filters: status (all, frozen, open, owed; the
word in the URL hash opens the tab on those rows, spinach_questions.html#open), batch, and a text filter on id and
text. A row shows its id (the anchor), the status word, Spinach's question (one line; the full cell on tap), their
proposal folded, the Yesly comment in full, the refs as links, the owner and the proposed date on open and owed rows,
the cause and the changed date. Journey rows also name their block and the sheet row they answer.

Controls: the identity picker and a comment box per row (page spinach_questions, item_id the row id, field
comment, kind comment; written 1.5 s after typing stops, as on the Wireframes v0.2 tab) and, on open and owed rows,
Approve and Dispute (field approve, kind verdict, value approved or disputed; a dispute opens the comment box and
asks for the position in words). The latest verdict per row and the comment history are read from the board table
and shown under the row. The status word changes only by a commit (scripts/apply_sq_approvals.py, pass 5).

Spinach's own cells are shown verbatim: non-ASCII characters become numeric entities so the page stays ASCII, and
the banned-word check runs over the page with their cells blanked (their text is theirs; HoA's chrome and answers
carry none of the words). Called at the end of scripts/build_site.py (after build_tracker.main()); also runs alone.
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

PAGE = "spinach_questions.html"
BOARD_PAGE = "spinach_questions"
DATA_FILE = os.path.join(DATA, "questions.json")
EXPORT_DIR = "exports"
IDENTITIES = ["Bhuvanaa", "Harish", "Gaurav", "Kajal", "Somil", "Raafiya", "Vatsal", "Compliance"]  # HoA's tab: Spinach never sees it
STATUSES = ["frozen", "open", "owed"]
SUBTABS = [("frontend", "Frontend", "FE"), ("backend", "Backend", "BE"), ("journey", "Journey", "JD")]
BLOCK_NAMES = {"H": "Header block", "W": "Workflow", "E": "Edge cases", "API": "API summary", "M": "Merge suggestion"}
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
WIRE = "wireframes_v02.html"
LITERAL_LINKS = {"Events": "events.html", "Wireframes v0.2": WIRE, "Part D": "#part-d", "Part E": "#part-e", "D spine": WIRE + "#D01"}
esc = site.esc


def escx(s):
    """HTML-escaped, with every non-ASCII character as a numeric entity, so Spinach's text stays verbatim on an ASCII page."""
    return "".join(ch if ord(ch) < 127 else "&#%d;" % ord(ch) for ch in esc(s))


def dmy(iso):
    if not iso or len(iso) < 10:
        return ""
    return "%d %s %s" % (int(iso[8:10]), MONTHS[int(iso[5:7]) - 1], iso[:4])


def ref_link(ref, ctx):
    wire = "index.html" if ctx["review"] else WIRE
    title = ""
    if ref in ctx["questions"]:
        href = "#" + ref
    elif ref in ctx["screens"]:
        href = wire + "#" + ref
    elif ref in ctx["states"]:
        href = wire + "#N01"
        title = ' title="state %s: the states table is N01"' % esc(ref)
    elif ref in ctx["integrations"]:
        href = "integrations.html#row/" + ref
    elif ref in ctx["trackers"]:
        href = "tracker.html#row/" + ref
    elif ref in LITERAL_LINKS:
        href = LITERAL_LINKS[ref].replace(WIRE, wire)
    else:
        return '<span class="ref">%s</span>' % escx(ref)
    return '<a class="ref" href="%s"%s>%s</a>' % (esc(href), title, escx(ref))


def counts(rows):
    out = {"all": len(rows)}
    for s in STATUSES:
        out[s] = sum(1 for r in rows if r["status"] == s)
    return out


def count_text(c):
    return "%d frozen, %d open, %d owed" % (c["frozen"], c["open"], c["owed"])


def render_row(r, ctx):
    """One question row. their() blanks Spinach's cells when the page is built for the banned-word check."""
    their = ctx["their"]
    rid, st = r["id"], r["status"]
    head = ['<a class="sid" href="#%s">%s</a>' % (esc(rid), esc(rid)), '<span class="tag st-%s">%s</span>' % (esc(st), esc(st))]
    if r["block"] in BLOCK_NAMES:
        head.append('<span class="meta">%s, sheet row %d: %s</span>' % (esc(BLOCK_NAMES[r["block"]]), r["row_no"], their(r["row"])))
    if r["area"]:
        head.append('<span class="meta">%s</span>' % their(r["area"]))
    head.append('<span class="meta chg">changed %s</span>' % esc(dmy(r["changed"])))
    first = (r["question"].split("\n")[0] if r["question"] else "") or "(no text in the cell)"
    body = ['<details class="qq"><summary title="their question; open for the full cell">%s</summary><div class="cell">%s</div></details>' % (their(first), their(r["question"]))]
    if r["proposal"]:
        body.append('<details class="prop"><summary>their proposal</summary><div class="cell">%s</div></details>' % their(r["proposal"]))
    if r["link"]:
        body.append('<div class="meta">their link: %s</div>' % their(r["link"]))
    body.append('<div class="ans">%s</div>' % escx(r["answer"]))
    if r["refs"]:
        body.append('<div class="refs">refs: %s</div>' % " ".join(ref_link(x, ctx) for x in r["refs"]))
    if st != "frozen":
        due = (dmy(r["due"]) + (" (proposed)" if r["due_about"] else "")) if r["due"] else "no date"
        body.append('<div class="own">owner: %s; due %s</div>' % (esc(r["owner"] or "-"), esc(due)))
    if r["cause"]:
        body.append('<div class="cause">cause: %s</div>' % esc("; ".join(r["cause"])))
    else:
        body.append('<div class="cause">cause: none until the row is frozen; the freezing commit writes approved by (first name), (date)</div>')
    ctl = []
    if st != "frozen":
        ctl.append('<button type="button" class="ok" data-approve="approved" data-id="%s">Approve</button>' % esc(rid))
        ctl.append('<button type="button" class="dis" data-approve="disputed" data-id="%s">Dispute</button>' % esc(rid))
    ctl.append('<textarea class="note" data-comment="%s" placeholder="comment, free text; recorded under your name"></textarea>' % esc(rid))
    text = " ".join([rid, r["area"], r["row"], r["question"], r["answer"], " ".join(r["refs"])]).lower()
    return ('<article class="qrow" id="%s" data-status="%s" data-batch="%s" data-text="%s"><div class="qh">%s</div>%s'
            '<div class="ctl">%s</div><div class="vbox" data-verdict-for="%s"></div></article>' % (
                esc(rid), esc(st), esc(r["batch"]), their(text), "".join(head), "".join(body), "".join(ctl), esc(rid)))


def sheet_sections(rows, ctx, journey=False):
    """The rows of one file grouped by sheet (and, for the journey file, by block) in sheet order."""
    out = []
    sheets = []
    for r in rows:
        key = (r["sheet_order"], r["sheet"])
        if key not in sheets:
            sheets.append(key)
    for order, name in sheets:
        srows = sorted([r for r in rows if r["sheet"] == name], key=lambda x: x["row_no"])
        c = counts(srows)
        inner = []
        if journey and any(r["block"] in BLOCK_NAMES for r in srows):
            blocks = []
            for r in srows:
                if r["block"] not in blocks:
                    blocks.append(r["block"])
            for b in blocks:
                brows = [r for r in srows if r["block"] == b]
                inner.append('<div class="blk"><h3>%s<small class="meta"> %d</small></h3>%s</div>' % (esc(BLOCK_NAMES.get(b, b)), len(brows), "".join(render_row(r, ctx) for r in brows)))
        else:
            inner.append("".join(render_row(r, ctx) for r in srows))
        out.append('<section class="sheet" id="sheet-%d-%s"><h2>%s<small><span data-shown>%d</span> of %d rows; %s</small></h2>%s</section>' % (
            order, esc(ctx["family"]), ctx["their"](name.strip()), len(srows), len(srows), esc(count_text(c)), "".join(inner)))
    return "".join(out)


def parts_tables(doc):
    d = site.table_html(["Template", "Screens", "Android back", "Loading", "Keyboard", "Validation"],
                        [[esc(t["template"]), esc(t["screens"]), esc(t["back"]), esc(t["loading"]), esc(t["keyboard"]), esc(t["validation"])] for t in doc["templates"]])
    e = site.table_html(["Group", "Screens", "Who", "Rule"], [[esc(g["group"]), esc(g["screens"]), esc(g["who"]), esc(g["rule"])] for g in doc["route_groups"]])
    return ('<section id="part-d" class="part"><h2>Part D: behaviour by template<small>referenced by FE-10, FE-24, FE-28, FE-29, FE-53; %d rows</small></h2>%s</section>'
            '<section id="part-e" class="part"><h2>Part E: route-access map<small>FE-05, FE-06; %d groups</small></h2>%s</section>' % (len(doc["templates"]), d, len(doc["route_groups"]), e))


def export_line(batch, f, review):
    """The download link of a file's export and the export date, once pass 4 has written it."""
    if not batch.get("exported"):
        return ""
    path = os.path.join(DOCS, EXPORT_DIR, f["export"])
    if not os.path.exists(path):
        return ""
    href = ("../" if review else "") + EXPORT_DIR + "/" + f["export"]
    return '<p class="meta exp">Export of %s: <a href="%s">%s</a> (xlsx, Spinach\'s layout, the Yesly Comments column filled)</p>' % (esc(dmy(batch["exported"])), esc(href), esc(f["export"]))


EXTRA_CSS = integ.EXTRA_CSS + """
  .qtabs{margin:0 0 14px;padding:0 0 8px;border-bottom:1px solid var(--line);gap:4px}
  .qtabs a{cursor:pointer;display:flex;gap:6px;align-items:baseline} .qtabs a small{color:var(--mute);font-size:11px;font-weight:400}
  .toolbar .chip b{margin-left:3px}
  .toolbar input{padding:5px 7px;border:1px solid var(--line);border-radius:5px;background:#fff;width:220px}
  .part table{font-size:12px} .part td{white-space:pre-wrap}
  .qrow{border:1px solid var(--line);border-radius:8px;padding:10px 12px;margin:0 0 8px;background:#FCFCFD;scroll-margin-top:60px}
  .qrow.hi{border-color:#C9A800;box-shadow:0 0 0 3px var(--accent-soft)}
  .qrow[hidden],section.sheet[hidden],.blk[hidden]{display:none}
  .qh{display:flex;gap:8px;align-items:baseline;flex-wrap:wrap;margin-bottom:4px} .qh .chg{margin-left:auto}
  .tag.st-frozen{background:var(--ink);color:#fff;border-color:var(--ink)}
  .tag.st-open{border-color:#C9A800;background:var(--accent-soft);color:var(--ink)}
  .tag.st-owed{border-color:#C9A800;border-style:dashed;color:var(--ink);background:#fff}
  details.qq{margin:2px 0} details.qq summary{font-weight:600;font-size:13px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;display:block;max-width:100%}
  details.qq[open] summary{white-space:normal}
  .cell{white-space:pre-wrap;font-size:12.5px;color:#3B4250;margin:4px 0 6px;padding-left:10px;border-left:3px solid var(--line)}
  details.prop{margin:2px 0} details.prop summary{font-weight:400;font-size:12px;color:var(--mute)}
  .ans{margin:6px 0;padding-left:10px;border-left:3px solid var(--accent);white-space:pre-wrap;font-size:13px}
  .refs{font-size:12px;color:var(--mute);margin-top:4px} .refs .ref{font-weight:600;text-decoration:none;border:1px solid var(--line);padding:0 4px;border-radius:4px;background:#fff;margin-right:2px;font-size:11px;color:var(--ink)}
  .own{font-size:12.5px;margin-top:4px} .qrow .cause{margin-top:4px}
  .ctl{display:flex;gap:8px;align-items:flex-start;flex-wrap:wrap;margin-top:8px} .ctl textarea{flex:1;min-width:260px;min-height:34px;margin-top:0}
  .ctl button{border:1px solid var(--ink);background:#fff;padding:5px 10px;border-radius:6px;cursor:pointer;font-weight:600} .ctl button.dis{border-color:#8A2E2E;color:#8A2E2E}
  .vbox{margin-top:6px;font-size:12.5px} .vbox .vline{font-weight:600} .vbox .clist{margin:4px 0 0;padding-left:16px;font-size:12px}
  .blk h3{margin:14px 0 6px} .blk h3 small{margin-left:6px}
  .exp{margin:0 0 10px}
  .todo{margin:4px 0 12px;padding-left:18px;font-size:12.5px} .todo li{margin:4px 0}
"""

JS = r"""
(function(){
  var KEY="yeslyf_sq_v1"; var S={}; try{ S=JSON.parse(localStorage.getItem(KEY)||"{}")||{}; }catch(e){ S={}; }
  if(!S.who) S.who=""; if(!S.comments) S.comments={}; if(!S.verdicts) S.verdicts={};
  var BOARD=window.yeslyfBoard||null;
  var MONTHS=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  var STATUS_WORDS=["all","frozen","open","owed"], VIEWS=["frontend","backend","journey"];
  function save(){ try{ localStorage.setItem(KEY, JSON.stringify(S)); }catch(e){} }
  function esc(s){ return String(s===undefined||s===null?"":s).split("&").join("&amp;").split("<").join("&lt;").split(">").join("&gt;").split('"').join("&quot;"); }
  var ft; function flash(t){ var s=document.getElementById("saved"); if(!s) return; s.textContent=t||"Recorded"; clearTimeout(ft); ft=setTimeout(function(){ s.textContent=""; },2200); }
  function dmyTs(ts){ var d=new Date(String(ts||"").slice(0,19)+"Z"); if(isNaN(d.getTime())) return String(ts||""); return d.getDate()+" "+MONTHS[d.getMonth()]+" "+d.getFullYear(); }
  var rows=Array.prototype.slice.call(document.querySelectorAll("article.qrow"));
  var state={status:"all", batch:"all", text:""};
  function show(view){ Array.prototype.forEach.call(document.querySelectorAll("[data-viewpane]"), function(p){ p.hidden=p.getAttribute("data-viewpane")!==view; });
    Array.prototype.forEach.call(document.querySelectorAll(".qtabs a[data-view]"), function(a){ a.className=a.getAttribute("data-view")===view?"on":""; }); }
  function applyFilters(){ var n=0, perView={};
    rows.forEach(function(a){ var ok=(state.status==="all"||a.getAttribute("data-status")===state.status)&&(state.batch==="all"||a.getAttribute("data-batch")===state.batch)&&(!state.text||a.getAttribute("data-text").indexOf(state.text)>=0);
      a.hidden=!ok; if(ok){ n++; var p=a.closest("[data-viewpane]"); if(p){ var v=p.getAttribute("data-viewpane"); perView[v]=(perView[v]||0)+1; } } });
    Array.prototype.forEach.call(document.querySelectorAll("section.sheet"), function(sec){ var vis=sec.querySelectorAll("article.qrow:not([hidden])").length; sec.hidden=!vis; var c=sec.querySelector("[data-shown]"); if(c) c.textContent=vis; });
    Array.prototype.forEach.call(document.querySelectorAll(".blk"), function(b){ b.hidden=!b.querySelectorAll("article.qrow:not([hidden])").length; });
    Array.prototype.forEach.call(document.querySelectorAll(".toolbar .chip[data-status]"), function(c){ c.className="chip"+(c.getAttribute("data-status")===state.status?" on":""); });
    Array.prototype.forEach.call(document.querySelectorAll(".qtabs a[data-view] [data-shown]"), function(el){ el.textContent=perView[el.getAttribute("data-shown")]||0; });
    var sh=document.getElementById("shown"); if(sh) sh.textContent=n+" of "+rows.length+" rows shown"; }
  function setStatus(s, fromHash){ state.status=s; applyFilters(); if(!fromHash){ try{ history.replaceState(null,"",s==="all"?location.pathname+location.search:"#"+s); }catch(e){} } }
  function onHash(){ var h=decodeURIComponent(location.hash.replace("#","")); if(!h) return;
    if(STATUS_WORDS.indexOf(h)>=0){ setStatus(h,true); return; }
    if(VIEWS.indexOf(h)>=0){ show(h); return; }
    var el=document.getElementById(h); if(!el) return;
    var pane=el.closest("[data-viewpane]"); if(pane) show(pane.getAttribute("data-viewpane"));
    if(el.classList.contains("qrow")&&el.hidden){ state.status="all"; state.text=""; var ft2=document.getElementById("ftext"); if(ft2) ft2.value=""; applyFilters(); }
    var old=document.querySelectorAll(".hi"); for(var i=0;i<old.length;i++) old[i].classList.remove("hi"); el.classList.add("hi");
    try{ el.scrollIntoView({block:"start",behavior:"instant"}); }catch(e){ el.scrollIntoView(true); } }
  function put(id, field, value, kind){ if(!BOARD) return true; var ok=BOARD.write({item_id:id, field:field, value:value, who:S.who||"", kind:kind}); if(!ok) setTimeout(function(){ flash(BOARD.noIdentity); },0); return ok; }
  function localRows(){ var out=[], id; for(id in S.comments) out.push({item_id:id, field:"comment", value:S.comments[id]||"", kind:"comment"}); for(id in S.verdicts) out.push({item_id:id, field:"approve", value:S.verdicts[id]||"", kind:"verdict"}); return out; }
  function paintRow(id){ var box=document.querySelector('[data-verdict-for="'+id+'"]'); if(!box||!BOARD) return; var hist=BOARD.history(id); var v=null, i;
    for(i=0;i<hist.length;i++){ if(hist[i].field==="approve"&&hist[i].value){ v=hist[i]; break; } }
    var html="";
    if(v){ var line=esc(v.value)+" by "+esc(v.who||"(no name yet)")+", "+esc(dmyTs(v.created_at));
      if(v.value==="disputed"){ var c=null; for(i=0;i<hist.length;i++){ var r=hist[i]; if(r.field==="comment"&&r.who===v.who&&String(r.created_at).slice(0,19)>=String(v.created_at).slice(0,19)&&String(r.value||"").trim()){ c=r; break; } }
        line+=c?": "+esc(c.value):": the position is still to be written in the comment box"; }
      html+='<div class="vline">'+line+(v.held?' <i>(waiting for a name)</i>':v.queued?' <i>(queued)</i>':'')+'</div>'; }
    var comments=hist.filter(function(r){ return r.field==="comment"&&String(r.value||"").trim(); });
    if(comments.length) html+='<ul class="clist">'+comments.map(function(r){ return '<li><b>'+esc(r.who||"(no name yet)")+'</b>, '+esc(dmyTs(r.created_at))+': '+esc(r.value)+'</li>'; }).join("")+'</ul>';
    box.innerHTML=html; }
  function paintAll(){ rows.forEach(function(a){ paintRow(a.id); }); }
  function applyRemote(latest){ latest.forEach(function(r){ if(r.field!=="comment") return; var ta=document.querySelector('textarea[data-comment="'+r.item_id+'"]'); if(ta&&S.comments[r.item_id]===undefined) ta.value=r.value||""; }); paintAll(); }
  var timers={};
  document.addEventListener("DOMContentLoaded", function(){
    var rv=document.getElementById("reviewer"); if(rv){ rv.innerHTML='<option value="">reviewing as</option>'+IDENTITIES.map(function(n){ return '<option value="'+esc(n)+'">'+esc(n)+'</option>'; }).join(""); rv.value=S.who||"";
      rv.addEventListener("change", function(){ S.who=IDENTITIES.indexOf(rv.value)>=0?rv.value:""; save(); var n=(BOARD&&S.who)?BOARD.named(S.who):0; flash(S.who?"Reviewing as "+S.who+(n?"; "+n+(n===1?" edit":" edits")+" recorded":""):""); paintAll(); }); }
    Array.prototype.forEach.call(document.querySelectorAll(".qtabs a[data-view]"), function(a){ a.addEventListener("click", function(ev){ ev.preventDefault(); show(a.getAttribute("data-view")); }); });
    Array.prototype.forEach.call(document.querySelectorAll(".toolbar .chip[data-status]"), function(c){ c.addEventListener("click", function(){ setStatus(c.getAttribute("data-status")); }); });
    var fb=document.getElementById("fbatch"); if(fb) fb.addEventListener("change", function(){ state.batch=fb.value; applyFilters(); });
    var ftx=document.getElementById("ftext"), tt; if(ftx) ftx.addEventListener("input", function(){ clearTimeout(tt); tt=setTimeout(function(){ state.text=ftx.value.trim().toLowerCase(); applyFilters(); },150); });
    Array.prototype.forEach.call(document.querySelectorAll("textarea[data-comment]"), function(ta){ var id=ta.getAttribute("data-comment");
      if(S.comments[id]!==undefined) ta.value=S.comments[id];
      if(BOARD) BOARD.attach(ta, id);
      ta.addEventListener("input", function(){ S.comments[id]=ta.value; save(); flash("Saving..."); clearTimeout(timers[id]); timers[id]=setTimeout(function(){ if(put(id,"comment",S.comments[id]||"","comment")) flash(); paintRow(id); },1500); }); });
    document.body.addEventListener("click", function(e){ var b=e.target.closest?e.target.closest("button[data-approve]"):null; if(!b) return; var id=b.getAttribute("data-id"), v=b.getAttribute("data-approve");
      S.verdicts[id]=v; save(); var ok=put(id,"approve",v,"verdict"); paintRow(id);
      var ta=document.querySelector('textarea[data-comment="'+id+'"]');
      if(v==="disputed"){ if(ta){ ta.placeholder="Say why: your position, in words, goes here"; ta.focus(); } flash("Disputed: write your position in the comment box"); }
      else flash(ok?"Approved by "+(S.who||"(no name yet)")+"; the status word changes by a commit":""); });
    if(BOARD) BOARD.init({page:PAGE_ID, apply:applyRemote, who:S.who||"", local:localRows});
    applyFilters(); onHash(); window.addEventListener("hashchange", onHash);
  });
  window.yeslyfQuestions={ rows: function(){ return rows.length; }, setStatus: setStatus, shown: function(){ return rows.filter(function(a){ return !a.hidden; }).length; } };
})();
"""


def build_page(doc, ctx, review=False, redact=False):
    ctx = dict(ctx, review=review, their=(lambda s: "") if redact else escx)
    rows = doc["rows"]
    batch = doc["batches"][0]
    total = counts(rows)
    who = '<div class="who">Reviewing as <select id="reviewer"></select></div>'
    pending = [r for r in rows if r["status"] != "frozen"]
    todo = "".join('<li><a class="sid" href="#%s">%s</a> <span class="tag st-%s">%s</span> %s <span class="meta">%s; due %s</span></li>' % (
        esc(r["id"]), esc(r["id"]), esc(r["status"]), esc(r["status"]), escx(r["item"] or r["answer"].split("\n")[0]), esc(r["owner"]),
        esc((dmy(r["due"]) + (" (proposed)" if r["due_about"] else "")) if r["due"] else "no date")) for r in pending)
    lead = ('<section><h1>Spinach questions</h1>'
            '<p class="lead">HoA\'s working view of every questionnaire Spinach sends: one sub-tab per file, every row with its answer (the Yesly comment) and one of three words: '
            'frozen (the answer stands), open (to be decided: an item HoA still decides), owed (to be verified: a fact somebody verifies first). '
            'Open and owed rows carry an owner and a proposed date. Approval is a comment under your name on the row (Approve, or Dispute with your position in words); '
            'the status word changes only by a commit, never on the page. Spinach never sees this tab: it receives the questionnaire files back, '
            'in its own layout, with the Yesly Comments column filled (the exports below).</p>'
            '<h3>Open and owed: what the team decides or verifies<small class="meta"> %d rows</small></h3><ul class="todo">%s</ul>'
            '<p class="meta">Batch %s: received %s, answered %s; %d rows, %s. Refs open the screen, state, integration or tracker row they name.</p>'
            '<div class="toolbar" id="qfilters"><span class="k">Status</span>%s<label>Batch <select id="fbatch"><option value="all">all</option>%s</select></label>'
            '<label>Find <input id="ftext" placeholder="id or text"></label><span id="shown" class="meta"></span></div></section>' % (
                len(pending), todo, esc(batch["id"]), esc(dmy(batch["received"])), esc(dmy(batch["answered"])), total["all"], esc(count_text(total)),
                "".join('<button type="button" class="chip%s" data-status="%s">%s<b>%d</b></button>' % (" on" if s == "all" else "", s, s, total[s]) for s in ["all"] + STATUSES),
                "".join('<option>%s</option>' % esc(b["id"]) for b in doc["batches"])))
    by_family = {fam: [r for r in rows if r["id"].startswith(fam + "-")] for _, _, fam in SUBTABS}
    files = {f["family"]: f for f in batch["files"]}
    tabs = "".join('<a data-view="%s"%s>%s <b><span data-shown="%s">%d</span> of %d</b><small>%s</small></a>' % (
        vid, ' class="on"' if i == 0 else "", esc(label), vid, len(by_family[fam]), len(by_family[fam]), esc(count_text(counts(by_family[fam])))) for i, (vid, label, fam) in enumerate(SUBTABS))
    panes = []
    for i, (vid, label, fam) in enumerate(SUBTABS):
        fctx = dict(ctx, family=fam)
        inner = export_line(batch, files[fam], review) if fam in files else ""
        if fam == "FE":
            inner += parts_tables(doc)
        inner += sheet_sections(by_family[fam], fctx, journey=(fam == "JD"))
        panes.append('<div data-viewpane="%s"%s>%s</div>' % (vid, "" if i == 0 else " hidden", inner))
    blob = '<script>var IDENTITIES=%s;\nvar PAGE_ID=%s;\nvar REVIEW=%s;</script>\n' % (site.js_blob(IDENTITIES), site.js_blob(BOARD_PAGE), site.js_blob(bool(review)))
    return (site.head("yeslyf Spinach questions", site.CSS + EXTRA_CSS, config="../config.js" if review else "config.js") + '<body>\n' +
            site.header(PAGE, "Spinach questions, %s: %d rows" % (batch["id"], total["all"]), who_html=who, show_export=False,
                        tabs=site.REVIEW_TABS if review else None, setup_link=not review) +
            '<main class="main" style="max-width:none">' + lead + '<nav class="tabs views qtabs">' + tabs + '</nav>' + "".join(panes) + '</main>\n' +
            blob + site.store_script() + '<script>' + JS + '</script>\n</body>\n</html>\n')


def context():
    screens = site.load("screens_v02.json")["screens"]
    live = {s["id"] for s in screens if s["v02"]["status"] not in ("dropped", "split")}
    states = {s["id"] for s in site.load("v02/states.json")["states"]}
    return {"screens": live, "states": states, "integrations": {r["id"] for r in site.load("integrations.json")["rows"]},
            "trackers": {r["id"] for r in site.load("tracker.json")["rows"]}}


def main():
    with open(DATA_FILE) as fh:
        raw = fh.read()
    site.check_ascii("data/questions.json", raw)
    doc = json.loads(raw)
    ctx = context()
    ctx["questions"] = {r["id"] for r in doc["rows"]}
    errors = []
    for r in doc["rows"]:
        if r["status"] not in STATUSES:
            errors.append("%s: status %r" % (r["id"], r["status"]))
        if r["status"] != "frozen" and not r["owner"]:
            errors.append("%s: no owner on an %s row" % (r["id"], r["status"]))
    pages, checks = {}, {}
    for review in (False,):  # one copy: the tab is HoA's and is not on the review link (Vatsal, 26 Sep 2026)
        name = ("review/" if review else "") + PAGE
        pages[name] = build_page(doc, ctx, review=review)
        checks[name] = build_page(doc, ctx, review=review, redact=True)  # Spinach's cells blanked: the banned words are checked over HoA's text
    for name, page in pages.items():
        site.check_ascii(name, page)
        if 'name="robots" content="noindex' not in page:
            errors.append(name + " lacks noindex")
        for word in site.FORBIDDEN:
            i = checks[name].find(word)
            while i >= 0:
                errors.append("%s contains %r outside Spinach's cells: ...%s..." % (name, word, checks[name][max(0, i - 50):i + len(word) + 30].replace("\n", " ")))
                i = checks[name].find(word, i + 1)
        if page.count('class="qrow"') != len(doc["rows"]):
            errors.append("%s draws %d rows, expected %d" % (name, page.count('class="qrow"'), len(doc["rows"])))
    if errors:
        for e in errors:
            print("ERROR: " + e)
        sys.exit(1)
    os.makedirs(os.path.join(DOCS, "review"), exist_ok=True)
    c = counts(doc["rows"])
    for name, page in pages.items():
        with open(os.path.join(DOCS, name), "w") as fh:
            fh.write(page)
        print("wrote docs/%s (%d bytes, %d rows: %s)" % (name, len(page), c["all"], count_text(c)))


if __name__ == "__main__":
    main()
