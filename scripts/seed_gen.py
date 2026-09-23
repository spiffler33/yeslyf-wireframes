#!/usr/bin/env python3
"""The yeslyf seed: synthetic people for the staff side (PLAN_admin_seed_v01.md, phase A).

Reads seed/config.json (every count, ratio and rule, each with its cause), seed/names.json and the board data
(data/screens_v02.json, data/v02/states.json, data/admin_crm.json, data/events_extra.json, data/integrations.json)
and writes data/seed/<run>/: one JSON per table keyed by person_id, events.jsonl and report.md. Standard library
only, no network; the output is fixed by the seed and the anchor date.

    python3 scripts/seed_gen.py                       both runs, anchor = the run date
    python3 scripts/seed_gen.py --run run-500         one run
    python3 scripts/seed_gen.py --anchor 2026-09-23   a fixed anchor; every date is relative to it

State is never an input label. The generator writes timestamped flags (state_flags.json); the resolver derives
the single state and the state_enter history from them with the precedence in the config (N01; plan section 7),
and the report lists every person for whom more than one predicate holds (the N01 gap list). No text is parsed:
ladder offsets, exits and event names are looked up by exact keys.
"""

import argparse
import collections
import datetime as dt
import json
import math
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))


# ---------------------------------------------------------------- small helpers

def load(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return json.load(f)


def DAYS(x):
    return dt.timedelta(days=x)


def HOURS(x):
    return dt.timedelta(hours=x)


def MINS(x):
    return dt.timedelta(minutes=x)


def SECS(x):
    return dt.timedelta(seconds=x)


def iso(t):
    return t.isoformat(timespec="seconds") if t is not None else None


def ymd(t):
    return t.date().isoformat() if t is not None else None


def days_between(a, b):
    return (b - a).total_seconds() / 86400.0


def pick(r, weights):
    items = list(weights.items()) if isinstance(weights, dict) else list(weights)
    total = float(sum(w for _, w in items))
    x = r.random() * total
    for k, w in items:
        x -= w
        if x < 0:
            return k
    return items[-1][0]


def exp_median(r, median, cap):
    mean = median / math.log(2)
    for _ in range(60):
        v = r.expovariate(1.0 / mean)
        if v <= cap:
            return v
    return r.uniform(0, cap)


def uni(r, pair):
    return r.uniform(pair[0], pair[1])


def clamp(x, lo, hi):
    return lo if x < lo else hi if x > hi else x


def rhu(x):
    return int(math.floor(x + 0.5))


def rnd(x, step):
    return int(step * math.floor(x / float(step) + 0.5))


def largest_remainder(n, weights):
    keys = list(weights)
    total = float(sum(weights.values()))
    raw = dict((k, n * weights[k] / total) for k in keys)
    out = dict((k, int(math.floor(raw[k]))) for k in keys)
    left = n - sum(out.values())
    order = sorted(keys, key=lambda k: (-(raw[k] - out[k]), keys.index(k)))
    for k in order[:left]:
        out[k] += 1
    return out


def band_index(v, bounds):
    i = 0
    for j, b in enumerate(bounds):
        if v >= b:
            i = j
    return i


def band_mid(bounds, i):
    if i + 1 < len(bounds):
        return (bounds[i] + bounds[i + 1]) / 2.0
    return bounds[i] * 1.5


def isin_check(body):
    digits = "".join(str(int(ch, 36)) for ch in body)
    total = 0
    for k, ch in enumerate(reversed(digits)):
        d = int(ch)
        if k % 2 == 0:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return body + str((10 - total % 10) % 10)


# ---------------------------------------------------------------- what is coded by hand (never parsed)

# admin_crm.json EVENTS, row by row: the names in each row's first cell and its screen (checked by equality).
CRM_EVENTS = [
    (("signed_up",), "A03"), (("reveal_seen",), "R09"), (("paywall_viewed",), "P01"), (("esign_done",), "P03"),
    (("paid",), "P05"), (("aa_connected", "aa_declined", "aa_failed"), "A06 to A09"),
    (("data_progress",), "D01 to D09"), (("data_complete",), "D10"), (("plan_built",), "G01"),
    (("plan_read",), "G03"), (("pdf_downloaded",), "G10"), (("call_booked", "call_completed", "no_show"), "K01 to K03"),
    (("action_done",), "E06"), (("plan_updated",), "H05"), (("update_accepted",), "H05"),
    (("review_due", "review_done"), "Q01"), (("payment_failed", "payment_recovered"), "Q03"),
    (("cancelled", "lapsed", "resubscribed"), "Q03"), (("rpq_due", "agreement_due"), "Q04"),
    (("ticket_created",), "H07"),
]
CRM_NAMES = set(n for names, _ in CRM_EVENTS for n in names)

# states.json exit lines coded by hand. PREV = "the previous state". An overlay state is entered from any state
# when its trigger fires (a call booked, a payment failing, a publish, a request); leaving it goes wherever the
# flags then say, which the exits call the previous state.
EXITS = {
    "S1": {"S2"}, "S2": {"S2b", "S2c", "S3"}, "S2b": {"S2c"}, "S2c": {"S3"},
    "S3": {"S4", "S5", "S19"}, "S4": {"S5", "S19"}, "S5": {"S6", "S18"}, "S6": {"S8", "S7"},
    "S7": {"S21", "PREV"}, "S8": {"S9"}, "S9": {"S10", "S11"}, "S10": {"S11", "S22"}, "S11": {"S8", "S9", "S10"},
    "S12": {"PREV", "S13"}, "S13": {"S8", "S9"}, "S14": set(), "S15": {"PREV", "S16"}, "S17": {"S4", "S5"},
    "S18": {"S8", "S9"}, "S19": {"S5"}, "S20": {"S7"}, "S21": {"S9"}, "S22": {"S8", "S9", "S10"},
    "S23": {"PREV"}, "S24": {"S13"}, "S25": set(),
}
OVERLAY_ENTRY = {"S7", "S11", "S12", "S13", "S15", "S17", "S20", "S21", "S22", "S23", "S24", "S25"}

D02_TYPES = [("D02a", ["bank_and_deposits"]), ("D02b", ["mutual_funds"]), ("D02c", ["stocks"]), ("D02d", ["nps"]),
             ("D02e", ["epf"]), ("D02f", ["ppf"]), ("D02g", ["gold"]),
             ("D02h", ["home_value", "investment_property_value", "investment_property_rent"]),
             ("D02i", ["ulip_surrender_value", "ulip_premium", "ulip_years_completed"]), ("D02j", ["other_assets"])]
ASSETS = ["bank_and_deposits", "mutual_funds", "stocks", "nps", "epf", "ppf", "gold", "ulip_surrender_value",
          "other_assets"]
KIND_OF_PRECISION = {"exact": "exact", "approx": "band", "unknown": "not_sure"}
PRECISION_OF_KIND = {"exact": "exact", "band": "approx", "none": "exact", "not_sure": "unknown", "default": "exact"}
AA_FIELDS = {"bank_and_deposits": "banks", "mutual_funds": "mf", "stocks": "demat", "nps": "nps", "current_sip": "banks"}
SHARPEN_SCREEN = {"partner_take_home": "G06", "rental_income": "G06", "other_income": "G06", "bucket_fixed": "G06",
                  "bucket_variable": "G06", "bucket_guilt_free": "G06", "current_sip": "G06", "take_home": "G03",
                  "total_outgoings": "G04", "bank_and_deposits": "G04", "mutual_funds": "G03", "stocks": "G03",
                  "epf": "G09", "nps": "G09", "ppf": "G09", "gold": "G11", "home_value": "G03",
                  "investment_property_value": "G09", "ulip_surrender_value": "G03", "ulip_premium": "G03",
                  "ulip_years_completed": "G05", "other_assets": "G09", "term_sum_assured": "G05",
                  "health_sum_insured": "G05", "other_policies": "G05"}
STATE_H01 = {"S6": "H01a", "S8": "H01b", "S9": "H01c", "S10": "H01d", "S11": "H01e", "S12": "H01f", "S13": "H01g",
             "S14": "H01h", "S16": "H01i", "S18": "H01j", "S22": "H01k"}


# ---------------------------------------------------------------- the board and the config

class Board:
    def __init__(self):
        sc = load("data/screens_v02.json")
        self.S = dict((s["id"], s) for s in sc["screens"])
        self.live = set(i for i, s in self.S.items() if s["v02"].get("status") not in ("dropped", "split"))
        st = load("data/v02/states.json")
        self.states = dict((s["id"], s) for s in st["states"])
        self.crm_rows = load("data/admin_crm.json")["EVENTS"]
        self.integ = dict((r["id"], r) for r in load("data/integrations.json")["rows"])
        table = [row for row in self.S["N04"]["ui"] if row[0] == "table"][0]
        self.templates = dict((row[0], {"channel": row[1], "state": row[2], "link": row[3], "text": row[4]})
                              for row in table[2])
        self.extra = load("data/events_extra.json")
        self.screen_events = dict((i, set(self.S[i]["events"])) for i in self.live)
        known = set()
        for i in self.live:
            known |= self.screen_events[i]
        known |= CRM_NAMES
        known |= set(e["name"] for e in self.extra["events"])
        self.known_events = known

    def lands(self, sid):
        return self.states[sid]["lands_on"]


def check_inputs(cfg, B):
    errs = []
    for i, (names, screen) in enumerate(CRM_EVENTS):
        row = B.crm_rows[i] if i < len(B.crm_rows) else None
        if row is None or row[0] != " / ".join(names) or row[1] != screen:
            errs.append("admin_crm EVENTS row %d differs from the coded list" % i)
    if len(B.crm_rows) != len(CRM_EVENTS):
        errs.append("admin_crm EVENTS has %d rows, the coded list %d" % (len(B.crm_rows), len(CRM_EVENTS)))
    slots = set(l["slot"] for s in B.states.values() for l in s["ladder"])
    for s in sorted(slots - set(cfg["nudges"]["offsets"])):
        errs.append("ladder slot %s has no offset in the config" % s)
    for f, c in cfg["fields"]["list"].items():
        spec = [x for x in B.S[c["screen"]]["spec"]["fields"] if isinstance(x, dict) and x.get("f") == f]
        if not spec:
            errs.append("field %s is not on %s" % (f, c["screen"]))
            continue
        if bool(spec[0].get("gate")) != bool(c["gate"]):
            errs.append("field %s: gate differs from the spec" % f)
        if "precision" in c and " | ".join(c["precision"]) != spec[0].get("precision"):
            errs.append("field %s: precision differs from the spec" % f)
    for k, v in cfg["integrations"]["vendors"].items():
        if v["row"] not in B.integ:
            errs.append("vendor %s: row %s missing" % (k, v["row"]))
    for s in cfg["precedence"]["order"]:
        if s not in B.states:
            errs.append("precedence names %s, not in states.json" % s)
    if set(B.states) - set(cfg["precedence"]["order"]) - {"S16"}:
        errs.append("states missing from the precedence: %s" % sorted(set(B.states) - set(cfg["precedence"]["order"])))
    return errs


class Ctx:
    def __init__(self, cfg, board, names, anchor, run):
        self.cfg, self.B, self.names, self.run = cfg, board, names, run
        clock = cfg["anchor_clock"]["time"].split(":")
        self.A = dt.datetime(anchor.year, anchor.month, anchor.day, int(clock[0]), int(clock[1]), tzinfo=IST)
        self.seed = cfg["seed"]["value"]
        self.tm = cfg["time_model"]
        self.tx = cfg["time_extras"]
        self.fields = cfg["fields"]["list"]
        self.hours = [(int(k), v) for k, v in self.tx["hours_ist"].items()]
        self.window_start = self.A - DAYS(self.tm["window_days"])
        self.vendors = cfg["integrations"]["vendors"]
        self.bands = cfg["bands"]["ladders_rs"]
        self.publishes = sorted(
            [dict(p, at=self.A - DAYS(p["days_before_anchor"])) for p in cfg["publishes"]["list"]],
            key=lambda x: x["at"])
        self.react = set(f for f, c in self.fields.items() if c["react"])
        self.gate = set(f for f, c in self.fields.items() if c["gate"])
        self.prec_order = cfg["precedence"]["order"]
        self.staff = cfg["staff"]["list"]
        self.advisers = [s["staff_id"] for s in self.staff if "call_centre" in s["roles"]]
        self.master = make_master(cfg)

    # waking-hours time helpers
    def hour(self, r):
        return pick(r, self.hours)

    def at_day(self, r, days_ago):
        t = self.A - DAYS(days_ago)
        t = t.replace(hour=self.hour(r), minute=r.randint(0, 59), second=r.randint(0, 59), microsecond=0)
        if t >= self.A:
            t = self.A - MINS(r.randint(20, 400))
        return t


def make_master(cfg):
    h = cfg["holdings"]
    cats = ["Flexi Cap", "Large Cap", "Mid Cap", "Small Cap", "ELSS", "Liquid", "Short Duration", "Hybrid",
            "Index Nifty 50", "Gilt"]
    mf = [{"isin": isin_check("INFSD%06d" % i), "name": "Seed %s Fund %02d Direct Growth" % (cats[i % len(cats)], i),
           "kind": "mf"} for i in range(1, h["master_mf"] + 1)]
    st = [{"isin": isin_check("INESD%06d" % i), "name": "Seed Industries %02d Ltd" % i, "kind": "stock"}
          for i in range(1, h["master_stocks"] + 1)]
    return {"mf": mf, "stock": st}


# ---------------------------------------------------------------- the person

class Person:
    def __init__(self, ctx, idx, spec):
        self.idx = idx
        self.r = random.Random("%s:%s:p%d" % (ctx.seed, ctx.run, idx))
        self.layer = spec["layer"]
        self.target = spec.get("target")
        self.base = spec.get("base", self.target)
        self.tier = spec.get("tier")
        self.path = spec.get("path")
        self.flags = set(spec.get("flags", ()))
        self.is_topup = bool(spec.get("is_topup"))
        self.a05 = spec.get("a05", True)
        self.pid = None
        self.tl = {}
        self.T = {}
        self.dec = {}
        self.loans = []
        self.goals = []
        self.rpq = None
        self.events = []
        self.seq = 0
        self.fed = {}
        self.holdings = []
        self.consents = []
        self.cas = []
        self.plans = []
        self.actions = []
        self.calls = []
        self.subs = []
        self.payments = []
        self.alc = []
        self.tickets = []
        self.ops = []
        self.integ = []
        self.tasks = []
        self.nudges = []
        self.updates = []
        self.failures = []
        self.reviews = []
        self.annual = []
        self.o03 = []
        self.missed_sips = []
        self.verified_actions = []
        self.difm_reviews = []
        self.sharpen_items = []
        self.version_requests = []
        self.email = None
        self.email_known_at = None
        self.pan = None
        self.landing = None
        self.last_screen = None
        self.stop_reason = None
        self.force_band = None
        self.force_not_sure = None
        self.prospect = None
        self.plausibility_flag = False
        self.engine_failure = "engine_failure" in self.flags

    def ev(self, t, name, screen=None, **props):
        self.seq += 1
        self.events.append([t, self.seq, name, screen, props])

    def sev(self, ctx, t, sid, suffix, **props):
        """A screen's own event (<id>_<suffix>), emitted only when the screen lists it."""
        name = sid + "_" + suffix
        if name in ctx.B.screen_events[sid]:
            self.ev(t, name, sid, **props)
            return True
        return False

    def nev(self, ctx, t, sid, name, **props):
        """A named event a screen lists as it is (sharpen_opened, call_no_show, mandate_active)."""
        if name in ctx.B.screen_events[sid]:
            self.ev(t, name, sid, **props)
            return True
        return False

    def view(self, ctx, t, sid, **props):
        self.ev(t, sid + "_view", sid, **props)
        return t

    def integ_call(self, ctx, t, vendor, call, outcome=None, detail=None):
        v = ctx.vendors[vendor]
        r = self.r
        if outcome is None:
            x = r.random()
            outcome = "timeout" if x < v["timeout"] else "failed" if x < v["timeout"] + v["fail"] else "ok"
        lat = int(uni(r, v["latency_ms"]) * (3 if outcome == "timeout" else 1))
        self.integ.append({"vendor": vendor, "integration": v["row"], "call": call, "outcome": outcome,
                           "latency_ms": lat, "at": t, "detail": detail})
        return outcome


# ---------------------------------------------------------------- population plan

def plan_population(ctx, R):
    cfg = ctx.cfg
    rc = cfg["runs"][ctx.run]
    L = rc["layers"]
    floor = rc["paid_floor"]
    scale = rc["ugly_scale"]
    cases = cfg["ugly_cases"]["cases"]
    ugly = dict((k, max(1, rhu(v["count"] * scale))) for k, v in cases.items())
    ugly["difm_prospect_manual"] = max(1, rhu(cfg["ugly_cases"]["difm_prospect_manual"]["count"] * scale))
    W = cfg["paid_state_weights"]["weights"]
    natural = largest_remainder(L["paid"], W)
    alloc = dict(natural)
    topup = dict((s, 0) for s in W)
    for s in W:
        if alloc[s] < floor:
            topup[s] += floor - alloc[s]
            alloc[s] = floor
    for k, v in cases.items():
        s = v.get("state")
        if s and ugly[k] > alloc[s]:
            topup[s] += ugly[k] - alloc[s]
            alloc[s] = ugly[k]
    specs = []
    for layer in ("lead", "S1", "S2", "S2b", "S2c"):
        for _ in range(L[layer]):
            specs.append({"layer": layer, "target": None if layer == "lead" else layer,
                          "tier": None if layer == "lead" else "free"})
    for s in W:
        for i in range(alloc[s]):
            specs.append({"layer": "paid", "target": s, "is_topup": i >= alloc[s] - topup[s]})
    paid = [s for s in specs if s["layer"] == "paid"]
    # tiers: DIFM is S14 (config difm_rule); the rest split DIWM:DIY by the tier mix
    tm = cfg["tier_mix"]["shares"]
    bases = cfg["overlay_bases"]
    for s in paid:
        s["tier"] = "difm" if s["target"] == "S14" else None
        # S18 and S21 keep their own timeline; their weights pick the read status inside the journey
        overlay = s["target"] in bases and s["target"] not in ("S18", "S21")
        s["base"] = pick(R, dict((k, v) for k, v in bases[s["target"]].items())) if overlay else s["target"]
        s["flags"] = set()
    # cases tied to a state
    for case, v in cases.items():
        st = v.get("state")
        if not st:
            continue
        pool = [s for s in paid if s["target"] == st]
        chosen = pool[:] if case != "engine_failure" and case != "second_no_show" else R.sample(pool, min(ugly[case], len(pool)))
        if case == "second_no_show" and len(pool) <= ugly[case]:
            chosen = pool[:]
        for s in chosen:
            s["flags"].add(case)
            if case == "second_no_show":
                s["tier"] = "diwm"
    # DIWM and DIY by quota over the paid people who are not DIFM (second no-shows are DIWM)
    rest = [s for s in paid if s["tier"] != "difm"]
    q = largest_remainder(len(rest), {"diwm": tm["diwm"], "diy": tm["diy"]})
    q["diwm"] -= sum(1 for s in rest if s["tier"] == "diwm")
    labels = ["diwm"] * max(0, q["diwm"]) + ["diy"] * q["diy"]
    R.shuffle(labels)
    free = [s for s in rest if s["tier"] is None]
    for s, lab in zip(free, labels + ["diy"] * len(free)):
        s["tier"] = lab
    for s in paid:
        if s["target"] == "S5" and "engine_failure" in s["flags"]:
            s["base"] = "S5"
    # A05 visited among S3 bases
    for s in paid:
        s["a05"] = True
        if s["base"] == "S3" and s["target"] != "S17":
            s["a05"] = R.random() < cfg["journey_rates"]["s3_a05_visited"]
    # source paths by quota; S15 is AA, S17 is CAS
    mix = cfg["source_path_mix"]["shares"]
    quota = largest_remainder(len(paid), mix)
    for s in paid:
        if s["target"] == "S15":
            s["path"] = "aa"
        elif s["target"] == "S17":
            s["path"] = "cas"
    for k in quota:
        quota[k] -= sum(1 for s in paid if s.get("path") == k)
    rest = [s for s in paid if not s.get("path")]
    labels = []
    for k in mix:
        labels += [k] * max(0, quota[k])
    while len(labels) < len(rest):
        labels.append(pick(R, mix))
    R.shuffle(labels)
    for s, lab in zip(rest, labels):
        s["path"] = lab
    # AA partial and AA failed inside the AA half, among people who reached A06
    elig = [s for s in paid if s["path"] == "aa" and s["target"] != "S15" and s["a05"]]
    n_part, n_fail = ugly["aa_partial"], ugly["aa_failed"]
    chosen = R.sample(elig, min(len(elig), n_part + n_fail))
    for s in chosen[:n_part]:
        s["flags"].add("aa_partial")
    for s in chosen[n_part:]:
        s["flags"].add("aa_failed")
    subs = [s for s in paid if s["tier"] != "difm"]
    for key, shares in (("period", cfg["period_mix"]["shares"]), ("method", cfg["payment_method_mix"]["shares"])):
        q = largest_remainder(len(subs), shares)
        labels = []
        for k in shares:
            labels += [k] * q[k]
        R.shuffle(labels)
        for s, lab in zip(subs, labels):
            s[key] = lab
    info = {"ugly": ugly, "natural": natural, "alloc": alloc, "topup": topup, "floor": floor, "layers": L}
    return specs, info


# ---------------------------------------------------------------- identity and the synthetic truth

def make_identity(p, ctx):
    r, cfg, N = p.r, ctx.cfg, ctx.names
    arche = pick(r, cfg["difm_archetypes"]["weights"]) if p.tier == "difm" else pick(r, cfg["archetype_weights"]["weights"])
    p.arche = arche
    a = cfg["archetypes"][arche]
    nz = cfg["archetypes"]["noise"]
    cities = cfg["cities"]["list"]
    if arche == "tail":
        p.age = r.randint(a["age_range"][0], a["age_range"][1])
        tier = 2 if r.random() < cfg["cities"]["tail_tier2_share"] else 1
        p.city = r.choice(sorted(c for c, v in cities.items() if v["tier"] == tier))
    else:
        p.age = int(clamp(round(a["age"] + r.gauss(0, nz["age_sd"])), max(24, a["age"] - 5), min(45, a["age"] + 5)))
        if r.random() < nz["city_keep"]:
            p.city = a["city"]
        else:
            tier = cities[a["city"]]["tier"]
            p.city = r.choice(sorted(c for c, v in cities.items() if v["tier"] == tier and c != a["city"]))
    ci = cities[p.city]
    p.city_tier, p.home_state, p.region = ci["tier"], ci["state"], ci["region"]
    reg = p.region if r.random() >= N["cross_region_share"] else r.choice(sorted(N["first"]))
    p.first = r.choice(N["first"][reg])
    p.last = r.choice(N["last"][reg])
    p.name_region = reg
    bands = cfg["age_bands"]["bands"]
    p.age_band = [b[2] for b in bands if b[0] <= p.age <= b[1]][0]
    # source
    if p.tier == "difm":
        p.source = pick(r, cfg["difm"]["sources"])
    else:
        p.source = pick(r, cfg["lead_sources"]["shares"])
    cd = cfg["consents_and_devices"]
    p.whatsapp_optin = r.random() < (cd["whatsapp_optin_community"] if p.source == "community" else cd["whatsapp_optin"])
    p.dnd = r.random() < cd["dnd"]
    p.device = pick(r, cd["device"])
    # household members
    members = [{"relation": "self", "name": p.first, "age": p.age, "earns": True, "lives_with_you": True}]
    if r.random() < a["partner"]:
        pa = int(round(p.age + a.get("partner_age_delta", -1) + r.gauss(0, 1.5)))
        members.append({"relation": "partner", "name": r.choice(N["first"][reg]), "age": max(22, pa),
                        "earns": r.random() < a.get("partner_earns", 0.5), "lives_with_you": True})
    kids = []
    if arche == "tail":
        if p.age >= 27 and r.random() < a["kid_share"]:
            for _ in range(1 if r.random() < 0.6 else 2):
                kids.append(r.randint(0, min(14, p.age - 23)))
    else:
        for i, k in enumerate(a["kids"]):
            if i == 1 and "second_kid" in a and r.random() >= a["second_kid"]:
                continue
            kids.append(int(clamp(round(k + r.gauss(0, 1.0)), 0, max(0, p.age - 21))))
    for k in sorted(kids, reverse=True):
        members.append({"relation": "child", "name": r.choice(N["first"][reg]), "age": k, "earns": False,
                        "lives_with_you": True})
    pdep, plive = a["parents"]
    if r.random() < pdep:
        live = r.random() < plive
        for _ in range(1 if r.random() < 0.45 else 2):
            members.append({"relation": "dependant parent", "name": None, "age": p.age + r.randint(26, 34),
                            "earns": False, "lives_with_you": live})
    p.members = members
    partner = [m for m in members if m["relation"] == "partner"]
    has_k = any(m["relation"] == "child" for m in members)
    par_live = any(m["relation"] == "dependant parent" and m["lives_with_you"] for m in members)
    if partner and has_k and par_live:
        ht = "Me + partner + kids + parents"
    elif partner and has_k:
        ht = "Me + partner + kids"
    elif partner:
        ht = "Me + partner"
    elif has_k:
        ht = "Me + kids"
    elif par_live:
        ht = "Me + parents"
    else:
        ht = "Just me"
    p.household_type = ht
    p.partner = partner[0] if partner else None
    p.has_dependants = has_k or any(m["relation"] == "dependant parent" for m in members) or (
        bool(partner) and not partner[0]["earns"])
    p.pets = r.random() < 0.15
    # lead details (landing sheet)
    ld = cfg["lead_details"]
    p.community_joined = p.source == "community" or r.random() < ld["community_joined_other"]
    on_sheet = p.source == "web_reveal" or (p.source == "community" and r.random() < ld["landing_share_community"])
    p.on_sheet = on_sheet and p.tier != "difm"
    p.top_concern = r.choice(ld["top_concerns"]) if p.on_sheet else None
    p.keyword = pick(r, ld["keywords"]) if p.on_sheet else None
    p.resource_sent = r.choice(ld["resources"]) if p.on_sheet else None


def tax_rate(ctx, gross):
    for cap, rate in ctx.cfg["take_home_tax_placeholder"]["brackets_lakh"]:
        if gross <= cap * 1e5:
            return rate
    return 0.28


def emi_of(principal, rate_pct, years):
    n = max(1, int(round(years * 12)))
    i = rate_pct / 1200.0
    return principal * i / (1 - (1 + i) ** -n)


def make_truth(p, ctx):
    r, cfg = p.r, ctx.cfg
    a = cfg["archetypes"][p.arche]
    nz = cfg["archetypes"]["noise"]
    co = cfg["coherence"]
    if p.arche == "tail":
        G = clamp(a["income_lakh"] * 1e5 * math.exp(r.gauss(0, 0.45)), 6e5, 8e6)
    else:
        G = a["income_lakh"] * 1e5 * math.exp(r.gauss(0, nz["income_lognormal_sd"]))
    T = p.T
    T["gross"] = rnd(G, 10000)
    if p.partner and p.partner["earns"]:
        s = uni(r, cfg["take_home_tax_placeholder"]["partner_share"])
        own, pg = G * (1 - s), G * s
    else:
        own, pg = G, 0.0
    T["own_gross"] = own
    T["take_home"] = rnd(own * (1 - tax_rate(ctx, own)) / 12.0, 100)
    T["partner_take_home"] = rnd(pg * (1 - tax_rate(ctx, pg)) / 12.0, 100) if pg else None
    # corpus: saved and invested, not the home (R04); the multiple grows with the years since 22
    cm = co["corpus_multiple"]
    t = clamp((p.age - cm["scaled_by_years_since"]) / 18.0, 0.0, 1.0)
    m = clamp((0.3 + 1.7 * t) * math.exp(r.gauss(0, 0.3)), cm["min"] * 1.02, cm["max"] * 0.98)
    corpus = T["gross"] * m
    ip = 0.0
    if r.random() < a["investment_property"] and corpus >= 4e6:
        ip = rnd(corpus * r.uniform(0.25, 0.5), 50000)
    investable = corpus - ip
    gt = co["gold_tier2"]
    weights = {}
    for f, (pres, w) in a["assets"].items():
        if f == "gold" and p.city_tier == 2:
            pres, w = min(1.0, pres * gt["presence_multiplier"]), w * gt["weight_multiplier"]
        if r.random() < pres:
            weights[f] = w * r.uniform(0.6, 1.4)
    weights.setdefault("bank_and_deposits", 0.2)
    tot = sum(weights.values())
    T["assets"] = dict((f, (rnd(investable * weights[f] / tot, 100) if f in weights else None)) for f in ASSETS)
    T["investment_property_value"] = ip or None
    # loans; a home loan makes the person a home owner
    lp, LC = a["loans"], cfg["loans"]
    loans = []
    home_value = None
    has_home_loan = r.random() < lp["home"]
    owner = has_home_loan or r.random() < a["home_owner"]
    if owner:
        if p.city_tier == 1:
            home_value = clamp(G * r.uniform(2.5, 5.0), 6e6, 3.5e7)
        else:
            home_value = clamp(G * r.uniform(2.0, 4.0), 3.5e6, 1.8e7)
        home_value = rnd(home_value, 100000)
    T["home_value"] = home_value
    for typ in ("home", "car", "personal", "education"):
        if typ == "home" and not has_home_loan:
            continue
        if typ != "home" and r.random() >= lp[typ]:
            continue
        c = LC[typ]
        if typ == "home":
            out = min(G * uni(r, c["outstanding_income_multiple"]), 0.8 * home_value)
            years = uni(r, c["years_left"])
        elif typ == "education" and a.get("education_closing"):
            out = r.uniform(50000, 300000)
            years = uni(r, c["closing_years_left"])
        else:
            out = uni(r, c["outstanding_rs"])
            years = uni(r, c["years_left"])
        rate = round(uni(r, c["rate"]), 2)
        loans.append({"type": typ, "outstanding": rnd(out, 10000), "rate": rate, "years_left": round(years, 1),
                      "lender": r.choice(LC["lenders"]),
                      "tax_deductible": typ == "home" and r.random() < LC["tax_deductible_home"],
                      "prepayment_allowed": pick(r, LC["prepayment_allowed"])})
    for l in loans:
        l["emi"] = rnd(emi_of(l["outstanding"], l["rate"], l["years_left"]), 100)
    TH = T["take_home"]
    cap = co["emi_max_share_of_take_home"] * TH
    total = sum(l["emi"] for l in loans)
    if total > cap * 0.97:
        f = cap * 0.9 / total
        for l in loans:
            l["outstanding"] = rnd(l["outstanding"] * f, 10000)
            l["emi"] = rnd(emi_of(l["outstanding"], l["rate"], l["years_left"]), 100)
    T["loans"] = loans
    T["total_emi"] = sum(l["emi"] for l in loans)
    T["credit_card_balance"] = rnd(uni(r, LC["credit_card"]["balance_rs"]), 1000) if r.random() < lp["credit_card"] else None
    if r.random() < lp["informal"]:
        T["informal_loans"] = rnd(uni(r, LC["informal"]["amount_rs"]), 5000)
        T["informal_direction"] = pick(r, LC["informal"]["direction"])
    else:
        T["informal_loans"] = None
        T["informal_direction"] = None
    # income extras
    ix = cfg["income_extras"]
    T["rental_income"] = rnd(ip * uni(r, ix["rent_yield"]) / 12.0, 500) if ip else None
    T["investment_property_rent"] = T["rental_income"]
    T["other_income"] = rnd(r.uniform(3000, 30000), 500) if r.random() < ix["other_income_share"] else None
    # outgoings (EMIs included), buckets, surplus, SIP
    lo, hi = co["outgoings_share_of_take_home"]
    out = max(TH * r.uniform(0.45, 0.80), T["total_emi"] + 0.15 * TH)
    out = rnd(clamp(out, lo * TH, hi * TH), 500)
    out = int(clamp(out, math.ceil(lo * TH), math.floor(hi * TH)))
    T["total_outgoings"] = out
    fixed = max(T["total_emi"], out * r.uniform(0.45, 0.62))
    fixed = min(fixed, out * 0.9)
    variable = (out - fixed) * r.uniform(0.55, 0.8)
    T["bucket_fixed"] = rnd(fixed, 500)
    T["bucket_variable"] = rnd(variable, 500)
    T["bucket_guilt_free"] = max(0, out - T["bucket_fixed"] - T["bucket_variable"])
    HH = TH + (T["partner_take_home"] or 0) + (T["rental_income"] or 0) + (T["other_income"] or 0)
    T["household_take_home"] = HH
    T["surplus"] = HH - out
    if r.random() < a["current_sip"]:
        T["current_sip"] = max(500, rnd(T["surplus"] * uni(r, ix["sip_share_of_surplus"]), 500))
        if T["current_sip"] > T["surplus"]:
            T["current_sip"] = rnd(T["surplus"] * 0.5, 100)
    else:
        T["current_sip"] = None
    share = T["surplus"] / float(HH)
    if share > 0.35:
        T["month_end_pattern"] = pick(r, [(0, 0.7), (2, 0.2), (1, 0.1)])
    elif share > 0.2:
        T["month_end_pattern"] = pick(r, [(0, 0.3), (1, 0.4), (2, 0.3)])
    else:
        T["month_end_pattern"] = pick(r, [(1, 0.3), (2, 0.4), (3, 0.3)])
    T["savings_rate_pct"] = 100.0 * share
    # ULIP detail
    if T["assets"]["ulip_surrender_value"]:
        T["ulip_premium"] = rnd(r.uniform(25000, 150000), 1000)
        T["ulip_years_completed"] = r.randint(1, 15)
    else:
        T["ulip_premium"] = T["ulip_years_completed"] = None
    # covers
    cv = cfg["covers"]
    pterm = (1 - co["term_missing_with_dependants"]) if p.has_dependants else co["term_have_without_dependants"]
    pterm = clamp(pterm * a["term_tilt"], 0.0, 0.95)
    if r.random() < pterm:
        sa = max(2500000, rnd(own * uni(r, cv["term_sum_assured_income_multiple"]), 500000))
        T["term"] = {"sum_assured": sa, "premium": rnd(sa * uni(r, cv["term_premium_rate"]), 100),
                     "until_age": r.randint(cv["term_until_age"][0], cv["term_until_age"][1])}
    else:
        T["term"] = None
    htype = pick(r, a["health"])
    if htype == "none":
        T["health"] = None
    else:
        si = 0
        if htype in ("employer", "both"):
            si += rnd(uni(r, cv["health_employer_si"]), 50000)
        if htype in ("personal", "both"):
            si += rnd(uni(r, cv["health_personal_si"]), 50000)
        family = bool(p.partner) or any(m["relation"] == "child" for m in p.members)
        T["health"] = {"type": {"employer": "Employer only", "personal": "Personal", "both": "Both"}[htype],
                       "sum_insured": si, "floater": family and r.random() < cv["floater_with_family"],
                       "premium": rnd(uni(r, cv["health_premium"]), 100) if htype != "employer" else None}
    T["other_policies"] = rnd(uni(r, cv["other_policies_si"]), 100000) if r.random() < cv["other_policies_share"] else None
    # goals
    gc = cfg["goals"]
    goals = []
    if r.random() >= gc["none_share"]:
        ty = gc["types"]
        yr = ctx.A.year
        for m in p.members:
            if m["relation"] == "child" and r.random() < ty["Education"]["per_child"]:
                goals.append({"type": "Education", "name": "%s's higher education" % m["name"],
                              "year": yr + max(1, 18 - m["age"]), "cost": uni(r, ty["Education"]["cost_rs"])})
        if r.random() < (a.get("goal_home", ty["Home upgrade"]["p"])):
            goals.append({"type": "Home upgrade", "name": "Home upgrade", "year": yr + r.randint(2, 8),
                          "cost": uni(r, ty["Home upgrade"]["cost_rs"])})
        if not p.partner and p.age < 32 and r.random() < ty["Wedding"]["p_single_under_32"]:
            goals.append({"type": "Wedding", "name": "Wedding", "year": yr + r.randint(1, 4),
                          "cost": uni(r, ty["Wedding"]["cost_rs"])})
        for name, key, yrs in (("Vehicle", "p", (1, 5)), ("Travel", "p", (1, 3)),
                               ("Business or second income", "p", (3, 10)), ("Health corpus", "p", (5, 15)),
                               ("Something else", "p", (2, 8))):
            if r.random() < ty[name][key]:
                goals.append({"type": name, "name": name, "year": yr + r.randint(yrs[0], yrs[1]),
                              "cost": uni(r, ty[name]["cost_rs"])})
        if any(m["relation"] == "dependant parent" for m in p.members) and r.random() < ty["Parents' support"]["p_with_parents"]:
            goals.append({"type": "Parents' support", "name": "Parents' support", "year": yr + r.randint(1, 5),
                          "cost": uni(r, ty["Parents' support"]["cost_rs"])})
        if not goals:
            goals.append({"type": "Travel", "name": "Travel", "year": yr + r.randint(1, 3),
                          "cost": uni(r, ty["Travel"]["cost_rs"])})
        r.shuffle(goals)
        goals = goals[:gc["max_goals"]]
        for g in goals:
            g["cost"] = rnd(g["cost"], 10000)
            g["cost_kind"] = pick(r, gc["cost_kind"])
            g["priority"] = pick(r, gc["priority"])
            g["timeline"] = "chips" if r.random() < 0.7 else "exact year"
    T["goals"] = goals
    wo = gc["work_optional"]
    if r.random() < wo["default_accepted"]:
        T["work_optional_age"], T["work_optional_default"] = 60, True
    else:
        T["work_optional_age"] = r.choice(wo["chips"]) if r.random() < 0.6 else r.randint(wo["typed_range"][0], wo["typed_range"][1])
        T["work_optional_default"] = False
    # risk profile (L03 bands; points by option order)
    rp = cfg["rpq"]
    deps = sum(1 for m in p.members if m["relation"] in ("child", "dependant parent")) + (
        1 if p.partner and not p.partner["earns"] else 0)
    q1 = 0 if deps == 0 else 1 if deps <= 2 else 2 if deps <= 4 else 3
    q2 = pick(r, [(0, 0.55), (1, 0.35), (2, 0.08), (3, 0.02)])
    app = clamp(a["risk_appetite"] + r.gauss(0, 0.15), 0.0, 1.0)

    def byapp():
        return int(clamp(round((1 - app) * 3 + r.gauss(0, 0.7)), 0, 3))
    sr = T["savings_rate_pct"]
    q4 = 0 if sr > 30 else 1 if sr >= 10 else (2 if T["assets"]["epf"] else 3)
    answers = [q1, q2, byapp(), q4, byapp(), byapp(), byapp(), byapp()]
    score = sum(rp["points_by_option"][x] for x in answers)
    band = [b[2] for b in rp["bands"] if b[0] <= score <= b[1]][0]
    T["rpq"] = {"answers": answers, "score": score, "risk_band": band}
    T["corpus"] = sum(v or 0 for v in T["assets"].values()) + ip


def truth_value(p, f):
    """The synthetic truth behind one spine field (None when the person does not have it)."""
    T = p.T
    if f in T.get("assets", {}):
        return T["assets"][f]
    if f in ("take_home", "partner_take_home", "rental_income", "other_income", "total_outgoings", "bucket_fixed",
             "bucket_variable", "bucket_guilt_free", "current_sip", "home_value", "investment_property_value",
             "investment_property_rent", "ulip_premium", "ulip_years_completed", "credit_card_balance",
             "informal_loans", "other_policies", "month_end_pattern"):
        return T.get(f)
    if f in ("term_sum_assured", "term_premium", "term_cover_until_age"):
        if not T["term"]:
            return None
        return {"term_sum_assured": T["term"]["sum_assured"], "term_premium": T["term"]["premium"],
                "term_cover_until_age": T["term"]["until_age"]}[f]
    if f in ("health_type", "health_sum_insured", "health_floater", "health_premium"):
        if not T["health"]:
            return None
        return {"health_type": T["health"]["type"], "health_sum_insured": T["health"]["sum_insured"],
                "health_floater": T["health"]["floater"], "health_premium": T["health"]["premium"]}[f]
    if f == "total_emi":
        return T["total_emi"]
    return None


# ---------------------------------------------------------------- stored values from decisions

def stored(ctx, p, f, dec):
    """(value, value_kind, band_id, precision) for a field from its decision and the truth."""
    kind = dec["kind"]
    fc = ctx.fields.get(f, {})
    if kind == "none":
        return None, "none", None, "exact"
    if kind == "not_sure":
        return None, "not_sure", None, "unknown"
    v = dec.get("value") if "value" in dec else truth_value(p, f)
    if kind == "band":
        lad = fc["ladder"]
        i = band_index(v, ctx.bands[lad])
        return rnd(band_mid(ctx.bands[lad], i), 100), "band", "%s.%d" % (lad, i), "approx"
    if kind == "default":
        return v, "exact", None, "exact"
    if isinstance(v, bool) or isinstance(v, str) or v is None:
        return v, "exact", None, "exact"
    if dec.get("source") in ("aa", "cas", "derived"):
        return int(round(v)), "exact", None, "exact"
    step = 1000 if v >= 10000 else 100 if v >= 1000 else 1
    return rnd(v, step), "exact", None, "exact"


def set_dec(p, f, kind, source, screen, at, **extra):
    old = p.dec.get(f)
    d = {"kind": kind, "source": source, "screen": screen, "at": at, "locked": False, "history": []}
    if old:
        d["history"] = old["history"] + [{"kind": old["kind"], "source": old["source"], "screen": old["screen"],
                                          "at": old["at"]}]
    d.update(extra)
    p.dec[f] = d
    return d


# ---------------------------------------------------------------- timelines

def sample_lead(ctx, r):
    a, b = ctx.tm["ramp"]
    u = r.random()
    # density a + (b - a) x on [0, 1] (x = 1 at the anchor), normalised
    x = (-a + math.sqrt(a * a + (b - a) * (a + b) * u)) / (b - a)
    t = ctx.window_start + DAYS(x * ctx.tm["window_days"])
    t = t.replace(hour=ctx.hour(r), minute=r.randint(0, 59), second=r.randint(0, 59), microsecond=0)
    return min(t, ctx.A - MINS(r.randint(30, 600)))


def pay_delay(ctx, r):
    pm = ctx.tm["paid_after_reveal"]
    x = r.random()
    if x < pm["same_session_share"]:
        return r.uniform(0.004, 0.12)
    if x < pm["same_session_share"] + pm["ladder_share"]:
        d = int(pick(r, pm["ladder_days"]))
        return max(0.2, d + r.uniform(-0.4, 0.4))
    return r.uniform(0.0, pm["max_days"])


def backward_chain(p, ctx, paid, allow_old=False):
    """lead, OTP and reveal before a payment (or a checkout); False when the lead falls outside the window."""
    r = p.r
    for _ in range(60):
        rev = paid - DAYS(pay_delay(ctx, r))
        otp = rev - DAYS(max(0.005, exp_median(r, ctx.tm["reveal_after_otp_days"]["median"], ctx.tm["reveal_after_otp_days"]["max"])))
        lead = otp - DAYS(exp_median(r, ctx.tm["otp_after_lead_days"]["median"], ctx.tm["otp_after_lead_days"]["max"]))
        if allow_old or lead >= ctx.window_start:
            p.tl.update(lead=lead.replace(microsecond=0), otp=otp.replace(microsecond=0), reveal=rev.replace(microsecond=0))
            return True
    return False


def first_d_delay(r):
    x = r.random()
    if x < 0.5:
        return r.uniform(0.005, 0.25)
    if x < 0.8:
        return r.uniform(0.5, 3.0)
    return r.uniform(3.0, 10.0)


PAID_AGO = {"S3": (0.05, 6.8), "S4": (0.2, 13.0), "S19": (7.3, 80.0), "S5": (1.1, 28.0), "S6": (1.1, 60.0),
            "S8": (2.0, 150.0), "S9": (8.0, 176.0), "S10": (25.0, 176.0), "S18": (8.2, 100.0), "S21": (6.0, 150.0)}
GATE_BASES = {"S5", "S6", "S8", "S9", "S10", "S18", "S21"}


def paid_ago_for(p, ctx, c):
    r, tgt, base = p.r, p.target, p.base
    lo, hi = PAID_AGO[base]
    P = ctx.cfg["period_mix"]["days"].get(p.period) if p.period else None
    if tgt == "S12":
        fa = r.uniform(0.05, 6.8)
        ks = [k for k in range(1, 12) if lo <= fa + k * P <= 176]
        if not ks:
            return None
        k = r.choice(ks)
        c["fail_ago"], c["fail_k"] = fa, k
        return fa + k * P
    if tgt == "S13":
        fa = r.uniform(7.1, 90.0)
        ks = [k for k in range(1, 12) if lo <= fa + k * P <= 176]
        if not ks:
            return None
        k = r.choice(ks)
        c["fail_ago"], c["fail_k"] = fa, k
        return fa + k * P
    if tgt == "S15":
        ea = r.uniform(0.05, 40.0)
        c["expiry_ago"] = ea
        c["conn_delay"] = r.uniform(0.003, 2.0)
        return ea + ctx.tm["consent_days"] + c["conn_delay"]
    if tgt == "S22":
        return r.uniform(106.0, 176.0)
    if tgt == "S23":
        return uni(r, ctx.tx["s23_tenure_days"])
    if tgt == "S24":
        return r.uniform(1.0, 6.8) if base == "S3" else r.uniform(1.0, 13.0) if base == "S4" else r.uniform(2.0, 20.0)
    if tgt == "S11":
        return r.uniform(max(lo, 16.0), max(hi, 40.0))
    return r.uniform(lo, hi)


def sample_paid_chain(p, ctx):
    """The milestones of one paid DIY or DIWM person, drawn from the time model until the target state's base
    holds at the anchor. Only the milestones the base needs are drawn (an S8 person never starts an action)."""
    r, A, tm = p.r, ctx.A, ctx.tm
    base, tgt = p.base, p.target
    for attempt in range(800):
        c = {}
        pa = paid_ago_for(p, ctx, c)
        if pa is None:
            continue
        paid = (A - DAYS(pa)).replace(microsecond=0)
        if paid.hour < 7:
            paid = paid.replace(hour=7 + r.randint(0, 14))
        if paid >= A:
            continue
        c["paid"] = paid
        # onboarding right after paying (65 percent) or a later session
        onb = paid + (MINS(r.uniform(2, 20)) if r.random() < 0.65 else DAYS(r.uniform(0.1, 3.0)))
        c["onb"] = onb if p.a05 else None
        ready = onb
        if p.path == "aa" and c["onb"]:
            c["aa_at"] = onb + MINS(r.uniform(1, 4))
            c["fetch_at"] = c["aa_at"] + MINS(r.uniform(1, 5))
        if p.path == "cas" and c["onb"]:
            c["cas_req"] = onb + MINS(r.uniform(1, 4))
            if tgt == "S17":
                pass
            elif p.cas_typed_instead:
                c["cas_abandon"] = c["cas_req"] + DAYS(r.uniform(0.02, 1.0))
                ready = c["cas_abandon"]
            else:
                c["cas_up"] = c["cas_req"] + HOURS(r.uniform(1.0, 48.0))
                c["cas_parsed"] = c["cas_up"] + MINS(r.uniform(1, 4))
                ready = c["cas_parsed"]
        if base == "S3":
            if not (A < paid + DAYS(7)):
                continue
            if c.get("onb") and c["onb"] >= A:
                c["onb"] = None
            if tgt == "S17" and (not c.get("cas_req") or c["cas_req"] >= A):
                continue
        else:
            fd = max(paid + DAYS(first_d_delay(r)), ready + MINS(r.uniform(2, 8)))
            c["first_d"] = fd
            if base == "S4":
                if not (fd <= A - MINS(10) and (fd - paid) < DAYS(7) and A < fd + DAYS(7)):
                    continue
                c["stop"] = fd + (A - fd) * r.uniform(0.05, 0.95)
            elif base == "S19":
                stall = paid + DAYS(7) if (fd - paid) >= DAYS(7) else fd + DAYS(7)
                if not (stall <= A - MINS(5) and fd <= A - MINS(30)):
                    continue
                c["stall"] = stall
                c["stop"] = fd + (A - fd) * r.uniform(0.02, 0.9)
            else:
                dur = uni(r, tm["data_steps_days"])
                gate = max(paid + DAYS(dur), fd + HOURS(2))
                if gate.hour < 7:
                    gate = gate.replace(hour=7 + r.randint(0, 2), minute=r.randint(0, 59))
                c["gate"] = gate
                if base == "S5":
                    if not (gate <= A - MINS(20) and A < gate + DAYS(7)):
                        continue
                    if p.engine_failure:
                        c["d10"] = gate + MINS(r.uniform(1, 6))
                        if c["d10"] >= A:
                            continue
                elif base == "S18":
                    c["built"] = gate + DAYS(7)
                    c["built_on"] = "partial"
                    if not c["built"] <= A - MINS(5):
                        continue
                else:
                    g2b = r.uniform(0.001, 0.02) if r.random() < 0.7 else r.uniform(1.0, 6.5)
                    c["built"] = gate + DAYS(g2b)
                    c["built_on"] = "full"
                    if c["built"] >= A - MINS(5):
                        continue
                if "built" in c:
                    read_needed = base in ("S8", "S9", "S10") or (base == "S18" and p.s18_read) or (
                        base == "S21" and p.s21_read)
                    if read_needed:
                        rd = r.uniform(0.001, 0.2) if r.random() < 0.5 else r.uniform(0.2, 10.0)
                        c["read"] = c["built"] + DAYS(rd)
                        if c["read"] >= A - MINS(2):
                            continue
                    acting = base in ("S9", "S10") or (base == "S18" and p.s18_acting)
                    if acting:
                        n = r.randint(ctx.cfg["actions"]["min"], ctx.cfg["actions"]["max"])
                        starts, dones = [], []
                        t0 = c["read"] + DAYS(uni(r, tm["first_action_after_read_days"]))
                        for i in range(n):
                            s = t0 if i == 0 else starts[-1] + DAYS(uni(r, tm["later_actions_days"]))
                            starts.append(s)
                            dones.append(s + DAYS(r.uniform(0.01, 10.0)))
                        c["n_actions"] = n
                        c["starts"], c["dones"] = starts, dones
                        if base == "S10" and not max(dones) <= A - MINS(5):
                            continue
                        if base in ("S9", "S18") and not (starts[0] <= A - MINS(5) and max(dones) > A):
                            continue
                    if base == "S21":
                        bk = c["built"] + DAYS(uni(r, tm["call_after_built_days"]))
                        slot = bk + DAYS(uni(r, tm["slot_after_booking_days"]))
                        slot = slot.replace(hour=r.choice(ctx.tx["call_hours_ist"]), minute=r.choice([0, 30]), second=0)
                        if not (slot + MINS(tm["call_minutes"]) <= A - MINS(5) and slot > bk):
                            continue
                        if c.get("read") and c["read"] > slot:
                            continue
                        c["s21_call"] = (bk, slot)
        # overlay checks
        if tgt == "S11":
            if not c.get("built") or c["built"] >= ctx.publishes[-1]["at"] - HOURS(2):
                continue
        if tgt == "S22":
            if not c.get("built") or c["built"] > A - DAYS(ctx.tm["review_every_days"] + ctx.tm["review_ignored_after_days"]):
                continue
        if tgt == "S24":
            lim = min(paid + DAYS(ctx.tm["refund_within_days"]), A - MINS(30))
            if lim <= paid + HOURS(2):
                continue
            c["refund_at"] = paid + (lim - paid) * r.uniform(0.05, 1.0)
            if c.get("first_d") and base == "S3":
                continue
        if tgt == "S20" and paid > A - DAYS(4.5 if "second_no_show" in p.flags else 2.5):
            continue
        if tgt == "S7" and paid > A - HOURS(6):
            continue
        if tgt in ("S12", "S13"):
            P = ctx.cfg["period_mix"]["days"][p.period]
            c["fail_at"] = paid + DAYS(P * c["fail_k"])
            if tgt == "S12" and not (c["fail_at"] <= A - MINS(30) and A < c["fail_at"] + DAYS(ctx.tm["grace_days"])):
                continue
            if tgt == "S13" and not (c["fail_at"] + DAYS(ctx.tm["grace_days"]) <= A - MINS(30)):
                continue
        if tgt == "S15":
            if not c.get("aa_at"):
                continue
        return c
    raise RuntimeError("no timeline for %s over %s after 800 draws" % (tgt, base))


# ---------------------------------------------------------------- journeys: leads and the free layers

def journey_lead(p, ctx):
    r = p.r
    p.tl["lead"] = sample_lead(ctx, r)
    p.created_at = p.tl["lead"]
    if p.on_sheet:
        p.landing = p.tl["lead"]
        p.email_known_at = p.tl["lead"]


def entry_events(p, ctx, otp):
    """A01 to A04 and the OTP (the lead becomes a verified lead)."""
    r = p.r
    t = otp - MINS(r.uniform(1.5, 6))
    p.view(ctx, t, "A01")
    t += SECS(r.randint(10, 40))
    p.view(ctx, t, "A02")
    p.integ_call(ctx, t + SECS(3), "gupshup", "send_otp", "ok")
    t = otp
    p.view(ctx, t, "A03")
    p.integ_call(ctx, t, "gupshup", "verify_otp", "ok")
    p.ev(t, "signed_up", "A03", phone="(the contact phone)", source=p.source, whatsapp_optin=p.whatsapp_optin,
         device=p.device)
    t += SECS(r.randint(5, 30))
    p.view(ctx, t, "A04")
    return t + SECS(r.randint(20, 90))


def reveal_events(p, ctx, t, upto, rev=None):
    """R01 to R07 answered up to `upto` (index 0..7); 7 means the full reveal, then R08 and R09 at `rev`."""
    r = p.r
    order = ["R01", "R02", "R03", "R04", "R05", "R06", "R07"]
    if rev is not None:
        step = (rev - SECS(30) - t) / 7
        for i, sid in enumerate(order):
            p.view(ctx, t + step * i, sid)
        return rev
    for i, sid in enumerate(order):
        if i > upto:
            break
        p.view(ctx, t, sid)
        if i == upto and upto < 7:
            p.last_screen = sid
            return t
        t += SECS(r.randint(8, 45))
    return t


def journey_free(p, ctx):
    r, A = p.r, ctx.A
    L = p.layer
    for attempt in range(300):
        lead = sample_lead(ctx, r)
        otp = lead + DAYS(exp_median(r, ctx.tm["otp_after_lead_days"]["median"], ctx.tm["otp_after_lead_days"]["max"]))
        otp = otp.replace(microsecond=0)
        if otp >= A - MINS(40):
            continue
        tl = {"lead": lead, "otp": otp}
        if L != "S1":
            rev = otp + DAYS(max(0.005, exp_median(r, ctx.tm["reveal_after_otp_days"]["median"], ctx.tm["reveal_after_otp_days"]["max"])))
            rev = rev.replace(microsecond=0)
            if rev >= A - MINS(10):
                continue
            tl["reveal"] = rev
            if L in ("S2b", "S2c"):
                co = rev + DAYS(pay_delay(ctx, r))
                if co.hour < 7:
                    co = co.replace(hour=8 + r.randint(0, 12))
                if co >= A - MINS(20):
                    continue
                tl["checkout"] = co.replace(microsecond=0)
                if L == "S2c":
                    es = co + (MINS(r.uniform(3, 15)) if r.random() < 0.8 else DAYS(r.uniform(0.2, 3.0)))
                    if es >= A - MINS(5):
                        continue
                    tl["esign"] = es.replace(microsecond=0)
        break
    p.tl.update(tl)
    p.created_at = p.tl["lead"]
    if p.on_sheet:
        p.landing = p.tl["lead"]
        p.email_known_at = p.tl["lead"]
    free_events(p, ctx)


def free_events(p, ctx):
    r, tl, jr = p.r, p.tl, ctx.cfg["journey_rates"]
    t = entry_events(p, ctx, tl["otp"])
    if p.layer == "S1":
        k = r.randint(jr["s1_reveal_screens_answered"][0], jr["s1_reveal_screens_answered"][1])
        p.reveal_upto = k
        reveal_events(p, ctx, t, k)
        return
    p.reveal_upto = 7
    rev = tl["reveal"]
    t = max(t, rev - MINS(r.uniform(2, 5)))
    reveal_events(p, ctx, t, 7, rev)
    p.view(ctx, rev - SECS(20), "R08")
    p.view(ctx, rev, "R09")
    p.reveal_seen_event_at = rev
    t = rev + SECS(r.randint(30, 120))
    if r.random() < jr["s2_video_watched"]:
        p.view(ctx, t, "R10")
        t += SECS(r.randint(40, 200))
    if r.random() < jr["s2_sample_opened"]:
        p.view(ctx, t, "R12")
        t += SECS(r.randint(30, 180))
    if r.random() < jr["s2_x01_seen"]:
        p.view(ctx, t, "X01")
        t += SECS(r.randint(5, 40))
    wall = p.layer != "S2" or r.random() < jr["s2_paywall_viewed"]
    if wall:
        pt = t if p.layer == "S2" else tl["checkout"] - MINS(r.uniform(1, 4))
        pt = max(pt, rev + SECS(40))
        p.view(ctx, pt, "P01")
        p.ev(pt, "paywall_viewed", "P01", sku_expanded=r.choice(["diy", "diwm", "none"]), from_state="S2")
    if p.layer in ("S2b", "S2c"):
        kyc(p, ctx, tl["checkout"])
        t = tl["checkout"] + SECS(r.randint(60, 240))
        p.view(ctx, t, "P03")
        if p.layer == "S2c":
            esign(p, ctx, tl["esign"])
            p.view(ctx, tl["esign"] + SECS(r.randint(20, 60)), "P04")
            p.last_screen = "P04"
        else:
            p.last_screen = "P03"


def kyc(p, ctx, t):
    r = p.r
    p.view(ctx, t, "P02")
    fail = r.random() < ctx.cfg["journey_rates"]["kra_fail"]
    p.integ_call(ctx, t + SECS(20), "cams_kra", "kra_fetch", "failed" if fail else "ok",
                 "KRA record not found; address taken on P02" if fail else None)
    p.kyc_status = "verified (address typed)" if fail else "verified"
    p.kyc_at = t + SECS(r.randint(40, 180))
    p.email_known_at = p.email_known_at or p.kyc_at
    p.pan_known = True
    p.tl["checkout"] = p.tl.get("checkout") or t


def esign(p, ctx, t):
    r = p.r
    if r.random() < ctx.cfg["journey_rates"]["esign_retry"]:
        p.integ_call(ctx, t - MINS(3), "protean", "esign", "failed", "OTP from the eSign provider not received")
    p.integ_call(ctx, t, "protean", "esign", "ok")
    p.ev(t, "esign_done", "P03", agreement_version=ctx.cfg["app_config"]["agreement_version"],
         esign_ref="ESIGN-SEED-%06d" % (p.idx * 7 + 11))
    p.tl["esign"] = t


# ---------------------------------------------------------------- journeys: paid

def journey_paid(p, ctx):
    r, A = p.r, ctx.A
    jr = ctx.cfg["journey_rates"]
    p.cas_typed_instead = p.path == "cas" and p.target != "S17" and r.random() < 0.15
    p.s18_read = r.random() < 0.6 if p.target == "S18" or p.base == "S18" else False
    p.s18_acting = False
    if p.base == "S18":
        sub = pick(r, ctx.cfg["overlay_bases"]["S18"])
        p.s18_read = sub in ("S8", "S9")
        p.s18_acting = sub == "S9"
    p.s21_read = r.random() < 0.7
    if p.base == "S21":
        sub = pick(r, ctx.cfg["overlay_bases"]["S21"])
        p.s21_read = sub == "S8"
    c = sample_paid_chain(p, ctx)
    p.chain = c
    paid = c["paid"]
    allow_old = p.target == "S23"
    if not backward_chain(p, ctx, paid - MINS(r.uniform(4, 15)), allow_old):
        backward_chain(p, ctx, paid - MINS(r.uniform(4, 15)), True)
        p.lead_clamped = True
    p.tl["paid"] = paid
    p.created_at = p.tl["lead"]
    if p.on_sheet:
        p.landing = p.tl["lead"]
        p.email_known_at = p.tl["lead"]
    # the free part of the journey
    t = entry_events(p, ctx, p.tl["otp"])
    p.reveal_upto = 7
    rev = p.tl["reveal"]
    t = max(t, rev - MINS(r.uniform(2, 5)))
    reveal_events(p, ctx, t, 7, rev)
    p.view(ctx, rev - SECS(20), "R08")
    p.view(ctx, rev, "R09")
    t = rev + SECS(r.randint(30, 120))
    if r.random() < 0.5:
        p.view(ctx, t, "R12")
        t += SECS(r.randint(30, 150))
    # checkout: P01 to P05 in the paying session
    co = paid - MINS(r.uniform(3, 12))
    if co <= rev:
        co = rev + (paid - rev) * 0.3
    p.tl["checkout"] = co
    p.view(ctx, co - SECS(40), "P01")
    p.sku = p.tier
    p.ev(co - SECS(30), "paywall_viewed", "P01", sku_expanded=p.tier, from_state="S2")
    kyc(p, ctx, co)
    es = co + (paid - co) * 0.5
    p.view(ctx, es - SECS(30), "P03")
    esign(p, ctx, es)
    p.view(ctx, paid - SECS(40), "P04")
    subscribe(p, ctx, paid, first=True)
    p.view(ctx, paid + SECS(5), "P05")
    # onboarding and the source path
    onboarding(p, ctx, c)
    # the data spine
    spine(p, ctx, c)
    # after the plan
    if c.get("built"):
        build_plan(p, ctx, c)
    overlays(p, ctx, c)
    renewals(p, ctx)
    consents(p, ctx)
    reviews(p, ctx)
    publishes(p, ctx)
    background_calls(p, ctx)


def subscribe(p, ctx, t, first=False, resub=False):
    r = p.r
    cfg = ctx.cfg
    P = cfg["period_mix"]["days"][p.period]
    coupon = cfg["gst"]["coupon_code"] if (first and r.random() < cfg["gst"]["coupon_zero_share"]) else None
    if first:
        p.coupon = coupon
    gst = "none" if (coupon or getattr(p, "coupon", None)) else (
        "cgst_sgst" if p.home_state == cfg["gst"]["org_state"] else "igst")
    sub = {"n": len(p.subs) + 1, "sku": p.tier, "period": p.period, "price_key": "%s_%s" % (p.tier, p.period),
           "amount": "Rs ___", "gst_type": gst, "payment_method": p.method, "coupon": getattr(p, "coupon", None),
           "start": t, "status": "active", "mandate_status": None, "renewals": [], "grace_until": None,
           "retry_count": 0, "cancel_reason": None, "refund_requested": False, "refund_status": None,
           "ended_at": None, "lapsed_at": None, "resubscribed": resub}
    if p.method == "upi":
        sub["mandate_status"] = "pending" if (days_between(t, ctx.A) < 3 and r.random() < cfg["mandate_pending_share"]["value"] * 4) else "active"
        if sub["mandate_status"] == "pending":
            sub["status"] = "pending_mandate"
    else:
        sub["mandate_status"] = "none (charged per period)"
    if r.random() < cfg["journey_rates"]["payment_first_try_fail"]:
        pay(p, ctx, sub, t - MINS(2), "failed", "UPI collect request declined")
    pay(p, ctx, sub, t, "captured")
    p.subs.append(sub)
    p.ev(t, "resubscribed" if resub else "paid", "P05" if not resub else "Q03", sku=p.tier, amount="Rs ___",
         period=p.period, razorpay_ids="(the deal's Razorpay ids)", mandate_status=sub["mandate_status"],
         **({"reason": "resubscribed after lapse"} if resub else {}))
    return sub


def pay(p, ctx, sub, t, status, detail=None):
    p.integ_call(ctx, t, "razorpay", "charge" if sub["renewals"] or sub.get("n", 1) > 1 else "checkout",
                 "ok" if status == "captured" else "failed", detail)
    p.payments.append({"sub_n": sub["n"], "at": t, "status": status, "amount": "Rs ___", "gst_type": sub["gst_type"],
                       "method": sub["payment_method"], "detail": detail})


def onboarding(p, ctx, c):
    r = p.r
    onb = c.get("onb")
    t0 = c["paid"] + SECS(r.randint(20, 90))
    p.view(ctx, t0, "O01")
    p.view(ctx, t0 + SECS(r.randint(10, 40)), "O02")
    if not onb:
        return
    t = max(onb - MINS(1), t0 + SECS(60))
    p.view(ctx, t, "D00")
    t = max(t + SECS(20), onb)
    p.view(ctx, t, "A05")
    p.source_choice_at = t
    if p.path == "aa":
        p.ev(t + SECS(30), "source_choice", "A05", source_choice="aa")
        aa_connect(p, ctx, c["aa_at"], c["fetch_at"])
    elif p.path == "cas":
        p.ev(t + SECS(30), "source_choice", "A05", source_choice="cas")
        cas_flow(p, ctx, c)
    else:
        p.ev(t + SECS(30), "source_choice", "A05", source_choice=r.choice(["manual", "later"]))
    p.aa_status = {"aa": "connected", "cas": "cas_uploaded", "manual": "not_connected"}[p.path]
    if "aa_failed" in p.flags:
        p.aa_status = "failed"
    elif "aa_partial" in p.flags:
        p.aa_status = "partial"
    if p.path == "cas" and not c.get("cas_up"):
        p.aa_status = "not_connected"


def aa_connect(p, ctx, t, fetch):
    r, cfg = p.r, ctx.cfg
    inst = cfg["aa_institutions"]
    p.view(ctx, t - SECS(40), "A06")
    banks = r.sample(inst["banks"], 1 if r.random() < 0.6 else 2)
    groups = {"banks": banks}
    T = p.T["assets"]
    if T["mutual_funds"]:
        groups["mf"] = r.sample(inst["mf"], 1 if r.random() < 0.6 else 2)
    if T["stocks"]:
        groups["demat"] = [r.choice(inst["demat"])]
    if T["nps"]:
        groups["nps"] = inst["nps"][:]
    failed_groups = []
    if "aa_failed" in p.flags:
        failed_groups = list(groups)
    elif "aa_partial" in p.flags:
        cand = [g for g in groups if g != "banks"] or ["banks"]
        failed_groups = r.sample(cand, 1 if len(cand) == 1 or r.random() < 0.7 else 2)
    ok = [i for g in groups for i in groups[g] if g not in failed_groups]
    bad = [i for g in groups for i in groups[g] if g in failed_groups]
    p.integ_call(ctx, t, "finvu", "consent_create", "ok")
    for g, lst in groups.items():
        for i in lst:
            if g in failed_groups:
                p.integ_call(ctx, fetch, "finvu", "fi_fetch", r.choice(["failed", "timeout"]), "%s: fetch did not return" % i)
            else:
                p.integ_call(ctx, fetch, "finvu", "fi_fetch", "ok")
    p.view(ctx, t + SECS(5), "A07")
    expiry = t + DAYS(ctx.tm["consent_days"])
    if "aa_failed" in p.flags:
        p.view(ctx, fetch + SECS(20), "A09")
        p.ev(fetch + SECS(20), "aa_failed", "A09", institutions_ok=[], institutions_failed=bad, consent_expiry=None)
        p.consents.append({"handle": "CONSENT-SEED-%05d-1" % p.idx, "status": "failed", "connected_at": t,
                           "expires_at": None, "renewed_at": None, "institutions_ok": [], "institutions_failed": bad,
                           "fetched_at": fetch})
        p.ops.append({"type": "aa_failure", "created_at": fetch + MINS(1), "detail": "AA failed entirely; manual path"})
        return
    p.ev(t, "aa_connected", "A06", institutions_ok=ok, institutions_failed=bad, consent_expiry=ymd(expiry))
    p.consents.append({"handle": "CONSENT-SEED-%05d-1" % p.idx, "status": "active", "connected_at": t,
                       "expires_at": expiry, "renewed_at": None, "institutions_ok": ok, "institutions_failed": bad,
                       "fetched_at": fetch})
    if bad:
        p.view(ctx, fetch + SECS(20), "A09")
        p.ops.append({"type": "aa_failure", "created_at": fetch + MINS(1),
                      "detail": "AA partial: %s did not return" % ", ".join(bad)})
    fed_groups = [g for g in groups if g not in failed_groups]
    for f, g in AA_FIELDS.items():
        if g in fed_groups and truth_value(p, f) is not None:
            p.fed[f] = {"source": "aa", "at": fetch, "screen": "A08"}
    if T["mutual_funds"] and "mf" in fed_groups:
        make_holdings(p, ctx, "mf", "aa", fetch)
    if T["stocks"] and "demat" in fed_groups:
        make_holdings(p, ctx, "stock", "aa", fetch)


def cas_flow(p, ctx, c):
    r = p.r
    t = c["cas_req"]
    src = "nsdl_cdsl" if (p.T["assets"]["stocks"] and r.random() < 0.6) else "cams_kfintech"
    p.view(ctx, t - SECS(20), "A10")
    p.ev(t, "cas_requested", "A10", cas_source=src)
    p.view(ctx, t + SECS(5), "A10a")
    rec = {"requested_at": t, "cas_source": src, "reminder_count": 0, "uploaded_at": None, "parsed_at": None,
           "abandoned_at": None}
    up = c.get("cas_up")
    end = up or c.get("cas_abandon") or ctx.A
    for hrs in (1, 24):
        if t + HOURS(hrs) < end:
            rec["reminder_count"] += 1
    if c.get("cas_abandon"):
        rec["abandoned_at"] = c["cas_abandon"]
        p.view(ctx, c["cas_abandon"], "A10a")
    if up:
        p.view(ctx, up - SECS(40), "A10b")
        p.ev(up, "cas_uploaded", "A10b", cas_source=src)
        p.view(ctx, c["cas_parsed"] - SECS(10), "A10c")
        p.ev(c["cas_parsed"], "cas_parsed", "A10c", cas_source=src)
        rec["uploaded_at"], rec["parsed_at"] = up, c["cas_parsed"]
        fields = ["mutual_funds"] + (["stocks"] if src == "nsdl_cdsl" else [])
        for f in fields:
            if truth_value(p, f) is not None:
                p.fed[f] = {"source": "cas", "at": c["cas_parsed"], "screen": "A10c"}
        if p.T["assets"]["mutual_funds"]:
            make_holdings(p, ctx, "mf", "cas", c["cas_parsed"])
        if src == "nsdl_cdsl" and p.T["assets"]["stocks"]:
            make_holdings(p, ctx, "stock", "cas", c["cas_parsed"])
    p.cas.append(rec)


def make_holdings(p, ctx, kind, source, t):
    r = p.r
    h = ctx.cfg["holdings"]
    total = p.T["assets"]["mutual_funds" if kind == "mf" else "stocks"]
    n = r.randint(h["mf_count"][0], h["mf_count"][1]) if kind == "mf" else r.randint(max(1, h["stock_count"][0]), h["stock_count"][1])
    picks = r.sample(ctx.master[kind], min(n, len(ctx.master[kind])))
    ws = [r.uniform(0.3, 1.0) for _ in picks]
    s = sum(ws)
    vals = [int(total * w / s) for w in ws]
    vals[-1] += int(total) - sum(vals)
    for inst, v in zip(picks, vals):
        nav = r.uniform(12, 480) if kind == "mf" else r.uniform(80, 3500)
        p.holdings.append({"isin": inst["isin"], "name": inst["name"], "kind": kind, "units": round(v / nav, 3),
                           "value": v, "source": source, "unknown_isin": False, "at": t})
        p.integ_call(ctx, t + SECS(r.randint(1, 30)), "accord", "isin_lookup", "ok")


# ---------------------------------------------------------------- the spine

def spine_steps(p, ctx):
    T = p.T
    steps = []

    def add(sid, section, kind, fields=None, item=None):
        steps.append({"sid": sid, "section": section, "kind": kind, "fields": fields or [], "item": item})
    add("D01", "family", "list", ["members", "has_dependants", "partner_earns", "pets"])
    for m in p.members[1:]:
        add("D01a", "family", "detail", item=m)
    add("D12a", "family", "relief")
    for i, q in enumerate("abcdefgh"):
        add("D08" + q, "risk", "tap", ["rpq_answers"] if q == "h" else [], item=i)
    add("D09", "risk", "tap", ["risk_band"])
    add("D12b", "risk", "relief")
    add("D05a", "income", "num", ["take_home"])
    if p.partner and p.partner["earns"]:
        add("D05b", "income", "num", ["partner_take_home"])
    if T["investment_property_value"]:
        add("D05c", "income", "num", ["rental_income"])
    add("D05d", "income", "num", ["other_income"])
    add("D12c", "income", "relief")
    add("D06a", "expenses", "num", ["total_outgoings"])
    add("D06b", "expenses", "num", ["bucket_fixed", "bucket_variable", "bucket_guilt_free"])
    add("D06c", "expenses", "tap", ["month_end_pattern"])
    add("D06d", "expenses", "num", ["current_sip"])
    add("D12d", "expenses", "relief")
    add("D02", "investments", "list")
    for sid, fields in D02_TYPES:
        if any(truth_value(p, f) is not None for f in fields):
            add(sid, "investments", "num", [f for f in fields if truth_value(p, f) is not None])
    add("D12e", "investments", "relief")
    add("D03", "loans", "list", ["has_loans", "credit_card_balance", "informal_loans"])
    for i in range(len(T["loans"])):
        add("D03a", "loans", "detail", item=i)
    add("D12f", "loans", "relief")
    add("D04", "insurance", "list", ["term_status", "health_status"])
    if T["term"]:
        add("D04a", "insurance", "detail", ["term_sum_assured", "term_premium", "term_cover_until_age"])
    if T["health"]:
        add("D04b", "insurance", "detail", ["health_type", "health_sum_insured", "health_floater", "health_premium"])
    if T["other_policies"]:
        add("D04c", "insurance", "detail", ["other_policies"])
    add("D12g", "insurance", "relief")
    add("D07", "goals", "list", ["goals"])
    for i in range(len(T["goals"])):
        add("D07a", "goals", "detail", item=i)
    add("D07b", "goals", "tap", ["work_optional_age"])
    add("D12h", "goals", "relief")
    return steps


def step_seconds(r, st):
    """Long enough for every event the screen emits (answer_num spends at most 20 s plus 15 s a field)."""
    k = st["kind"]
    n = 3 if st["sid"] == "D03a" else max(1, len(st["fields"]))
    if k == "num":
        return 25 + 16 * n + r.randint(5, 40)
    if k == "detail":
        return 30 + 16 * n + r.randint(5, 60)
    if k == "list":
        return r.randint(10, 40)
    if k == "tap":
        return r.randint(5, 15)
    return r.randint(3, 8)


def place(p, ctx, steps, t_start, t_end):
    """Session times for the steps: sessions break at relief cards; the first starts at t_start, the last ends
    about t_end."""
    r = p.r
    jr = ctx.cfg["journey_rates"]
    for st in steps:
        st["hes"] = 0
        if st["kind"] in ("num", "detail") and r.random() < jr["hesitation_share"]:
            st["hes"] = 45
            if r.random() < jr["hesitation_next"]:
                st["hes"] = 90
                if r.random() < jr["hesitation_next"]:
                    st["hes"] = 120
        st["secs"] = step_seconds(r, st) + st["hes"]
    breaks = [i for i, st in enumerate(steps[:-1]) if st["kind"] == "relief"]
    span = days_between(t_start, t_end) if t_end else 0
    kmax = 1 + len(breaks)
    k = pick(r, [(1, 0.25), (2, 0.3), (3, 0.25), (4, 0.12), (5, 0.08)])
    if span < 0.3:
        k = 1
    elif span < 1.5:
        k = min(k, 2)
    k = min(k, kmax)
    cut = sorted(r.sample(breaks, k - 1)) if k > 1 else []
    sessions, cur = [], []
    for i, st in enumerate(steps):
        cur.append(st)
        if i in cut:
            sessions.append(cur)
            cur = []
    if cur:
        sessions.append(cur)
    durs = [sum(st["secs"] for st in s) for s in sessions]
    starts = [t_start]
    if len(sessions) > 1:
        last_start = t_end - SECS(durs[-1]) if t_end else t_start + DAYS(r.uniform(1, 5))
        lo = t_start + SECS(durs[0] + 600)
        if last_start <= lo:
            last_start = lo + MINS(30)
        mids = sorted(r.uniform(0, 1) for _ in range(len(sessions) - 2))
        for m in mids:
            starts.append(lo + (last_start - lo) * m)
        starts.append(last_start)
        for i in range(1, len(starts)):
            s = starts[i]
            last = i == len(starts) - 1
            if s.hour < 7 and not last:
                s = s.replace(hour=7 + r.randint(0, 3))
                if t_end and s + SECS(durs[i]) > last_start:
                    s = starts[i]
            if s <= starts[i - 1] + SECS(durs[i - 1]):
                s = starts[i - 1] + SECS(durs[i - 1] + 300)
            starts[i] = s
    out = []
    for s, sess in zip(starts, sessions):
        t = s
        for j, st in enumerate(sess):
            out.append((st, t, j == len(sess) - 1 and s is not starts[-1]))
            t += SECS(st["secs"])
    return out


def choose_kind(p, ctx, f):
    r = p.r
    fc = ctx.fields[f]
    allowed = [KIND_OF_PRECISION[x] for x in fc.get("precision", ["exact"])]
    if p.force_band == f and "band" in allowed:
        return "band"
    if p.force_not_sure == f and "not_sure" in allowed:
        return "not_sure"
    if len(allowed) == 1:
        return allowed[0]
    mix = ctx.cfg["fields"]["precision_mix"][fc.get("lead", "exact")]
    w = dict((KIND_OF_PRECISION[k], v) for k, v in mix.items() if KIND_OF_PRECISION[k] in allowed)
    return pick(r, w)


def answer_num(p, ctx, st, t, fields, with_hes=True):
    """One number screen: hesitation, a ladder tap, then set, band, exact or skip for each field."""
    r, sid = p.r, st["sid"]
    if with_hes:
        for hs, sheet in ((45, "D11a"), (90, "D11b"), (120, "D11c")):
            if st.get("hes", 0) >= hs:
                p.sev(ctx, t + SECS(hs), sid, "hesitation_%d" % hs)
                p.view(ctx, t + SECS(hs + 1), sheet)
        t = t + SECS(st.get("hes", 0) + r.randint(5, 20))
    unit_kind = None
    for f in fields:
        truth = truth_value(p, f)
        fc = ctx.fields[f]
        if truth is None:
            set_dec(p, f, "none", "manual", sid, t)
            p.sev(ctx, t, sid, "set", field=f, source="manual", precision="exact", value="none")
            continue
        fed = p.fed.get(f)
        if fed and fed["at"] <= t:
            if r.random() < ctx.cfg["fields"]["aa_override_locked_share"]:
                set_dec(p, f, "exact", "manual", sid, t, locked=True)
                p.sev(ctx, t, sid, "exact_entered", field=f)
                p.sev(ctx, t, sid, "set", field=f, source="manual", precision="exact", overridden=fed["source"])
            else:
                set_dec(p, f, "exact", fed["source"], fed["screen"], fed["at"])
                p.sev(ctx, t, sid, "set", field=f, source=fed["source"], precision="exact", confirmed=True)
            t += SECS(r.randint(3, 12))
            continue
        if fc.get("unit") == "buckets" and unit_kind:
            kind = unit_kind
        else:
            kind = choose_kind(p, ctx, f)
            if fc.get("unit") == "buckets":
                unit_kind = kind
        if r.random() < ctx.cfg["journey_rates"]["ladder_tap_share"]:
            want = {"exact": ["ladder_typed", "ladder_lookup"], "band": ["ladder_band"],
                    "not_sure": ["ladder_vault"]}[kind]
            for suffix in want:
                if p.sev(ctx, t, sid, suffix, field=f):
                    break
        if kind == "exact":
            p.sev(ctx, t + SECS(4), sid, "exact_entered", field=f)
            p.sev(ctx, t + SECS(5), sid, "set", field=f, source="manual", precision="exact")
        elif kind == "band":
            p.sev(ctx, t + SECS(4), sid, "band_tapped", field=f)
            p.sev(ctx, t + SECS(5), sid, "set", field=f, source="manual", precision="approx")
        else:
            p.sev(ctx, t + SECS(4), sid, "skip", field=f)
        set_dec(p, f, kind, "manual", sid, t + SECS(5))
        t += SECS(r.randint(4, 15))
    return t


def answer_detail(p, ctx, st, t):
    r, sid = p.r, st["sid"]
    T = p.T
    for hs, sheet in ((45, "D11a"), (90, "D11b"), (120, "D11c")):
        if st.get("hes", 0) >= hs:
            p.sev(ctx, t + SECS(hs), sid, "hesitation_%d" % hs)
            p.view(ctx, t + SECS(hs + 1), sheet)
    t = t + SECS(st.get("hes", 0) + r.randint(5, 20))
    if sid == "D01a":
        return t
    if sid == "D03a":
        loan = T["loans"][st["item"]]
        rec = {"type": loan["type"], "emi": loan["emi"], "lender": loan["lender"],
               "tax_deductible": loan["tax_deductible"], "prepayment_allowed": loan["prepayment_allowed"],
               "captured_at": t, "screen_id": "D03a"}
        p.sev(ctx, t, sid, "exact_entered", field="emi")
        p.sev(ctx, t, sid, "set", field="emi", source="manual", precision="exact")
        for sub, lead in (("outstanding", "band"), ("years_left", "band")):
            mix = ctx.cfg["fields"]["precision_mix"][lead]
            kind = pick(r, dict((KIND_OF_PRECISION[k], v) for k, v in mix.items()))
            rec[sub + "_kind"] = kind
            if kind == "exact":
                p.sev(ctx, t + SECS(3), sid, "exact_entered", field=sub)
                p.sev(ctx, t + SECS(4), sid, "set", field=sub, source="manual", precision="exact")
            elif kind == "band":
                p.sev(ctx, t + SECS(3), sid, "band_tapped", field=sub)
                p.sev(ctx, t + SECS(4), sid, "set", field=sub, source="manual", precision="approx")
            else:
                p.sev(ctx, t + SECS(3), sid, "skip", field=sub)
        rec["d13_at"] = None
        p.loan_recs.append(rec)
        return t + SECS(8)
    if sid == "D07a":
        g = T["goals"][st["item"]]
        g["captured_at"] = t
        kind = g["cost_kind"]
        if kind == "exact":
            p.sev(ctx, t, sid, "exact_entered", field="cost_today")
            p.sev(ctx, t + SECS(1), sid, "set", field="cost_today", source="manual", precision="exact")
        elif kind == "band":
            p.sev(ctx, t, sid, "band_tapped", field="cost_today")
            p.sev(ctx, t + SECS(1), sid, "set", field="cost_today", source="manual", precision="approx")
        else:
            p.sev(ctx, t, sid, "skip", field="cost_today")
        return t + SECS(6)
    # D04a, D04b, D04c
    return answer_num(p, ctx, st, t, st["fields"], with_hes=False)


def spine(p, ctx, c):
    """Walk the spine from the first D screen saved to the stop, the gate or the end; set every decision."""
    r = p.r
    p.loan_recs = []
    if not c.get("first_d"):
        return
    steps = spine_steps(p, ctx)
    base = p.base
    stop = None
    if base == "S4" or (base == "S19" and not p.s19_ranges):
        lo, hi = ctx.cfg["journey_rates"]["s4_spine_share"]
        n = max(1, int(len(steps) * r.uniform(lo, hi)))
        stop = n
    if p.tier != "difm" and base == "S18" and not p.force_band:
        cands = [f for f in ("gold", "ppf", "nps", "other_assets", "term_sum_assured", "health_sum_insured",
                             "bucket_fixed", "partner_take_home", "home_value", "total_outgoings", "take_home")
                 if truth_value(p, f) is not None and p.fed.get(f) is None]
        p.force_band = cands[0] if cands else None
    if base == "S19" and p.s19_ranges:
        cands = [f for f in ("take_home", "total_outgoings", "bank_and_deposits", "epf", "mutual_funds")
                 if truth_value(p, f) is not None and p.fed.get(f) is None]
        p.force_not_sure = cands[0] if cands else None
    todo = steps if stop is None else steps[:stop]
    if base in GATE_BASES or (base == "S19" and p.s19_ranges) or p.tier == "difm":
        end = c.get("gate") or c.get("spine_end")
        end = end - MINS(r.uniform(1, 4)) if end else None
    else:
        end = c.get("stop")
    timeline = place(p, ctx, todo, c["first_d"], end)
    first = True
    section_done = set()
    p.spine_end_at = c["first_d"]
    for st, t, breaks in timeline:
        sid = st["sid"]
        if t >= ctx.A - MINS(3):
            break
        p.spine_end_at = t + SECS(st["secs"])
        if first:
            p.tl["first_d"] = t
            first = False
            if p.fed:
                p.view(ctx, t + SECS(8), "A08")
        p.view(ctx, t, sid)
        p.last_screen = sid
        k = st["kind"]
        if k == "num":
            answer_num(p, ctx, st, t, st["fields"])
        elif k == "detail":
            answer_detail(p, ctx, st, t)
        elif sid == "D01":
            set_dec(p, "members", "exact", "manual", "D01", t, value=len(p.members))
            if p.has_dependants:
                set_dec(p, "has_dependants", "exact", "manual", "D01", t, value=True)
            else:
                set_dec(p, "has_dependants", "none", "manual", "D01", t)
            if p.partner:
                set_dec(p, "partner_earns", "exact", "manual", "D01", t, value=p.partner["earns"])
            if r.random() < 0.6:
                set_dec(p, "pets", "exact", "manual", "D01", t, value=p.pets)
        elif sid == "D08h":
            set_dec(p, "rpq_answers", "exact", "manual", "D08h", t, value=8)
            p.rpq_at = t
        elif sid == "D09":
            set_dec(p, "risk_band", "exact", "derived", "D09", t, value=p.T["rpq"]["risk_band"])
        elif sid == "D06c":
            set_dec(p, "month_end_pattern", "exact", "manual", "D06c", t, value=p.T["month_end_pattern"])
        elif sid == "D02":
            for s2, fields in D02_TYPES:
                for f in fields:
                    if truth_value(p, f) is None:
                        set_dec(p, f, "none", "manual", "D02", t)
        elif sid == "D03":
            if p.T["loans"] or p.T["credit_card_balance"] or p.T["informal_loans"]:
                set_dec(p, "has_loans", "exact", "manual", "D03", t, value=True)
            else:
                set_dec(p, "has_loans", "none", "manual", "D03", t)
            for f in ("credit_card_balance", "informal_loans"):
                if truth_value(p, f) is None:
                    set_dec(p, f, "none", "manual", "D03", t)
                else:
                    set_dec(p, f, choose_kind(p, ctx, f), "manual", "D03", t)
            if not p.T["loans"]:
                set_dec(p, "total_emi", "exact", "derived", "D03", t, value=0)
        elif sid == "D04":
            set_dec(p, "term_status", "exact" if p.T["term"] else "none", "manual", "D04", t,
                    value="have" if p.T["term"] else None)
            set_dec(p, "health_status", "exact" if p.T["health"] else "none", "manual", "D04", t,
                    value=p.T["health"]["type"] if p.T["health"] else None)
            if not p.T["other_policies"]:
                set_dec(p, "other_policies", "none", "manual", "D04", t)
        elif sid == "D07":
            if p.T["goals"]:
                set_dec(p, "goals", "exact", "manual", "D07", t, value=len(p.T["goals"]))
            else:
                set_dec(p, "goals", "none", "manual", "D07", t)
        elif sid == "D07b":
            if p.T["work_optional_default"]:
                set_dec(p, "work_optional_age", "default", "default_accepted", "D07b", t, value=60)
            else:
                set_dec(p, "work_optional_age", "exact", "manual", "D07b", t, value=p.T["work_optional_age"])
        if sid == "D12f" or (sid == "D03a" and st["item"] == len(p.T["loans"]) - 1):
            if p.T["loans"] and "total_emi" not in p.dec:
                set_dec(p, "total_emi", "exact", "derived", "D03", t, value=p.T["total_emi"])
        if k == "relief":
            section_done.add(st["section"])
            p.ev(t + SECS(2), "data_progress", sid, step_id=st["section"], pct_complete=progress_pct(p, ctx))
            if breaks and r.random() < ctx.tx["o03_use_share"]:
                chip = pick(r, ctx.tx["o03_chips"])
                p.view(ctx, t + SECS(4), "O03")
                p.ev(t + SECS(8), "return_time_picked", "O03", chip=chip)
                when = o03_time(ctx, r, t, chip)
                if when:
                    p.o03.append((t, when))
    if p.loan_recs and "total_emi" not in p.dec and len(p.loan_recs) == len(p.T["loans"]):
        set_dec(p, "total_emi", "exact", "derived", "D03", p.loan_recs[-1]["captured_at"], value=p.T["total_emi"])
    p.spine_complete = stop is None
    if p.tier == "difm":
        return
    if base in GATE_BASES:
        finish_gate(p, ctx, c)
    elif base == "S19" and p.s19_ranges:
        t = timeline[-1][1] + SECS(20)
        p.view(ctx, t, "D10")
        p.last_screen = "D10"


def o03_time(ctx, r, t, chip):
    if chip == "Tonight":
        w = t.replace(hour=21, minute=0, second=0)
        return w if w > t else None
    if chip == "Tomorrow morning":
        return (t + DAYS(1)).replace(hour=8, minute=0, second=0)
    if chip == "This weekend":
        d = (5 - t.weekday()) % 7 or 7
        return (t + DAYS(d)).replace(hour=10, minute=0, second=0)
    return None


def not_sure_react(p, ctx):
    out = []
    for f, d in p.dec.items():
        fc = ctx.fields.get(f, {})
        if d["kind"] == "not_sure" and fc.get("react") and fc.get("ladder") and not fc.get("no_band"):
            out.append(f)
    for i, rec in enumerate(p.loan_recs):
        for sub in ("outstanding", "years_left"):
            if rec.get(sub + "_kind") == "not_sure":
                out.append("loans[%d].%s" % (i, sub))
    order = dict((f, i) for i, f in enumerate(ctx.fields))
    return sorted(out, key=lambda f: order.get(f, 900))


def finish_gate(p, ctx, c):
    """D10 after the spine; D13 for every not-sure field the React reads; then the gate is met."""
    r = p.r
    gate = c["gate"]
    t = max(gate - MINS(r.uniform(0.8, 2.5)), p.spine_end_at + SECS(r.randint(3, 15)))
    p.view(ctx, t, "D10")
    items = not_sure_react(p, ctx)
    if items:
        t += SECS(r.randint(10, 30))
        p.view(ctx, t, "D13")
        for f in items:
            t += SECS(r.randint(6, 20))
            p.ev(t, "range_picked", "D13", field=f)
            if f.startswith("loans["):
                i = int(f[6:f.index("]")])
                sub = f[f.index(".") + 1:]
                p.loan_recs[i][sub + "_kind"] = "band"
                p.loan_recs[i]["d13_at"] = t
            else:
                set_dec(p, f, "band", "manual", "D13", t, d13=True)
        t += SECS(r.randint(3, 10))
        p.ev(t, "ranges_done", "D13", count=len(items))
        t += SECS(3)
        p.view(ctx, t, "D10")
    gate = max(gate, t + SECS(5))
    p.tl["gate"] = gate
    p.ev(gate, "gate_met", "D10")
    p.last_screen = "D10"
    c["gate"] = gate
    if c.get("built") and c.get("built_on") == "full" and c["built"] <= gate:
        c["built"] = gate + MINS(r.uniform(0.5, 3))
    if c.get("d10"):
        c["d10"] = max(c["d10"], gate + MINS(1))
        p.tl["d10"] = c["d10"]
        p.view(ctx, c["d10"] - SECS(15), "D10")
        p.ev(c["d10"], "data_complete", "D10")
        p.integ_call(ctx, c["d10"] + SECS(2), "engine", "build", "failed", "engine returned an error; plan not built")
        p.view(ctx, c["d10"] + SECS(4), "G01")
        p.ops.append({"type": "engine_failure", "created_at": c["d10"] + MINS(1),
                      "detail": "D10 confirmed; the engine returned an error; no plan"})


def progress_pct(p, ctx):
    gate_fields = [f for f in ctx.gate if f in p.dec]
    done_gate = sum(1 for f in gate_fields if p.dec[f]["kind"] in ("exact", "band", "none", "default"))
    others = [f for f in p.dec if f not in ctx.gate]
    done_other = sum(1 for f in others if p.dec[f]["kind"] in ("exact", "band", "none", "default"))
    if p.tl.get("built"):
        return 100
    total_other = max(1, len(others) + 8)
    return int(min(99, 20 + 60 * done_gate / float(len(ctx.gate)) + 20 * done_other / float(total_other)))


# ---------------------------------------------------------------- the plan and after

def assumptions_at(ctx, t):
    cur = ctx.publishes[0]
    for pu in ctx.publishes:
        if pu["at"] <= t:
            cur = pu
    return cur


def band_fields(p, ctx):
    return sorted(f for f, d in p.dec.items() if d["kind"] == "band" and ctx.fields.get(f, {}).get("react"))


def build_plan(p, ctx, c):
    r = p.r
    built = c["built"]
    partial = c.get("built_on") == "partial"
    p.tl["built"] = built
    p.built_on = "partial" if partial else "full"
    if not partial:
        d10 = built - MINS(r.uniform(0.3, 1.5))
        if d10 <= p.tl["gate"]:
            d10 = p.tl["gate"] + SECS(30)
            built = max(built, d10 + SECS(40))
            p.tl["built"] = built
        p.tl["d10"] = d10
        p.view(ctx, d10 - SECS(20), "D10")
        p.ev(d10, "data_complete", "D10")
    pu = assumptions_at(ctx, built)
    unknown = sum(1 for f, d in p.dec.items() if d["kind"] == "not_sure")
    assumed = sum(1 for f, d in p.dec.items() if d["kind"] == "default")
    bands = band_fields(p, ctx)
    p.integ_call(ctx, built - SECS(2), "engine", "build", "ok")
    p.ev(built, "plan_built", "G01a" if partial else "D10", plan_version="v1",
         assumptions_version=pu["assumptions_version"], instrument_set_version=pu["instrument_set_version"],
         assumed_count=assumed, unknown_count=unknown, built_on=p.built_on, band_count=len(bands))
    if not partial:
        p.view(ctx, built + SECS(3), "G01")
    p.plans.append({"plan_version": "v1", "assumptions_version": pu["assumptions_version"],
                    "instrument_set_version": pu["instrument_set_version"], "built_at": built,
                    "built_on": p.built_on, "band_count": len(bands), "read_at": None, "pdf_downloaded_at": None,
                    "reason": "initial", "accepted_at": built})
    p.sharpen_items = [[built, None, f] for f in bands]
    make_actions(p, ctx, built, c.get("n_actions"))
    read = c.get("read")
    if read:
        read_plan(p, ctx, read)
    starts, dones = c.get("starts"), c.get("dones")
    if starts:
        run_actions(p, ctx, starts, dones)


def read_plan(p, ctx, t):
    r = p.r
    p.tl["read"] = t
    p.view(ctx, t, "G03")
    p.ev(t, "plan_read", "G03")
    p.plans[0]["read_at"] = t
    screens = ["G04", "G05", "G06", "G07", "G09", "G10"] + (["G11", "G12", "G13", "G14"] if p.tier in ("diy", "diwm") else [])
    x = t
    for sid in screens:
        if r.random() < 0.75:
            x = x + SECS(r.randint(30, 180))
            p.view(ctx, x, sid)
    if r.random() < ctx.cfg["journey_rates"]["plan_pdf_downloaded"]:
        x = x + SECS(r.randint(10, 60))
        p.view(ctx, x, "G10")
        p.ev(x, "pdf_downloaded", "G10", plan_version="v1")
        p.plans[0]["pdf_downloaded_at"] = x
        p.integ_call(ctx, x + SECS(5), "ses", "send_email", "ok", "plan PDF")


def make_actions(p, ctx, t, n_wanted=None):
    r = p.r
    A = ctx.cfg["actions"]
    T = p.T
    types = A["types"]
    cand = []
    for k, v in types.items():
        if "p" in v and r.random() < v["p"]:
            cand.append(k)
        elif k == "term_cover" and not T["term"] and p.has_dependants and r.random() < v["p_if_missing"]:
            cand.append(k)
        elif k == "health_cover" and T["health"] and T["health"]["type"] == "Employer only" and r.random() < v["p_if_employer_only"]:
            cand.append(k)
        elif k == "prepay_loan" and T["loans"] and r.random() < v["p_if_loans"]:
            cand.append(k)
        elif k == "exit_fund" and T["assets"]["mutual_funds"] and r.random() < v["p_if_mf"]:
            cand.append(k)
        elif k == "ulip_review" and T["assets"]["ulip_surrender_value"] and r.random() < v["p_if_ulip"]:
            cand.append(k)
    want = n_wanted or A["min"]
    for k in ("sip_start", "emergency_fund", "nominations", "stock_basket", "gold_etf", "health_cover", "term_cover"):
        if len(cand) < want and k not in cand:
            cand.append(k)
    cand = cand[:(n_wanted or A["max"])]
    surplus = T["surplus"]
    for i, k in enumerate(cand):
        amt = None
        if k == "emergency_fund":
            amt = rnd(max(T["total_outgoings"] * 6 - (T["assets"]["bank_and_deposits"] or 0) * 0.5, T["total_outgoings"]), 1000)
        elif k == "sip_start":
            amt = rnd(max(1000, surplus * r.uniform(0.3, 0.7)), 500)
        elif k in ("stock_basket", "gold_etf"):
            amt = rnd(r.uniform(20000, 200000), 1000)
        elif k == "exit_fund":
            amt = rnd((T["assets"]["mutual_funds"] or 0) * r.uniform(0.05, 0.25), 1000)
        elif k == "prepay_loan":
            amt = rnd(r.uniform(50000, 400000), 5000)
        p.actions.append({"type": k, "amount": amt, "due": t + DAYS([0, 30, 60, 240][min(i, 3)]),
                          "channel": types[k]["channel"], "status": "open", "started_at": None, "done_at": None,
                          "verification": None, "verified_at": None})


def run_actions(p, ctx, starts, dones):
    r, A = p.r, ctx.A
    cfgA = ctx.cfg["actions"]
    n = min(len(starts), len(p.actions))
    total = len(p.actions)
    done_count = 0
    order = list(range(total))
    for i in range(n):
        a = p.actions[order[i]]
        s, d = starts[i], dones[i]
        if s > A:
            break
        a["started_at"] = s
        a["status"] = "started"
        p.ev(s, "action_started", "E01", action=a["type"])
        ch = a["channel"]
        x = s + SECS(20)
        if ch == "in_app_mf":
            p.view(ctx, x, "E01")
            if not getattr(p, "ucc_done", False):
                p.view(ctx, x + SECS(30), "E02")
                p.view(ctx, x + SECS(60), "E07")
                p.integ_call(ctx, x + SECS(70), "bse_star", "ucc_register", "ok")
                p.ucc_done = True
            if a["type"] == "sip_start":
                p.view(ctx, x + SECS(90), "E10")
                p.nev(ctx, x + SECS(100), "E10", "mandate_started")
                p.integ_call(ctx, x + SECS(101), "bse_star", "mandate_register", "ok")
                act = s + (d - s) * 0.6
                if act <= A:
                    if r.random() < 0.1:
                        p.nev(ctx, s + (d - s) * 0.3, "E10", "mandate_rejected")
                    p.nev(ctx, act, "E10", "mandate_active")
            else:
                p.view(ctx, x + SECS(90), "E03")
                p.integ_call(ctx, x + SECS(100), "bse_star", "order", "ok")
        elif ch == "smallcase":
            p.view(ctx, x, "E04")
            p.integ_call(ctx, x + SECS(40), "smallcase", "order", "ok")
        else:
            p.view(ctx, x, "E05")
        if d <= A:
            if a["type"] == "sip_start":
                p.view(ctx, d - SECS(30), "E11")
                p.nev(ctx, d - SECS(10), "E11", "sips_registered")
                p.integ_call(ctx, d - SECS(9), "bse_star", "sip_register", "ok")
            done_count += 1
            a["done_at"] = d
            if ch == "outside":
                ver = "self_reported"
                a["status"] = "done"
                if r.random() < cfgA["verified_share_outside"]:
                    vt = d + DAYS(r.uniform(3, 20))
                    if vt <= A:
                        a["status"], a["verified_at"] = "verified", vt
                        p.verified_actions.append(vt)
            else:
                ver = "platform"
                a["status"] = "verified"
                a["verified_at"] = d
                p.verified_actions.append(d)
            a["verification"] = ver
            p.view(ctx, d, "E06")
            p.ev(d + SECS(2), "action_done", "E06", done_count=done_count, total_count=total,
                 verified=ver != "self_reported", verification="aa_verified" if ver == "platform" and r.random() < 0.3 else ver)
            if a["type"] == "sip_start" and r.random() < cfgA["missed_sip_share"]:
                ms = d + DAYS(r.uniform(25, 60))
                if ms <= A:
                    a["missed_sip_at"] = ms
                    p.missed_sips.append(ms)
    starts_done = [a for a in p.actions if a["started_at"]]
    if starts_done:
        p.tl["first_action"] = min(a["started_at"] for a in starts_done)
    if all(a["done_at"] for a in p.actions):
        p.tl["all_done"] = max(a["done_at"] for a in p.actions)


def book_call(p, ctx, bk, slot, outcome, topic=None, rebook_of=None):
    r = p.r
    adv = r.choice(ctx.advisers)
    topic = topic or r.choice(ctx.cfg["calls"]["topics"])
    call = {"booked_at": bk, "slot": slot, "adviser_id": adv, "topic": topic,
            "note": r.choice([None, None, "Want to go over my SIPs", "Not sure about the term cover", "New job next month"]),
            "outcome": outcome, "ended_at": slot + MINS(ctx.tm["call_minutes"]) if outcome != "booked" else None,
            "cancelled_at": None, "notes": None, "input_changes": [], "rebook_of": rebook_of,
            "same_adviser_requested": False, "purchase": None}
    if p.tier == "diy":
        pt = bk - MINS(r.uniform(2, 6))
        p.view(ctx, pt, "K04")
        p.nev(ctx, pt + SECS(30), "K04", "call_purchased")
        p.integ_call(ctx, pt + SECS(40), "razorpay", "a_la_carte", "ok")
        call["purchase"] = {"at": pt + SECS(40), "amount": "Rs ___", "receipt": "RCPT-SEED-%05d-%d" % (p.idx, len(p.alc) + 1)}
        p.alc.append(call["purchase"])
    p.view(ctx, bk - SECS(40), "K01")
    p.view(ctx, bk - SECS(15), "K05")
    p.ev(bk, "call_booked", "K01", slot=iso(slot), adviser_id=adv, topic=topic, tier=p.tier,
         summary="call booked: %s" % topic.lower())
    p.view(ctx, bk + SECS(3), "K02")
    p.calls.append(call)
    if outcome == "completed" and slot + MINS(45) <= ctx.A:
        end = slot + MINS(ctx.tm["call_minutes"])
        call["notes"] = "Walked through %s; next step agreed." % topic.lower()
        p.view(ctx, end + MINS(2), "K03")
        p.ev(end + MINS(2), "call_completed", "K03", slot=iso(slot), adviser_id=adv, summary=call["notes"])
    elif outcome == "no_show" and slot + MINS(20) <= ctx.A:
        p.ev(slot + MINS(20), "no_show", "K01", slot=iso(slot), adviser_id=adv, summary="client did not join")
        p.nev(ctx, slot + MINS(20), "K01", "call_no_show", topic=topic)
    elif outcome == "cancelled":
        call["cancelled_at"] = bk + (slot - bk) * r.uniform(0.2, 0.9)
        call["ended_at"] = None
    return call


def call_slot(ctx, r, bk, lo, hi):
    s = bk + DAYS(r.uniform(lo, hi))
    return s.replace(hour=r.choice(ctx.tx["call_hours_ist"]), minute=r.choice([0, 30]), second=0, microsecond=0)


def overlays(p, ctx, c):
    r, A, tgt = p.r, ctx.A, p.target
    if tgt == "S21":
        bk, slot = c["s21_call"]
        call = book_call(p, ctx, bk, slot, "completed")
        input_changes(p, ctx, call)
    if tgt == "S7":
        lo = max(c["paid"] + HOURS(2), A - DAYS(6), c.get("built", c["paid"]) + HOURS(1))
        bk = lo + (A - MINS(5) - lo) * r.uniform(0.05, 0.95)
        slot = call_slot(ctx, r, bk, 1, 7)
        while slot <= A:
            slot += DAYS(1)
        book_call(p, ctx, bk, slot, "booked")
    if tgt == "S20":
        base_t = max(c["paid"] + HOURS(3), c.get("built", c["paid"]))
        two = "second_no_show" in p.flags
        span = days_between(base_t, A)
        for _ in range(600):
            s2 = A - DAYS(r.uniform(0.1, max(0.2, min(10.0, span - (3.2 if two else 1.2)))))
            s2 = s2.replace(hour=r.choice(ctx.tx["call_hours_ist"]), minute=r.choice([0, 30]), second=0)
            if s2 + MINS(20) > A - MINS(5):
                continue
            rb = s2 - DAYS(r.uniform(1.0, 5.0))
            if "second_no_show" in p.flags:
                s1 = rb - DAYS(r.uniform(0.05, 2.0))
                s1 = s1.replace(hour=r.choice(ctx.tx["call_hours_ist"]), minute=r.choice([0, 30]), second=0)
                b1 = s1 - DAYS(r.uniform(1.0, 5.0))
                if b1 <= base_t or s1 + MINS(20) >= rb:
                    continue
                first = book_call(p, ctx, b1, s1, "no_show")
                book_call(p, ctx, rb, s2, "no_show", topic=first["topic"], rebook_of=0)
                p.second_no_show_at = s2 + MINS(20)
            else:
                if rb <= base_t:
                    continue
                book_call(p, ctx, rb, s2, "no_show")
            break
        else:
            raise RuntimeError("no S20 call history for person %d" % p.idx)
    if tgt == "S24":
        t = c["refund_at"]
        sub = p.subs[0]
        p.view(ctx, t - MINS(2), "H09")
        p.view(ctx, t - MINS(1), "Q03")
        p.view(ctx, t, "Q03a")
        reason = r.choice(["Not what I expected", "Too expensive for me right now", "I will do it myself",
                           "Found an adviser elsewhere"])
        sub.update(status="cancelled", cancel_reason=reason, refund_requested=True,
                   refund_status="pending (brief H5: to be decided)", ended_at=t)
        p.ev(t, "cancelled", "Q03a", reason=reason, refund_requested=True)
        p.tl["refund"] = t
        p.ops.append({"type": "refund_request", "created_at": t + MINS(1), "detail": "refund requested: %s" % reason})
    if tgt == "S25":
        lo = max(c["paid"] + HOURS(3), A - DAYS(10))
        t = lo + (A - MINS(30) - lo) * r.uniform(0.05, 0.95)
        p.view(ctx, t - MINS(1), "H09")
        p.tl["deletion"] = t
        p.ops.append({"type": "deletion_request", "created_at": t + MINS(1),
                      "detail": "deletion requested (H09); regulated records retained"})
    if tgt == "S23":
        due = c["paid"] + DAYS(ctx.tm["annual_days"])
        p.annual.append({"due_at": due, "confirmed_at": None})


def input_changes(p, ctx, call):
    """During a completed call after the plan the adviser types 1 or 2 numbers the person gave as bands; the
    engine re-runs (reason update) and the person accepts the diff."""
    r = p.r
    if r.random() >= ctx.cfg["calls"]["input_change_share"] or not p.tl.get("built"):
        call["notes"] = (call["notes"] or "") + " No input changes; the plan is unchanged."
        return
    end = call["slot"] + MINS(ctx.tm["call_minutes"])
    items = [it for it in p.sharpen_items if it[1] is None and it[0] <= call["slot"]]
    keep = 1 if p.base == "S18" else 0
    k = min(len(items) - keep, r.randint(1, 2))
    if k <= 0:
        call["notes"] = (call["notes"] or "") + " No input changes; the plan is unchanged."
        return
    for it in r.sample(items, k):
        f = it[2]
        it[1] = end - MINS(5)
        set_dec(p, f, "exact", "manual", "K03", end - MINS(5), entered_by=call["adviser_id"])
        call["input_changes"].append(f)
    new_version(p, ctx, end + MINS(1), "update", accept=end + MINS(r.uniform(2, 30)))


def new_version(p, ctx, t, reason, accept=None):
    """A re-run of the plan; versions are numbered later in time order (finalize_versions)."""
    if not p.plans:
        return
    p.integ_call(ctx, t - SECS(2), "engine", "rebuild", "ok")
    p.version_requests.append((t, reason, accept))
    if reason in ("publish", "life_event"):
        p.updates.append({"at": t, "accepted_at": accept if (accept and accept <= ctx.A) else None, "reason": reason})


def finalize_versions(p, ctx):
    for t, reason, accept in sorted(p.version_requests, key=lambda x: x[0]):
        prev = p.plans[-1]["plan_version"]
        v = "v%d" % (len(p.plans) + 1)
        pu = assumptions_at(ctx, t)
        bands = sum(1 for a, c, f in p.sharpen_items if a <= t and (c is None or c > t))
        p.plans.append({"plan_version": v, "assumptions_version": pu["assumptions_version"],
                        "instrument_set_version": pu["instrument_set_version"], "built_at": t, "built_on": p.built_on,
                        "band_count": bands, "read_at": None, "pdf_downloaded_at": None, "reason": reason,
                        "accepted_at": accept})
        p.ev(t, "plan_updated", "H05", from_version=prev, to_version=v, reason=reason)
        if accept and accept <= ctx.A:
            p.view(ctx, accept - SECS(20), "H05")
            p.ev(accept, "update_accepted", "H05", to_version=v)
    p.version_requests = []


def renewals(p, ctx):
    """Every renewal before the anchor; 5 percent fail; half recover in grace, half lapse and come back; the
    S12 and S13 targets carry the failure the target needs."""
    r, A = p.r, ctx.A
    tm = ctx.tm
    if not p.subs:
        return
    P = ctx.cfg["period_mix"]["days"][p.period]
    c = p.chain
    k = 0
    sub = p.subs[0]
    target_k = c.get("fail_k") if p.target in ("S12", "S13") else None
    while True:
        k += 1
        t = sub["start"] + DAYS(P * k)
        if t > A or sub["status"] in ("cancelled", "lapsed"):
            break
        if p.tl.get("refund") and t > p.tl["refund"]:
            break
        if target_k and k == target_k:
            fail(p, ctx, sub, t)
            if p.target == "S12":
                sub["status"], sub["grace_until"] = "failed", t + DAYS(tm["grace_days"])
                sub["retry_count"] = sum(1 for d in (1, 3, 5) if t + DAYS(d) <= A)
                for d in (1, 3, 5):
                    if t + DAYS(d) <= A:
                        pay(p, ctx, sub, t + DAYS(d), "failed", "retry declined")
                p.failures.append({"failed_at": t, "recovered_at": None, "lapsed_at": None, "resubscribed_at": None})
            else:
                la = t + DAYS(tm["grace_days"])
                sub["status"], sub["lapsed_at"], sub["ended_at"] = "lapsed", la, la
                sub["grace_until"] = la
                sub["retry_count"] = 3
                p.ev(la, "lapsed", "Q03c", reason="payment not recovered in grace")
                p.failures.append({"failed_at": t, "recovered_at": None, "lapsed_at": la, "resubscribed_at": None})
            break
        if target_k is None and r.random() < tm["renewal_fail_rate"] and days_between(t, A) > 1.0:
            fail(p, ctx, sub, t)
            if r.random() < tm["renewal_recover_share"] or days_between(t, A) < tm["grace_days"] + 5:
                rec = t + DAYS(min(uni(r, tm["recover_days"]), days_between(t, A) * 0.8))
                pay(p, ctx, sub, rec, "captured")
                p.ev(rec, "payment_recovered", "Q03b", grace_until=ymd(t + DAYS(tm["grace_days"])))
                p.failures.append({"failed_at": t, "recovered_at": rec, "lapsed_at": None, "resubscribed_at": None})
            else:
                la = t + DAYS(tm["grace_days"])
                rs = la + DAYS(min(uni(r, tm["resubscribe_after_lapse_days"]), days_between(la, A) * 0.8))
                sub["status"], sub["lapsed_at"], sub["ended_at"] = "lapsed", la, la
                p.ev(la, "lapsed", "Q03c", reason="payment not recovered in grace")
                p.view(ctx, rs - MINS(2), "Q02")
                p.failures.append({"failed_at": t, "recovered_at": None, "lapsed_at": la, "resubscribed_at": rs})
                sub = subscribe(p, ctx, rs, resub=True)
                k = 0
        else:
            pay(p, ctx, sub, t, "captured")
            sub["renewals"].append(t)


def fail(p, ctx, sub, t):
    pay(p, ctx, sub, t, "failed", "mandate debit failed")
    p.ev(t, "payment_failed", "Q03b", grace_until=ymd(t + DAYS(ctx.tm["grace_days"])))


def consents(p, ctx):
    """AA consents expire after 90 days; they are renewed around expiry, except the S15 target's last one."""
    r, A = p.r, ctx.A
    if not p.consents or p.consents[-1]["status"] != "active":
        return
    while True:
        cur = p.consents[-1]
        exp = cur["expires_at"]
        if exp > A:
            break
        if p.target == "S15":
            cur["status"] = "expired"
            break
        lo, hi = ctx.tm["consent_renew_days_around_expiry"]
        rn = exp + DAYS(r.uniform(lo, hi))
        if rn <= cur["connected_at"] + DAYS(30):
            rn = exp - DAYS(r.uniform(1, 5))
        if rn > A:
            rn = exp + (A - exp) * r.uniform(0.1, 0.9) if exp < A else A - MINS(30)
        cur["renewed_at"] = rn
        cur["status"] = "renewed"
        p.view(ctx, rn - SECS(30), "A06")
        new_exp = rn + DAYS(ctx.tm["consent_days"])
        p.integ_call(ctx, rn, "finvu", "consent_create", "ok")
        p.ev(rn, "aa_connected", "A06", institutions_ok=cur["institutions_ok"], institutions_failed=[],
             consent_expiry=ymd(new_exp), renewal=True)
        p.consents.append({"handle": "CONSENT-SEED-%05d-%d" % (p.idx, len(p.consents) + 1), "status": "active",
                           "connected_at": rn, "expires_at": new_exp, "renewed_at": None,
                           "institutions_ok": cur["institutions_ok"], "institutions_failed": [], "fetched_at": rn})
    if p.consents[-1]["status"] == "expired":
        p.aa_status = "expired"


def reviews(p, ctx):
    """Quarterly reviews from the plan's build; opened within 13 days except the S22 target's last one."""
    r, A = p.r, ctx.A
    if not p.tl.get("built") or p.tier not in ("diy", "diwm"):
        return
    every = ctx.tm["review_every_days"]
    k = 0
    while True:
        k += 1
        g = p.tl["built"] + DAYS(every * k)
        if g > A:
            break
        rid = "RV-%05d-%d" % (p.idx, k)
        p.ev(g, "review_due", "Q01", review_id=rid)
        p.integ_call(ctx, g + SECS(5), "finvu", "fi_fetch", "ok") if p.path == "aa" and p.aa_status in ("connected", "partial") else None
        last = p.tl["built"] + DAYS(every * (k + 1)) > A
        if last and p.target == "S22":
            p.reviews.append({"id": rid, "generated_at": g, "opened_at": None})
            break
        hi = min(uni(r, ctx.tm["review_open_days"]), days_between(g, A) * 0.9)
        if days_between(g, A) < ctx.tm["review_ignored_after_days"] and r.random() < 0.5:
            p.reviews.append({"id": rid, "generated_at": g, "opened_at": None})
            continue
        o = g + DAYS(max(0.01, hi))
        screen = "Q05" if p.s16 else "Q01"
        p.view(ctx, o, screen)
        p.ev(o, "review_opened", screen, review_id=rid)
        p.ev(o + MINS(3), "review_accepted", screen, review_id=rid)
        p.ev(o + MINS(3), "review_done", "Q01", review_id=rid)
        p.reviews.append({"id": rid, "generated_at": g, "opened_at": o})
        new_version(p, ctx, o + MINS(4), "review", accept=o + MINS(5))


def publishes(p, ctx):
    """Logic-panel publishes after the build re-run the plan (reason publish); accepted in days, except the S11
    target's last one."""
    r, A = p.r, ctx.A
    if not p.tl.get("built") or p.tier not in ("diy", "diwm"):
        return
    for i, pu in enumerate(ctx.publishes):
        if pu.get("initial") or pu["at"] <= p.tl["built"] or pu["at"] > A:
            continue
        t = pu["at"] + HOURS(r.uniform(1, 12))
        last = i == len(ctx.publishes) - 1
        if last and p.target == "S11":
            new_version(p, ctx, t, "publish", accept=None)
            continue
        acc = t + DAYS(min(uni(r, ctx.cfg["publishes"]["accept_days"]), days_between(t, A) * 0.9))
        new_version(p, ctx, t, "publish", accept=acc)


def background_calls(p, ctx):
    """Calls the target does not need: DIWM first and second calls after the plan, DIY a la carte calls,
    and a few before the plan. None of them may leave S7, S20 or S21 standing at the anchor."""
    r, A = p.r, ctx.A
    cc = ctx.cfg["calls"]
    tm = ctx.tm
    if p.target in ("S7", "S20", "S21"):
        return
    base = p.base
    built = p.tl.get("built")
    fa = p.tl.get("first_action")
    # before the plan
    if r.random() < cc["pre_plan_call"] and p.tl.get("first_d"):
        lim = built or A
        bk = p.tl["first_d"] + DAYS(r.uniform(0.2, 4))
        slot = call_slot(ctx, r, bk, 1, 5)
        if slot + MINS(60) < lim and slot + MINS(60) < A:
            book_call(p, ctx, bk, slot, "completed")
    if not built or base not in ("S9", "S10"):
        return
    p1 = cc["first_call"]["diwm"] if p.tier == "diwm" else cc["first_call"]["diy"]
    if r.random() < p1:
        bk = built + DAYS(uni(r, tm["call_after_built_days"]))
        slot = call_slot(ctx, r, bk, tm["slot_after_booking_days"][0], tm["slot_after_booking_days"][1])
        if slot + MINS(60) < A and (fa is None or slot < fa + DAYS(60)):
            out = pick(r, cc["outcome"])
            call = book_call(p, ctx, bk, slot, out)
            if out == "no_show":
                rb = slot + DAYS(r.uniform(0.1, 2))
                s2 = call_slot(ctx, r, rb, 1, 5)
                if s2 + MINS(60) < A:
                    call2 = book_call(p, ctx, rb, s2, "completed", topic=call["topic"], rebook_of=len(p.calls) - 1)
                    input_changes(p, ctx, call2)
                else:
                    p.calls.pop()
                    drop_last_call_events(p)
            elif out == "completed":
                input_changes(p, ctx, call)
            if p.tier == "diwm" and r.random() < cc["second_call_diwm"]:
                bk2 = slot + DAYS(r.uniform(14, 60))
                s3 = call_slot(ctx, r, bk2, 1, 7)
                if s3 + MINS(60) < A:
                    call3 = book_call(p, ctx, bk2, s3, "completed")
                    input_changes(p, ctx, call3)


def drop_last_call_events(p):
    """Remove the events of a no-show that would stand at the anchor (the rebook did not fit)."""
    keep = []
    cut = False
    for e in reversed(p.events):
        if not cut and e[2] in ("no_show", "call_no_show"):
            cut = True
            continue
        keep.append(e)
    p.events = list(reversed(keep))


# ---------------------------------------------------------------- DIFM

def journey_difm(p, ctx):
    r, A = p.r, ctx.A
    cfg = ctx.cfg
    created = ctx.at_day(r, r.uniform(10, 170))
    claim = created + DAYS(uni(r, cfg["difm"]["claim_days"]))
    if claim >= A - HOURS(6):
        claim = created + HOURS(r.uniform(2, 20))
    p.created_at = created
    p.tl.update(lead=created, otp=claim.replace(microsecond=0), difm_created=created)
    p.ops.append({"type": "difm_provisioning", "created_at": created, "detail": "DIFM household created from admin (M12)",
                  "resolved_at": claim})
    p.kyc_status = "verified (assisted onboarding, M12)"
    p.pan_known = True
    entry_events(p, ctx, p.tl["otp"])
    p.view(ctx, claim + MINS(2), "O01")
    p.view(ctx, claim + MINS(3), "O02")
    p.cas_typed_instead = False
    c = {"paid": claim, "onb": claim + MINS(5)}
    if p.path == "aa":
        c["aa_at"] = c["onb"] + MINS(2)
        c["fetch_at"] = c["aa_at"] + MINS(3)
    if p.path == "cas":
        c["cas_req"] = c["onb"] + MINS(2)
        c["cas_up"] = c["cas_req"] + HOURS(r.uniform(1, 30))
        c["cas_parsed"] = c["cas_up"] + MINS(2)
    onboarding(p, ctx, c)
    ready = c.get("cas_parsed") or c["onb"]
    fd = ready + MINS(r.uniform(3, 30))
    span = min(days_between(fd, A) * 0.8, r.uniform(1, 30))
    c["first_d"] = fd
    c["spine_end"] = fd + DAYS(max(0.09, span))
    p.chain = c
    p.base = "S14"
    spine(p, ctx, c)
    p.tl["gate"] = None
    k = 1
    while True:
        rv = claim + DAYS(ctx.cfg["nudges"]["difm_review_every_days"] * k)
        if rv > A + DAYS(90):
            break
        p.difm_reviews.append(rv)
        k += 1
    consents(p, ctx)


# ---------------------------------------------------------------- global selections that need data

def select_after(people, ctx, R, info):
    ug = info["ugly"]
    paid = [p for p in people if p.layer == "paid"]
    # life events (Q06) among read plans with room after the read
    pool = [p for p in paid if p.tl.get("read") and p.tier != "difm" and p.target not in ("S11",)
            and days_between(p.tl["read"], ctx.A) > 12]
    for p in R.sample(pool, min(ug["life_event"], len(pool))):
        life_event(p, ctx)
    # sharpen loop (G03 to G14) among read plans with band fields left
    pool = [p for p in paid if p.tl.get("read") and p.tier != "difm"
            and len([i for i in p.sharpen_items if i[1] is None]) > (1 if p.base == "S18" else 0)
            and days_between(p.tl["read"], ctx.A) > 1 and p.target not in ("S11",)]
    for p in R.sample(pool, min(ug["sharpen"], len(pool))):
        sharpen(p, ctx)
    info["realised_life_event"] = sum(1 for p in paid if getattr(p, "life_event_at", None))
    info["realised_sharpen"] = sum(1 for p in paid if getattr(p, "sharpen_count", 0))


def life_event(p, ctx):
    r, A = p.r, ctx.A
    chips = ctx.cfg["life_events"]["chips"]
    t = p.tl["read"] + DAYS(r.uniform(5, days_between(p.tl["read"], A) - 2))
    chip = r.choice(sorted(chips))
    p.view(ctx, t, "Q06")
    p.ev(t + SECS(20), "life_event_reported", "Q06", chips=[chip])
    p.view(ctx, t + SECS(30), "Q06a")
    x = t + SECS(60)
    for sid in chips[chip]:
        p.view(ctx, x, sid)
        if sid == "D05a" and "take_home" in p.dec:
            p.T["take_home"] = rnd(p.T["take_home"] * r.uniform(1.05, 1.2), 100)
            set_dec(p, "take_home", "exact", "manual", "D05a", x, via="Q06a")
            p.sev(ctx, x + SECS(10), "D05a", "exact_entered", field="take_home")
            p.sev(ctx, x + SECS(11), "D05a", "set", field="take_home", source="manual", precision="exact")
        elif sid == "D02a" and "bank_and_deposits" in p.dec and p.T["assets"]["bank_and_deposits"]:
            room = 2.95 * p.T["gross"] - p.T["corpus"]
            add = min(p.T["assets"]["bank_and_deposits"] * r.uniform(0.05, 0.3), max(0, room))
            p.T["assets"]["bank_and_deposits"] = rnd(p.T["assets"]["bank_and_deposits"] + add, 100)
            p.T["corpus"] = sum(v or 0 for v in p.T["assets"].values()) + (p.T["investment_property_value"] or 0)
            src = p.dec["bank_and_deposits"]["source"]
            set_dec(p, "bank_and_deposits", "exact", src if src == "aa" else "manual", "D02a", x, via="Q06a")
            p.sev(ctx, x + SECS(11), "D02a", "set", field="bank_and_deposits", source=src, precision="exact")
        x += SECS(r.randint(30, 90))
    p.ev(x, "life_event_rerun", "Q06a", chips=[chip])
    new_version(p, ctx, x + SECS(5), "life_event", accept=x + MINS(r.uniform(1, 20)))
    p.life_event_at = t
    p.life_event_chip = chip


def sharpen(p, ctx):
    r, A = p.r, ctx.A
    open_items = [i for i in p.sharpen_items if i[1] is None]
    keep = 1 if p.base == "S18" else 0
    k = min(len(open_items) - keep, r.randint(ctx.cfg["sharpen"]["fields_per_person"][0], ctx.cfg["sharpen"]["fields_per_person"][1]))
    if k <= 0:
        return
    t = p.tl["read"] + DAYS(r.uniform(0.5, max(0.6, days_between(p.tl["read"], A) - 0.5)))
    if t >= A:
        return
    n = 0
    for it in r.sample(open_items, k):
        f = it[2]
        g = SHARPEN_SCREEN.get(f, "G03")
        sid = ctx.fields[f]["screen"]
        p.view(ctx, t, g)
        p.nev(ctx, t + SECS(10), g, "sharpen_opened", field=f)
        p.view(ctx, t + SECS(15), sid)
        p.sev(ctx, t + SECS(40), sid, "exact_entered", field=f)
        p.sev(ctx, t + SECS(41), sid, "set", field=f, source="manual", precision="exact")
        set_dec(p, f, "exact", "manual", g, t + SECS(41), via=sid)
        it[1] = t + SECS(41)
        p.nev(ctx, t + SECS(45), g, "sharpen_saved", field=f)
        new_version(p, ctx, t + SECS(50), "sharpen", accept=t + SECS(80))
        n += 1
        t += MINS(r.uniform(2, 20))
        if t >= A:
            break
    p.sharpen_count = n


def settle_prospects(people, ctx, R, info):
    """The DIFM prospect rule (D02 investable total over the threshold) holds for exactly the configured count."""
    thr = ctx.cfg["difm_threshold"]["value_rs"]
    inv = ctx.cfg["fields"]["investable"]
    need = info["ugly"]["difm_prospect_rule"]
    elig = [p for p in people if p.layer == "paid" and p.tier in ("diy", "diwm")
            and all(f in p.dec for f in ("bank_and_deposits", "mutual_funds", "stocks", "epf"))]

    def total(p):
        s = 0
        for f in inv:
            d = p.dec.get(f)
            if d and d["kind"] in ("exact", "band"):
                s += stored(ctx, p, f, d)[0] or 0
        return s
    ranked = sorted(elig, key=lambda p: (-(sum(v or 0 for v in p.T["assets"].values())), p.idx))
    chosen = set(id(p) for p in ranked[:need])
    for p in elig:
        want_over = id(p) in chosen
        for _ in range(40):
            s = total(p)
            if want_over and s > thr * 1.02:
                break
            if not want_over and s <= thr * 0.98:
                break
            f = (thr * 1.25 / max(s, 1)) if want_over else (thr * 0.85 / max(s, 1))
            f = clamp(f, 0.5, 2.0)
            cap = 3.0 * p.T["gross"] / max(1.0, sum(v or 0 for v in p.T["assets"].values()) + (p.T["investment_property_value"] or 0))
            if want_over:
                f = min(f, max(1.0, cap * 0.98))
                if f <= 1.0001:
                    p.T["gross"] = rnd(p.T["gross"] * 1.15, 10000)
                    f = 1.1
            for a in inv:
                if p.T["assets"].get(a):
                    p.T["assets"][a] = rnd(p.T["assets"][a] * f, 100)
            for h in p.holdings:
                h["value"] = int(h["value"] * f)
        p.prospect = "rule" if total(p) > thr else None
        p.T["corpus"] = sum(v or 0 for v in p.T["assets"].values()) + (p.T["investment_property_value"] or 0)
    info["realised_prospects_rule"] = sum(1 for p in elig if p.prospect == "rule")
    # manual flags after a call (below the threshold)
    pool = [p for p in people if p.layer == "paid" and p.tier in ("diy", "diwm") and not p.prospect
            and any(c["outcome"] == "completed" and c["ended_at"] and c["ended_at"] <= ctx.A for c in p.calls)]
    for p in R.sample(pool, min(info["ugly"]["difm_prospect_manual"], len(pool))):
        p.prospect = "manual"
        last = max(c["ended_at"] for c in p.calls if c["outcome"] == "completed" and c["ended_at"] and c["ended_at"] <= ctx.A)
        p.prospect_at = last + MINS(10)
    info["realised_prospects_manual"] = sum(1 for p in people if p.prospect == "manual")


def settle_reveal(people, ctx, R, info):
    """R03, R04 and R05 answers; R04 agrees with the stored D02 total except for the plausibility-flag people."""
    cfg = ctx.cfg
    rb = cfg["reveal_bands"]
    inc, cor, sav = rb["income"], rb["corpus"], rb["savings"]
    with_d02 = [p for p in people if p.layer == "paid" and p.tier in ("diy", "diwm")
                and all(f in p.dec for f in ASSETS)]
    flagged = set(id(p) for p in R.sample(with_d02, min(info["ugly"]["plausibility"], len(with_d02))))
    for p in people:
        if p.layer == "lead" or not p.T:
            continue
        r = p.r
        G = p.T["gross"]
        i = band_index(G / 1e5, inc["bounds_lakh"])
        if r.random() < rb["misreport"]["income"]:
            i = int(clamp(i + r.choice([-1, 1]), 0, len(inc["labels"]) - 1))
        p.income_band = i
        p.income_exact = rnd(G, 50000) if r.random() < rb["exact_share"]["income"] else None
        if p.income_exact:
            p.income_band = band_index(p.income_exact / 1e5, inc["bounds_lakh"])
        corpus_total = None
        if id(p) in set(id(x) for x in with_d02):
            corpus_total = 0
            for f in ASSETS + ["investment_property_value"]:
                d = p.dec.get(f)
                if d and d["kind"] in ("exact", "band"):
                    corpus_total += stored(ctx, p, f, d)[0] or 0
            j = band_index(corpus_total / 1e5, cor["bounds_lakh"])
            if id(p) in flagged:
                j2 = j + r.choice([-2, -1, 1, 2])
                if j2 < 0 or j2 >= len(cor["labels"]):
                    j2 = j - 1 if j > 0 else j + 1
                j = j2
                p.plausibility_flag = True
            p.corpus_band = j
            p.corpus_exact = None
        else:
            j = band_index(p.T["corpus"] / 1e5, cor["bounds_lakh"])
            if r.random() < rb["misreport"]["corpus_prepaid"]:
                j = int(clamp(j + r.choice([-1, 1]), 0, len(cor["labels"]) - 1))
            p.corpus_band = j
            p.corpus_exact = rnd(p.T["corpus"], 50000) if r.random() < rb["exact_share"]["corpus"] else None
            if p.corpus_exact:
                p.corpus_band = band_index(p.corpus_exact / 1e5, cor["bounds_lakh"])
        p.corpus_total_d02 = corpus_total
        s = band_index(p.T["savings_rate_pct"], sav["bounds_pct"])
        if r.random() < rb["misreport"]["savings"]:
            s = int(clamp(s + r.choice([-1, 1]), 0, len(sav["labels"]) - 1))
        p.savings_band = s
        p.savings_exact = round(p.T["savings_rate_pct"], 1) if r.random() < rb["exact_share"]["savings"] else None
        if p.savings_exact is not None:
            p.savings_band = band_index(p.savings_exact, sav["bounds_pct"])
        p.journey_feel = None if r.random() < rb["journey_feel_skip"] else r.choice(rb["journey_feel"])
        p.aspiration = pick(r, list(zip(rb["aspiration"], cfg["archetypes"][p.arche]["aspiration"])))
        ps = rb["path_stub"]
        n = max(1, ps["at_age"] - p.age)
        sav_y = p.T["surplus"] * 12
        now = p.T["corpus"] * (1 + ps["now_return"]) ** n + sav_y * (((1 + ps["now_return"]) ** n - 1) / ps["now_return"])
        yes = p.T["corpus"] * (1 + ps["yes_return"]) ** n + sav_y * (((1 + ps["yes_return"]) ** n - 1) / ps["yes_return"])
        p.path_now_band = ps["band_labels"][band_index(now / 1e7, ps["band_bounds_cr"])]
        p.path_yes_band = ps["band_labels"][band_index(yes / 1e7, ps["band_bounds_cr"])]
        if id(p) in flagged:
            p.ops.append({"type": "data_quality", "created_at": p.tl.get("gate") or p.dec["bank_and_deposits"]["at"],
                          "detail": "plausibility: D02 total outside the R04 band given at the reveal"})
    info["realised_plausibility"] = sum(1 for p in people if p.plausibility_flag)


def settle_isins(people, ctx, R, info):
    pool = [(p, i) for p in people for i, h in enumerate(p.holdings)]
    need = info["ugly"]["unknown_isin"]
    for n, (p, i) in enumerate(R.sample(pool, min(need, len(pool)))):
        h = p.holdings[i]
        body = ("INF" if h["kind"] == "mf" else "INE") + "UK%06d" % (500 + n * 37 % 997)
        h["isin"] = isin_check(body)
        h["name"] = "Unrecognised holding %02d" % (n + 1)
        h["unknown_isin"] = True
        p.integ_call(ctx, h["at"] + SECS(40), "accord", "isin_lookup", "failed", "ISIN not in the instrument master")
        p.ops.append({"type": "unknown_isin", "created_at": h["at"] + MINS(2), "detail": "unknown ISIN %s" % h["isin"]})
    info["realised_unknown_isin"] = sum(1 for p in people for h in p.holdings if h["unknown_isin"])


def settle_tickets(people, ctx, R, info):
    tk = ctx.cfg["tickets"]
    A = ctx.A
    paid = [p for p in people if p.layer == "paid"]
    griev = set(id(p) for p in R.sample(paid, min(info["ugly"]["grievance"], len(paid))))
    for p in people:
        r = p.r
        if p.layer == "lead" or p.layer == "S1":
            continue
        share = tk["paid_share"] if p.layer == "paid" else tk["prepaid_share"]
        n = (1 if r.random() < share else 0) + (1 if id(p) in griev else 0)
        start = p.tl.get("paid") or p.tl.get("checkout") or p.tl.get("reveal") or p.tl.get("otp")
        if not start or start >= A - HOURS(3):
            continue
        for k in range(n):
            if id(p) in griev and k == n - 1:
                cat = "grievance"
            elif p.tier in ("diwm", "difm") and r.random() < 0.45:
                cat = "adviser_message"
            else:
                cat = "support"
            t = start + (A - start) * r.uniform(0.05, 0.97)
            t = t.replace(microsecond=0)
            if t.hour < 7:
                t = t.replace(hour=9)
            if t >= A:
                t = A - HOURS(2)
            subj = r.choice(tk["subjects"][cat])
            due = business_days(t, tk["sla_business_days"])
            resolved = None
            if r.random() < tk["resolved_share"]:
                rv = t + (due - t) * r.uniform(0.2, 1.4)
                resolved = rv if rv <= A else None
            p.tickets.append({"category": cat, "subject": subj, "created_at": t, "sla_due": due,
                              "resolved_at": resolved, "status": "resolved" if resolved else "open",
                              "scores_ref": "SCORES-SEED-%05d" % (p.idx * 13 % 99991) if cat == "grievance" else None,
                              "description": "Ticket raised in the app (H07): %s." % subj.lower()})
            p.view(ctx, t - SECS(40), "H07")
            p.ev(t, "ticket_created", "H07", category=cat, ticket_id="(set at write)")
    info["realised_grievance"] = sum(1 for p in people for t in p.tickets if t["category"] == "grievance")


def business_days(t, n):
    d = t
    k = 0
    while k < n:
        d += DAYS(1)
        if d.weekday() < 5:
            k += 1
    return d


def s2_bucket_floor(people, ctx):
    """Every S2 ladder bucket (days since the reveal) holds at least the floor; the youngest buckets are
    filled by re-dating people from the fullest one."""
    b = ctx.tx["s2_ladder_buckets"]
    floor = ctx.tx["s2_bucket_floor"]
    s2 = [p for p in people if p.layer == "S2"]

    def bucket(p):
        return band_index(days_between(p.tl["reveal"], ctx.A), b)
    moved = 0
    for i in range(len(b)):
        have = [p for p in s2 if bucket(p) == i]
        while len(have) < floor:
            counts = collections.Counter(bucket(p) for p in s2)
            donor_bucket = counts.most_common(1)[0][0]
            donor = [p for p in s2 if bucket(p) == donor_bucket][0]
            r = donor.r
            hi = b[i + 1] if i + 1 < len(b) else b[i] + 30
            age = r.uniform(b[i] + 0.05, hi - 0.05)
            rev = ctx.A - DAYS(age)
            otp = rev - DAYS(r.uniform(0.001, 0.3))
            lead = otp - DAYS(r.uniform(0.01, 3))
            donor.tl = {"lead": lead, "otp": otp, "reveal": rev}
            donor.events = []
            donor.integ = []
            donor.created_at = lead
            if donor.on_sheet:
                donor.landing = lead
                donor.email_known_at = lead
            free_events(donor, ctx)
            moved += 1
            have = [p for p in s2 if bucket(p) == i]
    return moved


# ---------------------------------------------------------------- identifiers, owners, contact points

def assign_ids(people, ctx, R):
    people.sort(key=lambda p: (p.created_at, p.idx))
    cp = ctx.cfg["contact_points"]
    serials = list(range(100000))
    R.shuffle(serials)
    used_email = collections.Counter()
    pans = set()
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for n, p in enumerate(people):
        p.pid = "P%05d" % (n + 1)
        p.phone = cp["phone_prefix"] + "%05d" % serials[n]
        base = "%s.%s" % (p.first.lower(), p.last.lower())
        used_email[base] += 1
        p.email_addr = "%s.%03d@%s" % (base, 100 + (used_email[base] * 37 + p.idx) % 900, cp["email_domain"])
        if p.email_known_at:
            p.email = p.email_addr
        if getattr(p, "pan_known", False):
            while True:
                pan = "".join(R.choice(letters) for _ in range(3)) + "P" + p.last[0].upper() + "%04d" % R.randint(0, 9999) + R.choice(letters)
                if pan not in pans:
                    pans.add(pan)
                    break
            p.pan = pan
            born = ctx.A.date().replace(year=ctx.A.year - p.age) - dt.timedelta(days=R.randint(1, 360))
            p.dob = born.isoformat()
    # owners: call-centre advisers by round robin in order of OTP time; DIFM to Harish
    contacts = sorted([p for p in people if p.layer != "lead"], key=lambda p: (p.tl["otp"], p.idx))
    k = 0
    for p in contacts:
        if p.tier == "difm":
            p.owner = ctx.cfg["difm"]["owner"]
        else:
            p.owner = ctx.advisers[k % len(ctx.advisers)]
            k += 1
    for p in people:
        if p.layer == "lead":
            p.owner = None


def reassign(people, ctx, R):
    """A few paid people ask for another adviser; ops reassigns the owner (owner_changed goes back to the app)."""
    A = ctx.A
    pool = [p for p in people if p.layer == "paid" and p.tier in ("diy", "diwm") and days_between(p.tl["paid"], A) > 6]
    n = max(1, rhu(len(pool) * ctx.cfg["ops_queue"]["reassignment_share"]))
    for p in R.sample(pool, min(n, len(pool))):
        t = p.tl["paid"] + (A - p.tl["paid"]) * R.uniform(0.2, 0.9)
        new = R.choice([a for a in ctx.advisers if a != p.owner])
        done = t + DAYS(R.uniform(0.3, 3.0))
        p.ops.append({"type": "reassignment", "created_at": t, "resolved_at": done if done <= A else None,
                      "detail": "client asked for another adviser: %s to %s" % (p.owner, new)})
        if done <= A:
            p.owner = new


# ---------------------------------------------------------------- the resolver

def flags_of(p, ctx):
    """The timestamped flags the resolver reads (what the app must store to compute state on every open)."""
    tl = p.tl
    F = {
        "tier": p.tier if p.layer != "lead" else None,
        "created_at": p.created_at,
        "signed_up_at": tl.get("otp") if p.layer != "lead" else None,
        "reveal_seen_at": tl.get("reveal") if getattr(p, "reveal_upto", 0) == 7 else None,
        "checkout_started_at": tl.get("checkout"),
        "esign_done_at": tl.get("esign"),
        "paid_at": tl.get("paid"),
        "first_d_saved_at": tl.get("first_d") if p.tier in ("diy", "diwm") else None,
        "gate_met_at": tl.get("gate") if p.tier in ("diy", "diwm") else None,
        "d10_confirmed_at": tl.get("d10"),
        "plan_built_at": tl.get("built"),
        "built_on": getattr(p, "built_on", None),
        "plan_read_at": tl.get("read"),
        "sharpen_items": [[a, c] for a, c, f in p.sharpen_items],
        "first_action_started_at": tl.get("first_action"),
        "all_actions_done_at": tl.get("all_done"),
        "calls": [[c["booked_at"], c["slot"], c["outcome"], c["cancelled_at"]] for c in p.calls],
        "updates": [[u["at"], u["accepted_at"]] for u in p.updates],
        "payment_failures": [[f["failed_at"], f["recovered_at"], f["lapsed_at"], f["resubscribed_at"]] for f in p.failures],
        "consents": [[c["connected_at"], c["expires_at"], c["renewed_at"]] for c in p.consents if c["status"] != "failed"],
        "cas": [[c["requested_at"], c["uploaded_at"], c["abandoned_at"]] for c in p.cas],
        "reviews": [[v["generated_at"], v["opened_at"]] for v in p.reviews],
        "annual": [[a["due_at"], a["confirmed_at"]] for a in p.annual],
        "refund_requested_at": tl.get("refund"), "refund_processed_at": None,
        "deletion_requested_at": tl.get("deletion"), "deletion_done_at": None,
        "aa_never_connected": bool(getattr(p, "s16", False)),
    }
    return F


def holds(F, t, ctx):
    """Every state whose predicate holds at t (states.json entry and exit rules, coded by hand)."""
    H = set()

    def by(x):
        return x is not None and x <= t
    tier = F["tier"]
    if tier is None:
        return H
    if tier == "difm":
        if by(F["signed_up_at"]):
            H.add("S14")
    else:
        if by(F["signed_up_at"]) and not by(F["reveal_seen_at"]):
            H.add("S1")
        paid = by(F["paid_at"])
        if not paid:
            if by(F["esign_done_at"]):
                H.add("S2c")
            elif by(F["checkout_started_at"]):
                H.add("S2b")
            elif by(F["reveal_seen_at"]):
                H.add("S2")
        if paid:
            pa = F["paid_at"]
            fd = F["first_d_saved_at"]
            stall = pa + DAYS(7) if (fd is None or fd >= pa + DAYS(7)) else fd + DAYS(7)
            gate = by(F["gate_met_at"])
            built = by(F["plan_built_at"])
            if not gate:
                if t >= stall:
                    H.add("S19")
                elif by(fd):
                    H.add("S4")
                else:
                    H.add("S3")
            elif not built and not by(F["d10_confirmed_at"]) and t < F["gate_met_at"] + DAYS(7):
                H.add("S5")
            if built:
                if not by(F["plan_read_at"]):
                    H.add("S6")
                elif not by(F["first_action_started_at"]):
                    H.add("S8")
                elif not by(F["all_actions_done_at"]):
                    H.add("S9")
                else:
                    H.add("S10")
                if F["built_on"] == "partial" and any(a <= t and (c is None or c > t) for a, c in F["sharpen_items"]):
                    H.add("S18")
                if not by(F["first_action_started_at"]) and any(
                        o == "completed" and call_end(b, s, o, cx) <= t and s > F["plan_built_at"] for b, s, o, cx in F["calls"]):
                    H.add("S21")
            calls = [c for c in F["calls"] if c[0] <= t]
            if any(b <= t < call_end(b, s, o, cx) for b, s, o, cx in calls):
                H.add("S7")
            past = sorted([c for c in calls if o_resolved(c, t)], key=lambda c: c[1])
            if past and past[-1][2] == "no_show" and not any(c[0] > past[-1][1] for c in calls):
                H.add("S20")
            if any(a <= t and not (acc is not None and acc <= t) for a, acc in F["updates"]):
                H.add("S11")
            for fa, rec, la, rs in F["payment_failures"]:
                if fa <= t < fa + DAYS(7) and not (rec is not None and rec <= t):
                    H.add("S12")
                if la is not None and la <= t and not (rs is not None and rs <= t):
                    H.add("S13")
            live = [c for c in F["consents"] if c[0] <= t]
            if live:
                cn, ex, rn = live[-1]
                if ex is not None and ex <= t and not (rn is not None and rn <= t):
                    H.add("S15")
            if any(rq <= t and not (up is not None and up <= t) and not (ab is not None and ab <= t) for rq, up, ab in F["cas"]):
                H.add("S17")
            if any(g + DAYS(14) <= t and not (o is not None and o <= t) for g, o in F["reviews"]):
                H.add("S22")
            if any(d <= t and not (c is not None and c <= t) for d, c in F["annual"]):
                H.add("S23")
    if by(F["refund_requested_at"]) and not by(F["refund_processed_at"]):
        H.add("S24")
    if by(F["deletion_requested_at"]) and not by(F["deletion_done_at"]):
        H.add("S25")
    return H


def call_end(b, s, o, cx):
    """When a booked call stops being S7: the end of the 45-minute slot, the no-show mark 20 minutes in, or the
    cancellation."""
    if o == "cancelled" and cx is not None:
        return cx
    if o == "no_show":
        return s + MINS(20)
    return s + MINS(45)


def o_resolved(c, t):
    b, s, o, cx = c
    return o in ("completed", "no_show") and call_end(b, s, o, cx) <= t


def resolve(H, prev, order):
    for s in order:
        if s in H:
            return s
    return prev


def timer_points(F):
    pts = []
    for k, v in F.items():
        if isinstance(v, dt.datetime):
            pts.append(v)
    for key in ("sharpen_items", "calls", "updates", "payment_failures", "consents", "cas", "reviews", "annual"):
        for row in F[key]:
            for v in row:
                if isinstance(v, dt.datetime):
                    pts.append(v)
    if F["paid_at"]:
        pts.append(F["paid_at"] + DAYS(7))
        if F["first_d_saved_at"]:
            pts.append(F["first_d_saved_at"] + DAYS(7))
    if F["gate_met_at"]:
        pts.append(F["gate_met_at"] + DAYS(7))
    for b, s, o, cx in F["calls"]:
        pts.append(call_end(b, s, o, cx))
    for g, o in F["reviews"]:
        pts.append(g + DAYS(14))
    for fa, rec, la, rs in F["payment_failures"]:
        pts.append(fa + DAYS(7))
    return pts


def history(F, ctx):
    A = ctx.A
    order = ctx.prec_order
    pts = sorted(set(x for x in timer_points(F) if x <= A) | {A})
    cur, base, out, gaps = None, None, [], []
    for t in pts:
        H = holds(F, t, ctx)
        # no predicate: keep the last underlying state (an ended overlay such as a past call is not kept)
        s = resolve(H, base or cur, order)
        if not H and cur is not None:
            gaps.append((t, s))
        if s != cur:
            out.append((t, s))
            cur = s
        if s not in OVERLAY_ENTRY:
            base = s
    return out, gaps


# ---------------------------------------------------------------- decorations: state_enter, nudges, tasks, opens

def decorate(p, ctx):
    r, A, B = p.r, ctx.A, ctx.B
    if p.layer == "lead":
        return
    F = p.F
    hist = p.hist
    prev = None
    for t, s in hist:
        p.ev(t, "state_enter_%s" % s, B.lands(s), state=s, from_state=prev)
        prev = s
    episodes = []
    for i, (t, s) in enumerate(hist):
        end = hist[i + 1][0] if i + 1 < len(hist) else A
        episodes.append((s, t, end))
    p.episodes = episodes
    nudges(p, ctx, episodes)
    tasks(p, ctx, episodes)
    app_opens(p, ctx, episodes)


def state_at(p, t):
    cur = None
    for x, s in p.hist:
        if x <= t:
            cur = s
    return cur


def nudges(p, ctx, episodes):
    r, A, B = p.r, ctx.A, ctx.B
    ncfg = ctx.cfg["nudges"]
    offs = ncfg["offsets"]
    cand = []
    tier = p.tier
    s2_entry = None
    for s, st, en in episodes:
        if s == "S2":
            s2_entry = st
        for step in B.states[s]["ladder"]:
            slot = step["slot"]
            rule = step["tier"]
            if rule != "all" and rule.lower() != tier:
                continue
            o = offs[slot]
            an = o["anchor"]
            dues = []
            if an == "entry":
                if o.get("skip_if_o03") and any(st <= a < en for a, w in p.o03):
                    continue
                dues = [st + HOURS(o["hours"])]
            elif an == "o03":
                dues = [w for a, w in p.o03 if st <= a < en]
            elif an == "slot":
                dues = [c["slot"] + HOURS(o["hours"]) for c in p.calls if st <= c["booked_at"] < en + SECS(1)]
            elif an == "missed_sip":
                dues = [m for m in p.missed_sips if st <= m <= en]
            elif an == "action_verified":
                dues = [v for v in p.verified_actions if st <= v <= en]
            elif an == "plan_anniversary":
                if p.tl.get("built"):
                    dues = [p.tl["built"] + DAYS(365)]
            elif an == "review_in_state":
                dues = [v["generated_at"] for v in p.reviews if st <= v["generated_at"] <= en]
            elif an == "next_sunday":
                d = (6 - st.weekday()) % 7 or 7
                dues = [(st + DAYS(d)).replace(hour=ctx.tx["s18_sunday_hour"], minute=0, second=0)]
            elif an == "entry_monthly":
                x = st + HOURS(o["hours"]) + DAYS(o["every_days"])
                while x <= en:
                    dues.append(x)
                    x += DAYS(o["every_days"])
            elif an == "second_no_show":
                sn = getattr(p, "second_no_show_at", None)
                if sn and abs((sn - st).total_seconds()) < 3600:
                    dues = [sn]
            elif an == "difm_review":
                dues = [d + HOURS(o["hours"]) for d in p.difm_reviews]
            for due in dues:
                if an in ("difm_review",):
                    if due <= A and st <= due <= en:
                        cand.append((due, slot, step["channel"], s, step["link"], en))
                    continue
                if st <= due <= en and due <= A:
                    cand.append((due, slot, step["channel"], s, step["link"], en))
        if s in ncfg["s2_ladder_continues_in"] and s2_entry:
            for slot in ncfg["s2_ladder_slots"]:
                o = offs[slot]
                due = s2_entry + HOURS(o["hours"])
                if st <= due <= en and due <= A:
                    step = [l for l in B.states["S2"]["ladder"] if l["slot"] == slot][0]
                    cand.append((due, slot, step["channel"], s, step["link"], en))
    # the "before" steps that fire ahead of the state they belong to
    for c in p.consents:
        if c["expires_at"] and c["status"] in ("expired", "renewed", "active"):
            due = c["expires_at"] + HOURS(offs["N-S15-7d-before"]["hours"])
            if due <= A and not (c["renewed_at"] and c["renewed_at"] <= due):
                cand.append((due, "N-S15-7d-before", "push", "S15", "A06", c["expires_at"]))
    for a in p.annual:
        for slot in ("N-S23-7d-before", "N-S23-d0", "N-S23-7d-after"):
            due = a["due_at"] + HOURS(offs[slot]["hours"])
            if due <= A:
                step = [l for l in B.states["S23"]["ladder"] if l["slot"] == slot][0]
                cand.append((due, slot, step["channel"], "S23", step["link"], A))
        rq = a["due_at"] - DAYS(7)
        if rq <= A:
            p.ev(rq, "rpq_due", "Q04", due_date=ymd(a["due_at"]))
            p.ev(rq, "agreement_due", "Q04", due_date=ymd(a["due_at"]))
    if getattr(p, "s16", False):
        for v in p.reviews:
            if v["generated_at"] <= A:
                cand.append((v["generated_at"] + MINS(5), "N-S16-review", "whatsapp", "S16", "Q05", A))
    cand.sort(key=lambda x: (x[0], x[1]))
    cap = ncfg["cap"]
    exempt = set(ncfg["cap_exempt"])
    paid_ref = p.tl.get("paid") or (p.tl.get("otp") if p.tier == "difm" else None)
    last = None
    seen = set()
    win = ncfg["send_window"]
    for due0, slot, channel, s, link, en in cand:
        key = (slot, due0)
        if key in seen:
            continue
        seen.add(key)
        due = due0
        if channel != "human call" and not (win["from"] <= due.hour < win["to"]):
            day = due if due.hour >= win["to"] else due - DAYS(1)
            due = (day + DAYS(1)).replace(hour=win["from"], minute=r.randint(0, 20), second=0, microsecond=0)
        check = "sent"
        if due > A or due > en + HOURS(0):
            check = "held: quiet hours, state ended first"
        elif channel == "human call":
            check = "task"
        elif channel == "whatsapp" and not (p.whatsapp_optin and not p.dnd):
            check = "held: no WhatsApp opt-in" if not p.whatsapp_optin else "held: DND"
        elif channel == "email" and not (p.email_known_at and p.email_known_at <= due):
            check = "held: no email on file"
        elif paid_ref and due >= paid_ref + DAYS(cap["from_days_after_paid"]) and slot not in exempt:
            if last is not None and due < last + DAYS(cap["days"]):
                check = "held: weekly cap"
            else:
                last = due
        row = {"slot": slot, "channel": channel, "state_id": s, "due_at": due0, "sent_at": None, "delivered": None,
               "opened": None, "clicked": None, "cap_check": check, "link": link}
        if check == "sent":
            row["sent_at"] = due
            dl = ctx.cfg["nudges"]["delivery"][channel]
            vendor = {"push": "fcm", "whatsapp": "wati", "email": "ses"}[channel]
            out = p.integ_call(ctx, due, vendor, "send", None)
            row["delivered"] = out == "ok" and r.random() < dl["delivered"]
            row["opened"] = bool(row["delivered"]) and r.random() < dl["opened"]
            row["clicked"] = bool(row["opened"]) and r.random() < max(dl["clicked"], 0.5 if channel == "push" else dl["clicked"])
            p.ev(due, "nudge_sent", ctx.B.lands(s) if s in ctx.B.states else None, slot=slot, channel=channel,
                 state=s, cap_check=check)
            if row["opened"]:
                ot = due + MINS(r.uniform(2, 600))
                if ot < A:
                    p.ev(ot, "nudge_opened", None, slot=slot, channel=channel)
                    if link and link not in ("G03",) and link in ctx.B.live and state_at(p, ot) == s:
                        p.view(ctx, ot + SECS(5), link, via="nudge")
        p.nudges.append(row)


def tasks(p, ctx, episodes):
    """CRM tasks (states.json crm_task): S2b after a day unsigned; S19 at the stall and S20 on the second
    no-show for DIWM (brief V2); S24 and S25 on the request. A call-centre task still open after 7 days is
    worked (called, the person still in the state); a task whose state has ended is done."""
    tc = ctx.cfg["tasks"]
    r, A = p.r, ctx.A
    rows = []
    for s, st, en in episodes:
        if s == "S2b" and st + DAYS(1) < en:
            rows.append(("S2b", st + DAYS(1), en, "owner"))
        if s == "S19" and p.tier == "diwm":
            rows.append(("S19", st, en, "owner"))
    sn = getattr(p, "second_no_show_at", None)
    if sn and p.tier == "diwm" and sn <= A:
        rebooked = [c["booked_at"] for c in p.calls if c["booked_at"] > sn]
        rows.append(("S20", sn, min(rebooked) if rebooked else A, "owner"))
    if p.tl.get("refund"):
        rows.append(("S24", p.tl["refund"], A, "ops01"))
    if p.tl.get("deletion"):
        rows.append(("S25", p.tl["deletion"], A, "ops01"))
    for s, created, until, who in rows:
        assignee = p.owner if who == "owner" else who
        fields = {"state_id": s, "tier": p.tier}
        if s == "S2b":
            fields["days_unsigned"] = int(days_between(p.tl["checkout"], min(until, A)))
        if s == "S19":
            fields["missing_fields"] = missing_fields(p, ctx, created)
            fields["last_screen"] = last_screen_at(p, created)
            fields["minutes_left"] = "about N minutes"
        if s == "S20":
            fields["call_topic"] = p.calls[-1]["topic"] if p.calls else None
            fields["no_show_count"] = sum(1 for c in p.calls if c["outcome"] == "no_show" and c["slot"] <= created)
        if s == "S24":
            fields["payment_reference"] = "(the deal's first payment id)"
            fields["cancel_reason"] = p.subs[0]["cancel_reason"] if p.subs else None
            fields["period_unexpired"] = True
        if s == "S25":
            fields["records_retained"] = tc["records_retained"]
            fields["requested_at"] = p.tl.get("deletion")
        status, closed, outcome = "open", None, None
        if s in ("S2b", "S19", "S20"):
            if until < A:
                status, closed, outcome = "done", until, "the state ended"
            elif days_between(created, A) > 7:
                closed = created + DAYS(r.uniform(0.5, 3.0))
                status, outcome = "done", "called; still %s" % s
        p.tasks.append({"state_id": s, "created_at": created, "due": business_days(created, tc["due_business_days"]),
                        "assignee": assignee, "status": status, "closed_at": closed, "outcome": outcome,
                        "fields": fields, "subject": "%s: %s" % (s, ctx.B.states[s]["primary_action"])})
        p.ev(created + SECS(2), "crm_task_created", ctx.B.lands(s), state=s)


def missing_fields(p, ctx, t):
    """The gate fields not yet a value, a band or explicit none at time t."""
    out = []
    for f in sorted(ctx.gate):
        k = kind_at(p, f, t)
        if k is None or k == "not_sure":
            out.append(f)
    return out


def kind_at(p, f, t):
    d = p.dec.get(f)
    if not d:
        return None
    steps = sorted(d["history"] + [{"kind": d["kind"], "at": d["at"]}], key=lambda h: h["at"])
    k = None
    for h in steps:
        if h["at"] <= t:
            k = h["kind"]
    return k


def last_screen_at(p, t):
    last = None
    for e in sorted(p.events, key=lambda e: (e[0], e[1])):
        if e[0] > t:
            break
        if e[2].endswith("_view") and e[3] and e[3][0] in "DAO":
            last = e[3]
    return last


def app_opens(p, ctx, episodes):
    """Organic opens after the plan (or for DIFM, after the claim): the landing screen of the state then."""
    r, A = p.r, ctx.A
    rates = ctx.cfg["journey_rates"]["app_opens_per_week_after_plan"]
    start = p.tl.get("built") or (p.tl.get("otp") if p.tier == "difm" else None)
    if not start:
        return
    for s, st, en in episodes:
        a = max(st, start)
        if a >= en:
            continue
        rate = rates.get(s, rates["other"])
        weeks = days_between(a, en) / 7.0
        n = int(weeks * rate + r.random())
        for _ in range(n):
            t = a + (en - a) * r.random()
            t = t.replace(hour=ctx.hour(r), minute=r.randint(0, 59), second=r.randint(0, 59), microsecond=0)
            if not (a <= t < en and t < A):
                continue
            land = STATE_H01.get(s) or ctx.B.lands(s)
            if land == "G03":
                continue
            p.ev(t, "open_organic", None)
            p.view(ctx, t + SECS(2), land)
            if s in ("S9", "S10") and r.random() < 0.3:
                p.view(ctx, t + SECS(40), "H02")
            if s in ("S8", "S9") and r.random() < 0.3:
                p.view(ctx, t + SECS(60), "H04")


# ---------------------------------------------------------------- tables

def person_row(p, ctx):
    A = ctx.A
    tl = p.tl
    lead = p.layer == "lead"
    calls_done = [c for c in p.calls if c["outcome"] == "completed" and c["ended_at"] and c["ended_at"] <= A]
    last_call = max((c["ended_at"] for c in calls_done), default=None)
    last_adv = [c["adviser_id"] for c in sorted(calls_done, key=lambda c: c["slot"])][-1:] or [None]
    sub = p.subs[-1] if p.subs else None
    renewal_due = None
    if sub and sub["status"] in ("active",):
        P = ctx.cfg["period_mix"]["days"][sub["period"]]
        k = 1
        while sub["start"] + DAYS(P * k) <= A:
            k += 1
        renewal_due = sub["start"] + DAYS(P * k)
    next_review = None
    if p.tier == "difm":
        nxt = [d for d in p.difm_reviews if d > A]
        next_review = nxt[0] if nxt else None
    elif tl.get("built"):
        k = 1
        while tl["built"] + DAYS(90 * k) <= A:
            k += 1
        next_review = tl["built"] + DAYS(90 * k)
    last_act = max((e[0] for e in p.events), default=None)
    manual = [d["at"] for d in p.dec.values() if d["source"] == "manual"]
    acts_done = sum(1 for a in p.actions if a["done_at"])
    fp = "not_started"
    if tl.get("first_d"):
        fp = "in_progress"
    if tl.get("built"):
        fp = "built"
    if tl.get("read"):
        fp = "read"
    if p.tier == "difm":
        fp = "not applicable (adviser relationship)"
    ip = None
    if p.tier in ("diy", "diwm"):
        ip = "not_started"
        if tl.get("built"):
            ip = "ready"
        if tl.get("first_action"):
            ip = "executing"
        if tl.get("all_done"):
            ip = "done"
    row = {
        "person_id": p.pid, "kind": "lead" if lead else "user", "first_name": p.first, "last_name": p.last,
        "phone": p.phone, "email": p.email, "city": p.city, "city_tier": p.city_tier,
        "age": None if (lead and p.source != "web_reveal") else p.age,
        "age_band": p.age_band if (not lead or p.source == "web_reveal") else None,
        "source": p.source, "whatsapp_optin": p.whatsapp_optin, "dnd": p.dnd,
        "created_at": iso(p.created_at), "otp_verified_at": iso(tl.get("otp")) if not lead else None,
        "lead_stage": "lead" if lead else "verified_lead", "archetype": p.arche, "is_topup": p.is_topup,
        "tier": p.tier, "sku": p.tier if p.tier in ("diy", "diwm") else None,
        "period": p.period if p.tier in ("diy", "diwm") else None,
        "subscription_status": (sub["status"] if sub else ("adviser relationship" if p.tier == "difm" else None)),
        "adviser_id": p.owner, "state_id": p.state_id, "state_entered_at": iso(p.state_entered_at),
        "progress_pct": p.progress, "profile_fulfilment_pct": p.fulfilment,
        "aa_status": getattr(p, "aa_status", None) if not lead else None,
        "consent_valid_till": ymd(p.consents[-1]["expires_at"]) if p.consents and p.consents[-1]["expires_at"] else None,
        "source_completeness": ("yes" if tl.get("gate") else "no") if p.layer == "paid" and p.tier != "difm" else None,
        "sharpen_count": getattr(p, "sharpen_count", 0) if p.layer == "paid" else None,
        "last_manual_update": iso(max(manual)) if manual else None,
        "difm_prospect_flag": p.prospect, "adviser_continuity": "off" if not lead else None,
        "last_adviser": last_adv[0],
        "key_dates": {"signed_up": ymd(tl.get("otp")) if not lead else None,
                      "reveal_seen": ymd(tl.get("reveal")) if getattr(p, "reveal_upto", 0) == 7 else None,
                      "paid": ymd(tl.get("paid")), "data_complete": ymd(tl.get("d10")), "plan_built": ymd(tl.get("built")),
                      "plan_read": ymd(tl.get("read")), "last_call": ymd(last_call), "next_review": ymd(next_review),
                      "renewal_due": ymd(renewal_due), "last_activity": ymd(last_act)},
        "mirrors": {"onboarding_pct": p.progress, "kyc_status": getattr(p, "kyc_status", "not_started") if not lead else None,
                    "aa_status": getattr(p, "aa_status", None) if not lead else None, "fp_status": fp if not lead else None,
                    "ip_status": ip, "actions_done": acts_done if p.actions else None,
                    "actions_total": len(p.actions) if p.actions else None},
        "s16_flag": bool(getattr(p, "s16", False)), "source_path": p.path if p.layer == "paid" else None,
        "journey_stage": p.state_id,
        "lead_details": {"top_concern": p.top_concern, "keyword": p.keyword, "community_joined": p.community_joined,
                         "resource_sent": p.resource_sent, "landing_at": iso(p.landing)},
        "legal_name": "%s %s" % (p.first, p.last) if p.pan else None, "pan": p.pan, "dob": getattr(p, "dob", None),
        "device": p.device if not lead else None, "plausibility_flag": p.plausibility_flag or None,
        "engine_failure": p.engine_failure or None,
    }
    return row


def fulfilment(p, ctx):
    if p.layer == "lead":
        return None
    have = 2
    total = 2 + 8 + 6
    up = getattr(p, "reveal_upto", 0)
    have += min(up, 7) + (1 if up == 7 else 0)
    if getattr(p, "pan_known", False):
        have += 4
    if p.tl.get("esign"):
        have += 1
    if p.tl.get("paid"):
        have += 1
    spine_fields = [f for f in ctx.fields if f in p.dec or (p.layer == "paid" and truth_value(p, f) is not None)]
    total += len(spine_fields) if p.layer == "paid" else 0
    have += sum(1 for f in p.dec if p.dec[f]["kind"] in ("exact", "band", "none", "default"))
    return int(round(100.0 * have / max(total, have)))


def build_tables(people, ctx):
    A = ctx.A
    T = collections.OrderedDict()
    for name in ("people", "households", "reveal", "financial_records", "loans", "covers", "goals", "rpq", "holdings",
                 "aa_consents", "cas_uploads", "plan_versions", "actions", "subscriptions", "payments", "a_la_carte",
                 "calls", "tickets", "ops_queue", "integration_events", "tasks", "nudges_sent", "state_flags"):
        T[name] = collections.OrderedDict()
    events = []
    counters = collections.Counter()
    for p in people:
        pid = p.pid
        T["people"][pid] = person_row(p, ctx)
        if p.layer == "lead":
            continue
        if getattr(p, "reveal_upto", 0) >= 1:
            T["households"][pid] = {"household_id": "HH-%s" % pid[1:], "household_type": p.household_type if p.reveal_upto >= 2 else None,
                                    "members": [dict(m) for m in p.members] if "members" in p.dec else None,
                                    "has_dependants": p.has_dependants if "members" in p.dec else None,
                                    "partner_earns": p.partner["earns"] if (p.partner and "members" in p.dec) else None,
                                    "pets": p.pets if "pets" in p.dec else None}
        up = getattr(p, "reveal_upto", 0)
        if up >= 1 or p.tier == "difm":
            rb = ctx.cfg["reveal_bands"]
            if p.tier == "difm":
                pass
            else:
                T["reveal"][pid] = {
                    "first_name": p.first if up >= 0 else None, "age": p.age,
                    "household_type": p.household_type if up >= 2 else None,
                    "income_band": rb["income"]["labels"][p.income_band] if up >= 3 else None,
                    "income_exact": p.income_exact if up >= 3 else None,
                    "corpus_band": rb["corpus"]["labels"][p.corpus_band] if up >= 4 else None,
                    "corpus_exact": p.corpus_exact if up >= 4 else None,
                    "savings_rate_band": rb["savings"]["labels"][p.savings_band] if up >= 5 else None,
                    "savings_rate_exact": p.savings_exact if up >= 5 else None,
                    "journey_feel": p.journey_feel if up >= 6 else None,
                    "aspiration": p.aspiration if up >= 7 else None,
                    "path_now_band": p.path_now_band if up == 7 else None,
                    "path_yes_band": p.path_yes_band if up == 7 else None,
                    "path_band_note": "stub; the engine (I04) owns the reveal maths" if up == 7 else None,
                    "reveal_seen_at": iso(p.tl.get("reveal")) if up == 7 else None}
        if p.dec:
            recs = []
            for f in ctx.fields:
                d = p.dec.get(f)
                if not d:
                    continue
                v, vk, bid, prec = stored(ctx, p, f, d)
                recs.append({"field": f, "value": v, "value_kind": vk, "band_id": bid,
                             "source": d["source"] if d["kind"] != "default" else "default_accepted",
                             "precision": prec, "locked": d.get("locked", False), "captured_at": iso(d["at"]),
                             "screen_id": d["screen"],
                             "history": [{"value_kind": {"exact": "exact", "band": "band", "none": "none", "not_sure": "not_sure", "default": "exact"}[h["kind"]],
                                          "precision": PRECISION_OF_KIND[h["kind"]], "source": h["source"],
                                          "screen_id": h["screen"], "captured_at": iso(h["at"])} for h in d["history"]]})
            T["financial_records"][pid] = recs
        if p.loan_recs if hasattr(p, "loan_recs") else False:
            rows = []
            for i, rec in enumerate(p.loan_recs):
                loan = p.T["loans"][i]
                row = {"loan_id": "%s-L%d" % (pid, i + 1), "type": loan["type"], "emi": loan["emi"],
                       "emi_kind": "exact", "lender": rec["lender"], "tax_deductible": rec["tax_deductible"],
                       "prepayment_allowed": rec["prepayment_allowed"], "captured_at": iso(rec["captured_at"]),
                       "screen_id": "D03a", "d13_at": iso(rec["d13_at"])}
                for sub, lad in (("outstanding", "loan_outstanding"), ("years_left", None)):
                    k = rec[sub + "_kind"]
                    if k == "exact":
                        row[sub] = loan[sub]
                        row[sub + "_band"] = None
                    elif k == "band":
                        if lad:
                            i2 = band_index(loan[sub], ctx.bands[lad])
                            row[sub] = rnd(band_mid(ctx.bands[lad], i2), 1000)
                            row[sub + "_band"] = "%s.%d" % (lad, i2)
                        else:
                            ch = ctx.cfg["bands"]["loan_years_chips"]
                            i2 = band_index(loan[sub], ch["bounds"])
                            row[sub] = ch["mid"][i2]
                            row[sub + "_band"] = ch["labels"][i2]
                    else:
                        row[sub] = None
                        row[sub + "_band"] = None
                    row[sub + "_kind"] = k
                row["rate"] = loan["rate"] if row["outstanding_kind"] != "not_sure" and row["years_left_kind"] != "not_sure" else None
                row["rate_kind"] = "derived" if row["rate"] is not None else "not_sure"
                rows.append(row)
            T["loans"][pid] = rows
        if "term_status" in p.dec:
            Tm, Hm = p.T["term"], p.T["health"]
            T["covers"][pid] = {
                "term_status": "have" if Tm else "none",
                "term_sum_assured": stored(ctx, p, "term_sum_assured", p.dec["term_sum_assured"])[0] if "term_sum_assured" in p.dec else None,
                "term_premium": stored(ctx, p, "term_premium", p.dec["term_premium"])[0] if "term_premium" in p.dec else None,
                "term_cover_until_age": stored(ctx, p, "term_cover_until_age", p.dec["term_cover_until_age"])[0] if "term_cover_until_age" in p.dec else None,
                "health_type": Hm["type"] if Hm else "none",
                "health_sum_insured": stored(ctx, p, "health_sum_insured", p.dec["health_sum_insured"])[0] if "health_sum_insured" in p.dec else None,
                "health_floater": stored(ctx, p, "health_floater", p.dec["health_floater"])[0] if "health_floater" in p.dec else None,
                "health_premium": stored(ctx, p, "health_premium", p.dec["health_premium"])[0] if "health_premium" in p.dec else None,
                "other_policies": stored(ctx, p, "other_policies", p.dec["other_policies"])[0] if "other_policies" in p.dec else None}
        if "goals" in p.dec:
            rows = []
            gm = ctx.cfg["bands"]["goal_horizon_chips"]
            for i, g in enumerate(p.T["goals"]):
                if "captured_at" not in g:
                    continue
                if g["cost_kind"] == "exact":
                    cost, ck, bid = g["cost"], "exact", None
                elif g["cost_kind"] == "band":
                    i2 = band_index(g["cost"], ctx.bands["goal_cost"])
                    cost, ck, bid = rnd(band_mid(ctx.bands["goal_cost"], i2), 1000), "band", "goal_cost.%d" % i2
                else:
                    cost, ck, bid = None, "not_sure", None
                yrs = g["year"] - A.year
                if g["timeline"] == "chips":
                    j = min(range(len(gm["years"])), key=lambda k: abs(gm["years"][k] - yrs))
                    year, tk = A.year + gm["years"][j], gm["labels"][j]
                else:
                    year, tk = g["year"], "exact year"
                rows.append({"goal_id": "%s-G%d" % (pid, i + 1), "name": g["name"], "type": g["type"], "year": year,
                             "timeline": tk, "cost_today": cost, "cost_kind": ck, "band_id": bid,
                             "priority": g["priority"], "yes_list": ck == "not_sure",
                             "captured_at": iso(g["captured_at"])})
            if rows:
                T["goals"][pid] = rows
        if "rpq_answers" in p.dec:
            T["rpq"][pid] = {"answers": p.T["rpq"]["answers"], "score": p.T["rpq"]["score"],
                             "risk_band": p.T["rpq"]["risk_band"], "taken_at": iso(p.rpq_at),
                             "questionnaire_version": ctx.cfg["rpq"]["questionnaire_version"]}
        if p.holdings:
            T["holdings"][pid] = [{"isin": h["isin"], "name": h["name"], "kind": h["kind"], "units": h["units"],
                                   "value": h["value"], "source": h["source"], "unknown_isin": h["unknown_isin"],
                                   "as_of": iso(h["at"])} for h in p.holdings]
        if p.consents:
            T["aa_consents"][pid] = [{"consent_handle": c["handle"], "status": "expired" if c["status"] == "renewed" else c["status"],
                                      "institutions_ok": c["institutions_ok"], "institutions_failed": c["institutions_failed"],
                                      "connected_at": iso(c["connected_at"]), "consent_expiry": iso(c["expires_at"]),
                                      "renewed_at": iso(c["renewed_at"]), "fetched_at": iso(c["fetched_at"])} for c in p.consents]
        if p.cas:
            T["cas_uploads"][pid] = [{"requested_at": iso(c["requested_at"]), "cas_source": c["cas_source"],
                                      "reminder_count": c["reminder_count"], "uploaded_at": iso(c["uploaded_at"]),
                                      "parsed_at": iso(c["parsed_at"]), "abandoned_at": iso(c["abandoned_at"])} for c in p.cas]
        if p.plans:
            rows = []
            for pv in p.plans:
                rows.append({"plan_version": pv["plan_version"], "assumptions_version": pv["assumptions_version"],
                             "instrument_set_version": pv["instrument_set_version"], "built_at": iso(pv["built_at"]),
                             "built_on": pv["built_on"], "band_count": pv["band_count"], "read_at": iso(pv["read_at"]),
                             "pdf_downloaded_at": iso(pv["pdf_downloaded_at"]), "reason": pv["reason"],
                             "accepted_at": iso(pv["accepted_at"]) if pv["accepted_at"] and pv["accepted_at"] <= A else None,
                             "summary_stub": plan_stub(p), "summary_label": ctx.cfg["plan_stub"]["label"]})
            T["plan_versions"][pid] = rows
        if p.actions:
            T["actions"][pid] = [{"action_id": "%s-X%d" % (pid, i + 1), "type": a["type"], "amount": a["amount"],
                                  "due": ymd(a["due"]), "channel": a["channel"], "status": a["status"],
                                  "started_at": iso(a["started_at"]), "done_at": iso(a["done_at"]),
                                  "verification": a["verification"], "verified_at": iso(a["verified_at"]),
                                  "missed_sip_at": iso(a.get("missed_sip_at"))} for i, a in enumerate(p.actions)]
        if p.subs:
            rows = []
            for s in p.subs:
                deal = "DL-%s-%d" % (pid[1:], s["n"])
                P = ctx.cfg["period_mix"]["days"][s["period"]]
                nb = None
                if s["status"] in ("active", "failed"):
                    k = 1
                    while s["start"] + DAYS(P * k) <= A:
                        k += 1
                    nb = ymd(s["start"] + DAYS(P * k))
                used = sum(1 for c in p.calls if c["outcome"] == "completed" and c["slot"] >= s["start"] and c["slot"] <= A
                           and (c["slot"] >= A - DAYS(P)))
                rows.append({"deal_id": deal, "sku": s["sku"], "period": s["period"], "price_key": s["price_key"],
                             "amount": s["amount"], "gst_type": s["gst_type"], "payment_method": s["payment_method"],
                             "coupon": s["coupon"], "razorpay_customer_id": "cust_SEED%s" % pid[1:],
                             "razorpay_subscription_or_txn_id": ("sub_SEED%s%d" % (pid[1:], s["n"])) if s["payment_method"] == "upi" else ("pay_SEED%s%d" % (pid[1:], s["n"])),
                             "mandate_status": s["mandate_status"], "start": ymd(s["start"]), "next_billing": nb,
                             "status": s["status"], "grace_until": ymd(s["grace_until"]), "retry_count": s["retry_count"],
                             "calls_included_per_period": ctx.cfg["app_config"]["calls_included"][s["sku"]][s["period"]],
                             "calls_used": used, "cancel_reason": s["cancel_reason"],
                             "refund_requested": s["refund_requested"], "refund_status": s["refund_status"],
                             "lapsed_at": iso(s["lapsed_at"]), "resubscribed": s["resubscribed"]})
            T["subscriptions"][pid] = rows
            prow = []
            for k, pay_ in enumerate(p.payments):
                deal = "DL-%s-%d" % (pid[1:], pay_["sub_n"])
                counters["invoice"] += 1 if pay_["status"] == "captured" else 0
                split = {"cgst_sgst": {"cgst": "Rs ___", "sgst": "Rs ___"}, "igst": {"igst": "Rs ___"}, "none": {}}[pay_["gst_type"]]
                prow.append({"payment_id": "PAY-%s-%d" % (pid[1:], k + 1), "deal_id": deal, "amount": pay_["amount"],
                             "gst_type": pay_["gst_type"], "gst_breakup": split, "status": pay_["status"],
                             "paid_at": iso(pay_["at"]), "method": pay_["method"],
                             "invoice_no": ("INV-SEED-%06d" % counters["invoice"]) if pay_["status"] == "captured" else None,
                             "detail": pay_["detail"]})
            T["payments"][pid] = prow
        if p.alc:
            rows = []
            for k, a in enumerate(p.alc):
                call_id = None
                for j, c in enumerate(p.calls):
                    if c["purchase"] is a:
                        call_id = "%s-C%d" % (pid, j + 1)
                rows.append({"purchase_id": "%s-A%d" % (pid, k + 1), "date": iso(a["at"]), "amount": a["amount"],
                             "receipt": a["receipt"], "call_id": call_id})
            T["a_la_carte"][pid] = rows
        if p.calls:
            rows = []
            for j, c in enumerate(p.calls):
                status = c["outcome"]
                if status in ("completed", "no_show") and c["slot"] + MINS(20) > A:
                    status = "booked"
                rows.append({"call_id": "%s-C%d" % (pid, j + 1), "adviser_id": c["adviser_id"], "booked_at": iso(c["booked_at"]),
                             "slot": iso(c["slot"]), "topic": c["topic"], "note": c["note"], "status": status,
                             "notes": c["notes"] if status == "completed" else None,
                             "input_changes": c["input_changes"] if status == "completed" else [],
                             "recording_ref": None, "recording_note": "to be verified: recording consent and retention",
                             "same_adviser_requested": c["same_adviser_requested"],
                             "rebook_of": ("%s-C%d" % (pid, c["rebook_of"] + 1)) if c["rebook_of"] is not None else None})
            T["calls"][pid] = rows
        if p.tickets:
            rows = []
            for j, tk in enumerate(p.tickets):
                counters["ticket"] += 1
                tk["ticket_id"] = "TK-%06d" % (p.idx * 10 + j + 1)
                rows.append({"ticket_id": tk["ticket_id"], "category": tk["category"], "subject": tk["subject"],
                             "description": tk["description"], "created_at": iso(tk["created_at"]),
                             "sla_due": iso(tk["sla_due"]), "status": tk["status"], "resolved_at": iso(tk["resolved_at"]),
                             "scores_ref": tk["scores_ref"]})
            T["tickets"][pid] = rows
        if p.ops:
            rows = []
            for j, o in enumerate(sorted(p.ops, key=lambda o: o["created_at"])):
                res = o.get("resolved_at")
                if res is None and o["type"] not in ("refund_request", "deletion_request", "engine_failure") and p.r.random() < ctx.cfg["ops_queue"]["resolved_share"]:
                    rt = o["created_at"] + DAYS(p.r.uniform(0.2, 6))
                    res = rt if rt <= A else None
                rows.append({"item_id": "%s-Q%d" % (pid, j + 1), "type": o["type"], "created_at": iso(o["created_at"]),
                             "owner": ctx.cfg["ops_queue"]["owner"], "status": "resolved" if res else "open",
                             "resolved_at": iso(res), "detail": o["detail"]})
            T["ops_queue"][pid] = rows
        if p.integ:
            T["integration_events"][pid] = [{"vendor": e["vendor"], "integration": e["integration"], "call": e["call"],
                                             "outcome": e["outcome"], "latency_ms": e["latency_ms"], "at": iso(e["at"]),
                                             "detail": e["detail"]} for e in sorted(p.integ, key=lambda e: e["at"]) if e["at"] <= A]
        if p.tasks:
            T["tasks"][pid] = [{"task_id": "%s-T%d" % (pid, j + 1), "state_id": t["state_id"], "subject": t["subject"],
                                "fields": dict((k, (iso(v) if isinstance(v, dt.datetime) else v)) for k, v in t["fields"].items()),
                                "assignee": t["assignee"], "created_at": iso(t["created_at"]), "due": iso(t["due"]),
                                "status": t["status"], "closed_at": iso(t["closed_at"]), "outcome": t["outcome"]}
                               for j, t in enumerate(p.tasks)]
        if p.nudges:
            T["nudges_sent"][pid] = [{"slot": n["slot"], "channel": n["channel"], "state_id": n["state_id"],
                                      "due_at": iso(n["due_at"]), "sent_at": iso(n["sent_at"]), "delivered": n["delivered"],
                                      "opened": n["opened"], "clicked": n["clicked"], "cap_check": n["cap_check"],
                                      "link": n["link"]} for n in p.nudges]
        T["state_flags"][pid] = flags_json(p.F)
    # events
    n = 0
    for p in people:
        tickets = iter([t["ticket_id"] for t in p.tickets])
        for e in sorted(p.events, key=lambda e: (e[0], e[1])):
            if e[0] > A:
                continue
            props = dict(e[4])
            if e[2] == "ticket_created":
                props["ticket_id"] = next(tickets, None)
            if e[2] == "signed_up":
                props["phone"] = p.phone
            n += 1
            events.append({"event_id": "EV%07d" % n, "person_id": p.pid, "event": e[2], "screen_id": e[3],
                           "at": iso(e[0]), "props": props})
    return T, events


def plan_stub(p):
    T = p.T
    emerg = round((T["assets"]["bank_and_deposits"] or 0) / float(max(1, T["total_outgoings"])), 1)
    sip = sum(a["amount"] or 0 for a in p.actions if a["type"] == "sip_start")
    gap = max(0, T["take_home"] * 12 * 10 - (T["term"]["sum_assured"] if T["term"] else 0))
    return {"emergency_months": emerg, "monthly_surplus": T["surplus"], "sip_total": sip, "cover_gap": gap}


def flags_json(F):
    def conv(v):
        if isinstance(v, dt.datetime):
            return iso(v)
        if isinstance(v, list):
            return [conv(x) for x in v]
        return v
    return dict((k, conv(v)) for k, v in F.items())


def config_table(ctx):
    cfg, B = ctx.cfg, ctx.B
    slots = []
    for slot, t in sorted(B.templates.items()):
        slots.append({"slot": slot, "channel": t["channel"], "state": t["state"], "deep_link": t["link"],
                      "text": t["text"], "label": "placeholder copy (gap G08)"})
    for sid in sorted(i for i in B.live if B.S[i]["template"] in ("T-num", "T-detail")):
        slots.append({"slot": "W-%s" % sid, "channel": "in-app", "state": None, "deep_link": sid,
                      "text": "Why this one matters on %s: placeholder copy" % B.S[sid]["title"],
                      "label": "placeholder copy (gap G08)"})
    ac = cfg["app_config"]
    return {"sku_cards": ac["sku_cards"], "copy_slots": slots, "feature_flags": ac["feature_flags"],
            "calls_included": ac["calls_included"], "a_la_carte_price": ac["a_la_carte_price"],
            "bands": {"placeholder": True, "note": cfg["bands"]["ref"], "ladders_rs": cfg["bands"]["ladders_rs"],
                      "reveal": dict((k, cfg["reveal_bands"][k]) for k in ("income", "corpus", "savings"))},
            "difm_threshold": {"value_rs": cfg["difm_threshold"]["value_rs"], "board_reads": cfg["difm_threshold"]["board_reads"],
                               "label": "placeholder (assumption)"},
            "agreement_version": ac["agreement_version"], "price_note": ac["price_note"],
            "assumptions_versions": [{"assumptions_version": p["assumptions_version"],
                                      "instrument_set_version": p["instrument_set_version"],
                                      "published_at": iso(p["at"])} for p in ctx.publishes]}


# ---------------------------------------------------------------- validation and the report

def validate(people, events, ctx):
    A = ctx.A
    res = collections.OrderedDict()
    co = ctx.cfg["coherence"]
    # coherence rules on the synthetic truth
    viol = collections.Counter()
    for p in people:
        if not p.T or p.layer == "lead":
            continue
        t = p.T
        m = t["corpus"] / float(t["gross"])
        if not (co["corpus_multiple"]["min"] - 1e-9 <= m <= co["corpus_multiple"]["max"] + 1e-9):
            viol["corpus between 0.3x and 3x income"] += 1
        if t["total_emi"] > co["emi_max_share_of_take_home"] * t["take_home"] + 1:
            viol["EMI at most 45 percent of take-home"] += 1
        lo, hi = co["outgoings_share_of_take_home"]
        if not (lo * t["take_home"] - 1 <= t["total_outgoings"] <= hi * t["take_home"] + 1):
            viol["outgoings 40 to 85 percent of take-home"] += 1
        if t["current_sip"] and t["current_sip"] > t["surplus"]:
            viol["SIP at most the surplus"] += 1
        if "goals" in p.dec and not (t["goals"] or p.dec["goals"]["kind"] == "none"):
            viol["goals: one or explicit none"] += 1
        rq = t["rpq"]
        if len(rq["answers"]) != 8 or rq["score"] != sum(ctx.cfg["rpq"]["points_by_option"][x] for x in rq["answers"]):
            viol["RPQ eight answers and score"] += 1
        if not [b for b in ctx.cfg["rpq"]["bands"] if b[0] <= rq["score"] <= b[1] and b[2] == rq["risk_band"]]:
            viol["risk band from the score"] += 1
    res["coherence"] = viol
    # stored values agree with the truth
    bad = 0
    for p in people:
        for f, d in p.dec.items():
            if d["kind"] == "band":
                v = truth_value(p, f)
                lad = ctx.bands[ctx.fields[f]["ladder"]]
                i = band_index(v, lad)
                if not (lad[i] <= v and (i + 1 == len(lad) or v < lad[i + 1])):
                    bad += 1
    res["stored_consistency"] = bad
    # ratio rules (reported, not violations)
    ratios = collections.OrderedDict()
    dep = [p for p in people if p.T and p.layer == "paid" and p.has_dependants]
    ratios["term cover missing among people with dependants"] = (sum(1 for p in dep if not p.T["term"]), len(dep), co["term_missing_with_dependants"])
    allp = [p for p in people if p.T and p.layer == "paid"]
    ratios["health employer-only"] = (sum(1 for p in allp if p.T["health"] and p.T["health"]["type"] == "Employer only"), len(allp), co["health_employer_only"])
    cps = [p for p in allp if p.partner]
    ratios["home loan among couples"] = (sum(1 for p in cps if any(l["type"] == "home" for l in p.T["loans"])), len(cps), co["home_loan_couples"])
    ratios["ULIP held"] = (sum(1 for p in allp if p.T["assets"]["ulip_surrender_value"]), len(allp), co["ulip_share"])
    res["ratios"] = ratios
    # gate: every built person has no unknown gate or React field; D13 rows where a range was taken
    gate_bad, react_bad, d13_rows, d13_bad = 0, 0, 0, 0
    for p in people:
        if not p.tl.get("built"):
            continue
        for f in ctx.gate:
            d = p.dec.get(f)
            if d is None or d["kind"] == "not_sure":
                gate_bad += 1
        for f in ctx.react:
            d = p.dec.get(f)
            fc = ctx.fields[f]
            if d is not None and d["kind"] == "not_sure" and not fc.get("no_band"):
                react_bad += 1
        for rec in p.loan_recs:
            for sub in ("outstanding", "years_left"):
                if rec[sub + "_kind"] == "not_sure":
                    react_bad += 1
        for f, d in p.dec.items():
            hist = [h for h in d["history"]] + [d]
            if any(h["screen"] == "D13" for h in hist):
                d13_rows += 1
                skipped = [h for h in d["history"] if h["kind"] == "not_sure"]
                if not skipped:
                    d13_bad += 1
    res["gate"] = {"built": sum(1 for p in people if p.tl.get("built")), "unknown_gate_fields": gate_bad,
                   "unknown_react_fields": react_bad, "d13_rows": d13_rows, "d13_without_prior_skip": d13_bad}
    # one state per person; target vs resolved; multi-predicate list; no-predicate list
    pairs = collections.Counter()
    multi = 0
    mism = collections.Counter()
    nopred = collections.Counter()
    for p in people:
        if p.layer == "lead":
            continue
        H = holds(p.F, A, ctx)
        if len(H) > 1:
            multi += 1
            for o in sorted(H - {p.state_id}, key=lambda s: ctx.prec_order.index(s) if s in ctx.prec_order else 99):
                pairs[(p.state_id, o)] += 1
        if not H:
            nopred[(p.state_id, "engine failure" if p.engine_failure else "other")] += 1
        if p.target and p.state_id != p.target:
            mism[(p.target, p.state_id)] += 1
    res["multi"] = {"people": multi, "pairs": pairs}
    res["nopred"] = nopred
    res["mismatch"] = mism
    # transitions against the exits
    trans_bad = collections.Counter()
    trans_all = 0
    for p in people:
        seq = [s for t, s in p.hist]
        for i in range(1, len(seq)):
            a, b = seq[i - 1], seq[i]
            trans_all += 1
            prev = seq[i - 2] if i >= 2 else None
            ok = b in EXITS.get(a, set()) or ("PREV" in EXITS.get(a, set()) and b == prev) or b in OVERLAY_ENTRY or (
                a in OVERLAY_ENTRY and (b == prev or b in EXITS.get(prev, set()) or prev is None))
            if not ok:
                trans_bad[(a, b)] += 1
    res["transitions"] = {"total": trans_all, "outside_exits": trans_bad}
    # event order
    first_seen = {}
    before_signup, read_before_built, unknown, after_anchor = 0, 0, collections.Counter(), 0
    per = collections.defaultdict(list)
    for e in events:
        per[e["person_id"]].append(e)
    byid = dict((p.pid, p) for p in people)
    for pid, evs in per.items():
        p = byid[pid]
        su = [e["at"] for e in evs if e["event"] == "signed_up"]
        if su:
            before_signup += sum(1 for e in evs if e["at"] < su[0] and e["event"] not in ("A01_view", "A02_view"))
        built = [e["at"] for e in evs if e["event"] == "plan_built"]
        read = [e["at"] for e in evs if e["event"] == "plan_read"]
        if read and (not built or read[0] < built[0]):
            read_before_built += 1
        for e in evs:
            if e["event"] not in ctx.B.known_events and not e["event"].startswith("state_enter_"):
                unknown[e["event"]] += 1
            if e["at"] > iso(A):
                after_anchor += 1
    res["events"] = {"rows": len(events), "before_signed_up": before_signup, "plan_read_before_built": read_before_built,
                     "unknown_names": unknown, "after_anchor": after_anchor}
    return res


def md_table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for r in rows:
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(out)


def report(people, T, events, ctx, info, res, moved):
    cfg, A = ctx.cfg, ctx.A
    L = info["layers"]
    run = ctx.run
    lines = ["# Seed report: %s" % run, "",
             "Anchor %s (every date is relative to it); seed %s; generated by scripts/seed_gen.py from seed/config.json. "
             "Synthetic people only; every number below comes from the config (causes there) and the checks in the "
             "generator." % (iso(A), ctx.seed), ""]
    # layers
    by_layer = collections.Counter(p.layer for p in people)
    top = collections.Counter(p.layer for p in people if p.is_topup)
    rows = []
    for k, label in (("lead", "Leads never OTP'd"), ("S1", "S1 signed up, no reveal"), ("S2", "S2 reveal seen, not paid"),
                     ("S2b", "S2b checkout started, eSign incomplete"), ("S2c", "S2c eSign done, not paid"), ("paid", "Paid, all post-paid states")):
        rows.append([label, L[k], by_layer[k], top[k]])
    rows.append(["total", sum(L.values()), len(people), sum(top.values())])
    lines += ["## 1. Layers", "", md_table(["layer", "config", "realised", "of which topup"], rows), ""]
    # state x tier grid
    order = ["S0", "S0w", "S1", "S2", "S2b", "S2c"] + [s for s in cfg["paid_state_weights"]["weights"]]
    grid = collections.defaultdict(collections.Counter)
    for p in people:
        s = p.state_id
        grid[s][p.tier or "lead"] += 1
    rows = []
    for s in order + sorted(set(grid) - set(order)):
        g = grid[s]
        nat = info["natural"].get(s, "")
        fl = info["floor"] if s in cfg["paid_state_weights"]["weights"] else ""
        tu = info["topup"].get(s, "")
        s16 = sum(1 for p in people if p.state_id == s and getattr(p, "s16", False))
        tot = sum(g.values())
        if tot == 0 and s not in cfg["paid_state_weights"]["weights"]:
            continue
        below = "below floor" if (fl != "" and tot < fl) else ""
        rows.append([s, g["lead"], g["free"], g["diy"], g["diwm"], g["difm"], tot, nat, fl, tu, s16, below])
    lines += ["## 2. State by tier against the floors", "",
              "Columns: lead (never OTP'd), free (OTP'd, not paid), DIY, DIWM, DIFM; natural = the dwell-weighted "
              "allocation before floors; S16 = people carrying the S16 flag beside the state.", "",
              md_table(["state", "lead", "free", "DIY", "DIWM", "DIFM", "total", "natural", "floor", "topup", "S16 flag", "check"], rows), ""]
    tt = sum(info["topup"].values())
    lines += ["Topups: %d people (is_topup true), by state: %s." % (
        tt, ", ".join("%s %d" % (s, n) for s, n in info["topup"].items() if n) or "none"), ""]
    # ratios
    paid = [p for p in people if p.layer == "paid"]
    nonlead = [p for p in people if p.layer != "lead"]
    rows = []
    src = collections.Counter(p.source for p in people if p.tier != "difm")
    n = sum(src.values())
    for k, v in cfg["lead_sources"]["shares"].items():
        rows.append(["lead source: %s" % k, "%.0f%%" % (100 * v), "%.1f%% (%d)" % (100.0 * src[k] / n, src[k])])
    tiers = collections.Counter(p.tier for p in paid)
    for k, v in cfg["tier_mix"]["shares"].items():
        rows.append(["paid tier: %s" % k, "%.0f%%" % (100 * v), "%.1f%% (%d)" % (100.0 * tiers[k] / len(paid), tiers[k])])
    paths = collections.Counter(p.path for p in paid)
    for k, v in cfg["source_path_mix"]["shares"].items():
        rows.append(["source path: %s" % k, "%.0f%%" % (100 * v), "%.1f%% (%d)" % (100.0 * paths[k] / len(paid), paths[k])])
    subs = [p for p in paid if p.tier in ("diy", "diwm")]
    per = collections.Counter(p.period for p in subs)
    for k, v in cfg["period_mix"]["shares"].items():
        rows.append(["period: %s" % k, "%.0f%%" % (100 * v), "%.1f%% (%d)" % (100.0 * per[k] / len(subs), per[k])])
    meth = collections.Counter(p.method for p in subs)
    for k, v in cfg["payment_method_mix"]["shares"].items():
        rows.append(["payment method: %s" % k, "%.0f%%" % (100 * v), "%.1f%% (%d)" % (100.0 * meth[k] / len(subs), meth[k])])
    gst = collections.Counter(s["gst_type"] for p in subs for s in p.subs[:1])
    rows.append(["GST type (first deal)", "by state; none on a zeroing coupon (2%)", ", ".join("%s %d" % kv for kv in sorted(gst.items()))])
    fails = sum(len(p.failures) for p in subs)
    ren = sum(len(s["renewals"]) for p in subs for s in p.subs) + fails
    tfail = sum(1 for p in subs if p.target in ("S12", "S13"))
    rows.append(["renewals failing", "5%", "%.1f%% without the S12 and S13 people (%d of %d); %.1f%% with them" % (
        100.0 * (fails - tfail) / max(1, ren - tfail), fails - tfail, ren - tfail, 100.0 * fails / max(1, ren))])
    s16 = sum(1 for p in paid if getattr(p, "s16", False))
    rows.append(["S16 flag among paid", "about 30%", "%.1f%% (%d)" % (100.0 * s16 / len(paid), s16)])
    arch = collections.Counter(p.arche for p in nonlead)
    rows.append(["archetypes (OTP'd people)", "seed plan weights", ", ".join("%s %d" % (k, arch[k]) for k in cfg["archetype_weights"]["weights"])])
    for k, (a, b, c) in res["ratios"].items():
        rows.append([k, "%.0f%%" % (100 * c), "%.1f%% (%d of %d)" % (100.0 * a / max(1, b), a, b)])
    bk = ctx.tx["s2_ladder_buckets"]
    s2 = [p for p in people if p.state_id == "S2"]
    hist = collections.Counter(band_index(days_between(p.tl["reveal"], ctx.A), bk) for p in s2)
    labels = ["%s to %s days" % (bk[i], bk[i + 1]) if i + 1 < len(bk) else "%s days and beyond" % bk[i] for i in range(len(bk))]
    lines += ["S2 people by days since the reveal (the ladder days 1, 3, 7, 21, 82): " +
              ", ".join("%s %d" % (labels[i], hist[i]) for i in range(len(bk))) + ".", ""]
    lines += ["## 3. Ratios: config against realised", "",
              "Paid-state allocation and topups bend some of these; none of them is a real ratio.", "",
              md_table(["ratio", "config", "realised"], rows), ""]
    # ugly cases
    ug = info["ugly"]
    real = {
        "engine_failure": sum(1 for p in paid if p.engine_failure),
        "aa_partial": sum(1 for p in paid if "aa_partial" in p.flags),
        "aa_failed": sum(1 for p in paid if "aa_failed" in p.flags),
        "unknown_isin": info.get("realised_unknown_isin"),
        "plausibility": info.get("realised_plausibility"),
        "second_no_show": sum(1 for p in paid if getattr(p, "second_no_show_at", None)),
        "refund_requested": sum(1 for p in paid if p.tl.get("refund")),
        "deletion_requested": sum(1 for p in paid if p.tl.get("deletion")),
        "grievance": info.get("realised_grievance"),
        "payment_failed": sum(1 for p in paid if p.state_id == "S12"),
        "lapsed": sum(1 for p in paid if p.state_id == "S13"),
        "difm_prospect_rule": info.get("realised_prospects_rule"),
        "sharpen": info.get("realised_sharpen"),
        "life_event": info.get("realised_life_event"),
        "consent_expired": sum(1 for p in paid if p.state_id == "S15"),
        "difm_prospect_manual": info.get("realised_prospects_manual"),
    }
    rows = []
    for k in list(cfg["ugly_cases"]["cases"]) + ["difm_prospect_manual"]:
        surf = cfg["ugly_cases"]["cases"].get(k, {}).get("surfaces", "M02, Zoho view")
        rows.append([k, ug[k], real[k], surf])
    lines += ["## 4. Ugly cases", "", md_table(["case", "wanted", "present", "surfaces on"], rows), ""]
    # N01 lists
    mp = res["multi"]
    rows = [[a, b, n] for (a, b), n in sorted(mp["pairs"].items(), key=lambda x: (-x[1], x[0]))]
    lines += ["## 5. The N01 multi-predicate list (the precedence gap list)", "",
              "%d people have more than one state predicate true at the anchor. Each row: the state the precedence "
              "picks, a state that also holds, and how many people. These go to the principal officer's seat as "
              "gaps." % mp["people"], "",
              md_table(["resolved state", "also holds", "people"], rows) if rows else "None.", ""]
    rows = [[s, why, n] for (s, why), n in sorted(res["nopred"].items())]
    lines += ["No predicate holds at the anchor (the person keeps the state they were in):", "",
              md_table(["kept state", "why", "people"], rows) if rows else "None.", ""]
    rows = [[a, b, n] for (a, b), n in sorted(res["mismatch"].items())]
    lines += ["Generated target against the resolved state (should be none):", "",
              md_table(["target", "resolved", "people"], rows) if rows else "None: every person resolves to the state the generator aimed at.", ""]
    tr = res["transitions"]
    rows = [[a, b, n] for (a, b), n in sorted(tr["outside_exits"].items(), key=lambda x: (-x[1], x[0]))]
    lines += ["State changes outside the states.json exits (%d of %d changes):" % (sum(tr["outside_exits"].values()), tr["total"]), "",
              md_table(["from", "to", "times"], rows) if rows else "None.", ""]
    # checks
    ev = res["events"]
    g = res["gate"]
    rows = [
        ["coherence rule violations", sum(res["coherence"].values()), "zero wanted; by rule: %s" % (dict(res["coherence"]) or "none")],
        ["stored bands that miss the truth", res["stored_consistency"], "zero wanted"],
        ["one state per person", "%d of %d" % (sum(1 for p in people if p.layer != "lead" and p.state_id), sum(1 for p in people if p.layer != "lead")),
         "OTP'd people with exactly one resolved state; leads read S0 or S0w"],
        ["built plans", g["built"], ""],
        ["built plans with an unknown gate field", g["unknown_gate_fields"], "zero wanted (the 16 gate fields)"],
        ["built plans with a not-sure React field", g["unknown_react_fields"], "zero wanted (phase 9: the gate is every field the React reads; health_floater has no band)"],
        ["D13 rows (fields resolved as a range)", g["d13_rows"], "%d without an earlier skip" % g["d13_without_prior_skip"]],
        ["events", ev["rows"], ""],
        ["events before signed_up", ev["before_signed_up"], "zero wanted (A01 and A02 come before the OTP by design)"],
        ["plan_read before plan_built", ev["plan_read_before_built"], "zero wanted"],
        ["events after the anchor", ev["after_anchor"], "zero wanted"],
        ["event names not on the board", sum(ev["unknown_names"].values()), dict(ev["unknown_names"]) or "none"],
        ["S2 people re-dated to fill a ladder bucket", moved, "floor %d per bucket" % ctx.tx["s2_bucket_floor"]],
        ["minimisation scan", "phase B", "runs on the exports"],
    ]
    lines += ["## 6. Checks", "", md_table(["check", "result", "note"], rows), ""]
    # volumes
    rows = [[k, len(v), sum(len(x) if isinstance(x, list) else 1 for x in v.values())] for k, v in T.items()]
    rows.append(["events.jsonl", "", len(events)])
    lines += ["## 7. Volumes", "", md_table(["table", "people with rows", "rows"], rows), ""]
    evc = collections.Counter(e["event"] for e in events)
    lines += ["Most frequent events: " + ", ".join("%s %d" % kv for kv in evc.most_common(15)), ""]
    nd = collections.Counter(n["cap_check"] for v in T["nudges_sent"].values() for n in v)
    moved = sum(1 for v in T["nudges_sent"].values() for n in v if n["sent_at"] and n["sent_at"] != n["due_at"])
    lines += ["Nudges (every ladder step that fell due): " + ", ".join("%s %d" % kv for kv in sorted(nd.items())) +
              ". %d sent later than due because they fell between 21:00 and 09:00 (N01 has no quiet-hours rule; "
              "gap, to be decided)." % moved, ""]
    # decisions
    rows = []
    for k, v in cfg.items():
        if isinstance(v, dict) and v.get("added") == "phase A":
            rows.append([k, v.get("cause", ""), (v.get("rule") or v.get("ref") or v.get("about") or "")[:170]])
    lines += ["## 8. Decisions taken in phase A where the plan was silent", "",
              "Each is a block in seed/config.json with added = phase A; Vatsal vetoes by reply.", "",
              md_table(["config block", "cause", "what"], rows), ""]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- writing

def write_keyed(path, table):
    with open(path, "w", encoding="ascii") as f:
        f.write("{\n")
        items = list(table.items())
        for i, (k, v) in enumerate(items):
            f.write(json.dumps(k) + ":" + json.dumps(v, separators=(",", ":"), ensure_ascii=True))
            f.write(",\n" if i + 1 < len(items) else "\n")
        f.write("}\n")


def build_run(cfg, board, names, anchor, run):
    ctx = Ctx(cfg, board, names, anchor, run)
    R = random.Random("%s:%s:global" % (ctx.seed, run))
    specs, info = plan_population(ctx, R)
    people = []
    for i, spec in enumerate(specs):
        p = Person(ctx, i, spec)
        p.period = spec.get("period")
        p.method = spec.get("method")
        p.s19_ranges = False
        make_identity(p, ctx)
        if p.layer != "lead":
            make_truth(p, ctx)
        people.append(p)
    jr = cfg["journey_rates"]
    for p in people:
        if p.layer == "paid" and p.base == "S19":
            p.s19_ranges = p.r.random() < jr["s19_only_ranges_missing"]
        p.s16 = p.layer == "paid" and (p.path == "manual" or "aa_failed" in p.flags)
        if p.layer == "lead":
            journey_lead(p, ctx)
        elif p.layer != "paid":
            journey_free(p, ctx)
        elif p.tier == "difm":
            journey_difm(p, ctx)
        else:
            journey_paid(p, ctx)
    moved = s2_bucket_floor(people, ctx)
    select_after(people, ctx, R, info)
    for p in people:
        if p.plans:
            finalize_versions(p, ctx)
    settle_prospects(people, ctx, R, info)
    settle_reveal(people, ctx, R, info)
    rb = cfg["reveal_bands"]
    for p in people:
        if getattr(p, "reveal_upto", 0) == 7:
            p.ev(p.tl["reveal"], "reveal_seen", "R09", income_band=rb["income"]["labels"][p.income_band],
                 corpus_band=rb["corpus"]["labels"][p.corpus_band], savings_band=rb["savings"]["labels"][p.savings_band],
                 journey_feel=p.journey_feel, aspiration=p.aspiration, path_now_band=p.path_now_band,
                 path_yes_band=p.path_yes_band, age_band=p.age_band, city=p.city)
    settle_isins(people, ctx, R, info)
    settle_tickets(people, ctx, R, info)
    assign_ids(people, ctx, R)
    reassign(people, ctx, R)
    for p in people:
        p.F = flags_of(p, ctx)
        p.hist, p.gaps = ([], []) if p.layer == "lead" else history(p.F, ctx)
        if p.layer == "lead":
            p.state_id = cfg["lead_journey_stage"]["web_reveal"] if p.source == "web_reveal" else cfg["lead_journey_stage"]["other"]
            p.state_entered_at = p.created_at
        else:
            p.state_id = p.hist[-1][1] if p.hist else None
            p.state_entered_at = p.hist[-1][0] if p.hist else None
        p.progress = None if p.layer == "lead" else (100 if p.tl.get("built") else progress_pct(p, ctx))
        p.fulfilment = fulfilment(p, ctx)
    for p in people:
        decorate(p, ctx)
    T, events = build_tables(people, ctx)
    res = validate(people, events, ctx)
    out = os.path.join(ROOT, "data", "seed", run)
    os.makedirs(out, exist_ok=True)
    for name, table in T.items():
        write_keyed(os.path.join(out, name + ".json"), table)
    with open(os.path.join(out, "staff.json"), "w", encoding="ascii") as f:
        json.dump(dict((s["staff_id"], s) for s in ctx.staff), f, indent=1, ensure_ascii=True)
        f.write("\n")
    with open(os.path.join(out, "config.json"), "w", encoding="ascii") as f:
        json.dump(config_table(ctx), f, indent=1, ensure_ascii=True)
        f.write("\n")
    with open(os.path.join(out, "events.jsonl"), "w", encoding="ascii") as f:
        for e in events:
            f.write(json.dumps(e, separators=(",", ":"), ensure_ascii=True) + "\n")
    rep = report(people, T, events, ctx, info, res, moved)
    with open(os.path.join(out, "report.md"), "w", encoding="ascii") as f:
        f.write(rep)
    return people, T, events, res, info


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--run", choices=["run-500", "run-3000"], action="append")
    ap.add_argument("--anchor", help="YYYY-MM-DD; default the run date")
    args = ap.parse_args()
    cfg = load("seed/config.json")
    names = load("seed/names.json")
    board = Board()
    errs = check_inputs(cfg, board)
    if errs:
        for e in errs:
            print("input check: " + e)
        sys.exit(1)
    anchor = dt.date.fromisoformat(args.anchor) if args.anchor else dt.date.today()
    for run in (args.run or ["run-500", "run-3000"]):
        people, T, events, res, info = build_run(cfg, board, names, anchor, run)
        print("%s: %d people, %d events, anchor %s; report data/seed/%s/report.md" % (
            run, len(people), len(events), anchor.isoformat(), run))


if __name__ == "__main__":
    main()
