#!/usr/bin/env python3
"""Check the provisioned Zoho org against the run-3000 exports (phase F), then write seed/zoho/leftovers.md.

Counts: every file's external IDs read back from Zoho (CRM by COQL, Desk tickets by search on Ticket External
ID) against the IDs the export carries, the whole set, not a sample; the four Campaigns lists of this phase are
counted once someone has imported them by hand; the Bookings service is looked up. Spot check: ten people end to
end, the eight contacts and two leads with the most linked rows: the record's name, phone and email, and every
linked row in each CRM file that carries the contact's external ID, and in Desk.

leftovers.md: every step the API refused or that no API covers (data/zoho_provision.json), each with its manual
fallback, then what the counts find missing.

Usage: python3 seed/zoho/verify.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import zoho  # noqa: E402
import provision as P  # noqa: E402

LEFTOVERS = os.path.join(HERE, "leftovers.md")
SPOT_CONTACTS, SPOT_LEADS = 8, 2
RECORD_LABELS = ["First Name", "Last Name", "Phone", "Email"]


def cell(text):
    return P.ascii_text(str(text), 400).replace("|", "/").replace("\n", " ")


class Check:
    def __init__(self):
        self.d = P.Data()
        self.c = zoho.Client()
        self.state = P.load_state()
        self.counts = []   # (object, expected, found, missing sample)
        self.missing = []  # (item, what, fallback)
        self.spot = []
        self.tickets = {}  # Ticket External ID -> Desk status, filled by desk_counts
        mods = {m.get("plural_label"): m["api_name"] for m in self.c.crm("GET", "/settings/modules")["modules"]}
        self.module, self.label_api = {}, {}
        for stem, path in self.d.crm_files:
            obj = self.d.idx[path]["object"]
            if obj in mods:
                self.module[path] = mods[obj]
                # file column label -> api name, resolved the way provision.py maps it (its label index, and its
                # LABEL_MAP where the Zoho field is labelled differently from the column)
                by = P.label_index(self.c.crm("GET", "/settings/fields", params={"module": mods[obj]})["fields"])
                self.label_api[path] = {}
                for col in self.d.idx[path]["columns"]:
                    zlabel = P.LABEL_MAP.get((path, col["label"]), col["label"])
                    if zlabel in by:
                        self.label_api[path][col["label"]] = by[zlabel]["api_name"]

    def coql_all(self, module_api, select, where):
        rows, last = [], None
        while True:
            cond = where if last is None else "(%s) and id > %s" % (where, last)
            q = "select id, %s from %s where %s order by id asc limit 2000" % (select, module_api, cond)
            page = P.coql_rows(self.c.crm("POST", "/coql", body={"select_query": q}, safe=True))
            rows.extend(page)
            if len(page) < 2000:
                return rows
            last = page[-1]["id"]

    # -- counts
    def crm_counts(self):
        for stem, path in self.d.crm_files:
            f = self.d.idx[path]
            expected = {r[f["external_id"]] for r in P.read_csv(path)}
            ext_api = self.label_api.get(path, {}).get(f["external_id"])
            if not ext_api:
                self.counts.append((f["object"], len(expected), 0, "no module or no %s field" % f["external_id"]))
                self.missing.append(("import/%s" % stem, "all %d %s rows" % (len(expected), f["object"]),
                                     "Import %s by hand (operator page step 10)." % path))
                continue
            found = {r.get(ext_api) for r in self.coql_all(self.module[path], ext_api, "%s is not null" % ext_api)}
            self.report(stem, path, f["object"], expected, found)

    def report(self, stem, path, obj, expected, found):
        miss = sorted(expected - found)
        extra = len(found - expected)
        self.counts.append((obj, len(expected), len(found & expected), ", ".join(miss[:5]) + (" and %d more" % (len(miss) - 5) if len(miss) > 5 else "")))
        zoho.log("  %-12s export %6d, in Zoho %6d, missing %d, extra %d" % (obj, len(expected), len(found & expected), len(miss), extra))
        if miss:
            self.missing.append(("import/%s" % stem, "%d %s rows missing (%s)" % (len(miss), obj, ", ".join(miss[:5])),
                                 "Re-run provision.py (upsert) once the cause in the rows above is fixed, or import "
                                 "those rows by hand."))

    def desk_counts(self):
        path = self.d.desk_file
        f = self.d.idx[path]
        rows = P.read_csv(path)
        ext = P.desk_tickets_setup(self.c)[3].get(f["external_id"])
        self.tickets = {}
        if not ext:
            self.counts.append(("Tickets", len(rows), 0, "no %s field" % f["external_id"]))
            return
        for row in rows:
            hit = (self.c.desk("GET", "/tickets/search", params={"customField1": "%s:%s" % (ext["apiName"], row[f["external_id"]]),
                                                               "limit": 1}) or {}).get("data") or []
            if hit:
                self.tickets[row[f["external_id"]]] = hit[0].get("status")
        expected = {r[f["external_id"]] for r in rows}
        self.report("tickets", path, "Tickets", expected, set(self.tickets))
        wrong = [r[f["external_id"]] for r in rows if r[f["external_id"]] in self.tickets
                 and self.tickets[r[f["external_id"]]] != P.DESK_STATUS[r["Status"]]]
        if wrong:
            self.missing.append(("import/tickets", "%d tickets with the wrong status (%s)" % (len(wrong), ", ".join(wrong[:5])),
                                 "Set the status by hand, closing without a closure notification."))

    def campaign_counts(self):
        resp = self.c.campaigns("GET", "/getmailinglists", params={"resfmt": "JSON", "sort": "asc", "fromindex": 1, "range": 100}) or {}
        lists = {x.get("listname"): x for x in resp.get("list_of_details") or []}
        for stage in P.CAMPAIGN_LISTS:
            rows = P.read_csv(P.op.campaign_path(stage))
            want = sum(1 for r in rows if r["Email"])
            got = lists.get(stage)
            n = int(got.get("noofcontacts") or 0) if got else 0
            self.counts.append(("Campaigns %s" % stage, want, n, "" if got else "list not imported yet (manual step)"))
            zoho.log("  Campaigns %-4s rows with an email %4d, in the list %4d%s" % (stage, want, n, "" if got else " (no list yet)"))

    def bookings_check(self):
        name = self.d.service_name()
        ws = ((self.c.bookings("GET", "/workspaces") or {}).get("response", {}).get("returnvalue", {}).get("data") or [])
        svc = []
        if ws:
            resp = self.c.bookings("GET", "/services", params={"workspace_id": ws[0]["id"]}) or {}
            svc = [s for s in resp.get("response", {}).get("returnvalue", {}).get("data") or [] if s.get("name") == name]
        self.counts.append(("Bookings service", 1, len(svc), "" if svc else "%s not found" % name))
        zoho.log("  Bookings service %r: %s" % (name, ("found, %s" % svc[0].get("duration")) if svc else "not found"))

    # -- spot check
    def pick(self):
        contacts = self.d.idx["zoho/contacts.csv"]
        link = contacts["external_id"]
        linked = {}
        for stem, path in self.d.crm_files:
            f = self.d.idx[path]
            if path == "zoho/contacts.csv" or link not in [c["label"] for c in f["columns"]]:
                continue
            for row in P.read_csv(path):
                linked.setdefault(row[link], {}).setdefault(path, set()).add(row[f["external_id"]])
        by_contact = self.d.person_by_contact()
        tf = self.d.idx[self.d.desk_file]
        for row in P.read_csv(self.d.desk_file):
            pid = by_contact.get(row["Contact Phone"]) or by_contact.get(row["Contact Email"])
            linked.setdefault(pid, {}).setdefault(self.d.desk_file, set()).add(row[tf["external_id"]])
        people = self.d.people()

        def score(pid):
            files = linked.get(pid, {})
            return (-len(files), -sum(len(v) for v in files.values()), pid)
        ranked = sorted((p for p in people if people[p][0] == "Contacts"), key=score)
        chosen = []
        # first the best-linked contact for each linked file nobody chosen covers yet, so every object is walked
        for lpath in sorted({lp for files in linked.values() for lp in files}):
            if not any(lpath in linked.get(p, {}) for p in chosen):
                pick = next((p for p in ranked if lpath in linked.get(p, {})), None)
                if pick:
                    chosen.append(pick)
        chosen += [p for p in ranked if p not in chosen][:max(0, SPOT_CONTACTS - len(chosen))]
        chosen += sorted((p for p in people if people[p][0] == "Leads"), key=score)[:SPOT_LEADS]
        return chosen, people, linked, link

    def spot_check(self):
        chosen, people, linked, link = self.pick()
        paths = {self.d.idx[p]["object"]: p for s, p in self.d.crm_files}
        for pid in chosen:
            obj, row = people[pid]
            path = paths[obj]
            apis = self.label_api.get(path, {})
            ext_api = apis.get(self.d.idx[path]["external_id"])
            problems, parts = [], []
            sel = [apis[x] for x in RECORD_LABELS if x in apis]
            got = P.coql_rows(self.c.crm("POST", "/coql", safe=True, body={
                "select_query": "select %s from %s where %s = '%s' limit 2" % (", ".join(sel), self.module[path], ext_api, pid)}))
            if len(got) != 1:
                problems.append("%d %s records" % (len(got), obj))
            else:
                for x in RECORD_LABELS:
                    if x in apis and (got[0].get(apis[x]) or "") != row[x]:
                        problems.append("%s is %r, export %r" % (x, got[0].get(apis[x]), row[x]))
                parts.append("record ok" if not problems else "record differs")
            for lpath, want in sorted(linked.get(pid, {}).items()):
                if lpath == self.d.desk_file:
                    have = {t for t in want if t in self.tickets}
                    parts.append("tickets %d/%d" % (len(have), len(want)))
                    if have != want:
                        problems.append("tickets missing: %s" % ", ".join(sorted(want - have)))
                    continue
                f = self.d.idx[lpath]
                lapis = self.label_api.get(lpath, {})
                lext, llink = lapis.get(f["external_id"]), lapis.get(link)
                have = set()
                if lext and llink:
                    have = {r.get(lext) for r in self.coql_all(self.module[lpath], lext, "%s = '%s'" % (llink, pid))}
                parts.append("%s %d/%d" % (f["object"], len(have & want), len(want)))
                if have != want:
                    problems.append("%s missing: %s" % (f["object"], ", ".join(sorted(want - have)[:5])))
            line = "%s (%s): %s" % (pid, obj, ", ".join(parts))
            self.spot.append((pid, obj, ", ".join(parts), "; ".join(problems) or "ok"))
            zoho.log("  " + line + ("" if not problems else "  PROBLEM: " + "; ".join(problems)))

    # -- leftovers.md
    def write(self):
        st = self.state
        ct = st.get("created_time") or {}
        out = ["# Zoho provisioning leftovers (phase F)", "",
               "Written by seed/zoho/verify.py on %s from data/zoho_provision.json (provision run of %s) and the "
               "verify counts, run-3000 exports. Each row is a step the API refused or that no API covers, with the "
               "manual fallback. Operator page items that are neither marked done by script nor listed here were "
               "never part of this phase; they stay as they were." % (zoho.stamp(), st.get("last_run", "?")), ""]
        if ct:
            out += ["Created_Time on the first record insert (%s %s, sent %s): %s%s." % (
                ct.get("module"), ct.get("record"), ct.get("sent"), ct.get("answer"),
                (", Zoho stamped " + ct["read_back"]) if ct.get("read_back") else (": " + ct["detail"]) if ct.get("detail") else ""), ""]
        rows = [x for x in st.get("left") or [] if x.get("kind") != "note"]
        out += ["## Left for a manual step (%d)" % len(rows), "",
                "| Operator item | What | Why | Manual fallback |", "|---|---|---|---|"]
        for x in rows:
            out.append("| %s | %s | %s | %s |" % (cell(x["item"]), cell(x["what"]), cell(x["why"]), cell(x["fallback"])))
        notes = [x for x in st.get("left") or [] if x.get("kind") == "note"]
        if notes:
            out += ["", "## Imported without a column (%d)" % len(notes), "", "| Operator item | What | Why | Later |",
                    "|---|---|---|---|"]
            for x in notes:
                out.append("| %s | %s | %s | %s |" % (cell(x["item"]), cell(x["what"]), cell(x["why"]), cell(x["fallback"])))
        if self.missing:
            out += ["", "## Missing after the run (%d)" % len(self.missing), "", "| Operator item | What | Manual fallback |",
                    "|---|---|---|"]
            for item, what, fb in self.missing:
                out.append("| %s | %s | %s |" % (cell(item), cell(what), cell(fb)))
        out += ["", "## Counts", "", "| Object | Export | In Zoho | Missing |", "|---|---|---|---|"]
        for obj, want, got, miss in self.counts:
            out.append("| %s | %d | %d | %s |" % (cell(obj), want, got, cell(miss) or "-"))
        out += ["", "## Ten people end to end", "", "| Person | Object | Linked rows found | Result |", "|---|---|---|---|"]
        for pid, obj, parts, res in self.spot:
            out.append("| %s | %s | %s | %s |" % (pid, obj, cell(parts), cell(res)))
        text = "\n".join(out) + "\n"
        text.encode("ascii")
        with open(LEFTOVERS, "w") as fh:
            fh.write(text)
        zoho.log("wrote %s: %d manual steps, %d missing after the run" % (os.path.relpath(LEFTOVERS, P.ROOT), len(rows), len(self.missing)))


def main():
    if sys.argv[1:]:
        raise SystemExit(__doc__)
    ch = Check()
    zoho.log("verify: counts")
    for name, step in [("CRM counts", ch.crm_counts), ("Desk counts", ch.desk_counts), ("Campaigns", ch.campaign_counts),
                       ("Bookings", ch.bookings_check), ("ten people end to end", ch.spot_check)]:
        try:
            step()
        except Exception as e:  # one refused read must not keep leftovers.md from being written
            zoho.log("  %s not checked: %s" % (name, P.ascii_text(e, 200)))
            ch.counts.append((name, 0, 0, "not checked: %s" % P.ascii_text(e, 120)))
    ch.write()


if __name__ == "__main__":
    main()
