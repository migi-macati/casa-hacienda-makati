#!/usr/bin/env python3
"""Read-only generated-site Chromium acceptance for current-original Gutenberg tokens."""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path("public")
LOCK = json.loads(Path("ops/published-search-sources.json").read_text())
CSS = (ROOT / "assets/style.css").read_text()
LINK = '<link rel="stylesheet" href="/assets/style.css">'
WIDTHS = {320: 41.6, 375: 48.75, 1280: 166.4}
assert len(LOCK["documents"]) == 15
assert sum(d["type"] == "article" for d in LOCK["documents"]) == 13
assert sum(d["type"] == "page" for d in LOCK["documents"]) == 2

def close(actual, expected, context):
    assert abs(actual - expected) <= 0.8, (context, actual, expected)

with sync_playwright() as pw:
    opts = {"headless": True}
    if os.environ.get("CHROMIUM_PATH"):
        opts["executable_path"] = os.environ["CHROMIUM_PATH"]
    browser = pw.chromium.launch(**opts)
    try:
        for width, expected in WIDTHS.items():
            page = browser.new_page(viewport={"width": width, "height": 812},
                                    java_script_enabled=False)
            page.route("**/*", lambda route: route.abort())
            count = 0
            for doc in LOCK["documents"]:
                html = (ROOT / doc["file"]).read_text()
                assert html.count(LINK) == 1, ("original stylesheet", doc["file"])
                assert html.count('<meta name="robots" content="noindex,nofollow">') == 1
                page.set_content(html.replace(LINK, "<style>" + CSS + "</style>"),
                                 wait_until="domcontentloaded")
                article = page.locator("article.content")
                assert article.count() == 1
                rules = article.locator(".wp-block-separator")
                count += rules.count()
                details = rules.evaluate_all("""els => els.map(e => {
                    const s=getComputedStyle(e), b=e.getBoundingClientRect();
                    return {width:b.width, border:s.borderBottomWidth,
                            style:s.borderBottomStyle, opacity:s.opacity,
                            left:b.left, right:b.right};
                })""")
                for d in details:
                    close(d["width"], expected, (doc["file"], width, "separator"))
                    assert d["border"] == "1px" and d["style"] == "solid", (doc["file"], d)
                    assert d["opacity"] == "1", ("source alpha opacity", doc["file"], d)
                    assert d["left"] >= -1 and d["right"] <= width + 1
                if doc["file"] == "cultural-significance/index.html":
                    heading = article.locator('[style*="padding-bottom:var(--wp--preset--spacing--60)"]')
                    assert heading.count() == 1
                    bottom = heading.evaluate("(e)=>parseFloat(getComputedStyle(e).paddingBottom)")
                    close(bottom, expected, (width, "spacing60"))
                    assert article.locator("p.has-border-color.has-base-border-color").count() == 12
                    assert article.locator(".wp-block-button__link[href]").count() == 12
                if doc["file"] == "about/index.html":
                    element = article.locator('[style*="margin-top:var(--wp--preset--spacing--70)"]')
                    assert element.count() == 1
                    top = element.evaluate("(e)=>parseFloat(getComputedStyle(e).marginTop)")
                    close(top, 54.08, (width, "unchanged spacing70"))
                assert page.locator('meta[name="robots"]').get_attribute("content") == "noindex,nofollow"
                assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"), (doc["file"], width, "screen overflow")
                page.emulate_media(media="print")
                assert article.evaluate("(e)=>getComputedStyle(e).display") != "none"
                assert rules.evaluate_all("els=>els.every(e=>getComputedStyle(e).display!=='none')")
                page.emulate_media(media="screen")
            assert count == 25, (width, "source-locked 25 separators", count)
            page.close()
    finally:
        browser.close()
print("Gutenberg current-theme tokens PASS: 15 published documents x 320/375/1280, 25 responsive 1px rules, spacing60, unchanged spacing70, print, noindex/no overflow.")
