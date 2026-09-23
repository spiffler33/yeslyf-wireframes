#!/usr/bin/env python3
"""Generate docs/admin_seats.html from data/seats.json (PLAN_admin_seed_v01.md section 15, deliverable D7; phase D
part 1, 23 Sep 2026).

The seats page: eight operator seats, each with the questions it asks, where the answer lives (the admin tab, Zoho
or a vendor console) and whether the seed plus that surface answers it. A "no" is a gap; gaps land on the brief
page (admin_brief.html, built separately). Same board pattern as scripts/build_operator.py: an "Editing as" name
control, a select per question writing {field: "answered", ...}, a comment box writing {field: "note", ...}
debounced, held edits when nobody is named yet, and a local cache that a live board row overrides.

data/seats.json contract (one row per seat, in the file's own order; PLAN_admin_seed_v01.md section 15):
  {"seats": [{"id": "<seat id>", "seat": "<seat name>", "questions": [
      {"id": "<prefix>-NN", "question": "...", "surface": "Admin tab" | "Zoho" | "vendor console",
       "screen": "<M id>" | "<Zoho view name>" | "<I-number and console, e.g. I09 dashboard>",
       "answered": "yes" | "no", "gap": "" | "<one sentence>", "brief": "T1".."T6",
       "view": {"object": "...", "name": "...", "criteria": "..."},   # only when surface is Zoho
       "cause": "..."}]}]}
The eight seat ids and names, and each seat's question-id prefix, are fixed below (SEATS); a question id is not
free text, it is a stable board item_id forever.

main() reads data/seats.json, validates it against the contract, and raises SystemExit with a clear message when the
file is missing or breaks the contract: any seat present is one of the eight, named exactly, with question ids unique
and in that seat's prefix-NN form. Called from build_site.main(); also runs on its own.
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

PAGE = "admin_seats.html"
DATA_FILE = os.path.join(DATA, "seats.json")
esc = site.esc

IDENTITIES = ["Bhuvanaa", "Harish", "Gaurav", "Kajal", "Somil", "Raafiya", "Vatsal", "Spinach", "Compliance"]
SURFACES = ["Admin tab", "Zoho", "vendor console"]
ANSWERED = ["yes", "no"]
BRIEFS = ["T1", "T2", "T3", "T4", "T5", "T6"]

# seat id -> (seat name, question id prefix), the contract's fixed eight, in plan section 15's order.
SEATS = [
    ("principal-officer", "Principal officer", "po"),
    ("adviser", "Adviser", "ad"),
    ("call-centre", "Call centre", "cc"),
    ("ops", "Ops", "op"),
    ("marketing", "Marketing", "mk"),
    ("compliance", "Compliance", "co"),
    ("support", "Support", "su"),
    ("finance", "Finance", "fi"),
]
SEAT_BY_ID = {sid: (name, prefix) for sid, name, prefix in SEATS}


def qid_ok(qid, prefix):
    # "<prefix>-NN": the prefix, a dash, exactly two digits. A closed, machine-defined format: a character check,
    # not a pattern rule (CLAUDE.md's no-regex line).
    head = prefix + "-"
    if not qid.startswith(head):
        return False
    digits = qid[len(head):]
    return len(digits) == 2 and digits.isdigit()


def validate(doc, screen_ids, integration_ids, order):
    problems = []
    seats = doc.get("seats")
    if not isinstance(seats, list):
        return ["seats.json needs a top-level \"seats\" list"]
    seat_ids_seen = set()
    qids_seen = set()
    for seat in seats:
        sid = seat.get("id", "")
        name = seat.get("seat", "")
        known = SEAT_BY_ID.get(sid)
        if not known:
            problems.append("seat %r: not one of the eight seats the contract names" % sid)
            continue
        if sid in seat_ids_seen:
            problems.append("seat %r: duplicate" % sid)
        seat_ids_seen.add(sid)
        want_name, prefix = known
        if name != want_name:
            problems.append("seat %r: seat name is %r, expected %r" % (sid, name, want_name))
        for q in seat.get("questions", []):
            qid = q.get("id", "")
            if not qid_ok(qid, prefix):
                problems.append("question %r: id is not in the contract's form %s-NN" % (qid, prefix))
            if qid in qids_seen:
                problems.append("question %r: duplicate id" % qid)
            qids_seen.add(qid)
            if not str(q.get("question", "")).strip():
                problems.append("question %r: question text is empty" % qid)
            surface = q.get("surface", "")
            if surface not in SURFACES:
                problems.append("question %r: surface %r is not one of %s" % (qid, surface, ", ".join(SURFACES)))
            answered = q.get("answered", "")
            if answered not in ANSWERED:
                problems.append("question %r: answered %r is not yes or no" % (qid, answered))
            if answered == "no" and not str(q.get("gap", "")).strip():
                problems.append("question %r: answered no with no gap text" % qid)
            if "pair" in q and not (isinstance(q["pair"], list) and len(q["pair"]) == 2 and q["pair"][0] != q["pair"][1]
                                    and all(s in order for s in q["pair"])):
                problems.append("question %r: pair %r is not two states of the section 7 precedence order" % (qid, q.get("pair")))
            brief = q.get("brief", "")
            if brief not in BRIEFS:
                problems.append("question %r: brief %r is not one of %s" % (qid, brief, ", ".join(BRIEFS)))
            screen = str(q.get("screen", ""))
            if surface == "Zoho":
                view = q.get("view") or {}
                if not (str(view.get("object", "")).strip() and str(view.get("name", "")).strip() and str(view.get("criteria", "")).strip()):
                    problems.append("question %r: surface is Zoho with no view {object, name, criteria}" % qid)
            elif surface == "Admin tab":
                if screen not in screen_ids:
                    problems.append("question %r: screen %r is not a screen in data/admin_screens.json" % (qid, screen))
            elif surface == "vendor console":
                inum = screen.split(" ")[0] if screen else ""
                if inum not in integration_ids:
                    problems.append("question %r: screen %r does not start with an I-number in data/integrations.json" % (qid, screen))
    return problems


def screen_html(q, ctx):
    surface = q["surface"]
    screen = str(q.get("screen", ""))
    if surface == "Admin tab":
        return '<a href="admin_wireframes.html#%s">%s</a>' % (esc(screen), esc(screen))
    if surface == "Zoho":
        view = q.get("view") or {}
        label = "%s (%s)" % (view.get("name", ""), view.get("object", ""))
        return '<a href="admin_operator.html">%s</a>' % esc(label)
    inum = screen.split(" ")[0] if screen else ""
    vendor = ctx["integ_by_id"].get(inum, {}).get("vendor", inum)
    return esc("%s (%s)" % (inum, vendor))


def precedence_order():
    with open(os.path.join(ROOT, "seed", "config.json")) as fh:
        return json.load(fh)["precedence"]["order"]


def proposal(q, order):
    """For an N01 state-pair question: the pair's winner under the section 7 precedence order, worded as a proposal
    the admin session confirms rather than invents (Vatsal, 23 Sep 2026); "" for any other question."""
    pair = q.get("pair")
    if not pair:
        return ""
    return "%s wins under the section 7 precedence order: proposed, to be confirmed at the admin session." % min(pair, key=order.index)


def render_question(q, ctx):
    qid = q["id"]
    ans = q.get("answered", "no")
    opts = "".join('<option value="%s"%s>%s</option>' % (v, " selected" if ans == v else "", v) for v in ANSWERED)
    sel = '<select class="ans" id="ans-%s" data-id="%s">%s</select>' % (esc(qid), esc(qid), opts)
    box = '<textarea class="note seatnote" id="note-%s" data-id="%s"></textarea>' % (esc(qid), esc(qid))
    return ('<tr id="row-%s"><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td class="gaptext">%s</td><td>%s</td></tr>' % (
        esc(qid), esc(qid), esc(q["question"]), esc(q["surface"]), screen_html(q, ctx), sel,
        esc(q.get("gap", "")) + ('<div class="proposed">%s</div>' % esc(q["proposed"]) if q.get("proposed") else ""), box))


def render_seat(seat, ctx):
    rows = "".join(render_question(q, ctx) for q in seat["questions"])
    return ('<section id="seat-%s"><h2>%s</h2><div class="wrap"><table><thead><tr>'
            '<th>Question id</th><th>Question</th><th>Surface</th><th>Screen</th><th>Answered</th><th>Gap</th><th>Comment</th>'
            '</tr></thead><tbody>%s</tbody></table></div></section>' % (esc(seat["id"]), esc(seat["seat"]), rows))


EXTRA_CSS = """
  .proposed{margin-top:4px;color:var(--ink)}
  .who select{padding:6px 8px;border:1px solid var(--line);border-radius:6px;background:#fff;max-width:170px}
  td select.ans{padding:4px 6px;border:1px solid var(--line);border-radius:5px;background:#fff}
  td textarea.seatnote{width:100%;min-height:36px;border:1px solid var(--line);border-radius:6px;padding:5px;resize:vertical;background:#fff;font-size:12px}
  td.gaptext{font-size:12px;color:var(--mute);max-width:220px}
"""

JS = r"""
(function(){
  var KEY="yeslyf_seats_v1";
  var byId={}; QUESTIONS.forEach(function(q){ byId[q.id]=q; });
  var S={}; try{ S=JSON.parse(localStorage.getItem(KEY)||"{}")||{}; }catch(e){ S={}; }
  if(!S.rows) S.rows={}; if(!S.who) S.who="";
  function save(){ try{ localStorage.setItem(KEY, JSON.stringify(S)); }catch(e){} }
  var ft; function flash(t){ var s=document.getElementById("saved"); if(!s) return; s.textContent=t||"Saved in this browser"; clearTimeout(ft); ft=setTimeout(function(){ s.textContent=""; },1800); }
  function esc(s){ return String(s===undefined||s===null?"":s).split("&").join("&amp;").split("<").join("&lt;").split(">").join("&gt;").split('"').join("&quot;"); }
  function row(id){ if(!S.rows[id]) S.rows[id]={}; return S.rows[id]; }
  function val(id){ var e=S.rows[id]; if(e&&e.answered!==undefined) return e.answered; var q=byId[id]; return q?q.answered:"no"; }
  function noteVal(id){ var e=S.rows[id]; return (e&&e.note!==undefined)?e.note:""; }
  function localRows(){ var out=[];
    for(var id in S.rows){ if(!byId[id]) continue; var e=S.rows[id];
      if(e.answered!==undefined) out.push({item_id:id,field:"answered",value:e.answered,kind:"field_edit"});
      if(e.note!==undefined) out.push({item_id:id,field:"note",value:e.note,kind:"comment"}); }
    return out; }
  function put(id,field,value,kind){ if(!window.yeslyfBoard) return true; var ok=yeslyfBoard.write({item_id:id,field:field,value:value,who:S.who||"",kind:kind}); if(!ok) setTimeout(function(){ flash(yeslyfBoard.noIdentity); },0); return ok; }
  function paintItem(id){ var el=document.getElementById("ans-"+id); var v=val(id); if(el&&el.value!==v) el.value=v; }
  function paintNote(id){ var el=document.getElementById("note-"+id); if(el){ var v=noteVal(id); if(el.value!==v) el.value=v; } }
  function paintSummary(){ var n=QUESTIONS.length,a=0; QUESTIONS.forEach(function(q){ if(val(q.id)==="yes") a++; }); var g=n-a;
    var el=document.getElementById("summary"); if(el) el.textContent=n+" questions, "+a+" answered, "+g+" gaps"; }
  function paintAll(){ QUESTIONS.forEach(function(q){ paintItem(q.id); paintNote(q.id); }); paintSummary(); var rv=document.getElementById("reviewer"); if(rv&&rv.value!==(S.who||"")) rv.value=S.who||""; }
  function setAnswered(id,v){ if(!byId[id]) return; v=(v==="yes")?"yes":"no"; row(id).answered=v; save(); paintItem(id); paintSummary(); if(put(id,"answered",v,"field_edit")) flash(); }
  function setNote(id,text){ if(!byId[id]) return; row(id).note=text; save(); paintNote(id); if(put(id,"note",text,"comment")) flash(); }
  function applyRemote(rows){ rows.forEach(function(r){
      if(r.field==="answered"&&byId[r.item_id]) row(r.item_id).answered=(r.value==="yes")?"yes":"no";
      else if(r.field==="note"&&byId[r.item_id]) row(r.item_id).note=r.value||""; });
    save(); paintAll(); }
  var tmr={};
  document.addEventListener("DOMContentLoaded",function(){
    if(window.yeslyfBoard){
      Array.prototype.forEach.call(document.querySelectorAll("textarea.seatnote"),function(t){ yeslyfBoard.attach(t,t.getAttribute("data-id")); });
      yeslyfBoard.init({page:"admin_seats",apply:applyRemote,who:S.who||"",local:localRows});
    }
    var rv=document.getElementById("reviewer"); if(rv){ rv.innerHTML='<option value="">editing as</option>'+IDENTITIES.map(function(n){ return '<option value="'+esc(n)+'">'+esc(n)+'</option>'; }).join("");
      rv.value=S.who||"";
      rv.addEventListener("change",function(){ S.who=IDENTITIES.indexOf(rv.value)>=0?rv.value:""; save(); var n=(window.yeslyfBoard&&S.who)?yeslyfBoard.named(S.who):0;
        flash(S.who?"Editing as "+S.who+(n?"; "+n+(n===1?" edit":" edits")+" recorded":""):""); }); }
    paintAll();
    document.body.addEventListener("change",function(e){ var t=e.target; if(!t||!t.classList||!t.classList.contains("ans")) return; var id=t.getAttribute("data-id"); if(!id||!byId[id]) return; setAnswered(id,t.value); });
    document.body.addEventListener("input",function(e){ var t=e.target; if(!t||!t.classList||!t.classList.contains("seatnote")) return; var id=t.getAttribute("data-id"); if(!id||!byId[id]) return;
      row(id).note=t.value; save(); flash("Saving...");
      clearTimeout(tmr[id]); tmr[id]=setTimeout(function(){ if(put(id,"note",noteVal(id),"comment")) flash(); },1500); });
  });
  window.yeslyfSeats={
    questions: function(){ return QUESTIONS.map(function(q){ return q.id; }); },
    answered: function(id){ return val(id); },
    setAnswered: function(id,v){ setAnswered(id,v); },
    note: function(id){ return noteVal(id); },
    setNote: function(id,text){ setNote(id,text); },
    apply: applyRemote
  };
})();
"""


def build_page(doc, questions, ctx):
    who = '<div class="who">Editing as <select id="reviewer"></select></div>'
    total = len(questions)
    answered = sum(1 for q in questions if q.get("answered") == "yes")
    gaps = total - answered
    intro = ('<section><h1>Seats: what each operator seat asks</h1>'
              '<p class="lead">Each seat\'s questions, where the answer lives (the admin tab, Zoho or a vendor console) '
              'and whether the seed answers it. A no is a gap; gaps land on the brief page (admin_brief.html).</p>'
              '<p class="meta" id="summary">%d questions, %d answered, %d gaps</p></section>' % (total, answered, gaps))
    sections = "".join(render_seat(seat, ctx) for seat in doc["seats"])
    blob = ('<script>var QUESTIONS=' + site.js_blob([{"id": q["id"], "answered": q.get("answered", "no")} for q in questions]) +
            ';\nvar IDENTITIES=' + site.js_blob(IDENTITIES) + ';</script>\n')
    return (site.head("yeslyf seats", site.CSS + site.SUBNAV_CSS + EXTRA_CSS, config="config.js") + '<body>\n' +
            site.header("admin_wireframes.html", "seats: what each seat asks", who_html=who, show_export=False, tabs=None, setup_link=True) +
            site.seed_subnav(PAGE) +
            '<main class="main" style="max-width:none">' + intro + sections + '</main>\n' +
            blob + site.store_script() + '<script>' + JS + '</script>\n</body>\n</html>\n')


def main():
    path = DATA_FILE
    if not os.path.exists(path):
        raise SystemExit("build_seats: %s does not exist yet (the seats contract, PLAN_admin_seed_v01.md section 15)" % path)
    with open(path) as fh:
        raw = fh.read()
    site.check_ascii(path, raw)
    try:
        doc = json.loads(raw)
    except ValueError as e:
        raise SystemExit("build_seats: %s is not valid JSON: %s" % (path, e))

    admin_screens = site.load("admin_screens.json")
    screen_ids = set(s["id"] for s in admin_screens["screens"])
    integrations = site.load("integrations.json")
    integration_ids = set(r["id"] for r in integrations["rows"])

    order = precedence_order()
    problems = validate(doc, screen_ids, integration_ids, order)
    if problems:
        raise SystemExit("build_seats: %s breaks the contract:\n%s" % (path, "\n".join("  - " + p for p in problems)))

    ctx = {"integ_by_id": {r["id"]: r for r in integrations["rows"]}}
    questions = [q for seat in doc["seats"] for q in seat["questions"]]
    for q in questions:
        q["proposed"] = proposal(q, order)
    page = build_page(doc, questions, ctx)
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
        raise SystemExit("build_seats: " + "; ".join(errors))

    with open(os.path.join(DOCS, PAGE), "w") as fh:
        fh.write(page)
    print("wrote docs/%s (%d bytes, %d seats, %d questions)" % (PAGE, len(page), len(doc["seats"]), len(questions)))


if __name__ == "__main__":
    main()
