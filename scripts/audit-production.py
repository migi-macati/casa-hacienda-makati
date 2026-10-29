#!/usr/bin/env python3
"""Read-only deployed HTTP, browser and media-byte acceptance; no private routes."""
import concurrent.futures
import hashlib
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ORIGIN = "https://casa-hacienda-makati.vercel.app"

class SameOrigin(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if urllib.parse.urlsplit(newurl).netloc != urllib.parse.urlsplit(ORIGIN).netloc:
            raise AssertionError("Cross-origin redirect rejected")
        return super().redirect_request(req, fp, code, msg, headers, newurl)

OPENER = urllib.request.build_opener(SameOrigin)

def get_bytes(path, cap=45 * 1024 * 1024):
    if not path.startswith("/") or path.startswith("//") or ".." in path.split("/"):
        raise AssertionError("Unsafe relative path")
    req = urllib.request.Request(ORIGIN + path, headers={"User-Agent": "CasaHaciendaReadOnlyQA/1.0"})
    with OPENER.open(req, timeout=40) as res:
        if res.status != 200 or urllib.parse.urlsplit(res.url).netloc != urllib.parse.urlsplit(ORIGIN).netloc:
            raise AssertionError("Unexpected response: " + path)
        check_noindex_response_header(res.headers, path)
        data = res.read(cap + 1)
        if len(data) > cap:
            raise AssertionError("Response exceeds size limit: " + path)
        return data

def get_json(path):
    return json.loads(get_bytes(path, 2 * 1024 * 1024))

def norm(s):
    return re.sub(r"\s+", " ", s).strip()

def validate_media(manifest, inventory):
    expected = [a["path"] for a in manifest["assets"]]
    actual = [a["path"] for a in inventory["assets"]]
    if (inventory.get("schema_version") != 1 or len(expected) != 82 or
        len(actual) != 82 or len(set(expected)) != 82 or
        len(set(actual)) != 82 or set(expected) != set(actual)):
        raise AssertionError("Production media inventory closure mismatch")
    for a in inventory["assets"]:
        if (not re.fullmatch(r"/media/[a-zA-Z0-9_./-]+", a["path"]) or
            ".." in a["path"].split("/") or
            not isinstance(a.get("bytes"), int) or a["bytes"] <= 0 or
            not re.fullmatch(r"[0-9a-f]{64}", a.get("sha256", ""))):
            raise AssertionError("Invalid media entry")
    return inventory["assets"]

def check_media(a):
    data = get_bytes(a["path"])
    if len(data) != a["bytes"] or hashlib.sha256(data).hexdigest() != a["sha256"]:
        raise AssertionError("Served-media SHA256 mismatch: " + a["path"])
    if a["path"].endswith(".webp") and not (data[:4] == b"RIFF" and data[8:12] == b"WEBP"):
        raise AssertionError("Invalid served WebP: " + a["path"])
    if a["path"].endswith(".pdf") and not data.startswith(b"%PDF"):
        raise AssertionError("Invalid served PDF: " + a["path"])
    return a["path"]

VISIBLE_TEXT = r"""() => {
 const article = document.querySelector('article.content');
 if (!article || document.querySelectorAll('article').length !== 1)
   throw new Error('Missing or ambiguous published article');
 const walker = document.createTreeWalker(article, NodeFilter.SHOW_TEXT);
 const parts = [];
 let node;
 while ((node = walker.nextNode())) {
   if (!node.textContent.trim()) continue;
   let visible = true;
   for (let element = node.parentElement; element; element = element.parentElement) {
     const style = getComputedStyle(element);
     if (element.hidden || element.inert || element.getAttribute('aria-hidden') === 'true' ||
         style.display === 'none' || style.visibility === 'hidden' ||
         style.visibility === 'collapse' || style.contentVisibility === 'hidden' ||
         Number(style.opacity) === 0 || /inset\(50%/.test(style.clipPath) ||
         /rect\(0px, 0px, 0px, 0px\)/.test(style.clip) ||
         (style.overflow === 'hidden' && element.getBoundingClientRect().width === 0 &&
          element.getBoundingClientRect().height === 0)) {
       visible = false; break;
     }
     if (element === article) break;
   }
   if (visible) parts.push(node.textContent);
 }
 return parts.join(' ').replace(/\s+/g, ' ').trim();
}"""


# Production-only, read-only gallery interaction and security checks.
GALLERY_ROUTES = {
    '/2023/08/12/cultural-significance-no-1/': (3, False),
    '/2023/10/21/history-of-barrio-olimpia-makati-rizal/': (7, True),
}

def check_noindex_response_header(headers, route):
    """Require the deployed HTTP privacy header, including on static assets.

    HTML meta and robots.txt cannot protect direct PDF or media responses.
    Refuse duplicate, missing or contradictory directives.
    """
    values = (headers.get_all("X-Robots-Tag") if hasattr(headers, "get_all")
              else [headers.get("x-robots-tag")])
    if (not values or len(values) != 1 or not isinstance(values[0], str) or
        not re.fullmatch(r"\s*noindex\s*,\s*nofollow\s*", values[0], re.I)):
        raise AssertionError("Global noindex/nofollow HTTP header missing or changed: " + route)


def check_security_headers(response, route):
    headers = response.headers
    check_noindex_response_header(headers, route)
    expected = {
        'x-content-type-options': 'nosniff',
        'x-frame-options': 'SAMEORIGIN',
        'referrer-policy': 'strict-origin-when-cross-origin',
    }
    for name, value in expected.items():
        if headers.get(name, '').lower() != value.lower():
            raise AssertionError(f'Security response header {name} missing or changed: {route}')
    if not headers.get('strict-transport-security', '').startswith('max-age='):
        raise AssertionError('HSTS missing: ' + route)


def check_live_gallery(page, route, expected_count, linked):
    gallery = page.locator('article.content .wp-block-gallery')
    if gallery.count() != 1:
        raise AssertionError('Gallery missing or duplicated: ' + route)
    if gallery.locator('figure.wp-block-image').count() != expected_count:
        raise AssertionError('Gallery source image count changed: ' + route)
    triggers = gallery.locator('a[href]' if linked else 'button.chm-gallery-trigger')
    if triggers.count() != expected_count:
        raise AssertionError('Gallery triggers missing: ' + route)
    if linked and not all(u.startswith('https://casahaciendamakati.wordpress.com/')
                          for u in triggers.evaluate_all('(nodes) => nodes.map(n => n.href)')):
        raise AssertionError('Original WordPress fallback links changed: ' + route)
    dialog = page.locator('dialog.chm-gallery-dialog')
    if dialog.count() != 1:
        raise AssertionError('Gallery dialog missing or duplicated: ' + route)
    triggers.first.click()
    if not dialog.is_visible() or not dialog.evaluate('(el) => el.open && el.matches(":modal")'):
        raise AssertionError('Native modal did not open: ' + route)
    if dialog.get_attribute('aria-labelledby') != 'chm-gallery-title':
        raise AssertionError('Gallery dialog lacks accessible title: ' + route)
    if dialog.get_attribute('aria-describedby') != 'chm-gallery-help':
        raise AssertionError('Gallery dialog lacks keyboard help description: ' + route)
    help_text = dialog.locator('#chm-gallery-help').inner_text()
    if 'Left and Right arrow keys' not in help_text or 'Home and End' not in help_text:
        raise AssertionError('Gallery keyboard instructions missing: ' + route)
    heading = dialog.locator('h2#chm-gallery-title')
    if heading.get_attribute('aria-live') != 'polite' or heading.get_attribute('aria-atomic') != 'true':
        raise AssertionError('Gallery image position lacks atomic live announcement: ' + route)
    if not dialog.locator('button.chm-gallery-close').evaluate('(el) => document.activeElement === el'):
        raise AssertionError('Modal did not receive focus: ' + route)
    previous = dialog.get_by_role('button', name='Previous image')
    next_button = dialog.get_by_role('button', name='Next image')
    for i in range(expected_count):
        if dialog.locator('h2').inner_text() != f'Image {i + 1} of {expected_count}':
            raise AssertionError(f'Wrong gallery position {i + 1}: {route}')
        image = dialog.locator('img.chm-gallery-image')
        if not image.get_attribute('alt') or '/media/' not in image.get_attribute('src'):
            raise AssertionError('Gallery image lacks local media or alt: ' + route)
        # Verify the deployed viewer describes distinct original captions and
        # avoids duplicating alt text when a source figure has no caption.
        source_figure = gallery.locator('figure.wp-block-image').nth(i)
        source_alt = source_figure.locator('img').get_attribute('alt')
        source_caption_node = source_figure.locator('figcaption')
        source_caption = ((source_caption_node.first.text_content() or '').strip()
                          if source_caption_node.count() else '')
        modal_caption = dialog.locator('p#chm-gallery-caption')
        if modal_caption.count() != 1 or norm(modal_caption.inner_text()) != norm(source_caption or source_alt):
            raise AssertionError('Gallery caption differs from source figure: ' + route)
        expected_description = ('chm-gallery-caption'
                                if source_caption and source_caption != source_alt else None)
        if image.get_attribute('aria-describedby') != expected_description:
            raise AssertionError('Gallery image caption association incorrect: ' + route)
        page.wait_for_function("""() => {
            const im = document.querySelector('dialog.chm-gallery-dialog img.chm-gallery-image');
            return im && im.complete && im.naturalWidth > 0;
        }""", timeout=20000)
        if i == 0 and not previous.is_disabled():
            raise AssertionError('Previous enabled at first image: ' + route)
        if i + 1 < expected_count:
            page.keyboard.press('ArrowRight')
    if not next_button.is_disabled():
        raise AssertionError('Next enabled at final image: ' + route)
    page.keyboard.press('Home')
    if heading.inner_text() != f'Image 1 of {expected_count}' or not previous.is_disabled():
        raise AssertionError('Home failed to reach first gallery image: ' + route)
    page.keyboard.press('End')
    if heading.inner_text() != f'Image {expected_count} of {expected_count}' or not next_button.is_disabled():
        raise AssertionError('End failed to reach final gallery image: ' + route)
    page.keyboard.press('ArrowLeft')
    if dialog.locator('h2').inner_text() != f'Image {expected_count - 1} of {expected_count}':
        raise AssertionError('Previous keyboard navigation failed: ' + route)
    next_button.click()
    page.keyboard.press('Escape')
    if dialog.is_visible():
        raise AssertionError('Escape failed to close gallery: ' + route)
    if not triggers.first.evaluate('(el) => document.activeElement === el'):
        raise AssertionError('Focus was not restored to gallery trigger: ' + route)


def check_missing_route(page):
    route = '/__chm_qa_unpublished_route_20261028__/'
    response = page.goto(ORIGIN + route, wait_until='load', timeout=45000)
    if not response or response.status != 404:
        raise AssertionError('Unknown route must return HTTP 404')
    check_security_headers(response, route)
    if page.locator('meta[name="robots"]').get_attribute('content') != 'noindex,nofollow':
        raise AssertionError('Unknown route must remain noindex')
    if page.locator('h1').inner_text() != 'Page not found':
        raise AssertionError('Unknown route did not render 404 template')

def validate_index(index, provenance):
    if (not isinstance(index, list) or len(index) != 15 or
        len({a["url"] for a in index}) != 15 or
        sum(a["type"] == "article" for a in index) != 13 or
        sum(a["type"] == "page" for a in index) != 2):
        raise AssertionError("Published route inventory mismatch")
    routes = [a["url"] for a in index]
    if any(not re.fullmatch(r"/[a-z0-9/-]+/", x) or ".." in x for x in routes):
        raise AssertionError("Unexpected published route")
    raw = json.dumps(index, ensure_ascii=False, separators=(",", ":")).encode()
    if (provenance.get("routes") != routes or
        provenance.get("indexSha256") != hashlib.sha256(raw).hexdigest()):
        raise AssertionError("Published search provenance mismatch")
    return index

def check_browser(index):
    from playwright.sync_api import sync_playwright
    errors = []
    visits = 0
    gallery_visits = 0
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        for width, height in ((1280, 800), (375, 812)):
            context = browser.new_context(viewport={"width": width, "height": height})
            page = context.new_page()
            page.on("pageerror", lambda error: errors.append(str(error)[:160]))
            for entry in index:
                url = ORIGIN + entry["url"]
                response = page.goto(url, wait_until="load", timeout=45000)
                page.wait_for_function("getComputedStyle(document.querySelector('.brand img')).width === '44px'", timeout=15000)
                if not response or response.status != 200:
                    raise AssertionError("Published page unavailable: " + entry["url"])
                check_security_headers(response, entry["url"])
                if page.locator('meta[name="robots"]').get_attribute("content") != "noindex,nofollow":
                    raise AssertionError("Noindex missing: " + entry["url"])
                if page.locator('link[rel="canonical"]').get_attribute("href") != url:
                    raise AssertionError("Canonical mismatch: " + entry["url"])
                if page.locator("h1").count() != 1 or norm(page.locator("h1").inner_text()) != entry["title"]:
                    raise AssertionError("Heading mismatch: " + entry["url"])
                if norm(page.evaluate(VISIBLE_TEXT)) != norm(entry["text"]):
                    raise AssertionError("Browser-visible text mismatch: " + entry["url"])
                # Closed native gallery dialogs contain an unpopulated image; check visible images here.
                # The gallery test separately requires a nonempty alt once its modal opens.
                if page.locator('img:not([alt]):visible, img[alt=""]:visible').count():
                    raise AssertionError("Image alternative missing: " + entry["url"])
                if page.evaluate("document.documentElement.scrollWidth > innerWidth + 3"):
                    offenders = page.evaluate("""() => [...document.querySelectorAll('body *')].map(e => ({tag:e.tagName,cls:typeof e.className==='string'?e.className.slice(0,90):'',right:Math.round(e.getBoundingClientRect().right),left:Math.round(e.getBoundingClientRect().left),width:Math.round(e.getBoundingClientRect().width)})).filter(x=>x.right>innerWidth+3||x.left< -3).slice(0,12)""")
                    raise AssertionError("Horizontal overflow: " + entry["url"] + " width=" + str(width) + " scrollWidth=" + str(page.evaluate("document.documentElement.scrollWidth")) + " offenders=" + json.dumps(offenders))
                if entry["type"] == "article" and page.locator('a[href*="casahaciendamakati.wordpress.com"]').count() == 0:
                    raise AssertionError("Original discussion bridge missing: " + entry["url"])
                if entry["url"] in GALLERY_ROUTES:
                    check_live_gallery(page, entry["url"], *GALLERY_ROUTES[entry["url"]])
                    gallery_visits += 1
                visits += 1
            response = page.goto(ORIGIN + "/", wait_until="domcontentloaded", timeout=45000)
            if not response or response.status != 200:
                raise AssertionError("Homepage unavailable")
            check_security_headers(response, "/")
            if page.locator('meta[name="robots"]').get_attribute("content") != "noindex,nofollow":
                raise AssertionError("Homepage noindex missing")
            if page.evaluate("document.documentElement.scrollWidth > innerWidth + 3"):
                raise AssertionError("Homepage horizontal overflow at width " + str(width))
            page.locator("#find").fill("orphanage")
            page.wait_for_function('document.querySelector("#search-status").textContent.includes("result")', timeout=15000)
            if page.locator(".card:visible").count() < 1:
                raise AssertionError("Homepage search failed")
            page.locator("#find").fill("zzzzunlikelynonmatch123")
            page.wait_for_function('document.querySelector("#search-status").textContent.startsWith("0 results")', timeout=15000)
            if not page.locator("#nothing").is_visible():
                raise AssertionError("Homepage no-results state missing")
            check_missing_route(page)
            context.close()
        browser.close()
    if errors:
        raise AssertionError("Browser JavaScript exceptions: " + "; ".join(errors[:5]))
    return visits, gallery_visits

def self_test():
    manifest = {"assets": [{"path": f"/media/2023/07/sample{i}.webp"} for i in range(82)]}
    inventory = {"schema_version": 1, "assets": [
        {"path": a["path"], "bytes": 12, "sha256": "a" * 64} for a in manifest["assets"]]}
    assert len(validate_media(manifest, inventory)) == 82
    inventory["assets"][0]["sha256"] = "invalid"
    try:
        validate_media(manifest, inventory)
    except AssertionError:
        pass
    else:
        raise AssertionError("Invalid checksum accepted")
    assert norm(" a \n b ") == "a b"
    assert len(GALLERY_ROUTES) == 2
    assert sum(n for n, _ in GALLERY_ROUTES.values()) == 10
    assert all(route.endswith("/") for route in GALLERY_ROUTES)
    check_noindex_response_header({"x-robots-tag": "noindex, nofollow"}, "/test.pdf")
    check_noindex_response_header({"x-robots-tag": "NOINDEX,NOFOLLOW"}, "/test.pdf")
    for bad in (None, "", "index, follow", "noindex", "nofollow",
                "noindex, follow", "noindex, nofollow, index",
                "noindex, nofollow; index"):
        try:
            check_noindex_response_header({"x-robots-tag": bad}, "/test.pdf")
        except AssertionError:
            pass
        else:
            raise AssertionError("Invalid privacy response header accepted: " + str(bad))
    class DuplicateHeaders:
        def get_all(self, name):
            return ["noindex, nofollow", "index, follow"]
    try:
        check_noindex_response_header(DuplicateHeaders(), "/test.pdf")
    except AssertionError:
        pass
    else:
        raise AssertionError("Duplicate contradictory privacy header accepted")
    print("Production acceptance self-tests PASS: media/index/gallery and 11 HTTP privacy fixtures")

def main():
    if sys.argv[1:] == ["--self-test"]:
        self_test(); return
    if len(sys.argv) != 1:
        raise SystemExit("Usage: python scripts/audit-production.py [--self-test]")
    index = validate_index(get_json("/search-index.json"), get_json("/search-provenance.json"))
    manifest = json.loads(Path("media-manifest.json").read_text())
    assets = validate_media(manifest, get_json("/media-integrity.json"))
    if "Disallow: /" not in get_bytes("/robots.txt", 20000).decode():
        raise AssertionError("Robots exclusion missing")
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        verified = list(pool.map(check_media, assets))
    print(f"Independent deployed media SHA256 PASS: {len(verified)}/82")
    visits, gallery_visits = check_browser(index)
    print(f"Independent deployed Chromium PASS: {visits}/30 published page visits, desktop/mobile, search, noindex, visible text, console")
    print(f"Independent production gallery interaction PASS: {gallery_visits}/4 gallery visits, 10 images per viewport, modal, keyboard, focus, original fallback links")
    print("Production security + X-Robots-Tag PASS: 82 media, JSON/robots, 30 published routes, 2 homepages and 2 HTTP 404 checks")
    print("WordPress historical fidelity, rights, PDFs, native comments, security/performance remain separate acceptance items.")

if __name__ == "__main__":
    main()
