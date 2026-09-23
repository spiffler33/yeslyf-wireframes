// yeslyf admin wireframes: M05 to M09 draw functions (phase C part 2, 23 Sep 2026, PLAN_admin_seed_v01.md
// section 14). Registers ADMIN.draw.M05 .. ADMIN.draw.M09 on top of the API in scripts/admin_core.js (window.ADMIN,
// ADMIN.h); never duplicates that API, only adds to the draw registry. Plain browser JavaScript: an IIFE, var and
// function only, no arrow functions, no modules, no libraries. Low-fi grey wireframe: only the w-* classes already
// in scripts/renderer_v02.css and the admin CSS already in docs/admin_wireframes.html; no new colour, no inline
// style, no new visual design.
//
// Every table cell that is plain text is escaped with H.esc; H.table/H.rows cells are otherwise HTML built from
// H.num/H.date/H.when/H.link/H.badge/H.mock, which already escape what they print.
(function(){
  var H = ADMIN.h;

  // ---------------------------------------------------------------- shared helpers (this file only)

  // "PID First Last", the same shape as admin_core.js's own (private) person label, for H.link text.
  function personLabel(pid){
    var p = ADMIN.byId[pid];
    if(!p) return pid;
    return pid + " " + (p.first_name || "") + (p.last_name ? " " + p.last_name : "");
  }
  function personLink(pid){
    return H.link(personLabel(pid), "M03", {person: pid});
  }
  // The M02 filter contract's tier keys are lead, free, diy, diwm, difm (a lead never carries people.tier).
  function tierBucket(p){
    return p.kind === "lead" ? "lead" : (p.tier || "free");
  }
  // A small bold section label inside a screen (reuses .spec-t, already defined for the side panel's own
  // section titles; .w-h is kept for the one screen-title heading per draw function).
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
  // given, renders each option's visible text (e.g. ADMIN.staffName for a staff id); the option value is always
  // the raw underlying value so a change handler can compare it straight against a row's field.
  function filterSelect(id, label, options, labelFn){
    var html = '<label>' + H.esc(label) + ' <select id="' + id + '"><option value="">all ' + H.esc(label) + '</option>';
    options.forEach(function(v){
      var text = labelFn ? labelFn(v) : v;
      html += '<option value="' + H.esc(v) + '">' + H.esc(text) + '</option>';
    });
    html += '</select></label>';
    return html;
  }
  // Natural sort for the short machine ids this file sorts a lot (v1..v10, A1, A2, ops01, P00001): split each
  // string into its non-digit prefix and trailing digit run by scanning character codes (no regex), and compare
  // the trailing numbers when the prefixes match; otherwise fall back to plain string order. Safe on ordinary
  // enum strings too (aa_status values, ops_queue types): they have no trailing digits, so this reduces to the
  // same plain string order a normal .sort() would give them.
  function splitTrailingNum(s){
    s = String(s);
    var i = s.length;
    while(i > 0 && s.charCodeAt(i - 1) >= 48 && s.charCodeAt(i - 1) <= 57) i--;
    return {prefix: s.slice(0, i), num: i < s.length ? parseInt(s.slice(i), 10) : null};
  }
  function naturalCompare(a, b){
    a = String(a); b = String(b);
    var pa = splitTrailingNum(a), pb = splitTrailingNum(b);
    if(pa.prefix === pb.prefix && pa.num !== null && pb.num !== null) return pa.num - pb.num;
    return a < b ? -1 : (a > b ? 1 : 0);
  }
  // The distinct values of accessor(x) over list, naturally sorted; used to build filter dropdown option lists.
  function distinctValues(list, accessor){
    var seen = {}, out = [];
    list.forEach(function(x){
      var v = accessor(x);
      if(v !== undefined && v !== null && v !== "" && !seen[v]){ seen[v] = true; out.push(v); }
    });
    out.sort(naturalCompare);
    return out;
  }
  // A "value, count" table, naturally sorted by value; counts is a plain {value: n} map. Used for every simple
  // breakdown in this file (plan/assumptions/instrument version counts, aa_status counts, consent status counts).
  function countsTable(title, counts){
    var keys = Object.keys(counts).sort(naturalCompare);
    var rows = keys.map(function(k){ return [H.esc(k), H.num(counts[k])]; });
    return subHead(title) + H.table(["Value", "People"], rows);
  }
  // Flattens a {person_id: [row, ...]} table (ops_queue, holdings, aa_consents, cas_uploads all share this shape)
  // into a plain array of {pid, row}, the seed's own iteration order.
  function flattenByPerson(table){
    var out = [];
    table = table || {};
    for(var pid in table){
      if(!Object.prototype.hasOwnProperty.call(table, pid)) continue;
      var rows = table[pid] || [];
      for(var i = 0; i < rows.length; i++) out.push({pid: pid, row: rows[i]});
    }
    return out;
  }
  // Whole days between two full ISO datetimes (never Date.now() or new Date() with no argument); the seed's
  // timestamps share one fixed offset throughout, so plain Date parsing is safe for a difference like this
  // (only display formatting is offset-sensitive, and this never displays the Date objects it builds).
  function daysBetween(fromIso, toIso){
    if(!fromIso || !toIso) return null;
    var a = new Date(fromIso), b = new Date(toIso);
    if(isNaN(a.getTime()) || isNaN(b.getTime())) return null;
    return Math.floor((b.getTime() - a.getTime()) / 86400000);
  }
  // Nearest-rank percentile of an already-ascending-sorted numeric array.
  function percentile(sortedArr, p){
    if(!sortedArr.length) return null;
    var idx = Math.ceil((p / 100) * sortedArr.length) - 1;
    if(idx < 0) idx = 0;
    if(idx >= sortedArr.length) idx = sortedArr.length - 1;
    return sortedArr[idx];
  }
  // "unknown_isin" -> "unknown isin": plain fixed-delimiter formatting of a closed set of seed enum values, not
  // a text classifier.
  function humanize(s){ return String(s || "").split("_").join(" "); }

  // {y, m} of an ISO string's own written year and month, by slicing (never a Date object): the seed's dates all
  // carry the fixed +05:30 offset, so the first 7 characters are always that calendar year and month as written,
  // regardless of the viewer's or the test runner's own timezone.
  function ymOf(iso){ return {y: +iso.slice(0, 4), m: +iso.slice(5, 7)}; }
  var MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  function monthLabel(ym){ return MONTHS[ym.m - 1] + " " + ym.y; }
  function addMonths(ym, n){
    var total = ym.y * 12 + (ym.m - 1) + n;
    return {y: Math.floor(total / 12), m: (total % 12) + 1};
  }

  // ================================================================== M05: states board

  ADMIN.draw.M05 = function(body, s){
    var people = ADMIN.people || [];
    var states = ADMIN.states || [];

    var headers = ["State", "Who", "Lead", "Free", "DIY", "DIWM", "DIFM", "Total", "S16", "Topup"];
    var totalTopup = 0;
    var rows = states.map(function(st){
      var inState = people.filter(function(p){ return p.state_id === st.id; });
      var counts = {lead: 0, free: 0, diy: 0, diwm: 0, difm: 0};
      var s16 = 0, topup = 0;
      inState.forEach(function(p){
        var b = tierBucket(p);
        if(counts[b] !== undefined) counts[b]++;
        if(p.s16_flag) s16++;
        if(p.is_topup) topup++;
      });
      totalTopup += topup;
      var total = inState.length;
      function tierCell(n, tier){
        return n ? H.link(H.num(n), "M02", {filter: "state=" + st.id + "&tier=" + tier}) : "0";
      }
      var totalCell = total ? H.link(H.num(total), "M02", {filter: "state=" + st.id}) : "0";
      var s16Cell = s16 ? H.link(H.num(s16), "M02", {filter: "state=" + st.id + "&flag=s16"}) : "0";
      var topupCell = topup ? H.link(H.num(topup), "M02", {filter: "state=" + st.id + "&flag=topup"}) : "0";
      return [H.esc(st.id), H.esc(st.who), tierCell(counts.lead, "lead"), tierCell(counts.free, "free"),
              tierCell(counts.diy, "diy"), tierCell(counts.diwm, "diwm"), tierCell(counts.difm, "difm"),
              totalCell, s16Cell, topupCell];
    });

    // S2 ladder-day histogram: whole days since key_dates.reveal_seen, bucketed at the ladder days 1, 3, 7, 21, 82.
    var s2 = people.filter(function(p){ return p.state_id === "S2"; });
    var thresholds = [1, 3, 7, 21, 82];
    var labels = ["0 to 1 day", "1 to 3 days", "3 to 7 days", "7 to 21 days", "21 to 82 days", "82 days and beyond"];
    var buckets = [0, 0, 0, 0, 0, 0];
    s2.forEach(function(p){
      var d = ADMIN.days(p.key_dates && p.key_dates.reveal_seen);
      if(d === null || d === undefined) return;
      var idx = thresholds.length;
      for(var i = 0; i < thresholds.length; i++){ if(d < thresholds[i]){ idx = i; break; } }
      buckets[idx]++;
    });
    var maxN = 0;
    buckets.forEach(function(n){ if(n > maxN) maxN = n; });
    var histHtml = labels.map(function(label, i){
      var pct = maxN ? Math.round((buckets[i] / maxN) * 100) : 0;
      return '<div class="w-prog"><span>' + H.esc(label) + ': ' + H.num(buckets[i]) + '</span><div><i style="width:' + pct + '%"></i></div></div>';
    }).join("");

    body.innerHTML =
      '<div class="w-h">' + H.esc(s.title) + '</div>' +
      H.table(headers, rows) +
      subHead("S2 ladder-day spread (whole days since the reveal was seen; " + H.num(s2.length) + " people in S2)") +
      histHtml +
      '<div class="w-note">Topups: ' + H.num(totalTopup) + ". Every person is synthetic; counts are the seed's, not a forecast.</div>";
  };

  // ================================================================== M06: ops queue

  function m06Matrix(items, types, statuses){
    var headers = ["Type"].concat(statuses).concat(["Total"]);
    var rows = types.map(function(ty){
      var rowTotal = 0;
      var cells = statuses.map(function(st){
        var n = items.filter(function(x){ return x.row.type === ty && x.row.status === st; }).length;
        rowTotal += n;
        return H.num(n);
      });
      return [H.esc(humanize(ty))].concat(cells).concat([H.num(rowTotal)]);
    });
    return subHead("By type and status") + H.table(headers, rows);
  }
  function m06StatusBadge(status){
    if(status === "resolved") return H.badge(status, "ok");
    if(status === "open") return H.badge(status, "warn");
    return H.badge(status || "", "");
  }
  function m06QueueTable(list){
    var headers = ["Item", "Type", "Person", "Created", "Age", "Owner", "Status", "Detail", "SLA"];
    var rows = list.map(function(x){
      var ageLabel;
      if(x.row.status === "resolved" && x.row.resolved_at){
        var toResolve = daysBetween(x.row.created_at, x.row.resolved_at);
        ageLabel = toResolve === null ? "" : (H.num(toResolve) + " d to resolve");
      } else {
        var age = ADMIN.days(x.row.created_at);
        ageLabel = age === null ? "" : (H.num(age) + " d");
      }
      return [H.esc(x.row.item_id), H.esc(humanize(x.row.type)), personLink(x.pid), H.date(x.row.created_at),
              ageLabel, H.esc(ADMIN.staffName(x.row.owner)), m06StatusBadge(x.row.status), H.esc(x.row.detail || ""), "-"];
    });
    return subHead("Queue (" + H.num(list.length) + ")") +
      (list.length ? H.table(headers, rows) : '<div class="w-note">No items match this filter.</div>');
  }

  ADMIN.draw.M06 = function(body, s){
    var items = flattenByPerson(ADMIN.t.ops_queue);
    items.sort(function(a, b){ return a.row.created_at < b.row.created_at ? 1 : (a.row.created_at > b.row.created_at ? -1 : 0); });
    var types = distinctValues(items, function(x){ return x.row.type; });
    var statuses = distinctValues(items, function(x){ return x.row.status; });
    var owners = distinctValues(items, function(x){ return x.row.owner; });

    body.innerHTML =
      '<div class="w-h">' + H.esc(s.title) + '</div>' +
      mockBar(s.writes) +
      m06Matrix(items, types, statuses) +
      '<div class="w-chips">' +
        filterSelect("m06-type", "type", types, humanize) +
        filterSelect("m06-status", "status", statuses) +
        filterSelect("m06-owner", "owner", owners, ADMIN.staffName) +
      '</div>' +
      '<div class="w-note">SLA per item type: to be decided.</div>' +
      '<div class="m06-queue"></div>';

    var typeSel = body.querySelector("#m06-type");
    var statusSel = body.querySelector("#m06-status");
    var ownerSel = body.querySelector("#m06-owner");
    var box = body.querySelector(".m06-queue");
    function render(){
      if(!box) return;
      var filtered = items.filter(function(x){
        return (!typeSel || !typeSel.value || x.row.type === typeSel.value) &&
               (!statusSel || !statusSel.value || x.row.status === statusSel.value) &&
               (!ownerSel || !ownerSel.value || x.row.owner === ownerSel.value);
      });
      box.innerHTML = m06QueueTable(filtered);
    }
    if(typeSel) typeSel.addEventListener("change", render);
    if(statusSel) statusSel.addEventListener("change", render);
    if(ownerSel) ownerSel.addEventListener("change", render);
    render();
  };

  // ================================================================== M07: data quality and integrations

  function m07Plausibility(){
    var list = (ADMIN.people || []).filter(function(p){ return p.plausibility_flag; });
    var rows = list.map(function(p){ return [personLink(p.person_id), H.esc(p.state_id || ""), H.esc(tierBucket(p))]; });
    return subHead("Plausibility flags (" + H.num(list.length) + ")") +
      (list.length ? H.table(["Person", "State", "Tier"], rows) : '<div class="w-note">None in this seed.</div>');
  }
  function m07UnknownIsin(){
    var list = flattenByPerson(ADMIN.t.holdings).filter(function(x){ return x.row.unknown_isin; });
    var rows = list.map(function(x){
      return [personLink(x.pid), H.esc(x.row.isin || ""), H.esc(x.row.name || ""), H.esc(x.row.source || ""), H.date(x.row.as_of)];
    });
    return subHead("Unknown ISINs (" + H.num(list.length) + ")") +
      (list.length ? H.table(["Person", "ISIN", "Name", "Source", "As of"], rows) : '<div class="w-note">None in this seed.</div>');
  }
  function m07EngineFailure(){
    var list = (ADMIN.people || []).filter(function(p){ return p.engine_failure; });
    var rows = list.map(function(p){
      return [personLink(p.person_id), H.esc(p.state_id || ""), H.date(p.key_dates && p.key_dates.data_complete)];
    });
    return subHead("Engine failures (" + H.num(list.length) + ")") +
      (list.length ? H.table(["Person", "State", "Data complete"], rows) : '<div class="w-note">None in this seed.</div>');
  }
  function m07Integrations(){
    var byId = {};
    var t = ADMIN.ievents || {};
    for(var pid in t){
      if(!Object.prototype.hasOwnProperty.call(t, pid)) continue;
      var evs = t[pid];
      for(var i = 0; i < evs.length; i++){
        var e = evs[i];
        if(!byId[e.integration]) byId[e.integration] = [];
        byId[e.integration].push(e);
      }
    }
    var ids = Object.keys(byId).sort(naturalCompare);
    var headers = ["Integration", "Calls", "Ok", "Failed", "Timeout", "Failure rate", "Last success", "Last failure", "Median ms", "95th pct ms"];
    var rows = ids.map(function(id){
      var evs = byId[id];
      var ok = 0, failed = 0, timeout = 0, lastOk = "", lastFail = "";
      var lat = [];
      evs.forEach(function(e){
        if(e.outcome === "ok"){ ok++; if(!lastOk || e.at > lastOk) lastOk = e.at; }
        else if(e.outcome === "failed"){ failed++; if(!lastFail || e.at > lastFail) lastFail = e.at; }
        else if(e.outcome === "timeout"){ timeout++; if(!lastFail || e.at > lastFail) lastFail = e.at; }
        if(typeof e.latency_ms === "number") lat.push(e.latency_ms);
      });
      lat.sort(function(a, b){ return a - b; });
      var med = percentile(lat, 50), p95 = percentile(lat, 95);
      return [H.esc(ADMIN.integ(id)), H.num(evs.length), H.num(ok), H.num(failed), H.num(timeout),
              H.pct(failed + timeout, evs.length), lastOk ? H.when(lastOk) : "-", lastFail ? H.when(lastFail) : "-",
              med === null ? "-" : H.num(med), p95 === null ? "-" : H.num(p95)];
    });
    return subHead("Integrations (" + H.num(ids.length) + "); failure rate counts failed and timeout together") +
      (ids.length ? H.table(headers, rows) : '<div class="w-note">No integration events in this seed.</div>');
  }

  ADMIN.draw.M07 = function(body, s){
    body.innerHTML =
      '<div class="w-h">' + H.esc(s.title) + '</div>' +
      mockBar(s.writes) +
      m07Plausibility() +
      m07UnknownIsin() +
      m07EngineFailure() +
      m07Integrations();
  };

  // ================================================================== M08: plan versions and publish impact

  // {pid: latest plan_versions row}; "latest" is the row with the largest built_at (ISO strings sharing one
  // fixed offset throughout the seed, so plain string comparison already sorts them chronologically).
  function m08LatestPlanVersions(){
    var out = {};
    var t = ADMIN.t.plan_versions || {};
    for(var pid in t){
      if(!Object.prototype.hasOwnProperty.call(t, pid)) continue;
      var versions = t[pid] || [];
      var best = null;
      for(var i = 0; i < versions.length; i++){
        if(!best || versions[i].built_at > best.built_at) best = versions[i];
      }
      if(best) out[pid] = best;
    }
    return out;
  }
  function m08CountBy(latest, field){
    var counts = {};
    for(var pid in latest){
      if(!Object.prototype.hasOwnProperty.call(latest, pid)) continue;
      var v = latest[pid][field];
      var k = (v === null || v === undefined || v === "") ? "none" : v;
      counts[k] = (counts[k] || 0) + 1;
    }
    return counts;
  }
  function m08Publishes(latest){
    var pubs = (ADMIN.t.config && ADMIN.t.config.assumptions_versions) || [];
    var headers = ["Assumptions version", "Instrument set version", "Published", "People on it"];
    var rows = pubs.map(function(r){
      var n = 0;
      for(var pid in latest){
        if(!Object.prototype.hasOwnProperty.call(latest, pid)) continue;
        var v = latest[pid];
        if(v.assumptions_version === r.assumptions_version && v.instrument_set_version === r.instrument_set_version) n++;
      }
      return [H.esc(r.assumptions_version), H.esc(r.instrument_set_version), H.date(r.published_at), H.num(n)];
    });
    return subHead("Publishes") +
      (rows.length ? H.table(headers, rows) : '<div class="w-note">No publishes recorded.</div>');
  }
  function m08Unaccepted(latest){
    var list = (ADMIN.people || []).filter(function(p){ return p.state_id === "S11"; });
    var headers = ["Person", "Version", "Built", "Days waiting"];
    var rows = list.map(function(p){
      var v = latest[p.person_id];
      var days = v ? ADMIN.days(v.built_at) : null;
      return [personLink(p.person_id), H.esc(v ? v.plan_version : ""), v ? H.when(v.built_at) : "", days === null ? "" : H.num(days)];
    });
    return subHead("Unaccepted updates (" + H.num(list.length) + ")") +
      (list.length ? H.table(headers, rows) : '<div class="w-note">None in this seed.</div>');
  }
  // pids whose latest assumptions_version is not the newest published one (by config.assumptions_versions'
  // published_at); sorted naturally for a stable page order.
  function m08OldVersionPids(latest){
    var pubs = (ADMIN.t.config && ADMIN.t.config.assumptions_versions) || [];
    var newest = null;
    pubs.forEach(function(r){ if(!newest || r.published_at > newest.published_at) newest = r; });
    var pids = [];
    if(newest){
      for(var pid in latest){
        if(!Object.prototype.hasOwnProperty.call(latest, pid)) continue;
        if(latest[pid].assumptions_version !== newest.assumptions_version) pids.push(pid);
      }
    }
    pids.sort(naturalCompare);
    return pids;
  }
  function m08OldVersionTable(pids, page, pageSize){
    var html = subHead("On an old assumptions version (" + H.num(pids.length) + ")");
    if(!pids.length) return html + '<div class="w-note">No one is on an old version in this seed.</div>';
    var start = page * pageSize;
    var slice = pids.slice(start, start + pageSize);
    var rows = slice.map(function(pid){ return [personLink(pid)]; });
    var pages = Math.ceil(pids.length / pageSize);
    html += H.table(["Person"], rows);
    html += '<div class="w-row"><span>Page ' + (page + 1) + ' of ' + pages + '</span><b>' +
      '<button type="button" class="w-btn2 m08-prev"' + (page <= 0 ? " disabled" : "") + '>Prev</button> ' +
      '<button type="button" class="w-btn2 m08-next"' + (start + pageSize >= pids.length ? " disabled" : "") + '>Next</button>' +
      '</b></div>';
    return html;
  }
  function m08Links(){
    return '<div class="w-p"><a href="wireframes_v02.html#L05">L05</a>, ' +
      '<a href="wireframes_v02.html#L06">L06</a> and <a href="wireframes_v02.html#L08">L08</a>: ' +
      'the publish screens on the wireframes tab.</div>';
  }

  ADMIN.draw.M08 = function(body, s){
    var latest = m08LatestPlanVersions();
    var oldPids = m08OldVersionPids(latest);
    var pageSize = 50, page = 0;

    body.innerHTML = '<div class="w-h">' + H.esc(s.title) + '</div><div class="m08-body"></div>';
    var box = body.querySelector(".m08-body");
    function render(){
      if(!box) return;
      box.innerHTML =
        countsTable("By plan version", m08CountBy(latest, "plan_version")) +
        countsTable("By assumptions version", m08CountBy(latest, "assumptions_version")) +
        countsTable("By instrument set version", m08CountBy(latest, "instrument_set_version")) +
        m08Publishes(latest) +
        m08Unaccepted(latest) +
        m08OldVersionTable(oldPids, page, pageSize) +
        m08Links();
      var prev = box.querySelector(".m08-prev");
      var next = box.querySelector(".m08-next");
      if(prev) prev.addEventListener("click", function(){ if(page > 0){ page--; render(); } });
      if(next) next.addEventListener("click", function(){ if((page + 1) * pageSize < oldPids.length){ page++; render(); } });
    }
    render();
  };

  // ================================================================== M09: AA and CAS

  function m09ConsentStatus(){
    var peopleCounts = {};
    (ADMIN.people || []).forEach(function(p){
      var k = p.aa_status || "none";
      peopleCounts[k] = (peopleCounts[k] || 0) + 1;
    });
    var consentCounts = {};
    flattenByPerson(ADMIN.t.aa_consents).forEach(function(x){
      var k = x.row.status || "none";
      consentCounts[k] = (consentCounts[k] || 0) + 1;
    });
    return countsTable("People by AA status", peopleCounts) + countsTable("Consent records by status", consentCounts);
  }
  // Consents by consent_expiry month, the anchor's month through six months after, plus an "already expired"
  // count. Both the cutoff and the month bucket are worked out by slicing and comparing the ISO strings
  // themselves (never a Date object): the seed's timestamps share one fixed offset throughout, so this is exact
  // and immune to the runtime's own timezone.
  function m09ExpiryCalendar(){
    var anchor = ADMIN.meta && ADMIN.meta.anchor;
    var withExpiry = flattenByPerson(ADMIN.t.aa_consents).filter(function(x){ return x.row.consent_expiry; });
    var already = 0;
    var monthCounts = [0, 0, 0, 0, 0, 0, 0];
    var anchorYM = anchor ? ymOf(anchor) : null;
    withExpiry.forEach(function(x){
      var exp = x.row.consent_expiry;
      if(anchor && exp < anchor){ already++; return; }
      if(!anchorYM) return;
      var expYM = ymOf(exp);
      var offset = (expYM.y - anchorYM.y) * 12 + (expYM.m - anchorYM.m);
      if(offset >= 0 && offset <= 6) monthCounts[offset]++;
    });
    var rows = monthCounts.map(function(n, i){
      var label = anchorYM ? monthLabel(addMonths(anchorYM, i)) : String(i);
      return [H.esc(label), H.num(n)];
    });
    var alreadyCell = already ? H.link(H.num(already), "M02", {filter: "state=S15"}) : "0";
    return subHead("Consent expiry calendar") +
      '<div class="w-row"><span>Already expired</span><b>' + alreadyCell + '</b></div>' +
      H.table(["Month", "Expiring"], rows);
  }
  function m09FipFailures(){
    var counts = {};
    flattenByPerson(ADMIN.t.aa_consents).forEach(function(x){
      (x.row.institutions_failed || []).forEach(function(name){ counts[name] = (counts[name] || 0) + 1; });
    });
    var institutionsHtml = countsTable("FIP failures by institution", counts);
    var list = (ADMIN.people || []).filter(function(p){ return p.aa_status === "partial" || p.aa_status === "failed"; });
    var rows = list.map(function(p){
      var badge = H.badge(p.aa_status || "", p.aa_status === "failed" ? "bad" : "warn");
      return [personLink(p.person_id), badge];
    });
    var peopleHtml = subHead("People with partial or failed consents (" + H.num(list.length) + ")") +
      (list.length ? H.table(["Person", "AA status"], rows) : '<div class="w-note">None in this seed.</div>');
    return institutionsHtml + peopleHtml;
  }
  function m09Cas(){
    var all = flattenByPerson(ADMIN.t.cas_uploads);
    var requested = all.filter(function(x){ return x.row.requested_at; }).length;
    var uploaded = all.filter(function(x){ return x.row.uploaded_at; }).length;
    var parsed = all.filter(function(x){ return x.row.parsed_at; }).length;
    var abandoned = all.filter(function(x){ return x.row.abandoned_at; }).length;
    var awaiting = all.filter(function(x){ return x.row.requested_at && !x.row.uploaded_at && !x.row.abandoned_at; });
    var summary = subHead("CAS") + H.rows([
      ["Requested", H.num(requested)],
      ["Uploaded", H.num(uploaded)],
      ["Parsed", H.num(parsed)],
      ["Abandoned", H.num(abandoned)]
    ]);
    var rows = awaiting.map(function(x){
      var days = ADMIN.days(x.row.requested_at);
      return [personLink(x.pid), H.date(x.row.requested_at), H.num(x.row.reminder_count || 0), days === null ? "" : H.num(days)];
    });
    var awaitingHtml = subHead("Awaiting upload (" + H.num(awaiting.length) + ")") +
      (awaiting.length ? H.table(["Person", "Requested", "Reminders", "Days since request"], rows) : '<div class="w-note">None in this seed.</div>');
    return summary + awaitingHtml;
  }

  ADMIN.draw.M09 = function(body, s){
    body.innerHTML =
      '<div class="w-h">' + H.esc(s.title) + '</div>' +
      mockBar(s.writes) +
      m09ConsentStatus() +
      m09ExpiryCalendar() +
      m09FipFailures() +
      m09Cas();
  };
})();
