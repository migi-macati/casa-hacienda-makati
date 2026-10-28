#!/usr/bin/env python3
"""Independent read-only production Chromium acceptance for the partial sources register.

Verifies live browser semantics, source URL identity and privacy. This does not
verify original archival documents, reproduction rights or manual screen readers.
"""
import argparse
import json
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright

ORIGIN = "https://casa-hacienda-makati.vercel.app"
IDS = ["nhcp-1937", "nhcp-1991", "bl-1775"]
SOURCE_URLS = [
    "https://philhistoricsites.nhcp.gov.ph/registry_database/san-pedro-macati/",
    "https://philhistoricsites.nhcp.gov.ph/registry_database/makati/",
    "https://searcharchives.bl.uk/catalog/040-002027896",
]
EXPECTED_HREFS = SOURCE_URLS + ["/cultural-significance/"]


def check_links(hrefs):
    if hrefs != EXPECTED_HREFS:
        raise AssertionError("Source register hrefs or ordering changed")
    for href in hrefs[:3]:
        u = urlsplit(href)
        if u.scheme != "https" or u.username or u.password or u.port or u.query or u.fragment:
            raise AssertionError("Source link is not an approved canonical HTTPS URL")
    return True


def self_test():
    assert check_links(EXPECTED_HREFS)
    bad = [
        EXPECTED_HREFS[:-1],
        EXPECTED_HREFS[:2] + ["https://searcharchives.bl.uk/catalog/040-002027897", EXPECTED_HREFS[3]],
        EXPECTED_HREFS[:2] + ["https://example.invalid/catalog/040-002027896", EXPECTED_HREFS[3]],
        EXPECTED_HREFS[:2] + ["http://searcharchives.bl.uk/catalog/040-002027896", EXPECTED_HREFS[3]],
        EXPECTED_HREFS[:2] + [EXPECTED_HREFS[2] + "?unverified=1", EXPECTED_HREFS[3]],
        [EXPECTED_HREFS[1], EXPECTED_HREFS[0], EXPECTED_HREFS[2], EXPECTED_HREFS[3]],
    ]
    for fixture in bad:
        try:
            check_links(fixture)
        except AssertionError:
            continue
        raise AssertionError("Unsafe source URL fixture passed")
    print("Deployed sources URL allowlist: six fail-closed fixtures PASS", flush=True)


def inspect(page, width, js_enabled, reduced_motion):
    response = page.goto(ORIGIN + "/", wait_until="load", timeout=60000)
    assert response and response.status == 200, "Production homepage unavailable"
    assert urlsplit(page.url).netloc == urlsplit(ORIGIN).netloc, "Cross-origin redirect"
    assert page.locator('meta[name="robots"]').get_attribute("content") == "noindex,nofollow"
    assert page.locator("h1").count() == 1, "Homepage H1 drift"
    assert page.locator("article.card").count() == 13, "Published article cards changed"
    section = page.locator('section[data-heritage-feature="sources"]')
    assert section.count() == 1, "Missing or duplicate sources register"
    assert section.get_attribute("aria-labelledby") == "heritage-sources-title"
    assert page.get_by_role("region", name="Sources and what they establish").count() == 1
    assert section.locator("h2#heritage-sources-title").is_visible()
    rows = section.locator("ol.source-records > li[data-source-id]")
    ids = [x.get_attribute("data-source-id") for x in rows.all()]
    assert ids == IDS, "Three reviewed institutional records required"
    assert rows.locator("h3").count() == 3
    body = section.inner_text()
    for boundary in (
        "not the original deed",
        "a different act from the 1607 donation",
        "The map sheet has not been examined",
        "does not establish that the Olympia house appears",
        "No map image is reproduced here",
        "Add MS 17641 C",
        "040-002027896",
    ):
        assert boundary in body, "Evidence limitation missing: " + boundary
    links = section.locator("a")
    hrefs = [x.get_attribute("href") for x in links.all()]
    check_links(hrefs)
    assert all(x.is_visible() for x in links.all()), "Hidden institutional link"
    assert section.locator("img,video,audio,iframe,canvas,script,object,embed").count() == 0
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 2"), "Horizontal overflow"
    assert page.evaluate('matchMedia("(prefers-reduced-motion: reduce)").matches') == reduced_motion
    links.nth(0).focus()
    assert links.nth(0).evaluate("(e) => document.activeElement === e")
    page.keyboard.press("Tab")
    assert links.nth(1).evaluate("(e) => document.activeElement === e"), "Keyboard source-link focus order"
    if width == 375:
        assert page.locator("details.mobile-nav summary").is_visible(), "Mobile menu missing"
    else:
        assert page.locator("nav.desktop-nav").is_visible(), "Desktop navigation missing"
    return {
        "viewport": width, "javaScript": js_enabled, "reducedMotion": reduced_motion,
        "sourceIds": ids, "sourceLinks": hrefs[:3], "articleCards": 13,
        "noindex": True, "keyboardFocus": True, "overflow": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--output-dir", default="source-register-browser-evidence")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    results = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            for width in (1280, 375):
                for js_enabled in (False, True):
                    for reduced_motion in (False, True):
                        context = browser.new_context(
                            viewport={"width": width, "height": 812},
                            java_script_enabled=js_enabled,
                            reduced_motion="reduce" if reduced_motion else "no-preference",
                        )
                        page = context.new_page()
                        try:
                            row = inspect(page, width, js_enabled, reduced_motion)
                            results.append(row)
                            try:
                                page.screenshot(
                                    path=str(out / f"sources-{width}-js{int(js_enabled)}-reduce{int(reduced_motion)}.png"),
                                    full_page=True, animations="disabled", timeout=15000,
                                )
                                row["screenshot"] = "saved"
                            except Exception as error:
                                row["screenshot"] = "unavailable"
                                print("Optional screenshot unavailable: " + type(error).__name__, flush=True)
                            print("Independent live sources PASS: " + json.dumps(row), flush=True)
                        finally:
                            context.close()
        finally:
            browser.close()
    assert len(results) == 8
    (out / "sources-browser-acceptance.json").write_text(json.dumps({
        "scope": "Read-only production Chromium smoke QA, not manual screen-reader, archival truth or rights clearance",
        "origin": ORIGIN, "tests": results, "allPassed": True,
    }, indent=2) + "\n")
    print("Independent deployed sources PASS: eight browser combinations, three reviewed institutional links", flush=True)


if __name__ == "__main__":
    main()
