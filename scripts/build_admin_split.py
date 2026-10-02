#!/usr/bin/env python3
"""docs/admin_split.html from data/admin_split.json (W12, 2 Oct 2026).

The crisp page: Spinach's admin feature matrix (9 Jul 2026) with one column added (the version picked for launch, who
provides it, one line why), the five things Spinach builds, what Zoho and the consoles hold, the open items. The working
notes (the full reasoning per row, our own items outside the sheet, the 13 sketches against Zoho, the outcome) are folded
at the bottom for doc 2. Read-only over the data file; ASCII and the forbidden words are checked like every other page.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_site as site  # noqa: E402

PAGE = "admin_split.html"
DATA_FILE = os.path.join(HERE, "..", "data", "admin_split.json")
OUT_FILE = os.path.join(HERE, "..", "docs", PAGE)
esc = site.esc

EXTRA_CSS = """
  .split{width:100%;border-collapse:collapse;font-size:12.5px;margin:8px 0 22px}
  .split th,.split td{border:1px solid var(--line);padding:7px 9px;vertical-align:top;text-align:left}
  .split th{background:var(--panel);font-weight:600}
  .split td.f{font-weight:600;white-space:nowrap}
  .split td.v{font-size:11.5px;color:var(--mute)}
  .split td.pick{background:#FFF8DC;min-width:220px}
  .split td.pick b{font-size:14px}
  .split tr.why td{background:var(--panel);border-top:0}
  .split tr.why p{margin:4px 0}
  .split ul{margin:2px 0 2px 16px;padding:0}
  .split li{margin:2px 0}
  .levels{display:flex;gap:18px;flex-wrap:wrap;font-size:12.5px;margin:6px 0 10px}
  .levels span b{font-weight:600}
  .open li,.builds li{margin:4px 0}
  details.notes{margin:26px 0 10px;border-top:1px solid var(--line);padding-top:10px}
  details.notes summary{cursor:pointer;font-weight:600;font-size:13px}
  details.notes h3{font-size:13px;margin:16px 0 4px}
  .tbd{color:#7A4B00}
"""


def paras(items):
    return "".join("<p>%s</p>" % esc(p) for p in items)


def ul(items, cls=""):
    if not items:
        return ""
    return '<ul%s>%s</ul>' % ((' class="%s"' % cls) if cls else "", "".join("<li>%s</li>" % esc(x) for x in items))


def cells_v(r):
    return "".join('<td class="v">%s</td>' % (ul(r[k]) if r[k] else '<span class="meta">-</span>') for k in ("v1", "v1_5", "v2", "v3"))


def sheet_table(doc):
    head = ("<tr><th>Admin feature</th><th>V1 - Collect and create views</th><th>V1.5 - Enhanced views</th>"
            "<th>V2 - Operational actions</th><th>V3 - Analytics and intelligence</th><th>Pick, who, why</th></tr>")
    rows = []
    for r in doc["features"]:
        pick = '<td class="pick"><b>%s, %s</b><br>%s</td>' % (esc(r["pick"]), esc(r["who"]), esc(r["line"]))
        rows.append('<tr id="f%d"><td class="f">%d. %s</td>%s%s</tr>' % (r["n"], r["n"], esc(r["feature"]), cells_v(r), pick))
    return '<table class="split">' + head + "".join(rows) + "</table>"


def builds_table(doc):
    head = "<tr><th>Spinach builds</th><th>What it holds</th></tr>"
    rows = "".join('<tr><td class="f">%s %s</td><td>%s</td></tr>' % (esc(b["id"]), esc(b["what"]), esc(b["detail"])) for b in doc["builds"])
    return '<table class="split">' + head + rows + "</table>"


def holds_table(doc):
    head = "<tr><th>Who</th><th>Holds (details in doc 2)</th></tr>"
    rows = "".join('<tr><td class="f">%s</td><td>%s</td></tr>' % (esc(h["who"]), esc(h["what"])) for h in doc["holds"])
    return '<table class="split">' + head + rows + "</table>"


# ---- the folded working notes ---------------------------------------------------------------------------------

def why_row(r, span):
    parts = [paras(r["why"])]
    parts.append("<p><b>Zoho holds</b> %s</p>" % esc(r["zoho"]))
    parts.append("<p><b>Spinach does</b> %s</p>" % esc(r["spinach"]))
    if r.get("verify"):
        parts.append("<p><b>To be verified</b></p>" + ul(r["verify"]))
    if r.get("decide"):
        parts.append('<p class="tbd"><b>Open</b></p>' + ul(r["decide"], "tbd"))
    parts.append('<p class="meta">Sketches: %s.</p>' % esc(r["sketches"]))
    return '<tr class="why"><td colspan="%d">%s</td></tr>' % (span, "".join(parts))


def notes_sheet(doc):
    head = "<tr><th>Admin feature</th><th>Pick, who</th><th>The full reasoning</th></tr>"
    rows = []
    for r in doc["features"]:
        rows.append('<tr id="n%d"><td class="f">%d. %s</td><td class="pick"><b>%s, %s</b><br>%s</td><td>%s%s</td></tr>' %
                    (r["n"], r["n"], esc(r["feature"]), esc(r["pick"]), esc(r["who"]), esc(r["line"]),
                     paras(r["why"]), ("<p><b>Zoho holds</b> %s</p><p><b>Spinach does</b> %s</p>" % (esc(r["zoho"]), esc(r["spinach"]))) +
                     (("<p><b>To be verified</b></p>" + ul(r["verify"])) if r.get("verify") else "") +
                     (('<p class="tbd"><b>Open</b></p>' + ul(r["decide"], "tbd")) if r.get("decide") else "") +
                     '<p class="meta">Sketches: %s.</p>' % esc(r["sketches"])))
    return '<table class="split">' + head + "".join(rows) + "</table>"


def own_table(doc):
    head = "<tr><th>Item</th><th>Where it comes from</th><th>What it holds (the best version)</th><th>Who</th></tr>"
    rows = []
    for r in doc["own"]:
        rows.append('<tr id="o%d"><td class="f">%d. %s</td><td>%s</td><td>%s</td><td class="pick">%s</td></tr>' %
                    (r["n"], r["n"], esc(r["feature"]), esc(r["source"]), ul(r["scope"]), esc(r["pick"])))
        rows.append(why_row(r, 4))
    return '<table class="split">' + head + "".join(rows) + "</table>"


def sketches_table(doc):
    head = "<tr><th>Page</th><th>Sketch</th><th>What it imagined</th><th>Zoho or a console instead</th><th>Status</th></tr>"
    rows = "".join('<tr><td class="f">%d</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' %
                   (s["page"], esc(s["title"]), esc(s["imagined"]), esc(s["zoho"]), esc(s["status"])) for s in doc["sketches"])
    return '<table class="split">' + head + rows + "</table>"


def notes(doc):
    u = doc["universal"]
    o = doc["outcome"]
    body = ('<h3>The rules the picks rest on</h3>' + ul(doc["rules"]) +
            '<h3>Is the sheet the universal set?</h3><p>%s</p>%s<p><b>The CRM set, later</b> %s</p>' % (esc(u["answer"]), ul(u["outside"]), esc(u["crm_later"])) +
            '<h3>The sheet, the full reasoning per row</h3>' + notes_sheet(doc) +
            '<h3>Our own items, outside the sheet</h3><p class="meta">%s</p>%s' % (esc(doc["own_note"]), own_table(doc)) +
            '<h3>The sketches against Zoho</h3><p class="meta">%s</p>%s' % (esc(doc["sketches_note"]), sketches_table(doc)) +
            '<h3>Outcome, if the picks are confirmed</h3><p><b>Spinach builds</b></p>%s<p><b>Zoho holds</b></p>%s<p><b>The consoles</b> %s</p>'
            '<p><b>What changes against the board</b> %s</p><p><b>To be decided</b></p>%s<p><b>To be verified in the trial</b></p>%s'
            % (ul(o["spinach"]), ul(o["zoho"]), esc(o["consoles"]), esc(o["changes"]), ul(o["decide"], "tbd"), ul(o["verify"])))
    return '<details class="notes" id="notes"><summary>Working notes for doc 2 (the reasoning, our own items, the sketches)</summary>' + body + '</details>'


def kajal_table(doc):
    head = "<tr><th>Her section</th><th>Her line</th><th>Lands at</th><th>Who holds it</th></tr>"
    rows = []
    last = None
    for k in doc["kajal"]:
        sec = esc(k["sec"]) if k["sec"] != last else ""
        last = k["sec"]
        rows.append('<tr><td class="f">%s</td><td>%s</td><td class="pick"><b>%s</b></td><td>%s</td></tr>' %
                    (sec, esc(k["item"]), esc(k["lands"]), esc(k["who"])))
    return '<table class="split">' + head + "".join(rows) + "</table>"


def build_page(doc):
    intro = ('<section><h1>The admin split: what Spinach builds</h1><p class="lead">%s</p><p class="meta">Cause: %s</p></section>'
             % (esc(doc["about"]), esc(doc["cause"])))
    levels = '<div class="levels">' + "".join('<span><b>%s</b> %s</span>' % (esc(a), esc(b)) for a, b in doc["levels"]) + '</div>'
    sheet = ('<section id="sheet"><h2>1. Spinach\'s sheet, with the pick</h2><p class="meta">%s The four version columns are the sheet\'s own words.</p>'
             % esc(doc["pick_rule"]) + levels + sheet_table(doc) + '</section>')
    builds = '<section id="builds" class="builds"><h2>2. What Spinach builds</h2>' + builds_table(doc) + '</section>'
    holds = '<section id="holds"><h2>3. What the bought tools hold</h2>' + holds_table(doc) + '</section>'
    open_ = '<section id="open" class="open"><h2>4. Open before Spinach plans</h2>' + ul(doc["open"], "tbd") + '</section>'
    kajal = ('<section id="kajal"><h2>5. Kajal\'s list of 8 Sep 2026, line by line</h2><p class="meta">%s</p>%s</section>'
             % (esc(doc["kajal_note"]), kajal_table(doc)))
    body = intro + sheet + builds + holds + open_ + kajal + notes(doc)
    return (site.head("yeslyf admin split", site.CSS + site.SUBNAV_CSS + EXTRA_CSS) + '<body>\n' +
            site.header("admin_wireframes.html", "admin split: what Spinach builds", who_html="", show_export=False,
                        tabs=None, setup_link=True) +
            site.seed_subnav(PAGE) +
            '<main class="main" style="max-width:none">' + body + '</main>\n' +
            site.store_script() + '<script>' + site.js_pill("admin_split") + '</script>\n</body>\n</html>\n')


def validate(doc):
    problems = []
    for key in ("about", "cause", "pick_rule", "rules", "levels", "universal", "features", "builds", "holds", "open",
                "own_note", "own", "sketches_note", "sketches", "outcome"):
        if key not in doc:
            problems.append("missing %s" % key)
    ns = [r["n"] for r in doc.get("features", [])]
    if ns != list(range(1, 13)):
        problems.append("features are not numbered 1 to 12: %s" % ns)
    for r in doc.get("features", []):
        for key in ("feature", "v1", "v1_5", "v2", "v3", "pick", "who", "line", "why", "zoho", "spinach", "verify", "decide", "sketches"):
            if key not in r:
                problems.append("feature %s: missing %s" % (r.get("n"), key))
        if r.get("pick") not in ("V1", "V1.5", "V2", "V3"):
            problems.append("feature %s: pick %r is not one level" % (r.get("n"), r.get("pick")))
        if r.get("who") not in ("Zoho", "Spinach", "Consoles"):
            problems.append("feature %s: who %r is not Zoho, Spinach or Consoles" % (r.get("n"), r.get("who")))
    for r in doc.get("own", []):
        for key in ("feature", "source", "scope", "pick", "why", "zoho", "spinach", "verify", "decide", "sketches"):
            if key not in r:
                problems.append("own %s: missing %s" % (r.get("n"), key))
    if len(doc.get("sketches", [])) != 13:
        problems.append("sketches: %d rows, expected 13" % len(doc.get("sketches", [])))
    # Kajal's 48 lines are the placement rows of the Admin and CRM tab: every one must land somewhere on this page.
    placement = site.load("admin_crm.json").get("PLACEMENT", [])
    want = set(r["item"] for r in placement)
    have = set(k.get("item") for k in doc.get("kajal", []))
    if want != have:
        problems.append("kajal lines do not match the placement rows: missing %s, extra %s" % (sorted(want - have), sorted(have - want)))
    for k in doc.get("kajal", []):
        if not k.get("lands") or not k.get("who"):
            problems.append("kajal line %r has no landing row or owner" % k.get("item"))
    text = json.dumps(doc)
    for word in site.FORBIDDEN:
        if word in text:
            problems.append("forbidden word %s" % word)
    return problems


def main():
    with open(DATA_FILE) as fh:
        doc = json.load(fh)
    problems = validate(doc)
    if problems:
        raise SystemExit("build_admin_split: " + "; ".join(problems))
    page = build_page(doc)
    site.check_ascii(PAGE, page)
    with open(OUT_FILE, "w") as fh:
        fh.write(page)
    print("wrote docs/%s (%d bytes; %d sheet rows, %d builds, %d own rows, %d sketches in the notes)" %
          (PAGE, len(page), len(doc["features"]), len(doc["builds"]), len(doc["own"]), len(doc["sketches"])))


if __name__ == "__main__":
    main()
