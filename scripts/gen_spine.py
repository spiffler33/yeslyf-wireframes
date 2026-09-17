"""Generate the repeated-layout instances of the v0.2 data spine from data/v02/spine.json.

Instances drawn from one contract each (plan_v2.md 4.3 rules, 4.6, appendices B and C; phase 9 of 11 Sep 2026):
  T-num number screens (D05a to D05d, D06a, D06d, D02a to D02j): one question, the Why this one matters link,
  the confirm-or-correct block where a value can arrive prefilled, exact input with readback, fixed band chips,
  the capture ladder for the item, the tri-state chips, hesitation sheets and the silent-autosave exit rule.
  T-tap risk profile questions D08a to D08h (the eight HoA questions verbatim; brief H3).
  T-card relief cards D12a to D12h (section done, N of eight, next section; the adviser-voice line is a copy slot).
  T-sheet hesitation sheets D11a to D11c (copy slots only; D11b reuses the screen's why-this-matters slot).
Every generated screen carries its causes. apply_decisions.py calls generate(doc), applies the phase 9 edit groups,
draws the section strip (spine.json "strip") and places the screens by data/v02/flow.json.
"""

CAUSE = "Vatsal, 10 Sep 2026"
CAUSE_P9 = "Vatsal, 11 Sep 2026"  # phase 9: no client-data assumptions, data-capture improvements
CAUSE_FWD = "Vatsal, 17 Sep 2026"  # mandatory and optional inputs: the Moving forward block and the field tags
SHEET_TARGETS = {"aa": "A05", "cas": "A10", "vault": "H06"}
EXIT_RULE = "Exit (rule 12): silent autosave with a Saved toast; no sheet (Vatsal, 11 Sep 2026)"


def why_link(sid):
    return ["link", "Why this one matters", sid]


def why_logic(sid):
    return ("Why this one matters (Vatsal, 11 Sep 2026): a collapsed in-place link under the question; copy slot W-%s "
            "(content is gap G08); D11b at 90 seconds reuses the same slot." % sid)


def num_screen(item, doc):
    bands = doc["bands"]
    sid = item["id"]
    prefill = item.get("prefill")
    parent = item.get("multi_parent")
    ui = [["h", item["question"]]]
    if item.get("hint"):
        ui.append(["p", item["hint"]])
    ui.append(why_link(sid))
    if prefill:
        lines = ["Rs ___, shown with its source tag"]
        if item.get("suggestion"):
            lines.append(item["suggestion"])
        ui.append(["card", "Prefilled from " + prefill, lines])
        ui.append(["btn", "That's about right", item["next"]])
        ui.append(["link", "Change it", sid])
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
                       "precision": "exact | approx | unknown", "note": item["mode"], "forward": "optional"})
    logic = [
        "%s (rule 3): %s" % (item["mode"].capitalize(), "the exact input leads; the bands sit under it" if item["mode"] == "exact-first" else "the bands lead; the exact input stays visible"),
        "Band rule (rule 3; Vatsal, 11 Sep 2026): fixed bands for this field from the M2 tables 9.1 to 9.5 where a table exists, else Rs ___ placeholder chips; a tapped band fills the exact field with the midpoint and tags the value approx; typing an exact number removes the tag. Dynamic bands are shelved until the data flywheel exists.",
        "Tri-state (rule 6): value, explicit none (the %s chip) or not sure (skip). Not sure is never stored as zero." % item.get("none", "None"),
        "Gate (rule 7; Vatsal, 11 Sep 2026): %s The plan builds when every field the React reads is a value (exact or band) or explicit none; a not-sure here is asked for as a quick range on D13 before the build, never filled from L02." % ("gate field (appendix B)." if any(f in doc["gate_fields"] for f in item["fields"]) else "sharpen field (appendix B); %s shows a Sharpen this link for it." % ", ".join(item.get("sharpen_in", ["the plan"]))),
        "Capture ladder (rule 8): the sources drawn under the input, in the order they apply to this item (appendix C).",
        why_logic(sid),
    ]
    if prefill:
        logic.append("Confirm or correct (Vatsal, 11 Sep 2026): when the value arrives prefilled, from %s, the primary button reads That's about right and stores the value with its source tag; Change it reveals the exact input in place; the derivation reads from what you told me earlier, never as an estimate." % prefill)
    if parent:
        logic.append("Opens only when its type is ticked on %s (Vatsal, 11 Sep 2026); an unticked type is stored as explicit none without opening this screen; Continue goes to the next ticked type, and after the last one to %s." % (parent, doc["multi_after"][parent]))
    if item.get("plausibility"):
        logic.append("Plausibility (rule 4): %s; a mismatch prompts a check, never a block." % item["plausibility"])
    logic.extend(item.get("logic", []))
    gate_names = [f["f"] for f in fields if f["gate"]]
    sharpen_names = [f["f"] for f in fields if not f["gate"]]
    forward = [
        "Continue is always enabled: an exact amount, a band, the %s chip or Not sure yet, skip all move on; a band or chip tap may auto-advance (rule 2)." % item.get("none", "None"),
        "Required: nothing on this screen; the spine never blocks on a number (Vatsal, 17 Sep 2026).",
    ]
    if gate_names:
        forward.append("Optional, gate: %s; left not sure, D10 lists it and D13 takes a range before the plan builds (rule 7)." % ", ".join(gate_names))
    if sharpen_names:
        forward.append("Optional, sharpen: %s; left not sure, it becomes a Sharpen this link in the plan section that reads it." % ", ".join(sharpen_names))
    branches = [["Continue", item["next"]], ["Skip", item["next"]]]
    for key in ("aa", "cas", "vault"):
        if any(step[0] == key for step in item["ladder"]):
            branches.append([{"aa": "Connect AA", "cas": "Upload CAS", "vault": "Vault"}[key], SHEET_TARGETS[key]])
    states = []
    if item.get("aa"):
        states.append("AA-fed: value prefilled and tagged AA-fed; a manual override locks the field against refresh (spec v0.1 A08)")
    if item.get("cas"):
        states.append("CAS-verified: holdings parsed from the CAS (A10c) fill the value and tag it CAS-verified")
    if prefill:
        states.append("Prefilled: the value shows with its source tag; the primary button reads That's about right; Change it reveals the input")
    states.append("Manual: field empty; the ladder and the bands do the work")
    if parent:
        states.append("Type not ticked on %s: this screen does not open; the field is explicit none" % parent)
        if item.get("aa"):
            states.append("Fetch failed for this type: the %s row reads fetch failed, upload a statement or type it; this screen opens with the ladder" % parent)
    states.append("Hesitation (rule 5): D11a at 45 seconds, D11b at 90 seconds, D11c at 120 seconds or on a second return")
    states.append(EXIT_RULE)
    states.extend(item.get("states", []))
    dev = [
        "Readback in words, per-month / per-year toggle where the field can be either, L and Cr quick multipliers, numeric keypad (rule 4).",
        "Store source (aa, cas, manual) and precision (exact, approx, unknown) per field (rule 9); the only default the plan takes is the work-optional age accepted on D07b, tagged default accepted (Vatsal, 11 Sep 2026); M2's COALESCE(exact, band, 0) is superseded for not-sure fields.",
    ]
    dev.extend(item.get("dev", []))
    return {
        "id": sid, "sec": "D", "title": item["title"], "tier": ["ALL"], "frame": "phone",
        "purpose": item["purpose"], "ui": ui,
        "spec": {"fields": fields, "forward": forward, "logic": logic, "branches": branches, "states": states, "dev": dev, "ladder": ladder},
        "template": "T-num", "path": "both", "events": [],
        "compliance": {"review": False, "reasons": ["plain copy"]},
        "v02": {"status": "new", "causes": [CAUSE, CAUSE_P9, CAUSE_FWD] + item.get("causes", [])},
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
            "spec": {"fields": [{"f": "rpq_answers", "gate": True, "source": "manual", "precision": "exact", "note": "answer %d of 8" % (i + 1), "forward": "required"}],
                     "forward": ["Next is enabled once an option is chosen; the tap auto-advances.",
                                 "Required: the answer (SEBI suitability; no fallback and no skip, appendix B).",
                                 "Optional: nothing."],
                     "logic": logic, "branches": [["Next", nxt]],
                     "states": ["Retake from D09 or Settings: answers prefilled, any can change", EXIT_RULE],
                     "dev": ["Store the answer with the questionnaire version; to be verified: the RPQ scoring map (gap G06)."]},
            "template": "T-tap", "path": "both", "events": [],
            "compliance": {"review": True, "reasons": ["advice language"]},
            "v02": {"status": "new", "causes": ["brief H3", CAUSE, CAUSE_P9, CAUSE_FWD]},
        })
    return out


def relief_screens(doc):
    """D12a to D12h: the relief card after each spine section (section relief, Vatsal, 11 Sep 2026)."""
    out = []
    secs = doc["sections"]
    for k, sec in enumerate(secs):
        sid = sec["insight"]
        nxt = sec["next_after_insight"]
        next_label = secs[k + 1]["label"] if k + 1 < len(secs) else "review and build"
        out.append({
            "id": sid, "sec": "D", "title": "Relief card: %s" % sec["label"], "tier": ["ALL"], "frame": "phone",
            "purpose": "The relief card after the last %s screen: section done, N of eight, what comes next and how long; keep going or set a reminder. The adviser-voice line on the card is a copy slot (rule 10, gap G08)." % sec["label"],
            "ui": [["card", "%s done" % sec["label"].capitalize(),
                    ["%d of eight sections." % (k + 1), "Next: %s, about N minutes." % next_label,
                     "Copy slot %s: one line in the adviser voice about your %s, chosen by the answers; no numbers (gap G08)" % (sid, sec["label"])]],
                   ["btn", "Keep going", nxt],
                   ["link", "Remind me later", "O03"]],
            "spec": {"fields": [],
                     "logic": ["Relief card (section relief, Vatsal, 11 Sep 2026): fires once after the last %s screen; it shows the section done, N of eight sections, and the next section with its minutes; two chips: Keep going opens the next section, Remind me later opens O03, the reminder picker." % sec["label"],
                               "The adviser-voice line (rule 10, V5 Stage 3) is a copy slot on the card, picked by the answers; explicit none and not sure pick different lines (rule 6); copy is content (gap G08)."],
                     "branches": [["Keep going", nxt], ["Remind me later", "O03"]],
                     "states": ["Section left incomplete: the card does not fire; it fires when the section completes later",
                                "Remind me later: O03 opens over this card; Set it and exit lands on O02", EXIT_RULE],
                     "dev": ["Slot id %s; variants keyed by the section's answers. Sections done counts completed sections, not screens." % sid]},
            "template": "T-card", "path": "both", "events": [],
            "compliance": {"review": True, "reasons": ["advice language"]},
            "v02": {"status": "new", "causes": [CAUSE, "V5 Stage 3", CAUSE_P9]},
        })
    return out


def hesitation_screens(doc):
    out = []
    for sid, seconds, title, slot_line in doc["hesitation"]:
        note = "Copy slot %s: %s (gap G08)" % (sid, slot_line)
        logic = ["Hesitation detection (rule 5, V5 Stage 3): shown over the current number screen at %d seconds%s." % (seconds, " or on a second return" if sid == "D11c" else ""),
                 "Keep going dismisses the sheet in place; the screen under it keeps its state.",
                 "Not sure yet, skip sets not sure on the field under the sheet in place and advances to that screen's Continue target."]
        causes = [CAUSE, "V5 Stage 3"]
        if sid == "D11b":
            note = "Copy slot %s: reuses the Why this one matters slot of the screen under the sheet (W-<screen>), the same line the link under the question shows from the start (gap G08)" % sid
            logic.append("Reuses the screen's why-this-matters slot (Vatsal, 11 Sep 2026): one copy slot per screen serves the link under the question and this sheet.")
            causes.append(CAUSE_P9)
        out.append({
            "id": sid, "sec": "D", "title": "%s (%d seconds)" % (title, seconds), "tier": ["ALL"], "frame": "phone",
            "purpose": "Hesitation sheet over any number screen at %d seconds. Copy slot only." % seconds,
            "ui": [["h", title], ["note", note],
                   ["btn", "Keep going", sid], ["link", "Not sure yet, skip", sid]],
            "spec": {"fields": [], "logic": logic,
                     "branches": [], "states": ["Fires at most once per screen per session"],
                     "dev": ["Slot id %s; timer per screen; events <screen>_hesitation_%d." % (sid, seconds)]},
            "template": "T-sheet", "path": "both", "events": [],
            "compliance": {"review": False, "reasons": ["plain copy"]},
            "v02": {"status": "new", "causes": causes},
        })
    return out


def generate(doc):
    out = [num_screen(item, doc) for item in doc["num_screens"]]
    out += rpq_screens(doc)
    out += relief_screens(doc)
    out += hesitation_screens(doc)
    return out
