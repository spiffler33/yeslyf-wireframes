#!/usr/bin/env python3
"""Generate docs/admin_operator.html from data/operator.json, seed/export_schema.json, the export CSVs,
data/integrations.json and data/v02/states.json (PLAN_admin_seed_v01.md section 13, deliverable D5; phase B part 2,
23 Sep 2026).

The operator checklist for the Zoho One afternoon: twelve steps (plan section 13, in order), a checkbox per item,
writing to board_entries the same way the tracker does (scripts/build_tracker.py is the model). Item ids are
stable lowercase slugs "step/slug" (data/operator.json) and are the board item_id forever. One notes textarea per
step writes to board_entries too (field "notes", item_id the step id, e.g. "org"), debounced 1500 ms like the
tracker's notes fields, so "to be verified" answers land next to their step.

Before it writes anything it runs the minimisation scan (python3 scripts/seed_export.py --scan-only, subprocess,
sys.executable); a breach fails the whole site build (plan section 12). Nothing seed-related is published from
here: no export file is copied into docs/, and no CSV is linked from the board. The masked admin bundle another
agent builds is the only seed-related thing that is published (Vatsal, 23 Sep 2026). Step 10 names each import
file by its path as plain text, with its external ID column and row counts per run, computed by reading the export
CSVs under data/seed/<run>/exports/ (never copied, never served).

Steps 3, 4, 5, 8 and 10 read seed/export_schema.json and the export CSVs to fill in columns, picklist values and
row counts; step 2 reads data/integrations.json for the WhatsApp, SMS/OTP and email vendor names (I11, I08, I10);
step 8's Marketing Automation journey reads the S4 ladder from data/v02/states.json. Everything else is the
hand-authored text in data/operator.json.

Called at the end of scripts/build_site.py (after build_tracker.main()); also runs on its own.
"""
import csv
import json
import os
import subprocess
import sys

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPTS)
DATA = os.path.join(ROOT, "data")
DOCS = os.path.join(ROOT, "docs")
SEED_DIR = os.path.join(ROOT, "seed")
sys.path.insert(0, SCRIPTS)
import build_site as site  # noqa: E402
import seed_export  # noqa: E402

with open(os.path.join(SEED_DIR, "config.json")) as _fh:
    BAND_LABELS = seed_export.band_label_cache(json.load(_fh))

PAGE = "admin_operator.html"
DATA_FILE = os.path.join(DATA, "operator.json")
SCHEMA_FILE = os.path.join(SEED_DIR, "export_schema.json")
SEED_EXPORT_SCRIPT = os.path.join(SCRIPTS, "seed_export.py")
RUNS = ["run-500", "run-3000"]
IDENTITIES = ["Bhuvanaa", "Harish", "Gaurav", "Kajal", "Somil", "Raafiya", "Vatsal", "Spinach", "Compliance"]
esc = site.esc

# The zoho/*.csv objects that get their own "custom fields" checkbox (step 3) and their own "import order"
# checkbox (step 10); App Events (its own step, 5) and Desk tickets (folded into step 7) are added separately
# where each step needs them. Campaigns and the landing sheet are not Zoho objects with a fixed field set here.
OBJECT_FILES = [
    ("leads", "zoho/leads.csv"),
    ("contacts", "zoho/contacts.csv"),
    ("deals", "zoho/deals.csv"),
    ("a_la_carte", "zoho/a_la_carte.csv"),
    ("calls", "zoho/calls.csv"),
    ("tasks", "zoho/tasks.csv"),
]
APP_EVENTS_FILE = "zoho/app_events.csv"
TICKETS_FILE = "desk/tickets.csv"
IMPORT_FILES = OBJECT_FILES + [("app_events", APP_EVENTS_FILE), ("tickets", TICKETS_FILE)]

# never-connect items that cite an integrations row: WhatsApp is I11 (plan section 13 item 2); the SMS/OTP and
# email rows are I08 (Gupshup, Mobile OTP) and I10 (Amazon SES, Email) in data/integrations.json. The vendor name
# is always looked up by id, never hard-coded.
NEVER_CONNECT_INTEGRATIONS = {"connect/whatsapp": "I11", "connect/sms": "I08", "connect/email": "I10"}

# picklist item id -> the (file, column label) sources for its values (plan section 13 item 4). Source and Task
# State ID are the two exceptions named in the brief; every other picklist reads the same-named contacts.csv
# column, except Lead Stage which only exists on leads.csv.
PICKLISTS = [
    ("picklist/journey-stage", [("zoho/contacts.csv", "Journey Stage")]),
    ("picklist/tier", [("zoho/contacts.csv", "Tier")]),
    ("picklist/sku", [("zoho/contacts.csv", "SKU")]),
    ("picklist/subscription-status", [("zoho/contacts.csv", "Subscription Status")]),
    ("picklist/source", [("zoho/contacts.csv", "Source"), ("zoho/leads.csv", "Lead Source")]),
    ("picklist/lead-stage", [("zoho/leads.csv", "Lead Stage")]),
    ("picklist/aa-status", [("zoho/contacts.csv", "AA Status")]),
    ("picklist/task-state-id", [("zoho/tasks.csv", "State ID")]),
]


def validate(doc):
    problems = []
    seen = set()
    for i, step in enumerate(doc.get("steps", []), start=1):
        sid = step.get("id", "")
        if step.get("n") != i:
            problems.append("step %r: n is %r, expected %d" % (sid, step.get("n"), i))
        if not str(step.get("title", "")).strip():
            problems.append("step %r: title is empty" % sid)
        for it in step.get("items", []):
            iid = it.get("id", "")
            if "/" not in iid or iid.split("/", 1)[0] != sid:
                problems.append("item %r: id does not start with %r/" % (iid, sid))
            if iid in seen:
                problems.append("item %r: duplicate id" % iid)
            seen.add(iid)
            if not str(it.get("text", "")).strip():
                problems.append("item %r: text is empty" % iid)
    return problems


def slugify(s):
    out, prev_dash = [], False
    for ch in str(s).lower():
        if ch.isalnum():
            out.append(ch)
            prev_dash = False
        elif not prev_dash:
            out.append("-")
            prev_dash = True
    return "".join(out).strip("-")


def run_scan():
    proc = subprocess.run([sys.executable, SEED_EXPORT_SCRIPT, "--scan-only"], cwd=ROOT, capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit("minimisation scan failed (python3 scripts/seed_export.py --scan-only):\n" + proc.stdout + proc.stderr)


def load_schema():
    with open(SCHEMA_FILE) as fh:
        raw = fh.read()
    return json.loads(raw)


def schema_index(schema):
    return {f["path"]: f for f in schema["files"]}


SEATS_FILE = os.path.join(DATA, "seats.json")


def load_seats():
    # Step 11's Zoho views per seat (PLAN_admin_seed_v01.md section 15). Minimal reading only; the seats page's own
    # builder (scripts/build_seats.py) owns full contract validation.
    path = SEATS_FILE
    if not os.path.exists(path):
        raise SystemExit("build_operator: %s does not exist yet (step 11's Zoho views per seat)" % path)
    with open(path) as fh:
        raw = fh.read()
    site.check_ascii(path, raw)
    try:
        return json.loads(raw)
    except ValueError as e:
        raise SystemExit("build_operator: %s is not valid JSON: %s" % (path, e))


# seed/export_schema.json carries one shared entry for every campaigns list, keyed literally "campaigns/<stage>.csv"
# (one column set for all stages); the actual per-stage files (one per Journey Stage value, so up to 29) only exist
# on disk, so their names come from the export directories, unioned over both runs.
CAMPAIGNS_TEMPLATE_PATH = "campaigns/<stage>.csv"


def campaign_path(stage):
    return "campaigns/%s.csv" % stage


def campaign_stage_names():
    names = set()
    for run in RUNS:
        d = os.path.join(DATA, "seed", run, "exports", "campaigns")
        if os.path.isdir(d):
            names.update(fn[:-4] for fn in os.listdir(d) if fn.endswith(".csv"))
    return sorted(names)


def csv_rows(run, path):
    # Never copied, never served: read straight from the generator's own output for the count only. A stage with
    # no rows in one run may simply have no file there; that counts as 0, not an error.
    fp = os.path.join(DATA, "seed", run, "exports", path)
    if not os.path.exists(fp):
        return 0
    with open(fp, newline="") as fh:
        n = sum(1 for _ in csv.reader(fh))
    return max(0, n - 1)


def find_column(schema_idx, path, label):
    f = schema_idx.get(path)
    if not f:
        raise SystemExit("build_operator: %s is missing from seed/export_schema.json" % path)
    for c in f["columns"]:
        if c.get("label") == label:
            return c
    raise SystemExit("build_operator: %s has no column %r (seed/export_schema.json)" % (path, label))


def column_detail(c):
    # semicolons: some labels carry commas ("Almost nothing, less than 5%")
    if c.get("values"):
        return "; ".join(str(v) for v in c["values"])
    if c.get("type") == "band":
        # the labels the picklist needs, from the same resolver the minimisation scan validates against
        return "; ".join(BAND_LABELS[c["label"]])
    if c.get("band"):
        bounds = ""
        if c.get("min") is not None or c.get("max") is not None:
            bounds = " (%s to %s)" % (c.get("min", ""), c.get("max", ""))
        return str(c["band"]) + bounds
    if c.get("note"):
        return str(c["note"])
    return "-"


def campaign_import_id(stage):
    return "import/campaigns-%s" % slugify(stage)


def all_items(doc):
    """Every checklist item that will render: the hand-authored ones plus one per campaigns/<stage>.csv found on
    disk, appended to step 10 (their id and text cannot be chosen ahead of the actual export files)."""
    items = []
    for step in doc["steps"]:
        items.extend(step["items"])
    for stage in campaign_stage_names():
        items.append({"id": campaign_import_id(stage), "text": "Import the %s campaigns list." % stage})
    return items


# ---- generated blocks and text, keyed by item id ---------------------------------------------------------------

def object_table(schema_idx, path):
    f = schema_idx.get(path)
    if not f:
        raise SystemExit("build_operator: %s is missing from seed/export_schema.json" % path)
    rows = "".join(
        "<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (esc(c.get("label", "")), esc(c.get("zoho_type") or c.get("type") or "-"), esc(column_detail(c)))
        for c in f["columns"])
    return '<div class="gen wrap"><table><thead><tr><th>Label</th><th>Zoho type</th><th>Values, band or note</th></tr></thead><tbody>%s</tbody></table></div>' % rows


def picklist_html(schema_idx, sources):
    seen = []
    for path, label in sources:
        col = find_column(schema_idx, path, label)
        for v in (col.get("values") or []):
            if v not in seen:
                seen.append(v)
    return '<div class="gen meta">Values: %s</div>' % esc("; ".join(str(v) for v in seen))


def step1_counts_html(schema_idx):
    files = OBJECT_FILES + [("app_events", APP_EVENTS_FILE)]
    parts = []
    for run in RUNS:
        bits = ["%s %d" % (esc(schema_idx.get(path, {}).get("object") or stem), csv_rows(run, path)) for stem, path in files]
        parts.append("%s: %s" % (run, ", ".join(bits)))
    return '<div class="gen meta">%s</div>' % "; ".join(parts)


def campaigns_lists_html():
    stages = campaign_stage_names()
    if not stages:
        return '<p class="gen meta">no campaigns/*.csv exports yet</p>'
    rows = "".join(
        "<li>%s: run-500 %d, run-3000 %d</li>" % (esc(campaign_path(s)), csv_rows("run-500", campaign_path(s)), csv_rows("run-3000", campaign_path(s)))
        for s in stages)
    return '<ul class="gen">%s</ul>' % rows


def s4_ladder_html(states):
    s4 = next((s for s in states.get("states", []) if s.get("id") == "S4"), None)
    if not s4:
        raise SystemExit("build_operator: S4 is missing from data/v02/states.json")
    rows = "".join(
        "<li>%s, %s: %s, links to %s</li>" % (esc(step.get("day", "")), esc(step.get("channel", "")), esc(step.get("slot", "")), esc(step.get("link", "")))
        for step in s4.get("ladder", []))
    return '<div class="gen meta">S4 ladder (never activated):</div><ul class="gen">%s</ul>' % rows


def seat_views_html(seats_by_id, seat_id):
    # step 11: that seat's Zoho views from data/seats.json, "<view name>: <object>; <criteria>", one per line.
    seat = seats_by_id.get(seat_id) or {}
    lines = []
    for q in seat.get("questions", []):
        if q.get("surface") == "Zoho":
            view = q.get("view") or {}
            lines.append("%s: %s; %s" % (view.get("name", ""), view.get("object", ""), view.get("criteria", "")))
    if not lines:
        return '<p class="gen meta">No Zoho view: this seat\'s questions live on the admin tab or a vendor console.</p>'
    return '<ul class="gen">%s</ul>' % "".join("<li>%s</li>" % esc(line) for line in lines)


def import_item_html(schema_idx, schema_key, csv_path=None):
    # Plain text only: no file is copied into docs/ and no CSV is ever linked from the board (Vatsal, 23 Sep 2026).
    # schema_key is the key into seed/export_schema.json (the campaigns files all share one template entry,
    # CAMPAIGNS_TEMPLATE_PATH); csv_path is the real file to count rows in, and defaults to schema_key when they
    # are the same file.
    csv_path = csv_path or schema_key
    f = schema_idx.get(schema_key)
    if not f:
        raise SystemExit("build_operator: %s is missing from seed/export_schema.json" % schema_key)
    ext = f.get("external_id")
    bits = ['<span class="meta">%s</span>' % esc(csv_path)]
    if ext:
        bits.append('<span class="meta">external ID: %s (re-imports update instead of duplicate)</span>' % esc(ext))
    bits.append('<span class="meta">%s</span>' % esc(", ".join("%s %d" % (run, csv_rows(run, csv_path)) for run in RUNS)))
    return '<div class="gen imp">%s</div>' % "".join(bits)


def _vendor_suffix(inum):
    def fn(ctx):
        vendor = ctx["integ_by_id"][inum]["vendor"]
        return " (%s, %s)." % (vendor, inum)
    return fn


TEXT_SUFFIX = {item_id: _vendor_suffix(inum) for item_id, inum in NEVER_CONNECT_INTEGRATIONS.items()}

BLOCK = {}
for _stem, _path in OBJECT_FILES:
    BLOCK["fields/%s" % _stem] = (lambda p: (lambda ctx: object_table(ctx["schema_idx"], p)))(_path)
BLOCK["module/app-events"] = lambda ctx: object_table(ctx["schema_idx"], APP_EVENTS_FILE)
for _item_id, _sources in PICKLISTS:
    BLOCK[_item_id] = (lambda s: (lambda ctx: picklist_html(ctx["schema_idx"], s)))(_sources)
BLOCK["org/record-cap"] = lambda ctx: step1_counts_html(ctx["schema_idx"])
BLOCK["campaigns/lists"] = lambda ctx: campaigns_lists_html()
BLOCK["campaigns/journey"] = lambda ctx: s4_ladder_html(ctx["states"])
for _stem, _path in IMPORT_FILES:
    BLOCK["import/%s" % _stem] = (lambda p: (lambda ctx: import_item_html(ctx["schema_idx"], p)))(_path)

VIEW_SEAT_IDS = ["principal-officer", "adviser", "call-centre", "ops", "marketing", "compliance", "support", "finance"]
for _sid in VIEW_SEAT_IDS:
    BLOCK["views/%s" % _sid] = (lambda s: (lambda ctx: seat_views_html(ctx["seats_by_id"], s)))(_sid)


def render_campaign_import_items(ctx):
    out = []
    for stage in campaign_stage_names():
        iid = campaign_import_id(stage)
        text = "Import the %s campaigns list." % stage
        out.append(citem(iid, text, import_item_html(ctx["schema_idx"], CAMPAIGNS_TEMPLATE_PATH, csv_path=campaign_path(stage))))
    return "".join(out)


STEP_EXTRA_ITEMS = {"import": render_campaign_import_items}


# ---- rendering ----------------------------------------------------------------------------------------------

def citem(item_id, text, extra=""):
    return ('<div class="citem" id="row-%s"><label><input type="checkbox" id="chk-%s" data-id="%s">'
            '<span>%s</span></label>%s</div>' % (esc(item_id), esc(item_id), esc(item_id), esc(text), extra))


def render_item(it, ctx):
    iid = it["id"]
    text = it["text"]
    suffix = TEXT_SUFFIX.get(iid)
    if suffix:
        text = text + suffix(ctx)
    block = BLOCK.get(iid)
    return citem(iid, text, block(ctx) if block else "")


def notes_box(step_id):
    return ('<div class="stepnotes-wrap"><label for="notes-%s">Notes for this step (answers to the to be verified '
            'items go here)</label><textarea class="note stepnotes" id="notes-%s" data-id="%s"></textarea></div>' %
            (esc(step_id), esc(step_id), esc(step_id)))


def render_step(step, ctx):
    sid = step["id"]
    items_html = "".join(render_item(it, ctx) for it in step["items"])
    extra_fn = STEP_EXTRA_ITEMS.get(sid)
    if extra_fn:
        items_html += extra_fn(ctx)
    return ('<section id="step-%s"><h2>%d. %s</h2><p class="lead">%s</p>%s%s</section>' %
            (esc(sid), step["n"], esc(step["title"]), esc(step["intro"]), items_html, notes_box(sid)))


EXTRA_CSS = """
  .who select{padding:6px 8px;border:1px solid var(--line);border-radius:6px;background:#fff;max-width:170px}
  .citem{border-top:1px solid var(--line);padding:8px 0}
  .citem:first-child{border-top:0}
  .citem label{display:flex;gap:8px;align-items:flex-start;cursor:pointer;font-size:13px}
  .citem input{margin-top:3px}
  .gen{margin:6px 0 0 24px}
  .gen table{font-size:12px}
  .gen ul{margin:2px 0;padding-left:18px;font-size:12.5px}
  .gen.meta{font-size:12px;color:var(--mute);margin-top:6px}
  .gen.imp{display:flex;gap:14px;flex-wrap:wrap;align-items:center;font-size:12px}
  .stepnotes-wrap{margin-top:10px}
  .stepnotes-wrap label{display:block;font-size:11px;color:var(--mute);margin-bottom:3px}
"""

JS = r"""
(function(){
  var KEY="yeslyf_operator_v1";
  var byId={}; ITEMS.forEach(function(it){ byId[it.id]=it; });
  var stepIds={}; STEPS.forEach(function(id){ stepIds[id]=true; });
  var S={}; try{ S=JSON.parse(localStorage.getItem(KEY)||"{}")||{}; }catch(e){ S={}; }
  if(!S.rows) S.rows={}; if(!S.who) S.who="";
  function save(){ try{ localStorage.setItem(KEY, JSON.stringify(S)); }catch(e){} }
  var ft; function flash(t){ var s=document.getElementById("saved"); if(!s) return; s.textContent=t||"Saved in this browser"; clearTimeout(ft); ft=setTimeout(function(){ s.textContent=""; },1800); }
  function esc(s){ return String(s===undefined||s===null?"":s).split("&").join("&amp;").split("<").join("&lt;").split(">").join("&gt;").split('"').join("&quot;"); }
  function row(id){ if(!S.rows[id]) S.rows[id]={}; return S.rows[id]; }
  function val(id){ var e=S.rows[id]; return (e&&e.done!==undefined)?e.done:"no"; }
  function noteVal(id){ var e=S.rows[id]; return (e&&e.notes!==undefined)?e.notes:""; }
  function localRows(){ var out=[];
    for(var id in S.rows){ var e=S.rows[id];
      if(byId[id]&&e.done!==undefined) out.push({item_id:id,field:"done",value:e.done,kind:"field_edit"});
      if(stepIds[id]&&e.notes!==undefined) out.push({item_id:id,field:"notes",value:e.notes,kind:"field_edit"}); }
    return out; }
  function put(id,field,value){ if(!window.yeslyfBoard) return true; var ok=yeslyfBoard.write({item_id:id,field:field,value:value,who:S.who||"",kind:"field_edit"}); if(!ok) setTimeout(function(){ flash(yeslyfBoard.noIdentity); },0); return ok; }
  function paintItem(id){ var el=document.getElementById("chk-"+id); var want=val(id)==="yes"; if(el&&el.checked!==want) el.checked=want; }
  function paintNotes(id){ var el=document.getElementById("notes-"+id); if(el){ var v=noteVal(id); if(el.value!==v) el.value=v; } }
  function paintProgress(){ var done=0; ITEMS.forEach(function(it){ if(val(it.id)==="yes") done++; }); var el=document.getElementById("progress"); if(el) el.textContent=done+" of "+ITEMS.length+" done"; }
  function paintAll(){ ITEMS.forEach(function(it){ paintItem(it.id); }); STEPS.forEach(paintNotes); paintProgress(); var rv=document.getElementById("reviewer"); if(rv&&rv.value!==(S.who||"")) rv.value=S.who||""; }
  function setDone(id,checked){ if(!byId[id]) return; var v=checked?"yes":"no"; row(id).done=v; save(); paintItem(id); paintProgress(); if(put(id,"done",v)) flash(); }
  function setNotes(id,text){ if(!stepIds[id]) return; row(id).notes=text; save(); paintNotes(id); if(put(id,"notes",text)) flash(); }
  function applyRemote(rows){ rows.forEach(function(r){
      if(r.field==="done"&&byId[r.item_id]) row(r.item_id).done=r.value||"no";
      else if(r.field==="notes"&&stepIds[r.item_id]) row(r.item_id).notes=r.value||""; });
    save(); paintAll(); }
  var tmr={};
  document.addEventListener("DOMContentLoaded",function(){
    if(window.yeslyfBoard){
      Array.prototype.forEach.call(document.querySelectorAll("textarea.stepnotes"),function(t){ yeslyfBoard.attach(t,t.getAttribute("data-id")); });
      yeslyfBoard.init({page:"admin_operator",apply:applyRemote,who:S.who||"",local:localRows});
    }
    var rv=document.getElementById("reviewer"); if(rv){ rv.innerHTML='<option value="">editing as</option>'+IDENTITIES.map(function(n){ return '<option value="'+esc(n)+'">'+esc(n)+'</option>'; }).join("");
      rv.value=S.who||"";
      rv.addEventListener("change",function(){ S.who=IDENTITIES.indexOf(rv.value)>=0?rv.value:""; save(); var n=(window.yeslyfBoard&&S.who)?yeslyfBoard.named(S.who):0;
        flash(S.who?"Editing as "+S.who+(n?"; "+n+(n===1?" edit":" edits")+" recorded":""):""); }); }
    paintAll();
    document.body.addEventListener("change",function(e){ var t=e.target; if(!t||t.tagName!=="INPUT"||t.type!=="checkbox") return; var id=t.getAttribute("data-id"); if(!id||!byId[id]) return; setDone(id,t.checked); });
    document.body.addEventListener("input",function(e){ var t=e.target; if(!t||!t.classList||!t.classList.contains("stepnotes")) return; var id=t.getAttribute("data-id"); if(!id||!stepIds[id]) return;
      row(id).notes=t.value; save(); flash("Saving...");
      clearTimeout(tmr[id]); tmr[id]=setTimeout(function(){ if(put(id,"notes",noteVal(id))) flash(); },1500); });
  });
  window.yeslyfOperator={
    items: function(){ return ITEMS.map(function(it){ return it.id; }); },
    done: function(id){ return val(id)==="yes"; },
    set: function(id,bool){ var el=document.getElementById("chk-"+id); if(el) el.checked=!!bool; setDone(id,!!bool); },
    notes: function(id){ return noteVal(id); },
    setNotes: function(id,text){ setNotes(id,text); },
    apply: applyRemote
  };
})();
"""


def build_page(doc, items, schema, schema_idx, integrations, states, seats_doc):
    ctx = {"schema": schema, "schema_idx": schema_idx, "integ_by_id": {r["id"]: r for r in integrations["rows"]}, "states": states,
           "seats_by_id": {s["id"]: s for s in seats_doc.get("seats", [])}}
    who = '<div class="who">Editing as <select id="reviewer"></select></div>'
    intro = ('<section><h1>Operator checklist: the Zoho afternoon</h1>'
             '<p class="lead">Every person in these files is synthetic; nothing is ever sent.</p>'
             '<p class="meta">Minimisation scan: pass, run-500 and run-3000</p>'
             '<p class="meta" id="progress">0 of %d done</p></section>' % len(items))
    steps_html = "".join(render_step(step, ctx) for step in doc["steps"])
    blob = ('<script>var ITEMS=' + site.js_blob(items) + ';\nvar STEPS=' + site.js_blob([s["id"] for s in doc["steps"]]) +
            ';\nvar IDENTITIES=' + site.js_blob(IDENTITIES) + ';</script>\n')
    return (site.head("yeslyf operator checklist", site.CSS + site.SUBNAV_CSS + EXTRA_CSS, config="config.js") + '<body>\n' +
            site.header("admin_wireframes.html", "operator checklist, %d items" % len(items), who_html=who, show_export=False, tabs=None, setup_link=True) +
            site.seed_subnav(PAGE) +
            '<main class="main" style="max-width:none">' + intro + steps_html + '</main>\n' +
            blob + site.store_script() + '<script>' + JS + '</script>\n</body>\n</html>\n')


def main():
    with open(DATA_FILE) as fh:
        raw = fh.read()
    site.check_ascii("data/operator.json", raw)
    doc = json.loads(raw)
    problems = validate(doc)
    if problems:
        for p in problems:
            print("ERROR: " + p)
        sys.exit(1)

    if not os.path.exists(SEED_EXPORT_SCRIPT):
        print("waiting for exports: scripts/seed_export.py does not exist yet")
        sys.exit(1)
    run_scan()
    if not os.path.exists(SCHEMA_FILE):
        print("waiting for exports: seed/export_schema.json does not exist yet")
        sys.exit(1)
    for run in RUNS:
        if not os.path.isdir(os.path.join(DATA, "seed", run, "exports")):
            print("waiting for exports: data/seed/%s/exports/ does not exist yet" % run)
            sys.exit(1)

    schema = load_schema()
    schema_idx = schema_index(schema)
    integrations = site.load("integrations.json")
    states = site.load_optional("v02", "states.json")
    if states is None:
        raise SystemExit("build_operator: data/v02/states.json is required (step 8's S4 ladder)")
    seats_doc = load_seats()

    items = all_items(doc)
    page = build_page(doc, items, schema, schema_idx, integrations, states, seats_doc)
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
    print("wrote docs/%s (%d bytes, %d steps, %d items)" % (PAGE, len(page), len(doc["steps"]), len(items)))


if __name__ == "__main__":
    main()
