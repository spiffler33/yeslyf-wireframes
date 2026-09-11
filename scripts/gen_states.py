#!/usr/bin/env python3
"""Draw section N and the H01 state variants from data/v02/states.json.

generate(states_doc, byid) -> list of screen objects in the v0.2 schema:
  N01 master state table (rebuilt), N02 onboarding ladder, N03 post-plan ladder, N04 message templates,
  N05 to N30 one message-and-landing mock per state S1 to S25, H01a to H01k the home variants by state,
  and Q05 Update your numbers (the manual quarterly review for S16 users).
byid is the dict of screens built so far; the H01 base is copied from it. Copy slots are IDs; the message
text is placeholder copy (gap G08). Called by scripts/apply_decisions.py after the overlays.
"""
import copy

CAUSE = "Vatsal, 10 Sep 2026 (section 5)"
CAUSE_V2 = "brief V2"
CAUSE_P9 = "Vatsal, 11 Sep 2026"  # phase 9: no client-data assumptions; confirm or correct on Q05
VARIANT_CAUSES = {"j": [CAUSE_P9]}
ONBOARDING = ["S2b", "S3", "S4", "S5", "S16", "S17", "S19"]
POST_PLAN = ["S6", "S7", "S8", "S9", "S10", "S11", "S12", "S13", "S15", "S18", "S20", "S21", "S22", "S23", "S24", "S25"]
CHANNEL_LABEL = {"push": "push", "whatsapp": "WhatsApp", "email": "email", "human call": "human call"}
LADDER_COLS = ["State", "Day", "Channel", "Copy slot", "Deep link", "Tier rule", "CRM task"]

VARIANTS = [
 # suffix, state, title, tier, path, hero card (title, lines), extra rows (ui rows after the hero), branches to add
 ("a", "S6", "Home: plan ready", ["ALL"], "both",
  ("Your plan is ready", ["Read it first: Plan overview, about N minutes", "What success looks like, then what needs attention, in order"]),
  [["btn", "Read my plan", "G03"]], [["Read", "G03"]]),
 ("b", "S8", "Home: next action", ["ALL"], "both",
  ("Your next action", ["<the first action from the action plan>", "In the app, or guided outside it: about N minutes"]),
  [["btn", "Do the first action", "E01"]], [["Next action", "E01"]]),
 ("c", "S9", "Home: executing", ["ALL"], "both",
  ("In progress", ["N of N actions done", "Next: <the next action>"]),
  [["btn", "Next action", "E01"]], [["Next action", "E01"]]),
 ("d", "S10", "Home: all actions done", ["ALL"], "both",
  ("All actions done", ["Your quarterly review is on <date>", "Anniversary: confirm your risk profile and renew (Q04)"]),
  [["btn", "See my progress", "H02"]], [["Progress", "H02"], ["Anniversary", "Q04"]]),
 ("e", "S11", "Home: plan updated", ["ALL"], "both",
  ("Your plan was updated", ["N changes, each with its reason", "Accept the update to refresh your action plan"]),
  [["btn", "See what changed", "H05"]], [["Update", "H05"]]),
 ("f", "S12", "Home: payment failed", ["DIY", "DIWM"], "both",
  ("Your payment did not go through", ["Retry within 7 days; nothing is lost", "The plan refresh pauses on day 7"]),
  [["btn", "Retry payment", "Q03b"]], [["Retry", "Q03b"]]),
 ("g", "S13", "Home: lapsed", ["DIY", "DIWM"], "both",
  ("Your membership has lapsed", ["Plan read-only, dated <date>; refresh stopped", "Resubscribe restores everything"]),
  [["btn", "Resubscribe", "Q03c"]], [["Resubscribe", "Q03c"]]),
 ("h", "S14", "Home: DIFM", ["DIFM"], "both",
  ("Your adviser manages this", ["This app tracks your progress; advice comes from your adviser directly", "Next review: <date>"]),
  [["btn", "Update my numbers", "H09"]], [["Update", "H09"]]),
 ("i", "S16", "Home: not connected", ["ALL"], "manual",
  ("Your next action", ["<the first action from the action plan>", "About N minutes"]),
  [["link", "Connect Account Aggregator to keep this live", "A05"], ["btn", "Do the first action", "E01"]], [["Connect", "A05"], ["Next action", "E01"]]),
 ("j", "S18", "Home: built on partial data", ["ALL"], "both",
  ("Built on what we have", ["N numbers are bands you picked, not exact figures; each can be sharpened from the plan", "The plan works today; exact numbers make it yours"]),
  [["card", "Sharpen", ["Take-home: a band you picked. Sharpen this", "Term cover: a band you picked. Sharpen this", "Each link opens the single screen and re-runs; H05 shows the diff"]],
   ["card", "Sunday sharpen", ["Want me to ask you for the N exact numbers on Sunday?", "Nudge slot N-S18-sunday"]],
   ["chips", ["Yes, Sunday", "Not now"]],
   ["btn", "Sharpen now", "D10"]], [["Sharpen", "D10"]]),
 ("k", "S22", "Home: review overdue", ["ALL"], "both",
  ("Your quarterly review is waiting", ["About N minutes: confirm what changed and rebuild", "DIWM: book a call to walk through it"]),
  [["btn", "Open the review", "Q01"], ["link", "Book a call", "K01"]], [["Review", "Q01"], ["Call", "K01"]]),
]


def ladder_summary(st):
    return "; ".join("%s %s%s" % (l["day"], CHANNEL_LABEL[l["channel"]], "" if l.get("tier", "all") == "all" else " (%s)" % l["tier"]) for l in st["ladder"])


def escalation_summary(st):
    e = st["escalation"]
    return "DIWM: %s. DIY: %s. DIFM: %s." % (e["diwm"], e["diy"], e["difm"])


def causes(st):
    out = [CAUSE]
    if any(l["channel"] == "human call" for l in st["ladder"]) or "brief V2" in st.get("cause", ""):
        out.append(CAUSE_V2)
    if "brief H5" in st.get("cause", ""):
        out.append("brief H5")
    if "11 Sep 2026" in st.get("cause", ""):
        out.append(CAUSE_P9)
    return out


def lands_text(st):
    """Landing screen for the N01 table: the alternate landing, when the contract has one, in brackets."""
    alt = st.get("lands_on_alt")
    if alt:
        return "%s (%s when %s)" % (st["lands_on"], alt["screen"], alt["when"])
    return st["lands_on"]


def desk(sid, title, purpose, ui, logic, dev, after, compliance, cause_list, events=None):
    return {
        "id": sid, "sec": "N", "title": title, "tier": ["ALL"], "frame": "desktop", "purpose": purpose,
        "ui": ui,
        "spec": {"fields": [], "logic": logic, "branches": [], "states": [], "dev": dev},
        "template": "T-table", "path": "both", "events": events or [], "compliance": compliance,
        "v02": {"status": "new", "causes": cause_list}, "after": after,
    }


def ladder_rows(states, ids):
    rows = []
    for st in states:
        if st["id"] not in ids:
            continue
        for l in st["ladder"]:
            task = "yes: %s" % ", ".join(st["crm_task"]["fields"]) if (l["channel"] == "human call" or (st["crm_task"]["created"] and l is st["ladder"][-1] and l["channel"] != "push")) else "no"
            rows.append([st["id"], l["day"], CHANNEL_LABEL[l["channel"]], l["slot"], l["link"], l.get("tier", "all"), task])
    return rows


def text_for(st, channel):
    if channel == "push":
        return st["push"]["text"]
    if channel == "whatsapp":
        return st["whatsapp"]["text"]
    if channel == "email":
        return st["email"]["text"] if st.get("email") else st["whatsapp"]["text"] + " (email variant)"
    return "Outbound call from the call centre; the CRM task carries the state ID, the missing fields and the tier."


def generate(states_doc, byid):
    states = states_doc["states"]
    rules = states_doc["rules"]
    out = []

    # N01 master table, rebuilt
    rows = [[st["id"], st["who"], lands_text(st), st["primary_action"], ladder_summary(st), escalation_summary(st), st["exit"]]
            for st in states]
    p9 = [CAUSE_P9] if any("11 Sep 2026" in st.get("cause", "") for st in states) else []
    n01 = desk("N01", "Returning-user state machine",
               "Every returning user is routed by state on open. One row per state: who, where it lands, the primary action, the nudge ladder, the human escalation by tier, the exit. The contract between backend, app and nudges.",
               [["table", ["State", "Who", "Lands on", "Primary action", "Nudge ladder", "Human escalation by tier", "Exit"], rows]],
               rules + ["States run S1 to S25; the next number is not used (Vatsal, 10 Sep 2026).", "H01 states land on their variant H01a to H01k (section 5.3)."],
               ["State is computed on every open from stored flags (M6 step determination extended).", "Nudge channels: push, WhatsApp, email, human call (brief V2); templates live in the CRM (N04)."],
               None, {"review": False, "reasons": ["internal"]}, [CAUSE, CAUSE_V2] + p9, ["crm_task_created"])
    n01.pop("after")
    n01["v02"]["status"] = "rebuilt"
    out.append(n01)

    out.append(desk("N02", "Onboarding ladder (paid, before the plan)",
                    "States S2b, S3, S4, S5, S16, S17 and S19 day by day: one row per ladder step with its channel, copy slot, deep link, tier rule and whether the CRM creates a task.",
                    [["table", LADDER_COLS, ladder_rows(states, ONBOARDING)]],
                    ["Before day 14 after payment the onboarding states may nudge at 24 hours, 72 hours and day 7 (spec v0.1, kept).", "O03's chosen time replaces the first scheduled nudge when it exists (Vatsal, 10 Sep 2026).", "Day 7 below the gate is S19: DIWM gets the outbound call task, DIY the a la carte offer (Vatsal, 10 Sep 2026; brief V2)."],
                    ["The CRM task fields are the columns the call centre sees: state ID, missing fields, tier, last screen, minutes left."],
                    "N01", {"review": False, "reasons": ["internal"]}, [CAUSE, CAUSE_V2]))

    out.append(desk("N03", "Post-plan ladder",
                    "States S6 to S13, S15, S18 and S20 to S25 day by day, under the one-nudge-a-week cap from day 14 after payment.",
                    [["table", LADDER_COLS, ladder_rows(states, POST_PLAN)]],
                    ["One nudge per week maximum across layers from day 14 after payment (spec v0.1, kept).", "Service nudges (a missed SIP, an action verified, a receipt) are not counted against the cap (spec v0.1, kept).", "Second no-show (S20): DIWM outbound call task, DIY a la carte offer (Vatsal, 10 Sep 2026; brief V2)."],
                    ["S14 DIFM is not on this ladder; the adviser relationship sets its dates."],
                    "N02", {"review": False, "reasons": ["internal"]}, [CAUSE, CAUSE_V2]))

    trows = []
    for st in states:
        for l in st["ladder"]:
            trows.append([l["slot"], CHANNEL_LABEL[l["channel"]], st["id"], l["link"], text_for(st, l["channel"])])
    out.append(desk("N04", "Message templates",
                    "Every push, WhatsApp and email template with its copy slot ID, channel, deep link and the state it serves. The text is placeholder copy (gap G08).",
                    [["table", ["Copy slot", "Channel", "State", "Deep link", "Placeholder text"], trows]],
                    ["Copy slots are IDs; the copy is content (gap G08) and lives in the CRM templates (Vatsal, 10 Sep 2026).", "Every nudge names the specific next screen and its minutes; never continue your journey (Vatsal, 10 Sep 2026).", "WhatsApp templates need approval before launch; to be verified: WhatsApp template approval lead time."],
                    ["Human-call rows are CRM tasks, not messages; the caller reads the task fields."],
                    "N03", {"review": True, "reasons": ["advertising code"]}, [CAUSE, CAUSE_V2] + p9, ["nudge_sent", "nudge_opened"]))

    # N05 to N30 mocks
    prev = "N04"
    for st in states:
        land = byid.get(st["lands_on"])
        land_title = land["title"] if land else st["lands_on"]
        lines = ["Primary action: %s" % st["primary_action"]]
        if st["minutes"]:
            lines.append(st["minutes"])
        ui = [
            ["h", "%s %s" % (st["id"], st["who"])],
            ["card", "Push (%s)" % st["push"]["slot"], [st["push"]["text"]]],
            ["card", "WhatsApp (%s)" % st["whatsapp"]["slot"], [st["whatsapp"]["text"]]],
        ]
        if st.get("email"):
            ui.append(["card", "Email (%s)" % st["email"]["slot"], [st["email"]["text"]]])
        alt = st.get("lands_on_alt")
        if alt:
            lines.append("When %s: lands on %s instead" % (alt["when"], alt["screen"]))
        ui.append(["card", "Lands on %s %s" % (st["lands_on"], land_title), lines])
        ui.append(["btn", "Open %s" % st["lands_on"], st["lands_on"]])
        if alt:
            ui.append(["btn2", "Open %s" % alt["screen"], alt["screen"]])
        events = ["state_enter_%s" % st["id"], "nudge_sent", "nudge_opened"]
        if st["crm_task"]["created"]:
            events.append("crm_task_created")
        logic = [
            "State %s: %s. Lands on %s; the nudges deep-link to %s." % (st["id"], st["who"], lands_text(st), st["deep_link"]),
            "Ladder: %s." % ladder_summary(st),
            "Escalation: %s" % escalation_summary(st),
            "Exit: %s." % st["exit"],
        ]
        if st["crm_task"]["created"]:
            logic.append("CRM task: %s (brief V2)." % ", ".join(st["crm_task"]["fields"]))
        screen = {
            "id": st["mock"], "sec": "N", "title": "State %s: %s" % (st["id"], st["who"]), "tier": ["ALL"], "frame": "phone",
            "purpose": "Message-and-landing mock for state %s: the push and WhatsApp message on the left, the landing screen on the right." % st["id"],
            "ui": ui,
            "spec": {"fields": [], "logic": logic, "branches": [["Open", st["lands_on"]]] + ([["Open", alt["screen"]]] if alt else []), "states": [st["id"]],
                     "dev": ["Copy slots are IDs; the text is placeholder copy (gap G08).", "state_enter_%s fires on open; nudge_sent and nudge_opened carry the slot and channel." % st["id"]]},
            "template": "T-msg", "path": "both", "events": events,
            "compliance": {"review": True, "reasons": ["advertising code"]},
            "v02": {"status": "new", "causes": causes(st)}, "after": prev,
        }
        out.append(screen)
        prev = st["mock"]

    # H01a to H01k
    base = byid.get("H01")
    if base is None:
        raise SystemExit("gen_states: H01 base missing")
    prev = "H01"
    for suffix, state, title, tier, path, hero, extra, branches in VARIANTS:
        s = copy.deepcopy(base)
        for key in ("v02", "after", "events"):
            s.pop(key, None)
        s["id"] = "H01" + suffix
        s["title"] = title
        s["tier"] = tier
        s["path"] = path
        s["frame"] = "phone"
        s["template"] = "T-hub"
        s["compliance"] = {"review": True, "reasons": ["advertising code"]}
        s["purpose"] = "Home for state %s: %s. The hero card and the state card change; the tabs and the community strip stay." % (state, hero[0])
        ui = []
        hero_done = False
        for row in base["ui"]:
            if row[0] == "card" and not hero_done:
                ui.append(["card", hero[0], hero[1]])
                ui.extend(extra)
                hero_done = True
                continue
            if row[0] == "p" and suffix == "i":
                ui.append(["p", "Last updated by you N days ago; connect Account Aggregator to keep this live."])
                continue
            if row[0] == "p" and suffix == "g":
                ui.append(["p", "Read-only since <date>. Refresh stopped."])
                continue
            ui.append(row)
        if not hero_done:
            ui.insert(1, ["card", hero[0], hero[1]])
            ui[2:2] = extra
        s["ui"] = ui
        spec = s["spec"]
        spec["branches"] = spec.get("branches", []) + [b for b in branches if b not in spec.get("branches", [])]
        spec["states"] = ["%s (this variant)" % state]
        spec["logic"] = ["Variant of H01 for state %s (section 5.3); the base logic applies." % state] + [l for l in base["spec"].get("logic", []) if "decided by state" in l]
        if suffix == "h":
            spec["logic"].append("DIFM: no next action from the engine and no in-app upsell; the card reads your adviser manages this (Vatsal, 10 Sep 2026).")
        if suffix == "i":
            spec["logic"].append("S16: numbers typed by the user; the freshness line re-asks for Account Aggregator (Vatsal, 10 Sep 2026).")
        if suffix == "j":
            spec["logic"].append("S18: the Sunday sharpen card schedules the nudge slot N-S18-sunday; the sharpen strip lists the fields entered as bands, never a value the user did not give (Vatsal, 11 Sep 2026).")
        spec["dev"] = ["Hero card and state card come from the state table (N01); nothing else changes between variants."]
        s["events"] = ["state_enter_%s" % state]
        s["v02"] = {"status": "new", "causes": [CAUSE] + VARIANT_CAUSES.get(suffix, [])}
        s["after"] = prev
        out.append(s)
        prev = s["id"]

    # Q05 Update your numbers
    out.append({
        "id": "Q05", "sec": "Q", "title": "Update your numbers", "tier": ["DIY", "DIWM"], "frame": "phone",
        "purpose": "The manual quarterly review for users without Account Aggregator (S16): the fields that move, the capture ladder, and the CAS route again. Mixed users keep their manual number where they locked it.",
        "ui": [
            ["h", "Update your numbers"],
            ["p", "Your plan runs on numbers you typed. Once a quarter I ask for the ones that move; about N minutes."],
            ["rows", [["Monthly take-home", "Rs ___, typed on <date>"], ["Monthly outgoings", "Rs ___, typed"], ["Bank balances and deposits", "Rs ___, typed"], ["Mutual funds", "Rs ___, typed"], ["Stocks and ETFs", "Rs ___, typed"]]],
            ["chips", ["Keep my manual number", "Update"]],
            ["card", "Faster ways", ["Connect Account Aggregator: keeps these live from now on", "Upload your CAS: mutual funds and stocks in one go"]],
            ["btn2", "Connect Account Aggregator", "A05"],
            ["btn2", "Upload my CAS", "A10"],
            ["link", "Edit take-home", "D05a"],
            ["link", "Edit outgoings", "D06a"],
            ["link", "Edit investments", "D02"],
            ["btn", "Rebuild my plan", "H05"],
        ],
        "spec": {
            "fields": [
                {"f": "take_home", "gate": True, "source": "manual", "precision": "exact or approx", "note": "locked manual value stays unless updated here"},
                {"f": "total_outgoings", "gate": True, "source": "manual", "precision": "exact or approx"},
                {"f": "bank_and_deposits", "gate": True, "source": "manual", "precision": "exact or approx"},
                {"f": "mutual_funds", "gate": True, "source": "manual or cas", "precision": "exact or approx"},
                {"f": "stocks", "gate": True, "source": "manual or cas", "precision": "exact or approx"},
            ],
            "logic": [
                "Manual quarterly review for S16 users (Vatsal, 10 Sep 2026): the fields that move, with the capture ladder and A10 again.",
                "Keep my manual number stays for mixed users: a locked manual field is not overwritten by a later Account Aggregator fetch (spec v0.1 A08, kept).",
                "The Account Aggregator re-ask lives here and at G12a (section 5.2, S16).",
                "Rebuild my plan re-runs the engine; H05 shows the diff.",
            ],
            "branches": [["Connect", "A05"], ["CAS", "A10"], ["Take-home", "D05a"], ["Outgoings", "D06a"], ["Investments", "D02"], ["Rebuild", "H05"]],
            "states": ["S16 AA not connected: this is the review", "Mixed sources: AA-fed rows show the fetched value and the manual lock; only typed rows are asked"],
            "dev": ["Runs on the plan anniversary quarter like Q01; the same review_id and diff pipeline.", "Each row links to its single D screen; saving there returns here."],
        },
        "template": "T-review", "path": "manual", "events": ["state_enter_S16"],
        "compliance": {"review": False, "reasons": ["plain copy"]},
        "v02": {"status": "new", "causes": [CAUSE]}, "after": "Q04",
    })
    return out
