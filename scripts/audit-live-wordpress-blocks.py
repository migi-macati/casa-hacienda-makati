#!/usr/bin/env python3
"""Read-only exact-production Chromium checks for already-published Gutenberg styling.

No original WordPress/Facebook requests, no media reuse, no private routes.
This checks rendered computed CSS and keyboard affordances, not manual WCAG,
pixel-identical Newspack parity, or a rights/publication decision.
"""
import argparse
import copy
import math
from urllib.parse import urlsplit

ORIGIN = "https://casa-hacienda-makati.vercel.app"
ROUTES = {
    "/about/": {"small": 14, "medium": 0, "large": 0, "xlarge": 0},
    "/cultural-significance/": {"small": 12, "medium": 1, "large": 0, "xlarge": 0},
    "/2023/08/12/cultural-significance-no-1/": {"small": 0, "medium": 0, "large": 4, "xlarge": 1},
    "/2024/02/06/cultural-significance-no-11/": {"small": 15, "medium": 5, "large": 0, "xlarge": 1},
    "/2024/10/28/cultural-significance-no-12/": {"small": 0, "medium": 3, "large": 0, "xlarge": 1},
}
VIEWPORTS = (320, 375, 1280)
CLASSES = {
    "small": "has-small-font-size",
    "medium": "has-medium-font-size",
    "large": "has-large-font-size",
    "xlarge": "has-x-large-font-size",
}
SNAPSHOT_JS = r"""() => {
  const article = document.querySelector('article.content');
  if (!article) throw new Error('Missing published article');
  const sample = selector => [...article.querySelectorAll(selector)].map(e => {
    const s = getComputedStyle(e);
    const size = parseFloat(s.fontSize);
    return {size, line:parseFloat(s.lineHeight) / size,
            visible:s.display !== 'none' && s.visibility === 'visible'};
  });
  const buttons = [...article.querySelectorAll('.wp-block-button__link')];
  const spacers = [...article.querySelectorAll('.wp-block-spacer[style*="height:100px"]')];
  const column = article.querySelector('.wp-block-column');
  return {
    articleCount:document.querySelectorAll('article.content').length,
    robots:document.querySelector('meta[name="robots"]')?.content,
    stylesheets:document.styleSheets.length,
    overflow:document.documentElement.scrollWidth > innerWidth + 2,
    classes:{
      small:sample('.has-small-font-size'),
      medium:sample('.has-medium-font-size'),
      large:sample('.has-large-font-size'),
      xlarge:sample('.has-x-large-font-size')
    },
    buttons:buttons.map(e=>({height:e.getBoundingClientRect().height,
      keyboard:e.tabIndex >= 0, visible:getComputedStyle(e).display !== 'none'})),
    spacers:spacers.map(e=>e.getBoundingClientRect().height),
    columnPaddingRight:column ? parseFloat(getComputedStyle(column).paddingRight) : null,
    columnPaddingLeft:column ? parseFloat(getComputedStyle(column).paddingLeft) : null
  };
}"""

def expected_size(kind, width):
    return {"small": 14, "medium": 20, "large": 36 if width == 1280 else 28,
            "xlarge": 42 if width == 1280 else 32}[kind]

def validate_snapshot(s, route, width):
    if route not in ROUTES or width not in VIEWPORTS:
        raise AssertionError("Unreviewed route or viewport")
    if (s.get("status") != 200 or s.get("header") != "noindex,nofollow"
            or s.get("robots") != "noindex,nofollow"
            or s.get("articleCount") != 1 or s.get("stylesheets", 0) < 1
            or s.get("overflow") is not False):
        raise AssertionError("Production/privacy/layout regression: " + route)
    for kind, count in ROUTES[route].items():
        values = s.get("classes", {}).get(kind)
        if not isinstance(values, list) or len(values) != count:
            raise AssertionError("Gutenberg source class inventory mismatch: " + route + " " + kind)
        for item in values:
            if (item.get("visible") is not True or
                    not math.isfinite(item.get("size", float("nan"))) or
                    abs(item["size"] - expected_size(kind, width)) > 0.6 or
                    not 1.19 <= item.get("line", 0) <= 2.1):
                raise AssertionError("Gutenberg computed font regression: " + route + " " + kind)
    if route == "/cultural-significance/":
        buttons = s.get("buttons")
        if (not isinstance(buttons, list) or len(buttons) != 12 or
                any(b.get("height", 0) < 44 or b.get("keyboard") is not True or
                    b.get("visible") is not True for b in buttons)):
            raise AssertionError("Published 12-button accessibility regression")
        spacers = s.get("spacers")
        if not isinstance(spacers, list) or len(spacers) != 12:
            raise AssertionError("Original 100px spacer inventory changed")
        expected_height = 100 if width == 1280 else 36
        if any(abs(h - expected_height) > 1 for h in spacers):
            raise AssertionError("Mobile/desktop Gutenberg spacer regression")
    if route == "/about/":
        if s.get("columnPaddingRight") is None or s.get("columnPaddingLeft") is None:
            raise AssertionError("Imported Gutenberg column missing")
        if width == 1280:
            if abs(s["columnPaddingRight"] - 80) > 1:
                raise AssertionError("Original desktop column gutter changed")
        elif abs(s["columnPaddingRight"]) > 1 or abs(s["columnPaddingLeft"]) > 1:
            raise AssertionError("Mobile Gutenberg column gutters restored")
    return True

def synthetic(route, width):
    result = {"status": 200, "header": "noindex,nofollow",
              "robots": "noindex,nofollow", "articleCount": 1,
              "stylesheets": 1, "overflow": False,
              "classes": {kind: [{"size": expected_size(kind, width),
                                   "line": 1.6, "visible": True}] * count
                          for kind, count in ROUTES[route].items()},
              "buttons": [], "spacers": [],
              "columnPaddingRight": 80 if width == 1280 else 0,
              "columnPaddingLeft": 0}
    if route == "/cultural-significance/":
        result["buttons"] = [{"height": 44, "keyboard": True, "visible": True}] * 12
        result["spacers"] = [100 if width == 1280 else 36] * 12
    return result

def self_test():
    for route in ROUTES:
        for width in VIEWPORTS:
            validate_snapshot(synthetic(route, width), route, width)
    base = synthetic("/cultural-significance/", 375)
    mutations = [
        ("status", lambda x: x.update(status=404)),
        ("privacy-header", lambda x: x.update(header="")),
        ("privacy-meta", lambda x: x.update(robots="index,follow")),
        ("missing-article", lambda x: x.update(articleCount=0)),
        ("missing-css", lambda x: x.update(stylesheets=0)),
        ("overflow", lambda x: x.update(overflow=True)),
        ("missing-class", lambda x: x["classes"]["small"].pop()),
        ("wrong-size", lambda x: x["classes"]["small"][0].update(size=30)),
        ("bad-line-height", lambda x: x["classes"]["medium"][0].update(line=0.8)),
        ("missing-button", lambda x: x["buttons"].pop()),
        ("tiny-target", lambda x: x["buttons"][0].update(height=20)),
        ("no-keyboard", lambda x: x["buttons"][0].update(keyboard=False)),
        ("oversize-spacer", lambda x: x["spacers"].__setitem__(0, 100)),
    ]
    for name, change in mutations:
        item = copy.deepcopy(base)
        change(item)
        try:
            validate_snapshot(item, "/cultural-significance/", 375)
        except AssertionError:
            continue
        raise AssertionError("Unsafe fixture unexpectedly passed: " + name)
    about = synthetic("/about/", 375)
    about["columnPaddingRight"] = 80
    try:
        validate_snapshot(about, "/about/", 375)
    except AssertionError:
        pass
    else:
        raise AssertionError("Mobile gutter mutation unexpectedly passed")
    print("Live Gutenberg QA: 15 synthetic viewport/route baselines and 14 fail-closed mutations PASS")

def run_live():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            context = browser.new_context(reduced_motion="reduce", service_workers="block")
            blocked = []
            def only_project(route):
                url = urlsplit(route.request.url)
                if (url.scheme, url.netloc) == ("https", urlsplit(ORIGIN).netloc):
                    route.continue_()
                else:
                    blocked.append(url.netloc)
                    route.abort()
            context.route("**/*", only_project)
            page = context.new_page()
            for width in VIEWPORTS:
                page.set_viewport_size({"width": width, "height": 812})
                for route in ROUTES:
                    response = page.goto(ORIGIN + route, wait_until="domcontentloaded", timeout=45000)
                    if response is None:
                        raise AssertionError("Missing production HTTP response: " + route)
                    page.wait_for_function("document.styleSheets.length >= 1")
                    snap = page.evaluate(SNAPSHOT_JS)
                    snap["status"] = response.status
                    snap["header"] = response.headers.get("x-robots-tag")
                    validate_snapshot(snap, route, width)
                    if route == "/cultural-significance/":
                        button = page.locator("article.content .wp-block-button__link").first
                        button.focus()
                        if not button.evaluate("(e) => document.activeElement === e"):
                            raise AssertionError("Published CTA cannot receive keyboard focus")
            context.close()
            print("Live Gutenberg QA: 15 exact-production Chromium route/viewport checks PASS")
            print("Third-party requests blocked (never followed): " + str(len(blocked)))
        finally:
            browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    self_test()
    if not args.self_test:
        run_live()
