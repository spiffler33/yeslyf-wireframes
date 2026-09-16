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
(function(){
  var CACHE_KEY = "yeslyf_entries_v1", PAGE_SIZE = 1000;
  var MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  var FIELDS = "id,item_id,field,value,who,kind,created_at";
  function cfg(name){ try { var v = window[name]; return typeof v === "string" ? v.trim() : ""; } catch(e){ return ""; } }
  var url = cfg("SUPABASE_URL"); while(url.length && url.charAt(url.length - 1) === "/") url = url.slice(0, -1);
  var key = cfg("SUPABASE_ANON_KEY");
  var configured = !!(url && key);
  var cache = {};
  try { cache = JSON.parse(localStorage.getItem(CACHE_KEY) || "{}") || {}; } catch(e){ cache = {}; }
  function saveCache(){ try { localStorage.setItem(CACHE_KEY, JSON.stringify(cache)); } catch(e){} }
  var page = "", applyFn = null, live = false, checked = false, lastWrite = "", boxes = [];
  function pc(){ if(!cache[page]) cache[page] = {}; var c = cache[page]; if(!c.rows) c.rows = []; if(!c.outbox) c.outbox = []; if(!c.last_write) c.last_write = ""; return c; }
  function esc(s){ return String(s === undefined || s === null ? "" : s).split("&").join("&amp;").split("<").join("&lt;").split(">").join("&gt;").split('"').join("&quot;"); }
  function two(n){ return (n < 10 ? "0" : "") + n; }
  function fmt(ts){
    // created_at arrives as UTC from the database and as toISOString() from the outbox; the first 19 characters are
    // the same shape in both, so the display never depends on how a browser parses fractional seconds or offsets.
    var d = new Date(String(ts || "").slice(0, 19) + "Z");
    if(isNaN(d.getTime())) return String(ts || "");
    return d.getDate() + " " + MONTHS[d.getMonth()] + " " + two(d.getHours()) + ":" + two(d.getMinutes());
  }
  function pill(){
    var p = document.getElementById("sheetpill"); if(!p) return;
    var text, title, on = false;
    if(!configured){ text = "offline, saved locally"; title = "docs/config.js has no Supabase URL and key: edits stay in this browser"; }
    else if(!checked){ text = "connecting"; title = "reading board_entries"; }
    else if(live){ text = "live" + (lastWrite ? ", last write " + fmt(lastWrite) : ""); title = "every edit is a row in board_entries; the time is the last write on this page by anyone"; on = true; }
    else { text = "offline, saved locally"; title = "the last request to Supabase failed: edits stay in this browser and are sent on the next load"; }
    p.textContent = text; p.title = title; p.className = "pill" + (on ? " on" : "");
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
  function fetchAll(offset, acc, cb){
    request("GET", "?select=" + FIELDS + "&page=eq." + encodeURIComponent(page) + "&order=id.asc&limit=" + PAGE_SIZE + "&offset=" + offset, undefined, function(s, rows){
      if(s !== "ok" || !rows || typeof rows.length !== "number"){ cb(false); return; }
      acc = acc.concat(rows);
      if(rows.length < PAGE_SIZE) cb(true, acc); else fetchAll(offset + PAGE_SIZE, acc, cb);
    });
  }
  function load(){
    pill();
    if(!configured || !page) return;
    flush(function(sent){
      fetchAll(0, [], function(ok, rows){
        checked = true; var c = pc();
        if(ok){
          c.rows = rows; c.last_write = rows.length ? rows[rows.length - 1].created_at : ""; lastWrite = c.last_write; saveCache();
          if(applyFn){
            var latest = {}; rows.forEach(function(r){ latest[r.item_id + "|" + r.field] = r; });
            var pending = {}; c.outbox.forEach(function(r){ pending[r.item_id + "|" + r.field] = 1; });
            var out = []; for(var k in latest) if(!pending[k]) out.push(latest[k]);
            try { applyFn(out); } catch(e){}
          }
        }
        live = ok && sent && !c.outbox.length; pill(); refreshHistory();
      });
    });
  }
  function write(row){
    // row: {item_id, field, value, who, kind}. Queued first, removed on success, so a tab closed mid-request
    // sends the row on the next load (a duplicate row is harmless: same latest value).
    if(!page) return;
    var r = {page: page, item_id: String(row.item_id), field: String(row.field),
             value: String(row.value === undefined || row.value === null ? "" : row.value),
             who: String(row.who || ""), kind: String(row.kind || "field_edit"), created_at: new Date().toISOString(), queued: true};
    if(!configured){ pill(); return; }
    var c = pc(); c.outbox.push(r); saveCache();
    request("POST", "", strip(r), function(s, j){
      var at = c.outbox.indexOf(r);
      if(s === "ok"){ if(at >= 0) c.outbox.splice(at, 1); remember(j); live = true; } else live = false;
      checked = true; saveCache(); pill(); refreshHistory();
    });
  }
  function history(item_id){
    var c = pc(); item_id = String(item_id);
    var queued = c.outbox.filter(function(r){ return r.item_id === item_id; }).slice().reverse();
    var rows = c.rows.filter(function(r){ return r.item_id === item_id; }).slice().reverse();
    return queued.concat(rows);
  }
  function historyHtml(item_id){
    if(!configured) return '<div class="hist-empty">local only: docs/config.js has no Supabase URL and key</div>';
    var rows = history(item_id);
    if(!rows.length) return '<div class="hist-empty">' + (checked ? "no rows yet for " + esc(item_id) : "not loaded yet") + '</div>';
    return '<ul class="hist">' + rows.map(function(r){
      return '<li><span class="t">' + esc(fmt(r.created_at)) + '</span> <b>' + esc(r.who || "-") + '</b> ' + esc(r.field) + ': ' +
             (r.value ? esc(r.value) : '<i>cleared</i>') + (r.queued ? ' <i>queued, not sent yet</i>' : '') + '</li>';
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
  function init(opts){ opts = opts || {}; page = String(opts.page || ""); applyFn = opts.apply || null; load(); }
  function status(){ return {configured: configured, live: live, checked: checked, last_write: lastWrite, queued: page ? pc().outbox.length : 0}; }
  function label(){ return configured && live ? "live (board_entries)" : "offline; this file is the record"; }
  window.yeslyfBoard = {init: init, write: write, history: history, attach: attach, refreshHistory: refreshHistory, status: status, label: label};
})();
