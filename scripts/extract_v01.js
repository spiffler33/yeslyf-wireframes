// Extract the embedded data of the four v0.1 HTML files by evaluating their script tags in a Node vm context.
// Writes data/screens_v01.json, data/admin_crm.json, data/review_rows_v01.json, data/decision_board_v01.json.
// The HTML files themselves are never modified; see CLAUDE.md.
"use strict";
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const ROOT = path.resolve(__dirname, "..");
const IN = path.join(ROOT, "inputs", "v01");
const OUT = path.join(ROOT, "data");

function scriptBodies(file) {
  const s = fs.readFileSync(file, "utf8");
  const out = [];
  let i = 0;
  for (;;) {
    const a = s.indexOf("<script", i);
    if (a < 0) break;
    const b = s.indexOf(">", a);
    const c = s.indexOf("</script>", b);
    out.push(s.slice(b + 1, c));
    i = c + 9;
  }
  return out;
}

function noop() {}
function fakeEl() {
  return {
    addEventListener: noop, querySelectorAll: () => [], querySelector: () => null, appendChild: noop,
    style: {}, classList: { add: noop, remove: noop, toggle: noop, contains: () => false },
    setAttribute: noop, getAttribute: () => null, focus: noop, value: "", innerHTML: "", textContent: "",
  };
}

function loadContext(file) {
  const ctx = {
    console: { log: noop, error: noop, warn: noop },
    localStorage: { getItem: () => null, setItem: noop, removeItem: noop },
    navigator: {}, location: { hash: "", href: "" },
    document: { getElementById: fakeEl, querySelector: () => null, querySelectorAll: () => [], addEventListener: noop, body: fakeEl(), createElement: fakeEl },
    setTimeout: noop, clearTimeout: noop, Blob: function () {}, URL: { createObjectURL: () => "" }, alert: noop,
  };
  ctx.window = ctx;
  vm.createContext(ctx);
  ctx.__errors = [];
  for (const body of scriptBodies(file)) {
    try { vm.runInContext(body, ctx, { filename: path.basename(file) }); }
    catch (e) { ctx.__errors.push(String(e).slice(0, 200)); }
  }
  return ctx;
}

function pick(ctx, names) {
  const o = {};
  for (const n of names) {
    if (ctx[n] === undefined) throw new Error("missing " + n);
    o[n] = ctx[n];
  }
  return o;
}

function write(name, obj) {
  const text = JSON.stringify(obj, null, 1) + "\n";
  for (let i = 0; i < text.length; i++) {
    if (text.charCodeAt(i) > 126) throw new Error(name + ": non-ASCII char at " + i + ": " + JSON.stringify(text.slice(i - 20, i + 20)));
  }
  fs.writeFileSync(path.join(OUT, name), text);
  console.log("wrote data/" + name + " (" + text.length + " bytes)");
}

fs.mkdirSync(OUT, { recursive: true });

const wire = loadContext(path.join(IN, "yeslyf_wireframes_v0.1.html"));
const w = pick(wire, ["SECTIONS", "SCREENS"]);
write("screens_v01.json", { source: "inputs/v01/yeslyf_wireframes_v0.1.html", sections: w.SECTIONS, screens: w.SCREENS });

const admin = loadContext(path.join(IN, "yeslyf_admin_crm_spec_v0.1.html"));
const a = pick(admin, ["STACK", "PLACEMENT", "CONTACT_FIELDS", "DEAL_FIELDS", "EVENTS", "INBOUND", "NUDGES", "NUDGE_EXAMPLES", "COMPLIANCE", "DECISIONS"]);
a.DECISIONS = a.DECISIONS.map(function (d) {
  return {
    id: d.id, q: d.q, position: d.rec, owner_v01: d.owner,
    stated_by: "Vatsal and Kajal (crm-and-nudges workstream), admin/CRM spec v0.1",
  };
});
write("admin_crm.json", Object.assign({ source: "inputs/v01/yeslyf_admin_crm_spec_v0.1.html",
  note: "DECISIONS were written in the admin/CRM spec v0.1 by the crm-and-nudges workstream (Vatsal and Kajal); 'position' is their stated position, not a recommendation to anyone else." }, a));

const log = loadContext(path.join(IN, "yeslyf_review_log_v0.1.html"));
const r = pick(log, ["ROWS"]);
write("review_rows_v01.json", { source: "inputs/v01/yeslyf_review_log_v0.1.html",
  note: "Raw rows 1 to 73 as exported. The disp/act columns carry the rejected v0.1 framing; use data/inputs.json for status.", rows: r.ROWS });

const board = loadContext(path.join(IN, "yeslyf_v0.2_decision_board.html"));
const b = pick(board, ["DECISIONS", "CONFIRM", "CHANGES", "ANSWERED", "GAPS", "HARISH_ROWS"]);
write("decision_board_v01.json", Object.assign({ source: "inputs/v01/yeslyf_v0.2_decision_board.html",
  note: "Data source only. The framing of this draft (rec, owner labels, dispositions) is rejected; attribution on the site comes from data/open_items.json and data/inputs.json." }, b));

for (const [n, c] of [["wireframes", wire], ["admin", admin], ["review log", log], ["board", board]]) {
  if (c.__errors.length) console.log("note: " + n + " script threw after data load: " + c.__errors.join(" | "));
}
console.log("screens: " + w.SCREENS.length + ", rows: " + r.ROWS.length);
