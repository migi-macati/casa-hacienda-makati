#!/usr/bin/env python3
"""Independent read-only production browser acceptance for two legal-record events.

A pass cannot establish historical parcel identity, rights, original scan
fidelity, full WordPress parity or manual screen-reader accessibility.
"""
import argparse
import json
from pathlib import Path
from urllib.parse import urlsplit

ORIGIN = "https://casa-hacienda-makati.vercel.app"
EVENT_IDS = ["1906-registration-application", "1907-court-decision"]
LINKS = [
    "https://www.chanrobles.com/scdecisions/jurisprudence1907/dec1907/gr_l-3788_1907.php",
    "https://lawyerly.ph/juris/view/c15f",
]

def check_links(hrefs):
    if hrefs != LINKS:
        raise AssertionError("Events source URL allowlist or order changed")
    for href, host in zip(hrefs, ("www.chanrobles.com", "lawyerly.ph")):
        u = urlsplit(href)
        if (u.scheme != "https" or u.netloc != host or u.username or u.password or
                u.port or u.query or u.fragment):
            raise AssertionError("Unsafe events source URL")
    return True

def self_test():
    assert check_links(LINKS)
    cases = [
        LINKS[:-1],
        LINKS + [LINKS[0]],
        LINKS[::-1],
        ["http://www.chanrobles.com/scdecisions/jurisprudence1907/dec1907/gr_l-3788_1907.php", LINKS[1]],
        [LINKS[0] + "?source=unverified", LINKS[1]],
        ["https://www.chanrobles.com.evil.test/scdecisions/jurisprudence1907/dec1907/gr_l-3788_1907.php", LINKS[1]],
        [LINKS[0], "https://example.invalid/juris/view/c15f"],
        [LINKS[0], LINKS[1] + "#unverified"],
        [LINKS[0], "//lawyerly.ph/juris/view/c15f"],
    ]
    for case in cases:
        try:
            check_links(case)
        except AssertionError:
            continue
        raise AssertionError("Unsafe events source fixture passed")
    print("Live events URL allowlist: nine fail-closed fixtures PASS", flush=True)

def inspect(page, width, js_enabled, reduced_motion):
    response = page.goto(ORIGIN + "/", wait_until="load", timeout=60000)
    assert response and response.status == 200, "Production homepage unavailable"
    assert urlsplit(page.url).netloc == urlsplit(ORIGIN).netloc, "Cross-origin redirect"
    assert page.locator('meta[name="robots"]').get_attribute("content") == "noindex,nofollow"
    assert page.locator("h1").count() == 1
    assert page.locator("article.card").count() == 13, "Published article cards changed"
    section = page.locator('section[data-heritage-feature="events"]')
    assert section.count() == 1, "Missing or duplicate events section"
    assert section.get_attribute("aria-labelledby") == "heritage-events-title"
    assert page.get_by_role("region", name="Events in the estate's legal record").count() == 1
    assert section.locator("h2#heritage-events-title").is_visible()
    rows = section.locator("ol.event-records > li[data-event-id]")
    ids = [x.get_attribute("data-event-id") for x in rows.all()]
    assert ids == EVENT_IDS, "Two attributed legal events required"
    assert rows.locator("h3").count() == 2
    body = section.inner_text()
    for limit in (
        "February 19, 1906", "December 21, 1907",
        "Pedro P. Roxas", "G.R. No. L-3788", "9 Phil. 408",
        "parcels A through D", "An application is not proof",
        "a deed was executed", "parcel C",
        "not a building-construction record", "includes appurtenances",
        "not the house's footprint", "third-party transcriptions",
        "official 1907 report scan and original 1906 parcel plan have not been inspected",
        "do not establish a completed land transfer",
        "No archival image or map is reproduced",
    ):
        assert limit in body, "Missing evidence limit: " + limit
    links = section.locator("a")
    hrefs = [x.get_attribute("href") for x in links.all()]
    check_links(hrefs)
    assert all(x.is_visible() for x in links.all()), "Hidden source link"
    assert section.locator("img,video,audio,iframe,canvas,script,object,embed").count() == 0
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 2"), "Horizontal overflow"
    assert page.evaluate('matchMedia("(prefers-reduced-motion: reduce)").matches') == reduced_motion
    links.nth(0).focus()
    assert links.nth(0).evaluate("e => document.activeElement === e"), "First link cannot focus"
    page.keyboard.press("Tab")
    assert links.nth(1).evaluate("e => document.activeElement === e"), "Second link focus order"
    if width == 375:
        assert page.locator("details.mobile-nav summary").is_visible(), "Mobile menu missing"
    else:
        assert page.locator("nav.desktop-nav").is_visible(), "Desktop navigation missing"
    return {"viewport": width, "javaScript": js_enabled, "reducedMotion": reduced_motion,
            "eventIds": ids, "sourceLinks": hrefs, "articleCards": 13,
            "noindex": True, "keyboardFocus": True, "overflow": False}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--output-dir", default="events-browser-evidence")
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
                                page.screenshot(path=str(out / f"events-{width}-js{int(js_enabled)}-reduce{int(reduced_motion)}.png"),
                                                full_page=True, animations="disabled", timeout=15000)
                                row["screenshot"] = "saved"
                            except Exception as error:
                                row["screenshot"] = "unavailable"
                                print("Optional screenshot unavailable: " + type(error).__name__, flush=True)
                            print("Independent live events PASS: " + json.dumps(row), flush=True)
                        finally:
                            context.close()
        finally:
            browser.close()
    assert len(results) == 8
    (out / "events-browser-acceptance.json").write_text(json.dumps({
        "scope": "Read-only production Chromium; not archival truth, rights, or manual screen-reader",
        "origin": ORIGIN, "tests": results, "allPassed": True,
    }, indent=2) + "\n")
    print("Independent live events PASS: eight browser combinations, two attributed legal events", flush=True)

if __name__ == "__main__":
    main()
