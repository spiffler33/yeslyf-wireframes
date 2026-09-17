// yeslyf wireframes v0.2 - renderer. Extends the v0.1 renderer (same element grammar, same layout).
// Embedded by scripts/build_site.py into docs/wireframes_v02.html after the data blobs:
//   SECTIONS, SCREENS (live screens in flow order), DROPPED (ids), STATES (section N contract, may be empty),
//   REASONS (compliance reason -> {review, check}).
//   INTEGRATIONS (phase 12: {as_of, rows: [{id, vendor, choice, fallback, screens}]}, the rows that serve each screen)
//   and FREEZE (the templates' freeze status), both optional.
// Filters: tier, path, state, compliance, template, frozen. Comments save under localStorage key "yeslyf_wire_v02";
// every verdict, reason and comment change is one row in board_entries (page "wireframes_v02") through the shared
// layer scripts/board_store.js (window.yeslyfBoard), which also fills the top bar pill and the History toggle.
// WIRE_OPTS (optional, set by the audience files of phase 9): identities (list), lock (one identity, fixed),
// key (storage key), spec ("full" | "design" | "compliance"), compFilter (false hides the compliance walk),
// exportTitle, exportFile. Absent: the full site behaviour.
(function(){
  var OPTS = (typeof WIRE_OPTS !== "undefined" && WIRE_OPTS) ? WIRE_OPTS : {};
  var TIERS = ["ALL","DIY","DIWM","DIFM"];
  var PATHS = ["both","aa","manual"];
  var IDENTITIES = OPTS.identities || ["Bhuvanaa","Harish","Gaurav","Kajal","Somil","Vatsal","Spinach","Compliance"];
  var LOCK = OPTS.lock || "";
  var SPEC = OPTS.spec || "full";
  var COMP_FILTER = OPTS.compFilter !== false;
  var EXPORT_TITLE = OPTS.exportTitle || "# yeslyf wireframes v0.2 - review comments";
  var EXPORT_FILE = OPTS.exportFile || "yeslyf_wireframe_review_v02.md";
  var VERDICTS = ["Keep","Change","Drop","Question"];
  var KEY = OPTS.key || "yeslyf_wire_v02";
  var PAGE = OPTS.page || "wireframes_v02";
  var state = { idx:0, tier:"ALL", path:"both", st:"", comp:"all", tpl:"all", fz:"all", map:false };
  var FREEZES = ["all","frozen","open"];
  var INTEG = (typeof INTEGRATIONS !== "undefined" && INTEGRATIONS) ? INTEGRATIONS : {as_of:"", rows:[]};
  var TFZ = (typeof FREEZE !== "undefined" && FREEZE) ? FREEZE : null;
  var liveChoices = null;  // final or open per integrations row, read from the board table once the page is live
  var byId = {}; SCREENS.forEach(function(s,i){ byId[s.id]=i; });
  var secName = {}; SECTIONS.forEach(function(s){ secName[s[0]]=s[1]; });
  var states = (typeof STATES !== "undefined" && STATES) ? STATES : [];
  var stateById = {}; states.forEach(function(st){ stateById[st.id]=st; });
  var dropped = (typeof DROPPED !== "undefined" && DROPPED) ? DROPPED : [];
  var split = (typeof SPLIT !== "undefined" && SPLIT) ? SPLIT : [];
  var reasons = (typeof REASONS !== "undefined" && REASONS) ? REASONS : {};
  var reasonNames = Object.keys(reasons);
  var templates = []; SCREENS.forEach(function(s){ if(templates.indexOf(s.template)<0) templates.push(s.template); }); templates.sort();

  // ---------- persistence (best effort) ----------
  var store = {};
  try { store = JSON.parse(localStorage.getItem(KEY) || "{}") || {}; } catch(e){ store = {}; }
  if(!store.notes) store.notes = {};
  if(!store.who) store.who = "";
  if(LOCK) store.who = LOCK;
  function save(){ try { localStorage.setItem(KEY, JSON.stringify(store)); } catch(e){} }
  function noteFor(id){ if(!store.notes[id]) store.notes[id] = {verdict:"", text:"", reason:"", who:""}; return store.notes[id]; }
  var BOARD = (typeof yeslyfBoard !== "undefined") ? yeslyfBoard : null;
  var NO_ID = BOARD ? BOARD.noIdentity : "Pick who you are at the top first; nothing is recorded without a name.";
  function put(id, field, value, kind){ if(!BOARD) return true; return BOARD.write({item_id:id, field:field, value:value, who:store.who || "", kind:kind}); }
  function saved(ok){ flash(ok ? "Saved in this browser" : NO_ID); }
  function wb(){ return BOARD ? BOARD.label() : "offline; this file is the record"; }
  function applyRemote(rows){
    // the latest row per screen and field from board_entries; the same shape the controls write
    rows.forEach(function(r){ if(byId[r.item_id] === undefined) return; var n = noteFor(r.item_id); var v = r.value || "";
      if(r.field === "verdict") n.verdict = VERDICTS.indexOf(v) >= 0 ? v : ""; else if(r.field === "reason") n.reason = v; else if(r.field === "text") n.text = v; else return;
      n.who = r.who || n.who; });
    save(); renderSpec(); renderNav();
  }

  function esc(s){ return String(s === undefined || s === null ? "" : s).split("&").join("&amp;").split("<").join("&lt;").split(">").join("&gt;").split('"').join("&quot;"); }
  function flash(t){ var el = document.getElementById("saved"); if(el) el.textContent = t || ""; }

  // ---------- scope ----------
  function tierOk(s){ return state.tier === "ALL" || s.tier.indexOf("ALL") >= 0 || s.tier.indexOf(state.tier) >= 0; }
  function pathOk(s){ return state.path === "both" || s.path === "both" || s.path === state.path; }
  function compOk(s){
    if(state.comp === "all") return true;
    var c = s.compliance || {};
    if(state.comp === "flagged") return !!c.review;
    return !!(c.reasons && c.reasons.indexOf(state.comp) >= 0);
  }
  function tplOk(s){ return state.tpl === "all" || s.template === state.tpl; }
  function fzOk(s){ return state.fz === "all" || (s.freeze && s.freeze.status === state.fz); }
  function inScope(s){ return pathOk(s) && compOk(s) && tplOk(s) && fzOk(s); }
  function scope(){ return SCREENS.filter(inScope); }
  function walkList(){ var out = []; SCREENS.forEach(function(s,i){ if(inScope(s) && tierOk(s)) out.push(i); }); return out; }
  function ensureScope(i){
    if(inScope(SCREENS[i])) return;
    state.path = "both"; state.comp = "all"; state.tpl = "all"; state.fz = "all"; syncFilters();
  }

  // ---------- wireframe element renderer (v0.1 grammar) ----------
  function el(e){
    var t = e[0];
    switch(t){
      case "h": return '<div class="w-h">'+esc(e[1])+'</div>';
      case "p": return '<div class="w-p">'+esc(e[1])+'</div>';
      case "note": return '<div class="w-note">'+esc(e[1])+'</div>';
      case "strip": return '<div class="w-strip">'+esc(e[1])+'</div>';
      case "in": return '<div class="w-in"><span>'+esc(e[1])+'</span></div>';
      case "chips": return '<div class="w-chips">'+e[1].map(function(c){return '<span class="w-chip">'+esc(c)+'</span>';}).join("")+'</div>';
      case "radio": return '<div class="w-radio">'+e[1].map(function(c){return '<div class="w-opt"><i></i><span>'+esc(c)+'</span></div>';}).join("")+'</div>';
      case "btn": return '<button class="w-btn" data-go="'+esc(e[2]||"")+'">'+esc(e[1])+'</button>';
      case "btn2": return '<button class="w-btn w-btn2" data-go="'+esc(e[2]||"")+'">'+esc(e[1])+'</button>';
      case "link": return '<a class="w-link" data-go="'+esc(e[2]||"")+'">'+esc(e[1])+'</a>';
      case "card": return '<div class="w-card"><div class="w-card-t">'+esc(e[1])+'</div><ul>'+(e[2]||[]).map(function(r){return '<li>'+esc(r)+'</li>';}).join("")+'</ul></div>';
      case "rows": return '<div class="w-rows">'+e[1].map(function(r){return '<div class="w-row"><span>'+esc(r[0])+'</span><b>'+esc(r[1])+'</b></div>';}).join("")+'</div>';
      case "chart": return '<div class="w-chart"><span>'+esc(e[1])+'</span></div>';
      case "video": return '<div class="w-video"><i></i><span>'+esc(e[1])+'</span></div>';
      case "num": return '<div class="w-num">'+esc(e[1])+'</div>';
      case "tabs": return '<div class="w-tabs">'+e[1].map(function(c,i){return '<span'+(i===0?' class="on"':'')+'>'+esc(c)+'</span>';}).join("")+'</div>';
      case "badge": return '<span class="w-badge">'+esc(e[1])+'</span>';
      case "progress": return '<div class="w-prog"><span>'+esc(e[1])+'</span><div><i style="width:'+(e[2]||50)+'%"></i></div></div>';
      case "table": return '<table class="w-table"><thead><tr>'+e[1].map(function(c){return '<th>'+esc(c)+'</th>';}).join("")+'</tr></thead><tbody>'+e[2].map(function(r){return '<tr>'+r.map(function(c){return '<td>'+esc(c)+'</td>';}).join("")+'</tr>';}).join("")+'</tbody></table>';
      default: return '';
    }
  }

  // ---------- render ----------
  function renderNav(){
    var html = '';
    SECTIONS.forEach(function(sec){
      var items = scope().filter(function(s){ return s.sec === sec[0]; });
      if(!items.length) return;
      html += '<div class="nav-sec"><div class="nav-sec-t">'+esc(sec[1])+'<em>'+items.length+'</em></div>';
      items.forEach(function(s){
        var i = byId[s.id]; var n = store.notes[s.id];
        var cls = (i === state.idx ? ' on' : '') + (tierOk(s) ? '' : ' dim');
        var dot = n && (n.text || n.verdict) ? '<i class="dot"></i>' : '';
        var mark = s.v02 && s.v02.status === "new" ? '<i class="mk new">new</i>' : (s.v02 && (s.v02.status === "changed" || s.v02.status === "rebuilt") ? '<i class="mk">changed</i>' : '');
        if(s.freeze && s.freeze.status === "open") mark += '<i class="mk open">open</i>';
        html += '<a class="nav-item'+cls+'" href="#'+s.id+'"><span class="nav-id">'+s.id+'</span><span>'+esc(s.title)+mark+'</span>'+dot+'</a>';
      });
      html += '</div>';
    });
    document.getElementById("nav").innerHTML = html;
    var on = document.querySelector(".nav-item.on"); if(on && on.scrollIntoView){ try { on.scrollIntoView({block:"nearest"}); } catch(e){} }
  }

  function renderRibbon(){
    var s = SCREENS[state.idx];
    document.getElementById("ribbon").innerHTML = SECTIONS.map(function(sec){
      var first = scope().filter(function(x){ return x.sec === sec[0]; })[0];
      if(!first) return '';
      return '<a href="#'+first.id+'" class="rib'+(sec[0] === s.sec ? ' on' : '')+'">'+esc(sec[1].split(" (")[0])+'</a>';
    }).join("");
  }

  function renderStrip(){
    var strip = document.getElementById("statestrip"); if(!strip) return;
    var st = stateById[state.st];
    if(!st){ strip.innerHTML = ''; strip.className = 'strip off'; return; }
    var parts = ['State '+esc(st.id)+': '+esc(st.who)+'; lands on '+esc(st.lands_on)+'; primary action: '+esc(st.primary_action)];
    if(st.minutes) parts.push(esc(st.minutes));
    if(st.exit) parts.push('exit: '+esc(st.exit));
    if(st.mock) parts.push('mock <a href="#'+esc(st.mock)+'" class="br">'+esc(st.mock)+'</a>');
    strip.innerHTML = parts.join('; ');
    strip.className = 'strip';
  }

  function renderScreen(){
    var s = SCREENS[state.idx];
    var frame = document.getElementById("frame");
    frame.className = "frame " + (s.frame === "desktop" ? "desktop" : "phone");
    var body = s.ui.map(el).join("");
    var hidden = !tierOk(s) ? '<div class="w-hidden">Not shown to a '+esc(state.tier)+' user</div>' : '';
    var fz = s.freeze ? '<span class="fz">'+esc(s.freeze.status)+'</span>' : '';
    frame.innerHTML = '<div class="frame-top"><span>'+esc(s.id)+'</span><span>'+esc(s.title)+'</span><span>'+esc(s.template)+'</span>'+fz+'</div><div class="frame-body">'+hidden+body+'</div>';
    document.getElementById("crumb").textContent = secName[s.sec] + "  /  " + s.id + "  " + s.title;
    var w = walkList(); var pos = w.indexOf(state.idx);
    document.getElementById("counter").textContent = (pos >= 0 ? (pos+1) + " of " + w.length : "outside the current filter") + "  /  " + SCREENS.length + " screens in v0.2";
    Array.prototype.forEach.call(frame.querySelectorAll("[data-go]"), function(b){
      b.addEventListener("click", function(ev){ ev.preventDefault(); var t = b.getAttribute("data-go"); if(t && byId[t] !== undefined){ ensureScope(byId[t]); go(byId[t]); } });
    });
    renderStrip();
  }

  function list(title, arr, linkable){
    if(!arr || !arr.length) return '';
    return '<div class="spec-block"><div class="spec-t">'+title+'</div><ul>'+arr.map(function(x){
      if(linkable){ return '<li><span>'+esc(x[0])+'</span> <a href="#'+esc(x[1])+'" class="br">'+esc(x[1])+'</a></li>'; }
      return '<li>'+esc(x)+'</li>';
    }).join("")+'</ul></div>';
  }
  function fieldLine(f){
    if(typeof f === "string") return f;
    var bits = [];
    if(f.gate) bits.push("gate");
    if(f.forward) bits.push(f.forward);
    if(f.source) bits.push("source " + (Array.isArray(f.source) ? f.source.join(", ") : f.source));
    if(f.precision) bits.push("precision " + (Array.isArray(f.precision) ? f.precision.join(", ") : f.precision));
    return (f.f || f.name || "") + (bits.length ? " (" + bits.join("; ") + ")" : "") + (f.note ? ": " + f.note : "");
  }
  function fieldsTitle(s){
    // "Fields captured" when any entry is required, optional or default; otherwise the screen only shows or holds
    // values captured elsewhere: "Fields read" (phase 12, Vatsal, 17 Sep 2026).
    var captured = (s.spec.fields || []).some(function(f){ return f && (f.forward === "required" || f.forward === "optional" || f.forward === "default"); });
    return captured ? "Fields captured" : "Fields read";
  }
  function marker(s){
    var v = s.v02 || {status:"kept", causes:[]};
    var st = v.status;
    var label = st === "new" ? "New in v0.2" : (st === "changed" || st === "rebuilt") ? "Changed in v0.2" + (st === "rebuilt" ? " (rebuilt)" : "") : "Kept from v0.1";
    var cls = st === "new" ? " new" : (st === "changed" || st === "rebuilt") ? " changed" : "";
    var causes = (SPEC === "full" && v.causes && v.causes.length) ? '<div>Cause: '+v.causes.map(esc).join("; ")+'</div>' : '';
    return '<div class="marker'+cls+'">'+freezeLine(s)+'<b>'+label+'</b>'+causes+'</div>';
  }
  function freezeLine(s){
    // Frozen since <date>, owed: ...  or  Open because: ... (phase 12; text, never colour alone). One item reads
    // inline; several read as a list, so the box stays scannable.
    var f = s.freeze; if(!f) return '';
    function items(arr){ if(!arr || !arr.length) return ''; if(arr.length === 1) return ' '+esc(arr[0]); return '<ul class="fz-list">'+arr.map(function(x){ return '<li>'+esc(x)+'</li>'; }).join("")+'</ul>'; }
    var owed = (f.owed && f.owed.length) ? '<div class="fz-owed">Owed:'+items(f.owed)+'</div>' : '';
    if(f.status === "open") return '<div class="fz-line"><b>Open</b> since '+esc(f.since)+', because:'+items(f.reason)+owed+'</div>';
    return '<div class="fz-line"><b>Frozen</b> since '+esc(f.since)+(owed ? '' : '')+'</div>'+owed;
  }
  function integrationsBlock(s){
    // The rows whose screens list names this screen, with the final or open choice: the build's value with its
    // date until the live rows arrive, then the current choice from the board table. Rows serving every screen
    // (screens ["all"]) are not repeated here.
    var rows = INTEG.rows.filter(function(r){ return r.screens.indexOf(s.id) >= 0; });
    var title = "Integrations" + ((!liveChoices && INTEG.as_of) ? " (as of " + esc(INTEG.as_of) + ")" : "");
    if(!rows.length) return '<div class="spec-block"><div class="spec-t">'+title+'</div><div class="tiers">none</div></div>';
    return '<div class="spec-block"><div class="spec-t">'+title+'</div><ul>'+rows.map(function(r){
      var ch = (liveChoices && liveChoices[r.id]) || r.choice || "open";
      var slip = (r.fallback && r.fallback !== "none") ? '; if it slips: '+esc(r.fallback) : '';
      return '<li>'+esc(r.id)+' '+esc(r.vendor)+', '+esc(ch)+slip+'</li>'; }).join("")+'</ul></div>';
  }

  function renderSpec(){
    var s = SCREENS[state.idx]; var n = noteFor(s.id);
    var c = s.compliance || {review:false, reasons:[], checks:[]};
    var html = marker(s);
    html += '<div class="spec-purpose">'+esc(s.purpose)+'</div>';
    if(SPEC === "compliance"){
      html += '<div class="spec-block"><div class="spec-t">Compliance flag</div><div class="tiers">reasons: ' + esc((c.reasons || []).join(", ")) + (c.note ? '; ' + esc(c.note) : '') + '</div></div>';
      if(c.checks && c.checks.length){
        html += '<div class="chk"><b>Compliance checklist</b><ul>'+c.checks.map(function(x){ return '<li>'+esc(x)+'</li>'; }).join("")+'</ul></div>';
      }
      html += '<div class="spec-block"><div class="spec-t">Where it sits</div><div class="tiers">'+esc(s.template)+'; path '+esc(s.path)+'; shown to '+esc(s.tier.join(", "))+'</div></div>';
      document.getElementById("spec").innerHTML = html;
      reviewControls(s, n);
      return;
    }
    html += '<div class="spec-block"><div class="spec-t">Template</div><div class="tiers">'+esc(s.template)+'</div></div>';
    html += '<div class="spec-block"><div class="spec-t">Path</div><div class="tiers">'+esc(s.path)+'</div></div>';
    html += '<div class="spec-block"><div class="spec-t">Shown to</div><div class="tiers">'+esc(s.tier.join(", "))+'</div></div>';
    html += list(fieldsTitle(s), (s.spec.fields || []).map(fieldLine));
    html += list("Moving forward", s.spec.forward);
    if(s.spec.ladder && s.spec.ladder.length){
      html += '<div class="spec-block"><div class="spec-t">Capture ladder</div><ul>'+s.spec.ladder.map(function(x){ return '<li><b>'+esc(x[0])+'</b>: '+esc(x[1])+'</li>'; }).join("")+'</ul></div>';
    }
    if(s.spec.multi_select){
      var ms = s.spec.multi_select;
      html += '<div class="spec-block"><div class="spec-t">Multi-select</div><ul>'+(ms.options || []).map(function(o){ return '<li><span>'+esc(o[0])+'</span> opens <a href="#'+esc(o[1])+'" class="br">'+esc(o[1])+'</a></li>'; }).join("")+
              '<li>'+esc(ms.none)+': every type is '+esc(ms.unticked)+'; then <a href="#'+esc(ms.after)+'" class="br">'+esc(ms.after)+'</a></li><li>Unticked types: '+esc(ms.unticked)+', never opened</li>'+(ms.prefilled ? '<li>'+esc(ms.prefilled)+'</li>' : '')+'</ul></div>';
    }
    if(s.spec.chip_map){
      html += '<div class="spec-block"><div class="spec-t">Chips and what each reopens</div><ul>'+s.spec.chip_map.map(function(c){ return '<li><span>'+esc(c.chip)+'</span>: '+c.reopens.map(function(t){ return '<a href="#'+esc(t)+'" class="br">'+esc(t)+'</a>'; }).join(", ")+'</li>'; }).join("")+'</ul></div>';
    }
    html += list("Logic", s.spec.logic);
    html += list("Branches", s.spec.branches, true);
    html += list("States", s.spec.states);
    html += list("Dev notes", s.spec.dev);
    html += integrationsBlock(s);
    html += list("Events", s.events);
    if(SPEC === "full"){
      html += '<div class="spec-block"><div class="spec-t">Compliance flag</div><div class="tiers">' + (c.review ? 'review: yes' : 'review: no') + '; reasons: ' + esc((c.reasons || []).join(", ")) + (c.note ? '; ' + esc(c.note) : '') + '</div></div>';
      if(c.checks && c.checks.length){
        html += '<div class="chk"><b>Compliance checklist</b><ul>'+c.checks.map(function(x){ return '<li>'+esc(x)+'</li>'; }).join("")+'</ul></div>';
      }
    }
    document.getElementById("spec").innerHTML = html;
    reviewControls(s, n);
  }
  function reviewControls(s, n){
    var v = document.getElementById("verdict");
    if(v) Array.prototype.forEach.call(v.querySelectorAll("button"), function(b){ b.className = (b.getAttribute("data-v") === n.verdict) ? "on" : ""; });
    var rs = document.getElementById("reason"); if(rs) rs.value = n.reason || "";
    var ta = document.getElementById("comment"); if(ta){ ta.value = n.text || ""; ta.placeholder = "Comment on "+s.id+": what to keep, change or drop, and why. Compliance: comment on language."; }
    var rv = document.getElementById("reviewer"); if(rv) rv.value = store.who || "";
    syncReason();
    if(BOARD) BOARD.refreshHistory();
    flash("");
  }
  function syncReason(){
    var wrap = document.getElementById("reason-wrap"); if(!wrap) return;
    wrap.className = "reason-wrap" + (store.who === "Compliance" ? "" : " off");
  }

  function go(i){
    if(i < 0 || i >= SCREENS.length) return;
    state.idx = i; var id = SCREENS[i].id;
    if(location.hash !== "#"+id){ try { history.replaceState(null, "", "#"+id); } catch(e){} }
    renderNav(); renderRibbon(); renderScreen(); renderSpec();
    var sel = document.getElementById("jump"); if(sel) sel.value = id;
    var m = document.getElementById("main"); if(m) m.scrollTop = 0;
  }
  function step(d){
    var w = walkList(); if(!w.length) return;
    var pos = w.indexOf(state.idx);
    var j = pos < 0 ? 0 : (pos + d + w.length) % w.length;
    go(w[j]);
  }
  function goFirst(){ var w = walkList(); if(w.length) go(w[0]); else { flash("No screen matches this filter"); } }

  // ---------- map ----------
  function renderMap(){
    var html = '';
    SECTIONS.forEach(function(sec){
      var items = scope().filter(function(s){ return s.sec === sec[0]; });
      if(!items.length) return;
      html += '<div class="map-sec"><h3>'+esc(sec[1])+'</h3><div class="map-row">'+items.map(function(s){
        return '<a href="#'+s.id+'" class="map-chip'+(tierOk(s) ? '' : ' dim')+'"><b>'+s.id+'</b>'+esc(s.title)+'</a>';
      }).join("")+'</div></div>';
    });
    document.getElementById("map").innerHTML = html;
  }
  function toggleMap(force){
    state.map = (force === undefined) ? !state.map : force;
    document.body.classList.toggle("map-on", state.map);
    document.getElementById("mapbtn").textContent = state.map ? "Back to screens" : "Journey map";
    if(state.map) renderMap();
  }

  // ---------- export ----------
  function exportText(){
    var lines = [EXPORT_TITLE, "Exported " + new Date().toLocaleString() + (store.who ? " by " + store.who : ""),
                 "Write-back: " + wb(), ""];
    var count = 0;
    SECTIONS.forEach(function(sec){
      var items = SCREENS.filter(function(s){ return s.sec === sec[0]; }).filter(function(s){ var n = store.notes[s.id]; return n && (n.text || n.verdict); });
      if(!items.length) return;
      lines.push("## " + sec[1]);
      items.forEach(function(s){
        var n = store.notes[s.id]; count++;
        var tag = []; if(n.verdict) tag.push(n.verdict); if(n.who) tag.push(n.who); if(n.reason) tag.push(n.reason);
        lines.push("- **" + s.id + " " + s.title + "**" + (tag.length ? " [" + tag.join("; ") + "]" : ""));
        if(n.text) lines.push("  " + String(n.text).split("\n").join("\n  "));
      });
      lines.push("");
    });
    if(!count) lines.push("(no comments yet)");
    return lines.join("\n");
  }
  function exportNotes(){
    var md = exportText();
    try { navigator.clipboard && navigator.clipboard.writeText(md); } catch(e){}
    try {
      var blob = new Blob([md], {type:"text/markdown"});
      var a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = EXPORT_FILE;
      document.body.appendChild(a); a.click(); document.body.removeChild(a);
    } catch(e){}
    flash("Comments exported and copied.");
  }

  // ---------- filters ----------
  function setFilter(kind, value){
    if(kind === "tier"){ state.tier = TIERS.indexOf(value) >= 0 ? value : "ALL"; }
    else if(kind === "path"){ state.path = PATHS.indexOf(value) >= 0 ? value : "both"; }
    else if(kind === "comp"){ state.comp = (value === "all" || value === "flagged" || reasonNames.indexOf(value) >= 0) ? value : "all"; }
    else if(kind === "tpl"){ state.tpl = (value === "all" || templates.indexOf(value) >= 0) ? value : "all"; }
    else if(kind === "freeze"){ state.fz = FREEZES.indexOf(value) >= 0 ? value : "all"; }
    else if(kind === "state"){
      state.st = stateById[value] ? value : "";
      var st = stateById[state.st];
      syncFilters();
      if(st && byId[st.lands_on] !== undefined){ ensureScope(byId[st.lands_on]); go(byId[st.lands_on]); }
      else { go(state.idx); }
      if(state.map) renderMap();
      return;
    }
    syncFilters();
    if(!inScope(SCREENS[state.idx]) || !tierOk(SCREENS[state.idx])) goFirst(); else go(state.idx);
    if(state.map) renderMap();
  }
  function syncFilters(){
    var tf = document.getElementById("tiers");
    if(tf) Array.prototype.forEach.call(tf.querySelectorAll("button"), function(x){ x.className = x.getAttribute("data-t") === state.tier ? "on" : ""; });
    var p = document.getElementById("fpath"); if(p) p.value = state.path;
    var c = document.getElementById("fcomp"); if(c) c.value = state.comp;
    var t = document.getElementById("ftpl"); if(t) t.value = state.tpl;
    var z = document.getElementById("ffreeze"); if(z) z.value = state.fz;
    var s = document.getElementById("fstate"); if(s) s.value = state.st;
    var sel = document.getElementById("jump");
    if(sel){ sel.innerHTML = scope().map(function(x){ return '<option value="'+x.id+'">'+x.id+'  '+esc(x.title)+'</option>'; }).join(""); sel.value = SCREENS[state.idx].id; }
  }
  function opt(v, label, on){ return '<option value="'+esc(v)+'"'+(on ? ' selected' : '')+'>'+esc(label)+'</option>'; }

  // ---------- wiring ----------
  function init(){
    var tf = document.getElementById("tiers");
    if(tf){
      tf.innerHTML = TIERS.map(function(t){ return '<button data-t="'+t+'"'+(t === state.tier ? ' class="on"' : '')+'>'+t+'</button>'; }).join("");
      tf.addEventListener("click", function(ev){ var b = ev.target.closest("button"); if(!b) return; setFilter("tier", b.getAttribute("data-t")); });
    }
    var fp = document.getElementById("fpath");
    if(fp){
      fp.innerHTML = opt("both", "both paths", true) + opt("aa", "aa", false) + opt("manual", "manual", false);
      fp.addEventListener("change", function(){ setFilter("path", fp.value); });
    }
    var fs = document.getElementById("fstate"); var fsw = document.getElementById("fstate-wrap");
    if(fs && states.length){
      fs.innerHTML = opt("", "no state", true) + states.map(function(st){ return opt(st.id, st.id + "  " + st.who, false); }).join("");
      fs.addEventListener("change", function(){ setFilter("state", fs.value); });
    } else if(fsw){ fsw.className = "off"; }
    var fc = document.getElementById("fcomp");
    if(fc){
      fc.innerHTML = opt("all", "all screens", true) + opt("flagged", "flagged only", false) + reasonNames.map(function(r){ return opt(r, r, false); }).join("");
      fc.addEventListener("change", function(){ setFilter("comp", fc.value); });
    }
    var ft = document.getElementById("ftpl");
    if(ft){
      ft.innerHTML = opt("all", "all templates" + (TFZ ? ", " + TFZ.count + " " + TFZ.status + " since " + TFZ.since : ""), true) + templates.map(function(t){ return opt(t, t, false); }).join("");
      ft.addEventListener("change", function(){ setFilter("tpl", ft.value); });
    }
    var ff = document.getElementById("ffreeze");
    if(ff){
      ff.innerHTML = opt("all", "frozen and open", true) + opt("frozen", "frozen only", false) + opt("open", "open only", false);
      ff.addEventListener("change", function(){ setFilter("freeze", ff.value); });
    }

    var prev = document.getElementById("prev"); if(prev) prev.addEventListener("click", function(){ step(-1); });
    var next = document.getElementById("next"); if(next) next.addEventListener("click", function(){ step(1); });
    var mb = document.getElementById("mapbtn"); if(mb) mb.addEventListener("click", function(){ toggleMap(); });
    var ex = document.getElementById("export"); if(ex) ex.addEventListener("click", exportNotes);

    var rv = document.getElementById("reviewer");
    if(rv && LOCK){
      rv.innerHTML = opt(LOCK, LOCK, true); rv.disabled = true; store.who = LOCK; save();
    } else if(rv){
      rv.innerHTML = opt("", "reviewing as", !store.who) + IDENTITIES.map(function(n){ return opt(n, n, store.who === n); }).join("");
      rv.addEventListener("change", function(){ store.who = IDENTITIES.indexOf(rv.value) >= 0 ? rv.value : ""; save(); syncReason(); flash(store.who ? "Reviewing as " + store.who : ""); });
    }
    var rs = document.getElementById("reason");
    if(rs){
      rs.innerHTML = opt("", "reason category", true) + reasonNames.map(function(r){ return opt(r, r, false); }).join("");
      rs.addEventListener("change", function(){ var n = noteFor(SCREENS[state.idx].id); n.reason = reasonNames.indexOf(rs.value) >= 0 ? rs.value : ""; n.who = store.who; save(); saved(put(SCREENS[state.idx].id, "reason", n.reason, "field_edit")); });
    }

    var v = document.getElementById("verdict");
    if(v){
      v.innerHTML = VERDICTS.map(function(x){ return '<button data-v="'+x+'">'+x+'</button>'; }).join("");
      v.addEventListener("click", function(ev){ var b = ev.target.closest("button"); if(!b) return;
        var id = SCREENS[state.idx].id; var n = noteFor(id); n.verdict = (n.verdict === b.getAttribute("data-v")) ? "" : b.getAttribute("data-v"); n.who = store.who; save(); var ok = put(id, "verdict", n.verdict, "verdict"); renderSpec(); renderNav(); saved(ok); });
    }
    var ta = document.getElementById("comment"); var timer;
    if(ta) ta.addEventListener("input", function(){ var id = SCREENS[state.idx].id; var n = noteFor(id); n.text = ta.value; n.who = store.who; save();
      flash("Saving..."); clearTimeout(timer); timer = setTimeout(function(){ saved(put(id, "text", noteFor(id).text || "", "comment")); renderNav(); }, 1500); });
    if(BOARD){ BOARD.attach(ta, function(){ return SCREENS[state.idx].id; }); BOARD.init({page: PAGE, apply: applyRemote});
      if(INTEG.rows.length) BOARD.read({page: "integrations", apply: function(latest, rows, ok){ if(!ok) return; liveChoices = {};
        latest.forEach(function(r){ if(r.field === "choice" && (r.value === "final" || r.value === "open")) liveChoices[r.item_id] = r.value; }); renderSpec(); }}); }

    var sel = document.getElementById("jump");
    if(sel) sel.addEventListener("change", function(){ if(byId[sel.value] !== undefined) go(byId[sel.value]); });
    window.addEventListener("hashchange", function(){ var id = location.hash.replace("#", ""); if(byId[id] !== undefined){ if(state.map) toggleMap(false); ensureScope(byId[id]); go(byId[id]); } else if(dropped.indexOf(id) >= 0){ flash(id + " was dropped in v0.2; see the Changelog tab"); } else if(split.indexOf(id) >= 0){ flash(id + " was split into its instances in v0.2; see the Changelog tab"); } });
    document.addEventListener("keydown", function(ev){ if(ev.target.tagName === "TEXTAREA" || ev.target.tagName === "INPUT" || ev.target.tagName === "SELECT") return; if(ev.key === "ArrowRight") step(1); if(ev.key === "ArrowLeft") step(-1); });
    syncFilters();
    var start = location.hash.replace("#", "");
    if(byId[start] !== undefined){ ensureScope(byId[start]); go(byId[start]); }
    else { go(0); if(dropped.indexOf(start) >= 0) flash(start + " was dropped in v0.2; see the Changelog tab"); else if(split.indexOf(start) >= 0) flash(start + " was split into its instances in v0.2; see the Changelog tab"); }
  }
  document.addEventListener("DOMContentLoaded", init);

  // test hook for scripts/check_site.py (and for the console)
  window.yeslyfWire = {
    go: function(id){ if(byId[id] !== undefined){ ensureScope(byId[id]); go(byId[id]); } },
    step: step,
    setFilter: setFilter,
    walk: function(){ return walkList().map(function(i){ return SCREENS[i].id; }); },
    current: function(){ return SCREENS[state.idx].id; },
    exportText: exportText,
    filters: function(){ return {tiers:TIERS, paths:PATHS, comps:COMP_FILTER ? ["all","flagged"].concat(reasonNames) : [], templates:templates, states:states.map(function(st){ return st.id; }), freeze:document.getElementById("ffreeze") ? FREEZES : []}; },
    landing: function(id){ return stateById[id] ? stateById[id].lands_on : ""; }
  };
})();
