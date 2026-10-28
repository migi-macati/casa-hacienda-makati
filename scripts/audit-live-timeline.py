#!/usr/bin/env python3
"""Read-only independent deployed Chromium QA for the four-entry sourced timeline.

Interaction/accessibility smoke gate, not historical-source or manual screen-reader acceptance.
"""
import argparse
import json
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright

ORIGIN = "https://casa-hacienda-makati.vercel.app"
YEARS = ["1607", "1608", "1620", "1768"]
SOURCE_PATHS = {"/registry_database/san-pedro-macati/", "/registry_database/makati/"}


def check_source_links(hrefs):
    if len(hrefs) != 4:
        raise AssertionError("Four timeline source links required")
    paths = []
    for href in hrefs:
        parsed = urlsplit(href)
        if (parsed.scheme != "https" or
                parsed.hostname != "philhistoricsites.nhcp.gov.ph" or
                parsed.path not in SOURCE_PATHS or parsed.query or parsed.fragment):
            raise AssertionError("Unreviewed timeline source URL")
        paths.append(parsed.path)
    if set(paths) != SOURCE_PATHS:
        raise AssertionError("Both NHCP marker records required")
    return True


def self_test():
    good = ["https://philhistoricsites.nhcp.gov.ph/registry_database/san-pedro-macati/",
            "https://philhistoricsites.nhcp.gov.ph/registry_database/makati/"]
    assert check_source_links([good[0], good[1], good[0], good[0]])
    for bad in ([good[0]] * 4,
                [good[0], good[1], good[0]],
                [good[0], good[1], good[0], "https://evil.example/"],
                [good[0], good[1], good[0], "http://philhistoricsites.nhcp.gov.ph/registry_database/makati/"],
                [good[0], good[1], good[0], "https://philhistoricsites.nhcp.gov.ph/registry_database/makati/?extra=1"]):
        try:
            check_source_links(bad)
        except AssertionError:
            continue
        raise AssertionError("Unreviewed source fixture passed")
    print("Deployed timeline source allowlist synthetic regressions PASS: 5 rejected cases")


def inspect(page, width, js_enabled, reduced_motion):
    response = page.goto(ORIGIN + "/", wait_until="load", timeout=60000)
    assert response and response.status == 200, "Production homepage unavailable"
    assert urlsplit(page.url).netloc == urlsplit(ORIGIN).netloc, "Cross-origin redirect"
    assert page.locator('meta[name="robots"]').get_attribute("content") == "noindex,nofollow"
    assert page.locator("h1").count() == 1
    assert page.locator("article.card").count() == 13, "Published article cards changed"
    section = page.locator('section[data-heritage-feature="timeline"]')
    assert section.count() == 1, "Missing or duplicate timeline"
    assert section.get_attribute("aria-labelledby") == "heritage-timeline-title"
    assert page.get_by_role("region", name="Early San Pedro Macati: what the records date").count() == 1
    assert section.locator("h2#heritage-timeline-title").is_visible()
    entries = section.locator("ol.timeline-list > li[data-year]")
    assert entries.count() == 4, "Four verified milestones expected"
    actual = [x.get_attribute("data-year") for x in entries.all()]
    assert actual == YEARS, f"Chronology changed: {actual}"
    assert all(x.inner_text().strip().startswith(year) for x, year in zip(entries.locator("h3").all(), YEARS))
    assert "does not establish when the surviving structure" in section.inner_text()
    assert "not original deeds or building plans" in section.inner_text()
    source_links = section.locator('a[href^="https://philhistoricsites.nhcp.gov.ph/"]')
    hrefs = [a.get_attribute("href") for a in source_links.all()]
    check_source_links(hrefs)
    assert all(a.is_visible() for a in source_links.all())
    assert section.locator("img,video,audio,iframe,canvas,script").count() == 0
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 2"), "Horizontal overflow"
    assert page.evaluate('matchMedia("(prefers-reduced-motion: reduce)").matches') == reduced_motion
    # Test real keyboard focus through successive source links without navigating off-site.
    source_links.nth(0).focus()
    assert source_links.nth(0).evaluate("(e) => document.activeElement === e")
    page.keyboard.press("Tab")
    assert source_links.nth(1).evaluate("(e) => document.activeElement === e"), "Timeline keyboard focus order"
    if width == 375:
        assert page.locator("details.mobile-nav summary").is_visible(), "Mobile menu missing"
    else:
        assert page.locator("nav.desktop-nav").is_visible(), "Desktop menu missing"
    return {"viewport": width, "javaScript": js_enabled, "reducedMotion": reduced_motion,
            "years": actual, "sourceLinks": len(hrefs), "articleCards": 13,
            "noindex": True, "keyboardFocus": True, "overflow": False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--output-dir", default="timeline-browser-evidence")
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
                            # Screenshot evidence is supplementary. An unstable element
                            # screenshot must not turn passing live accessibility checks
                            # into a false feature failure.
                            try:
                                page.screenshot(
                                    path=str(out / f"timeline-{width}-js{int(js_enabled)}-reduce{int(reduced_motion)}.png"),
                                    full_page=True, animations="disabled", timeout=15000,
                                )
                                row["screenshot"] = "saved"
                            except Exception as error:
                                row["screenshot"] = "unavailable"
                                print("Optional screenshot unavailable: " + type(error).__name__, flush=True)
                            print("Independent live timeline PASS: " + json.dumps(row), flush=True)
                        finally:
                            context.close()
        finally:
            browser.close()
    assert len(results) == 8
    (out / "timeline-browser-acceptance.json").write_text(json.dumps({
        "scope": "Independent production Chromium interaction smoke QA; not manual screen-reader or source-truth acceptance",
        "origin": ORIGIN,
        "tests": results,
        "allPassed": True,
    }, indent=2) + "\n")
    print("Independent deployed timeline PASS: 8 viewport/JS/motion combinations, 4 dated entries, 4 official source links")


if __name__ == "__main__":
    main()
