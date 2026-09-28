#!/usr/bin/env python3
"""Provision the Zoho One trial org (India datacentre) by API from the operator page data (phase F, Vatsal,
24 Sep 2026).

Reads, never restates: the operator page's own tables in scripts/build_operator.py (the import order, the picklist
items and their source columns, the band labels), seed/export_schema.json (every column's label, Zoho type and
picklist values, and each file's external ID column), data/seats.json (the seats, so the roles and the saved
views), data/operator.json (the item ids this run marks), seed/config.json (the call length) and the run-3000
exports under data/seed/run-3000/exports/.

Order: CRM fields and picklists on the standard modules; the custom modules App Events and A la carte with their
fields; roles; saved views; records (bulk write upsert on each file's external ID, in the operator page's import
order; Calls through the records API, which bulk write does not cover; the first record insert tests
Created_Time); Desk (department, categories, the ticket fields, tickets); Campaigns lists; the Bookings service.
Every step checks before it creates, so a re-run leaves what is already right alone.

A column maps to an existing field when the field's label is the column's label and its type can hold the
column, the way the import screen auto-maps; every other column becomes a custom field of the schema's type.

Never called, by design: anything that connects a channel, verifies a sender or domain, or sends. That rules out
Campaigns' contact-adding calls (listsubscribe mails a confirmation; the other two document their list key as
"to send a subscription mail"), Bookings staff and appointments (neither the staff invitation nor the booking
notifications are documented as suppressible), and any Desk assignee or help-centre invitation; resolved tickets
close with disableClosureNotification.

Writes data/zoho_provision.json: per operator item, done with a timestamp or left with the reason. The operator
page reads it for the "done by script" marks; seed/zoho/verify.py turns it into seed/zoho/leftovers.md.

Usage:
    python3 seed/zoho/provision.py --plan    print the plan from the data alone; no network, no token
    python3 seed/zoho/provision.py           run it against the org in seed/zoho/.local/token.json
"""
import csv
import datetime
import io
import json
import os
import sys
import time
import zipfile
import zoneinfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import zoho  # noqa: E402
import build_operator as op  # noqa: E402

RUN = "run-3000"
EXPORTS = os.path.join(ROOT, "data", "seed", RUN, "exports")
STATE_FILE = os.path.join(ROOT, "data", "zoho_provision.json")
SCREENS_FILE = os.path.join(ROOT, "data", "screens_v02.json")
STAFF_FILE = os.path.join(ROOT, "data", "seed", RUN, "staff.json")
CAUSE = "Vatsal, 24 Sep 2026 (phase F)"

# seed/export_schema.json zoho_type -> CRM data_type and the create properties (Create Custom Field API, v8)
CRM_TYPES = {
    "single line": ("text", {"length": 255}),
    "phone": ("phone", {"length": 30}),
    "email": ("email", {"length": 100}),
    "picklist": ("picklist", {}),
    "multi-select": ("multiselectpicklist", {}),
    "checkbox": ("boolean", {}),
    "date": ("date", {}),
    "date-time": ("datetime", {}),
    "percent": ("percent", {"length": 5}),
    "number": ("integer", {"length": 9}),
    "multi-line": ("textarea", {"length": 2000, "textarea": {"type": "small"}}),  # the create field API needs the
    # textarea type with the length: small (2000), large (32000) or rich_text (50000); first live run, 28 Sep 2026
    "URL": ("website", {"length": 255}),
}
# the existing field types that can hold a column of each type (an Amount currency field cannot hold "Rs ___")
COMPATIBLE = {
    "text": {"text", "textarea"}, "phone": {"phone", "text"}, "email": {"email"}, "picklist": {"picklist"},
    "multiselectpicklist": {"multiselectpicklist"}, "boolean": {"boolean"}, "date": {"date"},
    "datetime": {"datetime"}, "percent": {"percent", "integer", "double"}, "integer": {"integer", "bigint", "double"},
    "textarea": {"textarea", "text"}, "website": {"website", "text"},
}
DESK_TYPES = {"single line": "Text", "date-time": "DateTime", "multi-line": "Textarea", "email": "Email",
              "phone": "Phone", "date": "Date", "checkbox": "Boolean", "URL": "Website", "number": "Number",
              "percent": "Percent", "picklist": "Picklist"}

# The singular labels the two custom modules need (Create Custom Module API); the plural is the schema's object.
MODULE_SINGULAR = {"App Events": "App Event", "A la carte": "A la carte"}

# Zoho-mandatory fields the export files do not carry, and what fills each wherever the module has the field and no
# column maps to it (Vatsal, 24 Sep 2026, phase F): a custom module's record name is the row's external ID; a deal
# closes on its Start date at the default pipeline's won stage (every deal in the seed is a subscription taken); a
# call's subject is its Topic, its start the Slot, its type Outbound (the adviser rings at the booked slot). Only
# Call_Type is a constant.
MANDATORY_FILL = {
    "Name": {"column": None},
    "Company": {"value": "Individual"},  # Leads Company is layout-mandatory (first live run, 28 Sep 2026: the bulk
    # write job failed with "All mandatory fields are not mapped for the layout [Company]"); the seed's leads are
    # people, not firms, so every lead gets the one placeholder
    "Closing_Date": {"column": "Start"},
    "Stage": {"pipeline": "won_stage"},
    # Deals Account_Name is layout-mandatory too (second pass, 28 Sep 2026: "All mandatory fields are not mapped for
    # the layout [Account_Name]"). The seed's deals belong to people, so one placeholder account holds them all; a
    # lookup wants the record id, so the module goes through the records API (import_records). Only on Deals: the
    # same lookup sits on Contacts, where nothing requires it.
    "Account_Name": {"record": ("Accounts", "Account_Name", "Individual"), "modules": ("Deals",)},
    "Pipeline": {"only_value": True},  # only if Zoho marks it mandatory and the org has exactly one pipeline
    "Subject": {"column": "Topic"},
    "Call_Start_Time": {"column": "Slot"},
    "Call_Type": {"value": "Outbound"},
}
# The Calls status field: the insert records docs name it Outbound_Call_Status; the trial org's field list names it
# Outgoing_Call_Status (first live run, 28 Sep 2026). Whichever the org has is used; the row supplies it, the
# contact link and the logged length itself (import_calls).
CALL_STATUS_APIS = ("Outgoing_Call_Status", "Outbound_Call_Status")
# A logged call needs a duration in Zoho; the seed's time model gives every call the same length
# (seed/config.json time_model.call_minutes). No-shows and cancellations get none: Zoho decides what it accepts.
CALL_STATUS_FIELDS = {"completed": {"status": "Completed", "duration": True},
                      "booked": {"status": "Scheduled"}}
# Zoho field labels that differ from the file's column label (first live run, 28 Sep 2026): "Keyword" is refused
# ("System keyword not allowed in field label"), and Tasks, Calls and Events share one label namespace ("Field
# label duplicate"), so a Calls "Status" collides with the built-in Tasks Status and a Tasks "Contact External ID"
# with the field of that name created on Calls. The file column keeps its label; only the Zoho field is named so.
LABEL_MAP = {("zoho/leads.csv", "Keyword"): "Keyword Sent",
             ("zoho/calls.csv", "Status"): "Slot Status",
             ("zoho/calls.csv", "Notes"): "Description",  # any label holding "Notes" is refused on Calls (second and
             # third pass: "System keyword not allowed"); the built-in Calls Description field, a textarea, takes it
             ("zoho/tasks.csv", "Contact External ID"): "Task Contact External ID"}

DESK_CONTACT_COLUMNS = {"Contact Email": "email", "Contact Phone": "phone"}  # the ticket's contact, not a field
DESK_STATUS = {"open": "Open", "resolved": "Closed"}  # the file's two values -> Desk's status categories
# Tasks Status is Zoho's built-in picklist (the docs do not enumerate it; the org's field metadata does). The file's
# two values are translated to it instead of being added to it, what the import screen's value mapping would do
# (Vatsal, 24 Sep 2026): a done task is Completed, an open one Not Started. Applied where the file is read and where
# a column's values are listed, so the picklist check, the bulk file and the records API all see the same values.
VALUE_MAP = {("zoho/tasks.csv", "Status"): {"done": "Completed", "open": "Not Started"}}

# the lists this phase brings in (Vatsal, 24 Sep 2026: S0, S0w, S1, S2); the rest stay on the operator page
CAMPAIGN_LISTS = ["S0", "S0w", "S1", "S2"]
READ_ONLY_SEATS = {"finance"}  # operator item roles/finance, plan section 13 item 6: "Finance (read only)"
PRINCIPAL_SEAT = "principal-officer"  # sees everything: the top of the hierarchy under the org's own top role

BULK_ROWS = 10000  # the bulk write limitations page's per-request cap (the lower of the two figures it gives)
POLL = [5, 5, 10, 10, 15, 30]


# ---- data -----------------------------------------------------------------------------------------------------

def read_csv(path):
    with open(os.path.join(EXPORTS, path), newline="") as fh:
        rows = list(csv.DictReader(fh))
    for (p, label), table in VALUE_MAP.items():
        if p == path:
            for row in rows:
                row[label] = table.get(row[label], row[label])
    return rows


def load_json(path):
    with open(path) as fh:
        return json.load(fh)


class Data:
    def __init__(self):
        self.schema = op.load_schema()
        self.idx = op.schema_index(self.schema)
        self.seats = op.load_seats()["seats"]
        self.operator_items = {it["id"]: it["text"] for it in op.all_items(load_json(op.DATA_FILE))}
        self.config = load_json(os.path.join(ROOT, "seed", "config.json"))
        self.crm_files = [(stem, path) for stem, path in op.IMPORT_FILES if self.idx[path]["system"] == "Zoho CRM"]
        self.desk_file = next(path for stem, path in op.IMPORT_FILES if self.idx[path]["system"] == "Zoho Desk")
        # picklist items with more than one source (Source) put the union of their values on every source field
        self.union = {}
        for item_id, sources in op.PICKLISTS:
            vals = []
            for path, label in sources:
                for v in op.find_column(self.idx, path, label).get("values") or []:
                    if v not in vals:
                        vals.append(v)
            for path, label in sources:
                self.union[(path, label)] = (item_id, vals)

    def values(self, path, col):
        if (path, col["label"]) in self.union:
            return self.union[(path, col["label"])][1]
        if col.get("type") == "band":
            return op.BAND_LABELS[col["label"]]
        table = VALUE_MAP.get((path, col["label"]), {})
        return [table.get(v, v) for v in col.get("values") or []]

    def field_item(self, stem, obj):
        item = "fields/%s" % stem
        return item if item in self.operator_items else "module/%s" % op.slugify(obj)

    def people(self):
        """person id -> (object, row) from the Contacts and Leads files."""
        out = {}
        for stem, path in self.crm_files:
            f = self.idx[path]
            if f["object"] in ("Contacts", "Leads"):
                for row in read_csv(path):
                    out[row[f["external_id"]]] = (f["object"], row)
        return out

    def person_by_contact(self):
        """phone and email -> person id, for the Desk tickets, which carry only the contact's phone and email."""
        out = {}
        for pid, (obj, row) in self.people().items():
            for key in ("Phone", "Email"):
                if row.get(key):
                    out[row[key]] = pid
        return out

    def service_name(self):
        # the app's own name for the call a client books: screen K01 (data/screens_v02.json)
        return next(s["title"] for s in load_json(SCREENS_FILE)["screens"] if s.get("id") == "K01")

    def adviser_staff(self):
        staff = load_json(STAFF_FILE)
        return [s["name"] for s in staff.values() if "adviser" in s.get("roles", [])]


# ---- value shaping -------------------------------------------------------------------------------------------

def split_multi(value):
    return [v.strip() for v in value.split(";") if v.strip()]


def to_zone(value, tz):
    return datetime.datetime.fromisoformat(value).astimezone(tz).strftime("%Y-%m-%d %H:%M:%S")


def to_utc_ms(value):
    return datetime.datetime.fromisoformat(value).astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def csv_value(value, data_type, tz):
    """A bulk write CSV cell: multi-select joined by ';', date-times as the documented 'YYYY-MM-DD HH:MM:SS' in the
    CRM user's time zone; everything else as exported."""
    if not value:
        return ""
    if data_type == "multiselectpicklist":
        return ";".join(split_multi(value))
    if data_type == "datetime":
        return to_zone(value, tz)
    return value


def json_value(value, data_type):
    """A records API value."""
    if value == "":
        return None
    if data_type == "multiselectpicklist":
        return split_multi(value)
    if data_type == "boolean":
        return value == "true"
    if data_type in ("integer", "bigint"):
        return int(value)
    if data_type in ("percent", "double"):
        return float(value)
    return value


def chunks(seq, n):
    return [seq[i:i + n] for i in range(0, len(seq), n)]


def label_index(fields):
    """label -> field, by the label the import screen shows (display_label), by field_label, which can differ
    on older standard fields, and last by api_name, for standard fields whose label carries a section prefix
    (the Leads City field is labelled "Address - City"; first live run, 28 Sep 2026)."""
    out = {}
    for fld in fields:
        for key in ("display_label", "field_label", "api_name"):
            if fld.get(key) and fld[key] not in out:
                out[fld[key]] = fld
    return out


def ascii_text(value, n=300):
    text = json.dumps(value, sort_keys=True) if isinstance(value, (dict, list)) else str(value)
    text = text.encode("ascii", "replace").decode()
    return text if len(text) <= n else text[:n] + "..."


# ---- state ---------------------------------------------------------------------------------------------------

def load_state():
    if os.path.exists(STATE_FILE):
        return load_json(STATE_FILE)
    return {}


def guarded(rec, item, what, fallback, fn, *args):
    """Run one step; a refusal (or an answer shaped unlike the docs) is recorded against its operator item and the
    run goes on to the next step."""
    try:
        fn(*args)
    except zoho.ApiError as e:
        rec.leave(item, what, e, fallback, e.code())
    except Exception as e:  # an answer shaped unlike the docs, a lost connection: logged, left, and the run goes on
        rec.leave(item, what, "unexpected: %s %s" % (type(e).__name__, e), fallback)


def coql_rows(resp):
    """COQL rows from either answer shape the docs show: {"data": [...]} or {"response": {"result": [{Module: [...]}]}}."""
    if not isinstance(resp, dict):
        return []
    if isinstance(resp.get("data"), list):
        return resp["data"]
    rows = []
    for part in (resp.get("response") or {}).get("result") or []:
        for value in part.values():
            rows.extend(value)
    return rows


class Record:
    """What the run did, per operator item. An item already done in an earlier run keeps that run's timestamp."""

    def __init__(self, data):
        self.data = data
        self.prev = load_state()
        self.items = {}
        self.left = []
        self.created_time = self.prev.get("created_time")
        self.observed = {}

    def done(self, item, note=""):
        if item in self.items and self.items[item]["status"] == "left":
            return
        prev = (self.prev.get("items") or {}).get(item) or {}
        at = prev.get("at") if prev.get("status") == "done" else None
        self.items[item] = {"status": "done", "at": at or zoho.stamp(), "note": note}

    def leave(self, item, what, why, fallback, code=""):
        self.items[item] = {"status": "left", "note": what}
        self.left.append({"item": item, "what": what, "why": ascii_text(why, 500), "code": ascii_text(code, 80),
                          "fallback": fallback})
        zoho.log("  left: %s: %s (%s)" % (item, what, ascii_text(why, 200)))

    def note(self, item, what, why, fallback):
        # something the run did not carry over although the item is done (a column with no field that can hold it)
        self.left.append({"item": item, "what": what, "why": ascii_text(why, 500), "code": "", "fallback": fallback,
                          "kind": "note"})
        zoho.log("  note: %s: %s" % (item, what))

    def save(self):
        items = dict(self.prev.get("items") or {})
        items.update(self.items)
        doc = {
            "about": "Written by seed/zoho/provision.py (phase F): per operator item, done by script with a "
                     "timestamp, or left with the reason and the manual fallback. scripts/build_operator.py reads "
                     "the done items; seed/zoho/verify.py writes seed/zoho/leftovers.md from it.",
            "cause": CAUSE,
            "run": RUN,
            "last_run": zoho.stamp(),
            "created_time": self.created_time,
            "observed": self.observed,
            "items": dict(sorted(items.items())),
            "left": self.left,
        }
        text = json.dumps(doc, indent=1, sort_keys=False, ensure_ascii=True) + "\n"
        with open(STATE_FILE, "w") as fh:
            fh.write(text)


# ---- CRM -----------------------------------------------------------------------------------------------------

class Crm:
    def __init__(self, client, data, rec):
        self.c, self.d, self.rec = client, data, rec
        self.maps = {}      # path -> {column label: api name}
        self.types = {}     # path -> {column label: data_type of the field it maps to}
        self.meta = {}      # module api name -> fields metadata
        self.modules = {}   # object -> module api name
        self.picklist_ok = {}  # (path, label) -> True when the field carries every value
        self.placeholders = {}  # (module, field, value) -> record id, the placeholder a lookup fill points at
        self.ct_tried = False  # the Created_Time test runs once, on the run's first record insert
        org = client.crm("GET", "/org")["org"][0]
        self.zgid = org["zgid"]
        lic = org.get("license_details") or {}
        rec.observed["crm_org"] = {"type": org.get("type"), "edition": lic.get("paid_type"),
                                   "trial": lic.get("trial_type"), "trial_expiry": lic.get("trial_expiry")}
        me = client.crm("GET", "/users", params={"type": "CurrentUser"})["users"][0]
        self.tz = zoneinfo.ZoneInfo(me.get("time_zone") or "Asia/Kolkata")
        rec.observed["crm_user_time_zone"] = me.get("time_zone")

    def module_list(self):
        return self.c.crm("GET", "/settings/modules")["modules"]

    def fields(self, module_api):
        return self.c.crm("GET", "/settings/fields", params={"module": module_api})["fields"]

    # -- fields and picklists
    def ensure_fields(self, stem, path, module_api):
        f = self.d.idx[path]
        item = self.d.field_item(stem, f["object"])
        listed = self.fields(module_api)
        by_label = label_index(listed)
        mapping, types, create, refused, file_label = {}, {}, [], set(), {}
        clean = True
        for col in f["columns"]:
            label = col["label"]
            zlabel = LABEL_MAP.get((path, label), label)  # the Zoho field's label; mapping keys stay the file's
            if zlabel != label:
                zoho.log("  %s %s: the Zoho field is labelled %s" % (module_api, label, zlabel))
            want, extra = CRM_TYPES[col["zoho_type"]]
            values = self.d.values(path, col) if want in ("picklist", "multiselectpicklist") else []
            if (path, label) in VALUE_MAP:
                zoho.log("  %s %s: file values translated (%s)" % (module_api, label, ", ".join(
                    "%s -> %s" % kv for kv in VALUE_MAP[(path, label)].items())))
            is_ext = label == f.get("external_id")
            have = by_label.get(zlabel)
            if have:
                if have["data_type"] not in COMPATIBLE[want]:
                    zoho.log("  %s %s: existing %s field cannot hold a %s column; not mapped" % (module_api, label, have["data_type"], want))
                    continue
                mapping[label], types[label] = have["api_name"], have["data_type"]
                if values:
                    self.picklist_ok[(path, label)] = self.ensure_values(module_api, have, values, item, label)
                if is_ext and not have.get("unique"):
                    try:
                        self.c.crm("PATCH", "/settings/fields/%s" % have["id"], params={"module": module_api},
                                   body={"fields": [{"unique": {"case_sensitive": False}}]})
                    except zoho.ApiError as e:
                        clean = False
                        self.rec.leave(item, "make %s unique on %s" % (label, module_api), e, "In Zoho, edit the field "
                                       "and tick Do not allow duplicate values.", e.code())
                continue
            d = {"field_label": zlabel, "data_type": want}
            file_label[zlabel] = label
            d.update(extra)
            if values:
                d["pick_list_values"] = [{"display_value": v, "actual_value": v} for v in values]
            if is_ext:
                d["unique"] = {"case_sensitive": False}
            create.append(d)
        for batch in chunks(create, 5):  # the Create Custom Field API takes five per call
            try:
                resp = self.c.crm("POST", "/settings/fields", params={"module": module_api}, body={"fields": batch})
                results = (resp or {}).get("fields") or []
            except zoho.ApiError as e:
                results = e.body.get("fields") if isinstance(e.body, dict) and isinstance(e.body.get("fields"), list) else \
                    [{"status": "error", "code": e.code(), "message": str(e)} for _ in batch]
            for d, r in zip(batch, results):
                if r.get("status") == "success":
                    zoho.log("  %s: created %s (%s)" % (module_api, d["field_label"], d["data_type"]))
                else:
                    clean = False
                    refused.add(d["field_label"])
                    self.rec.leave(item, "create the %s field %s" % (module_api, d["field_label"]),
                                   r.get("message") or r, "Create it by hand with the type and values the operator "
                                   "page lists under %s." % item, r.get("code", ""))
        if create:
            listed = self.fields(module_api)
            by_label = label_index(listed)
            for d in create:
                have = by_label.get(d["field_label"])
                label = file_label[d["field_label"]]
                if have:
                    mapping[label], types[label] = have["api_name"], have["data_type"]
                    if d.get("pick_list_values"):
                        self.picklist_ok[(path, label)] = True
                elif d["field_label"] not in refused:
                    clean = False
                    self.rec.leave(item, "find the %s field %s after creating it" % (module_api, d["field_label"]),
                                   "not in the field list after the create call", "Check the field in Zoho, create "
                                   "it by hand if missing, then re-run.")
        self.maps[path], self.types[path] = mapping, types
        self.meta[module_api] = listed
        if clean:
            self.rec.done(item, "%d columns, %d created" % (len(f["columns"]), len(create)))

    def ensure_values(self, module_api, field, values, item, label):
        have = set()
        for pv in field.get("pick_list_values") or []:
            have.add(pv.get("actual_value"))
            have.add(pv.get("display_value"))
        missing = [v for v in values if v not in have]
        if not missing:
            return True
        try:
            self.c.crm("PATCH", "/settings/fields/%s" % field["id"], params={"module": module_api},
                       body={"fields": [{"pick_list_values": [{"display_value": v, "actual_value": v} for v in missing]}]})
            zoho.log("  %s %s: added %d picklist values" % (module_api, label, len(missing)))
            return True
        except zoho.ApiError as e:
            self.rec.leave(item, "add %d values to %s %s" % (len(missing), module_api, label), e,
                           "Add the values by hand: %s." % "; ".join(missing), e.code())
            return False

    def picklist_items(self):
        for item_id, sources in op.PICKLISTS:
            if all(self.picklist_ok.get(src) for src in sources):
                self.rec.done(item_id)
            elif item_id not in self.rec.items:
                self.rec.leave(item_id, "picklist values", "a source field is missing or refused its values",
                               "Create the picklist by hand with the values the operator page lists.")

    def ensure_module(self, obj):
        for m in self.module_list():
            if m.get("plural_label") == obj:
                return m["api_name"]
        profiles = [{"id": p["id"]} for p in self.c.crm("GET", "/settings/profiles")["profiles"]
                    if p.get("type", "normal_profile") == "normal_profile"]
        body = {"modules": [{"plural_label": obj, "singular_label": MODULE_SINGULAR[obj], "profiles": profiles}]}
        self.c.crm("POST", "/settings/modules", body=body)
        zoho.log("  created the custom module %s" % obj)
        for m in self.module_list():
            if m.get("plural_label") == obj:
                return m["api_name"]
        raise zoho.ApiError(None, "module %s not listed after creation" % obj, "GET", "/settings/modules")

    def all_fields(self):
        standard, custom = [], []
        listed = {m.get("plural_label"): m for m in self.module_list()}
        for stem, path in self.d.crm_files:
            obj = self.d.idx[path]["object"]
            m = listed.get(obj)
            (standard if m and m.get("generated_type") != "custom" else custom).append((stem, path, obj))
        for stem, path, obj in standard:
            zoho.log("fields: %s" % obj)
            self.modules[obj] = listed[obj]["api_name"]
            guarded(self.rec, self.d.field_item(stem, obj), "fields on %s" % obj, "Create the fields by hand as the "
                    "operator page lists them.", self.ensure_fields, stem, path, self.modules[obj])
        for stem, path, obj in custom:
            zoho.log("custom module: %s" % obj)
            item = self.d.field_item(stem, obj)
            try:
                self.modules[obj] = self.ensure_module(obj)
            except zoho.ApiError as e:
                self.rec.leave(item, "create the custom module %s" % obj, e, "Create the module by hand (Setup, "
                               "Modules and Fields), then re-run.", e.code())
                continue
            guarded(self.rec, item, "fields on %s" % obj, "Create the fields by hand as the operator page lists "
                    "them.", self.ensure_fields, stem, path, self.modules[obj])
        self.picklist_items()

    # -- roles
    def roles(self):
        zoho.log("roles")
        roles = self.c.crm("GET", "/settings/roles")["roles"]
        by_name = {r["name"]: r for r in roles}
        top = next((r for r in roles if not r.get("reporting_to")), None)
        seats = sorted(self.d.seats, key=lambda s: s["id"] != PRINCIPAL_SEAT)
        principal = next(s for s in seats if s["id"] == PRINCIPAL_SEAT)
        for seat in seats:
            item, name = "roles/%s" % seat["id"], seat["seat"]
            parent = top if seat is principal else by_name.get(principal["seat"])
            if name not in by_name:
                if parent is None:
                    self.rec.leave(item, "create the %s role" % name, "no role to report to", "Create it by hand "
                                   "under the Principal officer role.")
                    continue
                try:
                    self.c.crm("POST", "/settings/roles", body={"roles": [{"name": name, "reporting_to": {"id": parent["id"]},
                                                                           "share_with_peers": False}]})
                    zoho.log("  created the role %s" % name)
                except zoho.ApiError as e:
                    self.rec.leave(item, "create the %s role" % name, e, "Create it by hand under %s." %
                                   (parent.get("name")), e.code())
                    continue
                by_name = {r["name"]: r for r in self.c.crm("GET", "/settings/roles")["roles"]}
            if seat["id"] in READ_ONLY_SEATS:
                self.rec.leave(item, "make the %s seat read only" % name, "read only is a profile in Zoho, not a "
                               "role; the role exists", "When a %s user is added, give them a profile with view "
                               "permissions only (clone Standard, untick create, edit and delete)." % name)
            else:
                self.rec.done(item)

    # -- saved views
    def views(self):
        zoho.log("saved views")
        system_of = {f["object"]: f["system"] for f in self.d.schema["files"]}
        for seat in self.d.seats:
            for q in seat["questions"]:
                view = q.get("view") if q.get("surface") == "Zoho" else None
                if not view or system_of.get(view["object"]) not in ("Zoho CRM", "Zoho Desk"):
                    continue
                api = "CRM API v8 has Get Custom View Metadata and Change Sort Order only" if system_of[view["object"]] \
                    == "Zoho CRM" else "the Desk API lists views but has no create call"
                self.rec.leave("views/%s" % seat["id"], "saved view %s (%s)" % (view["name"], view["object"]),
                               "no create endpoint: " + api, "Create it by hand on %s: %s." % (view["object"], view["criteria"]))

    # -- records
    def fill_for(self, module_api, path, mapped_apis):
        """The MANDATORY_FILL fields this module has and no column maps, each with how it is filled; and the
        system-mandatory fields nothing fills."""
        f = self.d.idx[path]
        labels = [c["label"] for c in f["columns"]]
        fills, unfilled = [], []
        pipeline = None
        for fld in self.meta.get(module_api) or self.fields(module_api):
            api = fld["api_name"]
            if api in mapped_apis:
                continue
            rule = MANDATORY_FILL.get(api)
            if rule and rule.get("modules") and module_api not in rule["modules"]:
                rule = None
            if rule and "record" in rule:
                rid = self.placeholder_id(*rule["record"])
                if rid:
                    fills.append((api, fld["data_type"], None, {"id": rid}))
                    continue
            elif rule and rule.get("only_value"):
                if not fld.get("system_mandatory"):
                    continue
                vals = [pv.get("actual_value") for pv in fld.get("pick_list_values") or []
                        if pv.get("actual_value") and pv.get("actual_value") != "-None-"]
                if len(vals) == 1:
                    fills.append((api, fld["data_type"], None, vals[0]))
                    continue
            elif rule and "pipeline" in rule:
                pipeline = pipeline or self.default_pipeline(module_api) or self.stage_from_field(fld)
                if pipeline:
                    fills.append((api, fld["data_type"], None, pipeline[rule["pipeline"]]))
                    continue
            elif rule and "value" in rule:
                fills.append((api, fld["data_type"], None, rule["value"]))
                continue
            elif rule and (rule["column"] or f["external_id"]) in labels:
                fills.append((api, fld["data_type"], rule["column"] or f["external_id"], None))
                continue
            if fld.get("system_mandatory") and fld.get("data_type") != "ownerlookup" and not fld.get("read_only") \
                    and not fld.get("field_read_only"):
                unfilled.append(api)
        return fills, unfilled

    def default_pipeline(self, module_api):
        layouts = self.c.crm("GET", "/settings/layouts", params={"module": module_api}).get("layouts") or []
        for lay in layouts:
            resp = self.c.crm("GET", "/settings/pipeline", params={"layout_id": lay["id"]}) or {}
            for p in resp.get("pipeline") or []:
                if p.get("default"):
                    won = next((s.get("actual_value") or s.get("display_value") for s in p.get("maps") or []
                                if s.get("forecast_type") == "Closed Won"), None)
                    if won:
                        self.rec.observed["deal_stage_fill"] = won
                        return {"won_stage": won}
        return None

    def stage_from_field(self, fld):
        """An org with no pipelines (GET settings/pipeline answers 204; first live run, 28 Sep 2026) keeps its stages
        on the Stage field itself: the picklist value whose forecast_type is Closed Won is the won stage."""
        won = next((pv.get("actual_value") for pv in fld.get("pick_list_values") or []
                    if pv.get("forecast_type") == "Closed Won"), None)
        if won:
            self.rec.observed["deal_stage_fill"] = won
            return {"won_stage": won}
        return None

    def import_all(self):
        for stem, path in self.d.crm_files:
            obj = self.d.idx[path]["object"]
            item = "import/%s" % stem
            if obj not in self.modules or path not in self.maps:
                self.rec.leave(item, "import %s" % obj, "the module or its fields were not set up", "Import the file "
                               "by hand once the fields exist (operator page step 10).")
                continue
            zoho.log("import: %s" % obj)
            guarded(self.rec, item, "import %s" % obj, "Import %s by hand (operator page step 10)." % path,
                    self.import_calls if obj == "Calls" else self.import_bulk, stem, path, self.modules[obj])
            self.rec.save()

    def upload_columns(self, stem, path, module_api, supplied=()):
        """The file's mapped columns (external ID first, so a result file's first column names the row), the
        MANDATORY_FILL fills, and the system-mandatory fields nothing fills. supplied: fields the caller sets per row."""
        f = self.d.idx[path]
        mapping = self.maps[path]
        item = "import/%s" % stem
        ext = f["external_id"]
        if ext not in mapping:
            raise zoho.ApiError(None, "the external ID field %s is missing" % ext, "-", module_api)
        labels = [ext] + [c["label"] for c in f["columns"] if c["label"] != ext and c["label"] in mapping]
        for c in f["columns"]:
            if c["label"] not in mapping:
                self.rec.note(item, "column %s not imported" % c["label"], "the %s field with that label cannot hold "
                              "this column (the column carries only placeholder values)" % module_api,
                              "Map it once the field can hold the values (for Amount: when prices are set).")
        fills, unfilled = self.fill_for(module_api, path, {mapping[x] for x in labels} | set(supplied))
        return labels, fills, unfilled

    def created_time_test(self, module_api, path, labels, fills):
        """On the run's first record insert: send Created_Time as the row's own first date and read back what Zoho
        stamped. Only an insert answers the question; an update of a row an earlier run wrote does not."""
        if self.ct_tried:
            return
        self.ct_tried = True
        prev = self.rec.created_time or {}
        if prev.get("answer") in ("accepted", "ignored", "refused"):
            zoho.log("  Created_Time: answered on %s: %s" % (prev.get("at"), prev.get("answer")))
            return
        f = self.d.idx[path]
        row = read_csv(path)[0]
        col = next((c for c in f["columns"] if c["zoho_type"] in ("date", "date-time") and row[c["label"]]), None)
        if not col:
            return
        value = row[col["label"]]
        sent = value + "T00:00:00+05:30" if col["zoho_type"] == "date" else value
        rec = self.json_record(row, path, labels, fills)
        rec["Created_Time"] = sent
        body = {"data": [rec], "duplicate_check_fields": [self.maps[path][f["external_id"]]], "trigger": []}
        answer = {"module": module_api, "record": row[f["external_id"]], "sent": sent, "at": zoho.stamp()}
        try:
            r = (self.c.crm("POST", "/%s/upsert" % module_api, body=body).get("data") or [{}])[0]
        except zoho.ApiError as e:
            r = e.body["data"][0] if isinstance(e.body, dict) and e.body.get("data") else {"status": "error", "message": str(e)}
        details = r.get("details") or {}
        if r.get("status") == "success" and r.get("action") != "insert":
            answer.update({"answer": "unknown", "detail": "the record already existed, so this was an update"})
        elif r.get("status") == "success":
            back = details.get("Created_Time") or ""
            try:
                same = datetime.datetime.fromisoformat(back) == datetime.datetime.fromisoformat(sent)
            except ValueError:
                same = False
            answer.update({"read_back": back, "answer": "accepted" if same else "ignored"})
        elif details.get("api_name") == "Created_Time":
            answer.update({"answer": "refused", "detail": ascii_text("%s %s" % (r.get("code"), r.get("message")))})
        else:
            answer.update({"answer": "unknown", "detail": ascii_text("the record itself was refused: %s %s %s" % (
                r.get("code"), r.get("message"), details))})
        self.rec.created_time = answer
        zoho.log("  Created_Time test on the first record insert (%s %s): %s %s" % (
            module_api, answer["record"], answer["answer"], answer.get("read_back") or answer.get("detail") or ""))

    def import_bulk(self, stem, path, module_api):
        """Bulk write upsert on the external ID. The CSV header row is the field API names, so the job auto-maps
        (the documented mode for 'YYYY-MM-DD HH:MM:SS' date-times); at most BULK_ROWS rows per job."""
        f = self.d.idx[path]
        item = "import/%s" % stem
        rows = read_csv(path)
        labels, fills, unfilled = self.upload_columns(stem, path, module_api)
        if unfilled:
            self.rec.leave(item, "import %s" % f["object"], "mandatory fields with no column and no rule: %s" %
                           ", ".join(unfilled), "Import by hand and give those fields a value on the import screen.",
                           "MANDATORY_NOT_FOUND")
            return
        self.created_time_test(module_api, path, labels, fills)
        if any(isinstance(const, dict) for _, _, _, const in fills):  # a lookup fill: only the records API takes {"id"}
            self.import_records(stem, path, module_api, rows, labels, fills)
            return
        mapping, types = self.maps[path], self.types[path]
        header = [mapping[x] for x in labels] + [api for api, _, _, _ in fills]
        ext_api = mapping[f["external_id"]]
        totals = {"added": 0, "updated": 0, "other": 0}
        errors = {}
        for part, batch in enumerate(chunks(rows, BULK_ROWS), start=1):
            buf = io.StringIO()
            w = csv.writer(buf, lineterminator="\n")
            w.writerow(header)
            for row in batch:
                w.writerow([csv_value(row[x], types[x], self.tz) for x in labels] +
                           [csv_value(row[col], dtype, self.tz) if col else const for _, dtype, col, const in fills])
            name = "%s_%d.csv" % (stem, part)
            zbuf = io.BytesIO()
            with zipfile.ZipFile(zbuf, "w", zipfile.ZIP_DEFLATED) as z:
                z.writestr(name, buf.getvalue())
            up = self.c.request("POST", zoho.UPLOAD + "/crm/v8/upload", files={"file": (name + ".zip", zbuf.getvalue(), "application/zip")},
                                headers={"feature": "bulk-write", "X-CRM-ORG": self.zgid}, timeout=300, safe=True)
            file_id = up["details"]["file_id"]
            job = self.c.request("POST", zoho.API + "/crm/bulk/v8/write", safe=True, body={
                "character_encoding": "UTF-8", "operation": "upsert",
                "resource": [{"type": "data", "module": {"api_name": module_api}, "file_id": file_id, "file_names": [name],
                              "find_by": ext_api}]})
            job_id = job["details"]["id"]
            zoho.log("  bulk write job %s: %s, %d rows" % (job_id, name, len(batch)))
            counts, errs = self.job_result(self.wait_job(job_id))
            for k in totals:
                totals[k] += counts.get(k, 0)
            for k, v in errs.items():
                errors[k] = errors.get(k, 0) + v
        zoho.log("  %s: %d added, %d updated, %d not written, of %d" % (f["object"], totals["added"], totals["updated"],
                                                                     totals["other"], len(rows)))
        if totals["added"] + totals["updated"] == len(rows):
            self.rec.done(item, "%d rows" % len(rows))
        else:
            detail = "; ".join("%s (%d rows)" % (k, v) for k, v in sorted(errors.items()))
            self.rec.leave(item, "%d of %d %s rows not written" % (len(rows) - totals["added"] - totals["updated"],
                                                                  len(rows), f["object"]), detail or "see the job result",
                           "Fix the cause, then re-run (upsert: rows already in are updated, not duplicated).",
                           ",".join(sorted({k.split("-")[0] for k in errors})))

    def wait_job(self, job_id):
        waited, i = 0, 0
        while True:
            resp = self.c.request("GET", zoho.API + "/crm/bulk/v8/write/%s" % job_id)
            if isinstance(resp, dict) and isinstance(resp.get("data"), list):
                resp = resp["data"][0]
            status = (resp or {}).get("status", "")
            if status in ("COMPLETED", "FAILED"):
                return resp
            wait = POLL[min(i, len(POLL) - 1)]
            i += 1
            waited += wait
            if waited > 1800:
                raise zoho.ApiError(None, "bulk write job %s still %s after 30 minutes" % (job_id, status), "GET", "bulk write")
            time.sleep(wait)

    def job_result(self, result):
        """Per-row outcome from the job's result file; when it cannot be read, the job's own counts."""
        f = ((result.get("resource") or [{}])[0].get("file") or {})
        url = (result.get("result") or {}).get("download_url")
        if url:
            try:
                return parse_result(self.c.download(url if url.startswith("http") else zoho.API + url))
            except Exception as e:  # the job's own counts still stand; only the per-row reasons are lost
                zoho.log("  result file not read (%s); using the job's counts" % ascii_text(e, 120))
        counts = {"added": f.get("added_count", 0), "updated": f.get("updated_count", 0), "other": f.get("skipped_count", 0)}
        errors = {}
        if counts["other"] or result.get("status") == "FAILED":
            errors["%s, %d rows skipped (no result file)" % (result.get("status"), counts["other"])] = counts["other"]
        return counts, errors

    def json_record(self, row, path, labels, fills, extra=None):
        mapping, types = self.maps[path], self.types[path]
        rec = {}
        for x in labels:
            rec[mapping[x]] = json_value(row[x], types[x])
        for api, dtype, col, const in fills:
            rec[api] = json_value(row[col], dtype) if col else const
        rec.update(extra or {})
        return rec

    def record_ids(self, module_api, ext_api, values):
        out = {}
        for part in chunks(sorted(values), 50):
            q = "select id, %s from %s where %s in (%s)" % (ext_api, module_api, ext_api, ", ".join("'%s'" % v for v in part))
            for r in coql_rows(self.c.crm("POST", "/coql", body={"select_query": q}, safe=True)):
                out[r[ext_api]] = r["id"]
        return out

    def import_records(self, stem, path, module_api, rows, labels, fills):
        """The records API upsert on the external ID, 100 rows per call: for a module whose fill is a lookup record
        (Deals Account_Name), which a bulk write header cannot carry (a lookup column there needs a find_by mapping)."""
        f = self.d.idx[path]
        item = "import/%s" % stem
        ext_api = self.maps[path][f["external_id"]]
        ok, errors = 0, {}
        for batch in chunks(rows, 100):
            data = [self.json_record(row, path, labels, fills) for row in batch]
            try:
                resp = self.c.crm("POST", "/%s/upsert" % module_api, body={"data": data, "duplicate_check_fields": [ext_api], "trigger": []})
                results = resp.get("data") or []
            except zoho.ApiError as e:
                results = e.body.get("data") if isinstance(e.body, dict) and isinstance(e.body.get("data"), list) else \
                    [{"status": "error", "code": e.code(), "message": str(e)} for _ in batch]
            for r in results:
                if r.get("status") == "success":
                    ok += 1
                else:
                    why = (r.get("details") or {}).get("api_name") or ascii_text(r.get("message") or "")
                    key = "%s-%s" % (r.get("code"), why)
                    errors[key] = errors.get(key, 0) + 1
        zoho.log("  %s: %d of %d written" % (f["object"], ok, len(rows)))
        if ok == len(rows):
            self.rec.done(item, "%d rows" % ok)
        else:
            self.rec.leave(item, "%d of %d %s rows not written" % (len(rows) - ok, len(rows), f["object"]),
                           "; ".join("%s: %d rows" % (k, v) for k, v in sorted(errors.items())),
                           "Fix the cause, then re-run (upsert: rows already in are updated, not duplicated).",
                           ",".join(sorted({k.split("-")[0] for k in errors})))

    def placeholder_id(self, module_api, field_api, value):
        """The id of the one record in module_api whose field_api is value, created when missing: the placeholder a
        layout-mandatory lookup points at."""
        key = (module_api, field_api, value)
        if key not in self.placeholders:
            found = coql_rows(self.c.crm("POST", "/coql", safe=True, body={
                "select_query": "select id from %s where %s = '%s' limit 1" % (module_api, field_api, value)}))
            if found:
                rid = found[0]["id"]
                zoho.log("  %s: placeholder %s found" % (module_api, value))
            else:
                resp = self.c.crm("POST", "/%s" % module_api, body={"data": [{field_api: value}], "trigger": []})
                rid = ((resp.get("data") or [{}])[0].get("details") or {}).get("id")
                zoho.log("  %s: placeholder %s created" % (module_api, value))
            self.placeholders[key] = rid
            self.rec.observed["%s_placeholder" % module_api.lower()] = value
        return self.placeholders[key]

    def import_calls(self, stem, path, module_api):
        """Calls are not a bulk write module and not an upsert module: the records API insert, or update for rows an
        earlier run wrote (found by external ID), 100 rows per call, each call linked to its
        contact (Who_Id). A row whose contact is not in Zoho is not written."""
        f = self.d.idx[path]
        item = "import/%s" % stem
        rows = read_csv(path)
        status_api = next((fld["api_name"] for fld in self.meta.get(module_api) or self.fields(module_api)
                           if fld["api_name"] in CALL_STATUS_APIS), None)
        if not status_api:
            zoho.log("  Calls: the org has none of %s; the call status is not written" % ", ".join(CALL_STATUS_APIS))
        supplied = {"Who_Id", "Call_Duration"} | ({status_api} if status_api else set())
        labels, fills, unfilled = self.upload_columns(stem, path, module_api, supplied=supplied)
        if unfilled:
            self.rec.leave(item, "import Calls", "mandatory fields with no column and no rule: %s" % ", ".join(unfilled),
                           "Import by hand and give those fields a value on the import screen.", "MANDATORY_NOT_FOUND")
            return
        cpath = next(p for s, p in self.d.crm_files if self.d.idx[p]["object"] == "Contacts")
        link = self.d.idx[cpath]["external_id"]
        contact_ids = self.record_ids(self.modules["Contacts"], self.maps[cpath][link], {r[link] for r in rows})
        minutes = int(self.d.config["time_model"]["call_minutes"])
        duration = "%02d:%02d" % (minutes // 60, minutes % 60)
        ext_api = self.maps[path][f["external_id"]]
        # Calls are outside the upsert API's module list (the first live run answered "the given module is not
        # supported for this api"), so a re-run finds the rows already written by their external ID and updates
        # them (PUT, with the record id); the rest are inserted (POST).
        existing = self.record_ids(module_api, ext_api, {r[f["external_id"]] for r in rows})
        ok, errors = 0, {}
        for batch in chunks(rows, 100):
            data, sent = [], []
            for row in batch:
                cid = contact_ids.get(row[link])
                if not cid:
                    key = "no contact record for the row's %s" % link
                    errors[key] = errors.get(key, 0) + 1
                    continue
                extra = {"Who_Id": {"id": cid}}
                rule = CALL_STATUS_FIELDS.get(row["Status"], {})
                if rule.get("status") and status_api:
                    extra[status_api] = rule["status"]
                if rule.get("duration"):
                    extra["Call_Duration"] = duration
                rid = existing.get(row[f["external_id"]])
                if rid:
                    extra["id"] = rid
                data.append(self.json_record(row, path, labels, fills, extra))
                sent.append(row)
            for method in ("POST", "PUT"):
                part = [(row, rec) for row, rec in zip(sent, data) if ("id" in rec) == (method == "PUT")]
                if not part:
                    continue
                try:
                    resp = self.c.crm(method, "/%s" % module_api, body={"data": [rec for _, rec in part], "trigger": []})
                    results = resp.get("data") or []
                except zoho.ApiError as e:
                    results = e.body.get("data") if isinstance(e.body, dict) and isinstance(e.body.get("data"), list) else \
                        [{"status": "error", "code": e.code(), "message": str(e)} for _ in part]
                for (row, _), r in zip(part, results):
                    if r.get("status") == "success":
                        ok += 1
                    else:
                        why = (r.get("details") or {}).get("api_name") or ascii_text(r.get("message") or "")
                        key = "%s-%s (%s)" % (r.get("code"), why, row["Status"])
                        errors[key] = errors.get(key, 0) + 1
        zoho.log("  Calls: %d of %d written" % (ok, len(rows)))
        if ok == len(rows):
            self.rec.done(item, "%d rows" % ok)
        else:
            self.rec.leave(item, "%d of %d Calls rows not written" % (len(rows) - ok, len(rows)),
                           "; ".join("%s: %d rows" % (k, v) for k, v in sorted(errors.items())),
                           "to be decided: how a no-show, a cancelled call and a booked slot already past are logged "
                           "in Zoho Calls; then re-run (upsert).", ",".join(sorted({k.split("-")[0] for k in errors})))


def parse_result(raw):
    """A bulk write result zip: one CSV whose STATUS column says added, updated, skipped or unprocessed and whose
    ERRORS column carries '<code>-<column>'."""
    counts, errors = {"added": 0, "updated": 0, "other": 0}, {}
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        text = z.read(z.namelist()[0]).decode("utf-8", errors="replace")
    reader = csv.reader(io.StringIO(text))
    head = [h.strip().upper() for h in next(reader)]
    si = head.index("STATUS")
    ei = head.index("ERRORS") if "ERRORS" in head else None
    for row in reader:
        if len(row) <= si:
            continue
        st = row[si].strip().lower()
        if st in ("added", "updated"):
            counts[st] += 1
        else:
            counts["other"] += 1
            key = (row[ei].strip() if ei is not None and len(row) > ei and row[ei].strip() else st) or "unprocessed"
            errors[key] = errors.get(key, 0) + 1
    return counts, errors


# ---- Desk ----------------------------------------------------------------------------------------------------

def desk_tickets_setup(client):
    """The one department, its default ticket layout, and every ticket field by label: the layout's fields, then
    the org's ticket field list, since a field created by API need not sit on the layout."""
    deps = (client.desk("GET", "/departments", params={"limit": 100}) or {}).get("data") or []
    dep = next((x for x in deps if str(x.get("isDefault")).lower() == "true"), deps[0] if len(deps) == 1 else None)
    lay, by_label = None, {}
    if dep:
        lays = (client.desk("GET", "/layouts", params={"module": "tickets", "departmentId": dep["id"]}) or {}).get("data") or []
        lay = next((x for x in lays if x.get("isDefaultLayout")), lays[0] if lays else None)
    if lay:
        got = client.desk("GET", "/layouts/%s" % lay["id"]) or {}
        for sec in got.get("sections") or []:
            for fl in sec.get("fields") or []:
                by_label.setdefault(fl.get("displayLabel"), fl)
    try:
        for fl in (client.desk("GET", "/fields", params={"module": "tickets"}) or {}).get("data") or []:
            by_label.setdefault(fl.get("displayLabel"), fl)
    except zoho.ApiError as e:
        zoho.log("  ticket field list not read (%s); the layout's fields only" % e.code())
    return deps, dep, lay, by_label


class Desk:
    def __init__(self, client, data, rec):
        self.c, self.d, self.rec = client, data, rec

    def run(self):
        zoho.log("desk")
        path = self.d.desk_file
        f = self.d.idx[path]
        deps, dep, lay, by_label = desk_tickets_setup(self.c)
        if not dep:
            self.rec.leave("desk/department", "one department", "found %d departments and none is the default" % len(deps),
                           "Pick or create the one department in Desk (Setup, Departments).")
            return
        self.dep_id = dep["id"]
        self.rec.done("desk/department", "every ticket goes to %s" % ascii_text(dep.get("name", ""), 60))
        if not lay:
            self.rec.leave("desk/categories", "ticket layout", "no ticket layout listed", "Add the categories by hand.")
            return
        self.layout_id = lay["id"]
        self.categories(path, by_label)
        self.ticket_fields(path, f, by_label)
        self.rec.leave("desk/sla", "SLA of one business day", "no create endpoint: the Desk API lists SLAs but cannot "
                       "create or edit one", "Set it by hand: Setup, SLAs, one business day.")
        self.save_tickets(path, f)

    def category_values(self, fld):
        """The Category field's current values as strings, from the layout or the field's value list; None when
        either answer is not a plain list of strings."""
        vals = fld.get("allowedValues")
        if vals is None:
            try:
                got = self.c.desk("GET", "/layouts/%s/fields/%s/value" % (self.layout_id, fld["id"]))
            except zoho.ApiError:
                return None
            if got is None:  # 204: the layout holds no values for the field yet (first live run, 28 Sep 2026)
                return []
            vals = got
            if isinstance(got, dict):
                vals = got.get("data") if "data" in got else got.get("allowedValues")
        if isinstance(vals, list) and all(isinstance(v, str) for v in vals):
            return vals
        return None

    def categories(self, path, by_label):
        want = op.find_column(self.d.idx, path, "Category")["values"]
        fld = by_label.get("Category")
        if not fld:
            self.rec.leave("desk/categories", "the Category field", "not on the ticket layout", "Add the categories by hand.")
            return
        have = self.category_values(fld)
        if have is None:
            self.rec.leave("desk/categories", "add %s to Category" % ", ".join(want), "the field's current values could "
                           "not be read for sure, and the update replaces the whole list, so nothing was written",
                           "Add them by hand, spelled as the ticket file spells them.")
            return
        missing = [v for v in want if v not in have]
        if missing:
            try:
                self.c.desk("PATCH", "/layouts/%s/fields/%s" % (self.layout_id, fld["id"]), body={"allowedValues": have + missing})
                zoho.log("  Category: added %s" % ", ".join(missing))
            except zoho.ApiError as e:
                self.rec.leave("desk/categories", "add %s to Category" % ", ".join(missing), e,
                               "Add them by hand, spelled as the ticket file spells them.", e.code())
                return
        self.rec.done("desk/categories")

    def ticket_fields(self, path, f, by_label):
        self.fields = {}
        for col in f["columns"]:
            label = col["label"]
            if label in DESK_CONTACT_COLUMNS:
                continue
            have = by_label.get(label)
            if not have:
                body = {"displayLabel": label, "type": DESK_TYPES[col["zoho_type"]]}
                if body["type"] == "Text":
                    body["maxLength"] = 255
                try:
                    have = self.c.desk("POST", "/fields", params={"module": "tickets"}, body=body)
                    zoho.log("  ticket field %s created (%s)" % (label, have.get("apiName")))
                except zoho.ApiError as e:
                    item = "desk/scores-ref" if label == "SCORES Ref" else "import/tickets"
                    self.rec.leave(item, "create the ticket field %s" % label, e, "Create it by hand (Setup, Layouts "
                                   "and Fields, Tickets) as %s." % body["type"], e.code())
                    continue
            self.fields[label] = have
        if "SCORES Ref" in self.fields:
            self.rec.done("desk/scores-ref")

    def contact_id(self, row, people, person_by_contact, cache):
        key = row["Contact Email"] or row["Contact Phone"]
        if key in cache:
            return cache[key]
        pid = person_by_contact.get(row["Contact Phone"]) or person_by_contact.get(row["Contact Email"])
        if not pid:
            return None
        person = people[pid][1]
        field = "email" if row["Contact Email"] else "phone"
        found = (self.c.desk("GET", "/contacts/search", params={field: key, "limit": 10}) or {}).get("data") or []
        match = next((x for x in found if x.get(field) == key), None)
        if not match:
            body = {"lastName": person["Last Name"], "firstName": person["First Name"], "phone": row["Contact Phone"]}
            if row["Contact Email"]:
                body["email"] = row["Contact Email"]
            match = self.c.desk("POST", "/contacts", body=body)
        cache[key] = match["id"]
        return cache[key]

    def save_tickets(self, path, f):
        ext = f["external_id"]
        if ext not in self.fields or "Category" not in self.fields:
            self.rec.leave("import/tickets", "import Desk tickets", "the ticket fields are not all in place",
                           "Import desk/tickets.csv by hand once they are (operator page step 10).")
            return
        ext_api = self.fields[ext]["apiName"]
        people, person_by_contact, cache = self.d.people(), self.d.person_by_contact(), {}
        rows = read_csv(path)
        ok, errors = 0, {}
        for row in rows:
            try:
                found = (self.c.desk("GET", "/tickets/search", params={"customField1": "%s:%s" % (ext_api, row[ext]),
                                                                       "limit": 1}) or {}).get("data") or []
                if found:
                    tid, status = found[0]["id"], found[0].get("status")
                else:
                    cid = self.contact_id(row, people, person_by_contact, cache)
                    if not cid:
                        errors["no person with this phone or email"] = errors.get("no person with this phone or email", 0) + 1
                        continue
                    body = {"subject": row["Subject"], "departmentId": self.dep_id, "contactId": cid, "status": "Open", "cf": {}}
                    for col in f["columns"]:
                        label = col["label"]
                        if label in DESK_CONTACT_COLUMNS or label not in self.fields or not row[label] or label == "Status":
                            continue
                        fld = self.fields[label]
                        value = to_utc_ms(row[label]) if col["zoho_type"] == "date-time" else row[label]
                        if fld.get("isCustomField"):
                            body["cf"][fld["apiName"]] = value
                        else:
                            body[fld["apiName"]] = value
                    t = self.c.desk("POST", "/tickets", body=body)
                    tid, status = t["id"], t.get("status")
                want = DESK_STATUS[row["Status"]]
                if want == "Closed" and status != "Closed":
                    self.c.desk("PATCH", "/tickets/%s" % tid, params={"disableClosureNotification": "true"}, body={"status": "Closed"})
                ok += 1
            except zoho.ApiError as e:
                key = "%s %s" % (e.status, e.code() or ascii_text(e.body, 80))
                errors[key] = errors.get(key, 0) + 1
        zoho.log("  tickets: %d of %d in place" % (ok, len(rows)))
        if ok == len(rows):
            self.rec.done("import/tickets", "%d tickets" % ok)
        else:
            self.rec.leave("import/tickets", "%d of %d tickets not in place" % (len(rows) - ok, len(rows)),
                           "; ".join("%s: %d" % (k, v) for k, v in sorted(errors.items())),
                           "Fix the cause and re-run; tickets already in are found by Ticket External ID and left alone.")


# ---- Campaigns and Bookings ----------------------------------------------------------------------------------

def campaigns(data, rec):
    zoho.log("campaigns")
    for stage in CAMPAIGN_LISTS:
        path = op.campaign_path(stage)
        rows = read_csv(path)
        with_email = sum(1 for r in rows if r["Email"])
        rec.leave(op.campaign_import_id(stage), "the %s list, %d of %d rows with an email" % (stage, with_email, len(rows)),
                  "not called: every Campaigns call that adds contacts can send (listsubscribe mails a confirmation "
                  "to lists with a signup form; addlistandcontacts and addlistsubscribersinbulk document their list "
                  "key as 'to send a subscription mail'), and they take email addresses only",
                  "Import %s by hand into a list named %s (Contacts, Import, from file); map Phone, First Name, Stage, "
                  "Tier and WhatsApp Opt-in; rows without an email are skipped by Campaigns." % (path, stage))


def bookings(client, data, rec):
    zoho.log("bookings")
    name, minutes = data.service_name(), int(data.config["time_model"]["call_minutes"])
    ws = ((client.bookings("GET", "/workspaces") or {}).get("response", {}).get("returnvalue", {}).get("data") or [])
    if not ws:
        rec.leave("bookings/service", "the %s service" % name, "no Bookings workspace", "Open Bookings once to create "
                  "the workspace, then re-run.")
        return
    wid = ws[0]["id"]
    def listed():
        resp = client.bookings("GET", "/services", params={"workspace_id": wid}) or {}
        return [s for s in resp.get("response", {}).get("returnvalue", {}).get("data") or [] if s.get("name") == name]
    answer = None
    if not listed():
        try:
            answer = client.bookings("POST", "/createservice", files={"data": json.dumps(
                {"name": name, "workspace_id": wid, "duration": str(minutes), "service_type": "one_on_one"})})
        except zoho.ApiError as e:
            rec.leave("bookings/service", "create the %s service" % name, e, "Create it by hand: one on one, %d "
                      "minutes." % minutes, e.code())
            return
    svc = listed()
    if not svc:  # Bookings reports a refusal inside a 200 answer
        rec.leave("bookings/service", "create the %s service" % name, answer or "not listed after the create call",
                  "Create it by hand: one on one, %d minutes." % minutes)
        return
    rec.observed["bookings_service"] = {"name": name, "duration": svc[0].get("duration") if svc else None}
    staff = data.adviser_staff()
    rec.leave("bookings/service", "the staff %s" % ", ".join(staff), "not called: the add staff API requires an email "
              "and does not say whether it sends an invitation; the seed has no staff emails",
              "Add them by hand in Bookings with invitations off, then assign them to %s." % name)
    rec.leave("bookings/service", "a handful of appointments", "not called: booking notifications to customer and "
              "staff are a workspace setting the book appointment API cannot switch off",
              "Turn off customer and staff notifications in the workspace, then book them by hand.")


# ---- plan and run --------------------------------------------------------------------------------------------

def plan(data):
    print("Plan (no network): run %s, exports %s" % (RUN, os.path.relpath(EXPORTS, ROOT)))
    for stem, path in data.crm_files:
        f = data.idx[path]
        rows = read_csv(path)
        print("\n%s (%s, %d rows, external ID %s, operator items %s and import/%s)" % (
            f["object"], path, len(rows), f["external_id"], data.field_item(stem, f["object"]), stem))
        for col in f["columns"]:
            want = CRM_TYPES[col["zoho_type"]][0]
            vals = data.values(path, col) if want in ("picklist", "multiselectpicklist") else []
            table = VALUE_MAP.get((path, col["label"]))
            print("  %-34s %-20s %s%s%s" % (col["label"], want, ("%d values" % len(vals)) if vals else "",
                                            "  unique" if col["label"] == f["external_id"] else "",
                                            ("  translated: " + ", ".join("%s -> %s" % kv for kv in table.items())) if table else ""))
    print("\nPicklist items: %s" % ", ".join(item for item, _ in op.PICKLISTS))
    print("Roles: %s" % ", ".join(s["seat"] for s in data.seats))
    f = data.idx[data.desk_file]
    print("Desk: %s, %d rows; categories %s; fields %s" % (data.desk_file, len(read_csv(data.desk_file)),
                                                           ", ".join(op.find_column(data.idx, data.desk_file, "Category")["values"]),
                                                           ", ".join(c["label"] for c in f["columns"] if c["label"] not in DESK_CONTACT_COLUMNS)))
    for stage in CAMPAIGN_LISTS:
        rows = read_csv(op.campaign_path(stage))
        print("Campaigns %s: %d rows, %d with an email (left for the manual import)" % (stage, len(rows), sum(1 for r in rows if r["Email"])))
    print("Bookings: service %r, %s minutes; staff left for hand: %s" % (data.service_name(), data.config["time_model"]["call_minutes"],
                                                                       ", ".join(data.adviser_staff())))


def run(data):
    client = zoho.Client()
    rec = Record(data)
    zoho.log("provision: run %s" % RUN)
    crm = Crm(client, data, rec)
    crm.all_fields()
    rec.save()
    guarded(rec, "roles/%s" % PRINCIPAL_SEAT, "roles", "Create the roles by hand (operator page step 6).", crm.roles)
    crm.views()
    rec.save()
    crm.import_all()
    guarded(rec, "import/tickets", "Desk", "Do the Desk steps by hand (operator page steps 7 and 10).",
            Desk(client, data, rec).run)
    rec.save()
    campaigns(data, rec)
    guarded(rec, "bookings/service", "Bookings", "Create the service by hand.", bookings, client, data, rec)
    rec.save()
    done = sorted(k for k, v in rec.items.items() if v["status"] == "done")
    zoho.log("provision finished: %d items done by script, %d leftovers; next: python3 seed/zoho/verify.py" % (
        len(done), len([x for x in rec.left if x.get("kind") != "note"])))


def main():
    data = Data()
    if "--plan" in sys.argv[1:]:
        plan(data)
    elif sys.argv[1:]:
        raise SystemExit(__doc__)
    else:
        run(data)


if __name__ == "__main__":
    main()
