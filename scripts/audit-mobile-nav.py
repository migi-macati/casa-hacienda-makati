#!/usr/bin/env python3
"""Generated-site and independent production Chromium acceptance for no-JS navigation."""
import functools
import http.server
import json
import re
import sys
import threading
import urllib.parse
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright


class SameOrigin(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if urllib.parse.urlsplit(newurl).netloc != urllib.parse.urlsplit(ORIGIN).netloc:
            raise AssertionError("Cross-origin redirect rejected")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


OPENER = urllib.request.build_opener(SameOrigin)

ORIGIN = "https://casa-hacienda-makati.vercel.app"
MISSING = "/__chm_qa_unpublished_route_20261028__/"
EXPECTED_LINKS = [
    "/", "/about/", "/cultural-significance/", "/#archive",
    "https://facebook.com/casahaciendamakati",
]


def published_routes(index, locked_documents=None):
    assert isinstance(index, list) and len(index) == 15, "Published index count changed"
    assert sum(x.get("type") == "article" for x in index) == 13
    assert sum(x.get("type") == "page" for x in index) == 2
    paths = [x["url"] for x in index]
    assert len(set(paths)) == 15, "Duplicate published route"
    assert all(re.fullmatch(r"/[a-z0-9/-]+/", p) and ".." not in p for p in paths)
    if locked_documents is None:
        locked_documents = json.loads(Path("ops/published-search-sources.json").read_text())["documents"]
    expected = [("/" + d["file"].removesuffix("index.html"), d["type"]) for d in locked_documents]
    actual = [(x["url"], x["type"]) for x in index]
    assert len(expected) == 15 and actual == expected, "Deployed index differs from pinned published-source routes"
    return paths


def read_production_index():
    request = urllib.request.Request(
        ORIGIN + "/search-index.json",
        headers={"User-Agent": "CasaHaciendaReadOnlyQA/1.0"},
    )
    with OPENER.open(request, timeout=40) as response:
        assert response.status == 200
        assert urllib.parse.urlsplit(response.url).netloc == urllib.parse.urlsplit(ORIGIN).netloc
        raw = response.read(2 * 1024 * 1024 + 1)
    assert len(raw) <= 2 * 1024 * 1024
    return json.loads(raw)


def hrefs(locator):
    return [link.get_attribute("href") for link in locator.all()]


def check_navigation(page, route, width, expected_status):
    response = page.goto(route, wait_until="load", timeout=45000)
    assert response and response.status == expected_status, (route, expected_status)
    assert page.locator('meta[name="robots"]').get_attribute("content") == "noindex,nofollow", route
    skip = page.locator('a.skip-link[href="#main-content"]')
    main = page.locator('main#main-content[tabindex="-1"]')
    assert skip.count() == main.count() == 1, ("skip landmark", route)
    page.keyboard.press("Tab")
    assert skip.evaluate("(e) => document.activeElement === e"), ("skip first focus", route)
    assert skip.is_visible(), ("skip visible on focus", route)
    box = skip.bounding_box()
    assert box and box["width"] >= 44 and box["height"] >= 44, ("skip target size", route)
    assert 0 <= box["x"] < width and 0 <= box["y"] < 812, ("skip in viewport", route)
    page.keyboard.press("Enter")
    assert page.evaluate("location.hash") == "#main-content", ("skip target", route)
    assert main.evaluate("(e) => document.activeElement === e"), ("skip focus transfer", route)
    desktop = page.locator("nav.desktop-nav")
    mobile = page.locator("details.mobile-nav")
    assert desktop.count() == mobile.count() == 1, route
    assert hrefs(desktop.locator("a")) == EXPECTED_LINKS, ("desktop links", route)
    assert hrefs(mobile.locator("nav a")) == EXPECTED_LINKS, ("mobile links", route)
    assert desktop.get_attribute("aria-label") == "Primary", route
    assert mobile.locator("nav").get_attribute("aria-label") == "Mobile", route
    summary = mobile.locator("summary")
    assert summary.count() == 1 and summary.inner_text().strip() == "Menu", route
    if width == 1280:
        assert desktop.is_visible() and not mobile.is_visible(), route
    else:
        assert not desktop.is_visible() and summary.is_visible(), route
        assert not mobile.locator("nav").is_visible() and mobile.get_attribute("open") is None, route
        summary.click()
        assert mobile.locator("nav").is_visible() and mobile.get_attribute("open") is not None, route
        assert all(link.is_visible() for link in mobile.locator("nav a").all()), route
        summary.click()
        assert not mobile.locator("nav").is_visible() and mobile.get_attribute("open") is None, route


def self_test():
    sample = [
        {"url": f"/2023/01/{i:02d}/sample/", "type": "article" if i <= 13 else "page"}
        for i in range(1, 16)
    ]
    lock = [{"file": x["url"].lstrip("/") + "index.html", "type": x["type"]} for x in sample]
    assert len(published_routes(sample, lock)) == 15
    for changed in (
        sample[:-1],
        sample[:-1] + [dict(sample[0])],
        sample[:-1] + [{"url": "/private/", "type": "article"}],
        sample[:-1] + [{"url": "/../hidden/", "type": "page"}],
        sample[:-1] + [{"url": "/2023/01/15/other/", "type": "page"}],
    ):
        try:
            published_routes(changed, lock)
        except AssertionError:
            continue
        raise AssertionError("Invalid published-route fixture accepted")
    assert len(EXPECTED_LINKS) == 5 and EXPECTED_LINKS[0] == "/"
    print("Native navigation route/allowlist synthetic tests PASS: 7 assertions")


def main():
    if sys.argv[1:] == ["--self-test"]:
        self_test()
        return
    production = sys.argv[1:] == ["--production"]
    if sys.argv[1:] not in ([], ["--production"]):
        raise SystemExit("Usage: audit-mobile-nav.py [--self-test|--production]")
    server = None
    if production:
        paths = published_routes(read_production_index())
        origin = ORIGIN
        paths = ["/"] + paths + [MISSING]
    else:
        paths = published_routes(json.loads(Path("public/search-index.json").read_text()))
        paths = ["/"] + paths + ["/404.html"]
        server = http.server.ThreadingHTTPServer(
            ("127.0.0.1", 0),
            functools.partial(
                http.server.SimpleHTTPRequestHandler,
                directory=str(Path("public").resolve()),
            ),
        )
        threading.Thread(target=server.serve_forever, daemon=True).start()
        origin = f"http://127.0.0.1:{server.server_port}"
    visits = 0
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            for width in (1280, 375):
                context = browser.new_context(
                    viewport={"width": width, "height": 812},
                    java_script_enabled=False,
                )
                page = context.new_page()
                for path in paths:
                    expected_status = 404 if production and path == MISSING else 200
                    check_navigation(page, origin + path, width, expected_status)
                    visits += 1
                    print(f"Native nav PASS {width}px {path}", flush=True)
                context.close()
            browser.close()
    finally:
        if server:
            server.shutdown()
            server.server_close()
    assert visits == 34
    print(
        f"{'Independent production' if production else 'Generated-site'} "
        "native mobile navigation PASS: 17 routes x 2 viewports, no JavaScript."
    )


if __name__ == "__main__":
    main()
