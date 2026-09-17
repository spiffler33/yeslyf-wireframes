#!/usr/bin/env python3
"""Three self-contained audience files from the same data (phase 9d, Vatsal, 11 Sep 2026), written by
scripts/build_site.py into docs/audiences/ (or run this file alone to rebuild just them):

  yeslyf_v02_team.html        the full Wireframes v0.2 tab (all filters, spec panel, markers, causes), the Admin and
                              CRM v0.2 tab with the CRM backlog, and the Changelog; reviewer identity from the seven.
  yeslyf_v02_spinach.html     the wireframes with the spec panel, the tier, path, state and template filters, the
                              changed and new markers, and the counts page; identity locked to Spinach; no Meeting,
                              Gaps, Inputs, Admin and CRM, causes, compliance checklists or CRM backlog.
  yeslyf_v02_compliance.html  only the screens flagged for review, in flow order, each with its reason category,
                              checklist card and user-facing copy; identity locked to Compliance; no dev notes.

Self-contained: the screen data is embedded, the file opens from disk with no network, the comment controls and the
markdown export work offline (comments live in the browser under a per-file key). No Supabase URL or key anywhere (the
files do not load docs/config.js, so the pill reads "offline, saved locally"). noindex on each. Nothing here is
hand-edited; data/*.json is the source.
"""
import copy
import os
import sys

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS)
import build_site as site  # noqa: E402

TEAM_IDENTITIES = ["Bhuvanaa", "Harish", "Gaurav", "Kajal", "Somil", "Spinach", "Compliance"]
BANNER = "All copy is placeholder pending compliance review; comment on language on any screen."
FILES = [("yeslyf_v02_team.html", "team"), ("yeslyf_v02_spinach.html", "Spinach"), ("yeslyf_v02_compliance.html", "compliance")]

VIEW_JS = r"""
(function(){
  var ids = {}; SCREENS.forEach(function(s){ ids[s.id] = 1; });
  var tabs = document.querySelectorAll(".views a[data-view]");
  function show(id){
    Array.prototype.forEach.call(document.querySelectorAll("[data-viewpane]"), function(p){ p.hidden = p.getAttribute("data-viewpane") !== id; });
    Array.prototype.forEach.call(tabs, function(a){ a.className = a.getAttribute("data-view") === id ? "on" : ""; });
    if(id !== "wire") document.body.classList.remove("map-on");
  }
  Array.prototype.forEach.call(tabs, function(a){ a.addEventListener("click", function(ev){ ev.preventDefault(); show(a.getAttribute("data-view")); }); });
  window.addEventListener("hashchange", function(){ var id = location.hash.replace("#", ""); if(ids[id]) show("wire"); });
  document.addEventListener("DOMContentLoaded", function(){ var id = location.hash.replace("#", ""); if(id && !ids[id] && document.getElementById(id)){ var pane = document.getElementById(id).closest("[data-viewpane]"); if(pane) show(pane.getAttribute("data-viewpane")); } });
})();
"""


def header(subtitle, views, export_label):
    tabs = "".join('<a data-view="%s"%s>%s</a>' % (vid, ' class="on"' if i == 0 else "", site.esc(label)) for i, (vid, label) in enumerate(views))
    return ('<header class="top"><div class="brand">yeslyf <span>' + site.esc(subtitle) + '</span></div>'
            '<nav class="tabs views">' + tabs + '</nav>'
            '<div class="who">Reviewing as <select id="reviewer"></select></div>'
            '<div id="saved" class="saved"></div><span id="sheetpill" class="pill" title="Sheet write-back status">sheet: off</span>'
            '<button id="export" class="primary">' + site.esc(export_label) + '</button></header>\n')


def bar(tiers=True, path=True, state=True, comp=True, tpl=True, banner=False, freeze=True):
    parts = ['<div class="bar">']
    if tiers:
        parts.append('<div id="tiers" class="tiers"></div>')
    if path:
        parts.append('<label>Path <select id="fpath"></select></label>')
    if state:
        parts.append('<label id="fstate-wrap">State <select id="fstate"></select></label>')
    if comp:
        parts.append('<label>Compliance <select id="fcomp"></select></label>')
    if tpl:
        parts.append('<label>Template <select id="ftpl"></select></label>')
    if freeze:
        parts.append('<label>Frozen <select id="ffreeze"></select></label>')
    parts.append('<div class="actions"><button id="mapbtn">Journey map</button></div></div>\n')
    if banner:
        parts.append('<div class="banner">%s</div>\n' % site.esc(BANNER))
    return "".join(parts)


def blob(sections, screens, dropped, split, states, reasons, opts, integ=None, freeze=None):
    return ('<script>var SECTIONS=' + site.js_blob(sections) + ';\nvar SCREENS=' + site.js_blob(screens) + ';\nvar DROPPED=' + site.js_blob(dropped) +
            ';\nvar SPLIT=' + site.js_blob(split) + ';\nvar STATES=' + site.js_blob(states) + ';\nvar REASONS=' + site.js_blob(reasons) +
            ';\nvar INTEGRATIONS=' + site.js_blob(integ or {"as_of": "", "rows": []}) + ';\nvar FREEZE=' + site.js_blob(freeze) +
            ';\nvar WIRE_OPTS=' + site.js_blob(opts) + ';</script>\n')


def prep(screens, mode):
    """The screen records each audience embeds: full for the team; no compliance flag and no causes for Spinach;
    no spec (so no dev notes), no events and no causes for compliance."""
    out = []
    for s in screens:
        s = copy.deepcopy(s)
        if mode == "spinach":
            s.pop("compliance", None)
            s["v02"] = {"status": s["v02"]["status"]}
        elif mode == "compliance":
            s["spec"] = {}
            s.pop("events", None)
            s["v02"] = {"status": s["v02"]["status"]}
        out.append(s)
    return out


def in_file_links(html):
    """Links the site pages point at wireframes_v02.html#ID become in-file links."""
    return html.replace('href="wireframes_v02.html#', 'href="#')


def doc_pane(vid, nav, body):
    return '<div data-viewpane="%s" class="doc" hidden><div class="docnav">%s</div>%s</div>\n' % (vid, nav, body)


def counts_doc(chg):
    c = chg["counts"]
    fz = chg.get("freeze") or {}
    by_sec_rows = []
    for sec, info in c["by_section"].items():
        by_sec_rows.append([site.esc(sec), site.esc(info["name"]), str(info["screens"]), str(info.get("frozen", "")), str(info.get("open", "")), str(info["templates"]), site.esc(", ".join("%s %d" % kv for kv in info["by_template"].items()))])
    open_tpl = c.get("open_by_template", {})
    tstatus = ("%s since %s" % (fz["templates"]["status"], fz["templates"]["since"])) if fz else ""
    open_rows = site.table_html(["Screen", "Title", "Open because"], [[site.sid_link(x["id"], {x["id"]}), site.esc(x["title"]), site.esc("; ".join(x["reason"]))] for x in fz.get("open_screens", [])]) if fz else ""
    return ('<section id="counts"><h1>Counts: templates and instances</h1><p class="lead">%d screens in v0.2 across %d unique templates; %d frozen, %d open. Every instance of a repeated layout is drawn and tagged; this page counts them. '
            'Frozen: template, fields and tags, branches, states and events do not change without an entry in the Unfreeze log; copy, prices, counts, bands, scoring maps and grid values are config and are not covered.</p>'
            '<h3>By section</h3>%s<h3>By template</h3>%s<h3>Open screens</h3>%s</section>' % (
                c["total"], c["unique_templates"], c.get("frozen", 0), c.get("open", 0),
                site.table_html(["Section", "Name", "Screens", "Frozen", "Open", "Templates", "Instances per template"], by_sec_rows),
                site.table_html(["Template", "Status", "Screens", "Frozen", "Open"], [[site.esc(k), site.esc(tstatus), str(v), str(v - open_tpl.get(k, 0)), str(open_tpl.get(k, 0))] for k, v in c["by_template"].items()]),
                open_rows))


def page(title, head_subtitle, views, export_label, bar_html, panes, data, opts_js=True):
    return (site.head(title, site.read_script("renderer_v02.css"), config=None) + '<body>\n' + header(head_subtitle, views, export_label) +
            '<div data-viewpane="wire">' + bar_html + site.WIRE_LAYOUT + '</div>\n' + panes + data +
            site.store_script() + '<script>' + site.read_script("renderer_v02.js") + '</script>\n<script>' + VIEW_JS + '</script>\n</body>\n</html>\n')


def build_all(v02, states, reasons, admin, changelog):
    """{file name: (html, audience)} for the three files."""
    live = site.live_screens(v02)
    dropped = [s["id"] for s in v02["screens"] if s["v02"]["status"] == "dropped"]
    split = [s["id"] for s in v02["screens"] if s["v02"]["status"] == "split"]
    state_list = states["states"] if states else []
    integ = site.integrations_blob()
    freeze = site.freeze_blob(changelog)
    out = {}

    # team: everything, identity from the seven
    a_nav, a_body = site.admin_parts(admin, v02, states)
    c_nav, c_body = site.changelog_parts(changelog, v02, None)
    opts = {"identities": TEAM_IDENTITIES, "key": "yeslyf_wire_v02_team", "spec": "full",
            "exportTitle": "# yeslyf wireframes v0.2 - review comments (team file)", "exportFile": "yeslyf_v02_team_comments.md"}
    panes = doc_pane("admin", in_file_links(a_nav), in_file_links(a_body)) + doc_pane("changelog", in_file_links(c_nav), in_file_links(c_body))
    out["yeslyf_v02_team.html"] = (page(
        "yeslyf wireframes v0.2, team file", "wireframes v0.2 for the team, %d screens" % len(live),
        [("wire", "Wireframes v0.2"), ("admin", "Admin and CRM v0.2"), ("changelog", "Changelog")], "Export comments",
        bar(banner=True), panes, blob(v02["sections"], prep(live, "team"), dropped, split, state_list, reasons, opts, integ, freeze)), "team")

    # Spinach: the wireframes and the counts; identity locked; no compliance, no causes
    opts = {"identities": ["Spinach"], "lock": "Spinach", "key": "yeslyf_wire_v02_spinach", "spec": "design", "compFilter": False,
            "exportTitle": "# yeslyf wireframes v0.2 - Spinach comments", "exportFile": "yeslyf_v02_spinach_comments.md"}
    panes = '<div data-viewpane="counts" class="doc" hidden>%s</div>\n' % counts_doc(changelog)
    out["yeslyf_v02_spinach.html"] = (page(
        "yeslyf wireframes v0.2, Spinach file", "wireframes v0.2 for Spinach, %d screens, %d templates" % (len(live), changelog["counts"]["unique_templates"]),
        [("wire", "Wireframes v0.2"), ("counts", "Counts")], "Export comments",
        bar(comp=False), panes, blob(v02["sections"], prep(live, "spinach"), dropped, split, state_list, {}, opts, integ, freeze)), "Spinach")

    # compliance: flagged screens only, in flow order; identity locked; the review reasons only
    flagged = [s for s in live if s["compliance"]["review"]]
    review_reasons = {k: v for k, v in reasons.items() if v["review"]}
    opts = {"identities": ["Compliance"], "lock": "Compliance", "key": "yeslyf_wire_v02_compliance", "spec": "compliance",
            "exportTitle": "# yeslyf wireframes v0.2 - compliance comments", "exportFile": "yeslyf_v02_compliance_comments.md"}
    out["yeslyf_v02_compliance.html"] = (page(
        "yeslyf wireframes v0.2, compliance file", "wireframes v0.2 for compliance review, %d screens flagged" % len(flagged),
        [("wire", "Screens for review")], "Export comments",
        bar(tiers=False, path=False, state=False, tpl=False, banner=True, freeze=False), "", blob(v02["sections"], prep(flagged, "compliance"), dropped, split, [], review_reasons, opts)), "compliance")
    return out


def main():
    v02 = site.load("screens_v02.json")
    changelog = site.load("changelog.json")
    reasons = site.load("compliance_reasons.json")["reasons"]
    admin = site.load("admin_crm.json")
    states = site.load_optional("v02", "states.json")
    out = build_all(v02, states, reasons, admin, changelog)
    os.makedirs(os.path.join(site.DOCS, "audiences"), exist_ok=True)
    for name, (text, who) in out.items():
        site.check_ascii(name, text)
        with open(os.path.join(site.DOCS, "audiences", name), "w") as fh:
            fh.write(text)
        print("wrote docs/audiences/%s (%d bytes, for %s)" % (name, len(text), who))


if __name__ == "__main__":
    main()
