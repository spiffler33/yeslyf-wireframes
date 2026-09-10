"""Generate the repeated-layout instances of the v0.2 data spine from data/v02/spine.json.

Instances drawn from one contract each (plan_v2.md 4.3 rules, 4.6, appendices B and C):
  T-num number screens (D05a to D05d, D06a, D06d, D02a to D02j): one question, exact input with readback,
  band chips, the capture ladder for the item, the tri-state chips, hesitation sheets and the exit rule.
  T-tap risk profile questions D08a to D08h (the eight HoA questions verbatim; brief H3).
  T-card section insight cards D12a to D12h (copy slots only; V5 Stage 3, gap G08).
  T-sheet hesitation sheets D11a to D11c (copy slots only; V5 Stage 3).
Every generated screen carries its cause. apply_decisions.py calls generate(doc) and places the screens
by data/v02/flow.json.
"""

CAUSE = "Vatsal, 10 Sep 2026"
SHEET_TARGETS = {"aa": "A05", "cas": "A10", "vault": "H06"}


def num_screen(item, doc):
    bands = doc["bands"]
    ui = [["h", item["question"]]]
    if item.get("hint"):
        ui.append(["p", item["hint"]])
    if item.get("suggestion"):
        ui.append(["note", item["suggestion"]])
    ui.append(["in", item.get("input_label", "Rs ___, exact")])
    if item.get("period_toggle"):
        ui.append(["tabs", ["Per month", "Per year"]])
    ui.append(["note", "Reads back in words as you type: " + item.get("readback", "seventeen and a half lakh a year, about Rs 1.46 L a month")])
    if item["mode"] == "band-first":
        ui.append(["p", bands["caption_band_first"]])
    else:
        ui.append(["p", bands["caption_exact_first"]])
    ui.append(["chips", bands["chips"]])
    ui.append(["p", "Easier ways to get this number:"])
    ladder = []
    for step in item["ladder"]:
        key, label, text = step[0], step[1], step[2]
        target = SHEET_TARGETS.get(key)
        if target and key != "vault":
            ui.append(["link", label, target])
        elif key == "vault":
            ui.append(["link", label, "H06"])
        else:
            ui.append(["note", label + ": " + text])
        ladder.append([key, label + ": " + text])
    tri = [item.get("none", "None"), "Not sure yet, skip"]
    ui.append(["chips", tri])
    ui.append(["btn", "Continue", item["next"]])

    fields = []
    for f in item["fields"]:
        fields.append({"f": f, "gate": f in doc["gate_fields"], "source": item.get("sources", "manual"),
                       "precision": "exact | approx | unknown", "note": item["mode"]})
    logic = [
        "%s (rule 3): %s" % (item["mode"].capitalize(), "the exact input leads; the bands sit under it" if item["mode"] == "exact-first" else "the bands lead; the exact input stays visible"),
        "Band rule (V5): a tapped band fills the exact field with the midpoint for your income tier (L02) and tags the value approx; typing an exact number removes the tag.",
        "Tri-state (rule 6): value, explicit none (the %s chip) or not sure (skip). Not sure is never stored as zero." % item.get("none", "None"),
        "Gate (rule 7): %s" % ("this field gates the plan build; the plan builds when it is a value or explicit none." if any(f in doc["gate_fields"] for f in item["fields"]) else "sharpen field; the plan builds without it and %s shows a Sharpen this link." % ", ".join(item.get("sharpen_in", ["the plan"]))),
        "Capture ladder (rule 8): the sources drawn under the input, in the order they apply to this item (appendix C).",
    ]
    if item.get("plausibility"):
        logic.append("Plausibility (rule 4): %s; a mismatch prompts a check, never a block." % item["plausibility"])
    logic.extend(item.get("logic", []))
    branches = [["Continue", item["next"]], ["Skip", item["next"]]]
    for key in ("aa", "cas", "vault"):
        if any(step[0] == key for step in item["ladder"]):
            branches.append([{"aa": "Connect AA", "cas": "Upload CAS", "vault": "Vault"}[key], SHEET_TARGETS[key]])
    states = []
    if item.get("aa"):
        states.append("AA-fed: value prefilled and tagged AA-fed; a manual override locks the field against refresh (spec v0.1 A08)")
    if item.get("cas"):
        states.append("CAS-verified: holdings parsed from the CAS (A10c) fill the value and tag it CAS-verified")
    states.append("Manual: field empty; the ladder and the bands do the work")
    states.append("Hesitation (rule 5): D11a at 45 seconds, D11b at 90 seconds, D11c at 120 seconds or on a second return")
    states.append("Exit (rule 12): autosave, then O03 asks when the user will finish")
    states.extend(item.get("states", []))
    dev = [
        "Readback in words, per-month / per-year toggle where the field can be either, L and Cr quick multipliers, numeric keypad (rule 4).",
        "Store source (aa, cas, manual, assumed) and precision (exact, approx, unknown) per field (rule 9); M2's COALESCE(exact, band, 0) is superseded for not-sure fields.",
    ]
    dev.extend(item.get("dev", []))
    return {
        "id": item["id"], "sec": "D", "title": item["title"], "tier": ["ALL"], "frame": "phone",
        "purpose": item["purpose"], "ui": ui,
        "spec": {"fields": fields, "logic": logic, "branches": branches, "states": states, "dev": dev, "ladder": ladder},
        "template": "T-num", "path": "both", "events": [],
        "compliance": {"review": False, "reasons": ["plain copy"]},
        "v02": {"status": "new", "causes": [CAUSE] + item.get("causes", [])},
    }


def rpq_screens(doc):
    out = []
    qs = doc["rpq"]["questions"]
    for i, q in enumerate(qs):
        nxt = qs[i + 1]["id"] if i + 1 < len(qs) else doc["rpq"]["next_after"]
        ui = [["p", "Question %d of 8. SEBI requires this, and it decides how much of your money goes into equity." % (i + 1)], ["h", q["text"]]]
        if q.get("table"):
            ui.append(["table", q["table"][0], q["table"][1]])
        ui.append(["radio", q["options"]])
        ui.append(["btn", "Next", nxt])
        logic = ["Question %d of the eight HoA questions, verbatim from the questionnaire (brief H3); a tap auto-advances." % (i + 1),
                 "Band from the score once all eight are answered (D09); no fallback: SEBI suitability, which is why the profile sits early in the spine (rule 1)."]
        logic.extend(q.get("logic", []))
        out.append({
            "id": q["id"], "sec": "D", "title": "Risk profile question %d" % (i + 1), "tier": ["ALL"], "frame": "phone",
            "purpose": "Risk profile question %d of 8: %s." % (i + 1, q["topic"]),
            "ui": ui,
            "spec": {"fields": [{"f": "rpq_answers", "gate": True, "source": "manual", "precision": "exact", "note": "answer %d of 8" % (i + 1)}],
                     "logic": logic, "branches": [["Next", nxt]],
                     "states": ["Retake from D09 or Settings: answers prefilled, any can change", "Exit (rule 12): autosave, then O03"],
                     "dev": ["Store the answer with the questionnaire version; to be verified: the RPQ scoring map (gap G06)."]},
            "template": "T-tap", "path": "both", "events": [],
            "compliance": {"review": True, "reasons": ["advice language"]},
            "v02": {"status": "new", "causes": ["brief H3", CAUSE]},
        })
    return out


def insight_screens(doc):
    out = []
    for sec in doc["sections"]:
        sid = sec["insight"]
        out.append({
            "id": sid, "sec": "D", "title": "Section insight: %s" % sec["label"], "tier": ["ALL"], "frame": "phone",
            "purpose": "One card in the adviser voice after the last %s screen, chosen by the answers, no numbers. Copy slot only." % sec["label"],
            "ui": [["card", "Copy slot %s" % sid, ["One line in the adviser voice about your %s, chosen by the answers; no numbers (gap G08)" % sec["label"]]],
                   ["btn", "Continue", sec["next_after_insight"]]],
            "spec": {"fields": [], "logic": ["Section micro-feedback (rule 10, V5 Stage 3): fires once after the last screen of the %s section; the line is picked by the answers; explicit none and not sure pick different lines (rule 6)." % sec["label"],
                                             "Copy is content (gap G08); this screen holds the slot."],
                     "branches": [["Continue", sec["next_after_insight"]]],
                     "states": ["Section left incomplete: the card does not fire; it fires when the section completes later"],
                     "dev": ["Slot id %s; variants keyed by the section's answers." % sid]},
            "template": "T-card", "path": "both", "events": [],
            "compliance": {"review": True, "reasons": ["advice language"]},
            "v02": {"status": "new", "causes": [CAUSE, "V5 Stage 3"]},
        })
    return out


def hesitation_screens(doc):
    out = []
    for sid, seconds, title, slot_line in doc["hesitation"]:
        out.append({
            "id": sid, "sec": "D", "title": "%s (%d seconds)" % (title, seconds), "tier": ["ALL"], "frame": "phone",
            "purpose": "Hesitation sheet over any number screen at %d seconds. Copy slot only." % seconds,
            "ui": [["h", title], ["note", "Copy slot %s: %s (gap G08)" % (sid, slot_line)],
                   ["btn", "Keep going", sid], ["link", "Not sure yet, skip", sid]],
            "spec": {"fields": [], "logic": ["Hesitation detection (rule 5, V5 Stage 3): shown over the current number screen at %d seconds%s." % (seconds, " or on a second return" if sid == "D11c" else ""),
                                             "Keep going dismisses the sheet in place; the screen under it keeps its state.",
                                             "Not sure yet, skip sets not sure on the field under the sheet in place and advances to that screen's Continue target."],
                     "branches": [], "states": ["Fires at most once per screen per session"],
                     "dev": ["Slot id %s; timer per screen; events <screen>_hesitation_%d." % (sid, seconds)]},
            "template": "T-sheet", "path": "both", "events": [],
            "compliance": {"review": False, "reasons": ["plain copy"]},
            "v02": {"status": "new", "causes": [CAUSE, "V5 Stage 3"]},
        })
    return out


def generate(doc):
    out = [num_screen(item, doc) for item in doc["num_screens"]]
    out += rpq_screens(doc)
    out += insight_screens(doc)
    out += hesitation_screens(doc)
    return out
