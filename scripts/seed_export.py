#!/usr/bin/env python3
"""Build the Zoho/Desk/Campaigns/landing exports and fixtures bundle from a seed run,
then run the minimisation scan against seed/export_schema.json.

PLAN_admin_seed_v01.md sections 10 and 12; phase B part 1.

Usage:
    python3 scripts/seed_export.py                 build and scan both runs
    python3 scripts/seed_export.py --run run-500    build and scan one run
    python3 scripts/seed_export.py --scan-only      scan the exports already on disk, write nothing
    python3 scripts/seed_export.py --scan-only --run run-3000 --dir /path/to/copy
                                                     scan an arbitrary directory against run-3000's
                                                     seed (the negative-check hook)

Python 3 standard library only. No network. Deterministic: reads only the seed (data/seed/<run>/)
and seed/config.json; never today's date. Exit status 1 on any scan breach or schema mismatch.
"""

import argparse
import csv
import datetime
import email.utils
import json
import sys
import urllib.parse
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SEED_DIR = REPO_ROOT / "data" / "seed"
SEED_CONFIG_PATH = REPO_ROOT / "seed" / "config.json"
SCHEMA_PATH = REPO_ROOT / "seed" / "export_schema.json"
ADMIN_CRM_PATH = REPO_ROOT / "data" / "admin_crm.json"
STATES_PATH = REPO_ROOT / "data" / "v02" / "states.json"

RUNS = ["run-500", "run-3000"]

SCAN_DIRS = ["zoho", "desk", "campaigns", "landing"]

TABLE_META = [
    {"file": "people.json", "key": "person_id",
     "line": "one record per person: identity, contact, lifecycle dates, mirrors, state"},
    {"file": "households.json", "key": "person_id",
     "line": "the person's household composition (members, dependants, pets)"},
    {"file": "reveal.json", "key": "person_id",
     "line": "the R01 to R09 reveal answers: income, corpus and savings bands and exact values, aspiration, path bands"},
    {"file": "financial_records.json", "key": "person_id",
     "line": "every D-screen spine field captured for a person, with source, precision and lock state"},
    {"file": "loans.json", "key": "person_id",
     "line": "one entry per loan: type, EMI, outstanding, years left, rate"},
    {"file": "covers.json", "key": "person_id",
     "line": "the person's term and health cover position"},
    {"file": "goals.json", "key": "person_id",
     "line": "one entry per goal: name, year, cost, priority"},
    {"file": "rpq.json", "key": "person_id",
     "line": "the risk profiling questionnaire answers and resulting band"},
    {"file": "holdings.json", "key": "person_id",
     "line": "AA- or CAS-sourced holdings: ISIN, name, units, value"},
    {"file": "aa_consents.json", "key": "person_id",
     "line": "account aggregator consent history: status, institutions, expiry"},
    {"file": "cas_uploads.json", "key": "person_id",
     "line": "CAS statement upload and parse timeline"},
    {"file": "plan_versions.json", "key": "person_id",
     "line": "every plan version built for a person, with the summary stub"},
    {"file": "actions.json", "key": "person_id",
     "line": "post-plan actions (SIP starts, stock baskets) and their verification state"},
    {"file": "subscriptions.json", "key": "person_id",
     "line": "one entry per deal: SKU, period, mandate and billing state"},
    {"file": "payments.json", "key": "person_id",
     "line": "one entry per payment attempt against a deal"},
    {"file": "a_la_carte.json", "key": "person_id",
     "line": "single-call purchases outside the plan"},
    {"file": "calls.json", "key": "person_id",
     "line": "one entry per booked call: adviser, topic, status, notes"},
    {"file": "tickets.json", "key": "person_id",
     "line": "one entry per support, adviser-message or grievance ticket"},
    {"file": "ops_queue.json", "key": "person_id",
     "line": "internal ops work items: AA failures, data quality, refunds, DIFM provisioning"},
    {"file": "integration_events.json", "key": "person_id",
     "line": "one entry per vendor call: integration I-number, outcome, latency"},
    {"file": "tasks.json", "key": "person_id",
     "line": "one entry per CRM escalation task (the five crm_task states)"},
    {"file": "nudges_sent.json", "key": "person_id",
     "line": "one entry per nudge send: slot, channel, delivery and click state"},
    {"file": "state_flags.json", "key": "person_id",
     "line": "the resolver's internal per-person timeline; state_id and the state_enter history in events.jsonl are derived from this"},
    {"file": "staff.json", "key": "staff_id",
     "line": "the ten staff records: advisers, ops, support, compliance, Harish"},
    {"file": "config.json", "key": "n/a",
     "line": "the app's own config table for this run: SKU cards, copy slots, feature flags, calls-included matrix, bands, DIFM threshold"},
    {"file": "events.jsonl", "key": "event_id",
     "line": "the full event log: every screen view and product event, not just the CRM subset in zoho/app_events.csv"},
]

LEAD_STAGE_DISPLAY = {"lead": "lead", "verified_lead": "verified lead"}


# ---------------------------------------------------------------- generic helpers

def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def cellstr(v):
    if v is None:
        return ""
    if isinstance(v, bool):
        return "true" if v else "false"
    return str(v)


def joinmulti(values):
    if not values:
        return ""
    return "; ".join(values)


def table_row_count(d):
    if not d:
        return 0
    sample = next(iter(d.values()))
    if isinstance(sample, list):
        return sum(len(v) for v in d.values())
    return len(d)


def run_number(run):
    return run.split("-")[1]


def anchor_date(run):
    """The run's anchor date, read from report.md (never today's date)."""
    report = SEED_DIR / run / "report.md"
    with open(report, encoding="utf-8") as f:
        for line in f:
            if line.startswith("Anchor "):
                token = line.split()[1]
                return datetime.datetime.fromisoformat(token).date()
    raise RuntimeError("no Anchor line found in " + str(report))


def staff_name(staff_table, staff_id):
    if not staff_id:
        return None
    rec = staff_table.get(staff_id)
    return rec["name"] if rec else None


def admin_link(admin_link_base, run, person_id):
    return "{}?run={}&screen=M03&person={}".format(admin_link_base, run_number(run), person_id)


# ---------------------------------------------------------------- seed/config.json derived lookups

def money_field_names(seed_cfg):
    """Spine fields that hold a rupee amount in financial_records.json: kind 'amount', excluding
    ulip_years_completed (its 'amount' kind is a year count against the ulip_years ladder, not rupees)."""
    fields = seed_cfg["fields"]["list"]
    return set(n for n, m in fields.items() if m["kind"] == "amount" and n != "ulip_years_completed")


def age_band_labels(seed_cfg):
    return [b[2] for b in seed_cfg["age_bands"]["bands"]]


def reveal_labels(seed_cfg, kind):
    return seed_cfg["reveal_bands"][kind]["labels"]


def band_label_cache(seed_cfg):
    return {
        "Age Band": age_band_labels(seed_cfg),
        "Income Band": reveal_labels(seed_cfg, "income"),
        "Corpus Band": reveal_labels(seed_cfg, "corpus"),
        "Savings Band": reveal_labels(seed_cfg, "savings"),
    }


def allowed_app_event_names():
    """The CRM events from data/admin_crm.json EVENTS (multi-name rows split on ' / ') plus every
    state_enter_<state id> for a state declared in data/v02/states.json."""
    admin_crm = load_json(ADMIN_CRM_PATH)
    states = load_json(STATES_PATH)["states"]
    allowed = set()
    for row in admin_crm["EVENTS"]:
        for part in row[0].split(" / "):
            allowed.add(part.strip())
    allowed |= state_enter_names(states)
    return allowed


def state_enter_names(states):
    return set("state_enter_" + s["id"] for s in states)


# ---------------------------------------------------------------- row builders

def build_leads_rows(people):
    rows = []
    for pid, p in people.items():
        if p["kind"] != "lead":
            continue
        ld = p["lead_details"]
        rows.append({
            "Lead External ID": pid,
            "First Name": p["first_name"],
            "Last Name": p["last_name"],
            "Phone": p["phone"],
            "Email": p["email"],
            "City": p["city"],
            "Lead Source": p["source"],
            "Lead Stage": LEAD_STAGE_DISPLAY[p["lead_stage"]],
            "WhatsApp Opt-in": p["whatsapp_optin"],
            "DND": p["dnd"],
            "Age Band": p["age_band"],
            "Top Concern": ld["top_concern"],
            "Keyword": ld["keyword"],
            "Community Joined": ld["community_joined"],
            "Created Date": datetime.datetime.fromisoformat(p["created_at"]).date().isoformat(),
            "Is Seed Topup": p["is_topup"],
        })
    rows.sort(key=lambda r: r["Lead External ID"])
    return rows


def build_contacts_rows(run, people, reveal, staff, admin_link_base):
    rows = []
    for pid, p in people.items():
        if p["kind"] != "user":
            continue
        rv = reveal.get(pid, {})
        kd = p["key_dates"]
        m = p["mirrors"]
        rows.append({
            "Contact External ID": pid,
            "First Name": p["first_name"],
            "Last Name": p["last_name"],
            "Phone": p["phone"],
            "Email": p["email"],
            "City": p["city"],
            "Age Band": p["age_band"],
            "Source": p["source"],
            "WhatsApp Opt-in": p["whatsapp_optin"],
            "DND": p["dnd"],
            "Journey Stage": p["journey_stage"],
            "Tier": p["tier"],
            "SKU": p["sku"],
            "Subscription Status": p["subscription_status"],
            "Adviser Owner": staff_name(staff, p["adviser_id"]),
            "Income Band": rv.get("income_band"),
            "Corpus Band": rv.get("corpus_band"),
            "Savings Band": rv.get("savings_rate_band"),
            "Aspiration": rv.get("aspiration"),
            "Signed Up": kd["signed_up"],
            "Reveal Seen": kd["reveal_seen"],
            "Paid": kd["paid"],
            "Data Complete": kd["data_complete"],
            "Plan Built": kd["plan_built"],
            "Plan Read": kd["plan_read"],
            "Last Call": kd["last_call"],
            "Next Review": kd["next_review"],
            "Renewal Due": kd["renewal_due"],
            "Last Activity": kd["last_activity"],
            "Onboarding %": m["onboarding_pct"],
            "KYC Status": m["kyc_status"],
            "AA Status": m["aa_status"],
            "FP Status": m["fp_status"],
            "IP Status": m["ip_status"],
            "Actions Done": m["actions_done"],
            "Actions Total": m["actions_total"],
            "Consent Valid Till": p["consent_valid_till"],
            "Source Completeness": p["source_completeness"],
            "Sharpen Count": p["sharpen_count"],
            "Last Manual Update": p["last_manual_update"],
            "DIFM Prospect Flag": p["difm_prospect_flag"],
            "Adviser Continuity": p["adviser_continuity"],
            "Last Adviser": staff_name(staff, p["last_adviser"]),
            "Profile Fulfilment %": p["profile_fulfilment_pct"],
            "Admin Link": admin_link(admin_link_base, run, pid),
            "Is Seed Topup": p["is_topup"],
        })
    rows.sort(key=lambda r: r["Contact External ID"])
    return rows


def build_deals_rows(people, subscriptions):
    rows = []
    for pid, deals in subscriptions.items():
        p = people[pid]
        for d in deals:
            rows.append({
                "Deal External ID": d["deal_id"],
                "Contact External ID": pid,
                "Deal Name": "{} {}, {} {}".format(d["sku"].upper(), d["period"], p["first_name"], p["last_name"]),
                "SKU": d["sku"],
                "Period": d["period"],
                "Amount": d["amount"],
                "GST Type": d["gst_type"],
                "Payment Method": d["payment_method"],
                "Coupon": d["coupon"],
                "Razorpay Customer Id": d["razorpay_customer_id"],
                "Razorpay Subscription or Txn Id": d["razorpay_subscription_or_txn_id"],
                "Mandate Status": d["mandate_status"],
                "Start": d["start"],
                "Next Billing": d["next_billing"],
                "Status": d["status"],
                "Grace Until": d["grace_until"],
                "Retry Count": d["retry_count"],
                "Calls Included Per Period": d["calls_included_per_period"],
                "Calls Used": d["calls_used"],
                "Cancel Reason": d["cancel_reason"],
                "Refund Requested": d["refund_requested"],
                "Refund Status": d["refund_status"],
            })
    rows.sort(key=lambda r: r["Deal External ID"])
    return rows


def build_a_la_carte_rows(a_la_carte):
    rows = []
    for pid, purchases in a_la_carte.items():
        for x in purchases:
            rows.append({
                "Purchase External ID": x["purchase_id"],
                "Contact External ID": pid,
                "Date": x["date"],
                "Amount": x["amount"],
                "Receipt": x["receipt"],
                "Call Id": x["call_id"],
            })
    rows.sort(key=lambda r: r["Purchase External ID"])
    return rows


def build_calls_rows(calls, staff):
    rows = []
    for pid, items in calls.items():
        for c in items:
            rows.append({
                "Call External ID": c["call_id"],
                "Contact External ID": pid,
                "Adviser": staff_name(staff, c["adviser_id"]),
                "Booked At": c["booked_at"],
                "Slot": c["slot"],
                "Topic": c["topic"],
                "Status": c["status"],
                "Notes": c["notes"],
                "Input Changes": joinmulti(c.get("input_changes")),
            })
    rows.sort(key=lambda r: r["Call External ID"])
    return rows


def build_tasks_rows(tasks, staff):
    rows = []
    for pid, items in tasks.items():
        for t in items:
            f = t["fields"]
            rows.append({
                "Task External ID": t["task_id"],
                "Contact External ID": pid,
                "Subject": t["subject"],
                "State ID": t["state_id"],
                "Tier": f.get("tier"),
                "Days Unsigned": f.get("days_unsigned"),
                "Missing Fields": joinmulti(f.get("missing_fields")),
                "Last Screen": f.get("last_screen"),
                "Minutes Left": f.get("minutes_left"),
                "Call Topic": f.get("call_topic"),
                "No-show Count": f.get("no_show_count"),
                "Payment Reference": f.get("payment_reference"),
                "Cancel Reason": f.get("cancel_reason"),
                "Period Unexpired": f.get("period_unexpired"),
                "Records Retained": joinmulti(f.get("records_retained")),
                "Requested At": f.get("requested_at"),
                "Assignee": staff_name(staff, t["assignee"]),
                "Due": t["due"],
                "Status": t["status"],
            })
    rows.sort(key=lambda r: r["Task External ID"])
    return rows


def build_app_events_and_ticket_events(seed_dir, allowed_events, ticket_person_ids):
    """One pass over events.jsonl: collect the app_events.csv rows (allowed CRM + state_enter events)
    and, for people who raised a ticket, their full event stream (needed to compute the ticket
    Description's stage/last-screen-as-of-created_at)."""
    app_rows = []
    events_by_person = {pid: [] for pid in ticket_person_ids}
    with open(seed_dir / "events.jsonl", encoding="utf-8") as f:
        for line in f:
            e = json.loads(line)
            pid = e["person_id"]
            if pid in events_by_person:
                events_by_person[pid].append(e)
            if e["event"] in allowed_events:
                app_rows.append({
                    "Event External ID": e["event_id"],
                    "Contact External ID": pid,
                    "Event": e["event"],
                    "Screen": e["screen_id"],
                    "At": e["at"],
                    "Props": json.dumps(e["props"], sort_keys=True, separators=(",", ":")),
                })
    app_rows.sort(key=lambda r: r["Event External ID"])
    return app_rows, events_by_person


def ticket_context(person, events, integration_events, created_at_iso, state_enter_set):
    """Stage, tier, last screen and last integration failure as of the ticket's created_at
    (PLAN_admin_seed_v01.md section 12, the desk/tickets.csv Description rule)."""
    created_at = datetime.datetime.fromisoformat(created_at_iso)

    state = None
    best_t = None
    for e in events:
        if e["event"] in state_enter_set:
            t = datetime.datetime.fromisoformat(e["at"])
            if t <= created_at and (best_t is None or t > best_t):
                best_t = t
                state = e["props"]["state"]
    if state is None:
        state = person["state_id"]

    screen = None
    best_t2 = None
    for e in events:
        if e["screen_id"] is not None and e["event"] == e["screen_id"] + "_view":
            t = datetime.datetime.fromisoformat(e["at"])
            if t <= created_at and (best_t2 is None or t > best_t2):
                best_t2 = t
                screen = e["screen_id"]

    failure = "none"
    best_t3 = None
    for row in integration_events:
        if row["outcome"] != "ok":
            t = datetime.datetime.fromisoformat(row["at"])
            if t <= created_at and (best_t3 is None or t > best_t3):
                best_t3 = t
                failure = "{} {} {}".format(row["integration"], row["call"], row["outcome"])

    tier = person.get("tier") or "none"
    screen_text = screen if screen is not None else "none"
    return state, tier, screen_text, failure


def build_tickets_rows(tickets, people, events_by_person, integration_events, state_enter_set):
    rows = []
    for pid, items in tickets.items():
        p = people[pid]
        person_events = events_by_person.get(pid, [])
        person_integration = integration_events.get(pid, [])
        for t in items:
            state, tier, screen, failure = ticket_context(
                p, person_events, person_integration, t["created_at"], state_enter_set)
            desc = "{} Stage {}. Tier {}. Last screen {}. Last integration failure: {}.".format(
                t["description"], state, tier, screen, failure)
            rows.append({
                "Ticket External ID": t["ticket_id"],
                "Contact Email": p["email"],
                "Contact Phone": p["phone"],
                "Category": t["category"],
                "Subject": t["subject"],
                "Description": desc,
                "Created At": t["created_at"],
                "SLA Due": t["sla_due"],
                "Status": t["status"],
                "Resolved At": t["resolved_at"],
                "SCORES Ref": t["scores_ref"],
            })
    rows.sort(key=lambda r: r["Ticket External ID"])
    return rows


def build_campaigns_files(people):
    by_stage = {}
    for pid, p in people.items():
        stage = p["journey_stage"]
        by_stage.setdefault(stage, []).append({
            "Email": p["email"],
            "Phone": p["phone"],
            "First Name": p["first_name"],
            "Stage": stage,
            "Tier": p["tier"],
            "WhatsApp Opt-in": p["whatsapp_optin"],
        })
    for rows in by_stage.values():
        rows.sort(key=lambda r: r["Email"] or "")
    return by_stage


def build_landing_rows(people):
    rows = []
    for pid, p in people.items():
        ld = p["lead_details"]
        if ld.get("landing_at"):
            rows.append({
                "Timestamp": ld["landing_at"],
                "Email": p["email"],
                "Top Money Concern": ld["top_concern"],
                "Keyword": ld["keyword"],
                "Source": p["source"],
                "Community Joined": ld["community_joined"],
                "Resource Sent": ld["resource_sent"],
            })
    rows.sort(key=lambda r: r["Email"] or "")
    return rows


def screen_section_map():
    """screen_id -> section letter, from data/screens_v02.json: for each screen, its declared "sec"
    validated against the letters in the "sections" table (PLAN_admin_seed_v01.md section 12, the
    Mixpanel row: "the first element of ... 'sections' whose letter matches the screen's 'sec'")."""
    screens = load_json(REPO_ROOT / "data" / "screens_v02.json")
    letters = set(s[0] for s in screens["sections"])
    m = {}
    for s in screens["screens"]:
        sec = s.get("sec")
        if sec in letters:
            m[s["id"]] = sec
    return m


def build_mixpanel_events(seed_dir, people, section_map, state_enter_set):
    """One line per events.jsonl row, in file order, event name unchanged. events.jsonl is grouped by
    person and chronological within each person (checked), so a single pass with a per-person state
    tracker gives the correct 'latest state_enter at or before this event' for every row."""
    person_state = {}
    lines = []
    with open(seed_dir / "events.jsonl", encoding="utf-8") as f:
        for line in f:
            e = json.loads(line)
            pid = e["person_id"]
            if e["event"] in state_enter_set:
                person_state[pid] = e["props"]["state"]
            p = people[pid]
            screen_id = e["screen_id"]
            props = {
                "distinct_id": pid,
                "time": int(datetime.datetime.fromisoformat(e["at"]).timestamp()),
                "$insert_id": e["event_id"],
                "screen_id": screen_id,
                "section": section_map.get(screen_id) if screen_id else None,
                "tier": p["tier"],
                "state": person_state.get(pid),
                "source_path": p["source_path"],
                "is_topup": p["is_topup"],
            }
            obj = {"event": e["event"], "properties": props}
            lines.append(json.dumps(obj, sort_keys=True, separators=(",", ":")))
    return lines


def build_mixpanel_profiles(people):
    """One line per person, sorted by person_id. 'signed_up' uses otp_verified_at (the precise moment;
    its date always equals key_dates.signed_up, checked) rather than fabricating a midnight timestamp
    from the date-only key_dates field."""
    lines = []
    for pid in sorted(people.keys()):
        p = people[pid]
        otp = p.get("otp_verified_at")
        signed_up = int(datetime.datetime.fromisoformat(otp).timestamp()) if otp else None
        obj = {
            "$distinct_id": pid,
            "$set": {
                "tier": p["tier"],
                "state": p["state_id"],
                "source": p["source"],
                "source_path": p["source_path"],
                "city_tier": p["city_tier"],
                "age_band": p["age_band"],
                "is_topup": p["is_topup"],
                "signed_up": signed_up,
            },
        }
        lines.append(json.dumps(obj, sort_keys=True, separators=(",", ":")))
    return lines


# ---------------------------------------------------------------- CSV / JSONL writers

def write_csv(path, header, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        for r in rows:
            w.writerow([cellstr(r[h]) for h in header])


def write_jsonl(path, lines):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for line in lines:
            f.write(line)
            f.write("\n")


# ---------------------------------------------------------------- run export build

def write_run_exports(run, schema):
    seed_dir = SEED_DIR / run
    people = load_json(seed_dir / "people.json")
    staff = load_json(seed_dir / "staff.json")
    reveal = load_json(seed_dir / "reveal.json")
    subscriptions = load_json(seed_dir / "subscriptions.json")
    a_la_carte = load_json(seed_dir / "a_la_carte.json")
    calls = load_json(seed_dir / "calls.json")
    tasks = load_json(seed_dir / "tasks.json")
    tickets = load_json(seed_dir / "tickets.json")
    integration_events = load_json(seed_dir / "integration_events.json")

    admin_link_base = schema["admin_link_base"]
    exports_dir = seed_dir / "exports"
    file_schema_by_path = {f["path"]: f for f in schema["files"]}

    def header_for(path):
        return [c["label"] for c in file_schema_by_path[path]["columns"]]

    summaries = []

    def emit(relpath, header, rows):
        write_csv(exports_dir / relpath, header, rows)
        summaries.append((relpath, len(rows), len(header)))

    emit("zoho/leads.csv", header_for("zoho/leads.csv"), build_leads_rows(people))
    emit("zoho/contacts.csv", header_for("zoho/contacts.csv"),
         build_contacts_rows(run, people, reveal, staff, admin_link_base))
    emit("zoho/deals.csv", header_for("zoho/deals.csv"), build_deals_rows(people, subscriptions))
    emit("zoho/a_la_carte.csv", header_for("zoho/a_la_carte.csv"), build_a_la_carte_rows(a_la_carte))
    emit("zoho/calls.csv", header_for("zoho/calls.csv"), build_calls_rows(calls, staff))
    emit("zoho/tasks.csv", header_for("zoho/tasks.csv"), build_tasks_rows(tasks, staff))

    states = load_json(STATES_PATH)["states"]
    allowed_events = allowed_app_event_names()
    state_enter_set = state_enter_names(states)
    ticket_person_ids = set(tickets.keys())
    app_rows, events_by_person = build_app_events_and_ticket_events(seed_dir, allowed_events, ticket_person_ids)
    emit("zoho/app_events.csv", header_for("zoho/app_events.csv"), app_rows)

    ticket_rows = build_tickets_rows(tickets, people, events_by_person, integration_events, state_enter_set)
    emit("desk/tickets.csv", header_for("desk/tickets.csv"), ticket_rows)

    campaign_header = [c["label"] for c in file_schema_by_path["campaigns/<stage>.csv"]["columns"]]
    by_stage = build_campaigns_files(people)
    for stage in sorted(by_stage.keys()):
        emit("campaigns/{}.csv".format(stage), campaign_header, by_stage[stage])

    emit("landing/landing_sheet.csv", header_for("landing/landing_sheet.csv"), build_landing_rows(people))

    section_map = screen_section_map()
    mixpanel_summaries = []

    def emit_jsonl(relpath, lines):
        write_jsonl(exports_dir / relpath, lines)
        mixpanel_summaries.append((relpath, len(lines)))

    emit_jsonl("mixpanel/events.jsonl", build_mixpanel_events(seed_dir, people, section_map, state_enter_set))
    emit_jsonl("mixpanel/profiles.jsonl", build_mixpanel_profiles(people))

    return summaries, mixpanel_summaries


# ---------------------------------------------------------------- fixtures (README + private zip)

def write_fixtures_readme(run, zip_name):
    seed_dir = SEED_DIR / run
    lines = []
    lines.append("# Fixtures bundle: " + run)
    lines.append("")
    lines.append("For Spinach's dev and staging databases. The canonical bundle for this run ships as a")
    lines.append("private zip in this folder: " + zip_name + ".")
    lines.append("It is not committed to the repo (see .gitignore) and never published on the board;")
    lines.append("Spinach receives it by hand (Vatsal, 23 Sep 2026). It holds data/seed/" + run + "/*.json,")
    lines.append("events.jsonl and report.md, plus this README, all under a folder named like the zip")
    lines.append("(the zip name without .zip).")
    lines.append("")
    lines.append("## Tables")
    lines.append("")
    lines.append("| file | key | holds | rows (" + run + ") | joins |")
    lines.append("|---|---|---|---|---|")
    for meta in TABLE_META:
        fname = meta["file"]
        if fname == "config.json":
            count = "n/a (a single config object, not person-keyed)"
        elif fname == "events.jsonl":
            with open(seed_dir / fname, encoding="utf-8") as f:
                count = str(sum(1 for _ in f))
        else:
            d = load_json(seed_dir / fname)
            count = str(table_row_count(d))
        if fname in ("staff.json", "config.json"):
            joins = "n/a"
        elif fname == "subscriptions.json":
            joins = "person_id; deal_id joins payments.json"
        elif fname == "payments.json":
            joins = "person_id; deal_id joins subscriptions.json"
        elif fname == "calls.json":
            joins = "person_id; call_id joins a_la_carte.json"
        elif fname == "a_la_carte.json":
            joins = "person_id; call_id joins calls.json"
        else:
            joins = "person_id"
        lines.append("| {} | {} | {} | {} | {} |".format(fname, meta["key"], meta["line"], count, joins))
    lines.append("")
    lines.append("## Joins not carried by a column name above")
    lines.append("")
    lines.append("- staff_id: people.json (adviser_id, last_adviser), calls.json (adviser_id), tasks.json")
    lines.append("  (assignee) and ops_queue.json (owner) all reference a key in staff.json.")
    lines.append("")
    lines.append("## Personal data")
    lines.append("")
    lines.append("- people.json carries first_name, last_name, phone, email, legal_name, pan and dob.")
    lines.append("- households.json carries each member's name and age.")
    lines.append("- reveal.json carries first_name.")
    lines.append("- PAN is synthetic in format only. It appears in the canonical seed and in this")
    lines.append("  fixtures bundle; it never appears in any Zoho export (the minimisation scan enforces")
    lines.append("  this).")
    lines.append("")
    text = "\n".join(lines) + "\n"
    path = SEED_DIR / run / "exports" / "fixtures" / "README.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def build_fixtures_zip(run):
    """A private, deterministic zip of the run's canonical seed (Vatsal, 23 Sep 2026): entries
    sorted by name, a fixed anchor-date timestamp, ZIP_DEFLATED at level 9. Not committed
    (.gitignore: data/seed/*/exports/fixtures/*.zip)."""
    seed_dir = SEED_DIR / run
    fixtures_dir = seed_dir / "exports" / "fixtures"
    anch = anchor_date(run)
    zip_name = "yeslyf_seed_{}_{}.zip".format(anch.isoformat(), run)
    zip_path = fixtures_dir / zip_name
    folder = zip_name[:-4]

    entries = []
    for p in seed_dir.glob("*.json"):
        entries.append((folder + "/" + p.name, p))
    entries.append((folder + "/events.jsonl", seed_dir / "events.jsonl"))
    entries.append((folder + "/report.md", seed_dir / "report.md"))
    entries.append((folder + "/fixtures/README.md", fixtures_dir / "README.md"))
    entries.sort(key=lambda e: e[0])

    dt = (anch.year, anch.month, anch.day, 0, 0, 0)

    fixtures_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w") as zf:
        for arcname, src in entries:
            data = src.read_bytes()
            zi = zipfile.ZipInfo(arcname, date_time=dt)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o644 << 16
            zf.writestr(zi, data, compresslevel=9)

    return zip_path, zip_name


def write_exports_readme(run, summaries, mixpanel_summaries, scan_line, zip_name):
    lines = []
    lines.append("# Exports: " + run)
    lines.append("")
    lines.append("Generated by scripts/seed_export.py from data/seed/" + run + "/ and seed/export_schema.json.")
    lines.append("")
    lines.append("| file | rows | columns |")
    lines.append("|---|---|---|")
    for relpath, nrows, ncols in summaries:
        lines.append("| {} | {} | {} |".format(relpath, nrows, ncols))
    lines.append("")
    lines.append("## Mixpanel (JSONL, phase E done early: plan section 12)")
    lines.append("")
    lines.append("Third party: no names, phones, emails or PAN. One JSON object per line, compact,")
    lines.append("sorted keys, ASCII, \\n endings.")
    lines.append("")
    lines.append("| file | lines |")
    lines.append("|---|---|")
    for relpath, nlines in mixpanel_summaries:
        lines.append("| {} | {} |".format(relpath, nlines))
    lines.append("")
    lines.append("## Scan")
    lines.append("")
    lines.append(scan_line)
    lines.append("")
    lines.append("## Rules")
    lines.append("")
    lines.append("- Bands and dates only in the Zoho files: no exact rupee value, only a band label or")
    lines.append("  the placeholder 'Rs ___'.")
    lines.append("- No PAN, no holdings (ISIN, name or units) in any export.")
    lines.append("- Every email is at example.com; no other domain appears.")
    lines.append("")
    lines.append("## Fixtures")
    lines.append("")
    lines.append("The canonical bundle for this run ships as a private zip, fixtures/" + zip_name + ",")
    lines.append("not committed and never published on the board (Vatsal, 23 Sep 2026); see")
    lines.append("fixtures/README.md.")
    lines.append("")
    text = "\n".join(lines) + "\n"
    path = SEED_DIR / run / "exports" / "README.md"
    path.write_text(text, encoding="utf-8")
    return path


# ---------------------------------------------------------------- minimisation scan

def rupee_decimal_str(v):
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v)


def collect_sensitive(run, seed_cfg):
    seed_dir = SEED_DIR / run
    money_fields = money_field_names(seed_cfg)

    rupee = set()
    counts = {}

    def add_rupee(v, table):
        if isinstance(v, (int, float)) and v > 0:
            rupee.add(v)
            counts[table] = counts.get(table, 0) + 1

    fr = load_json(seed_dir / "financial_records.json")
    for pid, rows in fr.items():
        for r in rows:
            if r["field"] in money_fields:
                add_rupee(r["value"], "financial_records")

    reveal = load_json(seed_dir / "reveal.json")
    for pid, r in reveal.items():
        add_rupee(r.get("income_exact"), "reveal")
        add_rupee(r.get("corpus_exact"), "reveal")

    loans = load_json(seed_dir / "loans.json")
    for pid, rows in loans.items():
        for r in rows:
            add_rupee(r.get("emi"), "loans")
            add_rupee(r.get("outstanding"), "loans")

    covers = load_json(seed_dir / "covers.json")
    for pid, r in covers.items():
        for k in ("term_sum_assured", "term_premium", "health_sum_insured", "health_premium", "other_policies"):
            add_rupee(r.get(k), "covers")

    goals = load_json(seed_dir / "goals.json")
    for pid, rows in goals.items():
        for r in rows:
            add_rupee(r.get("cost_today"), "goals")

    isin = set()
    holding_name = set()
    units = set()
    holdings = load_json(seed_dir / "holdings.json")
    for pid, rows in holdings.items():
        for r in rows:
            add_rupee(r.get("value"), "holdings")
            if r.get("isin"):
                isin.add(r["isin"])
            if r.get("name"):
                holding_name.add(r["name"])
            if r.get("units") is not None:
                units.add(r["units"])

    actions = load_json(seed_dir / "actions.json")
    for pid, rows in actions.items():
        for r in rows:
            add_rupee(r.get("amount"), "actions")

    plan_versions = load_json(seed_dir / "plan_versions.json")
    for pid, rows in plan_versions.items():
        for r in rows:
            ss = r.get("summary_stub", {})
            add_rupee(ss.get("monthly_surplus"), "plan_versions")
            add_rupee(ss.get("sip_total"), "plan_versions")
            add_rupee(ss.get("cover_gap"), "plan_versions")

    people = load_json(seed_dir / "people.json")
    pan = set(v["pan"] for v in people.values() if v.get("pan"))
    phone = set(v["phone"] for v in people.values() if v.get("phone"))
    email_other = set()
    for v in people.values():
        if v.get("email"):
            local, sep, domain = v["email"].rpartition("@")
            if domain != "example.com":
                email_other.add(v["email"])

    rupee_str = set(rupee_decimal_str(v) for v in rupee)

    return {
        "rupee": rupee,
        "rupee_str": rupee_str,
        "units": units,
        "pan": pan,
        "isin": isin,
        "holding_name": holding_name,
        "email_other": email_other,
        "phone": phone,
        "money_field_counts": counts,
        "money_field_names": sorted(money_fields),
    }


def try_parse_number(s):
    try:
        return int(s)
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        return None


def walk_json_leaves(value):
    if isinstance(value, dict):
        for v in value.values():
            yield from walk_json_leaves(v)
    elif isinstance(value, list):
        for v in value:
            yield from walk_json_leaves(v)
    else:
        yield value


def leak_check_cell(raw, col_type, sensitive):
    kinds = []
    if raw == "":
        return kinds

    num = try_parse_number(raw)
    if num is not None:
        if num in sensitive["rupee"]:
            kinds.append("rupee value equal (" + raw + ")")
        if num in sensitive["units"]:
            kinds.append("holding units equal (" + raw + ")")
    if raw in sensitive["pan"]:
        kinds.append("PAN equal")
    if raw in sensitive["isin"]:
        kinds.append("ISIN equal")
    if raw in sensitive["holding_name"]:
        kinds.append("holding name equal")
    if raw in sensitive["email_other"]:
        kinds.append("non-example.com email equal")

    if col_type == "json":
        # clause (a) is leaf-by-leaf for JSON, not just the serialised cell as a whole
        try:
            parsed = json.loads(raw)
        except ValueError:
            parsed = None
        if parsed is not None:
            for leaf in walk_json_leaves(parsed):
                if isinstance(leaf, bool):
                    continue
                if isinstance(leaf, (int, float)):
                    if leaf in sensitive["rupee"]:
                        kinds.append("rupee value equal in a JSON leaf (" + str(leaf) + ")")
                    if leaf in sensitive["units"]:
                        kinds.append("holding units equal in a JSON leaf (" + str(leaf) + ")")
                elif isinstance(leaf, str):
                    if leaf in sensitive["pan"]:
                        kinds.append("PAN equal in a JSON leaf")
                    if leaf in sensitive["isin"]:
                        kinds.append("ISIN equal in a JSON leaf")
                    if leaf in sensitive["holding_name"]:
                        kinds.append("holding name equal in a JSON leaf")
                    if leaf in sensitive["email_other"]:
                        kinds.append("non-example.com email equal in a JSON leaf")

    if col_type in ("text", "json"):
        for p in sensitive["pan"]:
            if p in raw:
                kinds.append("PAN substring (" + p + ")")
        for i in sensitive["isin"]:
            if i in raw:
                kinds.append("ISIN substring (" + i + ")")
        for n in sensitive["holding_name"]:
            if n in raw:
                kinds.append("holding name substring (" + n + ")")
        for e in sensitive["email_other"]:
            if e in raw:
                kinds.append("non-example.com email substring (" + e + ")")

    if col_type == "text" and any(c.isdigit() for c in raw):
        for r in sensitive["rupee_str"]:
            if r in raw:
                kinds.append("rupee value substring (" + r + ")")

    return kinds


def validate_type(value, col, band_cache, seen_ids, is_external_id):
    t = col["type"]
    if t == "id":
        if value == "":
            return "blank id"
        if is_external_id:
            if value in seen_ids:
                return "duplicate id"
            seen_ids.add(value)
        return None
    if value == "":
        return None
    if t == "text":
        return None
    if t == "picklist":
        if value not in col["values"]:
            return "not in picklist: " + value
        return None
    if t == "multi":
        for part in value.split("; "):
            if part not in col["values"]:
                return "multi part not in values: " + part
        return None
    if t == "email":
        name, addr = email.utils.parseaddr(value)
        if not addr or "@" not in addr:
            return "not a parseable email"
        local, sep, domain = addr.rpartition("@")
        if domain != "example.com":
            return "domain not example.com"
        return None
    if t == "phone":
        if len(value) != 10 or not value.isdigit():
            return "not a 10-digit phone"
        return None
    if t == "date":
        try:
            datetime.date.fromisoformat(value)
        except ValueError:
            return "not a valid date"
        return None
    if t == "datetime":
        try:
            datetime.datetime.fromisoformat(value)
        except ValueError:
            return "not a valid datetime"
        return None
    if t in ("int", "pct"):
        try:
            n = int(value)
        except ValueError:
            return "not an int"
        if not (col["min"] <= n <= col["max"]):
            return "out of range [{}, {}]".format(col["min"], col["max"])
        return None
    if t == "bool":
        if value not in ("true", "false"):
            return "not true/false"
        return None
    if t == "band":
        if value not in band_cache[col["label"]]:
            return "not in band labels"
        return None
    if t == "money":
        if value != "Rs ___":
            return "not the Rs ___ placeholder"
        return None
    if t == "url":
        parts = urllib.parse.urlsplit(value)
        if parts.scheme != "https" or parts.netloc != "spiffler33.github.io":
            return "bad url scheme or host"
        return None
    if t == "json":
        try:
            json.loads(value)
        except ValueError:
            return "not valid json"
        return None
    return "unknown column type: " + t


def find_export_csvs(exports_root):
    found = set()
    for d in SCAN_DIRS:
        dpath = exports_root / d
        if dpath.is_dir():
            for p in sorted(dpath.rglob("*.csv")):
                found.add(str(p.relative_to(exports_root)).replace("\\", "/"))
    return found


def find_mixpanel_files(exports_root):
    found = []
    d = exports_root / "mixpanel"
    if d.is_dir():
        for p in sorted(d.glob("*.jsonl")):
            found.append(str(p.relative_to(exports_root)).replace("\\", "/"))
    return found


MIXPANEL_LEAK_KEYS = ("pan", "isin", "holding_name", "email_other", "phone")
MIXPANEL_LEAK_LABELS = {
    "pan": "PAN", "isin": "ISIN", "holding_name": "holding name",
    "email_other": "non-example.com email", "phone": "phone number",
}


def scan_mixpanel_file(relpath, path, sensitive):
    """Exact-membership only (no substring check): mixpanel properties are structured fields
    (ids, codes, timestamps, booleans), never prose, so there is nothing to substring-scan.
    Checked over every JSON value (every leaf), not just each line as a whole."""
    problems = []
    line_count = 0
    value_count = 0
    raw = path.read_bytes()
    if not raw.isascii():
        problems.append(relpath + ": file is not ASCII")
    with open(path, encoding="utf-8") as f:
        for i, raw_line in enumerate(f, start=1):
            line = raw_line.rstrip("\n")
            if not line:
                continue
            line_count += 1
            try:
                obj = json.loads(line)
            except ValueError:
                problems.append("{} line {}: not valid json".format(relpath, i))
                continue
            for leaf in walk_json_leaves(obj):
                value_count += 1
                if isinstance(leaf, bool):
                    continue
                if isinstance(leaf, (int, float)):
                    if leaf in sensitive["rupee"]:
                        problems.append("{} line {}: leak, rupee value equal ({})".format(relpath, i, leaf))
                elif isinstance(leaf, str):
                    for key in MIXPANEL_LEAK_KEYS:
                        if leaf in sensitive[key]:
                            problems.append("{} line {}: leak, {} equal".format(relpath, i, MIXPANEL_LEAK_LABELS[key]))
    return problems, line_count, value_count


def run_scan(run, exports_root, seed_cfg, schema):
    sensitive = collect_sensitive(run, seed_cfg)
    band_cache = band_label_cache(seed_cfg)
    problems = []
    cell_checks = 0

    files_schema = schema["files"]
    literal = {f["path"]: f for f in files_schema if "<" not in f["path"]}
    template = next(f for f in files_schema if "<" in f["path"])

    found = find_export_csvs(exports_root)
    campaign_found = set(p for p in found if p.startswith("campaigns/"))
    other_found = found - campaign_found

    for p in literal:
        if p not in found:
            problems.append("schema: declared file missing on disk: " + p)
    for p in other_found:
        if p not in literal:
            problems.append("schema: file on disk not declared: " + p)
    if not campaign_found:
        problems.append("schema: no campaigns/*.csv found on disk for the campaigns/<stage>.csv template")

    def check_file(relpath, file_schema):
        nonlocal cell_checks
        path = exports_root / relpath
        raw = path.read_bytes()
        if not raw.isascii():
            problems.append(relpath + ": file is not ASCII")
        with open(path, "r", newline="", encoding="utf-8") as f:
            rows = list(csv.reader(f))
        if not rows:
            problems.append(relpath + ": empty file, no header")
            return
        header = rows[0]
        expected = [c["label"] for c in file_schema["columns"]]
        if header != expected:
            problems.append(relpath + ": header does not match the declared columns")
            return
        seen_ids = set()
        external_id_label = file_schema.get("external_id")
        for i, row in enumerate(rows[1:], start=2):
            if len(row) != len(header):
                problems.append("{} row {}: {} cells, expected {}".format(relpath, i, len(row), len(header)))
                continue
            for col, value in zip(file_schema["columns"], row):
                cell_checks += 1
                is_external_id = col["label"] == external_id_label
                err = validate_type(value, col, band_cache, seen_ids, is_external_id)
                if err:
                    problems.append("{} row {} col {}: {}".format(relpath, i, col["label"], err))
                for kind in leak_check_cell(value, col["type"], sensitive):
                    problems.append("{} row {} col {}: leak, {}".format(relpath, i, col["label"], kind))

    for p in sorted(other_found):
        check_file(p, literal[p])
    for p in sorted(campaign_found):
        check_file(p, template)

    mp_lines = 0
    mp_values = 0
    for relpath in find_mixpanel_files(exports_root):
        mp_problems, n_lines, n_values = scan_mixpanel_file(relpath, exports_root / relpath, sensitive)
        problems.extend(mp_problems)
        mp_lines += n_lines
        mp_values += n_values

    return problems, cell_checks, mp_lines, mp_values, sensitive


# ---------------------------------------------------------------- CLI

def do_build(run, schema):
    summaries, mixpanel_summaries = write_run_exports(run, schema)
    for relpath, nrows, ncols in summaries:
        print("{} {}: {} rows, {} columns".format(run, relpath, nrows, ncols))
    for relpath, nlines in mixpanel_summaries:
        print("{} {}: {} lines".format(run, relpath, nlines))

    # the zip embeds fixtures/README.md, and the README names the zip, so derive the name first
    # (it only needs the anchor date, not the zip itself), write the README, then build the zip.
    anch = anchor_date(run)
    zip_name = "yeslyf_seed_{}_{}.zip".format(anch.isoformat(), run)
    write_fixtures_readme(run, zip_name)
    zip_path, zip_name = build_fixtures_zip(run)
    print("{} fixtures/{}: {} bytes".format(run, zip_name, zip_path.stat().st_size))

    seed_cfg = load_json(SEED_CONFIG_PATH)
    exports_root = SEED_DIR / run / "exports"
    problems, cell_checks, mp_lines, mp_values, _sensitive = run_scan(run, exports_root, seed_cfg, schema)
    if problems:
        scan_line = "FAIL: {} breach(es) across {} CSV cells and {} mixpanel lines ({} values) checked".format(
            len(problems), cell_checks, mp_lines, mp_values)
        print("{} scan: {}".format(run, scan_line))
        for pr in problems:
            print("  " + pr)
    else:
        scan_line = "PASS: 0 breaches across {} CSV cells and {} mixpanel lines ({} values) checked".format(
            cell_checks, mp_lines, mp_values)
        print("{} scan: {}".format(run, scan_line))

    write_exports_readme(run, summaries, mixpanel_summaries, scan_line, zip_name)
    return len(problems) == 0


def do_scan_only(run, schema, exports_root):
    seed_cfg = load_json(SEED_CONFIG_PATH)
    problems, cell_checks, mp_lines, mp_values, _sensitive = run_scan(run, exports_root, seed_cfg, schema)
    if problems:
        print("{} scan: FAIL, {} breach(es) across {} CSV cells and {} mixpanel lines ({} values) checked".format(
            run, len(problems), cell_checks, mp_lines, mp_values))
        for pr in problems:
            print("  " + pr)
        return False
    print("{} scan: PASS, 0 breaches across {} CSV cells and {} mixpanel lines ({} values) checked".format(
        run, cell_checks, mp_lines, mp_values))
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", choices=RUNS, help="one run only (default: both)")
    ap.add_argument("--scan-only", action="store_true", help="scan existing exports, write nothing")
    ap.add_argument("--dir", help="scan this directory instead of data/seed/<run>/exports (with --scan-only)")
    args = ap.parse_args()

    runs = [args.run] if args.run else RUNS
    schema = load_json(SCHEMA_PATH)

    ok = True
    if args.scan_only:
        for run in runs:
            exports_root = Path(args.dir) if args.dir else (SEED_DIR / run / "exports")
            ok = do_scan_only(run, schema, exports_root) and ok
    else:
        if args.dir:
            print("--dir is only meaningful with --scan-only; ignoring it", file=sys.stderr)
        for run in runs:
            ok = do_build(run, schema) and ok

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
