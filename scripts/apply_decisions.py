#!/usr/bin/env python3
"""Build data/screens_v02.json and data/changelog.json from the data layer.

Order of application:
  1. data/screens_v01.json, the accepted v0.1 skeleton (never edited).
  2. data/screen_meta_v02.json: template, path, frame, compliance flag and extra events per carried screen.
  3. data/decision_effects.json: groups in file order (the meeting brief first, then the section 0 overrides,
     then CLAUDE.md wording). Every edit writes its cause on the screen (v02.causes).
  4. data/v02/*.json overlays (phases 4 and 5): full screens that replace or add, each with v02.status and
     v02.causes; data/v02/flow.json fixes the order within a section when present. Edit groups carrying
     "stage": "after_generation" (phase 9) apply after the spine and the states are generated, so they can
     touch generated screens; the section strip (spine.json "strip") is drawn on every spine screen then.
  5. Events by template (appendix D) and the compliance checklist text.
  6. Validation (scripts/validate_v02.py, structural checks) then the write.
The changelog lists changed, added, dropped, rerouted, superseded and to-be-verified items and the counts
for Spinach. Hand-edit data/*.json, never docs/.
"""
import copy
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import validate_v02  # noqa: E402

NUM_EVENTS = ["set", "skip", "hesitation_45", "hesitation_90", "hesitation_120", "band_tapped", "exact_entered"]
TBV = "to be verified:"
FORWARD_TAGS = ("required", "optional", "default", "system")  # mandatory and optional inputs (Vatsal, 17 Sep 2026)


def load(name):
    with open(os.path.join(DATA, name)) as fh:
        return json.load(fh)


def dump(name, obj):
    text = json.dumps(obj, indent=1, ensure_ascii=True) + "\n"
    for i, ch in enumerate(text):
        if ord(ch) > 126:
            raise SystemExit("%s: non-ASCII character at %d: %r" % (name, i, text[i - 20:i + 20]))
    with open(os.path.join(DATA, name), "w") as fh:
        fh.write(text)
    print("wrote data/%s (%d bytes)" % (name, len(text)))


class Build:
    def __init__(self):
        v01 = load("screens_v01.json")
        meta = load("screen_meta_v02.json")
        self.sections = meta["sections"]
        self.screens = []
        self.byid = {}
        for s in v01["screens"]:
            s = copy.deepcopy(s)
            s.setdefault("frame", "phone")
            m = meta["screens"].get(s["id"])
            if m is None:
                raise SystemExit("screen_meta_v02.json has no entry for %s" % s["id"])
            s["template"] = m["template"]
            s["path"] = m["path"]
            if "frame" in m:
                s["frame"] = m["frame"]
            s["compliance"] = copy.deepcopy(m["compliance"])
            s["events"] = list(m.get("events", []))
            if m.get("reason_note"):
                s["compliance"]["note"] = m["reason_note"]
            s["v02"] = {"status": "kept", "causes": []}
            self.add_screen(s)
        self.rerouted = []

    def add_screen(self, s, after=None, before=None):
        if s["id"] in self.byid:
            raise SystemExit("duplicate screen id %s" % s["id"])
        if after is not None:
            i = self.index(after) + 1
        elif before is not None:
            i = self.index(before)
        else:
            i = len(self.screens)
        self.screens.insert(i, s)
        self.byid = {x["id"]: x for x in self.screens}

    def index(self, sid):
        for i, s in enumerate(self.screens):
            if s["id"] == sid:
                return i
        raise SystemExit("unknown screen %s" % sid)

    def get(self, sid):
        s = self.byid.get(sid)
        if s is None:
            raise SystemExit("unknown screen %s" % sid)
        return s

    # ---- edit helpers -------------------------------------------------------------------------------------
    @staticmethod
    def row_matches(row, match):
        if match is None:
            return False
        if row[0] != match[0]:
            return False
        if len(match) < 2 or match[1] is None:
            return True
        return row[1] == match[1]

    def find_row(self, s, match):
        hits = [i for i, row in enumerate(s["ui"]) if self.row_matches(row, match)]
        if len(hits) != 1:
            raise SystemExit("%s: ui match %r found %d times" % (s["id"], match, len(hits)))
        return hits[0]

    def touch(self, s, cause, status="changed"):
        v = s["v02"]
        if cause not in v["causes"]:
            v["causes"].append(cause)
        if v["status"] == "kept" or (v["status"] == "changed" and status == "rebuilt"):
            v["status"] = status

    def apply(self, e, group_cause):
        cause = e.get("cause", group_cause)
        op = e["op"]
        if op == "add":
            s = copy.deepcopy(e["value"])
            s.setdefault("frame", "phone")
            s.setdefault("events", [])
            for key in ("template", "path", "compliance", "tier", "spec", "ui", "title", "purpose", "sec"):
                if key not in s:
                    raise SystemExit("add %s: missing %s" % (s.get("id"), key))
            s["v02"] = {"status": "new", "causes": [cause]}
            self.add_screen(s, after=e.get("after"), before=e.get("before"))
            return
        if op == "reroute" and e["screen"] == "*":
            for s in self.screens:
                self.reroute(s, e["from"], e["to"], cause)
            return
        s = self.get(e["screen"])
        if op == "set":
            s[e["key"]] = e["value"]
            self.touch(s, cause)
        elif op == "ui":
            s["ui"] = e["value"]
            self.touch(s, cause, "rebuilt")
        elif op == "ui_replace":
            s["ui"][self.find_row(s, e["match"])] = e["value"]
            self.touch(s, cause)
        elif op == "ui_remove":
            del s["ui"][self.find_row(s, e["match"])]
            self.touch(s, cause)
        elif op == "ui_insert":
            after = e.get("after", "end")
            if after == "end":
                s["ui"].append(e["value"])
            elif after == "start":
                s["ui"].insert(0, e["value"])
            else:
                s["ui"].insert(self.find_row(s, after) + 1, e["value"])
            self.touch(s, cause)
        elif op == "table_row":
            row = s["ui"][e["index"]]
            if row[0] != "table":
                raise SystemExit("%s: ui[%d] is not a table" % (s["id"], e["index"]))
            hits = [i for i, r in enumerate(row[2]) if r[0] == e["row"]]
            if len(hits) != 1:
                raise SystemExit("%s: table row %r found %d times" % (s["id"], e["row"], len(hits)))
            row[2][hits[0]] = e["value"]
            self.touch(s, cause)
        elif op == "table_replace":
            if s["ui"][e["index"]][0] != "table":
                raise SystemExit("%s: ui[%d] is not a table" % (s["id"], e["index"]))
            s["ui"][e["index"]] = e["value"]
            self.touch(s, cause)
        elif op == "table_add_row":
            row = s["ui"][e["index"]]
            if row[0] != "table":
                raise SystemExit("%s: ui[%d] is not a table" % (s["id"], e["index"]))
            row[2].append(e["value"])
            self.touch(s, cause)
        elif op == "table_remove_row":
            row = s["ui"][e["index"]]
            if row[0] != "table":
                raise SystemExit("%s: ui[%d] is not a table" % (s["id"], e["index"]))
            hits = [i for i, r in enumerate(row[2]) if r[0] == e["row"]]
            if len(hits) != 1:
                raise SystemExit("%s: table row %r found %d times" % (s["id"], e["row"], len(hits)))
            del row[2][hits[0]]
            self.touch(s, cause)
        elif op == "field_replace":
            fields = s["spec"]["fields"]
            hits = [i for i, f in enumerate(fields) if isinstance(f, dict) and f.get("f") == e["field"]]
            if len(hits) != 1:
                raise SystemExit("%s: spec field %r found %d times" % (s["id"], e["field"], len(hits)))
            fields[hits[0]] = e["value"]
            self.touch(s, cause)
        elif op == "forward":
            # Moving forward block (spec.forward) plus one tag per captured field (Vatsal, 17 Sep 2026):
            # every field on the screen must be named in e["tags"], so nothing stays unclassified.
            s["spec"]["forward"] = e["value"]
            tags = dict(e.get("tags", {}))
            fields = s["spec"]["fields"]
            for i, f in enumerate(fields):
                key = f if isinstance(f, str) else f.get("f")
                if key not in tags:
                    raise SystemExit("%s: forward tags miss field %r" % (s["id"], key))
                tag = tags.pop(key)
                if tag not in FORWARD_TAGS:
                    raise SystemExit("%s: forward tag %r on %r not in %s" % (s["id"], tag, key, FORWARD_TAGS))
                if isinstance(f, str):
                    fields[i] = {"f": f, "forward": tag}
                else:
                    f["forward"] = tag
            if tags:
                raise SystemExit("%s: forward tags name unknown fields %s" % (s["id"], sorted(tags)))
            self.touch(s, cause)
        elif op == "status":
            if e["value"] not in ("changed", "rebuilt", "new"):
                raise SystemExit("%s: status op cannot set %r" % (s["id"], e["value"]))
            s["v02"]["status"] = e["value"]
            self.touch(s, cause, e["value"])
        elif op == "split":
            if s["v02"]["status"] != "dropped":
                raise SystemExit("%s: split relabels a dropped screen; status is %s" % (s["id"], s["v02"]["status"]))
            for inst in e["instances"]:
                if inst not in self.byid:
                    raise SystemExit("%s: split instance %s does not exist" % (s["id"], inst))
            v = s["v02"]
            s["v02"] = {"status": "split", "causes": v["causes"] + ([cause] if cause not in v["causes"] else []),
                        "pointer": v.get("pointer", ""), "instances": list(e["instances"])}
        elif op in ("spec_replace", "spec_remove"):
            lines = s["spec"][e["key"]]
            hits = [i for i, l in enumerate(lines) if l == e["match"]]
            if len(hits) != 1:
                raise SystemExit("%s: spec.%s line %r found %d times" % (s["id"], e["key"], e["match"], len(hits)))
            if op == "spec_replace":
                lines[hits[0]] = e["value"]
            else:
                del lines[hits[0]]
            self.touch(s, cause)
        elif op == "spec_add":
            v = e["value"]
            if e["key"] == "branches":
                s["spec"]["branches"].append(v)
            elif isinstance(v, list):
                s["spec"][e["key"]].extend(v)
            else:
                s["spec"][e["key"]].append(v)
            self.touch(s, cause)
        elif op == "spec_set":
            s["spec"][e["key"]] = e["value"]
            self.touch(s, cause)
        elif op == "reroute":
            self.reroute(s, e["from"], e["to"], cause)
        elif op == "drop":
            s["v02"] = {"status": "dropped", "causes": [cause], "pointer": e["pointer"]}
        elif op == "meta":
            for key in ("template", "path", "compliance", "frame"):
                if key in e:
                    s[key] = e[key]
            if "events" in e:
                s["events"] = list(e["events"])
            self.touch(s, cause)
        else:
            raise SystemExit("unknown op %s" % op)

    def reroute(self, s, frm, to, cause):
        hit = False
        for row in s["ui"]:
            if row[0] in ("btn", "btn2", "link") and row[2] == frm:
                self.rerouted.append({"screen": s["id"], "label": row[1], "from": frm, "to": to, "cause": cause})
                row[2] = to
                hit = True
        for br in s["spec"]["branches"]:
            if br[1] == frm:
                br[1] = to
                hit = True
        if hit:
            self.touch(s, cause)

    # ---- overlays -----------------------------------------------------------------------------------------
    def overlay(self):
        """Phases 4 and 5: edit groups (data/v02/*edits*.json), full screens (data/v02/screens_*.json),
        generated instances (gen_spine over spine.json, gen_states over states.json), then flow.json order."""
        files = sorted(glob.glob(os.path.join(DATA, "v02", "*.json")))
        until = int(os.environ.get("UNTIL_PHASE", "9"))
        if until < 5:
            files = [p for p in files if not os.path.basename(p).startswith("phase5") and os.path.basename(p) != "states.json"]
        later = []
        for path in files:
            name = os.path.basename(path)
            if "edits" not in name:
                continue
            with open(path) as fh:
                doc = json.load(fh)
            for g in doc["groups"]:
                if g.get("stage") == "after_generation":
                    later.append(g)
                    continue
                for e in g["edits"]:
                    self.apply(e, g["cause"])
        for path in files:
            name = os.path.basename(path)
            if not name.startswith("screens_"):
                continue
            with open(path) as fh:
                doc = json.load(fh)
            self.merge(doc.get("screens", []), name)
            for r in doc.get("rerouted", []):
                self.rerouted.append(r)
        spine = os.path.join(DATA, "v02", "spine.json")
        if os.path.exists(spine):
            import gen_spine
            with open(spine) as fh:
                self.merge(gen_spine.generate(json.load(fh)), "spine.json")
        states = os.path.join(DATA, "v02", "states.json")
        if os.path.exists(states) and until >= 5:
            import gen_states
            with open(states) as fh:
                self.merge(gen_states.generate(json.load(fh), self.byid), "states.json")
        for g in later:
            for e in g["edits"]:
                self.apply(e, g["cause"])
        if os.path.exists(spine):
            with open(spine) as fh:
                self.draw_strip(json.load(fh).get("strip"))
        flow = os.path.join(DATA, "v02", "flow.json")
        if os.path.exists(flow):
            with open(flow) as fh:
                order = json.load(fh)["order"]
            pos = {sid: i for i, sid in enumerate(order)}
            missing = [s["id"] for s in self.screens if s["id"] not in pos and s["v02"]["status"] not in ("dropped", "split")]
            unknown = [sid for sid in order if sid not in self.byid]
            if missing:
                raise SystemExit("flow.json lacks: %s" % " ".join(missing))
            if unknown:
                print("note: flow.json names screens not built yet: %s" % " ".join(unknown))
            self.screens.sort(key=lambda s: pos.get(s["id"], 10 ** 6))
            self.byid = {x["id"]: x for x in self.screens}

    def draw_strip(self, strip):
        """Section strip on every spine screen (phase 9, section relief): section name, step x of y, sections
        done of eight; the first screen of each section adds the "Now: <section>, N quick questions" line.
        Detail screens carry their parent's step. spine.json "strip" declares the structure; the text is derived."""
        if not strip:
            return
        cause = strip["cause"]
        total = len(strip["sections"])
        for k, sec in enumerate(strip["sections"]):
            steps = sec["screens"]
            for i, sid in enumerate(steps):
                text = "%s: step %d of %d; %d of %d sections done" % (sec["label"], i + 1, len(steps), k, total)
                rows = [["strip", text]]
                if i == 0:
                    rows.append(["p", "Now: %s, %s quick questions." % (sec["label"].lower(), sec.get("questions", "N"))])
                self.insert_strip(sid, rows, cause)
                for det, parent in sec.get("details", {}).items():
                    if parent == sid:
                        self.insert_strip(det, [["strip", text + " (detail)"]], cause)
        for sid in strip.get("after", []):
            self.insert_strip(sid, [["strip", "%s: %d of %d sections done" % (strip.get("after_label", "Review and build"), total, total)]], cause)

    def insert_strip(self, sid, rows, cause):
        s = self.get(sid)
        if s["v02"]["status"] in ("dropped", "split"):
            raise SystemExit("strip: %s is not live" % sid)
        if any(r[0] == "strip" for r in s["ui"]):
            raise SystemExit("strip: %s already carries a strip" % sid)
        s["ui"][0:0] = rows
        self.touch(s, cause)

    def merge(self, screens, name):
        for s in screens:
            if True:
                s = copy.deepcopy(s)
                s.setdefault("frame", "phone")
                s.setdefault("events", [])
                v = s.get("v02") or {}
                if "causes" not in v or not v["causes"]:
                    raise SystemExit("%s: %s carries no cause" % (name, s["id"]))
                after, before = s.pop("after", None), s.pop("before", None)
                if s["id"] in self.byid:
                    old = self.byid[s["id"]]
                    status = v.get("status", "rebuilt")
                    if status == "dropped":
                        old["v02"] = {"status": "dropped", "causes": v["causes"], "pointer": v.get("pointer", "")}
                        continue
                    s["v02"] = {"status": status, "causes": old["v02"]["causes"] + [c for c in v["causes"] if c not in old["v02"]["causes"]]}
                    self.screens[self.index(s["id"])] = s
                    self.byid[s["id"]] = s
                else:
                    s["v02"] = {"status": v.get("status", "new"), "causes": v["causes"]}
                    if after is not None and after not in self.byid:
                        after = None
                    if before is not None and before not in self.byid:
                        before = None
                    self.add_screen(s, after=after, before=before)

    # ---- finish -------------------------------------------------------------------------------------------
    def finish(self, reasons):
        for s in self.screens:
            ev = ["%s_view" % s["id"]]
            if s["template"] == "T-num":
                ev += ["%s_%s" % (s["id"], x) for x in NUM_EVENTS]
                for lad in s["spec"].get("ladder", []):
                    ev.append("%s_ladder_%s" % (s["id"], lad[0]))
            for x in s.get("events", []):
                if x not in ev:
                    ev.append(x)
            s["events"] = ev
            for r in s["compliance"]["reasons"]:
                if r not in reasons:
                    raise SystemExit("%s: unknown compliance reason %r" % (s["id"], r))
            s["compliance"]["checks"] = [reasons[r]["check"] for r in s["compliance"]["reasons"]]


def tbv_items(screens):
    """Every 'to be verified: <item>' marker on a live screen, grouped by item text."""
    found = {}

    def walk(o, sid):
        if isinstance(o, str):
            i = o.find(TBV)
            while i >= 0:
                rest = o[i + len(TBV):].strip()
                cut = len(rest)
                for stop in (")", ";", ". ", "\n"):
                    j = rest.find(stop)
                    if 0 <= j < cut:
                        cut = j
                item = rest[:cut].strip().rstrip(".")
                found.setdefault(item, [])
                if sid not in found[item]:
                    found[item].append(sid)
                i = o.find(TBV, i + 1)
        elif isinstance(o, list):
            for x in o:
                walk(x, sid)
        elif isinstance(o, dict):
            for v in o.values():
                walk(v, sid)

    for s in screens:
        if s["v02"]["status"] not in ("dropped", "split"):
            walk({k: v for k, v in s.items() if k != "v02"}, s["id"])
    return [{"item": k, "screens": v} for k, v in sorted(found.items())]


def counts(screens, sections):
    live = [s for s in screens if s["v02"]["status"] not in ("dropped", "split")]
    by_sec = {}
    for sec in sections:
        items = [s for s in live if s["sec"] == sec[0]]
        t = {}
        for s in items:
            t[s["template"]] = t.get(s["template"], 0) + 1
        by_sec[sec[0]] = {"name": sec[1], "screens": len(items), "templates": len(t), "by_template": dict(sorted(t.items()))}
    t = {}
    for s in live:
        t[s["template"]] = t.get(s["template"], 0) + 1
    st = {}
    for s in screens:
        st[s["v02"]["status"]] = st.get(s["v02"]["status"], 0) + 1
    return {"total": len(live), "unique_templates": len(t), "by_template": dict(sorted(t.items())),
            "by_section": by_sec, "by_status": st}


def main():
    b = Build()
    effects = load("decision_effects.json")
    for g in effects["groups"]:
        for e in g["edits"]:
            b.apply(e, g["cause"])
    b.overlay()
    reasons = load("compliance_reasons.json")["reasons"]
    b.finish(reasons)

    problems = validate_v02.structural(b.screens)
    if problems:
        print("validation failed:")
        for p in problems:
            print("  " + p)
        return 1

    changelog = {
        "source": "scripts/apply_decisions.py over data/screens_v01.json, data/decision_effects.json and data/v02/",
        "changed": [{"id": s["id"], "title": s["title"], "status": s["v02"]["status"], "causes": s["v02"]["causes"]}
                    for s in b.screens if s["v02"]["status"] in ("changed", "rebuilt")],
        "added": [{"id": s["id"], "title": s["title"], "template": s["template"], "causes": s["v02"]["causes"]}
                  for s in b.screens if s["v02"]["status"] == "new"],
        "dropped": [{"id": s["id"], "title": s["title"], "pointer": s["v02"].get("pointer", ""), "causes": s["v02"]["causes"]}
                    for s in b.screens if s["v02"]["status"] == "dropped"],
        "split": [{"id": s["id"], "title": s["title"], "instances": s["v02"].get("instances", []), "pointer": s["v02"].get("pointer", ""), "causes": s["v02"]["causes"]}
                  for s in b.screens if s["v02"]["status"] == "split"],
        "rerouted": b.rerouted,
        "superseded": effects["superseded"],
        "to_be_verified": tbv_items(b.screens),
        "counts": counts(b.screens, b.sections),
    }
    dump("screens_v02.json", {"source": changelog["source"], "sections": b.sections, "screens": b.screens})
    dump("changelog.json", changelog)
    c = changelog["counts"]
    print("screens: %d live (%s); templates: %d; changed %d, added %d, dropped %d, split %d, rerouted %d, to be verified %d" % (
        c["total"], ", ".join("%s %d" % kv for kv in sorted(c["by_status"].items())), c["unique_templates"],
        len(changelog["changed"]), len(changelog["added"]), len(changelog["dropped"]), len(changelog["split"]),
        len(changelog["rerouted"]), len(changelog["to_be_verified"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
