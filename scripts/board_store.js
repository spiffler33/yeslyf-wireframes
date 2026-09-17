// yeslyf board store: the shared save layer of every page (phase 11, Vatsal, 16 Sep 2026).
// Every comment, verdict and field edit on every page is one row in the Supabase table board_entries
// (page, item_id, field, value, who, kind, created_at); rows are never updated or deleted. docs/config.js, loaded
// in the head before this script, sets SUPABASE_URL and SUPABASE_ANON_KEY; both blank keeps the page local only.
// Each page keeps its own localStorage store as before (that is the offline cache). This layer adds one key,
// "yeslyf_entries_v1", holding per page the rows last fetched, the outbox (inserts that failed) and the last write.
// On load it sends the outbox, fetches the page's rows (1000 at a time), hands the latest value per item and
// field to the page (the apply callback; a queued local edit for the same field wins), and writes
// "live, last write <time>" or "offline, saved locally" into the top bar pill. The history toggle under a comment
// box lists every row of that item, newest first, queued rows on top.
// Requests carry the key in the apikey header only (the publishable key is not a JWT and is refused in
// Authorization; the legacy anon key works the same way in apikey alone).
// Phase 12 (Vatsal, 17 Sep 2026): write() refuses a row with no identity and returns false (the page says so in
// plain words; nothing is queued); rows in BOARD_IGNORE (data/board_ignore.json: page, item_id and the minute of
// created_at) are test rows and are dropped from every fetch, so counts, exports and history never see them;
// read({page, apply}) fetches another page's rows read-only (page "" is every page) for the pages that need them
// (the Integrations choice on the wireframes spec panel, the Tracker's question list and daily update); init({also})
// names pages whose rows are read into this page's cache as well (the Tracker reads the W rows written under
// page integrations before the move), so the latest value and the history are whole; writes stay on the page.
// Held edits (Vatsal, 17 Sep 2026): a write without a name is not refused into thin air. The row waits in this
// browser (the latest value per item and field), the pill says how many are waiting, and the moment the page picks
// a name (named(who)) they go out stamped with it. init({who, local}) does the same on load: local() returns the
// values the page shows ({item_id, field, value, kind}); any the table does not hold are sent too, so an edit typed
// before the name was picked, or before this rule existed, is recorded once there is a name. While edits wait, the
// page asks in words beside the name control ("Who is this? Pick your name to record your N edits.") until a name
// is picked; the ask is the store's own element and style, so every page gets it (Vatsal, 17 Sep 2026).
(function(){
  var CACHE_KEY = "yeslyf_entries_v1", PAGE_SIZE = 1000;
  var NAME_TEXT = "Held until you pick your name at the top; recorded then.";
  var ALL = {}, loaded = false;  // the latest value per item and field over every row fetched on load, test rows included
  var MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  var FIELDS = "id,page,item_id,field,value,who,kind,created_at";
  var IGNORE = (typeof BOARD_IGNORE !== "undefined" && BOARD_IGNORE) ? BOARD_IGNORE : [];
  function cfg(name){ try { var v = window[name]; return typeof v === "string" ? v.trim() : ""; } catch(e){ return ""; } }
  var url = cfg("SUPABASE_URL"); while(url.length && url.charAt(url.length - 1) === "/") url = url.slice(0, -1);
  var key = cfg("SUPABASE_ANON_KEY");
  var configured = !!(url && key);
  var cache = {};
  try { cache = JSON.parse(localStorage.getItem(CACHE_KEY) || "{}") || {}; } catch(e){ cache = {}; }
  function saveCache(){ try { localStorage.setItem(CACHE_KEY, JSON.stringify(cache)); } catch(e){} }
  var page = "", also = [], applyFn = null, localFn = null, WHO = "", live = false, checked = false, lastWrite = "", boxes = [];
  function pc(){ if(!cache[page]) cache[page] = {}; var c = cache[page]; if(!c.rows) c.rows = []; if(!c.outbox) c.outbox = []; if(!c.last_write) c.last_write = ""; if(!c.held) c.held = []; return c; }
  function esc(s){ return String(s === undefined || s === null ? "" : s).split("&").join("&amp;").split("<").join("&lt;").split(">").join("&gt;").split('"').join("&quot;"); }
  function two(n){ return (n < 10 ? "0" : "") + n; }
  function fmt(ts){
    // created_at arrives as UTC from the database and as toISOString() from the outbox; the first 19 characters are
    // the same shape in both, so the display never depends on how a browser parses fractional seconds or offsets.
    var d = new Date(String(ts || "").slice(0, 19) + "Z");
    if(isNaN(d.getTime())) return String(ts || "");
    return d.getDate() + " " + MONTHS[d.getMonth()] + " " + two(d.getHours()) + ":" + two(d.getMinutes());
  }
  function ignored(r){
    // a test row: same page and item, written in the minute the ignore list names (data/board_ignore.json)
    var minute = String(r.created_at || "").slice(0, 16);
    for(var i = 0; i < IGNORE.length; i++){ var g = IGNORE[i]; if(g.page === r.page && g.item_id === r.item_id && g.minute === minute) return true; }
    return false;
  }
  function keep(rows){ var out = []; for(var i = 0; i < rows.length; i++) if(!ignored(rows[i])) out.push(rows[i]); return out; }
  function control(){ return document.getElementById("reviewer") || document.getElementById("who"); }
  var styled = false;
  function askStyle(){
    if(styled || !document.head || !document.head.appendChild) return; styled = true;
    var st = document.createElement("style");
    st.textContent = ".askname-note{font-weight:700;color:#1B1F27;background:#FFF4B8;border:1px solid #C9A800;border-radius:6px;padding:4px 8px;font-size:12px;line-height:1.3}" +
                     "select.askname,input.askname{border:2px solid #1B1F27 !important}";
    document.head.appendChild(st);
  }
  function ask(held){
    // The ask beside the name control while edits wait for a name: words that stay, not a flash.
    var c = control(); if(!c || !c.parentNode) return;
    var el = document.getElementById("askname");
    if(!held){ if(el && el.parentNode) el.parentNode.removeChild(el); if(c.classList) c.classList.remove("askname"); return; }
    if(!el || !el.parentNode){ el = document.createElement("span"); el.id = "askname"; el.className = "askname-note"; c.parentNode.insertBefore(el, c.nextSibling); askStyle(); }
    el.textContent = "Who is this? Pick your name to record your " + (held === 1 ? "edit." : held + " edits.");
    if(c.classList) c.classList.add("askname");
  }
  function pill(){
    var held = page ? pc().held.length : 0;
    ask(held);
    var p = document.getElementById("sheetpill"); if(!p) return;
    var text, title, on = false;
    if(held){ text = held + (held === 1 ? " edit" : " edits") + " waiting for a name"; title = NAME_TEXT; }
    else if(!configured){ text = "offline, saved locally"; title = "docs/config.js has no Supabase URL and key: edits stay in this browser"; }
    else if(!checked){ text = "connecting"; title = "reading board_entries"; }
    else if(live){ text = "live" + (lastWrite ? ", last write " + fmt(lastWrite) : ""); title = "every edit is a row in board_entries; the time is the last write on this page by anyone"; on = true; }
    else { text = "offline, saved locally"; title = "the last request to Supabase failed: edits stay in this browser and are sent on the next load"; }
    p.textContent = text; p.title = title; p.className = "pill" + (on ? " on" : "") + (held ? " held" : "");
  }
  function strip(r){ return {page: r.page, item_id: r.item_id, field: r.field, value: r.value, who: r.who, kind: r.kind}; }
  function request(method, query, body, cb){
    // cb(status, json) exactly once; status is "ok", "rejected" (the server answered with an error) or "net".
    var done = false;
    function finish(s, j){ if(done) return; done = true; try { cb(s, j); } catch(e){} }
    var headers = {"apikey": key};
    if(body !== undefined){ headers["Content-Type"] = "application/json"; headers["Prefer"] = "return=representation"; }
    var p;
    try { p = fetch(url + "/rest/v1/board_entries" + query, {method: method, headers: headers, body: body === undefined ? undefined : JSON.stringify(body)}); }
    catch(e){ finish("net"); return; }
    Promise.resolve(p).then(function(res){
      if(!res || typeof res.ok !== "boolean") throw new Error("no response");
      if(!res.ok){ finish("rejected", res.status); return; }
      return res.json().then(function(j){ finish("ok", j); });
    }).catch(function(){ finish("net"); });
  }
  function remember(j){
    var r = (j && typeof j.length === "number" && j.length) ? j[0] : null; if(!r || !r.created_at) return;
    var c = pc(); c.rows.push(r); c.last_write = r.created_at; lastWrite = c.last_write;
  }
  function flush(cb){
    // Send every queued row in order; a row that fails stays queued; the caller learns whether all went through.
    var c = pc(); var queue = c.outbox.slice(); var i = 0; var failed = 0;
    (function next(){
      if(i >= queue.length){ saveCache(); cb(failed === 0); return; }
      var row = queue[i++];
      request("POST", "", strip(row), function(s, j){
        if(s === "ok"){ var at = c.outbox.indexOf(row); if(at >= 0) c.outbox.splice(at, 1); remember(j); } else failed++;
        next();
      });
    })();
  }
  function fetchRows(pageName, offset, acc, cb, all){
    // every row of one page (or of every page when pageName is ""), 1000 at a time, in id order; test rows dropped
    // (all, when given, still records the latest value per item and field over every row, test rows included:
    // the sync compares against it, so a local copy of a test row is never re-sent as a real one; 17 Sep 2026)
    var filter = pageName ? "&page=eq." + encodeURIComponent(pageName) : "";
    request("GET", "?select=" + FIELDS + filter + "&order=id.asc&limit=" + PAGE_SIZE + "&offset=" + offset, undefined, function(s, rows){
      if(s !== "ok" || !rows || typeof rows.length !== "number"){ cb(false); return; }
      if(all) rows.forEach(function(r){ var k = r.item_id + "|" + r.field; if(!all[k] || r.id > all[k].id) all[k] = {id: r.id, value: String(r.value === undefined || r.value === null ? "" : r.value)}; });
      acc = acc.concat(keep(rows));
      if(rows.length < PAGE_SIZE) cb(true, acc); else fetchRows(pageName, offset + PAGE_SIZE, acc, cb, all);
    });
  }
  function latestOf(rows){ var latest = {}; rows.forEach(function(r){ latest[r.item_id + "|" + r.field] = r; }); var out = []; for(var k in latest) out.push(latest[k]); return out; }
  function fetchPages(names, acc, cb){
    // the rows of several pages, merged in id order (ids grow with time, so the latest row per field is the last one)
    if(!names.length){ acc.sort(function(a, b){ return a.id - b.id; }); cb(true, acc); return; }
    fetchRows(names[0], 0, [], function(ok, rows){ if(!ok){ cb(false); return; } fetchPages(names.slice(1), acc.concat(rows), cb); }, ALL);
  }
  function load(){
    pill();
    if(!configured || !page) return;
    ALL = {}; loaded = false;
    flush(function(sent){
      fetchPages([page].concat(also), [], function(ok, rows){
        checked = true; var c = pc();
        if(ok){
          loaded = true;
          var own = rows.filter(function(r){ return r.page === page; });
          c.rows = rows; c.last_write = own.length ? own[own.length - 1].created_at : ""; lastWrite = c.last_write; saveCache();
          if(applyFn){
            var pending = {}; c.outbox.forEach(function(r){ pending[r.item_id + "|" + r.field] = 1; });
            var out = latestOf(rows).filter(function(r){ return !pending[r.item_id + "|" + r.field]; });
            try { applyFn(out); } catch(e){}
          }
        }
        live = ok && sent && !c.outbox.length; pill(); refreshHistory();
        if(ok && WHO) sync(WHO);
      });
    });
  }
  function read(opts){
    // Read-only: the rows of another page (or of every page when opts.page is ""); apply(latest, rows) once they arrive.
    opts = opts || {};
    if(!configured){ try { opts.apply([], [], false); } catch(e){} return; }
    fetchRows(String(opts.page || ""), 0, [], function(ok, rows){
      rows = ok ? rows : [];
      try { opts.apply(latestOf(rows), rows, ok); } catch(e){}
    });
  }
  function write(row){
    // row: {item_id, field, value, who, kind}. Without a name the row is held (false: not recorded yet); every row
    // names who wrote it (Vatsal, 17 Sep 2026) and the held rows go out through named(). With a name it is queued
    // first, removed on success, so a tab closed mid-request sends the row on the next load (a duplicate row is
    // harmless: same latest value).
    if(!page) return false;
    var who = String(row.who || "").trim();
    var r = {page: page, item_id: String(row.item_id), field: String(row.field),
             value: String(row.value === undefined || row.value === null ? "" : row.value),
             who: who, kind: String(row.kind || "field_edit"), created_at: new Date().toISOString(), queued: true};
    if(!who){ hold(r); return false; }
    if(!configured){ pill(); return true; }
    var c = pc(); c.outbox.push(r); saveCache();
    request("POST", "", strip(r), function(s, j){
      var at = c.outbox.indexOf(r);
      if(s === "ok"){ if(at >= 0) c.outbox.splice(at, 1); remember(j); live = true; } else live = false;
      checked = true; saveCache(); pill(); refreshHistory();
    });
    return true;
  }
  function hold(r){
    // the latest value per item and field waits here, in first-edit order, until the page picks a name
    var c = pc(); r.held = true;
    for(var i = 0; i < c.held.length; i++){ if(c.held[i].item_id === r.item_id && c.held[i].field === r.field){ c.held[i] = r; saveCache(); pill(); refreshHistory(); return; } }
    c.held.push(r); saveCache(); pill(); refreshHistory();
  }
  function latestValue(item_id, field){
    // the table's latest value for one field over every row fetched on load (this page and the pages read with it,
    // test rows included), or null when the table has none
    var e = ALL[item_id + "|" + field]; return e ? e.value : null;
  }
  function sync(who){
    // The page has a name: the held rows are stamped with it and sent, then, once the table has been read, every
    // value the page shows that the table does not hold (local() minus the latest row per field) goes out as well.
    // Returns how many were sent.
    who = String(who || "").trim(); if(!page || !who) return 0;
    var c = pc(), now = new Date().toISOString(), out = [], seen = {};
    c.held.forEach(function(r){ r.who = who; r.created_at = now; delete r.held; out.push(r); seen[r.item_id + "|" + r.field] = 1; });
    c.held = [];
    c.outbox.forEach(function(r){ seen[r.item_id + "|" + r.field] = 1; });
    var local = []; try { local = (loaded && localFn) ? (localFn() || []) : []; } catch(e){ local = []; }
    local.forEach(function(e){
      var item = String(e.item_id), field = String(e.field), value = String(e.value === undefined || e.value === null ? "" : e.value);
      if(seen[item + "|" + field]) return;
      var remote = latestValue(item, field);
      if(remote === null ? value === "" : remote === value) return;
      out.push({page: page, item_id: item, field: field, value: value, who: who, kind: String(e.kind || "field_edit"), created_at: now, queued: true});
    });
    if(!out.length){ saveCache(); pill(); return 0; }
    if(!configured){ saveCache(); pill(); return out.length; }
    out.forEach(function(r){ c.outbox.push(r); }); saveCache(); pill();
    flush(function(sent){ checked = true; live = sent; pill(); refreshHistory(); });
    return out.length;
  }
  function named(who){ WHO = String(who || "").trim(); return sync(WHO); }
  function history(item_id){
    var c = pc(); item_id = String(item_id);
    var held = c.held.filter(function(r){ return r.item_id === item_id; }).slice().reverse();
    var queued = c.outbox.filter(function(r){ return r.item_id === item_id; }).slice().reverse();
    var rows = c.rows.filter(function(r){ return r.item_id === item_id; }).slice().reverse();
    return held.concat(queued, rows);
  }
  function historyHtml(item_id){
    if(!configured) return '<div class="hist-empty">local only: docs/config.js has no Supabase URL and key</div>';
    var rows = history(item_id);
    if(!rows.length) return '<div class="hist-empty">' + (checked ? "no rows yet for " + esc(item_id) : "not loaded yet") + '</div>';
    return '<ul class="hist">' + rows.map(function(r){
      return '<li><span class="t">' + esc(fmt(r.created_at)) + '</span> <b>' + esc(r.who || (r.held ? "(no name yet)" : "(no identity)")) + '</b> ' + esc(r.field) + ': ' +
             (r.value ? esc(r.value) : '<i>cleared</i>') + (r.held ? ' <i>waiting for a name</i>' : r.queued ? ' <i>queued, not sent yet</i>' : '') + '</li>';
    }).join("") + '</ul>';
  }
  function refreshHistory(){ boxes.forEach(function(b){ if(!b.box.hidden) b.box.innerHTML = historyHtml(b.id()); }); }
  function attach(el, idFn){
    // Adds a "History" toggle right after a control; idFn is the item id or a function returning it.
    if(!el || !el.parentNode) return;
    var id = typeof idFn === "function" ? idFn : function(){ return idFn; };
    var wrap = document.createElement("div"); wrap.className = "histwrap"; wrap.style.gridColumn = "1 / -1";  // a full row inside a grid form
    var b = document.createElement("button"); b.type = "button"; b.className = "hist-toggle"; b.textContent = "History";
    var box = document.createElement("div"); box.className = "histbox"; box.hidden = true;
    b.addEventListener("click", function(){ box.hidden = !box.hidden; if(!box.hidden) box.innerHTML = historyHtml(id()); });
    wrap.appendChild(b); wrap.appendChild(box);
    el.parentNode.insertBefore(wrap, el.nextSibling);
    boxes.push({box: box, id: id});
  }
  function init(opts){ opts = opts || {}; page = String(opts.page || ""); also = (opts.also || []).map(String).filter(function(p){ return p && p !== page; }); applyFn = opts.apply || null; localFn = opts.local || null; WHO = String(opts.who || "").trim(); load(); }
  function status(){ return {configured: configured, live: live, checked: checked, last_write: lastWrite, queued: page ? pc().outbox.length : 0, held: page ? pc().held.length : 0}; }
  function label(){ return configured && live ? "live (board_entries)" : "offline; this file is the record"; }
  window.yeslyfBoard = {init: init, write: write, named: named, read: read, history: history, attach: attach, refreshHistory: refreshHistory, status: status, label: label, fmt: fmt,
                        noIdentity: NAME_TEXT};
})();
