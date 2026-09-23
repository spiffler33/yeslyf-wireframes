// yeslyf admin wireframes: the API the per-screen drawing files build on (phase C part 1, 23 Sep 2026).
// Loaded by scripts/build_admin_wireframes.py after renderer_v02.js and before the ADMIN_SCREEN_FILES
// (admin_screens_1.js, _2.js, _3.js). Depends on the data blob (SECTIONS, SCREENS, WIRE_OPTS, ADMIN_RUNS,
// ADMIN_STATES, ADMIN_PLACEMENT, INTEGRATIONS) and on renderer_v02.js's WIRE_OPTS-reading hooks: this file only
// ADDS properties onto the same WIRE_OPTS object the data blob already declared (drawScreen, specTop) and never
// calls yeslyfBoard.write itself; the renderer's own comment controls are the only thing that writes board rows.
//
// Screen files register a draw function per screen: ADMIN.draw.M02 = function(body, s){ ... };  body is the
// frame's .frame-body element to fill, s is the screen record from data/admin_screens.json (SCREENS).
(function(){
  var UI_KEY = "yeslyf_admin_wire_v01_ui";
  var MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  var loaded = false;          // true once the current run's meta/people/tables/ievents have arrived
  var pidIndex = {};           // person_id -> index in ADMIN.people (which chunk it lives in)
  var chunkCache = {};         // "run:idx" -> Promise<chunk file contents>

  function esc(s){ return String(s === undefined || s === null ? "" : s).split("&").join("&amp;").split("<").join("&lt;").split(">").join("&gt;").split('"').join("&quot;"); }
  function two(n){ return (n < 10 ? "0" : "") + n; }
  function fetchJSON(url){
    return fetch(url).then(function(r){
      if(!r || !r.ok) throw new Error("fetch failed: " + url);
      return r.json();
    });
  }

  // ---------------------------------------------------------------- ADMIN.h: small render helpers
  function numIN(n){
    if(n === null || n === undefined || isNaN(n)) return "";
    var neg = n < 0; n = Math.round(Math.abs(n));
    var s = String(n);
    if(s.length <= 3) return (neg ? "-" : "") + s;
    var last3 = s.slice(-3), rest = s.slice(0, -3), parts = [];
    while(rest.length > 2){ parts.unshift(rest.slice(-2)); rest = rest.slice(0, -2); }
    if(rest.length) parts.unshift(rest);
    return (neg ? "-" : "") + parts.join(",") + "," + last3;
  }
  function localDate(iso){
    // same trick as board_store.js: take the clock-face time as written (first 19 chars), read it back as if it
    // were UTC and format it with the UTC getters, so the display never shifts with the viewer's own timezone.
    if(!iso) return null;
    var d = new Date(String(iso).slice(0, 19) + "Z");
    return isNaN(d.getTime()) ? null : d;
  }
  function dateStr(iso){
    var d = localDate(iso);
    return d ? (d.getUTCDate() + " " + MONTHS[d.getUTCMonth()] + " " + d.getUTCFullYear()) : "";
  }
  function whenStr(iso){
    var d = localDate(iso);
    return d ? (dateStr(iso) + ", " + two(d.getUTCHours()) + ":" + two(d.getUTCMinutes())) : "";
  }
  function pct(a, b){
    if(!b) return "0%";
    return Math.round((a / b) * 100) + "%";
  }
  var H = {
    esc: esc,
    table: function(headers, rows, opts){
      opts = opts || {};
      var head = "<thead><tr>" + headers.map(function(h){ return "<th>" + esc(h) + "</th>"; }).join("") + "</tr></thead>";
      var body = "<tbody>" + rows.map(function(r){ return "<tr>" + r.map(function(c){ return "<td>" + c + "</td>"; }).join("") + "</tr>"; }).join("") + "</tbody>";
      return '<div class="w-table-wide"><table class="w-table' + (opts.cls ? " " + esc(opts.cls) : "") + '">' + head + body + "</table></div>";
    },
    rows: function(pairs){
      return '<div class="w-rows">' + pairs.map(function(p){ return '<div class="w-row"><span>' + esc(p[0]) + "</span><b>" + (p[1] === undefined || p[1] === null ? "" : p[1]) + "</b></div>"; }).join("") + "</div>";
    },
    badge: function(text, kind){
      return '<span class="w-badge' + (kind ? " " + esc(kind) : "") + '">' + esc(text) + "</span>";
    },
    mock: function(label, event){
      return '<button type="button" class="w-btn2" data-mock="1" data-label="' + esc(label) + '" data-event="' + esc(event || "") + '">' + esc(label) + "</button>";
    },
    date: dateStr,
    when: whenStr,
    num: numIN,
    pct: pct,
    link: function(label, screenId, opts){
      opts = opts || {};
      var attrs = ' data-open="1" data-screen="' + esc(screenId) + '"';
      if(opts.person) attrs += ' data-person="' + esc(opts.person) + '"';
      if(opts.filter) attrs += ' data-filter="' + esc(opts.filter) + '"';
      return '<a href="#" class="w-link"' + attrs + ">" + esc(label) + "</a>";
    }
  };

  // ---------------------------------------------------------------- the API object
  var ADMIN = {
    run: "3000", ready: Promise.resolve(), meta: null, people: [], byId: {}, t: {}, ievents: {},
    states: (typeof ADMIN_STATES !== "undefined" && ADMIN_STATES) ? ADMIN_STATES : [],
    statesById: {}, placement: (typeof ADMIN_PLACEMENT !== "undefined" && ADMIN_PLACEMENT) ? ADMIN_PLACEMENT : [],
    anchor: null, current: "", nav: {}, draw: {}, h: H
  };
  ADMIN.states.forEach(function(st){ ADMIN.statesById[st.id] = st; });

  ADMIN.days = function(iso){
    if(!ADMIN.anchor || !iso) return null;
    var d = new Date(String(iso));
    if(isNaN(d.getTime())) return null;
    return Math.floor((ADMIN.anchor.getTime() - d.getTime()) / 86400000);
  };

  function runsMap(){ return (typeof ADMIN_RUNS !== "undefined" && ADMIN_RUNS) ? ADMIN_RUNS : {}; }

  function saveUI(){
    try { localStorage.setItem(UI_KEY, JSON.stringify({run: ADMIN.run, person: ADMIN.current || ""})); } catch(e){}
  }
  function readUI(){
    try { return JSON.parse(localStorage.getItem(UI_KEY) || "{}") || {}; } catch(e){ return {}; }
  }

  ADMIN.load = function(run){
    run = runsMap()[run] ? run : "3000";
    ADMIN.run = run;
    loaded = false;
    saveUI();
    var base = runsMap()[run];
    var p = Promise.all([
      fetchJSON(base + "meta.json"),
      fetchJSON(base + "people.json"),
      fetchJSON(base + "tables.json"),
      fetchJSON(base + "integration_events.json")
    ]).then(function(res){
      ADMIN.meta = res[0]; ADMIN.people = res[1]; ADMIN.t = res[2]; ADMIN.ievents = res[3];
      ADMIN.byId = {}; pidIndex = {};
      ADMIN.people.forEach(function(person, i){ ADMIN.byId[person.person_id] = person; pidIndex[person.person_id] = i; });
      ADMIN.anchor = new Date(ADMIN.meta.anchor);
      loaded = true;
    });
    ADMIN.ready = p;
    return p;
  };

  ADMIN.detail = function(pid){
    var i = pidIndex[pid];
    if(i === undefined) return Promise.reject(new Error("unknown person " + pid));
    var chunkSize = (ADMIN.meta && ADMIN.meta.chunk_size) || 100;
    var idx = Math.floor(i / chunkSize);
    var name = String(idx); while(name.length < 4) name = "0" + name;
    var key = ADMIN.run + ":" + name;
    if(!chunkCache[key]) chunkCache[key] = fetchJSON(runsMap()[ADMIN.run] + "person/" + name + ".json");
    return chunkCache[key].then(function(chunk){ return chunk[pid]; });
  };

  function personLabel(pid){
    var p = ADMIN.byId[pid];
    if(!p) return pid;
    return pid + " " + (p.first_name || "") + (p.last_name ? " " + p.last_name : "");
  }

  ADMIN.select = function(pid){
    ADMIN.current = pid;
    saveUI();
    var input = document.getElementById("aperson");
    if(input) input.value = personLabel(pid);
    if(window.yeslyfWire){
      var cur = window.yeslyfWire.current();
      if(cur === "M03" || cur === "M04") window.yeslyfWire.go(cur);
    }
  };

  ADMIN.open = function(screenId, opts){
    ADMIN.nav = opts || {};
    if(opts && opts.person) ADMIN.select(opts.person);
    if(window.yeslyfWire) window.yeslyfWire.go(screenId);
  };

  ADMIN.integ = function(id){
    var rows = (typeof INTEGRATIONS !== "undefined" && INTEGRATIONS && INTEGRATIONS.rows) ? INTEGRATIONS.rows : [];
    for(var i = 0; i < rows.length; i++) if(rows[i].id === id) return id + " " + rows[i].vendor;
    return id;
  };
  ADMIN.staffName = function(id){
    var list = (ADMIN.t && ADMIN.t.staff) || [];
    for(var i = 0; i < list.length; i++) if(list[i].staff_id === id) return list[i].name;
    return id || "";
  };
  ADMIN.flash = function(text){
    var el = document.getElementById("saved");
    if(el) el.textContent = text || "";
  };

  // ---------------------------------------------------------------- renderer hooks
  function replaceTokens(text){
    var out = String(text || "");
    var rows = (typeof INTEGRATIONS !== "undefined" && INTEGRATIONS && INTEGRATIONS.rows) ? INTEGRATIONS.rows : [];
    rows.forEach(function(r){
      out = out.split("{" + r.id + "}").join(ADMIN.integ(r.id));
    });
    return out;
  }

  // WIRE_OPTS is declared by the data blob before this script runs (site.js_blob(wire_opts) in
  // build_admin_wireframes.py); renderer_v02.js already captured that same object as OPTS by reference, so
  // mutating it here (not redeclaring it, which would shadow it as a function-scoped local) is what makes the
  // renderer's OPTS.specTop / OPTS.drawScreen calls reach these functions.
  WIRE_OPTS.specTop = function(s){
    if(!s || !s.role) return "";
    var roleParts = [];
    for(var k in s.role){ if(Object.prototype.hasOwnProperty.call(s.role, k)) roleParts.push(k + ": " + s.role[k]); }
    var writes = s.writes || [];
    var writeParts = writes.map(function(w){ return w.action + " (" + w.roles.join(", ") + ")"; });
    var vendorLabel = ADMIN.integ("I14") + " instead?";
    return '<div class="spec-block a-top"><div class="spec-t">Seat and actions</div>' +
      '<div class="a-line"><b>Seat</b> ' + esc((s.seat || []).join(", ")) + '</div>' +
      '<div class="a-line"><b>Role</b> ' + esc(roleParts.join("; ")) + '</div>' +
      '<div class="a-line"><b>Built, not bought</b></div>' +
      '<div class="a-line"><b>Write actions (mock)</b> ' + (writeParts.length ? esc(writeParts.join("; ")) : "none") + '</div>' +
      '<div class="a-line"><b>' + esc(vendorLabel) + '</b> ' + esc(replaceTokens(s.zoho_instead)) + '</div>' +
      '</div>';
  };

  function wireFrame(frame){
    if(frame._adminWired) return;
    frame._adminWired = true;
    frame.addEventListener("click", function(ev){
      var t = ev.target;
      var openEl = t.closest ? t.closest("[data-open]") : null;
      if(openEl){
        ev.preventDefault();
        ADMIN.open(openEl.getAttribute("data-screen"), {
          person: openEl.getAttribute("data-person") || undefined,
          filter: openEl.getAttribute("data-filter") || undefined
        });
        return;
      }
      var mockEl = t.closest ? t.closest("[data-mock]") : null;
      if(mockEl){
        ev.preventDefault();
        ADMIN.flash("Mock: " + (mockEl.getAttribute("data-label") || mockEl.textContent) + " is not written anywhere");
        return;
      }
      var personEl = t.closest ? t.closest("[data-person]") : null;
      if(personEl){
        ev.preventDefault();
        ADMIN.select(personEl.getAttribute("data-person"));
      }
    });
  }

  WIRE_OPTS.drawScreen = function(s, frame){
    var body = frame.querySelector(".frame-body");
    if(!body) return;
    wireFrame(frame);
    var fn = ADMIN.draw[s.id];
    if(!fn) return; // no draw function registered yet (the static "Loading the seed..." fallback stays up)
    if(!loaded){
      body.innerHTML = '<div class="w-note">Loading the seed, run ' + esc(ADMIN.run) + '...</div>';
      ADMIN.ready.then(function(){
        if(window.yeslyfWire && window.yeslyfWire.current() === s.id){
          var freshBody = frame.querySelector(".frame-body");
          if(freshBody) ADMIN.draw[s.id](freshBody, s);
        }
      });
      return;
    }
    fn(body, s);
  };

  // ---------------------------------------------------------------- default person and deep links
  function defaultPerson(){
    var list = ADMIN.people || [];
    var i;
    for(i = 0; i < list.length; i++){
      var p = list[i];
      if((p.tier === "diy" || p.tier === "diwm") && p.state_id === "S9") return p.person_id;
    }
    for(i = 0; i < list.length; i++){
      if(list[i].tier === "diy" || list[i].tier === "diwm") return list[i].person_id;
    }
    return list.length ? list[0].person_id : "";
  }

  var params = new URLSearchParams(location.search);
  var qRun = params.get("run");
  var qScreen = params.get("screen");
  var qPerson = params.get("person");
  var savedUI = readUI();
  var startRun = (qRun === "500" || qRun === "3000") ? qRun : (runsMap()[savedUI.run] ? savedUI.run : "3000");
  if(qScreen){
    try { history.replaceState(null, "", location.pathname + location.search + "#" + qScreen); }
    catch(e){ location.hash = qScreen; }
  }
  ADMIN.load(startRun).then(function(){
    var pid = qPerson || (pidIndex[savedUI.person] !== undefined ? savedUI.person : "") || defaultPerson();
    if(pid) ADMIN.select(pid);
  });

  // ---------------------------------------------------------------- page chrome: run select, person input
  document.addEventListener("DOMContentLoaded", function(){
    var runSel = document.getElementById("arun");
    if(runSel){
      runSel.value = startRun;
      runSel.addEventListener("change", function(){
        ADMIN.load(runSel.value).then(function(){
          fillPeopleList();
          // keep the same person selected across the run switch when that id still exists in the new run;
          // only fall back to the default person when it does not (the two runs have different head counts).
          var pid = ADMIN.byId[ADMIN.current] ? ADMIN.current : defaultPerson();
          if(pid) ADMIN.select(pid);
          var cur = window.yeslyfWire ? window.yeslyfWire.current() : "";
          if(cur && window.yeslyfWire) window.yeslyfWire.go(cur);
        });
      });
    }
    var input = document.getElementById("aperson");
    if(input){
      input.addEventListener("change", function(){
        var v = input.value || "";
        var pid = v.split(" ")[0];
        if(ADMIN.byId[pid]) ADMIN.select(pid);
      });
    }
    ADMIN.ready.then(fillPeopleList);
  });

  function fillPeopleList(){
    var list = document.getElementById("apeople");
    if(!list) return;
    var html = "";
    (ADMIN.people || []).forEach(function(p){
      html += '<option value="' + esc(personLabel(p.person_id)) + '"></option>';
    });
    list.innerHTML = html;
  }

  window.ADMIN = ADMIN;
})();
