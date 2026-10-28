#!/usr/bin/env python3
"""Read-only production Chromium acceptance for two attributed Casa Hacienda locations.

DOM/interaction checks do not prove parcel identity, historical photograph
provenance, reproduction rights, or manual screen-reader accessibility.
"""
import argparse
import json
from pathlib import Path
from urllib.parse import urlsplit

ORIGIN = "https://casa-hacienda-makati.vercel.app"
PLACE_IDS = ["olympia-claim", "poblacion-account"]
LINKS = [
    "/2023/08/12/cultural-significance-no-3/",
    "https://bluprint-onemega.com/architecture/heritage/poblacion-heritage-district/",
    "/about/",
]


def check_links(hrefs):
    if hrefs != LINKS:
        raise AssertionError("Location source links or ordering changed")
    for href in (hrefs[0], hrefs[2]):
        parts = urlsplit(href)
        if parts.scheme or parts.netloc or parts.query or parts.fragment or not href.startswith("/") or href.startswith("//"):
            raise AssertionError("Internal source link is not canonical relative path")
    external = urlsplit(hrefs[1])
    if (external.scheme != "https" or external.netloc != "bluprint-onemega.com" or
            external.username or external.password or external.port or external.query or external.fragment):
        raise AssertionError("Unapproved external source URL")
    return True


def self_test():
    assert check_links(LINKS)
    bad = [
        LINKS[:-1],
        [LINKS[2], LINKS[1], LINKS[0]],
        [LINKS[0], "https://example.invalid/heritage", LINKS[2]],
        [LINKS[0], "http://bluprint-onemega.com/architecture/heritage/poblacion-heritage-district/", LINKS[2]],
        [LINKS[0], LINKS[1] + "?tracking=1", LINKS[2]],
        ["//evil.invalid/2023/08/12/cultural-significance-no-3/", LINKS[1], LINKS[2]],
        [LINKS[0] + "#unverified", LINKS[1], LINKS[2]],
        [LINKS[0], LINKS[1], "/private/"],
    ]
    for case in bad:
        try:
            check_links(case)
        except AssertionError:
            continue
        raise AssertionError("Unsafe location URL fixture passed")
    print("Live places URL allowlist: eight fail-closed fixtures PASS", flush=True)


def inspect(page, width, js_enabled, reduced_motion):
    response = page.goto(ORIGIN + "/", wait_until="load", timeout=60000)
    assert response and response.status == 200, "Production homepage unavailable"
    assert urlsplit(page.url).netloc == urlsplit(ORIGIN).netloc, "Cross-origin redirect"
    assert page.locator('meta[name="robots"]').get_attribute("content") == "noindex,nofollow"
    assert page.locator("h1").count() == 1
    assert page.locator("article.card").count() == 13, "Published article cards changed"
    section = page.locator('section[data-heritage-feature="places"]')
    assert section.count() == 1, "Missing or duplicate location guide"
    assert section.get_attribute("aria-labelledby") == "heritage-places-title"
    assert page.get_by_role("region", name="Two Casa Hacienda locations in the historical accounts").count() == 1
    assert section.locator("h2#heritage-places-title").is_visible()
    rows = section.locator("ol.place-records > li[data-place-id]")
    ids = [x.get_attribute("data-place-id") for x in rows.all()]
    assert ids == PLACE_IDS, "Two separate location accounts required"
    assert rows.locator("h3").count() == 2
    body = section.inner_text()
    for boundary in (
        "9126 Sultana Street, Barangay Olympia",
        "expressly distinguishes this location",
        "now Poblacion Park",
        "Independent secondary account",
        "have not yet been independently verified against this parcel",
        "cannot establish that the surviving Olympia remains and the former Poblacion offices are the same building",
        "not a verified parcel-level identification",
        "reproduction rights remain unverified",
        "No historical photograph, map image or location overlay is reproduced here",
    ):
        assert boundary in body, "Historical qualification missing: " + boundary
    links = section.locator("a")
    hrefs = [x.get_attribute("href") for x in links.all()]
    check_links(hrefs)
    assert all(x.is_visible() for x in links.all()), "Hidden location source link"
    assert section.locator("img,video,audio,iframe,canvas,script,object,embed").count() == 0
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 2"), "Horizontal overflow"
    assert page.evaluate('matchMedia("(prefers-reduced-motion: reduce)").matches') == reduced_motion
    links.nth(0).focus()
    assert links.nth(0).evaluate("e => document.activeElement === e"), "Source link cannot focus"
    page.keyboard.press("Tab")
    assert links.nth(1).evaluate("e => document.activeElement === e"), "Keyboard source-link focus order"
    page.keyboard.press("Tab")
    assert links.nth(2).evaluate("e => document.activeElement === e"), "Keyboard About link focus order"
    if width == 375:
        assert page.locator("details.mobile-nav summary").is_visible(), "Mobile menu missing"
    else:
        assert page.locator("nav.desktop-nav").is_visible(), "Desktop navigation missing"
    return {
        "viewport": width, "javaScript": js_enabled, "reducedMotion": reduced_motion,
        "placeIds": ids, "sourceLinks": hrefs, "articleCards": 13,
        "noindex": True, "keyboardFocus": True, "overflow": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--output-dir", default="places-browser-evidence")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    from playwright.sync_api import sync_playwright
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
                                    path=str(out / f"places-{width}-js{int(js_enabled)}-reduce{int(reduced_motion)}.png"),
                                    full_page=True, animations="disabled", timeout=15000,
                                )
                                row["screenshot"] = "saved"
                            except Exception as error:
                                row["screenshot"] = "unavailable"
                                print("Optional screenshot unavailable: " + type(error).__name__, flush=True)
                            print("Independent live places PASS: " + json.dumps(row), flush=True)
                        finally:
                            context.close()
        finally:
            browser.close()
    assert len(results) == 8
    (out / "places-browser-acceptance.json").write_text(json.dumps({
        "scope": "Read-only production Chromium, not parcel truth, reproduction rights or manual screen-reader",
        "origin": ORIGIN, "tests": results, "allPassed": True,
    }, indent=2) + "\n")
    print("Independent live places PASS: eight browser combinations, two attributed accounts", flush=True)


if __name__ == "__main__":
    main()
