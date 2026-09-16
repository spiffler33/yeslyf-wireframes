#!/usr/bin/env python3
"""Generate docs/ (the GitHub Pages root) from data/*.json. Never hand-edit docs/.

Pages: index.html (Meeting, frozen), gaps.html (frozen), inputs.html (frozen), wireframes.html (v0.1 as-is),
admin.html (v0.1 as-is), wireframes_v02.html (generated from data/screens_v02.json with the v0.2 renderer in
scripts/renderer_v02.js), admin_v02.html (data/admin_crm.json plus the v0.2 additions, the CRM backlog and the
nudge matrix from data/v02/states.json), changelog.html (data/changelog.json), setup.html, and the three
self-contained audience files under docs/audiences/ (scripts/build_audiences.py; phase 9d), and the review link
under docs/review/ (index.html is Wireframes v0.2, admin_v02.html is Admin and CRM v0.2; the same pages with only
their two tabs and no setup link; one link for the team, Spinach and Compliance; Vatsal, 11 Sep 2026), and the
integrations page (integrations.html plus its review copy review/integrations.html, from data/integrations.json and
data/dependencies.json by scripts/build_integrations.py, called at the end of main; phase 10b, 16 Sep 2026), and the
event schema (events.html plus review/events.html, from the screens data and data/events_extra.json by
scripts/build_events.py, called after it; phase 10b-2, 16 Sep 2026).
The two v0.1 files are copied byte-identical into docs/v01/ and served as-is.
Style reuses the v0.1 tokens. Choices save in localStorage (try/catch), post to the sheet endpoint
when one is configured, and export as a markdown build brief. Every page carries noindex.
"""
import filecmp
import html
import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
DOCS = os.path.join(ROOT, "docs")
SCRIPTS = os.path.dirname(os.path.abspath(__file__))
V01_IN = os.path.join(ROOT, "inputs", "v01")
V01_FILES = ["yeslyf_wireframes_v0.1.html", "yeslyf_admin_crm_spec_v0.1.html"]
WIRE = "v01/yeslyf_wireframes_v0.1.html"
ADMIN = "v01/yeslyf_admin_crm_spec_v0.1.html"
MEETING_DATE = "09 Sep 2026"  # the meeting the board was built for; not today, so a rebuild does not relabel the page
FROZEN_BANNER = "Frozen on 9 Sep 2026; decisions recorded below; controls disabled"
PENDING = "arrives with phase 5 (data/v02/states.json)"
# Strings that must not appear on a v0.2 page (plan_v2.md section 7, check 6). The frozen pages keep their v0.1 wording.
FORBIDDEN = ["Priya", "founders", "Founders", "Yeslyf", "recommendation", "Recommendation"]
V02_PAGES = ["wireframes_v02.html", "admin_v02.html", "changelog.html", "review/index.html", "review/admin_v02.html"]


def load(name):
    with open(os.path.join(DATA, name)) as fh:
        return json.load(fh)


def load_optional(*parts):
    path = os.path.join(DATA, *parts)
    if not os.path.exists(path):
        return None
    with open(path) as fh:
        return json.load(fh)


def read_script(name):
    with open(os.path.join(SCRIPTS, name)) as fh:
        return fh.read()


def esc(s):
    return html.escape(str(s if s is not None else ""), quote=True)


def names(lst):
    return " and ".join(lst)


def js_blob(obj):
    # JSON inside a script tag: ASCII only, and no "</" so a string can never close the tag.
    return json.dumps(obj, ensure_ascii=True).replace("</", "<\\/")


CSS = """
  :root{--paper:#EEF0F3;--panel:#fff;--ink:#1B1F27;--mute:#5F6773;--line:#D3D7DE;--accent:#FFDA00;--accent-soft:#FFF4B8;
    --sans:-apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,"Helvetica Neue",Arial,sans-serif}
  *{box-sizing:border-box}
  html,body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);font-size:14px;line-height:1.45;scroll-behavior:smooth}
  button,select,input,textarea{font-family:inherit;font-size:13px}
  a{color:inherit}
  ::selection{background:var(--accent)}
  :focus-visible{outline:2px solid var(--ink);outline-offset:2px}
  .top{position:sticky;top:0;z-index:5;display:flex;align-items:center;gap:12px;padding:8px 18px;background:var(--panel);border-bottom:1px solid var(--line);flex-wrap:wrap}
  .brand{font-weight:700;font-size:16px;white-space:nowrap}
  .brand span{font-weight:400;color:var(--mute);margin-left:8px;font-size:13px}
  .tabs{display:flex;gap:2px;flex-wrap:wrap}
  .tabs a{text-decoration:none;font-size:13px;padding:6px 10px;border-radius:6px;border:1px solid transparent;color:var(--mute)}
  .tabs a:hover{background:#F5F6F8}
  .tabs a.on{color:var(--ink);font-weight:600;border-color:var(--line);background:#fff}
  .who{display:flex;align-items:center;gap:6px;font-size:12px;color:var(--mute);margin-left:auto}
  .who input{padding:6px 8px;border:1px solid var(--line);border-radius:6px;width:170px}
  .saved{font-size:12px;color:var(--mute);min-width:120px}
  .pill{font-size:11px;border:1px solid var(--line);border-radius:999px;padding:2px 8px;color:var(--mute);text-decoration:none;white-space:nowrap}
  .pill.on{border-color:#C9A800;background:var(--accent-soft);color:var(--ink)}
  .top .primary{border:1px solid var(--accent);background:var(--accent);padding:7px 12px;border-radius:6px;font-weight:600;cursor:pointer}
  .top .ghost{border:1px solid var(--line);background:#fff;padding:7px 12px;border-radius:6px;cursor:pointer}
  .frozen{padding:6px 18px;background:#F1F2F4;border-bottom:1px solid var(--line);font-size:12.5px;color:var(--mute)}
  .decided-line{font-size:12.5px;margin:0 0 8px;padding:5px 10px;border-radius:6px;background:var(--accent-soft);border:1px solid #C9A800}
  .layout{display:grid;grid-template-columns:240px minmax(0,1fr)}
  .nav{position:sticky;top:49px;height:calc(100vh - 49px);overflow:auto;background:var(--panel);border-right:1px solid var(--line);padding:10px 0}
  .nav a{display:block;padding:6px 14px 6px 11px;text-decoration:none;font-size:13px;border-left:3px solid transparent}
  .nav a:hover{background:#F5F6F8}
  .nav .sub{padding-left:24px;font-size:12px;color:var(--mute)}
  .main{padding:18px 26px 120px;max-width:1150px}
  section{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:18px 22px;margin:0 0 16px;scroll-margin-top:60px}
  h1{font-size:22px;margin:0 0 6px}
  h2{font-size:17px;margin:0 0 4px}
  h2 small{font-weight:400;color:var(--mute);font-size:13px;margin-left:8px}
  h3{font-size:14px;margin:14px 0 4px}
  .lead{color:var(--mute);margin:0 0 12px;max-width:860px}
  .rule{padding-left:10px;border-left:3px solid var(--accent);margin:8px 0 12px;max-width:900px}
  ul{margin:6px 0;padding-left:18px} li{margin:3px 0}
  .stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px;margin:8px 0 4px}
  .stat{border:1px solid var(--line);border-radius:8px;padding:10px 12px;background:#FCFCFD}
  .stat b{display:block;font-size:22px} .stat span{font-size:12px;color:var(--mute)}
  .item{border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:0 0 12px;background:#FCFCFD;scroll-margin-top:60px}
  .item.hi{border-color:#C9A800;box-shadow:0 0 0 3px var(--accent-soft)}
  .item.done{border-color:#7A8797}
  .item-h{display:flex;gap:10px;align-items:baseline;flex-wrap:wrap;margin-bottom:6px}
  .item-h b{font-size:15px}
  .tag{font-size:11px;border:1px solid var(--line);border-radius:4px;padding:1px 6px;background:#fff;color:var(--mute);white-space:nowrap}
  .tag.hi{border-color:#B2434F;color:#B2434F;font-weight:600}
  .tag.team{border-color:var(--ink);color:var(--ink);font-weight:600}
  .tag.done{background:var(--ink);color:#fff;border-color:var(--ink)}
  .tag.new{border-color:var(--ink);color:var(--ink)}
  .tag.changed{border-color:#C9A800;background:var(--accent-soft);color:var(--ink)}
  .screens a{font-size:11px;font-weight:600;text-decoration:none;border:1px solid var(--line);padding:0 5px;border-radius:4px;margin-right:3px;background:#fff}
  .ctx{font-size:13px;margin:0 0 8px;color:#3B4250}
  .pos{margin:0 0 8px;padding-left:10px;border-left:3px solid var(--accent)}
  .pos li{font-size:12.5px} .pos b{font-weight:600}
  .pos .ref{color:var(--mute);font-size:11.5px}
  .cond{font-size:12.5px;margin:0 0 8px} .cond li{list-style:none;margin-left:-18px}
  .dflt-line{font-size:12.5px;margin:6px 0 4px;color:#3B4250}
  .opt{display:flex;gap:10px;align-items:flex-start;padding:7px 10px;border:1px solid var(--line);border-radius:8px;margin:5px 0;background:#fff;cursor:pointer}
  .opt input{margin-top:3px}
  .opt.dflt{border-color:#C9A800;background:#FFFDF2}
  .opt .held{display:block;font-size:11.5px;color:var(--mute);margin-top:2px}
  .dpill{display:inline-block;font-size:10.5px;font-weight:700;background:var(--accent);border-radius:4px;padding:1px 6px;margin-left:6px;white-space:nowrap}
  .ppill{display:inline-block;font-size:10.5px;border:1px dashed var(--mute);border-radius:4px;padding:1px 6px;margin-left:6px;color:var(--mute);white-space:nowrap}
  .dep{font-size:12.5px;color:#3B4250;margin:8px 0 0;padding:6px 10px;border:1px dashed var(--line);border-radius:6px;background:#fff}
  .dep.on{border-style:solid;border-color:#C9A800;background:#FFFBEA}
  .dep b{font-weight:600}
  .meta{font-size:11.5px;color:var(--mute)}
  .note{width:100%;min-height:40px;border:1px solid var(--line);border-radius:6px;padding:6px;resize:vertical;background:#fff;margin-top:6px}
  .decided{display:flex;gap:8px;align-items:center;font-size:12.5px;margin-top:8px}
  .qa{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:8px 12px;align-items:start;padding:7px 0;border-bottom:1px solid var(--line);font-size:12.5px}
  .qa:last-child{border-bottom:0}
  .qa .t{white-space:pre-wrap} .qa .t b{white-space:nowrap}
  .qa .c{display:flex;gap:4px;align-items:center;flex-wrap:wrap;justify-content:flex-end}
  .qa button{border:1px solid var(--line);background:#fff;padding:4px 9px;border-radius:5px;cursor:pointer}
  .qa button.on{background:var(--accent);border-color:#C9A800;font-weight:600}
  .qa button.on.no{background:#F1F2F4;border-color:var(--ink)}
  .qa input{padding:4px 6px;border:1px solid var(--line);border-radius:5px;width:180px}
  .qa .decided-line{grid-column:1 / -1;margin:0}
  .gap{border:1px solid var(--line);border-radius:8px;padding:10px 12px;margin:0 0 8px;background:#FCFCFD;scroll-margin-top:60px}
  .gap-h{display:flex;gap:8px;align-items:baseline;flex-wrap:wrap}
  .gap .why{font-size:12.5px;color:#3B4250;margin:6px 0}
  .gap .rec{font-size:12.5px;margin:6px 0;padding-left:10px;border-left:3px solid var(--accent)}
  .gap-c{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-top:6px;font-size:12px}
  .gap-c select,.gap-c input{padding:5px;border:1px solid var(--line);border-radius:5px;background:#fff}
  table{width:100%;border-collapse:collapse;font-size:12.5px} th{text-align:left;border-bottom:2px solid var(--ink);padding:6px 8px;font-size:12px;vertical-align:bottom} td{border-bottom:1px solid var(--line);padding:6px 8px;vertical-align:top}
  td.n{font-variant-numeric:tabular-nums;color:var(--mute);white-space:nowrap}
  td .raw{white-space:pre-wrap}
  td .ans{margin-top:4px;padding-left:8px;border-left:3px solid var(--accent);font-size:12px}
  td .basis{color:var(--mute);font-size:11.5px;margin-top:3px}
  .status{font-size:11px;border:1px solid var(--line);border-radius:4px;padding:1px 6px;white-space:nowrap;background:#fff}
  .status.open{border-color:#C9A800;background:var(--accent-soft)}
  .status.quick-accept{border-color:#7A8797}
  .filters{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 12px;font-size:12px;align-items:center}
  .filters select{padding:5px;border:1px solid var(--line);border-radius:5px;background:#fff}
  tr.hidden{display:none}
  tr.hi td{background:var(--accent-soft)}
  details{margin:8px 0} summary{cursor:pointer;font-weight:600;font-size:13px}
  pre{background:#F5F6F8;border:1px solid var(--line);border-radius:6px;padding:10px;font-size:11.5px;overflow:auto;white-space:pre-wrap}
  .setup input{width:100%;padding:7px;border:1px solid var(--line);border-radius:6px;margin:4px 0}
  .frame-wrap{height:calc(100vh - 49px)} .frame-wrap iframe{width:100%;height:100%;border:0;background:#fff}
  .frame-bar{display:flex;gap:10px;align-items:center;padding:6px 18px;background:var(--panel);border-bottom:1px solid var(--line);font-size:12px;color:var(--mute);flex-wrap:wrap}
  .frame-bar select{padding:5px;border:1px solid var(--line);border-radius:5px;background:#fff;max-width:360px}
  .frame-wrap.with-bar{height:calc(100vh - 88px)}
  .wrap{overflow-x:auto}
  .sid{font-weight:600;text-decoration:none;border:1px solid var(--line);padding:0 5px;border-radius:4px;background:#fff;white-space:nowrap}
  .cause{color:var(--mute);font-size:11.5px}
  @media (max-width:1000px){.layout{display:block}.nav{display:none}.main{padding:12px}.who{margin-left:0}.qa{grid-template-columns:1fr}.qa .c{justify-content:flex-start}}
"""

TABS = [("index.html", "Meeting"), ("gaps.html", "Gaps"), ("inputs.html", "Inputs"),
        ("wireframes.html", "Wireframes v0.1"), ("admin.html", "Admin and CRM v0.1"),
        ("wireframes_v02.html", "Wireframes v0.2"), ("admin_v02.html", "Admin and CRM v0.2"),
        ("changelog.html", "Changelog"), ("integrations.html", "Integrations"), ("events.html", "Events"), ("setup.html", "Setup")]
# The review link (docs/review/): the v0.2 pages with only their tabs (Vatsal, 11 Sep 2026); Integrations added 16 Sep 2026;
# Events added 16 Sep 2026 (phase 10b-2).
REVIEW_TABS = [("index.html", "Wireframes v0.2"), ("admin_v02.html", "Admin and CRM v0.2"), ("integrations.html", "Integrations"),
               ("events.html", "Events")]


def head(title, css=None):
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            '<meta name="robots" content="noindex, nofollow">\n'
            '<title>' + esc(title) + '</title>\n<style>' + (CSS if css is None else css) + '</style>\n</head>\n')


def header(current, subtitle, show_export=True, who_html=None, export_label="Export brief", tabs=None, setup_link=True):
    tabs = "".join('<a href="%s"%s>%s</a>' % (href, ' class="on"' if href == current else "", esc(label))
                   for href, label in (TABS if tabs is None else tabs))
    if who_html is None:
        who_html = '<div class="who">Decided by <input id="who" placeholder="your first name"></div>'
    pill = ('<a id="sheetpill" class="pill" href="setup.html" title="Sheet write-back status">sheet: off</a>' if setup_link
            else '<span id="sheetpill" class="pill" title="Sheet write-back status">sheet: off</span>')
    right = who_html + '<div id="saved" class="saved"></div>' + pill
    if show_export:
        right += '<button id="export" class="primary">%s</button>' % esc(export_label)
    return ('<header class="top"><div class="brand">yeslyf <span>' + esc(subtitle) + '</span></div>'
            '<nav class="tabs">' + tabs + '</nav>' + right + '</header>\n')


def frozen_banner():
    return '<div class="frozen">%s</div>\n' % esc(FROZEN_BANNER)


JS_COMMON = r"""
(function(){
  var KEY="yeslyf_board_v1"; var S={};
  try{ S=JSON.parse(localStorage.getItem(KEY)||"{}")||{}; }catch(e){ S={}; }
  function save(){ try{ localStorage.setItem(KEY, JSON.stringify(S)); }catch(e){} }
  try{ var q=location.search||""; var qi=q.indexOf("endpoint="); if(qi>=0){ var qv=decodeURIComponent(q.slice(qi+9).split("&")[0]).trim(); if(qv){ S.endpoint=qv; save(); } if(history.replaceState) history.replaceState(null,"",location.pathname+location.hash); } }catch(e){}
  function g(k){ if(!S[k]) S[k]={}; return S[k]; }
  function who(){ return (S.who||"").trim(); }
  var ft; function flash(t){ var s=document.getElementById("saved"); if(!s) return; s.textContent=t||"Saved in this browser"; clearTimeout(ft); ft=setTimeout(function(){ s.textContent=""; },1800); }
  function sink(kind,row){ var ep=(S.endpoint||"").trim(); if(!ep) return false; row.kind=kind; row.who=who(); row.ts=new Date().toISOString();
    try{ fetch(ep,{method:"POST",mode:"no-cors",headers:{"Content-Type":"text/plain"},body:JSON.stringify(row)}); }catch(e){} return true; }
  function pill(){ var p=document.getElementById("sheetpill"); if(!p) return; var on=!!(S.endpoint||"").trim(); p.textContent=on?"sheet: on":"sheet: off"; p.className="pill"+(on?" on":""); }
  function choiceOf(id){ var r=S["item:"+id]; if(r&&r.choice!==undefined) return r.choice; var d=DATA.items[id]?DATA.items[id].dflt:null; return d?d:null; }
  function choiceList(id){ var c=choiceOf(id); if(c===null||c===undefined) return []; return Array.isArray(c)?c:[c]; }
  function optText(id,key){ var it=DATA.items[id]; for(var i=0;i<it.options.length;i++) if(it.options[i].key===key) return it.options[i].text; return key; }
  function depOn(id,ifKey){ var list=choiceList(id); var r=S["item:"+id]||{}; if(ifKey.indexOf("not:")===0){ var k=ifKey.slice(4); return !!r.decided && list.length>0 && list.indexOf(k)<0; } return list.indexOf(ifKey)>=0; }
  function paintItem(id){ var card=document.getElementById("item-"+id); if(!card) return; var r=S["item:"+id]||{}; var list=choiceList(id);
    var inputs=card.querySelectorAll("input[data-item]"); for(var i=0;i<inputs.length;i++){ inputs[i].checked=list.indexOf(inputs[i].value)>=0; }
    var dc=card.querySelector("input[data-decided]"); if(dc) dc.checked=!!r.decided;
    var ta=card.querySelector("textarea[data-item]"); if(ta && ta.value!==(r.note||"")) ta.value=r.note||"";
    card.className="item"+(r.decided?" done":"")+(card.className.indexOf(" hi")>=0?" hi":"");
    var tag=card.querySelector(".tag.done"); if(tag) tag.style.display=r.decided?"":"none";
    var deps=card.querySelectorAll(".dep"); for(var j=0;j<deps.length;j++){ deps[j].className="dep"+(depOn(id,deps[j].getAttribute("data-if"))?" on":""); } }
  function paintAll(){ for(var id in DATA.items) paintItem(id);
    for(var n in DATA.qa){ var r=S["qa:"+n]||{}; var row=document.getElementById("qa-"+n); if(!row) continue; var bs=row.querySelectorAll("button[data-v]"); for(var i=0;i<bs.length;i++){ bs[i].className=(bs[i].getAttribute("data-v")===r.v?"on":"")+(bs[i].getAttribute("data-v")==="decline"?" no":""); } var inp=row.querySelector("input[data-qan]"); if(inp&&inp.value!==(r.note||"")) inp.value=r.note||""; }
    for(var gid in DATA.gaps){ var gr=S["gap:"+gid]||{}; var el=document.getElementById("gap-"+gid); if(!el) continue; var f=el.querySelectorAll("[data-f]"); for(var k=0;k<f.length;k++){ var key=f[k].getAttribute("data-f"); if(f[k].value!==(gr[key]||"")) f[k].value=gr[key]||""; } }
    var w=document.getElementById("who"); if(w&&w.value!==(S.who||"")) w.value=S.who||""; pill(); }
  function recordItem(id){ var r=g("item:"+id); r.decided=true; save(); var list=choiceList(id); var labels=list.map(function(k){ return k+" "+optText(id,k); });
    sink("decisions",{item_id:id,choice:list.join(", "),choice_text:labels.join(" | "),note:r.note||""}); paintItem(id); flash(); }
  function md(){ var L=["# yeslyf meeting brief","Exported "+new Date().toLocaleString()+(who()?" by "+who():""),"Sheet endpoint: "+((S.endpoint||"").trim()?"configured":"not configured; this file is the record"),""];
    L.push("## Decisions");
    DATA.order.forEach(function(id){ var it=DATA.items[id]; var r=S["item:"+id]||{}; var list=choiceList(id); var owner=it.owner;
      var line="- "+id+" "+it.title+" ("+owner+"): ";
      if(!list.length){ line+= (owner==="Team"?"no choice made":"no choice made; "+owner+" to decide"); }
      else { line+=list.map(function(k){ return k+" "+optText(id,k); }).join("; "); if(it.dflt&&!r.decided){ line+=" (default, "+it.dflt_who+"'s position; not confirmed in the meeting)"; } else if(r.decided){ line+=" (decided in the meeting"+(who()?", "+who():"")+")"; } }
      if(r.note) line+="\n  Note: "+String(r.note).split("\n").join(" ");
      it.deps.forEach(function(d){ if(depOn(id,d.if_key)) line+="\n  Follows: "+d.then+" (Vatsal recommendation)"; });
      L.push(line); });
    L.push(""); L.push("## Quick-accepts");
    DATA.qa_order.forEach(function(n){ var q=DATA.qa[n]; var r=S["qa:"+n]||{}; L.push("- row "+n+" "+q.screen+" ("+q.reviewer+", for "+q.owner+"): "+(r.v||"not ticked")+(r.note?" | "+r.note:"")); });
    L.push(""); L.push("## Gaps");
    DATA.gap_order.forEach(function(gid){ var x=DATA.gaps[gid]; var r=S["gap:"+gid]||{}; L.push("- "+gid+" "+x.title+": "+(r.status||"no status")+(r.owner?" | owner: "+r.owner:"")+(r.date?" | by: "+r.date:"")+(r.note?" | "+String(r.note).split("\n").join(" "):"")); });
    return L.join("\n"); }
  function exportBrief(){ var text=md(); try{ navigator.clipboard&&navigator.clipboard.writeText(text); }catch(e){}
    var b=new Blob([text],{type:"text/markdown"}); var a=document.createElement("a"); a.href=URL.createObjectURL(b); a.download="yeslyf_meeting_brief.md"; document.body.appendChild(a); a.click(); document.body.removeChild(a); flash("Brief exported and copied"); }
  function deepLink(){ var h=location.hash||""; if(h.indexOf("#screen/")===0){ location.href="wireframes.html#"+h.slice(8); return; }
    var id=null; if(h.indexOf("#item/")===0) id="item-"+h.slice(6); else if(h.indexOf("#gap/")===0) id="gap-"+h.slice(5); else if(h.indexOf("#row/")===0) id="row-"+h.slice(5);
    if(!id) return; var el=document.getElementById(id); if(!el) return; var old=document.querySelectorAll(".hi"); for(var i=0;i<old.length;i++) old[i].classList.remove("hi"); el.classList.add("hi"); try{ el.scrollIntoView({block:"start",behavior:"instant"}); }catch(e){ el.scrollIntoView(true); } }
  var tmr={};
  document.addEventListener("DOMContentLoaded",function(){
    paintAll(); deepLink(); window.addEventListener("load",function(){ setTimeout(deepLink,60); }); window.addEventListener("hashchange",deepLink);
    var w=document.getElementById("who"); if(w) w.addEventListener("input",function(e){ S.who=e.target.value; save(); });
    var ex=document.getElementById("export"); if(ex) ex.addEventListener("click",exportBrief);
    var ep=document.getElementById("endpoint"); if(ep){ ep.value=S.endpoint||""; ep.addEventListener("input",function(e){ S.endpoint=e.target.value.trim(); save(); pill(); flash(S.endpoint?"Endpoint saved in this browser":"Endpoint cleared"); }); }
    var test=document.getElementById("testrow"); if(test) test.addEventListener("click",function(){ var ok=sink("decisions",{item_id:"TEST",choice:"test",choice_text:"test row from setup page",note:""}); flash(ok?"Test row sent; check the decisions tab of the sheet":"No endpoint set"); });
    document.body.addEventListener("change",function(e){ var t=e.target;
      if(t.type==="radio"&&t.getAttribute("data-item")){ g("item:"+t.getAttribute("data-item")).choice=t.value; recordItem(t.getAttribute("data-item")); }
      if(t.type==="checkbox"&&t.getAttribute("data-item")){ var id=t.getAttribute("data-item"); var r=g("item:"+id); var list=choiceList(id).slice(); var i=list.indexOf(t.value); if(t.checked&&i<0) list.push(t.value); if(!t.checked&&i>=0) list.splice(i,1); r.choice=list; recordItem(id); }
      if(t.type==="checkbox"&&t.getAttribute("data-decided")){ var id2=t.getAttribute("data-decided"); var r2=g("item:"+id2); r2.decided=t.checked; if(t.checked&&r2.choice===undefined&&DATA.items[id2].dflt) r2.choice=DATA.items[id2].dflt; save(); if(t.checked) recordItem(id2); else { paintItem(id2); flash(); } }
      if(t.tagName==="SELECT"&&t.getAttribute("data-gap")){ var gid=t.getAttribute("data-gap"); g("gap:"+gid)[t.getAttribute("data-f")]=t.value; save(); var gr=S["gap:"+gid]; sink("gaps",{gap_id:gid,status:gr.status||"",owner_date:((gr.owner||"")+" "+(gr.date||"")).trim(),note:gr.note||""}); flash(); }
      if(t.type==="date"&&t.getAttribute("data-gap")){ var gid2=t.getAttribute("data-gap"); g("gap:"+gid2).date=t.value; save(); var gr2=S["gap:"+gid2]; sink("gaps",{gap_id:gid2,status:gr2.status||"",owner_date:((gr2.owner||"")+" "+(gr2.date||"")).trim(),note:gr2.note||""}); flash(); }
    });
    document.body.addEventListener("input",function(e){ var t=e.target;
      var item=t.getAttribute("data-item"); if(item&&t.tagName==="TEXTAREA"){ g("item:"+item).note=t.value; save(); flash(); clearTimeout(tmr[item]); tmr[item]=setTimeout(function(){ var r=S["item:"+item]; if(r&&r.decided) sink("decisions",{item_id:item,choice:choiceList(item).join(", "),choice_text:choiceList(item).map(function(k){return k+" "+optText(item,k);}).join(" | "),note:r.note||""}); },1500); return; }
      var qn=t.getAttribute("data-qan"); if(qn){ g("qa:"+qn).note=t.value; save(); flash(); clearTimeout(tmr["qa"+qn]); tmr["qa"+qn]=setTimeout(function(){ var r=S["qa:"+qn]; if(r&&r.v) sink("quick_accepts",{input_n:qn,accept:r.v,note:r.note||""}); },1500); return; }
      var gid=t.getAttribute("data-gap"); if(gid&&t.getAttribute("data-f")!=="status"){ g("gap:"+gid)[t.getAttribute("data-f")]=t.value; save(); flash(); clearTimeout(tmr["gap"+gid]); tmr["gap"+gid]=setTimeout(function(){ var gr=S["gap:"+gid]; sink("gaps",{gap_id:gid,status:gr.status||"",owner_date:((gr.owner||"")+" "+(gr.date||"")).trim(),note:gr.note||""}); },1500); }
    });
    document.body.addEventListener("click",function(e){ var t=e.target; if(t.tagName!=="BUTTON") return; var n=t.getAttribute("data-qa"); if(!n) return; var r=g("qa:"+n); r.v=(r.v===t.getAttribute("data-v"))?"":t.getAttribute("data-v"); save(); paintAll(); flash(); sink("quick_accepts",{input_n:n,accept:r.v||"cleared",note:r.note||""}); });
    var reset=document.getElementById("reset"); if(reset) reset.addEventListener("click",function(){ if(!confirm("Clear every choice and note saved in this browser? The sheet keeps what was already sent.")) return; var keep={who:S.who,endpoint:S.endpoint}; S=keep; save(); paintAll(); flash("Cleared"); });
    var f=document.getElementById("filters"); if(f){ f.addEventListener("change",applyFilters); applyFilters(); }
  });
  function applyFilters(){ var f=document.getElementById("filters"); if(!f) return; var rv=f.querySelector("[name=reviewer]").value, ws=f.querySelector("[name=workstream]").value, st=f.querySelector("[name=status]").value; var rows=document.querySelectorAll("tr[data-n]"); var shown=0;
    for(var i=0;i<rows.length;i++){ var r=rows[i]; var ok=(rv==="All"||(" "+r.getAttribute("data-reviewers")+" ").indexOf(" "+rv+" ")>=0)&&(ws==="All"||r.getAttribute("data-ws")===ws)&&(st==="All"||r.getAttribute("data-status")===st); r.className=(ok?"":"hidden")+(r.className.indexOf("hi")>=0?" hi":""); if(ok) shown++; }
    var c=document.getElementById("count"); if(c) c.textContent=shown+" of "+rows.length+" rows"; }
})();
"""

# The v0.2 static pages (admin, changelog) carry only the endpoint capture and the sheet pill; no board controls.
JS_PILL = r"""
(function(){
  var KEY="yeslyf_board_v1"; var S={};
  try{ S=JSON.parse(localStorage.getItem(KEY)||"{}")||{}; }catch(e){ S={}; }
  try{ var q=location.search||""; var qi=q.indexOf("endpoint="); if(qi>=0){ var qv=decodeURIComponent(q.slice(qi+9).split("&")[0]).trim(); if(qv){ S.endpoint=qv; try{ localStorage.setItem(KEY, JSON.stringify(S)); }catch(e){} } if(history.replaceState) history.replaceState(null,"",location.pathname+location.hash); } }catch(e){}
  document.addEventListener("DOMContentLoaded",function(){ var p=document.getElementById("sheetpill"); if(!p) return; var on=!!(S.endpoint||"").trim(); p.textContent=on?"sheet: on":"sheet: off"; p.className="pill"+(on?" on":""); });
})();
"""


def build_data_blob(items, inputs, gaps):
    d = {"items": {}, "order": [], "qa": {}, "qa_order": [], "gaps": {}, "gap_order": []}
    for it in items:
        dflt = None
        if it.get("default"):
            dflt = it["default"]["key"] if it["control"] == "single" else [it["default"]["key"]]
        d["items"][it["id"]] = {"title": it["title"], "owner": names(it["owner"]), "control": it["control"],
                                "options": [{"key": o["key"], "text": o["text"]} for o in it["options"]],
                                "dflt": dflt, "dflt_who": it["default"]["who"] if it.get("default") else "",
                                "deps": [{"if_key": x["if_key"], "then": x["then"]} for x in it.get("dependencies", [])]}
        d["order"].append(it["id"])
    for row in inputs:
        if row["status"] == "quick-accept":
            d["qa"][str(row["n"])] = {"screen": row["screen"], "reviewer": row["reviewer"], "owner": names(row["owner"])}
            d["qa_order"].append(str(row["n"]))
    for gp in gaps:
        d["gaps"][gp["id"]] = {"title": gp["title"]}
        d["gap_order"].append(gp["id"])
    return json.dumps(d, ensure_ascii=True)


def screen_links(ids):
    return '<span class="screens">' + "".join('<a href="wireframes.html#%s" target="_blank" title="open in the v0.1 wireframes">%s</a>' % (esc(s), esc(s)) for s in ids) + '</span>'


# ---- the recorded decisions (data/decisions.json), shown on the frozen pages ------------------------------------

def decided_text(rec):
    """'Decided: <keys>; <status>; note: <note>' with the status reduced to one of three neutral phrases."""
    keys = ", ".join(rec.get("choice") or [])
    status = rec.get("status") or ""
    if not keys:
        phrase = "no choice made"
    elif status.startswith("default"):
        phrase = "default; not confirmed in the meeting"
    else:
        phrase = "decided in the meeting"
    line = "Decided: " + (keys if keys else "no choice") + "; " + phrase
    if rec.get("note"):
        line += "; note: " + rec["note"]
    return line


def render_item(it, decided=None):
    owner = names(it["owner"])
    with_ = (" (with " + ", ".join(it["with"]) + ")") if it.get("with") else ""
    team = it["owner"] == ["Team"]
    dis = " disabled" if decided is not None else ""
    h = ['<div class="item" id="item-%s">' % esc(it["id"])]
    h.append('<div class="item-h"><b>%s %s</b>' % (esc(it["id"]), esc(it["title"])))
    h.append('<span class="tag%s">%s%s</span>' % (" team" if team else "", esc(owner), esc(with_)))
    h.append('<span class="tag">%s</span>' % esc(it["workstream"]))
    h.append('<span class="tag%s">impact %s</span>' % (" hi" if it["impact"] == "High" else "", esc(it["impact"])))
    h.append('<span class="tag done" style="display:none">decided</span>')
    h.append(screen_links(it["screens"]) + '</div>')
    if decided is not None:
        h.append('<div class="decided-line">%s</div>' % esc(decided_text(decided)))
    h.append('<p class="ctx">%s</p>' % esc(it["context"]))
    h.append('<ul class="pos">')
    for p in it["positions"]:
        h.append('<li><b>%s</b> <span class="ref">(%s)</span>: %s</li>' % (esc(p["who"]), esc(p["ref"]), esc(p["position"])))
    h.append('</ul>')
    if it.get("conditions"):
        h.append('<ul class="cond">' + "".join('<li>Condition to verify (%s): %s</li>' % (esc(c["verifies"]), esc(c["what"])) for c in it["conditions"]) + '</ul>')
    d = it.get("default")
    if team:
        h.append('<div class="dflt-line">Team item: decided in the meeting by everyone. Nothing is preselected.</div>')
    elif d:
        h.append('<div class="dflt-line">Default: %s\'s stated position (option %s), preselected. Change it only if the meeting decides otherwise.</div>' % (esc(d["who"]), esc(d["key"])))
    else:
        h.append('<div class="dflt-line">%s to decide. Inputs listed above; nothing is preselected.</div>' % esc(owner + with_))
    typ = "checkbox" if it["control"] == "multi" else "radio"
    for o in it["options"]:
        is_d = bool(d) and o["key"] == d["key"]
        held = ("held by: " + ", ".join(o["held_by"])) if o.get("held_by") else ""
        h.append('<label class="opt%s"><input type="%s" name="item-%s" value="%s" data-item="%s"%s%s><span>%s. %s%s%s<span class="held">%s</span></span></label>' % (
            " dflt" if is_d else "", typ, esc(it["id"]), esc(o["key"]), esc(it["id"]), " checked" if is_d else "", dis,
            esc(o["key"]), esc(o["text"]),
            '<span class="dpill">default: %s</span>' % esc(d["who"]) if is_d else "",
            '<span class="ppill">possible form</span>' if not o.get("held_by") else "",
            esc(held)))
    for dep in it.get("dependencies", []):
        h.append('<div class="dep" data-if="%s"><b>%s</b> (Vatsal recommendation): %s</div>' % (esc(dep["if_key"]), esc(dep["if_text"]), esc(dep["then"])))
    h.append('<textarea class="note" data-item="%s" placeholder="Note from the meeting (who said what, conditions, dates)"%s></textarea>' % (esc(it["id"]), dis))
    h.append('<label class="decided"><input type="checkbox" data-decided="%s"%s> Decided in the meeting</label>' % (esc(it["id"]), dis))
    h.append('</div>')
    return "\n".join(h)


def render_qa(row, decided=None):
    txt = row["text"]
    dis = " disabled" if decided is not None else ""
    h = ['<div class="qa" id="qa-%d">' % row["n"]]
    h.append('<div class="t"><b>row %d, %s, %s:</b> %s</div>' % (row["n"], esc(row["screen"]), esc(row["reviewer"]), esc(txt)))
    h.append('<div class="c"><button data-qa="%d" data-v="accept"%s>Accept</button><button data-qa="%d" data-v="decline"%s>Decline</button><input data-qan="%d" placeholder="note"%s></div>' % (row["n"], dis, row["n"], dis, row["n"], dis))
    if decided is not None:
        line = "Decided: " + (decided.get("accept") or "not ticked")
        if decided.get("note"):
            line += "; note: " + decided["note"]
        h.append('<div class="decided-line">%s</div>' % esc(line))
    h.append('</div>')
    return "\n".join(h)


def audience_links(audiences):
    """One chrome line on index.html pointing at the audience files (phase 9d); the frozen content is untouched."""
    if not audiences:
        return ""
    return '<div class="frozen">Audience files, self-contained, open from disk with no network: %s. Sizes on the Changelog tab.</div>\n' % ", ".join(
        '<a href="%s">%s</a>' % (esc(a["href"]), esc(a["for"])) for a in audiences)


def build_meeting(items, inputs, gaps, decisions=None, audiences=None):
    dec_items = {d["item_id"]: d for d in (decisions or {}).get("items", [])}
    dec_qa = {str(q["n"]): q for q in (decisions or {}).get("quick_accepts", [])}
    frozen = decisions is not None
    order = []
    for it in items:
        key = names(it["owner"])
        if key not in order:
            order.append(key)
    by_owner = {k: [it for it in items if names(it["owner"]) == k] for k in order}
    qa_by_owner = {}
    for row in inputs:
        if row["status"] == "quick-accept":
            qa_by_owner.setdefault(names(row["owner"]), []).append(row)
    for k in qa_by_owner:
        if k not in order:
            order.append(k)
    team_items = sum(1 for it in items if it["owner"] == ["Team"])
    n_qa = sum(len(v) for v in qa_by_owner.values())
    nav = []
    body = []
    for k in order:
        sec_id = "sec-" + k.replace(" ", "-").lower()
        its = by_owner.get(k, [])
        qas = qa_by_owner.get(k, [])
        nav.append('<a href="#%s">%s <em style="color:var(--mute);font-style:normal">(%d%s)</em></a>' % (sec_id, esc(k), len(its), (" + %d quick" % len(qas)) if qas else ""))
        for it in its:
            nav.append('<a class="sub" href="#item/%s">%s %s</a>' % (esc(it["id"]), esc(it["id"]), esc(it["title"])))
        body.append('<section id="%s"><h2>%s<small>%s</small></h2>' % (sec_id, esc(k), "decides in the meeting; nothing preselected" if k == "Team" else "owner; the stated position is the default"))
        for it in its:
            body.append(render_item(it, dec_items.get(it["id"], {"choice": [], "status": "", "note": ""}) if frozen else None))
        if qas:
            body.append('<h3>Quick-accepts for %s</h3><p class="meta">Suggestions by others inside this workstream. Only the owner accepts or declines; one line each.</p>' % esc(k))
            for row in qas:
                body.append(render_qa(row, dec_qa.get(str(row["n"]), {"accept": "", "note": ""}) if frozen else None))
        body.append('</section>')
    intro = ('<section id="s-how"><h1>Meeting: open items, by owner</h1>'
             '<p class="lead">Every position carries the first name of the person who said it and where. The owner of a workstream holds the default: '
             'if the owner has stated a position it is preselected, otherwise the item reads "&lt;owner&gt; to decide". Team items have nothing preselected. '
             'Accepted items are not on this page; they are on the Inputs tab with their status.</p>'
             '<div class="rule">In the meeting: type your name at the top, change only what the meeting decides, tick "Decided in the meeting", add a note where a condition or date was agreed. '
             'Export brief at the end; if the sheet is on, every change is also written there as it happens.</div>'
             '<div class="stats"><div class="stat"><b>%d</b><span>open items</span></div><div class="stat"><b>%d</b><span>Team items, no default</span></div>'
             '<div class="stat"><b>%d</b><span>quick-accepts to tick</span></div><div class="stat"><b>%d</b><span>gaps needing an owner</span></div>'
             '<div class="stat"><b>%d</b><span>review rows, all with a status</span></div></div></section>' % (len(items), team_items, n_qa, len(gaps), len(inputs)))
    reset = '<button id="reset" class="ghost"%s>Clear this browser</button>' % (" disabled" if frozen else "")
    page = (head("yeslyf product board: meeting") + '<body>\n' + header("index.html", "product board, meeting " + MEETING_DATE) + (frozen_banner() if frozen else "") + audience_links(audiences) +
            '<div class="layout"><nav class="nav"><a href="#s-how">How to read this</a>' + "".join(nav) +
            '<a href="gaps.html" style="margin-top:10px;color:var(--mute)">Gaps (%d)</a><a href="inputs.html" style="color:var(--mute)">Inputs (%d)</a></nav>' % (len(gaps), len(inputs)) +
            '<main class="main">' + intro + "\n".join(body) +
            '<section><h2>Housekeeping</h2><p class="meta">Choices and notes save in this browser only, per device. ' + reset + '</p></section>' +
            '</main></div>\n<script>var DATA=' + build_data_blob(items, inputs, gaps) + ';</script>\n<script>' + JS_COMMON + '</script>\n</body>\n</html>\n')
    return page


def build_gaps(items, inputs, gaps, decisions=None):
    frozen = decisions is not None
    dec_gaps = {g["id"]: g for g in (decisions or {}).get("gaps", [])}
    dis = " disabled" if frozen else ""
    body = ['<section><h1>Gaps: things nobody raised</h1><p class="lead">Each gap carries a Vatsal recommendation and a suggested owner by first name. The meeting gives each one an owner and a date, or drops it. Nothing here is decided until the owner says so.</p></section>']
    for gp in gaps:
        body.append('<div class="gap" id="gap-%s"><div class="gap-h"><b>%s %s</b><span class="tag%s">impact %s</span><span class="tag">suggested owner: %s</span></div>' % (
            esc(gp["id"]), esc(gp["id"]), esc(gp["title"]), " hi" if gp["impact"] == "High" else "", esc(gp["impact"]), esc(names(gp["suggested_owner"]))))
        if frozen:
            rec = dec_gaps.get(gp["id"], {})
            body.append('<div class="decided-line">%s</div>' % esc("Recorded in the meeting: " + (rec.get("status") or "no status")))
        body.append('<div class="why">%s</div>' % esc(gp["why"]))
        body.append('<div class="rec"><b>Vatsal recommendation:</b> %s</div>' % esc(gp["recommendation"]))
        body.append('<div class="gap-c"><label>Status <select data-gap="%s" data-f="status"%s><option value="">open</option><option>owner named</option><option>agreed, date set</option><option>dropped</option></select></label>'
                    '<label>Owner <input data-gap="%s" data-f="owner" placeholder="first name"%s></label><label>By <input type="date" data-gap="%s" data-f="date"%s></label></div>' % (esc(gp["id"]), dis, esc(gp["id"]), dis, esc(gp["id"]), dis))
        body.append('<textarea class="note" data-gap="%s" data-f="note" placeholder="Note"%s></textarea></div>' % (esc(gp["id"]), dis))
    page = (head("yeslyf product board: gaps") + '<body>\n' + header("gaps.html", "product board, gaps") + (frozen_banner() if frozen else "") +
            '<div class="layout"><nav class="nav">' + "".join('<a class="sub" href="#gap/%s">%s %s</a>' % (esc(g["id"]), esc(g["id"]), esc(g["title"][:40])) for g in gaps) + '</nav>' +
            '<main class="main">' + "\n".join(body) + '</main></div>\n<script>var DATA=' + build_data_blob(items, inputs, gaps) + ';</script>\n<script>' + JS_COMMON + '</script>\n</body>\n</html>\n')
    return page


def build_inputs(items, inputs, gaps, ownership, frozen=False):
    reviewers = ["Bhuvanaa", "Gaurav", "Harish", "Kajal", "Somil"]
    ws_ids = [w["id"] for w in ownership]
    statuses = ["open", "quick-accept", "accepted", "answered"]
    counts = {}
    for r in inputs:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    rows = []
    for r in inputs:
        srcs = r["sources"]
        if len(srcs) == 1:
            text = '<div class="raw">%s</div>' % esc(srcs[0]["text"])
            verdict = srcs[0]["verdict"]
        else:
            text = "".join('<div class="raw"><b>%s (%s%s)</b>: %s</div>' % (esc(s["reviewer"]), esc(s["screen"]), esc(", " + s["verdict"]) if s["verdict"] else "", esc(s["text"])) for s in srcs)
            verdict = ""
        extra = ""
        if r["status"] == "answered":
            extra = '<div class="ans"><b>Answer (%s):</b> %s</div>' % (esc(r["answer_by"]), esc(r["answer"]))
        elif r.get("note"):
            extra = '<div class="basis">%s</div>' % esc(r["note"])
        item = ('<a href="index.html#item/%s">%s</a>' % (esc(r["item"]), esc(r["item"]))) if r["item"] else ""
        scr = r["screen"]
        scr_html = ('<a href="wireframes.html#%s" target="_blank">%s</a>' % (esc(scr), esc(scr))) if scr and scr not in ("All",) and "-" not in scr else esc(scr)
        rows.append('<tr id="row-%d" data-n="%d" data-reviewers="%s" data-ws="%s" data-status="%s"><td class="n">%d</td><td>%s</td><td>%s</td><td>%s</td><td>%s%s</td><td>%s<div class="meta">%s</div></td><td><span class="status %s">%s</span></td><td>%s</td></tr>' % (
            r["n"], r["n"], esc(" ".join(s["reviewer"] for s in srcs)), esc(r["workstream"] or "none"), esc(r["status"]),
            r["n"], esc(r["reviewer"]), scr_html, esc(verdict), text, extra, esc(r["workstream"] or "-"), esc(names(r["owner"])), esc(r["status"]), esc(r["status"]), item))
    filters = ('<div class="filters" id="filters"><label>Reviewer <select name="reviewer"><option>All</option>%s</select></label>'
               '<label>Workstream <select name="workstream"><option>All</option>%s<option value="none">none</option></select></label>'
               '<label>Status <select name="status"><option>All</option>%s</select></label><span id="count" class="meta"></span></div>' % (
                   "".join("<option>%s</option>" % esc(x) for x in reviewers), "".join("<option>%s</option>" % esc(x) for x in ws_ids),
                   "".join("<option>%s</option>" % esc(x) for x in statuses)))
    intro = ('<section><h1>Inputs: the 73 review rows</h1><p class="lead">Raw comments from the five exports, with the row numbers of the v0.1 review log. Status labels only: '
             'open (attached to an item on the Meeting tab), quick-accept (the owner ticks it in the meeting), accepted (the owner of the workstream said it, or nothing is asked), '
             'answered (a factual question the v0.1 spec answers; the answer is quoted and credited to spec v0.1).</p>'
             '<div class="stats">%s</div></section>' % "".join('<div class="stat"><b>%d</b><span>%s</span></div>' % (counts.get(s, 0), s) for s in statuses))
    page = (head("yeslyf product board: inputs") + '<body>\n' + header("inputs.html", "product board, inputs", show_export=False) + (frozen_banner() if frozen else "") +
            '<main class="main" style="max-width:none">' + intro + '<section>' + filters +
            '<div style="overflow-x:auto"><table><thead><tr><th>#</th><th>Reviewer</th><th>Screen</th><th>Verdict</th><th>Comment (raw)</th><th>Workstream, owner</th><th>Status</th><th>Item</th></tr></thead><tbody>' +
            "\n".join(rows) + '</tbody></table></div></section></main>\n<script>var DATA=' + build_data_blob(items, inputs, gaps) + ';</script>\n<script>' + JS_COMMON + '</script>\n</body>\n</html>\n')
    return page


def build_frame_page(current, subtitle, title, src, screens=None):
    bar = ""
    js = ""
    if screens:
        opts = "".join('<option value="%s">%s %s</option>' % (esc(s["id"]), esc(s["id"]), esc(s["title"])) for s in screens)
        bar = ('<div class="frame-bar"><label>Jump to screen <select id="jump"><option value="">(section X: read me first)</option>%s</select></label>'
               '<a href="%s" target="_blank">Open the v0.1 file in its own tab</a><span>Deep link: wireframes.html#R09</span></div>' % (opts, esc(src)))
        js = ('var base="%s";var fr=document.getElementById("fr");function idOf(){var h=location.hash.replace("#","");if(h.indexOf("screen/")===0)h=h.slice(7);return h;}'
              'function show(){var id=idOf();fr.src="about:blank";setTimeout(function(){fr.src=base+(id?"#"+id:"");},0);var j=document.getElementById("jump");if(j)j.value=id;}'
              'document.getElementById("jump").addEventListener("change",function(e){location.hash=e.target.value;});window.addEventListener("hashchange",show);show();' % esc(src))
    else:
        bar = '<div class="frame-bar"><a href="%s" target="_blank">Open the v0.1 file in its own tab</a><span>Served as-is from docs/v01/; screen IDs inside it link to the wireframes.</span></div>' % esc(src)
        js = 'var fr=document.getElementById("fr");fr.src="%s"+(location.hash||"");' % esc(src)
    page = (head(title) + '<body>\n' + header(current, subtitle, show_export=False) + bar +
            '<div class="frame-wrap with-bar"><iframe id="fr" title="%s"></iframe></div>\n<script>%s</script>\n<script>%s</script>\n</body>\n</html>\n' % (esc(title), js, JS_COMMON))
    return page


# ---- v0.2 pages --------------------------------------------------------------------------------------------------

def sid_link(sid, live_ids):
    if sid in live_ids:
        return '<a class="sid" href="wireframes_v02.html#%s">%s</a>' % (esc(sid), esc(sid))
    return '<span class="sid">%s</span>' % esc(sid)


def live_screens(v02):
    """Screens drawn on the v0.2 pages: not dropped, not split (a split screen is its instances)."""
    return [s for s in v02["screens"] if s["v02"]["status"] not in ("dropped", "split")]


WIRE_LAYOUT = ('<div class="layout">\n<aside id="nav" class="nav"></aside>\n'
               '<main id="main" class="main"><div class="mobile-jump"><select id="jump"></select></div>'
               '<div id="ribbon" class="ribbon"></div><div class="crumb-row"><span id="crumb"></span><span id="counter"></span></div>'
               '<div id="statestrip" class="strip off"></div>'
               '<div class="stage"><button id="prev" class="arrow" title="Previous screen">&larr;</button><div id="frame" class="frame phone"></div>'
               '<button id="next" class="arrow" title="Next screen">&rarr;</button></div></main>\n'
               '<aside class="side"><div class="review"><div class="review-t">Your verdict on this screen</div>'
               '<div id="verdict" class="verdict"></div><div id="reason-wrap" class="reason-wrap off"><select id="reason"></select></div>'
               '<textarea id="comment"></textarea></div><div id="spec" class="spec"></div></aside>\n</div>\n<div id="map" class="map"></div>\n')


def build_wire_v02(v02, states, reasons, review=False):
    """review=True renders the docs/review/ copy: the same page with only the two v0.2 tabs and no setup link."""
    live = live_screens(v02)
    dropped = [s["id"] for s in v02["screens"] if s["v02"]["status"] == "dropped"]
    split = [s["id"] for s in v02["screens"] if s["v02"]["status"] == "split"]
    who = '<div class="who">Reviewing as <select id="reviewer"></select></div>'
    bar = ('<div class="bar"><div id="tiers" class="tiers"></div>'
           '<label>Path <select id="fpath"></select></label>'
           '<label id="fstate-wrap">State <select id="fstate"></select></label>'
           '<label>Compliance <select id="fcomp"></select></label>'
           '<label>Template <select id="ftpl"></select></label>'
           '<div class="actions"><button id="mapbtn">Journey map</button></div></div>\n'
           '<div class="banner">All copy is placeholder pending compliance review; comment on language on any screen.</div>\n')
    layout = WIRE_LAYOUT
    data = ('<script>var SECTIONS=' + js_blob(v02["sections"]) + ';\nvar SCREENS=' + js_blob(live) + ';\nvar DROPPED=' + js_blob(dropped) +
            ';\nvar SPLIT=' + js_blob(split) + ';\nvar STATES=' + js_blob(states["states"] if states else []) + ';\nvar REASONS=' + js_blob(reasons) + ';</script>\n')
    page = (head("yeslyf wireframes v0.2", read_script("renderer_v02.css")) + '<body>\n' +
            header("index.html" if review else "wireframes_v02.html", "wireframes v0.2, " + str(len(live)) + " screens", who_html=who,
                   export_label="Export comments", tabs=REVIEW_TABS if review else None, setup_link=not review) +
            bar + layout + data + '<script>' + read_script("renderer_v02.js") + '</script>\n</body>\n</html>\n')
    return page


def table_html(cols, rows):
    return ('<div class="wrap"><table><thead><tr>' + "".join('<th>%s</th>' % esc(c) for c in cols) + '</tr></thead><tbody>' +
            "".join('<tr>' + "".join('<td>%s</td>' % cell for cell in r) + '</tr>' for r in rows) + '</tbody></table></div>')


def cell(v):
    if isinstance(v, list):
        return esc(", ".join(str(x) for x in v))
    if isinstance(v, dict):
        return esc("; ".join("%s: %s" % (k, x) for k, x in v.items()))
    if isinstance(v, bool):
        return "yes" if v else "no"
    return esc(v)


def generic(value, headers=None):
    """Render any data shape as a table, a list or a paragraph; unknown shapes never break the build."""
    if value is None:
        return '<p class="meta">none</p>'
    if isinstance(value, str):
        return '<p>%s</p>' % esc(value)
    if isinstance(value, dict):
        if value and all(isinstance(x, dict) for x in value.values()):
            keys = []
            for x in value.values():
                for k in x:
                    if k not in keys:
                        keys.append(k)
            return table_html(["key"] + keys, [[esc(k)] + [cell(x.get(c, "")) for c in keys] for k, x in value.items()])
        return table_html(["key", "value"], [[esc(k), cell(v)] for k, v in value.items()])
    if isinstance(value, list):
        if not value:
            return '<p class="meta">none</p>'
        if all(isinstance(x, dict) for x in value):
            keys = []
            for x in value:
                for k in x:
                    if k not in keys:
                        keys.append(k)
            return table_html(keys, [[cell(x.get(c, "")) for c in keys] for x in value])
        if all(isinstance(x, list) for x in value):
            width = max(len(x) for x in value)
            cols = list(headers or [])
            while len(cols) < width:
                cols.append("col %d" % (len(cols) + 1))
            return table_html(cols[:width], [[cell(c) for c in x] + [""] * (width - len(x)) for x in value])
        return '<ul>' + "".join('<li>%s</li>' % cell(x) for x in value) + '</ul>'
    return '<p>%s</p>' % esc(value)


V01_ADMIN_SECTIONS = [
    ("STACK", "Stack: bought tools", None),
    ("PLACEMENT", "Placement: where each need lives", None),
    ("CONTACT_FIELDS", "Contact fields", ["Field", "Source and use"]),
    ("DEAL_FIELDS", "Deal fields", ["Field", "Detail"]),
    ("EVENTS", "Events: app to CRM", ["Event", "Screen", "Fields"]),
    ("INBOUND", "Inbound: CRM to app", ["Event", "Direction", "Fields"]),
    ("NUDGES", "Nudges (v0.1 matrix)", None),
    ("NUDGE_EXAMPLES", "Nudge examples", None),
    ("COMPLIANCE", "Compliance records", ["Record", "Where it lives", "Export"]),
    ("DECISIONS", "Decisions in the admin spec", None),
]
V02_ADMIN_SECTIONS = [
    ("note_v02", "Note on v0.2"),
    ("changes_v02", "Changes in v0.2"),
    ("PLACEMENT_NOTE", "Placement note (v0.2)"),
    ("DEAL_FIELDS_V02", "Deal fields added in v0.2"),
    ("CONTACT_FIELDS_V02", "Contact fields added in v0.2"),
    ("COMPLIANCE_NOTE", "Compliance records note (v0.2)"),
]


def nudge_matrix(states):
    if not states:
        return '<p class="meta">%s</p>' % esc(PENDING)
    rows = []
    for st in states["states"]:
        esc_ = st.get("escalation") or {}
        tier_rule = "; ".join("%s: %s" % (k.upper(), v) for k, v in esc_.items()) if isinstance(esc_, dict) else cell(esc_)
        task = st.get("crm_task") or {}
        if isinstance(task, dict):
            task_txt = ("yes: " + cell(task.get("fields", ""))) if task.get("created") else "no"
        else:
            task_txt = cell(task)
        ladder = st.get("ladder") or []
        if not ladder:
            rows.append([esc(st["id"]) + " " + esc(st.get("who", "")), "-", "-", "-", "-", esc(tier_rule), esc(task_txt)])
        for step in ladder:
            link = step.get("link", "")
            rows.append([esc(st["id"]) + " " + esc(st.get("who", "")), cell(step.get("day", "")), cell(step.get("channel", "")), cell(step.get("slot", "")),
                         esc(link), esc(tier_rule), esc(task_txt)])
    return table_html(["State", "Day", "Channel", "Copy slot", "Deep link", "Tier rule", "CRM task"], rows)


def admin_parts(admin, v02, states):
    """(nav links html, body html) of the Admin and CRM v0.2 page; shared with the team audience file."""
    live = live_screens(v02)
    body = ['<section><h1>Admin and CRM v0.2</h1><p class="lead">The v0.1 admin and CRM spec carried forward, then the v0.2 additions from plan_v2.md section 6: '
            'the platform is to be decided (one platform); the nudge matrix covers states S1 to S25; the CRM backlog holds what the team said to remember for the CRM planning session.</p>'
            '<p class="meta">Source: data/admin_crm.json and data/v02/states.json. The v0.1 spec is also served as-is on the Admin and CRM v0.1 tab.</p></section>']
    nav = []
    for key, title, headers in V01_ADMIN_SECTIONS:
        if key not in admin:
            continue
        sec_id = "a-" + key.lower()
        nav.append('<a href="#%s">%s</a>' % (sec_id, esc(title)))
        note = admin.get(key + "_NOTE_V02") or admin.get(key.lower() + "_note_v02")
        value = admin[key]
        if key == "DECISIONS":
            # owner_v01 is a v0.1 record kept in the data; the v0.2 page shows the question, the position and who stated it
            value = [{k: v for k, v in d.items() if k != "owner_v01"} for d in value]
        body.append('<section id="%s"><h2>%s</h2>%s%s</section>' % (sec_id, esc(title), ('<p class="rule">%s</p>' % esc(note)) if note else "", generic(value, headers)))
    body.append('<section id="a-v02"><h2>v0.2 additions</h2><p class="meta">Cause on every row where the data carries one.</p></section>')
    nav.append('<a href="#a-v02">v0.2 additions</a>')
    for key, title in V02_ADMIN_SECTIONS:
        if key in admin:
            sec_id = "a-" + key.lower()
            nav.append('<a class="sub" href="#%s">%s</a>' % (sec_id, esc(title)))
            body.append('<section id="%s"><h3>%s</h3>%s</section>' % (sec_id, esc(title), generic(admin[key])))
    v02_dec = [d for d in admin.get("DECISIONS", []) if d.get("id") not in ("D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8")]
    if v02_dec:
        nav.append('<a class="sub" href="#a-decisions-v02">Decisions added in v0.2</a>')
        body.append('<section id="a-decisions-v02"><h3>Decisions added in v0.2</h3>%s</section>' % generic(v02_dec))
    nav.append('<a class="sub" href="#a-events-v02">Events v0.2</a>')
    body.append('<section id="a-events-v02"><h3>Events v0.2 (every live screen, appendix D)</h3>%s</section>' % table_html(
        ["Screen", "Template", "Events"], [[sid_link(s["id"], {x["id"] for x in live}), esc(s["template"]), esc(", ".join(s.get("events", [])))] for s in live]))
    nav.append('<a class="sub" href="#a-nudges-v02">Nudges matrix v0.2</a>')
    body.append('<section id="a-nudges-v02"><h3>Nudges matrix v0.2 (one row per state per ladder step)</h3>%s%s</section>' % (
        ('<ul>' + "".join('<li>%s</li>' % esc(r) for r in states.get("rules", [])) + '</ul>') if states and states.get("rules") else "", nudge_matrix(states)))
    nav.append('<a href="#a-backlog">CRM backlog</a>')
    backlog = admin.get("CRM_BACKLOG")
    body.append('<section id="a-backlog"><h2>CRM backlog</h2><p class="lead">Items the team said to remember for the CRM planning session.</p>%s</section>' % (
        generic(backlog) if backlog else '<p class="meta">arrives with phase 6 (CRM_BACKLOG in data/admin_crm.json)</p>'))
    return "".join(nav), "\n".join(body)


def build_admin_v02(admin, v02, states, review=False):
    """review=True renders the docs/review/ copy; its screen links point at the review copy of Wireframes v0.2."""
    nav, body = admin_parts(admin, v02, states)
    if review:
        body = body.replace('href="wireframes_v02.html#', 'href="index.html#')
    page = (head("yeslyf admin and CRM v0.2") + '<body>\n' +
            header("admin_v02.html", "admin and CRM v0.2", show_export=False, tabs=REVIEW_TABS if review else None, setup_link=not review) +
            '<div class="layout"><nav class="nav">' + nav + '</nav><main class="main" style="max-width:none">' + body +
            '</main></div>\n<script>' + JS_PILL + '</script>\n</body>\n</html>\n')
    return page


def changelog_parts(chg, v02, audiences=None):
    """(nav links html, body html) of the Changelog page; audiences (name, for, href, bytes) adds the audience-file
    section. Shared with the team audience file, which passes no audiences."""
    live_ids = {s["id"] for s in live_screens(v02)}
    c = chg["counts"]
    split = chg.get("split", [])
    body = ['<section><h1>Changelog: v0.1 to v0.2</h1><p class="lead">Every touched screen with its cause: a brief item, a review row, "Vatsal, 10 Sep 2026" or "Vatsal, 11 Sep 2026". '
            'Dropped screens keep their ID and point to where their content went; split screens keep their ID and list their instances. Counts for Spinach are at the end.</p>'
            '<div class="stats"><div class="stat"><b>%d</b><span>screens in v0.2</span></div><div class="stat"><b>%d</b><span>changed</span></div>'
            '<div class="stat"><b>%d</b><span>added</span></div><div class="stat"><b>%d</b><span>dropped</span></div><div class="stat"><b>%d</b><span>split</span></div><div class="stat"><b>%d</b><span>branches rerouted</span></div>'
            '<div class="stat"><b>%d</b><span>brief items superseded</span></div><div class="stat"><b>%d</b><span>to be verified</span></div><div class="stat"><b>%d</b><span>templates</span></div></div></section>' % (
                c["total"], len(chg["changed"]), len(chg["added"]), len(chg["dropped"]), len(split), len(chg["rerouted"]), len(chg["superseded"]), len(chg["to_be_verified"]), c["unique_templates"])]
    body.append('<section id="c-changed"><h2>Changed<small>%d screens</small></h2>%s</section>' % (len(chg["changed"]), table_html(
        ["Screen", "Title", "Status", "Cause"], [[sid_link(x["id"], live_ids), esc(x["title"]), '<span class="tag changed">%s</span>' % esc(x["status"]), esc("; ".join(x["causes"]))] for x in chg["changed"]])))
    body.append('<section id="c-added"><h2>Added<small>%d screens</small></h2>%s</section>' % (len(chg["added"]), table_html(
        ["Screen", "Title", "Template", "Cause"], [[sid_link(x["id"], live_ids), esc(x["title"]), esc(x.get("template", "")), esc("; ".join(x["causes"]))] for x in chg["added"]])))
    body.append('<section id="c-dropped"><h2>Dropped<small>%d screens; IDs stay reserved</small></h2>%s</section>' % (len(chg["dropped"]), table_html(
        ["Screen", "Title", "Where the content went", "Cause"], [[esc(x["id"]), esc(x["title"]), esc(x["pointer"]), esc("; ".join(x["causes"]))] for x in chg["dropped"]])))
    body.append('<section id="c-split"><h2>Split<small>%d screens; IDs stay reserved; each is drawn as its instances</small></h2>%s</section>' % (len(split), table_html(
        ["Screen", "Title", "Instances", "Cause"], [[esc(x["id"]), esc(x["title"]), " ".join(sid_link(i, live_ids) for i in x["instances"]), esc("; ".join(x["causes"]))] for x in split])))
    body.append('<section id="c-rerouted"><h2>Rerouted branches<small>%d</small></h2>%s</section>' % (len(chg["rerouted"]), table_html(
        ["Screen", "Branch", "From", "To", "Cause"], [[sid_link(x["screen"], live_ids), esc(x["label"]), esc(x["from"]), sid_link(x["to"], live_ids), esc(x.get("cause", ""))] for x in chg["rerouted"]])))
    body.append('<section id="c-superseded"><h2>Superseded brief items<small>plan_v2.md section 0</small></h2>%s</section>' % table_html(
        ["Item", "The brief recorded", "Applied instead", "Cause"], [[esc(x["item"]), esc(x["brief"]), esc(x["override"]), esc(x["cause"])] for x in chg["superseded"]]))
    body.append('<section id="c-tbv"><h2>To be verified<small>%d items, by item</small></h2>%s</section>' % (len(chg["to_be_verified"]), table_html(
        ["Item", "Screens"], [[esc(x["item"]), " ".join(sid_link(s, live_ids) for s in x["screens"])] for x in chg["to_be_verified"]])))
    by_sec_rows = []
    for sec, info in c["by_section"].items():
        by_sec_rows.append([esc(sec), esc(info["name"]), str(info["screens"]), str(info["templates"]), esc(", ".join("%s %d" % kv for kv in info["by_template"].items()))])
    body.append('<section id="c-counts"><h2>Counts for Spinach<small>templates and instances</small></h2>'
                '<p class="meta">%d screens in v0.2 across %d unique templates. Status: %s.</p><h3>By section</h3>%s<h3>By template</h3>%s</section>' % (
                    c["total"], c["unique_templates"], esc(", ".join("%s %d" % kv for kv in sorted(c["by_status"].items()))),
                    table_html(["Section", "Name", "Screens", "Templates", "Instances per template"], by_sec_rows),
                    table_html(["Template", "Screens"], [[esc(k), str(v)] for k, v in c["by_template"].items()])))
    entries = [("c-changed", "Changed"), ("c-added", "Added"), ("c-dropped", "Dropped"), ("c-split", "Split"), ("c-rerouted", "Rerouted branches"),
               ("c-superseded", "Superseded brief items"), ("c-tbv", "To be verified"), ("c-counts", "Counts for Spinach")]
    if audiences:
        body.append('<section id="c-audiences"><h2>Audience files<small>self-contained; each opens from disk with no network</small></h2>'
                    '<p class="meta">Generated by scripts/build_audiences.py from the same data. Comment controls and the markdown export work offline; the sheet endpoint field is blank.</p>%s</section>' % table_html(
                        ["File", "For", "Size"], [['<a href="%s">%s</a>' % (esc(a["href"]), esc(a["name"])), esc(a["for"]), esc("%d KB (%d bytes)" % (round(a["bytes"] / 1024), a["bytes"]))] for a in audiences]))
        entries.append(("c-audiences", "Audience files"))
    nav = "".join('<a href="#%s">%s</a>' % (a, b) for a, b in entries)
    return nav, "\n".join(body)


def build_changelog(chg, v02, audiences=None):
    nav, body = changelog_parts(chg, v02, audiences)
    page = (head("yeslyf changelog v0.1 to v0.2") + '<body>\n' + header("changelog.html", "changelog, v0.1 to v0.2", show_export=False) +
            '<div class="layout"><nav class="nav">' + nav + '</nav><main class="main">' + body + '</main></div>\n<script>' + JS_PILL + '</script>\n</body>\n</html>\n')
    return page


def build_setup():
    steps = ('<section class="setup"><h1>Setup: sheet write-back</h1>'
             '<p class="lead">The site works without this: choices save per browser and Export brief produces the record. With an endpoint, every change is also appended to the Google Sheet "yeslyf decisions" as it happens, from every device, no login needed for anyone.</p>'
             '<label>Endpoint URL (Apps Script web app)</label><input id="endpoint" placeholder="https://script.google.com/macros/s/.../exec">'
             '<p class="meta">Stored in this browser only. Each person pastes it once, or opens the site with ?endpoint=... (see below). <button id="testrow" class="ghost">Send a test row</button></p>'
             '<h3>Three steps (about three minutes)</h3><ol>'
             '<li>Open the Google Sheet "yeslyf decisions" in Vatsal\'s Drive (created 9 Sep 2026; Vatsal shares the link). Extensions, Apps Script. Replace the code with the block below. Save.</li>'
             '<li>Deploy, New deployment, type Web app. Execute as: Me. Who has access: Anyone. Deploy, authorise, copy the web app URL.</li>'
             '<li>Paste the URL in the field above on each device that will take decisions, or share the link index.html?endpoint=THE_URL once; the page stores it and then removes it from the address bar.</li></ol>'
             '<p class="rule">v0.2 review comments post to the tab v02_comments when the deployed script accepts a tab field; the script below does, but no redeploy is planned (spiff, 11 Sep 2026). Reviewers press Export comments on the Wireframes v0.2 tab and send the markdown file to spiff</p>'
             '<details open><summary>Apps Script (doPost appends a row to the right tab; creates the tabs on first use)</summary><pre id="script"></pre></details>'
             '<details><summary>Sheet columns (also in sheet_template.csv)</summary><pre>decisions:     ts, who, item_id, choice, choice_text, note\n'
             'gaps:          ts, who, gap_id, status, owner_date, note\nquick_accepts: ts, who, input_n, accept, note\nv02_comments:  ts, who, screen, verdict, reason, text</pre>'
             '<p class="meta"><a href="sheet_template.csv">Download sheet_template.csv</a> (one block per tab, to paste if you prefer to create the tabs by hand).</p></details>'
             '<details><summary>Read path after the meeting</summary><p class="meta">File, Share, Publish to web, the whole document as CSV; give Vatsal the link. scripts/pull_sheet.py reads it; last write per item wins; every row is kept in data/decisions_raw.json.</p></details>'
             '</section>')
    js = ('document.getElementById("script").textContent=' + json.dumps(APPS_SCRIPT) + ';'
          '')
    page = (head("yeslyf product board: setup") + '<body>\n' + header("setup.html", "product board, setup", show_export=False) +
            '<main class="main">' + steps + '</main>\n<script>' + js + '</script>\n<script>' + JS_COMMON + '</script>\n</body>\n</html>\n')
    return page


APPS_SCRIPT = """function doPost(e) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var d = JSON.parse(e.postData.contents);
  var tabs = {
    decisions: ["ts", "who", "item_id", "choice", "choice_text", "note"],
    gaps: ["ts", "who", "gap_id", "status", "owner_date", "note"],
    quick_accepts: ["ts", "who", "input_n", "accept", "note"],
    v02_comments: ["ts", "who", "screen", "verdict", "reason", "text"]
  };
  var name = (d.tab && String(d.tab).length) ? String(d.tab) : (tabs[d.kind] ? d.kind : "other");
  var cols = tabs[name] || ((d.cols && d.cols.length) ? d.cols : ["ts", "who", "kind", "payload"]);
  var sh = ss.getSheetByName(name);
  if (!sh) { sh = ss.insertSheet(name); sh.appendRow(cols); }
  var row = cols.map(function (c) { return c === "payload" ? JSON.stringify(d) : (d[c] === undefined ? "" : d[c]); });
  sh.appendRow(row);
  return ContentService.createTextOutput("ok");
}
"""

SHEET_TEMPLATE = """# tab: decisions
ts,who,item_id,choice,choice_text,note
# tab: gaps
ts,who,gap_id,status,owner_date,note
# tab: quick_accepts
ts,who,input_n,accept,note
# tab: v02_comments
ts,who,screen,verdict,reason,text
"""


def check_ascii(name, text):
    for i, ch in enumerate(text):
        if ord(ch) > 126:
            raise SystemExit("%s: non-ASCII character at %d: %r" % (name, i, text[max(0, i - 30):i + 10]))


def main():
    items = load("open_items.json")["items"]
    inputs = load("inputs.json")["rows"]
    gaps = load("gaps.json")["gaps"]
    ownership = load("ownership.json")["workstreams"]
    screens = load("screens_v01.json")["screens"]
    decisions = load("decisions.json")
    v02 = load("screens_v02.json")
    changelog = load("changelog.json")
    reasons = load("compliance_reasons.json")["reasons"]
    admin = load("admin_crm.json")
    states = load_optional("v02", "states.json")

    os.makedirs(os.path.join(DOCS, "v01"), exist_ok=True)
    for f in V01_FILES:
        shutil.copyfile(os.path.join(V01_IN, f), os.path.join(DOCS, "v01", f))
    import build_audiences
    aud_pages = build_audiences.build_all(v02, states, reasons, admin, changelog)
    os.makedirs(os.path.join(DOCS, "audiences"), exist_ok=True)
    audiences = []
    for name, (text, who) in aud_pages.items():
        check_ascii(name, text)
        with open(os.path.join(DOCS, "audiences", name), "w") as fh:
            fh.write(text)
        audiences.append({"name": name, "for": who, "href": "audiences/" + name, "bytes": len(text)})
    pages = {
        "index.html": build_meeting(items, inputs, gaps, decisions, audiences),
        "gaps.html": build_gaps(items, inputs, gaps, decisions),
        "inputs.html": build_inputs(items, inputs, gaps, ownership, frozen=True),
        "wireframes.html": build_frame_page("wireframes.html", "wireframes v0.1, served as-is", "yeslyf wireframes v0.1", WIRE, screens),
        "admin.html": build_frame_page("admin.html", "admin and CRM spec v0.1, served as-is", "yeslyf admin and CRM spec v0.1", ADMIN),
        "wireframes_v02.html": build_wire_v02(v02, states, reasons),
        "admin_v02.html": build_admin_v02(admin, v02, states),
        "changelog.html": build_changelog(changelog, v02, audiences),
        "setup.html": build_setup(),
        "sheet_template.csv": SHEET_TEMPLATE,
        "review/index.html": build_wire_v02(v02, states, reasons, review=True),
        "review/admin_v02.html": build_admin_v02(admin, v02, states, review=True),
    }
    os.makedirs(os.path.join(DOCS, "review"), exist_ok=True)
    for name, text in pages.items():
        check_ascii(name, text)
        with open(os.path.join(DOCS, name), "w") as fh:
            fh.write(text)
    with open(os.path.join(DOCS, ".nojekyll"), "w") as fh:
        fh.write("")
    with open(os.path.join(DATA, "sheet_template.csv"), "w") as fh:
        fh.write(SHEET_TEMPLATE)

    # acceptance checks on the generated pages
    problems = []
    meeting = pages["index.html"]
    n_dep = sum(len(it.get("dependencies", [])) for it in items)
    markup = meeting.replace(JS_COMMON, "")  # the export template carries the dependency label once
    if markup.lower().count("recommendation") != n_dep:
        problems.append("meeting page: 'recommendation' appears %d times, expected %d (dependency blocks only)" % (markup.lower().count("recommendation"), n_dep))
    for name, text in pages.items():
        if name.endswith(".html") and 'name="robots" content="noindex' not in text:
            problems.append(name + " lacks noindex")
    for name in V02_PAGES + list(aud_pages.keys()):
        text = pages[name] if name in pages else aud_pages[name][0]
        if name in aud_pages and 'name="robots" content="noindex' not in text:
            problems.append("audiences/" + name + " lacks noindex")
        for word in FORBIDDEN:
            i = text.find(word)
            while i >= 0:
                problems.append("%s contains %r: ...%s..." % (name, word, text[max(0, i - 50):i + len(word) + 30].replace("\n", " ")))
                i = text.find(word, i + 1)
    for it in items:
        if it["owner"] == ["Team"] and ('name="item-%s"' % it["id"]) in meeting and ("checked" in meeting.split('id="item-%s"' % it["id"])[1].split("</div>\n<div class=\"item\"")[0].split("<textarea")[0]):
            problems.append("Team item %s has something preselected" % it["id"])
    for f in V01_FILES:
        if not filecmp.cmp(os.path.join(V01_IN, f), os.path.join(DOCS, "v01", f), shallow=False):
            problems.append("docs/v01/%s differs from inputs/v01/" % f)
    if problems:
        for p in problems[:60]:
            print("ERROR: " + p)
        if len(problems) > 60:
            print("ERROR: ... %d more" % (len(problems) - 60))
        sys.exit(1)
    for name, text in pages.items():
        print("wrote docs/%s (%d bytes)" % (name, len(text)))
    for a in audiences:
        print("wrote docs/%s (%d bytes, for %s)" % (a["href"], a["bytes"], a["for"]))
    print("copied %d v0.1 files into docs/v01/ unchanged" % len(V01_FILES))
    if states is None:
        print("note: data/v02/states.json absent; the state filter and the nudge matrix show the placeholder line")
    import build_integrations  # docs/integrations.html and docs/review/integrations.html from data/integrations.json (phase 10b)
    build_integrations.main()
    import build_events  # docs/events.html and docs/review/events.html from the screens data and data/events_extra.json (phase 10b-2)
    build_events.main()


if __name__ == "__main__":
    main()
