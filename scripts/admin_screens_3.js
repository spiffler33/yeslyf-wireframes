// yeslyf admin wireframes: M10 to M14, over the API in scripts/admin_core.js (phase C part 2, 23 Sep 2026).
// Plain browser JavaScript in the renderer's idiom: an IIFE, var, function; no modules, no arrow functions,
// no libraries. Registers ADMIN.draw.M10 .. ADMIN.draw.M14. Never calls yeslyfBoard; every write is H.mock.
(function(){
  var ADMIN = window.ADMIN;
  var H = ADMIN.h;
  var ROLES = ["Principal officer", "Adviser", "Call centre", "Ops", "Marketing", "Compliance", "Support", "Finance"];

  // ---------------------------------------------------------------- shared helpers
  function esc(s){ return H.esc(s); }
  function numRs(n){ return (n === null || n === undefined) ? "" : "Rs " + H.num(n); }
  function wireAnchor(wire){
    if(!wire) return "";
    return '<a href="wireframes_v02.html#' + esc(wire) + '">' + esc(wire) + "</a>";
  }
  // Every table in ADMIN.t keyed by person_id -> array of rows, flattened to {pid, row} pairs. rpq, covers and
  // config are keyed by person_id -> one object each, not an array, and never go through this helper.
  function flatten(tableName){
    var t = (ADMIN.t && ADMIN.t[tableName]) || {};
    var out = [];
    for(var pid in t){
      if(!Object.prototype.hasOwnProperty.call(t, pid)) continue;
      var rows = t[pid] || [];
      for(var i = 0; i < rows.length; i++) out.push({pid: pid, row: rows[i]});
    }
    return out;
  }
  function isPaidTier(tier){ return !!tier && tier !== "free"; }
  function stateLabel(id){
    var st = ADMIN.statesById[id];
    return id + (st && st.who ? (": " + st.who) : "");
  }
  function personLabel(pid){
    var p = ADMIN.byId[pid];
    if(!p) return pid;
    return pid + " " + (p.first_name || "") + (p.last_name ? " " + p.last_name : "");
  }

  // ================================================================== M10: Config
  ADMIN.draw.M10 = function(body, s){
    var cfg = (ADMIN.t && ADMIN.t.config) || {};
    var skuCards = cfg.sku_cards || [];
    var copySlots = cfg.copy_slots || [];
    var flags = cfg.feature_flags || {};
    var calls = cfg.calls_included || {};
    var bands = cfg.bands || {};
    var difm = cfg.difm_threshold || {};
    var assumptions = cfg.assumptions_versions || [];

    var html = '<div class="w-h">Config</div>' +
      '<div class="w-note">The runtime configuration the app reads. Every edit below is mock.</div>';

    // SKU cards
    html += '<div class="spec-t">SKU cards</div>';
    skuCards.forEach(function(c){
      html += '<div class="w-card"><div class="w-card-t">' + esc(c.sku) + ": " + esc(c.name) + '</div><ul>' +
        '<li>Monthly: ' + esc(c.price_monthly) + '</li>' +
        '<li>Quarterly: ' + esc(c.price_quarterly) + '</li>' +
        '<li>Calls included: ' + esc(c.calls_included) + '</li>' +
        '</ul>' + H.mock("Edit " + c.sku + " card", "M10_edit") + '</div>';
    });

    // Copy slots: search over id and text
    html += '<div class="spec-t">Copy slots</div>' +
      '<div class="w-note">Every N-* (nudge) and W-* (in-app) slot with its current text.</div>' +
      '<input type="text" id="m10-cs-q" placeholder="search copy slots by id or text" autocomplete="off">' +
      H.mock("Edit copy slots", "M10_edit") +
      '<div id="m10-cs-results"></div>';

    // Feature flags
    html += '<div class="spec-t">Feature flags</div>' +
      H.rows(Object.keys(flags).sort().map(function(k){ return [k, esc(flags[k])]; })) +
      H.mock("Edit feature flags", "M10_edit");

    // calls_included matrix: tier by period
    var periods = ["monthly", "quarterly"];
    var tiers = Object.keys(calls).sort();
    html += '<div class="spec-t">Calls included matrix</div>' +
      H.table(["Tier"].concat(periods), tiers.map(function(t){
        return [esc(t)].concat(periods.map(function(p){ return esc((calls[t] || {})[p]); }));
      })) + H.mock("Edit calls-included matrix", "M10_edit");

    // Bands: placeholder ladders
    html += '<div class="spec-t">Bands ' + H.badge("placeholder") + '</div>' +
      '<div class="w-note">' + esc(bands.note || "") + '</div>';
    var ladders = bands.ladders_rs || {};
    html += H.table(["Field", "Boundaries (Rs)"], Object.keys(ladders).sort().map(function(f){
      return [esc(f), esc(ladders[f].map(function(n){ return H.num(n); }).join(" / "))];
    }));
    var reveal = bands.reveal || {};
    html += H.table(["Reveal field", "Labels"], Object.keys(reveal).sort().map(function(f){
      var labels = (reveal[f] && reveal[f].labels) || [];
      return [esc(f), esc(labels.join("; "))];
    })) + H.mock("Edit bands", "M10_edit");

    // DIFM threshold, as the board reads it
    html += '<div class="spec-t">DIFM threshold</div>' +
      H.rows([["Value, as the board reads it", esc(difm.board_reads || "")], ["Label", esc(difm.label || "")]]) +
      H.mock("Edit DIFM threshold", "M10_edit");

    // Agreement version and assumptions versions
    html += '<div class="spec-t">Agreement version</div>' + H.rows([["Current", esc(cfg.agreement_version || "")]]);
    html += '<div class="spec-t">Assumptions versions</div>' +
      H.table(["Assumptions", "Instrument set", "Published"], assumptions.map(function(a){
        return [esc(a.assumptions_version), esc(a.instrument_set_version), H.date(a.published_at)];
      }));

    // Where it lives
    var blocks = ["SKU cards", "copy slots N-* and W-* with current text", "feature flags",
      "calls_included matrix", "bands (placeholder)", "DIFM threshold"];
    html += '<div class="spec-t">Where it lives</div>' +
      '<div class="w-note">' + ADMIN.integ("I15") + ' is open; this table is that choice made visible.</div>' +
      H.table(["Config block", "Built (this screen)", ADMIN.integ("I14") + " (Creator)", ADMIN.integ("I15")],
        blocks.map(function(b){
          return [esc(b), "edit here (mock)", "to be verified: a Creator form the app reads",
            "to be verified: a collection the app reads"];
        }));

    body.innerHTML = html;

    function renderCopySlots(q){
      var box = body.querySelector("#m10-cs-results");
      if(!box) return;
      var list = copySlots;
      if(q){
        var qq = q.toLowerCase();
        list = copySlots.filter(function(c){
          var hay = (String(c.slot || "") + " " + String(c.text || "")).toLowerCase();
          return hay.indexOf(qq) >= 0;
        });
      }
      box.innerHTML = H.table(["Slot", "Channel", "State", "Text"], list.map(function(c){
        return [esc(c.slot), esc(c.channel), esc(c.state), esc(c.text)];
      })) + '<div class="w-note">' + esc(list.length + " of " + copySlots.length + " copy slots") + '</div>';
    }
    var csq = body.querySelector("#m10-cs-q");
    if(csq) csq.addEventListener("input", function(){ renderCopySlots(csq.value); });
    renderCopySlots("");
  };

  // ================================================================== M11: Audit log
  ADMIN.draw.M11 = function(body, s){
    var PAGE_SIZE = 50;
    var audit = ((ADMIN.t && ADMIN.t.audit) || []).slice().sort(function(a, b){
      if(a.at === b.at) return 0;
      return a.at < b.at ? 1 : -1; // newest first
    });
    var state = {page: 0};

    var countsByRecord = {};
    audit.forEach(function(a){ countsByRecord[a.record] = (countsByRecord[a.record] || 0) + 1; });
    var recordKeys = Object.keys(countsByRecord).sort();
    var whoValues = {};
    audit.forEach(function(a){ whoValues[a.who] = true; });
    var whoKeys = Object.keys(whoValues).sort();

    var html = '<div class="w-h">Audit log</div>' +
      '<div class="w-note">Every change to a regulated record for every person, newest first. Write actions are mock.</div>' +
      '<div class="spec-t">Counts by record</div>' +
      H.rows(recordKeys.map(function(k){ return [k, H.num(countsByRecord[k])]; }).concat([["total", H.num(audit.length)]])) +
      '<div class="spec-t">Filters</div>' +
      '<label>Record <select id="m11-record"><option value="">All records</option>' +
      recordKeys.map(function(k){ return '<option value="' + esc(k) + '">' + esc(k) + '</option>'; }).join("") +
      '</select></label> ' +
      '<label>Who <select id="m11-who"><option value="">All</option>' +
      whoKeys.map(function(k){ return '<option value="' + esc(k) + '">' + esc(k) + '</option>'; }).join("") +
      '</select></label> ' +
      '<label>Person <input type="text" id="m11-q" placeholder="person id or name" autocomplete="off"></label> ' +
      H.mock("Export", "M11_export") +
      '<div id="m11-results"></div>';
    body.innerHTML = html;

    function detailText(d){
      d = d || {};
      var parts = [];
      for(var k in d){
        if(!Object.prototype.hasOwnProperty.call(d, k)) continue;
        var v = d[k];
        if(v === null || v === undefined || v === "") continue;
        if(v && v.constructor === Array) v = v.join(", ");
        parts.push(k + ": " + v);
      }
      return parts.join("; ");
    }

    function filtered(){
      var recEl = body.querySelector("#m11-record");
      var whoEl = body.querySelector("#m11-who");
      var qEl = body.querySelector("#m11-q");
      var rec = recEl ? recEl.value : "";
      var who = whoEl ? whoEl.value : "";
      var q = (qEl ? qEl.value : "").toLowerCase();
      return audit.filter(function(a){
        if(rec && a.record !== rec) return false;
        if(who && a.who !== who) return false;
        if(q){
          var hay = (String(a.person_id || "") + " " + personLabel(a.person_id)).toLowerCase();
          if(hay.indexOf(q) < 0) return false;
        }
        return true;
      });
    }

    function renderResults(){
      var box = body.querySelector("#m11-results");
      if(!box) return;
      var list = filtered();
      var totalPages = Math.max(1, Math.ceil(list.length / PAGE_SIZE));
      if(state.page >= totalPages) state.page = totalPages - 1;
      if(state.page < 0) state.page = 0;
      var pageRows = list.slice(state.page * PAGE_SIZE, state.page * PAGE_SIZE + PAGE_SIZE);
      var rows = pageRows.map(function(a){
        return [H.when(a.at), H.link(personLabel(a.person_id), "M03", {person: a.person_id}),
          esc(a.record), esc(a.action), esc(a.who), esc(detailText(a.detail))];
      });
      box.innerHTML = H.table(["When", "Person", "Record", "Action", "Who", "Detail"], rows) +
        '<div class="w-note">' + esc(list.length + " rows; page " + (state.page + 1) + " of " + totalPages) + '</div>' +
        '<button type="button" class="w-btn2" id="m11-prev">Prev</button> ' +
        '<button type="button" class="w-btn2" id="m11-next">Next</button>';
      var prev = box.querySelector("#m11-prev");
      var next = box.querySelector("#m11-next");
      if(prev) prev.addEventListener("click", function(){ state.page--; renderResults(); });
      if(next) next.addEventListener("click", function(){ state.page++; renderResults(); });
    }

    ["m11-record", "m11-who"].forEach(function(id){
      var el = body.querySelector("#" + id);
      if(el) el.addEventListener("change", function(){ state.page = 0; renderResults(); });
    });
    var qEl = body.querySelector("#m11-q");
    if(qEl) qEl.addEventListener("input", function(){ state.page = 0; renderResults(); });
    renderResults();
  };

  // ================================================================== M12: Assisted onboarding and DIFM provisioning
  ADMIN.draw.M12 = function(body, s){
    var people = ADMIN.people || [];
    var difmPeople = people.filter(function(p){ return p.tier === "difm"; });
    var provisioning = flatten("ops_queue").filter(function(x){ return x.row.type === "difm_provisioning"; });
    var prospects = people.filter(function(p){ return p.difm_prospect_flag; });
    var prospectGroups = {};
    prospects.forEach(function(p){
      var key = p.tier + "|" + p.difm_prospect_flag;
      prospectGroups[key] = (prospectGroups[key] || 0) + 1;
    });

    var html = '<div class="w-h">Assisted onboarding and DIFM provisioning</div>' +
      '<div class="w-note">A DIFM household created from admin, claimed later by OTP.</div>';

    html += '<div class="spec-t">DIFM people</div>' +
      H.table(["Person", "Created", "OTP claimed", "Owner", "State", "Subscription status"], difmPeople.map(function(p){
        return [H.link(personLabel(p.person_id), "M03", {person: p.person_id}), H.date(p.created_at),
          p.otp_verified_at ? H.when(p.otp_verified_at) : "not yet", esc(ADMIN.staffName(p.adviser_id)),
          esc(stateLabel(p.state_id)), esc(p.subscription_status || "")];
      }));

    html += '<div class="spec-t">Ops queue: DIFM provisioning</div>' +
      H.table(["Person", "Created", "Owner", "Status", "Detail"], provisioning.map(function(x){
        return [H.link(personLabel(x.pid), "M03", {person: x.pid}), H.date(x.row.created_at),
          esc(ADMIN.staffName(x.row.owner)), H.badge(x.row.status, x.row.status === "resolved" ? "ok" : "warn"),
          esc(x.row.detail || "")];
      }));

    html += '<div class="spec-t">DIFM prospects</div>' +
      '<div class="w-note">Total investable assets over the threshold (flag: rule), or flagged by hand after a call (flag: manual).</div>' +
      H.rows(Object.keys(prospectGroups).sort().map(function(key){
        var parts = key.split("|");
        var tier = parts[0], flag = parts[1];
        var contractFlag = flag === "rule" ? "difm_rule" : "difm_manual";
        var label = tier + ", flag " + flag;
        return [label, H.link(H.num(prospectGroups[key]), "M02", {filter: "flag=" + contractFlag + "&tier=" + tier})];
      }));

    html += '<div class="spec-t">Create a DIFM household</div>' +
      '<div class="w-in"><span>First name</span></div>' +
      '<div class="w-in"><span>Phone</span></div>' +
      '<div class="w-in"><span>Household type</span></div>' +
      '<div class="w-chips"><span class="w-chip">Corporate session</span><span class="w-chip">Referral</span></div>' +
      '<div class="w-in"><span>Owner: ' + esc(ADMIN.staffName("harish")) + '</span></div>' +
      H.mock("Create household", "M12_create") + " " +
      H.mock("Invite (never sent)", "M12_invite");

    body.innerHTML = html;
  };

  // ================================================================== M13: KPI page
  ADMIN.draw.M13 = function(body, s){
    var people = ADMIN.people || [];
    var paid = people.filter(function(p){ return isPaidTier(p.tier); });
    var paidTotal = paid.length;

    function inWindow(iso, lo, hi){
      var d = ADMIN.days(iso);
      return d !== null && d >= lo && d < hi;
    }
    function pidsOf(list){ return list.map(function(p){ return p.person_id; }); }

    var ROW_FN = {};

    ROW_FN["Total users"] = function(){
      var list = people.filter(function(p){ return p.kind === "user"; });
      return {value: H.num(list.length) + " people, kind user", pids: pidsOf(list)};
    };

    ROW_FN["New users, today / week / month"] = function(){
      var withOtp = people.filter(function(p){ return p.otp_verified_at; });
      var wk1 = withOtp.filter(function(p){ return inWindow(p.otp_verified_at, 0, 7); });
      var wk2 = withOtp.filter(function(p){ return inWindow(p.otp_verified_at, 7, 14); });
      return {value: "OTP verified in the 7 days before the anchor: " + H.num(wk1.length) +
          "; the 7 days before that: " + H.num(wk2.length), pids: pidsOf(wk1).concat(pidsOf(wk2))};
    };

    ROW_FN["Active users"] = function(){
      // key_dates.last_activity is each person's last event (open_organic, nudge_opened, screen views included)
      var users = people.filter(function(p){ return p.kind === "user"; });
      var d7 = users.filter(function(p){ var d = ADMIN.days(p.key_dates.last_activity); return d !== null && d < 7; });
      var d30 = users.filter(function(p){ var d = ADMIN.days(p.key_dates.last_activity); return d !== null && d < 30; });
      return {value: "active in the 7 days before the anchor (last activity): " + H.num(d7.length) +
        "; in the 30 days: " + H.num(d30.length) + " of " + H.num(users.length) + " users", pids: pidsOf(d30)};
    };

    ROW_FN["In onboarding"] = function(){
      var states = ["S1", "S2", "S2b", "S2c", "S3", "S4", "S5"];
      var pids = [];
      var parts = states.map(function(st){
        var list = people.filter(function(p){ return p.state_id === st; });
        pids = pids.concat(pidsOf(list));
        return stateLabel(st) + ": " + H.link(H.num(list.length), "M02", {filter: "state=" + st});
      });
      return {value: parts.join("; "), pids: pids};
    };

    ROW_FN["Paid users"] = function(){
      var diy = paid.filter(function(p){ return p.tier === "diy"; });
      var diwm = paid.filter(function(p){ return p.tier === "diwm"; });
      return {value: "diy: " + H.link(H.num(diy.length), "M02", {filter: "tier=diy"}) +
        "; diwm: " + H.link(H.num(diwm.length), "M02", {filter: "tier=diwm"}) +
        "; total (diy plus diwm, difm apart): " + H.num(diy.length + diwm.length),
        pids: pidsOf(diy).concat(pidsOf(diwm))};
    };

    function paidBySku(){
      var diy = paid.filter(function(p){ return p.tier === "diy"; });
      var diwm = paid.filter(function(p){ return p.tier === "diwm"; });
      var difm = paid.filter(function(p){ return p.tier === "difm"; });
      return {value: "diy: " + H.link(H.num(diy.length), "M02", {filter: "tier=diy"}) +
        "; diwm: " + H.link(H.num(diwm.length), "M02", {filter: "tier=diwm"}) +
        "; difm (apart, not a self-serve sku): " + H.link(H.num(difm.length), "M02", {filter: "tier=difm"}),
        pids: pidsOf(diy).concat(pidsOf(diwm)).concat(pidsOf(difm))};
    }
    ROW_FN["Plan opted, by SKU"] = paidBySku;
    ROW_FN["Plan type mix"] = paidBySku;

    ROW_FN["Plans in progress (being prepared)"] = function(){
      var stuck = people.filter(function(p){ return p.key_dates.data_complete && !p.key_dates.plan_built; });
      var recent = people.filter(function(p){ return p.key_dates.plan_built && inWindow(p.key_dates.plan_built, 0, 1); });
      return {value: "data complete, plan not built (engine failures): " +
        H.link(H.num(stuck.length), "M02", {filter: "flag=engine_failure"}) +
        "; plans built in the last 24 hours: " + H.num(recent.length),
        pids: pidsOf(stuck).concat(pidsOf(recent))};
    };

    ROW_FN["Plans completed (delivered)"] = function(){
      var built = people.filter(function(p){ return p.key_dates.plan_built; });
      var read = people.filter(function(p){ return p.key_dates.plan_read; });
      return {value: "built: " + H.num(built.length) + "; read: " + H.num(read.length) +
        "; unread (the state S6 gap): " + H.num(built.length - read.length), pids: pidsOf(built)};
    };

    ROW_FN["Pending actions (admin / adviser / customer service)"] = function(){
      var rows = flatten("actions").filter(function(x){ return x.row.status === "open"; });
      var pids = {}; rows.forEach(function(x){ pids[x.pid] = true; });
      return {value: H.num(rows.length) + " actions open (status open in the actions table)", pids: Object.keys(pids)};
    };

    ROW_FN["AUA (assets under advisory)"] = function(){
      var assets = (ADMIN.t && ADMIN.t.assets) || {};
      var byTier = {}, nByTier = {}, pids = [];
      for(var pid in assets){
        if(!Object.prototype.hasOwnProperty.call(assets, pid)) continue;
        var p = ADMIN.byId[pid];
        if(!p || !isPaidTier(p.tier)) continue;
        var sum = 0, vals = assets[pid];
        for(var f in vals) if(Object.prototype.hasOwnProperty.call(vals, f)) sum += vals[f];
        byTier[p.tier] = (byTier[p.tier] || 0) + sum;
        nByTier[p.tier] = (nByTier[p.tier] || 0) + 1;
        pids.push(pid);
      }
      var parts = Object.keys(byTier).sort().map(function(t){
        return t + ": " + numRs(byTier[t]) + " (n=" + H.num(nByTier[t]) + ")";
      });
      return {value: parts.join("; ") || "not in the seed: no paid person carries a recorded asset", pids: pids};
    };

    ROW_FN["SIP book (ongoing monthly investments)"] = function(){
      var star = flatten("actions").filter(function(x){ return x.row.type === "sip_start" && x.row.channel === "in_app_mf"; });
      var starSum = star.reduce(function(a, x){ return a + (x.row.amount || 0); }, 0);
      var sip = (ADMIN.t && ADMIN.t.sip) || {};
      var aaCount = 0, aaSum = 0, aaPids = [];
      for(var pid in sip){
        if(!Object.prototype.hasOwnProperty.call(sip, pid)) continue;
        if(sip[pid].source === "aa"){ aaCount++; aaSum += (sip[pid].value || 0); aaPids.push(pid); }
      }
      return {value: ADMIN.integ("I02") + "-executed SIPs: " + H.num(star.length) + ", " + numRs(starSum) +
        "; AA-detected (current SIP records sourced from AA): " + H.num(aaCount) + ", " + numRs(aaSum),
        pids: star.map(function(x){ return x.pid; }).concat(aaPids)};
    };

    ROW_FN["AA availed"] = function(){
      var rows = flatten("aa_consents");
      var byStatus = {};
      var pids = {};
      rows.forEach(function(x){ byStatus[x.row.status] = (byStatus[x.row.status] || 0) + 1; pids[x.pid] = true; });
      var order = ["active", "declined", "expired", "failed"];
      var parts = order.map(function(k){ return k + ": " + H.num(byStatus[k] || 0); });
      var n = Object.keys(pids).length;
      return {value: parts.join("; ") + "; " + H.num(n) + " of " + H.num(paidTotal) +
        " paid people (" + H.pct(n, paidTotal) + ")", pids: Object.keys(pids)};
    };

    ROW_FN["Active users, retention"] = function(){
      var recent = paid.filter(function(p){ return p.key_dates.last_activity && inWindow(p.key_dates.last_activity, 0, 14); });
      return {value: "not a week-N cohort table; a recency proxy: " + H.num(recent.length) + " of " +
        H.num(paidTotal) + " paid people active in the last 14 days (" + H.pct(recent.length, paidTotal) + ")",
        pids: pidsOf(recent)};
    };

    ROW_FN["Drop-offs by screen and stage"] = function(){
      return {value: "in the event log, not on this tab: screen-view counts per screen (this tab reads the events " +
        "one person at a time)", pids: []};
    };

    ROW_FN["Completion %, average completion time, stage-wise drop-off"] = function(){
      var signedUp = people.filter(function(p){ return p.key_dates.signed_up; }).length;
      var reveal = people.filter(function(p){ return p.key_dates.reveal_seen; }).length;
      var dataComplete = people.filter(function(p){ return p.key_dates.data_complete; }).length;
      return {value: "reveal funnel (signed up to reveal seen): " + H.pct(reveal, signedUp) +
        "; paywall funnel (reveal seen to paid): " + H.pct(paidTotal, reveal) +
        "; data funnel (paid to data complete): " + H.pct(dataComplete, paidTotal) +
        "; in the event log, not on this tab: average completion time and a per-screen drop-off",
        pids: []};
    };

    ROW_FN["KYC failure rate"] = function(){
      // the KYC fetch is the I06 integration; a failed fetch falls back to a typed address, so kyc_status stays verified
      var calls = 0, failedCalls = 0, failedPids = [];
      Object.keys(ADMIN.ievents || {}).forEach(function(pid){
        var hit = false;
        (ADMIN.ievents[pid] || []).forEach(function(e){
          if(e.integration !== "I06") return;
          calls++;
          if(e.outcome !== "ok"){ failedCalls++; hit = true; }
        });
        if(hit) failedPids.push(pid);
      });
      return {value: ADMIN.integ("I06") + ": " + H.num(failedCalls) + " of " + H.num(calls) + " calls failed (" +
        H.pct(failedCalls, calls) + "); " + H.num(failedPids.length) + " people had a failure and typed their address instead",
        pids: failedPids};
    };

    ROW_FN["AA failure rate"] = function(){
      var withStatus = people.filter(function(p){ return p.aa_status; });
      var attempted = withStatus.filter(function(p){
        return p.aa_status === "connected" || p.aa_status === "partial" || p.aa_status === "failed" || p.aa_status === "expired";
      });
      var failed = withStatus.filter(function(p){ return p.aa_status === "failed"; });
      var notConnected = withStatus.filter(function(p){ return p.aa_status === "not_connected"; }).length;
      var cas = withStatus.filter(function(p){ return p.aa_status === "cas_uploaded"; }).length;
      return {value: H.num(failed.length) + " of " + H.num(attempted.length) + " connected or attempted (" +
        H.pct(failed.length, attempted.length) + "); not connected: " + H.num(notConnected) +
        "; used CAS instead: " + H.num(cas), pids: pidsOf(withStatus)};
    };

    ROW_FN["Sample plan to paid conversion"] = function(){
      var reveal = people.filter(function(p){ return p.key_dates.reveal_seen; });
      return {value: "reveal seen to paid: " + H.num(paidTotal) + " of " + H.num(reveal.length) + " (" +
        H.pct(paidTotal, reveal.length) + ")", pids: pidsOf(reveal).concat(pidsOf(paid))};
    };

    function paymentConversion(){
      var s2b = people.filter(function(p){ return p.state_id === "S2b"; });
      var s2c = people.filter(function(p){ return p.state_id === "S2c"; });
      return {value: "checkout abandoned, esign incomplete (state S2b): " +
        H.link(H.num(s2b.length), "M02", {filter: "state=S2b"}) +
        "; esign done, not paid (state S2c): " + H.link(H.num(s2c.length), "M02", {filter: "state=S2c"}) +
        "; in the event log, not on this tab: the paywall_viewed count that starts this funnel",
        pids: pidsOf(s2b).concat(pidsOf(s2c))};
    }
    ROW_FN["Payment conversion"] = paymentConversion;
    ROW_FN["Conversion rate"] = paymentConversion;

    ROW_FN["Subscription conversion"] = function(){
      return {value: "not in the seed: a one-time-purchase SKU (sku_cards has only diy and diwm, both " +
        "subscriptions; this conversion needs a one-time SKU to start from)", pids: []};
    };

    function revenueMirror(){
      var subs = flatten("subscriptions");
      var pays = flatten("payments");
      var dealSku = {};
      subs.forEach(function(x){ dealSku[x.row.deal_id] = x.row.sku; });
      var activeBySku = {}, capturedBySku = {}, pids = {};
      subs.forEach(function(x){
        pids[x.pid] = true;
        if(x.row.status === "active") activeBySku[x.row.sku] = (activeBySku[x.row.sku] || 0) + 1;
      });
      pays.forEach(function(x){
        pids[x.pid] = true;
        var sku = dealSku[x.row.deal_id] || "unknown";
        if(x.row.status === "captured") capturedBySku[sku] = (capturedBySku[sku] || 0) + 1;
      });
      var skus = ["diy", "diwm"];
      var parts = skus.map(function(sk){
        return sk + ": " + H.num(capturedBySku[sk] || 0) + " payments captured, " +
          H.num(activeBySku[sk] || 0) + " active deals";
      });
      return {value: parts.join("; ") + "; amounts stay Rs ___ (never invented)", pids: Object.keys(pids)};
    }
    ROW_FN["Revenue"] = revenueMirror;

    ROW_FN["Plans generated, viewed, downloaded"] = function(){
      var versions = flatten("plan_versions");
      var viewed = versions.filter(function(x){ return x.row.read_at; });
      var downloaded = versions.filter(function(x){ return x.row.pdf_downloaded_at; });
      return {value: "generated: " + H.num(versions.length) + "; viewed: " + H.num(viewed.length) +
        " (" + H.pct(viewed.length, versions.length) + "); downloaded: " + H.num(downloaded.length) +
        " (" + H.pct(downloaded.length, versions.length) + ")",
        pids: versions.map(function(x){ return x.pid; })};
    };

    ROW_FN["Time from data completion to plan"] = function(){
      return {value: "in the event log, not on this tab: the data_complete time to the second (the key date keeps " +
        "the day; plan_built has a full timestamp)", pids: []};
    };

    ROW_FN["FP to IP conversion"] = function(){
      return {value: "not in the seed: a one-time, FP-only purchase event (the current tiers bundle the " +
        "financial plan into the membership, so there is nothing to convert from)", pids: []};
    };

    ROW_FN["Not started / partially completed / completed"] = function(){
      var users = people.filter(function(p){ return p.kind === "user"; });
      var buckets = {not_started: [], partial: [], completed: []};
      users.forEach(function(p){
        var pf = p.profile_fulfilment_pct;
        if(pf === null || pf === undefined || pf === 0) buckets.not_started.push(p);
        else if(pf === 100) buckets.completed.push(p);
        else buckets.partial.push(p);
      });
      return {value: "proxy from profile_fulfilment_pct (not the per-D01-D09 flags, which live only in " +
        "each person's chunk): not started " + H.num(buckets.not_started.length) + ", partial " +
        H.num(buckets.partial.length) + ", completed " + H.num(buckets.completed.length),
        pids: pidsOf(users)};
    };

    ROW_FN["System generated / AA sourced / manually entered"] = function(){
      var sip = (ADMIN.t && ADMIN.t.sip) || {};
      var bySource = {}, pids = [];
      for(var pid in sip){
        if(!Object.prototype.hasOwnProperty.call(sip, pid)) continue;
        bySource[sip[pid].source] = (bySource[sip[pid].source] || 0) + 1;
        pids.push(pid);
      }
      var parts = Object.keys(bySource).sort().map(function(k){ return k + ": " + H.num(bySource[k]); });
      return {value: "current SIP records only: " + parts.join("; ") +
        "; not in the seed (aggregate): a per-field source count across every financial record, which " +
        "lives only in each person's chunk", pids: pids};
    };

    ROW_FN["Needs verification"] = function(){
      var items = flatten("ops_queue").filter(function(x){
        return x.row.type === "data_quality" || x.row.type === "unknown_isin" || x.row.type === "aa_failure";
      });
      var byType = {};
      items.forEach(function(x){ byType[x.row.type] = (byType[x.row.type] || 0) + 1; });
      var open = items.filter(function(x){ return x.row.status === "open"; });
      var flagged = people.filter(function(p){ return p.plausibility_flag; });
      var parts = Object.keys(byType).sort().map(function(k){ return k + ": " + H.num(byType[k]); });
      return {value: parts.join("; ") + " (queue items, open: " + H.num(open.length) + "); people flagged " +
        "plausibility on M02: " + H.link(H.num(flagged.length), "M02", {filter: "flag=plausibility"}),
        pids: items.map(function(x){ return x.pid; }).concat(pidsOf(flagged))};
    };

    ROW_FN["Total paid, pending, failed, refunded, revenue"] = function(){
      var pays = flatten("payments");
      var captured = pays.filter(function(x){ return x.row.status === "captured"; }).length;
      var failed = pays.filter(function(x){ return x.row.status === "failed"; }).length;
      var subs = flatten("subscriptions");
      var pendingMandate = subs.filter(function(x){ return x.row.status === "pending_mandate"; }).length;
      var refundRequested = subs.filter(function(x){ return x.row.refund_requested; }).length;
      return {value: "captured: " + H.num(captured) + "; failed: " + H.num(failed) + "; pending mandate: " +
        H.num(pendingMandate) + "; refund requested: " + H.num(refundRequested) +
        " (none completed yet; refund policy is to be decided); revenue stays Rs ___",
        pids: pays.map(function(x){ return x.pid; }).concat(subs.map(function(x){ return x.pid; }))};
    };

    ROW_FN["Last sync and failures: KYC, AA, payment gateway, email, WhatsApp, push"] = function(){
      var ievents = ADMIN.ievents || {};
      var byVendor = {};
      for(var pid in ievents){
        if(!Object.prototype.hasOwnProperty.call(ievents, pid)) continue;
        var rows = ievents[pid] || [];
        for(var i = 0; i < rows.length; i++){
          var e = rows[i];
          var v = byVendor[e.integration] || {ok: 0, failed: 0, last: null};
          if(e.outcome === "ok") v.ok++; else v.failed++;
          if(!v.last || e.at > v.last) v.last = e.at;
          byVendor[e.integration] = v;
        }
      }
      var ids = Object.keys(byVendor).sort();
      var parts = ids.map(function(id){
        var v = byVendor[id];
        return ADMIN.integ(id) + ": ok " + H.num(v.ok) + ", failed " + H.num(v.failed) + ", last " + H.date(v.last);
      });
      return {value: parts.join("; "), pids: Object.keys(ievents)};
    };

    ROW_FN["Templates: email, WhatsApp"] = function(){
      var slots = (ADMIN.t.config.copy_slots) || [];
      var email = slots.filter(function(c){ return c.channel === "email"; }).length;
      var wa = slots.filter(function(c){ return c.channel === "WhatsApp"; }).length;
      return {value: "email: " + H.num(email) + "; WhatsApp: " + H.num(wa), pids: []};
    };
    ROW_FN["Templates: push"] = function(){
      var slots = (ADMIN.t.config.copy_slots) || [];
      var n = slots.filter(function(c){ return c.channel === "push"; }).length;
      return {value: H.num(n) + " push slots", pids: []};
    };
    ROW_FN["Templates: in-app"] = function(){
      var slots = (ADMIN.t.config.copy_slots) || [];
      var n = slots.filter(function(c){ return c.channel === "in-app"; }).length;
      return {value: H.num(n) + " in-app slots", pids: []};
    };
    ROW_FN["Trigger-based rules"] = function(){
      var slots = (ADMIN.t.config.copy_slots) || [];
      var states = {};
      slots.forEach(function(c){ states[c.state] = true; });
      return {value: "no rule engine is built; the state table is the rule. " + H.num(Object.keys(states).length) +
        " state labels carry nudge copy in this seed", pids: []};
    };

    ROW_FN["Intro and transition videos"] = function(){
      return {value: "not in the seed: no CMS video entries are generated", pids: []};
    };
    ROW_FN["Sample plan content"] = function(){
      return {value: "not in the seed: no persona sample-plan content is generated", pids: []};
    };
    ROW_FN["Questions and answer options"] = function(){
      var rpq = (ADMIN.t && ADMIN.t.rpq) || {};
      var versions = {};
      for(var pid in rpq){
        if(!Object.prototype.hasOwnProperty.call(rpq, pid)) continue;
        if(rpq[pid] && rpq[pid].questionnaire_version) versions[rpq[pid].questionnaire_version] = true;
      }
      return {value: "not in the seed: question wording and answer options; the questionnaire version tag " +
        "is present: " + esc(Object.keys(versions).join(", ")), pids: []};
    };
    ROW_FN["Tooltips, disclaimers, educational content, general content, FAQs"] = function(){
      return {value: "not in the seed: no CMS content of this kind is generated", pids: []};
    };
    ROW_FN["Agreements"] = function(){
      var signed = ((ADMIN.t && ADMIN.t.audit) || []).filter(function(a){ return a.record === "agreement" && a.action === "signed"; });
      return {value: "agreement version: " + esc(ADMIN.t.config.agreement_version || "") + "; signed: " +
        H.num(signed.length), pids: signed.map(function(a){ return a.person_id; })};
    };

    ROW_FN["Admin users, roles and permissions"] = function(){
      var staff = (ADMIN.t && ADMIN.t.staff) || [];
      var byRole = {};
      staff.forEach(function(st){ (st.roles || []).forEach(function(r){ byRole[r] = (byRole[r] || 0) + 1; }); });
      var parts = Object.keys(byRole).sort().map(function(r){ return r + ": " + H.num(byRole[r]); });
      return {value: H.num(staff.length) + " staff records; by role: " + parts.join("; "), pids: []};
    };
    ROW_FN["Audit logs"] = function(){
      var audit = (ADMIN.t && ADMIN.t.audit) || [];
      return {value: H.num(audit.length) + " rows; exportable from the audit log screen, " + H.link("M11", "M11"),
        pids: audit.map(function(a){ return a.person_id; })};
    };
    ROW_FN["System settings"] = function(){
      var flags = (ADMIN.t.config.feature_flags) || {};
      var parts = Object.keys(flags).sort().map(function(k){ return k + ": " + esc(flags[k]); });
      return {value: parts.join("; "), pids: []};
    };
    ROW_FN["Fee structure"] = function(){
      var cards = (ADMIN.t.config.sku_cards) || [];
      var parts = cards.map(function(c){
        return c.sku + ": " + esc(c.price_monthly) + " per month, " + esc(c.price_quarterly) +
          " per quarter, calls included " + esc(c.calls_included);
      });
      return {value: parts.join("; "), pids: []};
    };

    ROW_FN["Name, email, mobile, signed-in date, last activity"] = function(){
      var users = people.filter(function(p){ return p.kind === "user"; });
      var complete = users.filter(function(p){ return p.email && p.phone && p.key_dates.signed_up; });
      return {value: H.num(complete.length) + " of " + H.num(users.length) +
        " contacts carry a name, email, phone and signed-up date", pids: pidsOf(users)};
    };
    ROW_FN["Paid user, subscription, current journey stage"] = function(){
      var byStatus = {};
      paid.forEach(function(p){ byStatus[p.subscription_status] = (byStatus[p.subscription_status] || 0) + 1; });
      var parts = Object.keys(byStatus).sort().map(function(k){ return k + ": " + H.num(byStatus[k]); });
      return {value: H.num(paidTotal) + " paid people carry a subscription status and a journey stage; " +
        parts.join("; "), pids: pidsOf(paid)};
    };
    ROW_FN["Onboarding %, KYC status, AA status, financial plan status, investment plan status"] = function(){
      var users = people.filter(function(p){ return p.kind === "user"; });
      var kyc = {}, fp = {}, ip = {};
      users.forEach(function(p){
        var m = p.mirrors || {};
        if(m.kyc_status) kyc[m.kyc_status] = (kyc[m.kyc_status] || 0) + 1;
        if(m.fp_status) fp[m.fp_status] = (fp[m.fp_status] || 0) + 1;
        if(m.ip_status) ip[m.ip_status] = (ip[m.ip_status] || 0) + 1;
      });
      function fmt(o){ return Object.keys(o).sort().map(function(k){ return k + " " + H.num(o[k]); }).join(", "); }
      return {value: "kyc: " + fmt(kyc) + "; financial plan: " + fmt(fp) + "; investment plan: " + fmt(ip),
        pids: pidsOf(users)};
    };
    ROW_FN["Assigned adviser / RM"] = function(){
      var withAdviser = paid.filter(function(p){ return p.adviser_id; });
      return {value: H.num(withAdviser.length) + " of " + H.num(paidTotal) + " paid people carry an adviser or RM",
        pids: pidsOf(withAdviser)};
    };

    var rows = ADMIN.placement || [];
    var groups = [];
    var bySec = {};
    rows.forEach(function(r){
      var fn = ROW_FN[r.item];
      var res = fn ? fn() : {value: "not in the seed: no computation defined for this row", pids: []};
      var g = bySec[r.sec];
      if(!g){ g = {sec: r.sec, items: [], pidset: {}}; bySec[r.sec] = g; groups.push(g); }
      g.items.push({item: r.item, def: r.def, wire: r.wire, value: res.value});
      (res.pids || []).forEach(function(pid){ g.pidset[pid] = true; });
    });

    var html = '<div class="w-h">KPI page</div>' +
      '<div class="w-note">The Placement rows, computed from the seed in the browser, run ' + esc(ADMIN.run) +
      '. Every figure is seed, synthetic.</div>';
    groups.forEach(function(g){
      html += '<div class="spec-t">' + esc(g.sec) + '</div>' +
        H.table(["Item", "Definition", "Value", "Screen"], g.items.map(function(it){
          return [esc(it.item), esc(it.def), it.value, wireAnchor(it.wire)];
        }));
      var topups = 0;
      for(var pid in g.pidset){
        if(Object.prototype.hasOwnProperty.call(g.pidset, pid) && ADMIN.byId[pid] && ADMIN.byId[pid].is_topup) topups++;
      }
      html += '<div class="w-note">seed, synthetic; topups: ' + H.num(topups) + '</div>';
    });
    body.innerHTML = html;
  };

  // ================================================================== M14: Roles and permissions
  ADMIN.draw.M14 = function(body, s){
    var screens = (typeof SCREENS !== "undefined" ? SCREENS : []).filter(function(sc){ return sc.sec === "M"; });

    var html = '<div class="w-h">Roles and permissions</div>' +
      '<div class="w-note">The access matrix: which seat can act, read, or read only their own people, on which screen.</div>';

    html += '<div class="spec-t">Screens by role</div>' +
      H.table(["Screen"].concat(ROLES), screens.map(function(sc){
        var label = sc.id + " " + sc.title;
        var cells = ROLES.map(function(r){ return esc((sc.role && sc.role[r]) || "-"); });
        return [esc(label)].concat(cells);
      }));

    var writeRows = [];
    screens.forEach(function(sc){
      (sc.writes || []).forEach(function(w){ writeRows.push({screen: sc.id + " " + sc.title, action: w.action, event: w.event, roles: w.roles || []}); });
    });
    html += '<div class="spec-t">Write actions by role</div>' +
      H.table(["Screen", "Action", "Event"].concat(ROLES), writeRows.map(function(w){
        var cells = ROLES.map(function(r){ return w.roles.indexOf(r) >= 0 ? "yes" : "-"; });
        return [esc(w.screen), esc(w.action), esc(w.event)].concat(cells);
      }));

    html += '<div class="w-note">' + ADMIN.integ("I14") + ' profiles cover that product only; this matrix is for the built tool.</div>';
    body.innerHTML = html;
  };
})();
