#!/usr/bin/env python3
"""Read-only production Chromium acceptance of existing source-preserving Gutenberg repairs.

No requests to WordPress, Facebook, or other third parties. This is computed-style
QA, not Newspack pixel parity, manual screen-reader certification, or rights approval.
"""
import copy
import hashlib
import json
import math
import os
import re
from pathlib import Path
from urllib.parse import urlsplit

ORIGIN = "https://casa-hacienda-makati.vercel.app"
ROOT = Path(__file__).resolve().parent.parent
LOCK = json.loads((ROOT / "ops/published-search-sources.json").read_text())
KEY_ROUTES = {
    "/about/",
    "/cultural-significance/",
    "/2023/08/12/cultural-significance-no-1/",
    "/2023/10/21/history-of-barrio-olimpia-makati-rizal/",
    "/2024/10/28/cultural-significance-no-12/",
}
COLOR = {
    "has-primary-color": "rgb(28, 59, 48)",
    "has-foreground-color": "rgb(36, 62, 48)",
    "has-black-color": "rgb(17, 17, 17)",
}
SNAPSHOT = r"""() => {
  const article = document.querySelector('article.content');
  if (!article) throw Error('missing article');
  const style = e => getComputedStyle(e);
  const colors = {};
  for (const cls of ['has-primary-color','has-foreground-color','has-black-color'])
    colors[cls] = [...article.querySelectorAll('.'+cls+'.has-text-color')].map(e=>style(e).color);
  const rules = [...article.querySelectorAll('.wp-block-separator')].map(e=>({
    width:e.getBoundingClientRect().width,
    border:style(e).borderBottomStyle,
    thickness:style(e).borderBottomWidth
  }));
  const frames = [...article.querySelectorAll('p.has-border-color.has-base-border-color')].map(e=>({
    width:style(e).borderTopWidth, type:style(e).borderTopStyle, color:style(e).borderTopColor
  }));
  const galleries = [...article.querySelectorAll('.wp-block-gallery.has-nested-images')].map(e=>({
    columns:style(e).gridTemplateColumns.split(' ').filter(Boolean).length,
    figures:e.querySelectorAll(':scope > figure.wp-block-image').length
  }));
  const table = article.querySelector('.wp-block-group.has-accent-background-color.has-background');
  const tableFigure = article.querySelector('.wp-block-table.is-style-stripes');
  const indents = [...article.querySelectorAll('p[style*="padding-left:var(--wp--preset--spacing--70)"]')]
    .map(e=>parseFloat(style(e).paddingLeft));
  const aboutMargin = article.querySelector('.wp-block-columns[style*="margin-top:var(--wp--preset--spacing--70)"]');
  const significanceHeading = article.querySelector('h2[style*="padding-bottom:var(--wp--preset--spacing--60)"]');
  return {
    articleCount:document.querySelectorAll('article.content').length,
    robots:document.querySelector('meta[name="robots"]')?.content,
    stylesheetCount:document.styleSheets.length,
    overflow:document.documentElement.scrollWidth > innerWidth + 2,
    colors, rules, frames, galleries, indents,
    aboutMargin:aboutMargin ? parseFloat(style(aboutMargin).marginTop) : null,
    headingPadding:significanceHeading ? parseFloat(style(significanceHeading).paddingBottom) : null,
    table:table && tableFigure ? {
      background:style(table).backgroundColor,
      width:tableFigure.getBoundingClientRect().width,
      viewport:innerWidth,
      rows:tableFigure.querySelectorAll('tr').length,
      stripe:style(tableFigure.querySelector('tbody tr:nth-child(even)')).backgroundColor
    } : null
  };
}"""

def source_inventory():
    css = (ROOT / "public/assets/style.css").read_bytes()
    css_blob = hashlib.sha1(b"blob " + str(len(css)).encode() + b"\0" + css).hexdigest()
    assert css_blob == LOCK["stylesheetGitBlob"], "Reviewed stylesheet source lock changed"
    docs = LOCK["documents"]
    assert len(docs) == 15
    assert sum(d["type"] == "article" for d in docs) == 13
    assert sum(d["type"] == "page" for d in docs) == 2
    total = {"has-primary-color": 0, "has-foreground-color": 0,
             "has-black-color": 0, "wp-block-separator": 0,
             "has-base-border-color": 0, "has-nested-images": 0}
    inventory = {}
    for doc in docs:
        path = ROOT / "public" / doc["file"]
        raw = path.read_bytes()
        digest = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        assert digest == doc["gitBlob"], "Original WordPress source changed: " + doc["file"]
        html = raw.decode("utf-8")
        assert '<meta name="robots" content="noindex,nofollow">' in html
        classes = [set(c.split()) for c in re.findall(r'class="([^"]+)"', html)]
        counts = {key: sum(key in c for c in classes) for key in total}
        for key in COLOR:
            assert all("has-text-color" in c for c in classes if key in c)
        for key in total:
            total[key] += counts[key]
        inventory["/" + doc["file"].removesuffix("index.html")] = counts
    assert total == {
        "has-primary-color": 16, "has-foreground-color": 55,
        "has-black-color": 5, "wp-block-separator": 25,
        "has-base-border-color": 12, "has-nested-images": 2
    }, total
    assert inventory["/cultural-significance/"]["has-base-border-color"] == 12
    return inventory

def validate(s, counts, route, width):
    assert s["status"] == 200 and re.fullmatch(r"noindex\s*,\s*nofollow", s["header"] or "", re.I)
    assert s["robots"] == "noindex,nofollow" and s["articleCount"] == 1
    assert s["stylesheetCount"] >= 1 and s["overflow"] is False
    for key, rgb in COLOR.items():
        assert len(s["colors"][key]) == counts[key], (route, key)
        assert all(color == rgb for color in s["colors"][key]), (route, key, "color")
    assert len(s["rules"]) == counts["wp-block-separator"], (route, "separator inventory")
    expected = min(168.0, width * 0.13)  # Verified current WordPress spacing-60
    for rule in s["rules"]:
        assert (abs(rule["width"] - expected) <= 0.8 and
                rule["border"] == "solid" and rule["thickness"] == "1px"), (route, width, rule)
    assert len(s["frames"]) == counts["has-base-border-color"], (route, "frame inventory")
    assert all(f == {"width": "15px", "type": "solid", "color": "rgb(252, 249, 241)"}
               for f in s["frames"]), (route, "frame styling")
    assert len(s["galleries"]) == counts["has-nested-images"], (route, "gallery inventory")
    if route == "/2023/08/12/cultural-significance-no-1/":
        assert s["galleries"] == [{"columns": 1 if width == 320 else 2 if width == 375 else 3,
                                    "figures": 3}], (route, "gallery grid")
    if route == "/2023/10/21/history-of-barrio-olimpia-makati-rizal/":
        assert s["galleries"] == [{"columns": 1 if width == 320 else 2 if width == 375 else 4,
                                    "figures": 7}], (route, "gallery grid")
        assert len(s["indents"]) == 29 and all(abs(v - 54.08) <= 0.5 for v in s["indents"]), "Olympia paragraph indents"
    if route == "/about/":
        assert s["aboutMargin"] is not None and abs(s["aboutMargin"] - 54.08) <= 0.5, "About column margin"
    if route == "/cultural-significance/":
        assert s["headingPadding"] is not None and abs(s["headingPadding"] - min(168.0, width * 0.13)) <= 0.8, "Significance heading spacing"
    if route == "/2024/10/28/cultural-significance-no-12/":
        table = s["table"]
        assert table and table["background"] == "rgb(240, 226, 201)"
        assert table["stripe"] == "rgb(244, 240, 232)" and table["rows"] == 5
        assert table["width"] <= table["viewport"] + 1, "Table overflows page"
    return True

def self_test(inventory):
    route = "/cultural-significance/"
    counts = inventory[route]
    sample = {
        "status": 200, "header": "noindex,nofollow", "robots": "noindex,nofollow",
        "articleCount": 1, "stylesheetCount": 1, "overflow": False,
        "colors": {k: [v] * counts[k] for k, v in COLOR.items()},
        "rules": [{"width": 48.75, "border": "solid", "thickness": "1px"}] * counts["wp-block-separator"],
        "frames": [{"width": "15px", "type": "solid", "color": "rgb(252, 249, 241)"}] * 12,
        "galleries": [], "indents": [], "aboutMargin": None, "headingPadding": 48.75, "table": None
    }
    validate(sample, counts, route, 375)
    changes = [
        ("status", lambda x: x.update(status=404)),
        ("privacy-header", lambda x: x.update(header="index,follow")),
        ("privacy-meta", lambda x: x.update(robots="index,follow")),
        ("stylesheet", lambda x: x.update(stylesheetCount=0)),
        ("overflow", lambda x: x.update(overflow=True)),
        ("frames-count", lambda x: x["frames"].pop()),
        ("frame-style", lambda x: x["frames"][0].update(type="none")),
        ("frame-width", lambda x: x["frames"][0].update(width="0px")),
        ("frame-color", lambda x: x["frames"][0].update(color="transparent")),
        ("heading-spacing", lambda x: x.update(headingPadding=0)),
        ("old-heading-spacing", lambda x: x.update(headingPadding=36)),
        ("article", lambda x: x.update(articleCount=0)),
    ]
    if counts["wp-block-separator"]:
        changes.append(("separator", lambda x: x["rules"][0].update(thickness="0px")))
    for key in COLOR:
        if counts[key]:
            changes.append((key + "-color", lambda x, k=key: x["colors"][k].__setitem__(0, "rgb(255, 255, 255)")))
    for name, mutate in changes:
        item = copy.deepcopy(sample)
        mutate(item)
        try:
            validate(item, counts, route, 375)
        except (AssertionError, KeyError):
            pass
        else:
            raise AssertionError("Negative fixture did not fail closed: " + name)
    sep_route = "/2023/08/12/cultural-significance-no-1/"
    sep_counts = inventory[sep_route]
    sep = copy.deepcopy(sample)
    sep["colors"] = {k: [v] * sep_counts[k] for k, v in COLOR.items()}
    sep["rules"] = [{"width": 48.75, "border": "solid", "thickness": "1px"}
                    for _ in range(sep_counts["wp-block-separator"])]
    sep["frames"] = []
    sep["headingPadding"] = None
    sep["galleries"] = [{"columns": 2, "figures": 3}]
    validate(sep, sep_counts, sep_route, 375)
    separator_mutations = [
        ("old-100px-width", lambda x: x["rules"][0].update(width=100)),
        ("old-2px-border", lambda x: x["rules"][0].update(thickness="2px")),
        ("missing-solid-border", lambda x: x["rules"][0].update(border="none")),
        ("missing-separator", lambda x: x["rules"].pop()),
    ]
    for name, mutate in separator_mutations:
        changed = copy.deepcopy(sep)
        mutate(changed)
        try:
            validate(changed, sep_counts, sep_route, 375)
        except (AssertionError, KeyError):
            pass
        else:
            raise AssertionError("Negative separator fixture did not fail: " + name)
    for width in (320, 375, 1280):
        changed = copy.deepcopy(sample)
        changed["headingPadding"] = min(168.0, width * 0.13)
        validate(changed, counts, route, width)
    print("Recent Gutenberg production QA: source inventory and",
          len(changes) + len(separator_mutations), "negative fixtures PASS")

def run_live(inventory):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            context = browser.new_context(reduced_motion="reduce", service_workers="block")
            blocked = []
            def restrict(route):
                parsed = urlsplit(route.request.url)
                if (parsed.scheme, parsed.netloc) == ("https", urlsplit(ORIGIN).netloc):
                    route.continue_()
                else:
                    blocked.append(parsed.netloc)
                    route.abort()
            context.route("**/*", restrict)
            page = context.new_page()
            checks = 0
            evidence = []
            for route, counts in inventory.items():
                for width in ((320, 375, 1280) if route in KEY_ROUTES else (375,)):
                    page.set_viewport_size({"width": width, "height": 812})
                    response = page.goto(ORIGIN + route, wait_until="domcontentloaded", timeout=45000)
                    assert response is not None, "No production response: " + route
                    page.wait_for_function("document.styleSheets.length >= 1", timeout=20000)
                    s = page.evaluate(SNAPSHOT)
                    s["status"] = response.status
                    s["header"] = response.headers.get("x-robots-tag")
                    validate(s, counts, route, width)
                    evidence.append({"route": route, "viewport": width,
                                     "separators": s["rules"], "headingPadding": s["headingPadding"],
                                     "robots": s["robots"], "header": s["header"],
                                     "overflow": s["overflow"]})
                    checks += 1
            context.close()
            assert checks == 25, ("Unexpected published route/viewport inventory", checks)
            out = ROOT / "artifacts/live-current-wordpress-tokens.json"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps({"scope": "15 source-locked published routes; 25 production Chromium visits",
                                       "stylesheetGitBlob": LOCK["stylesheetGitBlob"],
                                       "checks": evidence}, indent=2) + "\n")
            print("Recent Gutenberg production QA:", checks, "real Chromium route/viewport checks PASS")
            print("Third-party requests aborted:", len(blocked))
        finally:
            browser.close()

if __name__ == "__main__":
    inventory = source_inventory()
    self_test(inventory)
    if os.environ.get("CHM_SELF_TEST") != "1":
        run_live(inventory)
