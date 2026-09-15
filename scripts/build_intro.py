#!/usr/bin/env python3
"""Intro deck for Spinach (phase 10a, Vatsal, 15 Sep 2026): docs/intro.html and the self-contained
docs/audiences/yeslyf_intro_spinach.html from data/story.json and the nine golden-path screens of
data/screens_v02.json. Run from scripts/build_site.py, or alone to rebuild just these two files.

Nothing on a slide is drawn by hand: the text comes from story.json, the frames from the screens data through the
v0.2 element grammar (esc and el, copied verbatim from scripts/renderer_v02.js into scripts/intro.js; the build stops
if the copy drifts). Slide 5 embeds five fields of each of the nine screens (id, title, template, frame, ui) and
nothing else, so no spec, causes or compliance notes reach the file. Both files open with no network; noindex on each.
Both copies open a frame in the review copy of Wireframes v0.2 (docs/review/, the one link for everyone; Vatsal,
15 Sep 2026): the site copy by a relative link, the audience copy, which opens from disk, by the Pages URL.
"""
import os
import sys

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS)
import build_site as site  # noqa: E402

FILE = "yeslyf_intro_spinach.html"
SITE_LINK = "review/index.html#"
REVIEW_LINK = "https://spiffler33.github.io/yeslyf-wireframes/review/index.html#"
FRAME_FIELDS = ("id", "title", "template", "frame", "ui")
COPY_MARKS = [("  // BEGIN copy esc", "  // END copy esc"), ("  // BEGIN copy el", "  // END copy el")]


def check_copy(intro_js, renderer_js):
    """Each block between the copy markers in intro.js must still appear verbatim in renderer_v02.js."""
    for begin, end in COPY_MARKS:
        a = intro_js.find(begin)
        b = intro_js.find(end)
        if a < 0 or b < 0 or b < a:
            raise SystemExit("intro.js: copy markers %r / %r not found" % (begin, end))
        block = intro_js[intro_js.index("\n", a) + 1:b].rstrip("\n")
        if block not in renderer_js:
            raise SystemExit("intro.js: the block after %r no longer matches scripts/renderer_v02.js; recopy it" % begin)


def frames_for(story, v02):
    """The nine golden-path screens, five fields each, in slide order; the build stops if one does not resolve."""
    live = {s["id"]: s for s in site.live_screens(v02)}
    frames = []
    for sl in story["slides"]:
        for sid in sl.get("frames", []):
            if sid not in live:
                raise SystemExit("story.json: frame %s is not a live v0.2 screen" % sid)
            frames.append({k: live[sid][k] for k in FRAME_FIELDS})
    return frames


def check_story(story):
    slides = story["slides"]
    if len(slides) != 10:
        raise SystemExit("story.json: expected 10 slides, found %d" % len(slides))
    for n, sl in enumerate(slides, 1):
        if not sl.get("title") or not sl.get("say") or not (sl.get("lines") or sl.get("frames")):
            raise SystemExit("story.json: slide %d needs a title, a say line, and lines or frames" % n)
    if slides[0]["lines"][0] != story["purpose"]["line"]:
        raise SystemExit("story.json: the purpose line must be the first line of slide 1")


def slide_html(n, sl, story):
    parts = ['<section class="slide%s%s" id="s%d">' % (" on" if n == 1 else "", " frames" if sl.get("frames") else "", n),
             '<h1>%s</h1>' % site.esc(sl["title"])]
    if sl.get("frames"):
        parts.append('<div id="grid" class="grid"></div>')
    else:
        for line in sl["lines"]:
            if n == 1 and line == story["purpose"]["line"]:
                parts.append('<p class="line purpose">%s</p><span class="tag">%s</span>' % (site.esc(line), site.esc(story["purpose"]["marker"])))
            else:
                parts.append('<p class="line">%s</p>' % site.esc(line))
    parts.append('<aside class="say"><b>Say</b>%s</aside></section>\n' % site.esc(sl["say"]))
    return "".join(parts)


def page(story, frames, link, title):
    css = site.read_script("renderer_v02.css") + site.read_script("intro.css")
    body = ['<main class="deck">\n'] + [slide_html(n, sl, story) for n, sl in enumerate(story["slides"], 1)]
    body.append('</main>\n<div id="counter" class="counter">1 / %d</div>\n' % len(story["slides"]))
    data = '<script>var FRAMES=' + site.js_blob(frames) + ';\nvar LINK=' + site.js_blob(link) + ';</script>\n'
    return (site.head(title, css) + '<body>\n' + "".join(body) + data +
            '<script>' + site.read_script("intro.js") + '</script>\n</body>\n</html>\n')


def build_all(v02, story):
    """{path under docs/: html} for the two files."""
    check_story(story)
    check_copy(site.read_script("intro.js"), site.read_script("renderer_v02.js"))
    frames = frames_for(story, v02)
    return {"intro.html": page(story, frames, SITE_LINK, story["title"]),
            "audiences/" + FILE: page(story, frames, REVIEW_LINK, story["title"] + ", " + story["for"] + " file")}


def main():
    v02 = site.load("screens_v02.json")
    story = site.load("story.json")
    out = build_all(v02, story)
    os.makedirs(os.path.join(site.DOCS, "audiences"), exist_ok=True)
    for name, text in out.items():
        site.check_ascii(name, text)
        if 'name="robots" content="noindex' not in text:
            raise SystemExit(name + " lacks noindex")
        for word in site.FORBIDDEN:
            if word in text:
                raise SystemExit("%s contains %r" % (name, word))
        with open(os.path.join(site.DOCS, name), "w") as fh:
            fh.write(text)
        print("wrote docs/%s (%d bytes)" % (name, len(text)))


if __name__ == "__main__":
    main()
