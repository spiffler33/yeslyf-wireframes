#!/usr/bin/env python3
"""Read the Zoho org as phase G finds it (G0) and as it leaves it (G9): counts only, nothing written to Zoho.

Reads, all by API: CRM users, roles, profiles, the saved views of the five modules the seats' views live on, the v8
API list (which paths and scopes exist for custom views and dashboards); Desk views and the tickets' assignee and
due date (an SLA leaves a due date; the only documented SLA list call is per account and needs Desk.accounts.READ,
which the grant lacks); Campaigns lists; Bookings staff on the service and appointments; Calls. Each read is one
row: object, count now, target after G9, detail. A read the grant refuses is a row too, never a crash.

Writes data/zoho_live.json: "baseline" on the first run only, "counts" on every run, and leaves "items" (what the
later phases did by hand, with a timestamp and how) untouched. Prints the same table.

Usage: python3 seed/zoho/live.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import zoho  # noqa: E402
import provision as P  # noqa: E402

LIVE_FILE = os.path.join(P.ROOT, "data", "zoho_live.json")
APIS_FILE = os.path.join(zoho.LOCAL, "apis_v8.json")
STAFF_FILE = os.path.join(P.ROOT, "data", "seed", "run-3000", "staff.json")
CALLS_CSV = "zoho/calls.csv"

# The saved views phase G builds by hand, by module plural label, named exactly as seed/zoho/leftovers.md lists them
# (the 15 "saved view" rows: 11 on CRM modules, 4 on Desk tickets).
CRM_VIEWS = {
    "Deals": ["Paid by SKU, this week and last", "Payment reconciliation", "GST split", "Refunds"],
    "Contacts": ["DIFM prospects to call", "Same adviser offer", "Opt-in and DND"],
    "Tasks": ["Call centre today", "Call centre outcomes"],
    "App Events": ["RPQ refresh due"],
    "A la carte": ["A la carte receipts"],
}
DESK_VIEWS = ["Grievances past SLA", "Grievance register", "Open tickets with context", "Past SLA"]
FINANCE_PROFILE = "Finance read only"
# paths of the v8 API list worth quoting in the phase report (custom views and dashboards have no known create call)
API_WORDS = ["custom_views", "analytics", "dashboard", "profiles", "roles", "users"]
APPOINTMENT_WINDOW = ("01-Jan-2026 00:00:00", "31-Dec-2027 23:59:59")  # dd-MMM-yyyy HH:mm:ss, the docs' format


def refusal(e):
    return "not read: %s" % (e.code() if isinstance(e, zoho.ApiError) else P.ascii_text(e, 120))


class Live:
    def __init__(self):
        self.c = zoho.Client()
        self.rows = []  # (object, now, target, detail)
        with open(STAFF_FILE) as fh:
            self.staff = json.load(fh)
        self.staff_names = {s["name"] for s in self.staff.values()}

    def row(self, obj, now, target, detail=""):
        self.rows.append((obj, now, target, P.ascii_text(detail, 300)))
        zoho.log("  %-28s now %5s  target %5s  %s" % (obj, now, target, detail))

    def guarded(self, name, fn):
        try:
            fn()
        except Exception as e:  # a refused read is a row, and the next read runs
            self.row(name, "-", "-", refusal(e))

    # ---- CRM
    def users(self):
        users = (self.c.crm("GET", "/users", params={"type": "AllUsers"}) or {}).get("users") or []
        seen = []
        for u in users:
            name = u.get("full_name") or ""
            who = name if name in self.staff_names else "the admin user"  # never an email or a surname
            seen.append("%s: %s, %s, %s" % (who, (u.get("role") or {}).get("name"), (u.get("profile") or {}).get("name"),
                                           u.get("status")))
        self.row("users", len(users), 1 + len(self.staff), "; ".join(seen))

    def roles(self):
        roles = (self.c.crm("GET", "/settings/roles") or {}).get("roles") or []
        self.row("roles", len(roles), len(roles), ", ".join(r.get("display_label") or r.get("name") or "?" for r in roles))

    def profiles(self):
        profiles = (self.c.crm("GET", "/settings/profiles") or {}).get("profiles") or []
        names = [p.get("display_label") or p.get("name") or "?" for p in profiles]
        target = len(profiles) + (0 if FINANCE_PROFILE in names else 1)
        self.row("profiles", len(profiles), target, ", ".join(names) + ("" if FINANCE_PROFILE in names else
                                                                        "; %s not yet" % FINANCE_PROFILE))

    def view_count(self, api, view_id):
        """Records in a custom view: the records API paged by cvid (info.count is the page's count, so the pages
        are summed until more_records is false)."""
        n, page = 0, 1
        while True:
            resp = self.c.crm("GET", "/" + api, params={"cvid": view_id, "fields": "id", "per_page": 200, "page": page}) or {}
            n += len(resp.get("data") or [])
            if not (resp.get("info") or {}).get("more_records"):
                return n
            page += 1

    def crm_views(self):
        mods = {m.get("plural_label"): m["api_name"] for m in self.c.crm("GET", "/settings/modules")["modules"]}
        for label, wanted in CRM_VIEWS.items():
            api = mods.get(label)
            if not api:
                self.row("views %s" % label, "-", len(wanted), "no module with that label")
                continue
            views = (self.c.crm("GET", "/settings/custom_views", params={"module": api}) or {}).get("custom_views") or []
            by_name = {}
            for v in views:
                by_name.setdefault(v.get("name"), v)
                by_name.setdefault(v.get("display_value"), v)
            have, missing = [], []
            for w in wanted:
                if w in by_name:
                    have.append("%s %d" % (w, self.view_count(api, by_name[w]["id"])))
                else:
                    missing.append(w)
            self.row("views %s" % label, len(have), len(wanted), "%d views on the module; present (records): %s; missing: %s" %
                     (len(views), "; ".join(have) or "none", ", ".join(missing) or "none"))

    def apis(self):
        resp = self.c.crm("GET", "/__apis") or {}
        items = resp.get("__apis") or resp.get("apis") or []
        os.makedirs(zoho.LOCAL, exist_ok=True)
        with open(APIS_FILE, "w") as fh:
            json.dump(resp, fh, indent=1, sort_keys=True)
        hits = []
        for it in items:
            path = it.get("path") or it.get("name") or ""
            if any(w in path.lower() for w in API_WORDS):
                ops = ", ".join("%s %s" % (o.get("method"), o.get("oauth_scope")) for o in it.get("operation_types") or [])
                hits.append("%s [%s]" % (path, ops))
        for h in sorted(hits):
            zoho.log("    api %s" % h)
        self.row("v8 api paths listed", len(items), len(items), "%d paths name custom views, analytics, dashboards, "
                 "profiles, roles or users (printed above; the whole list is in %s)" %
                 (len(hits), os.path.relpath(APIS_FILE, P.ROOT)))

    def calls(self):
        n, page = 0, 1
        while True:
            resp = self.c.crm("GET", "/Calls", params={"fields": "id", "per_page": 200, "page": page}) or {}
            n += len(resp.get("data") or [])
            if not (resp.get("info") or {}).get("more_records"):
                break
            page += 1
        rows = P.read_csv(CALLS_CSV)
        self.row("calls", n, len(rows), "export rows by status: " + ", ".join(
            "%s %d" % (s, sum(1 for r in rows if r["Status"] == s)) for s in sorted({r["Status"] for r in rows})))

    # ---- Desk
    def desk(self):
        deps, dep, lay, by_label = P.desk_tickets_setup(self.c)
        if not dep:
            self.row("desk views", "-", len(DESK_VIEWS), "no default department")
            return
        views = (self.c.desk("GET", "/views", params={"module": "tickets", "departmentId": dep["id"]}) or {}).get("data") or []
        names = {v.get("name") for v in views}
        have = [w for w in DESK_VIEWS if w in names]
        self.row("desk views", len(have), len(DESK_VIEWS), "%d views, %d custom; missing: %s" %
                 (len(views), sum(1 for v in views if v.get("isCustomView")), ", ".join(w for w in DESK_VIEWS if w not in names) or "none"))

    def desk_tickets(self):
        tickets, start = [], 0
        while True:
            page = (self.c.desk("GET", "/tickets", params={"from": start, "limit": 100}) or {}).get("data") or []
            tickets.extend(page)
            if len(page) < 100:
                break
            start += 100
        assigned = sum(1 for t in tickets if t.get("assigneeId"))
        due = sum(1 for t in tickets if t.get("dueDate"))
        open_ = sum(1 for t in tickets if (t.get("statusType") or "").lower() == "open")
        self.row("tickets assigned", assigned, len(tickets), "%d tickets; G2 assigns them to Support 01" % len(tickets))
        self.row("tickets with a due date", due, open_, "%d open tickets; an SLA sets the due date; to be verified: "
                 "whether Desk applies a new SLA to tickets that already exist" % open_)

    # ---- Campaigns
    def campaigns(self):
        resp = self.c.campaigns("GET", "/getmailinglists", params={"resfmt": "JSON", "sort": "asc", "fromindex": 1, "range": 100}) or {}
        lists = {x.get("listname"): x for x in resp.get("list_of_details") or []}
        for stage in P.CAMPAIGN_LISTS:
            want = sum(1 for r in P.read_csv(P.op.campaign_path(stage)) if r["Email"])
            got = lists.get(stage)
            self.row("campaigns %s" % stage, int(got.get("noofcontacts") or 0) if got else 0, want,
                     "list present" if got else "no list yet")

    # ---- Bookings
    def bookings(self):
        name = P.Data().service_name()
        ws = ((self.c.bookings("GET", "/workspaces") or {}).get("response", {}).get("returnvalue", {}).get("data") or [])
        if not ws:
            self.row("bookings staff on the service", "-", 6, "no workspace")
            return
        wid = ws[0]["id"]
        resp = self.c.bookings("GET", "/services", params={"workspace_id": wid}) or {}
        svc = [s for s in resp.get("response", {}).get("returnvalue", {}).get("data") or [] if s.get("name") == name]
        sid = svc[0].get("id") if svc else None
        resp = self.c.bookings("GET", "/staffs", params={"workspace_id": wid}) or {}
        staff = resp.get("response", {}).get("returnvalue", {}).get("data") or []
        on = [s for s in staff if sid and sid in (s.get("assigned_services") or [])]
        advisers = [s["name"] for s in self.staff.values() if "adviser" in s["roles"]]
        self.row("bookings staff on the service", len(on), len(advisers), "%d staff in the workspace; service %s %s" %
                 (len(staff), name, "found" if sid else "not found"))
        booked = sum(1 for r in P.read_csv(CALLS_CSV) if r["Status"] == "booked")
        n, page = 0, 1
        while True:
            body = {"from_time": APPOINTMENT_WINDOW[0], "to_time": APPOINTMENT_WINDOW[1], "page": page, "per_page": 100}
            if sid:
                body["service_id"] = sid
            rv = (self.c.bookings("POST", "/fetchappointment", files={"data": json.dumps(body)}, safe=True) or {}
                  ).get("response", {}).get("returnvalue", {})
            data = rv.get("data") if isinstance(rv, dict) else None
            n += len(data or [])
            if not (isinstance(rv, dict) and rv.get("next_page_available")):
                break
            page += 1
        self.row("bookings appointments", n, booked, "window %s to %s; target is the export's booked rows" % APPOINTMENT_WINDOW)


def write(rows):
    state = {}
    if os.path.exists(LIVE_FILE):
        with open(LIVE_FILE) as fh:
            state = json.load(fh)
    counts = {"at": zoho.stamp(), "rows": [{"object": o, "now": n, "target": t, "detail": d} for o, n, t, d in rows]}
    state.setdefault("about", "Written by seed/zoho/live.py (phase G): the Zoho org's counts before the phase "
                     "(baseline, G0) and after each run (counts), plus the operator items the phase finished by hand "
                     "or by API (items: status, at, how, phase). scripts/build_operator.py reads the items.")
    state.setdefault("cause", "plan G, 28 Sep 2026")
    state.setdefault("baseline", counts)
    state["counts"] = counts
    state.setdefault("items", {})
    text = json.dumps(state, indent=1, sort_keys=True) + "\n"
    text.encode("ascii")
    with open(LIVE_FILE, "w") as fh:
        fh.write(text)
    zoho.log("wrote %s: %d rows" % (os.path.relpath(LIVE_FILE, P.ROOT), len(rows)))


def main():
    if sys.argv[1:]:
        raise SystemExit(__doc__)
    live = Live()
    zoho.log("live: counts, read only")
    for name, step in [("users", live.users), ("roles", live.roles), ("profiles", live.profiles), ("views", live.crm_views),
                       ("v8 api paths listed", live.apis), ("calls", live.calls), ("desk views", live.desk),
                       ("tickets", live.desk_tickets), ("campaigns", live.campaigns), ("bookings", live.bookings)]:
        live.guarded(name, step)
    write(live.rows)


if __name__ == "__main__":
    main()
