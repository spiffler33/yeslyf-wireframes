// Intro deck for Spinach (phase 10a, Vatsal, 15 Sep 2026). Embedded by scripts/build_intro.py into docs/intro.html and
// docs/audiences/yeslyf_intro_spinach.html after the data blobs: FRAMES (the nine golden-path screens from
// data/screens_v02.json, five fields each, in slide order) and LINK (where a frame opens). No network, no libraries.
// One slide per viewport; arrow keys, space and tap advance; n toggles the Say line; a slide counter.
(function(){
  // BEGIN copy esc (verbatim from scripts/renderer_v02.js; build_intro.py stops the build if it drifts)
  function esc(s){ return String(s === undefined || s === null ? "" : s).split("&").join("&amp;").split("<").join("&lt;").split(">").join("&gt;").split('"').join("&quot;"); }
  // END copy esc
  // BEGIN copy el (verbatim from scripts/renderer_v02.js; the wireframe element grammar)
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
  // END copy el

  function frameHtml(s){
    return '<div class="frame ' + (s.frame === "desktop" ? "desktop" : "phone") + '"><div class="frame-top"><span>' + esc(s.id) + '</span><span>' + esc(s.title) + '</span><span>' + esc(s.template) + '</span></div><div class="frame-body">' + s.ui.map(el).join("") + '</div></div>';
  }
  function thumbHtml(s){
    return '<figure class="thumb"><div class="fit" aria-hidden="true">' + frameHtml(s) + '</div><figcaption><b>' + esc(s.id) + '</b>' + esc(s.title) + '</figcaption>' +
      '<a class="hit" href="' + esc(LINK + s.id) + '" aria-label="' + esc(s.id + " " + s.title + ", open in wireframes v0.2") + '"></a></figure>';
  }

  var slides = Array.prototype.slice.call(document.querySelectorAll(".slide"));
  var counter = document.getElementById("counter");
  var grid = document.getElementById("grid");
  var idx = 0;

  // Slide 5: one uniform scale so three rows of three fit the viewport, caption beside each frame; one column at
  // phone width, frame at natural size with the caption below, and the slide scrolls.
  function fit(){
    var slide = grid.closest(".slide");
    var fits = Array.prototype.slice.call(grid.querySelectorAll(".fit"));
    var maxW = 0, maxH = 0;
    fits.forEach(function(f){ var fr = f.firstChild; if(fr.offsetWidth > maxW) maxW = fr.offsetWidth; if(fr.offsetHeight > maxH) maxH = fr.offsetHeight; });
    var cols = window.innerWidth >= 900 ? 3 : 1, rows = Math.ceil(fits.length / cols), caption = cols > 1 ? 160 : 0;
    var cs = getComputedStyle(grid), colGap = parseFloat(cs.columnGap) || 0, rowGap = parseFloat(cs.rowGap) || 0;
    var cellW = (grid.clientWidth - colGap * (cols - 1)) / cols - caption;
    var availH = slide.clientHeight - grid.getBoundingClientRect().top - parseFloat(getComputedStyle(slide).paddingBottom) - rowGap * (rows - 1);
    var s = Math.min(1, cellW / maxW);
    if(cols > 1) s = Math.min(s, availH / (rows * maxH));
    fits.forEach(function(f){ var fr = f.firstChild; fr.style.transform = "scale(" + s + ")"; f.style.width = (fr.offsetWidth * s) + "px"; f.style.height = (fr.offsetHeight * s) + "px"; });
  }

  function show(i){
    idx = Math.max(0, Math.min(slides.length - 1, i));
    slides.forEach(function(s, k){ s.classList.toggle("on", k === idx); });
    counter.textContent = (idx + 1) + " / " + slides.length;
    slides[idx].scrollTop = 0;
    if(grid && slides[idx].contains(grid)) fit();
  }

  document.addEventListener("keydown", function(ev){
    if(ev.altKey || ev.ctrlKey || ev.metaKey) return;
    var k = ev.key;
    if(k === "ArrowRight" || k === "ArrowDown" || k === " " || k === "PageDown"){ ev.preventDefault(); show(idx + 1); }
    else if(k === "ArrowLeft" || k === "ArrowUp" || k === "PageUp"){ ev.preventDefault(); show(idx - 1); }
    else if(k === "Home"){ ev.preventDefault(); show(0); }
    else if(k === "End"){ ev.preventDefault(); show(slides.length - 1); }
    else if(k === "n" || k === "N"){ document.body.classList.toggle("notes"); }
  });
  document.querySelector(".deck").addEventListener("click", function(ev){
    if(ev.target.closest("a, button")) return;
    if(window.getSelection && String(window.getSelection())) return;
    show(idx + 1);
  });
  window.addEventListener("resize", function(){ if(grid && slides[idx].contains(grid)) fit(); });

  if(grid) grid.innerHTML = FRAMES.map(thumbHtml).join("");
  show(0);
})();
