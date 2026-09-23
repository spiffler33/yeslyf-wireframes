#!/usr/bin/env python3
"""Generate docs/admin_brief.html from the board's own data (PLAN_admin_seed_v01.md section 16, deliverable D8;
phase D part 2, 23 Sep 2026).

Six tables (T1 to T6), pre-filled from data that already exists, each row carrying a cause. A row is never a value
copied out of the canonical seed (data/seed/run-3000/*.json): T1 lists field NAMES and types, never a person's PAN,
phone, email or rupee amount. Every table is a <details> section, open by default, with a count in its summary.

Gap rows come from data/seats.json (the seats page, deliverable D7, written by another agent): every question
answered "no" becomes a "gap" row in the table its "brief" key names, cause "<seat> seat, seats page (<question
id>)". The page also embeds every question as a small JS blob and re-reads the live board (page "admin_seats") on
load, so a later answer on the seats page adds or drops a gap row without a rebuild (yeslyfBoard.read). This page
writes nothing of its own: no comment box, no edit control; only the top-bar pill inits (site.js_pill) plus that
one read.

Sources (read-only; never printed whole, never hand-edited):
- data/seed/run-3000/*.json and events.jsonl: the canonical seed tables (T1's field catalogue; type is derived from
  every value actually found, never hand-declared).
- data/screens_v02.json: spec.fields (source and precision tags for T1; also feeds T2 and T6).
- data/admin_crm.json: EVENTS (T2), PLACEMENT (T6 dashboards).
- data/admin_screens.json: the built M02-M14 screens (T3; also feeds T2).
- seed/export_schema.json: the Zoho export columns (T1's "where mirrored"; most of T4).
- data/operator.json: the Roles step (T4).
- data/v02/states.json: crm_task per state (T4), the nudge rules (T5).
- data/seed/run-3000/config.json: feature_flags and copy_slots (T5).
- data/integrations.json: I11 WATI, I13 (T5, T6).
- data/v02/flow.json: screen order, for the three T6 funnels.

Called from build_site.main(); also runs on its own (`python3 scripts/build_brief.py`).
"""
import collections
import itertools
import json
import os
import sys
from datetime import date, datetime

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPTS)
DATA = os.path.join(ROOT, "data")
DOCS = os.path.join(ROOT, "docs")
sys.path.insert(0, SCRIPTS)
import build_site as site  # noqa: E402

PAGE = "admin_brief.html"
RUN = "run-3000"
SCHEMA_PATH = os.path.join(ROOT, "seed", "export_schema.json")
EVENTS_PATH = os.path.join(DATA, "seed", RUN, "events.jsonl")
esc = site.esc

# ---- T1: the seed tables, in the order plan section 11 lists them (auto-detected shape: one record per person, or
# a list of records per person; "config" and "events" are special-cased below, not person-keyed at all). ----------
PERSON_TABLES = [
    "people", "households", "reveal", "financial_records", "loans", "covers", "goals", "rpq", "holdings",
    "aa_consents", "cas_uploads", "plan_versions", "actions", "subscriptions", "payments", "a_la_carte",
    "calls", "tickets", "ops_queue", "integration_events", "tasks", "nudges_sent", "staff",
]
TABLE_ORDER = PERSON_TABLES[:22] + ["events"] + PERSON_TABLES[22:] + ["config"]

# PII class: an explicit dict, never inferred from a field's name (plan section 16, T1). Values not listed here,
# and tables not listed here, are "none".
PII_PERSONAL = {
    "people": {"first_name", "last_name", "legal_name", "phone", "email", "pan", "dob", "city", "age"},
    "households": {"members"},
    "calls": {"notes"},
    "tickets": {"subject", "description"},
}
PII_FINANCIAL_FIELDS = {
    "financial_records": {"value"},
    "reveal": {"income_exact", "corpus_exact"},
    "goals": {"cost_today"},
    "actions": {"amount"},
}
PII_FINANCIAL_TABLES = {"loans", "covers", "holdings", "subscriptions", "payments", "a_la_carte"}

CAUSE_T1 = "seed plan, 22 Sep 2026 (section 11)"
CAUSE_T3_DEFAULT = "seed plan, 22 Sep 2026 (PLAN_admin_seed_v01.md section 14)"
CAUSE_T4 = "seed plan, 22 Sep 2026 (sections 12 and 13)"
CAUSE_T5 = "STATES"

# The 8 seats, by the fixed slug their id carries in data/operator.json's roles step (seats_contract.md: eight
# seats, by role, no people's names). A closed, permanent set of 8 ids; not a pattern match.
ROLE_SLUG_NAME = {
    "principal-officer": "Principal officer", "adviser": "Adviser", "call-centre": "Call centre", "ops": "Ops",
    "marketing": "Marketing", "compliance": "Compliance", "support": "Support", "finance": "Finance",
}

VALID_BRIEF = {"T1", "T2", "T3", "T4", "T5", "T6"}
VALID_SURFACE = {"Admin tab", "Zoho", "vendor console"}
VALID_ANSWERED = {"yes", "no"}


# ---- generic seed scanning --------------------------------------------------------------------------------------

def classify_value(v):
    """One value to one of the T1 type tags, or None for a value that carries no type information (null)."""
    if v is None:
        return None
    if isinstance(v, bool):
        return "bool"
    if isinstance(v, int):
        return "integer"
    if isinstance(v, float):
        return "number"
    if isinstance(v, list):
        return "list"
    if isinstance(v, dict):
        return "object"
    if isinstance(v, str):
        try:
            date.fromisoformat(v)
            return "date"
        except ValueError:
            pass
        try:
            datetime.fromisoformat(v)
            return "date-time"
        except ValueError:
            pass
        return "text"
    return "text"


def type_label(types_seen):
    if not types_seen:
        return "text"
    if len(types_seen) == 1:
        return next(iter(types_seen))
    return "mixed"


def scan_records(records, types_out):
    """records: an iterable of dicts (one canonical seed table's rows). types_out: a {field path: set(type tag)}
    accumulator, mutated in place. A dict-valued field is expanded one level (key.subkey); a list-valued field is
    not (its own value is typed "list")."""
    for rec in records:
        if not isinstance(rec, dict):
            continue
        for k, v in rec.items():
            if isinstance(v, dict) and v:
                for k2, v2 in v.items():
                    t = classify_value(v2)
                    if t:
                        types_out[k + "." + k2].add(t)
            else:
                t = classify_value(v)
                if t:
                    types_out[k].add(t)


def load_person_table(name):
    """Every record of one canonical seed table, regardless of whether the file holds one record per person or a
    list of records per person (auto-detected from the data itself, per person_id)."""
    with open(os.path.join(DATA, "seed", RUN, name + ".json")) as fh:
        d = json.load(fh)
    sample = next((v for v in d.values() if v), None)
    if isinstance(sample, list):
        return list(itertools.chain.from_iterable(v for v in d.values() if isinstance(v, list)))
    return [v for v in d.values() if isinstance(v, dict)]


def scan_events(types_out, props_by_event):
    """One pass over events.jsonl: T1 typing for the "events" table (props expanded one level, as "props.<key>"),
    and, for T2, the union of prop keys ever carried by each named event (the payload fallback)."""
    with open(EVENTS_PATH) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            for k, v in rec.items():
                if k == "props" and isinstance(v, dict) and v:
                    for k2, v2 in v.items():
                        t = classify_value(v2)
                        if t:
                            types_out["props." + k2].add(t)
                    props_by_event[rec.get("event")].update(v.keys())
                else:
                    t = classify_value(v)
                    if t:
                        types_out[k].add(t)


def pii_class(table, field):
    if table in PII_FINANCIAL_TABLES:
        return "financial"
    if field in PII_FINANCIAL_FIELDS.get(table, ()):
        return "financial"
    if field in PII_PERSONAL.get(table, ()):
        return "personal"
    return "none"


def build_mirror_index(schema):
    """seed/export_schema.json column "field" (the exact seed path; "source" is the human note) -> the Zoho column
    label(s) that mirror it. Zoho files count as mirrors (the landing sheet is an input, not a mirror), and each
    label reads with its object."""
    mirror = collections.defaultdict(list)
    for f in schema["files"]:
        if f.get("system") not in ("Zoho CRM", "Zoho Desk", "Zoho Campaigns"):
            continue
        for c in f["columns"]:
            if c.get("field"):
                mirror[c["field"]].append("%s: %s" % (f.get("object"), c["label"]))
    return mirror


def build_screens_field_index(screens_doc):
    """The first spec.fields entry (name or f) per field name, in screen order, for T1's source/precision tags."""
    idx = {}
    for s in screens_doc["screens"]:
        for fl in (s.get("spec") or {}).get("fields", []) or []:
            if not isinstance(fl, dict):
                continue
            name = fl.get("name") or fl.get("f")
            if name and name not in idx:
                idx[name] = {"source": fl.get("source") or "-", "precision": fl.get("precision") or "-"}
    return idx


def build_t1(schema, screens_doc):
    types_by_path = collections.defaultdict(set)  # "table.field" -> set of type tags
    props_by_event = collections.defaultdict(set)

    for name in PERSON_TABLES:
        local = collections.defaultdict(set)
        scan_records(load_person_table(name), local)
        for path, s in local.items():
            types_by_path[name + "." + path] = s

    with open(os.path.join(DATA, "seed", RUN, "config.json")) as fh:
        config_doc = json.load(fh)
    local = collections.defaultdict(set)
    scan_records([config_doc], local)
    for path, s in local.items():
        types_by_path["config." + path] = s

    local = collections.defaultdict(set)
    scan_events(local, props_by_event)
    for path, s in local.items():
        types_by_path["events." + path] = s

    mirror = build_mirror_index(schema)
    screens_field_idx = build_screens_field_index(screens_doc)

    def sort_key(full_path):
        table, field = full_path.split(".", 1)
        return (TABLE_ORDER.index(table) if table in TABLE_ORDER else 999, field)

    rows = []
    for full_path in sorted(types_by_path.keys(), key=sort_key):
        table, field = full_path.split(".", 1)
        type_tag = type_label(types_by_path[full_path])
        leaf = field.rsplit(".", 1)[-1]
        sp = screens_field_idx.get(leaf)
        source_tag = sp["source"] if sp else "-"
        precision_tag = sp["precision"] if sp else "-"
        labels = mirror.get(full_path)
        mirrored = "; ".join(dict.fromkeys(labels)) if labels else "none"
        rows.append([table, field, type_tag, source_tag, precision_tag, pii_class(table, field), mirrored, CAUSE_T1])
    return rows, config_doc, props_by_event


# ---- T2: the event contract ---------------------------------------------------------------------------------

def split_event_names(raw):
    return [n.strip() for n in raw.split(" / ") if n.strip()]


def build_t2(admin_crm, screens_doc, admin_screens, states_doc, props_by_event):
    trigger = collections.OrderedDict()   # event name -> list of trigger-screen strings, first-seen order
    payload = {}
    cause = collections.defaultdict(list)
    in_admin_crm = set()

    def add(name, screen_str, cause_tag):
        trigger.setdefault(name, [])
        if screen_str and screen_str not in trigger[name]:
            trigger[name].append(screen_str)
        if cause_tag not in cause[name]:
            cause[name].append(cause_tag)

    for entry in admin_crm.get("EVENTS", []):
        raw_name = entry[0] if len(entry) > 0 else ""
        screen_str = entry[1] if len(entry) > 1 else ""
        payload_text = entry[2] if len(entry) > 2 else ""
        for name in split_event_names(raw_name):
            in_admin_crm.add(name)
            add(name, screen_str, "admin_crm.json EVENTS")
            if payload_text and name not in payload:
                payload[name] = payload_text

    for s in site.live_screens(screens_doc):
        for name in s.get("events", []) or []:
            add(name, s["id"], "screens_v02.json events")

    for s in admin_screens["screens"]:
        for name in s.get("events", []) or []:
            add(name, s["id"], "admin_screens.json")

    state_enter_set = {"state_enter_" + s["id"] for s in states_doc["states"]}

    rows = []
    for name in sorted(trigger.keys()):
        pl = payload.get(name)
        if not pl:
            keys = sorted(props_by_event.get(name, ()))
            pl = ", ".join(keys) if keys else "-"
        consumers = []
        if name in in_admin_crm or name in state_enter_set:
            consumers.append("CRM")
        if name in state_enter_set or name in ("nudge_sent", "nudge_opened"):
            consumers.append("nudge ladder")
        consumers.append("analytics")
        rows.append([name, ", ".join(trigger[name]), pl, ", ".join(consumers), "; ".join(cause[name])])
    return rows


# ---- T3: built screens ---------------------------------------------------------------------------------------

def build_t3(admin_screens):
    rows = []
    for s in admin_screens["screens"]:
        reads = "; ".join(str(x) for x in s["spec"]["fields"])
        writes = "; ".join("%s (%s)" % (w["action"], ", ".join(w["roles"])) for w in s.get("writes", []) or [])
        role = "; ".join("%s: %s" % (k, v) for k, v in s["role"].items())
        cause = "; ".join(s["v02"]["causes"]) or CAUSE_T3_DEFAULT
        rows.append([s["id"], s["title"], ", ".join(s["seat"]), reads, writes or "-", role, cause])
    return rows


# ---- T4: Zoho configuration -----------------------------------------------------------------------------------

def build_t4(schema, schema_idx, questions, states_doc, operator_doc):
    rows = []

    for f in schema["files"]:
        if f["path"] == "campaigns/<stage>.csv":
            continue  # one row per real stage instead, from this same file's Stage column (below)
        obj = f.get("object") or f["path"]
        for c in f["columns"]:
            detail = "zoho type: %s" % (c.get("zoho_type") or c.get("type") or "-")
            if c.get("values"):
                detail += "; values: " + "; ".join(str(v) for v in c["values"])
            elif c.get("note"):
                detail += "; " + str(c["note"])
            rows.append([obj, c["label"], detail, CAUSE_T4])

    for q in questions:
        if q.get("surface") == "Zoho" and isinstance(q.get("view"), dict):
            v = q["view"]
            rows.append([v.get("object", "-"), "saved view: %s (%s)" % (v.get("name", "-"), q["_seat_name"]),
                         v.get("criteria", "-"), gap_cause(q)])

    for s in states_doc["states"]:
        ct = s.get("crm_task") or {}
        if ct.get("created"):
            subject = "%s %s" % (s["id"], s.get("primary_action", ""))
            rows.append(["Tasks", "state_enter: %s" % s["id"],
                         "subject: %s; fields: %s" % (subject, ", ".join(ct.get("fields", []))), CAUSE_T4])

    tix = schema_idx.get("desk/tickets.csv") or {}
    cat_col = next((c for c in tix.get("columns", []) if c.get("label") == "Category"), None)
    cats = "; ".join(cat_col.get("values", [])) if cat_col else "-"
    rows.append(["Desk", "categories and SLA", "categories: %s; SLA: one business day; SCORES Ref field" % cats, CAUSE_T4])

    camp = schema_idx.get("campaigns/<stage>.csv") or {}
    stage_col = next((c for c in camp.get("columns", []) if c.get("label") == "Stage"), None)
    for stage in (stage_col.get("values", []) if stage_col else []):
        rows.append(["Campaigns", stage, "list for journey stage %s" % stage, CAUSE_T4])

    rows.append(["Bookings", "service", "one service, 45-minute slots, staff Adviser 01 to 06", CAUSE_T4])

    for step in operator_doc.get("steps", []):
        if step.get("id") != "roles":
            continue
        for it in step.get("items", []):
            slug = it["id"].split("/", 1)[-1]
            name = ROLE_SLUG_NAME.get(slug, slug)
            rows.append(["Roles", name, "advisers see their own people, ops sees records, "
                         "the principal officer sees everything", CAUSE_T4])

    rows.append(["Layouts", "-", "to be decided", CAUSE_T4])
    return rows


# ---- T5: nudge rules -------------------------------------------------------------------------------------------

def build_t5(config_doc, states_doc, admin_crm, integrations_by_id):
    rows = []
    rows.append(["v0.2 nudge matrix", "one row per state per ladder step; see admin_v02.html#a-nudges-v02", CAUSE_T5])

    cap = config_doc.get("feature_flags", {}).get("nudge_cap_per_week", "-")
    cap_rule = states_doc["rules"][0] if states_doc.get("rules") else "-"
    rows.append(["weekly cap enforcement", "config feature_flags.nudge_cap_per_week: %s. %s" % (cap, cap_rule), CAUSE_T5])

    contact_row = next((r for r in admin_crm.get("CONTACT_FIELDS", []) if r and r[0] == "WhatsApp opt-in, DND flag"), None)
    inbound_row = next((r for r in admin_crm.get("INBOUND", []) if r and r[0] == "consent_changed"), None)
    detail = "%s: %s." % (contact_row[0], contact_row[1]) if contact_row else "-"
    if inbound_row:
        detail += " Inbound sync (%s, %s): %s." % (inbound_row[0], inbound_row[1], inbound_row[2])
    detail += " to be decided: whether a nudge already queued is dropped when DND or opt-in changes mid-week."
    rows.append(["opt-in and DND handling", detail, CAUSE_T5])

    wati = integrations_by_id.get("I11", {})
    vendor = wati.get("vendor", "not decided")
    for slot in config_doc.get("copy_slots", []):
        if slot.get("channel") == "WhatsApp":
            rows.append(["template: %s" % slot.get("slot", "-"),
                         "state: %s; deep link: %s; approval: to be verified (I11, %s)" % (
                             slot.get("state", "-"), slot.get("deep_link", "-"), vendor), CAUSE_T5])
    return rows


# ---- T6: analytics ---------------------------------------------------------------------------------------------

USER_PROPERTIES = ["tier", "state", "source", "source_path", "city tier", "age band", "is_topup"]
FUNNELS = [("R01 to R09", "R01", "R09"), ("R12 to P05", "R12", "P05"), ("O02 to D10", "O02", "D10")]


def build_t6(screens_doc, flow_order, admin_crm, integrations_by_id):
    rows = []
    live = site.live_screens(screens_doc)
    rows.append(["screen views", "%d screens, each fires <id>_view" % len(live), "screens_v02.json events"])

    all_events = set()
    for s in live:
        for e in s.get("events", []) or []:
            all_events.add(e)
    named = sorted(e for e in all_events if not e.endswith("_view"))
    rows.append(["named events", "%d distinct named events (excludes <id>_view)" % len(named), "screens_v02.json events"])

    for prop in USER_PROPERTIES:
        rows.append(["user property: %s" % prop, "analytics profile property (I13)",
                     "seed plan, 22 Sep 2026 (section 12)"])

    for label, start, end in FUNNELS:
        i, j = flow_order.index(start), flow_order.index(end)
        rows.append(["funnel: %s" % label, ", ".join(flow_order[i:j + 1]), "data/v02/flow.json order"])

    rows.append(["retention by paid cohort", "to be decided: cohort definition and retention window",
                 "seed plan, 22 Sep 2026 (section 12)"])

    for p in admin_crm.get("PLACEMENT", []):
        rows.append(["dashboard: %s" % p.get("sec", "-"), p.get("item", "-"), "admin_crm.json PLACEMENT"])

    i13 = integrations_by_id.get("I13", {})
    rows.append(["tool", "I13, %s (vendor %s)" % (i13.get("choice", "open"), i13.get("vendor", "not decided")),
                 "data/integrations.json I13"])
    return rows


# ---- data/seats.json: the contract of scratchpad/seats_contract.md ---------------------------------------------

def validate_seats(doc):
    problems = []
    seats = doc.get("seats")
    if not isinstance(seats, list) or not seats:
        return ["seats.json: 'seats' must be a non-empty list"]
    seen_ids = set()
    for seat in seats:
        sid = seat.get("id", "")
        sname = seat.get("seat", "")
        if not sid or not sname:
            problems.append("seat %r: missing id or seat name" % (seat.get("id"),))
        for q in seat.get("questions", []) or []:
            qid = q.get("id", "")
            if not qid:
                problems.append("seat %s: a question is missing id" % sid)
                continue
            if qid in seen_ids:
                problems.append("question %s: duplicate id" % qid)
            seen_ids.add(qid)
            if not str(q.get("question", "")).strip():
                problems.append("question %s: question text is empty" % qid)
            if q.get("answered") not in VALID_ANSWERED:
                problems.append("question %s: answered %r is not yes or no" % (qid, q.get("answered")))
            if q.get("surface") not in VALID_SURFACE:
                problems.append("question %s: surface %r is not one of %s" % (qid, q.get("surface"), ", ".join(sorted(VALID_SURFACE))))
            if q.get("brief") not in VALID_BRIEF:
                problems.append("question %s: brief %r is not one of T1 to T6" % (qid, q.get("brief")))
            if q.get("answered") == "no" and not str(q.get("gap", "")).strip():
                problems.append("question %s: answered no but gap text is empty" % qid)
            if not str(q.get("cause", "")).strip():
                problems.append("question %s: cause is empty" % qid)
    return problems


def flatten_seats(doc):
    out = []
    for seat in doc.get("seats", []):
        for q in seat.get("questions", []) or []:
            q = dict(q)
            q["_seat_name"] = seat.get("seat", "")
            q["_seat_id"] = seat.get("id", "")
            out.append(q)
    return out


def gap_cause(q):
    return "%s seat, seats page (%s)" % (q["_seat_name"], q["id"])


# ---- rendering -------------------------------------------------------------------------------------------------

TABLES = [
    ("T1", "T1 Data model", ["table", "field", "type", "source tag", "precision tag", "PII class", "where mirrored", "cause"]),
    ("T2", "T2 Event contract", ["event", "trigger screens", "payload", "consumers", "cause"]),
    ("T3", "T3 Built screens", ["screen", "title", "seat", "reads", "write actions", "role", "cause"]),
    ("T4", "T4 Zoho configuration", ["object", "field", "detail", "cause"]),
    ("T5", "T5 Nudge rules", ["item", "detail", "cause"]),
    ("T6", "T6 Analytics", ["item", "detail", "cause"]),
]


def render_gap_row(q):
    text = ("gap - <b>%s</b>: %s <span class=\"meta\">%s</span>" %
            (esc(q["question"]), esc(q.get("gap") or "(no detail)"), esc(gap_cause(q))))
    return '<tr class="gaprow" id="gap-%s" data-qid="%s"><td colspan="99">%s</td></tr>' % (esc(q["id"]), esc(q["id"]), text)


def render_table_section(table_id, title, cols, rows, gap_questions):
    thead = "<tr>" + "".join("<th>%s</th>" % esc(c) for c in cols) + "</tr>"
    body = "".join("<tr>" + "".join("<td>%s</td>" % site.cell(v) for v in r) + "</tr>" for r in rows)
    gaps_html = "".join(render_gap_row(q) for q in gap_questions)
    total = len(rows) + len(gap_questions)
    summary = ('%s <span class="meta" id="count-%s">, %d rows, %d gaps</span>' %
               (esc(title), table_id, total, len(gap_questions)))
    return ('<details open><summary>%s</summary><div class="wrap"><table><thead>%s</thead>'
            '<tbody id="tbody-%s">%s%s</tbody></table></div></details>' %
            (summary, thead, table_id, body, gaps_html))


EXTRA_CSS = """
  .gaprow td{border-left:3px solid #B2434F;background:#FFF8F6}
  .gaprow b{font-weight:600}
"""

JS = r"""
(function(){
  var byId={}; QUESTIONS.forEach(function(q){ byId[q.id]=q; });
  var shown={}; QUESTIONS.forEach(function(q){ shown[q.id]=q.answered==="no"; });
  function esc(s){ return String(s===undefined||s===null?"":s).split("&").join("&amp;").split("<").join("&lt;").split(">").join("&gt;").split('"').join("&quot;"); }
  function countGaps(brief){ var n=0; for(var id in shown){ if(shown[id]&&byId[id].brief===brief) n++; } return n; }
  function updateSummary(brief){ var el=document.getElementById("count-"+brief); if(!el) return; var g=countGaps(brief);
    el.textContent=", "+((BASE_COUNTS[brief]||0)+g)+" rows, "+g+" gaps"; }
  function gapHtml(q){ return "gap - <b>"+esc(q.question)+"</b>: "+esc(q.gap||"(no detail)")+" <span class=\"meta\">"+esc(q.cause_text)+"</span>"; }
  function addGap(q){ if(shown[q.id]) return; var tbody=document.getElementById("tbody-"+q.brief); if(!tbody) return;
    var tr=document.createElement("tr"); tr.className="gaprow"; tr.id="gap-"+q.id; tr.setAttribute("data-qid",q.id);
    var td=document.createElement("td"); td.setAttribute("colspan","99"); td.innerHTML=gapHtml(q);
    tr.appendChild(td); tbody.appendChild(tr); shown[q.id]=true; updateSummary(q.brief); }
  function removeGap(qid){ var q=byId[qid]; if(!q||!shown[qid]) return; var el=document.getElementById("gap-"+qid);
    if(el&&el.parentNode) el.parentNode.removeChild(el); shown[qid]=false; updateSummary(q.brief); }
  function applyRemote(latest){ (latest||[]).forEach(function(r){ if(r.field!=="answered") return; var q=byId[r.item_id]; if(!q) return;
    if(r.value==="yes") removeGap(r.item_id); else addGap(q); }); }
  document.addEventListener("DOMContentLoaded",function(){
    if(window.yeslyfBoard) yeslyfBoard.read({page:"admin_seats", apply:function(latest){ applyRemote(latest); }});
  });
  window.yeslyfBrief={ applyRemote:applyRemote, gapShown:function(qid){ return !!shown[qid]; },
    gapIds:function(brief){ var out=[]; for(var id in shown){ if(shown[id]&&(!brief||byId[id].brief===brief)) out.push(id); } return out.sort(); },
    count:function(brief){ return (BASE_COUNTS[brief]||0)+countGaps(brief); } };
})();
"""


def build_page(table_rows, questions):
    by_gap = {tid: [q for q in questions if q.get("brief") == tid and q.get("answered") == "no"] for tid, _, _ in TABLES}
    base_counts = {tid: len(table_rows[tid]) for tid, _, _ in TABLES}
    sections = "".join(render_table_section(tid, title, cols, table_rows[tid], by_gap[tid]) for tid, title, cols in TABLES)

    intro = ('<section><h1>Admin brief skeleton: what the built tool, the CRM, the database and the event feed '
             'must hold</h1><p class="lead">Tables T1 to T6 are pre-filled from the board\'s data; rows marked '
             'gap come from the seats page.</p></section>')

    questions_blob = [
        {"id": q["id"], "brief": q.get("brief"), "question": q.get("question"), "gap": q.get("gap") or "",
         "answered": q.get("answered"), "cause_text": gap_cause(q)}
        for q in questions
    ]
    total_rows = sum(base_counts.values()) + sum(len(v) for v in by_gap.values())
    blob = ('<script>var QUESTIONS=' + site.js_blob(questions_blob) + ';\nvar BASE_COUNTS=' + site.js_blob(base_counts) + ';</script>\n')

    return (site.head("yeslyf admin brief skeleton", site.CSS + site.SUBNAV_CSS + EXTRA_CSS) + '<body>\n' +
            site.header("admin_wireframes.html", "admin brief skeleton, %d rows" % total_rows, who_html="", show_export=False, tabs=None, setup_link=True) +
            site.seed_subnav(PAGE) +
            '<main class="main">' + intro + sections + '</main>\n' +
            blob + site.store_script() + '<script>' + site.js_pill("admin_brief") + JS + '</script>\n</body>\n</html>\n')


# ---- orchestration ----------------------------------------------------------------------------------------------

def load_sources():
    schema = json.load(open(SCHEMA_PATH))
    schema_idx = {f["path"]: f for f in schema["files"]}
    screens_doc = site.load("screens_v02.json")
    admin_crm = site.load("admin_crm.json")
    admin_screens = site.load("admin_screens.json")
    operator_doc = site.load("operator.json")
    integrations = site.load("integrations.json")
    integrations_by_id = {r["id"]: r for r in integrations["rows"]}
    states_doc = site.load_optional("v02", "states.json")
    if states_doc is None:
        raise SystemExit("build_brief: data/v02/states.json is required")
    flow_doc = site.load_optional("v02", "flow.json")
    if flow_doc is None:
        raise SystemExit("build_brief: data/v02/flow.json is required (the three T6 funnels)")
    return {
        "schema": schema, "schema_idx": schema_idx, "screens_doc": screens_doc, "admin_crm": admin_crm,
        "admin_screens": admin_screens, "operator_doc": operator_doc, "integrations_by_id": integrations_by_id,
        "states_doc": states_doc, "flow_order": flow_doc["order"],
    }


def build_tables(src):
    t1, config_doc, props_by_event = build_t1(src["schema"], src["screens_doc"])
    t2 = build_t2(src["admin_crm"], src["screens_doc"], src["admin_screens"], src["states_doc"], props_by_event)
    t3 = build_t3(src["admin_screens"])
    return {"T1": t1, "T2": t2, "T3": t3, "config_doc": config_doc}


def main():
    seats_file = os.path.join(DATA, "seats.json")
    if not os.path.exists(seats_file):
        raise SystemExit("build_brief: %s is missing. The seats page (deliverable D7) writes it; "
                          "run scripts/build_brief.py again once it exists." % os.path.relpath(seats_file, ROOT))
    with open(seats_file) as fh:
        raw = fh.read()
    site.check_ascii(os.path.relpath(seats_file, ROOT), raw)
    seats_doc = json.loads(raw)
    problems = validate_seats(seats_doc)
    if problems:
        for p in problems:
            print("ERROR: " + p)
        sys.exit(1)
    questions = flatten_seats(seats_doc)

    src = load_sources()
    partial = build_tables(src)
    t4 = build_t4(src["schema"], src["schema_idx"], questions, src["states_doc"], src["operator_doc"])
    t5 = build_t5(partial["config_doc"], src["states_doc"], src["admin_crm"], src["integrations_by_id"])
    t6 = build_t6(src["screens_doc"], src["flow_order"], src["admin_crm"], src["integrations_by_id"])
    table_rows = {"T1": partial["T1"], "T2": partial["T2"], "T3": partial["T3"], "T4": t4, "T5": t5, "T6": t6}

    page = build_page(table_rows, questions)
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
    counts = ", ".join("%s %d" % (tid, len(table_rows[tid])) for tid, _, _ in TABLES)
    print("wrote docs/%s (%d bytes; %s; %d questions from %s)" %
          (PAGE, len(page), counts, len(questions), os.path.relpath(seats_file, ROOT)))


if __name__ == "__main__":
    main()
