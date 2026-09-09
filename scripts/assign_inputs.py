#!/usr/bin/env python3
"""Phase 1b: give every review row a workstream, an owner and a status (PLAN.md section 4 rules),
then validate the data layer (CLAUDE.md working discipline).

Statuses: open (attached to an open item), quick-accept (owner ticks in the meeting),
accepted (the owner said it, or nothing is asked), answered (the v0.1 spec answers a factual question).
The table below is explicit per row; nothing is guessed from wording.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

# n: (workstream, status, item, answer or note)
ASSIGN = {
    1: ("tech", "open", "G1", ""),
    2: ("sku-set", "open", "T1", ""),
    3: ("journey-to-paywall", "quick-accept", "", ""),
    4: ("tech", "accepted", "", "Gaurav owns tech (A02 mechanics)."),
    5: ("tech", "accepted", "", "Gaurav owns tech (OTP handling)."),
    6: ("tech", "accepted", "", "Gaurav owns tech (video delivery, A04 mechanics)."),
    7: ("journey-to-paywall", "quick-accept", "", ""),
    8: ("journey-to-paywall", "quick-accept", "", ""),
    9: ("journey-to-paywall", "quick-accept", "", ""),
    10: ("journey-to-paywall", "quick-accept", "", ""),
    11: ("journey-to-paywall", "quick-accept", "", ""),
    12: ("journey-to-paywall", "accepted", "", "Bhuvanaa owns journey-to-paywall."),
    13: ("tech", "accepted", "", "Gaurav owns analytics events. X01 and N01 in v0.1 already list the drop-off states and their nudges."),
    14: ("journey-to-paywall", "accepted", "B1", "Bhuvanaa owns the pre-paywall copy; also listed under B1."),
    15: ("journey-to-paywall", "quick-accept", "B1", "A question for the content owner; gap G08 covers the content list. Also listed under B1."),
    16: ("journey-to-paywall", "open", "B1", ""),
    17: ("journey-to-paywall", "open", "B1", ""),
    18: ("journey-to-paywall", "accepted", "B1", "Bhuvanaa owns the pre-paywall screens; also listed under B1."),
    19: ("journey-to-paywall", "answered", "V1", "The link goes to H08 Community (spec v0.1, X01 ui). X01 nudges: day 1 reveal saved, day 3 an insight from the reveal, day 7 testimonials and paywall details, day 21, day 82 (X01 logic). Testimonials are subject to gap G02."),
    20: ("sku-set", "open", "T1", ""),
    21: ("admin", "quick-accept", "", ""),
    22: ("admin", "open", "K1", ""),
    23: ("data-collection", "quick-accept", "", ""),
    24: ("data-collection", "answered", "", "The tier is chosen at the paywall (spec v0.1: P01 field sku); O01 renders one card by tier (O01 logic). The three cards in the frame are the three tier variants, not a choice."),
    25: ("data-collection", "accepted", "", "Bhuvanaa owns data-collection (O01)."),
    26: ("data-collection", "quick-accept", "", "Step 1 leads to A05, the AA explainer; O02 is the hub the user returns to (spec v0.1, O02 logic)."),
    27: ("tech", "accepted", "", "Gaurav owns the AA vendor flow. His note answers Somil's question: the OTPs are the AA's own consent steps (discover, then fetch per provider), not a yeslyf screen."),
    28: ("data-collection", "accepted", "", "Bhuvanaa owns data-collection."),
    29: ("data-collection", "accepted", "", "Bhuvanaa owns data-collection; the Safebox integration is a build question for Gaurav."),
    30: ("investment-advisory", "open", "H3", ""),
    31: ("financial-plan-logic", "quick-accept", "", ""),
    32: ("financial-plan-logic", "open", "B2", ""),
    33: ("financial-plan-logic", "open", "B4", ""),
    34: ("adviser-staffing", "open", "S1", ""),
    35: ("calls-model", "open", "T2", ""),
    36: ("tech", "accepted", "", "Gaurav owns E01-E06 integrations."),
    37: ("tech", "accepted", "", "Gaurav owns E01-E06 integrations."),
    38: ("compliance", "open", "H4", ""),
    39: ("product", "accepted", "", "Vatsal owns product; accepted as a goals progress screen, H10 (PLAN.md section 9)."),
    40: ("product", "answered", "", "v0.1 draws the split on H02: invested by you vs market movement, from monthly snapshots (H02 dev) and the AA refresh on open (H01 dev). Whether the data supports it is a build question in Gaurav's workstream."),
    41: ("product", "answered", "", "H02 and H03 open from the Progress card on Home; H04 is the Actions tab. Home tabs: Home, Plan, Actions, Vault, Help (spec v0.1, H01 ui and branches)."),
    42: ("product", "answered", "", "State S11 (plan updated) puts a banner on Home that opens H05 (spec v0.1, H01 states); the nudge goes by push, WhatsApp or email per N01 (N01 dev) and the admin/CRM nudge row for S11."),
    43: ("product", "accepted", "", "Vatsal owns product; accepted as a portfolio screen, H11 (PLAN.md section 9)."),
    44: ("product", "answered", "", "Vault is a tab on Home (spec v0.1, H01 ui tabs; branch Vault to H06)."),
    45: ("calls-model", "open", "T2", ""),
    46: ("product", "open", "V1", ""),
    47: ("product", "accepted", "", "Vatsal owns product; accepted as the rebuild rule: any time, versions kept, diff shown (PLAN.md section 9). Spec v0.1 H09: update answers reopens the relevant D screens, the plan re-runs, H05 shows the diff; H06 keeps plan versions."),
    48: ("crm-and-nudges", "answered", "", "Every N01 state already maps to nudge rows in the admin/CRM spec v0.1 (NUDGES table, sent as Zoho journeys keyed on journey stage; PLACEMENT, Notifications). N01 dev: templates live in the CRM."),
    49: ("tech", "open", "G2", ""),
    50: ("admin", "accepted", "G2", "Kajal owns admin; also listed under G2."),
    51: ("logic-panel", "quick-accept", "H1", "Also listed under H1."),
    52: ("financial-plan-logic", "open", "B3", ""),
    53: ("product", "answered", "", "Q02 opens only the questions the chosen event affects (event to question map), re-runs the plan and shows the diff on H05 (spec v0.1, Q02 purpose and logic). Vatsal accepts a copy change on the line (PLAN.md section 9)."),
    54: ("product", "accepted", "", "Vatsal owns product; accepted (PLAN.md section 9)."),
    55: ("admin", "accepted", "", "No change asked."),
    56: ("", "accepted", "", "Keep verdicts; no change asked."),
    57: ("logic-panel", "answered", "", "Yes. L02 holds every number the engine uses that is not the user's own, editable with effective dates; a change creates a staging version, and every plan stores the assumptions version it used (spec v0.1, L02)."),
    58: ("compliance", "open", "K1", ""),
    59: ("data-collection", "quick-accept", "", ""),
    60: ("data-collection", "quick-accept", "", ""),
    61: ("financial-plan-logic", "answered", "", "Already the rule: the G04 target is 6 months of expenses, with the months value in L02 (spec v0.1, G04 ui and logic)."),
    62: ("tech", "open", "G1", ""),
    63: ("tech", "open", "G1", ""),
    64: ("investment-advisory", "accepted", "", "Harish owns investment-advisory; rationale storage accepted (PLAN.md section 9)."),
    65: ("product", "open", "V1", ""),
    66: ("compliance", "open", "H5", ""),
    67: ("crm-and-nudges", "open", "V2", ""),
    68: ("investment-advisory", "open", "H1", ""),
    69: ("investment-advisory", "open", "H1", ""),
    70: ("logic-panel", "open", "H2", ""),
    71: ("logic-panel", "answered", "", "Commentary means the user-facing timing text: the lumpsum-versus-staggered rule fed by a few numbers the adviser types, no live feeds (spec v0.1, L07 purpose)."),
    72: ("logic-panel", "answered", "", "In the engine, not in the panel: L05 previews a staged change by running the engine against a snapshot of all active users (spec v0.1, L05 purpose and dev). The allocation logic sits behind G11 to G13."),
    73: ("compliance", "open", "H6", ""),
}

STATUSES = ("open", "quick-accept", "accepted", "answered")


def load(name):
    with open(os.path.join(DATA, name)) as fh:
        return json.load(fh)


def dump(name, obj):
    text = json.dumps(obj, indent=1, ensure_ascii=True) + "\n"
    with open(os.path.join(DATA, name), "w") as fh:
        fh.write(text)


def main():
    inputs = load("inputs.json")
    ownership = {w["id"]: w for w in load("ownership.json")["workstreams"]}
    items = {i["id"]: i for i in load("open_items.json")["items"]}
    gaps = load("gaps.json")["gaps"]
    errors = []

    for row in inputs["rows"]:
        n = row["n"]
        if n not in ASSIGN:
            errors.append("row %d has no assignment" % n)
            continue
        ws, status, item, note = ASSIGN[n]
        if status not in STATUSES:
            errors.append("row %d: bad status %s" % (n, status))
        if ws and ws not in ownership:
            errors.append("row %d: unknown workstream %s" % (n, ws))
        if item and item not in items:
            errors.append("row %d: unknown item %s" % (n, item))
        if status == "open" and not item:
            errors.append("row %d is open but attached to no item" % n)
        if status == "answered" and not note:
            errors.append("row %d is answered without answer text" % n)
        w = ownership.get(ws)
        row["workstream"] = ws
        row["owner"] = list(w["owner"]) if w else []
        row["status"] = status
        row["item"] = item
        if status == "answered":
            row["answer"] = note
            row["answer_by"] = "spec v0.1"
            row["note"] = ""
        else:
            row["note"] = note
            row.pop("answer", None)
            row.pop("answer_by", None)

    # open items: every item has an owner, at least one named position, options with holders or 'possible form'
    for it in items.values():
        if not it.get("owner"):
            errors.append("%s has no owner" % it["id"])
        if not it.get("positions"):
            errors.append("%s has no named position" % it["id"])
        for p in it.get("positions", []):
            if not p.get("who") or not p.get("ref"):
                errors.append("%s: position without who or ref" % it["id"])
        for o in it.get("options", []):
            if not o.get("held_by"):
                o["possible_form"] = True
        keys = [o["key"] for o in it.get("options", [])]
        d = it.get("default")
        if it["owner"] == ["Team"] and d:
            errors.append("%s is a Team item with a default" % it["id"])
        if d:
            if d["key"] not in keys:
                errors.append("%s default key %s not in options" % (it["id"], d["key"]))
            if d["who"] not in it["owner"]:
                errors.append("%s default is held by %s who is not the owner" % (it["id"], d["who"]))
            holders = " ".join(o["held_by"] and " ".join(o["held_by"]) or "" for o in it["options"] if o["key"] == d["key"])
            if d["who"] not in holders:
                errors.append("%s default option %s is not held by %s" % (it["id"], d["key"], d["who"]))
        for dep in it.get("dependencies", []):
            if dep.get("recommended_by") != "Vatsal":
                errors.append("%s dependency without Vatsal as recommender" % it["id"])
        text = json.dumps(it).lower()
        for banned in ("founder", "recommendation"):
            if banned in text:
                errors.append("%s contains the word %s" % (it["id"], banned))
        # rows attached to the item must point back
        for n in it.get("input_rows", []):
            if ASSIGN.get(n, ("", "", "", ""))[2] != it["id"]:
                errors.append("%s lists row %d but the row points to %r" % (it["id"], n, ASSIGN.get(n, ("", "", "", ""))[2]))
    for row in inputs["rows"]:
        if row["item"] and row["n"] not in items[row["item"]].get("input_rows", []):
            errors.append("row %d points to %s but the item does not list it" % (row["n"], row["item"]))

    for g in gaps:
        for k in ("id", "title", "why", "recommendation", "suggested_owner", "impact"):
            if not g.get(k):
                errors.append("gap %s missing %s" % (g.get("id"), k))
        if "founder" in json.dumps(g).lower():
            errors.append("gap %s contains founders" % g["id"])

    # ASCII check on every data file
    for name in sorted(os.listdir(DATA)):
        if name.endswith(".json"):
            with open(os.path.join(DATA, name), "rb") as fh:
                data = fh.read()
            bad = [i for i, b in enumerate(data) if b > 126]
            if bad:
                errors.append("%s has non-ASCII bytes at %s" % (name, bad[:3]))

    if errors:
        for e in errors:
            print("ERROR: " + e)
        sys.exit(1)

    dump("inputs.json", inputs)
    dump("open_items.json", {"source": load("open_items.json")["source"], "items": list(items.values())})

    counts = {}
    for row in inputs["rows"]:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    print("statuses:", counts)
    print("")
    print("%-4s %-24s %-22s %-26s %s" % ("item", "owner", "default (who)", "title", "positions"))
    for it in items.values():
        d = it.get("default")
        who = " and ".join(it["owner"])
        if d:
            dflt = "%s: option %s" % (d["who"], d["key"])
        elif it["owner"] == ["Team"]:
            dflt = "none (Team)"
        else:
            dflt = who + " to decide"
        print("%-4s %-24s %-22s %-26s %d" % (it["id"], who + (" (with " + ", ".join(it["with"]) + ")" if it.get("with") else ""), dflt, it["title"][:26], len(it["positions"])))
    print("")
    qa = {}
    for row in inputs["rows"]:
        if row["status"] == "quick-accept":
            qa.setdefault(" and ".join(row["owner"]), []).append("%d %s (%s)" % (row["n"], row["screen"], row["reviewer"]))
    for owner, rows in qa.items():
        print("quick-accepts for %s: %s" % (owner, "; ".join(rows)))


if __name__ == "__main__":
    main()
