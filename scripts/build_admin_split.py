#!/usr/bin/env python3
"""docs/admin_split.html from data/admin_split.json (W12, 2 Oct 2026).

Spinach's admin panel feature matrix (9 Jul 2026) with one column added (the version picked and who provides it) and the
explanation under each row; yeslyf's own admin items outside the sheet; the 13 sketches against Zoho; the outcome.
Read-only over the data file; ASCII and the forbidden words are checked like every other page.
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
  .split td.pick{background:#FFF8DC;min-width:200px}
  .split tr.why td{background:var(--panel);border-top:0}
  .split tr.why p{margin:4px 0}
  .split tr.why b{font-weight:600}
  .split ul{margin:2px 0 2px 16px;padding:0}
  .split li{margin:2px 0}
  .levels{display:flex;gap:18px;flex-wrap:wrap;font-size:12.5px;margin:6px 0 14px}
  .levels span b{font-weight:600}
  .rules li,.outcome li{margin:3px 0}
  .outcome h3{font-size:13px;margin:16px 0 4px}
  .tbd{color:#7A4B00}
"""


def paras(items):
    return "".join("<p>%s</p>" % esc(p) for p in items)


def ul(items, cls=""):
    if not items:
        return ""
    return '<ul%s>%s</ul>' % ((' class="%s"' % cls) if cls else "", "".join("<li>%s</li>" % esc(x) for x in items))


def why_row(r, span):
    parts = [paras(r["why"])]
    parts.append("<p><b>Zoho holds</b> %s</p>" % esc(r["zoho"]))
    parts.append("<p><b>Spinach does</b> %s</p>" % esc(r["spinach"]))
    if r.get("verify"):
        parts.append("<p><b>To be verified</b></p>" + ul(r["verify"]))
    if r.get("decide"):
        parts.append('<p class="tbd"><b>Open</b></p>' + ul(r["decide"], "tbd"))
    parts.append('<p class="meta">Sketches: %s. to be decided: confirm the pick.</p>' % esc(r["sketches"]))
    return '<tr class="why"><td colspan="%d">%s</td></tr>' % (span, "".join(parts))


def features_table(doc):
    head = ("<tr><th>Admin feature</th><th>V1 - Collect and create views</th><th>V1.5 - Enhanced views</th>"
            "<th>V2 - Operational actions</th><th>V3 - Analytics and intelligence</th><th>Pick: level, and who</th></tr>")
    rows = []
    for r in doc["features"]:
        cells = "".join("<td>%s</td>" % (ul(r[k]) if r[k] else '<span class="meta">-</span>') for k in ("v1", "v1_5", "v2", "v3"))
        pick = '<td class="pick"><b>%s</b><br>%s</td>' % (esc(r["pick_level"]), esc(r["pick_who"]))
        rows.append('<tr id="f%d"><td class="f">%d. %s</td>%s%s</tr>' % (r["n"], r["n"], esc(r["feature"]), cells, pick))
        rows.append(why_row(r, 6))
    return '<table class="split">' + head + "".join(rows) + "</table>"


def own_table(doc):
    head = "<tr><th>Item</th><th>Where it comes from</th><th>What it holds (the best version)</th><th>Pick: who</th></tr>"
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


def build_page(doc):
    u = doc["universal"]
    o = doc["outcome"]
    intro = ('<section><h1>The admin split: Spinach\'s sheet with a pick per row, and our own items</h1>'
             '<p class="lead">%s</p><p class="meta">Cause: %s</p></section>' % (esc(doc["about"]), esc(doc["cause"])))
    rules = '<section><h2>The rules the picks rest on</h2>' + ul(doc["rules"], "rules") + '</section>'
    universal = ('<section><h2>Is the sheet the universal set?</h2><p>%s</p><p><b>Outside the sheet</b></p>%s'
                 '<p><b>The CRM set, later</b> %s</p></section>' % (esc(u["answer"]), ul(u["outside"]), esc(u["crm_later"])))
    levels = '<div class="levels">' + "".join('<span><b>%s</b> %s</span>' % (esc(a), esc(b)) for a, b in doc["levels"]) + '</div>'
    features = ('<section id="sheet"><h2>1. Spinach\'s sheet, with the pick</h2>'
                '<p class="meta">The four version columns are the sheet\'s own words (9 Jul 2026); the last column and the row '
                'under each feature are new.</p>' + levels + features_table(doc) + '</section>')
    own = ('<section id="own"><h2>2. Our own items, outside the sheet</h2><p class="meta">%s</p>%s</section>'
           % (esc(doc["own_note"]), own_table(doc)))
    sk = ('<section id="sketches"><h2>3. The sketches against Zoho</h2><p class="meta">%s</p>%s</section>'
          % (esc(doc["sketches_note"]), sketches_table(doc)))
    outcome = ('<section id="outcome" class="outcome"><h2>4. Outcome, if the picks are confirmed</h2>'
               '<h3>Spinach builds</h3>%s<h3>Zoho holds</h3>%s<h3>The consoles</h3><p>%s</p>'
               '<h3>What changes against the board</h3><p>%s</p><h3>To be decided</h3>%s<h3>To be verified in the trial</h3>%s</section>'
               % (ul(o["spinach"]), ul(o["zoho"]), esc(o["consoles"]), esc(o["changes"]), ul(o["decide"], "tbd"), ul(o["verify"])))
    body = intro + rules + universal + features + own + sk + outcome
    return (site.head("yeslyf admin split", site.CSS + site.SUBNAV_CSS + EXTRA_CSS) + '<body>\n' +
            site.header("admin_wireframes.html", "admin split: the sheet, our items, the sketches", who_html="", show_export=False,
                        tabs=None, setup_link=True) +
            site.seed_subnav(PAGE) +
            '<main class="main" style="max-width:none">' + body + '</main>\n' +
            site.store_script() + '<script>' + site.js_pill("admin_split") + '</script>\n</body>\n</html>\n')


def validate(doc):
    problems = []
    for key in ("about", "cause", "rules", "levels", "universal", "features", "own_note", "own", "sketches_note", "sketches", "outcome"):
        if key not in doc:
            problems.append("missing %s" % key)
    ns = [r["n"] for r in doc.get("features", [])]
    if ns != list(range(1, 13)):
        problems.append("features are not numbered 1 to 12: %s" % ns)
    for r in doc.get("features", []):
        for key in ("feature", "v1", "v1_5", "v2", "v3", "pick_level", "pick_who", "why", "zoho", "spinach", "verify", "decide", "sketches"):
            if key not in r:
                problems.append("feature %s: missing %s" % (r.get("n"), key))
    for r in doc.get("own", []):
        for key in ("feature", "source", "scope", "pick", "why", "zoho", "spinach", "verify", "decide", "sketches"):
            if key not in r:
                problems.append("own %s: missing %s" % (r.get("n"), key))
    if len(doc.get("sketches", [])) != 13:
        problems.append("sketches: %d rows, expected 13" % len(doc.get("sketches", [])))
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
    print("wrote docs/%s (%d bytes; %d sheet rows, %d own rows, %d sketches)" %
          (PAGE, len(page), len(doc["features"]), len(doc["own"]), len(doc["sketches"])))


if __name__ == "__main__":
    main()
