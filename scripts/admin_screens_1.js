// yeslyf admin wireframes: M02 to M04 draw functions (phase C part 2, 23 Sep 2026, PLAN_admin_seed_v01.md
// section 14). Registers ADMIN.draw.M02, ADMIN.draw.M03, ADMIN.draw.M04 on top of the API in
// scripts/admin_core.js (window.ADMIN, ADMIN.h); never duplicates that API, only adds to the draw registry.
// Plain browser JavaScript: an IIFE, var and function only, no arrow functions, no modules, no libraries.
// Low-fi grey wireframe: only the w-* classes already in scripts/renderer_v02.css and the admin CSS already in
// docs/admin_wireframes.html; no new colour, no inline style, no new visual design.
//
// Every table cell that is plain text is escaped with H.esc; H.table/H.rows cells are otherwise HTML built from
// H.num/H.date/H.when/H.link/H.badge/H.mock, which already escape what they print. No vendor name is written
// here: integration rows are always rendered through ADMIN.integ(id).
(function(){
  var H = ADMIN.h;

  // ---------------------------------------------------------------- shared helpers (this file only)

  // The M02 filter contract's tier keys are lead, free, diy, diwm, difm (a lead never carries people.tier).
  function tierBucket(p){
    return p.kind === "lead" ? "lead" : (p.tier || "free");
  }
  // A small bold section label inside a screen (reuses .spec-t, already defined for the side panel's own
  // section titles).
  function subHead(text){
    return '<div class="spec-t">' + H.esc(text) + '</div>';
  }
  // A row of mock write-action buttons, built from data/admin_screens.json's own s.writes (never hardcoded
  // action names), wrapped in .w-chips purely for its flex-wrap-gap layout (no colour or new class involved).
  function mockBar(writes){
    if(!writes || !writes.length) return "";
    var html = writes.map(function(w){ return H.mock(w.action, w.event); }).join(" ");
    return '<div class="w-chips">' + html + '</div>';
  }
  // A <label>Text <select>...</select></label>, first option "all <label>" with an empty value. labelFn, when
  // given, renders each option's visible text (e.g. ADMIN.staffName for a staff id); selected, when it matches
  // an option's raw value, marks that option (used to preset a select from ADMIN.nav.filter).
  function filterSelect(id, label, options, labelFn, selected){
    var html = '<label>' + H.esc(label) + ' <select id="' + id + '"><option value=""' + (selected ? "" : " selected") + '>all ' + H.esc(label) + '</option>';
    options.forEach(function(v){
      var text = labelFn ? labelFn(v) : v;
      html += '<option value="' + H.esc(v) + '"' + (selected === v ? " selected" : "") + '>' + H.esc(text) + '</option>';
    });
    html += '</select></label>';
    return html;
  }
  // A <details class="spec-block"> section titled with its row count, matching the side spec panel's own
  // grammar (renderer_v02.js's block()); used here for the M03 person record's sub-sections.
  function detailsBlock(title, count, inner, open){
    return '<details class="spec-block"' + (open ? " open" : "") + '><summary class="spec-t">' + H.esc(title) +
      ' <span class="cnt">(' + count + ')</span></summary>' + inner + '</details>';
  }
  function yn(v){ return (v === null || v === undefined) ? "-" : (v ? "yes" : "no"); }
  function numOrDash(v){ return (typeof v === "number") ? H.num(v) : "-"; }
  function rsOrDash(v){ return (typeof v === "number") ? ("Rs " + H.num(v)) : "-"; }
  function textOrDash(v){ return (v === null || v === undefined || v === "") ? "-" : H.esc(String(v)); }
  function joinOrDash(list){ return (list && list.length) ? H.esc(list.join(", ")) : "-"; }

  // The five flag badges every list or record screen shows (M02's columns, M03's identity strip). A person with
  // none shows a plain dash.
  function flagBadges(p){
    var out = "";
    if(p.s16_flag) out += H.badge("S16") + " ";
    if(p.difm_prospect_flag) out += H.badge("DIFM prospect") + " ";
    if(p.is_topup) out += H.badge("seed topup") + " ";
    if(p.plausibility_flag) out += H.badge("plausibility", "warn") + " ";
    if(p.engine_failure) out += H.badge("engine failure", "bad") + " ";
    return out || "-";
  }

  // A compact "key: value, key2: value2" rendering of a flat props/detail object (event props, audit detail).
  // A nested array or object is stringified with JSON.stringify rather than left to implicit toString, so it
  // never prints "[object Object]".
  function kv(obj){
    var out = [];
    for(var k in obj){
      if(!Object.prototype.hasOwnProperty.call(obj, k)) continue;
      var v = obj[k], vs;
      if(v === null || v === undefined) vs = "";
      else if(typeof v === "object") vs = JSON.stringify(v);
      else vs = String(v);
      out.push(k + ": " + vs);
    }
    return out.join(", ");
  }
  // True when a households/covers/rpq-shaped object carries at least one captured value (these chunk tables
  // default to {} only when the person never reached that screen; once a record exists its fields start out
  // null and fill in over time, so "has a record" means "has any non-null field", not "the dict is non-empty").
  function hasAny(obj){
    if(!obj) return false;
    for(var k in obj){
      if(Object.prototype.hasOwnProperty.call(obj, k) && obj[k] !== null && obj[k] !== undefined) return true;
    }
    return false;
  }

  // Money-denominated financial_records fields, transcribed from seed/config.json fields.list (kind "amount"),
  // minus ulip_years_completed (kind "amount" but a year count, ladder "ulip_years", not currency). This is a
  // closed, machine-defined enumeration read once from the seed generator's own field catalogue, not a guess.
  var MONEY_FIELDS = {
    bank_and_deposits: 1, bucket_fixed: 1, bucket_guilt_free: 1, bucket_variable: 1, credit_card_balance: 1,
    current_sip: 1, epf: 1, gold: 1, health_premium: 1, health_sum_insured: 1, home_value: 1, informal_loans: 1,
    investment_property_rent: 1, investment_property_value: 1, mutual_funds: 1, nps: 1, other_assets: 1,
    other_income: 1, other_policies: 1, partner_take_home: 1, ppf: 1, rental_income: 1, stocks: 1, take_home: 1,
    term_premium: 1, term_sum_assured: 1, total_emi: 1, total_outgoings: 1, ulip_premium: 1, ulip_surrender_value: 1
  };
  // The value cell of one financial_records row: not sure and none read as themselves; a band shows its band_id
  // (bands are placeholder ladders, so the id is the honest value, not a fabricated exact rupee number); an
  // exact value renders through its type, with the Rs prefix only for the fields that are genuinely money.
  function financialValueCell(r){
    if(r.value_kind === "not_sure") return "not sure";
    if(r.value_kind === "none") return "none";
    if(r.value_kind === "band") return textOrDash(r.band_id);
    var v = r.value;
    if(typeof v === "boolean") return yn(v);
    if(typeof v === "number") return MONEY_FIELDS[r.field] ? ("Rs " + H.num(v)) : H.num(v);
    return textOrDash(v);
  }

  var TIER_VALUES = ["lead", "free", "diy", "diwm", "difm"];
  var PATH_VALUES = ["aa", "cas", "manual"];
  var KIND_VALUES = ["lead", "user"];
  var FLAG_ORDER = ["s16", "plausibility", "engine_failure", "difm_prospect", "difm_rule", "difm_manual", "topup"];
  var FLAG_LABELS = {
    s16: "S16", plausibility: "plausibility flag", engine_failure: "engine failure",
    difm_prospect: "DIFM prospect (any)", difm_rule: "DIFM prospect (rule)", difm_manual: "DIFM prospect (manual)",
    topup: "seed topup"
  };
  function flagMatches(p, flag){
    if(flag === "s16") return !!p.s16_flag;
    if(flag === "plausibility") return !!p.plausibility_flag;
    if(flag === "engine_failure") return !!p.engine_failure;
    if(flag === "topup") return !!p.is_topup;
    if(flag === "difm_prospect") return !!p.difm_prospect_flag;
    if(flag === "difm_rule") return p.difm_prospect_flag === "rule";
    if(flag === "difm_manual") return p.difm_prospect_flag === "manual";
    return true;
  }

  // ================================================================== M02: People, search and list
  ADMIN.draw.M02 = function(body, s){
    // ADMIN.nav.filter (a query string set by another screen's H.link(count, "M02", {filter: "..."})) presets
    // the controls once, then is cleared so a later plain visit to M02 starts clean.
    var initialFilter = (ADMIN.nav && ADMIN.nav.filter) || "";
    ADMIN.nav = {};
    var initParams = new URLSearchParams(initialFilter);
    var filt = {
      q: initParams.get("q") || "",
      state: initParams.get("state") || "",
      tier: initParams.get("tier") || "",
      path: initParams.get("path") || "",
      adviser: initParams.get("adviser") || "",
      flag: initParams.get("flag") || "",
      kind: initParams.get("kind") || ""
    };
    var page = 1;
    var perPage = 50;
    var people = ADMIN.people || [];

    var statesPresent = {}, advisersPresent = {};
    people.forEach(function(p){
      if(p.state_id) statesPresent[p.state_id] = true;
      if(p.adviser_id) advisersPresent[p.adviser_id] = true;
    });
    var stateIds = (ADMIN.states || []).map(function(st){ return st.id; }).filter(function(id){ return statesPresent[id]; });
    var staffList = (ADMIN.t && ADMIN.t.staff) || [];
    var adviserIds = staffList.map(function(st){ return st.staff_id; }).filter(function(id){ return advisersPresent[id]; });

    function stateLabel(id){ var st = ADMIN.statesById[id]; return id + (st ? " " + st.who : ""); }
    function flagLabel(v){ return FLAG_LABELS[v] || v; }

    body.innerHTML =
      '<div class="w-h">' + H.esc(s.title) + '</div>' +
      '<div><label>Search <input type="text" id="m02-q" placeholder="ID, first or last name, phone last 3, email" value="' + H.esc(filt.q) + '"></label></div>' +
      '<div>' +
        filterSelect("m02-state", "state", stateIds, stateLabel, filt.state) + ' ' +
        filterSelect("m02-tier", "tier", TIER_VALUES, null, filt.tier) + ' ' +
        filterSelect("m02-path", "path", PATH_VALUES, null, filt.path) + ' ' +
        filterSelect("m02-adviser", "adviser", adviserIds, ADMIN.staffName, filt.adviser) + ' ' +
        filterSelect("m02-flag", "flag", FLAG_ORDER, flagLabel, filt.flag) + ' ' +
        filterSelect("m02-kind", "kind", KIND_VALUES, null, filt.kind) +
      '</div>' +
      mockBar(s.writes) +
      '<div class="w-note" id="m02-count"></div>' +
      '<div class="m02-results"></div>';

    var qEl = body.querySelector("#m02-q");
    if(qEl) qEl.addEventListener("input", function(){ filt.q = qEl.value || ""; page = 1; render(); });
    [["#m02-state", "state"], ["#m02-tier", "tier"], ["#m02-path", "path"], ["#m02-adviser", "adviser"],
     ["#m02-flag", "flag"], ["#m02-kind", "kind"]].forEach(function(pair){
      var el = body.querySelector(pair[0]);
      if(el) el.addEventListener("change", function(){ filt[pair[1]] = el.value || ""; page = 1; render(); });
    });

    function matches(p){
      if(filt.state && p.state_id !== filt.state) return false;
      if(filt.tier && tierBucket(p) !== filt.tier) return false;
      if(filt.path && p.source_path !== filt.path) return false;
      if(filt.adviser && p.adviser_id !== filt.adviser) return false;
      if(filt.kind && p.kind !== filt.kind) return false;
      if(filt.flag && !flagMatches(p, filt.flag)) return false;
      var q = filt.q.trim().toLowerCase();
      if(q){
        var hay = [p.person_id, p.first_name, p.last_name, p.phone, p.email]
          .filter(function(x){ return x; }).join(" ").toLowerCase();
        if(hay.indexOf(q) < 0) return false;
      }
      return true;
    }

    function render(){
      var filtered = people.filter(matches);
      var countEl = body.querySelector("#m02-count");
      if(countEl) countEl.textContent = H.num(filtered.length) + " people match, of " + H.num(people.length) + " (run " + ADMIN.run + ")";

      var pages = Math.max(1, Math.ceil(filtered.length / perPage));
      if(page > pages) page = pages;
      if(page < 1) page = 1;
      var pageRows = filtered.slice((page - 1) * perPage, (page - 1) * perPage + perPage);

      var resultsEl = body.querySelector(".m02-results");
      if(!resultsEl) return;
      if(!filtered.length){ resultsEl.innerHTML = '<div class="w-note">No people match these filters.</div>'; return; }

      var rows = pageRows.map(function(p){
        var name = (p.first_name || "") + (p.last_name ? " " + p.last_name : "");
        return [
          H.link(name || p.person_id, "M03", {person: p.person_id}),
          H.esc(p.person_id),
          H.esc(p.state_id || "-"),
          H.esc(tierBucket(p)),
          H.esc(p.source_path || "-"),
          H.esc(p.adviser_id ? ADMIN.staffName(p.adviser_id) : "-"),
          H.esc(p.city || "-"),
          H.date(p.key_dates && p.key_dates.last_activity),
          flagBadges(p)
        ];
      });
      var html = H.table(["Person", "ID", "State", "Tier", "Path", "Adviser", "City", "Last activity", "Flags"], rows);
      html += '<div class="m02-pager">' +
        '<button type="button" class="m02-prev"' + (page <= 1 ? " disabled" : "") + '>Previous</button> ' +
        '<span>page ' + page + ' of ' + pages + '</span> ' +
        '<button type="button" class="m02-next"' + (page >= pages ? " disabled" : "") + '>Next</button></div>';
      resultsEl.innerHTML = html;

      var prevBtn = resultsEl.querySelector(".m02-prev");
      if(prevBtn) prevBtn.addEventListener("click", function(){ if(page > 1){ page--; render(); } });
      var nextBtn = resultsEl.querySelector(".m02-next");
      if(nextBtn) nextBtn.addEventListener("click", function(){ if(page < pages){ page++; render(); } });
    }
    render();
  };

  // ================================================================== M03: Person record
  var KEY_DATE_FIELDS = [
    ["Signed up", "signed_up"], ["Reveal seen", "reveal_seen"], ["Paid", "paid"], ["Data complete", "data_complete"],
    ["Plan built", "plan_built"], ["Plan read", "plan_read"], ["Last call", "last_call"], ["Next review", "next_review"],
    ["Renewal due", "renewal_due"], ["Last activity", "last_activity"]
  ];
  var MIRROR_FIELDS = [
    ["Onboarding %", "onboarding_pct"], ["KYC status", "kyc_status"], ["AA status", "aa_status"],
    ["FP status", "fp_status"], ["IP status", "ip_status"], ["Actions done", "actions_done"], ["Actions total", "actions_total"]
  ];

  function identityRows(p){
    var stEntry = ADMIN.statesById[p.state_id];
    var stateText = (stEntry ? (p.state_id + " " + stEntry.who) : (p.state_id || "-")) + " (entered " + (H.date(p.state_entered_at) || "-") + ")";
    return [
      ["Name", textOrDash((p.first_name || "") + (p.last_name ? " " + p.last_name : ""))],
      ["ID", H.esc(p.person_id)],
      ["Phone", textOrDash(p.phone)],
      ["Email", p.email ? H.esc(p.email) : "no email yet"],
      ["City", H.esc((p.city || "-") + " (tier " + (p.city_tier || "-") + ")")],
      ["Age band", textOrDash(p.age_band)],
      ["Source", textOrDash(p.source)],
      ["Kind", textOrDash(p.kind)],
      ["Tier", H.esc(tierBucket(p))],
      ["SKU", p.sku ? H.esc(p.sku) : "none"],
      ["Period", p.period ? H.esc(p.period) : "none"],
      ["State", H.esc(stateText)],
      ["Adviser", p.adviser_id ? H.esc(ADMIN.staffName(p.adviser_id)) : "not assigned"],
      ["Subscription status", p.subscription_status ? H.esc(p.subscription_status) : "no subscription"],
      ["Flags", flagBadges(p)],
      ["WhatsApp opt-in", yn(p.whatsapp_optin)],
      ["DND", yn(p.dnd)],
      ["PAN", "kept off the board"]
    ];
  }

  function renderLead(body, s, p){
    var ld = p.lead_details || {};
    var rows = identityRows(p).concat([
      ["Top concern", textOrDash(ld.top_concern)],
      ["Keyword", textOrDash(ld.keyword)],
      ["Community joined", yn(ld.community_joined)],
      ["Resource sent", textOrDash(ld.resource_sent)],
      ["Landing at", H.when(ld.landing_at) || "-"]
    ]);
    body.innerHTML =
      '<div class="w-h">' + H.esc(s.title) + '</div>' +
      H.rows(rows) +
      '<div class="w-note">No app record: this person never verified the OTP.</div>';
  }

  // ---------- M03 per-table sections (each returns {count, html}; a 0 count is folded into "No rows: ...") ----------
  function financialSection(detail){
    var rows = (detail.financial_records || []).slice().sort(function(a, b){
      return a.captured_at < b.captured_at ? -1 : (a.captured_at > b.captured_at ? 1 : 0);
    });
    var out = rows.map(function(r){
      return [
        H.esc(r.field), financialValueCell(r), H.esc(r.value_kind), H.badge(r.source),
        H.badge(r.precision, r.precision === "unknown" ? "warn" : ""), yn(r.locked), H.date(r.captured_at), textOrDash(r.screen_id)
      ];
    });
    return { count: rows.length, html: rows.length ? H.table(["Field", "Value", "Value kind", "Source", "Precision", "Locked", "Captured", "Screen"], out) : "" };
  }
  function householdSection(detail){
    var h = detail.households || {};
    if(!hasAny(h)) return { count: 0, html: "" };
    var rows = [
      ["Household ID", textOrDash(h.household_id)],
      ["Household type", textOrDash(h.household_type)],
      ["Has dependants", yn(h.has_dependants)],
      ["Partner earns", yn(h.partner_earns)],
      ["Pets", yn(h.pets)]
    ];
    var membersHtml = "";
    if(h.members && h.members.length){
      var mrows = h.members.map(function(m){ return [textOrDash(m.relation), textOrDash(m.name), numOrDash(m.age), yn(m.earns), yn(m.lives_with_you)]; });
      membersHtml = H.table(["Relation", "Name", "Age", "Earns", "Lives with you"], mrows);
    }
    return { count: 1, html: H.rows(rows) + membersHtml };
  }
  function loansSection(detail){
    var rows = detail.loans || [];
    if(!rows.length) return { count: 0, html: "" };
    var out = rows.map(function(l){
      return [textOrDash(l.type), textOrDash(l.lender), rsOrDash(l.emi), rsOrDash(l.outstanding), numOrDash(l.years_left),
        (typeof l.rate === "number") ? (l.rate + "%") : "-", yn(l.tax_deductible)];
    });
    return { count: rows.length, html: H.table(["Type", "Lender", "EMI", "Outstanding", "Years left", "Rate", "Tax deductible"], out) };
  }
  function coversSection(detail){
    var c = detail.covers || {};
    if(!hasAny(c)) return { count: 0, html: "" };
    var rows = [
      ["Term status", textOrDash(c.term_status)],
      ["Term sum assured", rsOrDash(c.term_sum_assured)],
      ["Term premium", rsOrDash(c.term_premium)],
      ["Term cover until age", numOrDash(c.term_cover_until_age)],
      ["Health type", textOrDash(c.health_type)],
      ["Health sum insured", rsOrDash(c.health_sum_insured)],
      ["Health floater", yn(c.health_floater)],
      ["Health premium", rsOrDash(c.health_premium)],
      ["Other policies", c.other_policies ? H.esc(c.other_policies) : "none"]
    ];
    return { count: 1, html: H.rows(rows) };
  }
  function goalsSection(detail){
    var rows = detail.goals || [];
    if(!rows.length) return { count: 0, html: "" };
    var out = rows.map(function(g){
      var cost;
      if(g.cost_kind === "not_sure") cost = "not sure";
      else if(g.cost_kind === "band") cost = textOrDash(g.band_id);
      else cost = rsOrDash(g.cost_today);
      return [textOrDash(g.name), numOrDash(g.year), cost, textOrDash(g.priority), textOrDash(g.timeline), yn(g.yes_list)];
    });
    return { count: rows.length, html: H.table(["Goal", "Year", "Cost", "Priority", "Timeline", "Yes list"], out) };
  }
  function rpqSection(detail){
    var r = detail.rpq || {};
    if(!hasAny(r)) return { count: 0, html: "" };
    var rows = [
      ["Questionnaire version", textOrDash(r.questionnaire_version)],
      ["Score", numOrDash(r.score)],
      ["Risk band", textOrDash(r.risk_band)],
      ["Taken", H.date(r.taken_at) || "-"],
      ["Answers", joinOrDash(r.answers)]
    ];
    return { count: 1, html: H.rows(rows) };
  }
  function planVersionsSection(t, pid){
    var rows = (t.plan_versions && t.plan_versions[pid]) || [];
    if(!rows.length) return { count: 0, html: "" };
    var out = rows.map(function(v){
      var stub = v.summary_stub || {};
      var stubText = "emergency " + ((typeof stub.emergency_months === "number") ? (H.num(stub.emergency_months) + " months") : "-") +
        "; surplus " + rsOrDash(stub.monthly_surplus) + "; SIP " + rsOrDash(stub.sip_total) + "; cover gap " + rsOrDash(stub.cover_gap) +
        " (" + H.esc(v.summary_label || "stub, not the engine") + ")";
      return [
        textOrDash(v.plan_version), textOrDash(v.assumptions_version), textOrDash(v.instrument_set_version), textOrDash(v.built_on),
        H.date(v.built_at) || "-", H.date(v.read_at) || "-", H.date(v.pdf_downloaded_at) || "-", textOrDash(v.reason),
        H.date(v.accepted_at) || "-", stubText
      ];
    });
    return { count: rows.length, html: H.table(["Version", "Assumptions", "Instrument set", "Built on", "Built", "Read", "PDF", "Reason", "Accepted", "Summary stub"], out) };
  }
  function aaConsentsSection(t, pid){
    var rows = (t.aa_consents && t.aa_consents[pid]) || [];
    if(!rows.length) return { count: 0, html: "" };
    var out = rows.map(function(c){
      return [textOrDash(c.status), H.date(c.connected_at) || "-", H.date(c.consent_expiry) || "-", H.date(c.renewed_at) || "-",
        joinOrDash(c.institutions_ok), joinOrDash(c.institutions_failed)];
    });
    return { count: rows.length, html: H.table(["Status", "Connected", "Expiry", "Renewed", "Institutions ok", "Institutions failed"], out) };
  }
  function casUploadsSection(t, pid){
    // cas_source (e.g. "cams_kfintech") has no I-number in data/integrations.json, so it is left off this table
    // rather than writing a vendor name directly (CLAUDE.md: cite I-numbers, never a vendor name).
    var rows = (t.cas_uploads && t.cas_uploads[pid]) || [];
    if(!rows.length) return { count: 0, html: "" };
    var out = rows.map(function(c){
      return [H.date(c.requested_at) || "-", H.date(c.uploaded_at) || "-", H.date(c.parsed_at) || "-", numOrDash(c.reminder_count), H.date(c.abandoned_at) || "-"];
    });
    return { count: rows.length, html: H.table(["Requested", "Uploaded", "Parsed", "Reminders", "Abandoned"], out) };
  }
  function holdingsSection(t, pid){
    var rows = (t.holdings && t.holdings[pid]) || [];
    if(!rows.length) return { count: 0, html: "" };
    var out = rows.map(function(h){
      return [textOrDash(h.isin), textOrDash(h.name), (typeof h.units === "number") ? H.esc(String(h.units)) : "-",
        rsOrDash(h.value), textOrDash(h.source), h.unknown_isin ? H.badge("unknown ISIN", "warn") : ""];
    });
    return { count: rows.length, html: H.table(["ISIN", "Name", "Units", "Value", "Source", "Flag"], out) };
  }
  function callsSection(t, pid){
    var rows = (t.calls && t.calls[pid]) || [];
    if(!rows.length) return { count: 0, html: "" };
    var sorted = rows.slice().sort(function(a, b){ return (a.slot || "") < (b.slot || "") ? 1 : -1; });
    var out = sorted.map(function(c){
      return [c.adviser_id ? H.esc(ADMIN.staffName(c.adviser_id)) : "-", H.when(c.slot) || "-", textOrDash(c.topic),
        textOrDash(c.status), textOrDash(c.notes || c.note), joinOrDash(c.input_changes)];
    });
    return { count: rows.length, html: H.table(["Adviser", "Slot", "Topic", "Status", "Notes", "Input changes"], out) };
  }
  function ticketsSection(t, pid){
    var rows = (t.tickets && t.tickets[pid]) || [];
    if(!rows.length) return { count: 0, html: "" };
    var out = rows.map(function(tk){
      return [textOrDash(tk.subject), textOrDash(tk.category), textOrDash(tk.status), H.date(tk.created_at) || "-",
        H.date(tk.sla_due) || "-", H.date(tk.resolved_at) || "-", tk.scores_ref ? H.esc(tk.scores_ref) : "none"];
    });
    return { count: rows.length, html: H.table(["Subject", "Category", "Status", "Created", "SLA due", "Resolved", "SCORES ref"], out) };
  }
  function tasksSection(t, pid){
    var rows = (t.tasks && t.tasks[pid]) || [];
    if(!rows.length) return { count: 0, html: "" };
    var out = rows.map(function(tk){
      return [textOrDash(tk.subject || tk.state_id), tk.assignee ? H.esc(ADMIN.staffName(tk.assignee)) : "-",
        H.date(tk.due) || "-", textOrDash(tk.status), textOrDash(tk.outcome)];
    });
    return { count: rows.length, html: H.table(["Task", "Assignee", "Due", "Status", "Outcome"], out) };
  }
  function actionsSection(t, pid){
    var rows = (t.actions && t.actions[pid]) || [];
    if(!rows.length) return { count: 0, html: "" };
    var out = rows.map(function(a){
      return [textOrDash(a.type), rsOrDash(a.amount), textOrDash(a.channel), H.date(a.due) || "-", H.date(a.done_at) || "-",
        textOrDash(a.status), textOrDash(a.verification)];
    });
    return { count: rows.length, html: H.table(["Type", "Amount", "Channel", "Due", "Done", "Status", "Verification"], out) };
  }
  function subsPaymentsSection(t, pid){
    var subs = (t.subscriptions && t.subscriptions[pid]) || [];
    var pays = (t.payments && t.payments[pid]) || [];
    if(!subs.length && !pays.length) return { count: 0, html: "" };
    var html = "";
    if(subs.length){
      var srows = subs.map(function(sub){
        return [textOrDash(sub.sku), textOrDash(sub.period), H.esc(sub.amount), textOrDash(sub.status),
          H.date(sub.start) || "-", H.date(sub.next_billing) || "-",
          H.esc(String(sub.calls_included_per_period)) + " included, " + H.num(sub.calls_used) + " used"];
      });
      html += subHead("Subscriptions") + H.table(["SKU", "Period", "Amount", "Status", "Start", "Next billing", "Calls"], srows);
    }
    if(pays.length){
      var prows = pays.map(function(p2){
        return [textOrDash(p2.invoice_no), H.esc(p2.amount), textOrDash(p2.status), H.date(p2.paid_at) || "-", textOrDash(p2.method)];
      });
      html += subHead("Payments") + H.table(["Invoice", "Amount", "Status", "Paid", "Method"], prows);
    }
    return { count: subs.length + pays.length, html: html };
  }
  function nudgesSection(detail){
    var rows = detail.nudges_sent || [];
    if(!rows.length) return { count: 0, html: "" };
    var out = rows.map(function(n){
      return [textOrDash(n.state_id), textOrDash(n.channel), textOrDash(n.slot), H.when(n.sent_at) || "-",
        yn(n.delivered), yn(n.opened), yn(n.clicked), textOrDash(n.cap_check)];
    });
    return { count: rows.length, html: H.table(["State", "Channel", "Slot", "Sent", "Delivered", "Opened", "Clicked", "Cap check"], out) };
  }
  function ieventsSection(pid){
    var rows = (ADMIN.ievents && ADMIN.ievents[pid]) || [];
    if(!rows.length) return { count: 0, html: "" };
    var sorted = rows.slice().sort(function(a, b){ return (a.at || "") < (b.at || "") ? 1 : -1; });
    var out = sorted.map(function(e){
      return [H.esc(ADMIN.integ(e.integration)), textOrDash(e.call), textOrDash(e.outcome),
        (typeof e.latency_ms === "number") ? (H.num(e.latency_ms) + " ms") : "-", H.when(e.at) || "-"];
    });
    return { count: rows.length, html: H.table(["Integration", "Call", "Outcome", "Latency", "When"], out) };
  }
  function stateFlagsSection(detail){
    var flags = detail.state_flags || {};
    var keys = Object.keys(flags).sort();
    if(!keys.length) return { count: 0, html: "" };
    var rows = keys.map(function(k){
      var v = flags[k], vs;
      if(v === null || v === undefined) vs = "-";
      else if(typeof v === "object") vs = JSON.stringify(v);
      else if(typeof v === "boolean") vs = yn(v);
      else vs = String(v);
      return [k, H.esc(vs)];
    });
    return { count: keys.length, html: H.rows(rows) };
  }
  function auditSection(t, pid){
    var rows = (t.audit || []).filter(function(a){ return a.person_id === pid; });
    if(!rows.length) return { count: 0, html: "" };
    var sorted = rows.slice().sort(function(a, b){ return (a.at || "") < (b.at || "") ? 1 : -1; });
    var out = sorted.map(function(a){
      return [H.when(a.at) || "-", textOrDash(a.record), textOrDash(a.action), textOrDash(a.who), H.esc(kv(a.detail || {}))];
    });
    return { count: rows.length, html: H.table(["When", "Record", "Action", "Who", "Detail"], out) };
  }

  function isViewEvent(name){ return typeof name === "string" && name.length > 5 && name.slice(-5) === "_view"; }

  function renderPerson(body, s, pid, p, detail){
    var t = ADMIN.t || {};
    var timelineShown = 50;
    var timelineShowViews = false;
    var events = (detail.events || []).slice().sort(function(a, b){ return a[0] < b[0] ? 1 : (a[0] > b[0] ? -1 : 0); });

    function renderTimeline(){
      var visible = timelineShowViews ? events : events.filter(function(e){ return !isViewEvent(e[1]); });
      var shown = visible.slice(0, timelineShown);
      var rows = shown.map(function(e){
        var at = e[0], name = e[1], screenId = e[2], props = e[3] || {};
        var screenCell = screenId ? ('<a href="wireframes_v02.html#' + H.esc(screenId) + '" target="_blank">' + H.esc(screenId) + '</a>') : "-";
        return [H.when(at) || "-", H.esc(name), screenCell, H.esc(kv(props))];
      });
      var html = shown.length ? H.table(["When", "Event", "Screen", "Props"], rows) : '<div class="w-note">No events to show.</div>';
      html += '<div class="m03-timeline-controls">' +
        '<button type="button" class="m03-tl-views">' + (timelineShowViews ? "Hide screen views" : "Show screen views") + '</button>' +
        (visible.length > timelineShown ? ' <button type="button" class="m03-tl-more">Show 50 more</button>' : '') +
        '</div>';
      var el = body.querySelector(".m03-timeline-body");
      if(!el) return;
      el.innerHTML = html;
      var vb = el.querySelector(".m03-tl-views");
      if(vb) vb.addEventListener("click", function(){ timelineShowViews = !timelineShowViews; timelineShown = 50; renderTimeline(); });
      var mb = el.querySelector(".m03-tl-more");
      if(mb) mb.addEventListener("click", function(){ timelineShown += 50; renderTimeline(); });
    }

    var kd = p.key_dates || {};
    var keyDateRows = KEY_DATE_FIELDS.map(function(f){ return [f[0], H.date(kd[f[1]]) || "-"]; });
    var mirrors = p.mirrors || {};
    var mirrorRows = MIRROR_FIELDS.map(function(f){
      var v = mirrors[f[1]];
      return [f[0], (v === null || v === undefined) ? "-" : (typeof v === "number" ? H.num(v) : H.esc(v))];
    });
    var progressRows = [
      ["Progress %", (typeof p.progress_pct === "number") ? (H.num(p.progress_pct) + "%") : "-"],
      ["Profile fulfilment %", (typeof p.profile_fulfilment_pct === "number") ? (H.num(p.profile_fulfilment_pct) + "%") : "-"]
    ];

    var otherSections = [
      ["Household", householdSection(detail)],
      ["Loans", loansSection(detail)],
      ["Covers", coversSection(detail)],
      ["Goals", goalsSection(detail)],
      ["Risk profile", rpqSection(detail)],
      ["Plan versions", planVersionsSection(t, pid)],
      ["AA consents", aaConsentsSection(t, pid)],
      ["CAS uploads", casUploadsSection(t, pid)],
      ["Holdings", holdingsSection(t, pid)],
      ["Calls", callsSection(t, pid)],
      ["Tickets", ticketsSection(t, pid)],
      ["Tasks", tasksSection(t, pid)],
      ["Actions", actionsSection(t, pid)],
      ["Subscriptions and payments", subsPaymentsSection(t, pid)],
      ["Nudges sent", nudgesSection(detail)],
      ["Integration events", ieventsSection(pid)],
      ["State flags", stateFlagsSection(detail)],
      ["Audit", auditSection(t, pid)]
    ];
    var emptyTitles = [];
    var sectionsHtml = "";
    otherSections.forEach(function(pair){
      var title = pair[0], res = pair[1];
      if(!res.count){ emptyTitles.push(title); return; }
      sectionsHtml += detailsBlock(title, res.count, res.html, false);
    });
    var emptyLine = emptyTitles.length ? '<div class="w-note">No rows: ' + H.esc(emptyTitles.join(", ")) + '</div>' : "";

    var fin = financialSection(detail);
    var financialBlock = detailsBlock("Financial record", fin.count, fin.html || '<div class="w-note">No financial records yet.</div>', true);
    var timelineBlock = detailsBlock("Timeline", events.length, '<div class="m03-timeline-body"></div>', true);

    body.innerHTML =
      '<div class="w-h">' + H.esc(s.title) + '</div>' +
      H.rows(identityRows(p)) +
      mockBar(s.writes) +
      subHead("Key dates") + H.rows(keyDateRows) +
      subHead("Mirrors") + H.rows(mirrorRows) +
      subHead("Progress") + H.rows(progressRows) +
      timelineBlock +
      financialBlock +
      sectionsHtml +
      emptyLine;

    renderTimeline();
  }

  ADMIN.draw.M03 = function(body, s){
    var pid = ADMIN.current;
    if(!pid){ body.innerHTML = '<div class="w-h">' + H.esc(s.title) + '</div><div class="w-note">No person selected.</div>'; return; }
    var p = ADMIN.byId[pid];
    if(!p){ body.innerHTML = '<div class="w-h">' + H.esc(s.title) + '</div><div class="w-note">Unknown person.</div>'; return; }
    if(p.kind === "lead"){ renderLead(body, s, p); return; }

    body.innerHTML = '<div class="w-h">' + H.esc(s.title) + '</div><div class="w-note">Loading this person...</div>';
    ADMIN.detail(pid).then(function(detail){
      if(!window.yeslyfWire || window.yeslyfWire.current() !== "M03") return;
      if(ADMIN.current !== pid) return;
      renderPerson(body, s, pid, p, detail);
    })["catch"](function(){
      if(!window.yeslyfWire || window.yeslyfWire.current() !== "M03") return;
      if(ADMIN.current !== pid) return;
      body.innerHTML = '<div class="w-h">' + H.esc(s.title) + '</div><div class="w-note">Could not load this person.</div>';
    });
  };

  // ================================================================== M04: Pre-call view
  function drawM04(body, s, pid, p, detail){
    var t = ADMIN.t || {};

    // Plan at a glance (G03 snapshot): the latest plan version by built_at, its summary stub, and actions done
    // of total from the mirrors.
    var pvs = (t.plan_versions && t.plan_versions[pid]) || [];
    var latestPv = null;
    pvs.forEach(function(v){ if(!latestPv || (v.built_at || "") > (latestPv.built_at || "")) latestPv = v; });
    var glanceHtml;
    if(latestPv){
      var stub = latestPv.summary_stub || {};
      var mirrors = p.mirrors || {};
      var doneTotal = (typeof mirrors.actions_done === "number" && typeof mirrors.actions_total === "number")
        ? (H.num(mirrors.actions_done) + " of " + H.num(mirrors.actions_total))
        : "no actions yet";
      glanceHtml = H.rows([
        ["Emergency fund", (typeof stub.emergency_months === "number") ? (H.num(stub.emergency_months) + " months") : "-"],
        ["Monthly surplus", rsOrDash(stub.monthly_surplus)],
        ["SIP total", rsOrDash(stub.sip_total)],
        ["Cover gap", rsOrDash(stub.cover_gap)],
        ["Label", H.esc(latestPv.summary_label || "stub, not the engine")],
        ["Plan version", textOrDash(latestPv.plan_version)],
        ["Read", H.date(latestPv.read_at) || "-"],
        ["Actions done", doneTotal]
      ]);
    } else {
      glanceHtml = '<div class="w-note">No plan built yet.</div>';
    }

    // What is missing: financial records not_sure or unknown, plus the missing_fields of the latest S19 task while
    // the person is still in S19 (the call centre's task closes as "called; still S19", the fields stay missing).
    var missingFin = (detail.financial_records || []).filter(function(r){ return r.value_kind === "not_sure" || r.precision === "unknown"; });
    var missingHtml = "";
    if(missingFin.length){
      var mfRows = missingFin.map(function(r){ return [H.esc(r.field), H.esc(r.value_kind), H.esc(r.precision)]; });
      missingHtml += H.table(["Field", "Value kind", "Precision"], mfRows);
    }
    var tasks = (t.tasks && t.tasks[pid]) || [];
    var lastS19 = null;
    if(p.state_id === "S19") tasks.forEach(function(tk){ if(tk.state_id === "S19" && (!lastS19 || tk.created_at > lastS19.created_at)) lastS19 = tk; });
    if(lastS19){
      var mf = (lastS19.fields && lastS19.fields.missing_fields) || [];
      missingHtml += subHead("S19 task (" + lastS19.status + "), missing fields") + '<div class="w-p">' + (mf.length ? H.esc(mf.join(", ")) : "none listed") + '</div>';
    }
    if(!missingHtml) missingHtml = '<div class="w-note">Nothing missing.</div>';

    // Last call (latest completed) and Booked (every booked call).
    var calls = (t.calls && t.calls[pid]) || [];
    var lastCompleted = null;
    calls.forEach(function(c){ if(c.status === "completed" && (!lastCompleted || (c.slot || "") > (lastCompleted.slot || ""))) lastCompleted = c; });
    var lastCallHtml = lastCompleted ? H.rows([
      ["Date", H.when(lastCompleted.slot) || "-"],
      ["Topic", textOrDash(lastCompleted.topic)],
      ["Notes", textOrDash(lastCompleted.notes)],
      ["Input changes", joinOrDash(lastCompleted.input_changes)]
    ]) : '<div class="w-note">No completed call yet.</div>';

    var booked = calls.filter(function(c){ return c.status === "booked"; }).slice().sort(function(a, b){ return (a.slot || "") < (b.slot || "") ? -1 : 1; });
    var bookedHtml = booked.length ? H.table(["Slot", "Topic", "Note"], booked.map(function(c){
      return [H.when(c.slot) || "-", textOrDash(c.topic), textOrDash(c.note)];
    })) : '<div class="w-note">No call booked.</div>';

    // Script for this state: what the state entry holds for a call. No state in data/v02/states.json carries a
    // script field, so the "to be decided" line always shows; this is reported as a gap.
    var stEntry = ADMIN.statesById[p.state_id];
    var scriptHtml;
    if(stEntry){
      var slots = [];
      if(stEntry.push && stEntry.push.slot) slots.push(stEntry.push.slot);
      if(stEntry.whatsapp && stEntry.whatsapp.slot) slots.push(stEntry.whatsapp.slot);
      if(stEntry.email && stEntry.email.slot) slots.push(stEntry.email.slot);
      var crmFields = (stEntry.crm_task && stEntry.crm_task.fields) || [];
      scriptHtml = H.rows([
        ["State", H.esc(stEntry.id + " " + stEntry.who)],
        ["Primary action", textOrDash(stEntry.primary_action)],
        ["Lands on", textOrDash(stEntry.lands_on)],
        ["Task fields", crmFields.length ? H.esc(crmFields.join(", ")) : "none"],
        ["Copy slot ids", slots.length ? H.esc(slots.join(", ")) : "none"]
      ]) + '<div class="w-note">to be decided: a call script per state</div>';
    } else {
      scriptHtml = '<div class="w-note">to be decided: a call script per state</div>';
    }

    // Calls left this period: from the active subscription.
    var subs = (t.subscriptions && t.subscriptions[pid]) || [];
    var activeSub = null;
    subs.forEach(function(sub){ if(sub.status === "active") activeSub = sub; });
    var callsLeftHtml = activeSub
      ? ('<div class="w-p">' + H.esc(String(activeSub.calls_included_per_period)) + ' included, ' + H.num(activeSub.calls_used) + ' used</div>')
      : '<div class="w-note">No active subscription.</div>';

    var writesHtml = subHead("Actions") +
      '<div><textarea id="m04-notes" rows="3" placeholder="K03 notes and input changes"></textarea></div>' +
      mockBar(s.writes);

    body.innerHTML =
      '<div class="w-h">' + H.esc(s.title) + '</div>' +
      subHead("Plan at a glance (G03 snapshot)") + glanceHtml +
      subHead("What is missing") + missingHtml +
      subHead("Last call") + lastCallHtml +
      subHead("Booked") + bookedHtml +
      subHead("Script for this state") + scriptHtml +
      subHead("Calls left this period") + callsLeftHtml +
      writesHtml;
  }

  ADMIN.draw.M04 = function(body, s){
    var pid = ADMIN.current;
    if(!pid){ body.innerHTML = '<div class="w-h">' + H.esc(s.title) + '</div><div class="w-note">No person selected.</div>'; return; }
    var p = ADMIN.byId[pid];
    if(!p){ body.innerHTML = '<div class="w-h">' + H.esc(s.title) + '</div><div class="w-note">Unknown person.</div>'; return; }

    body.innerHTML = '<div class="w-h">' + H.esc(s.title) + '</div><div class="w-note">Loading this person...</div>';
    ADMIN.detail(pid).then(function(detail){
      if(!window.yeslyfWire || window.yeslyfWire.current() !== "M04") return;
      if(ADMIN.current !== pid) return;
      drawM04(body, s, pid, p, detail);
    })["catch"](function(){
      if(!window.yeslyfWire || window.yeslyfWire.current() !== "M04") return;
      if(ADMIN.current !== pid) return;
      body.innerHTML = '<div class="w-h">' + H.esc(s.title) + '</div><div class="w-note">Could not load this person.</div>';
    });
  };
})();
