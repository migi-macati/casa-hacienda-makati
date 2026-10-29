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
    if ('Left and Right arrow keys' not in help_text or 'Home and End' not in help_text
            or 'Escape to close' not in help_text):
        raise AssertionError('Gallery keyboard instructions missing: ' + route)
    heading = dialog.locator('h2#chm-gallery-title')
    status = dialog.locator('p.chm-gallery-status[role="status"]')
    if (heading.get_attribute('aria-live') is not None or status.count() != 1 or
            status.get_attribute('aria-live') != 'polite' or status.get_attribute('aria-atomic') != 'true'):
        raise AssertionError('Gallery combined position/description status missing: ' + route)
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
        if norm(status.inner_text()) != norm(f'Image {i + 1} of {expected_count}. {source_caption or source_alt}'):
            raise AssertionError('Gallery live status omits position or description: ' + route)
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

def validate_reading_column_geometry(g, width, route):
    """Fail closed if deployed article prose reverts to the over-wide desktop column."""
    required = ("layout", "prose", "sidebar", "proseRight", "sidebarLeft",
                "articleBottom", "sidebarTop")
    if any(k not in g or not isinstance(g[k], (int, float)) for k in required):
        raise AssertionError("Incomplete live reading geometry: " + route)
    if width == 1280:
        if not (930 <= g["layout"] <= 965 and 610 <= g["prose"] <= 665
                and 210 <= g["sidebar"] <= 240
                and g["sidebarLeft"] - g["proseRight"] >= 25):
            raise AssertionError("Desktop reading-width/sidebar regression: " + route + " " + str(g))
    elif width == 375:
        if not (g["layout"] <= 375 and 295 <= g["prose"] <= 335
                and g["sidebarTop"] >= g["articleBottom"] - 3):
            raise AssertionError("Mobile reading-width/stacking regression: " + route + " " + str(g))
    else:
        raise AssertionError("Unreviewed reading-width viewport")
    return True


def check_live_reading_column(page, width, route):
    g = page.evaluate("""() => {
      const layout = document.querySelector('.layout');
      const article = document.querySelector('article.content');
      const sidebar = document.querySelector('.sidebar');
      if (!layout || !article || !sidebar) throw new Error('Reading layout missing');
      const l = layout.getBoundingClientRect();
      const a = article.getBoundingClientRect();
      const s = sidebar.getBoundingClientRect();
      return {layout:l.width, prose:a.width, sidebar:s.width,
              proseRight:a.right, sidebarLeft:s.left,
              articleBottom:a.bottom, sidebarTop:s.top};
    }""")
    return validate_reading_column_geometry(g, width, route)



def validate_comment_bridge_snapshot(s, route):
    """Check one public article's existing WordPress discussion fallback."""
    expected = 'https://casahaciendamakati.wordpress.com' + route
    if not re.fullmatch(r'/\d{4}/\d{2}/\d{2}/[a-z0-9-]+/', route):
        raise AssertionError('Invalid published article route for discussion QA')
    if s.get('originalCount') != 1 or s.get('bridgeCount') != 1 or s.get('bridgeLinks') != 1:
        raise AssertionError('Missing or duplicated original discussion bridge: ' + route)
    if s.get('originalHref') != expected or s.get('bridgeHref') != expected + '#respond':
        raise AssertionError('Discussion bridge target differs from published WordPress route: ' + route)
    if s.get('target') != '_blank' or set((s.get('rel') or '').split()) != {'noopener', 'noreferrer'}:
        raise AssertionError('Unsafe original WordPress discussion target: ' + route)
    if (s.get('name') != 'Read or leave a comment on WordPress ↗' or
            s.get('inOriginal') is not True or s.get('visible') is not True or
            s.get('keyboardFocusable') is not True):
        raise AssertionError('Inaccessible or misplaced WordPress discussion bridge: ' + route)
    if s.get('localCommentForms') != 0:
        raise AssertionError('Unreviewed local comment collection appeared: ' + route)
    return True


def check_live_comment_bridge(page, route):
    s = page.evaluate("""() => {
      const originals = [...document.querySelectorAll('.original')];
      const bridges = [...document.querySelectorAll('.comment-bridge')];
      const links = bridges.flatMap(e => [...e.querySelectorAll('a[href]')]);
      const original = originals[0];
      const bridge = bridges[0];
      const link = links[0];
      const rect = link?.getBoundingClientRect();
      const style = link && getComputedStyle(link);
      return {originalCount:originals.length, bridgeCount:bridges.length,
        bridgeLinks:links.length, originalHref:original?.querySelector(':scope > a[href]')?.href,
        bridgeHref:link?.href, target:link?.getAttribute('target'),
        rel:link?.getAttribute('rel'), name:link?.textContent.trim(),
        inOriginal:!!(original && bridge && bridge.parentElement === original),
        visible:!!(rect && rect.width>0 && rect.height>0 && style.display!=='none' && style.visibility==='visible'),
        keyboardFocusable:!!(link && link.tabIndex>=0),
        localCommentForms:document.querySelectorAll('form[action*="comment"], textarea[name="comment"], #respond form').length};
    }""")
    validate_comment_bridge_snapshot(s, route)
    link = page.locator('.original .comment-bridge a')
    link.focus()
    if not link.evaluate('(el) => document.activeElement === el'):
        raise AssertionError('WordPress discussion link cannot receive focus: ' + route)
    page.keyboard.press('Shift+Tab')
    if not page.locator('.original > a[href]').evaluate('(el) => document.activeElement === el'):
        raise AssertionError('Original-publication link not reachable before discussion link: ' + route)
    page.keyboard.press('Tab')
    if not link.evaluate('(el) => document.activeElement === el'):
        raise AssertionError('Discussion link not keyboard reachable: ' + route)
    return True



def validate_mobile_nav_snapshot(s, route):
    """Fail closed on missing, duplicated or hidden live mobile navigation."""
    links = ["/", "/about/", "/cultural-significance/", "/#archive",
             "https://facebook.com/casahaciendamakati"]
    if (s.get("menus") != 1 or s.get("summaries") != 1 or
            s.get("summaryText") != "Menu" or s.get("navLabel") != "Mobile" or
            s.get("links") != links or s.get("scriptCount") != 1 or
            s.get("scriptSrc") != ORIGIN + "/assets/mobile-nav-keyboard.js" or
            s.get("initiallyOpen") is not False or
            s.get("summaryVisible") is not True or
            s.get("desktopHidden") is not True or
            s.get("summaryFocusable") is not True):
        raise AssertionError("Production mobile navigation structure/visibility regression: " + route)
    return True


def check_live_mobile_nav(page, route):
    snapshot = page.evaluate("""() => {
      const menus = [...document.querySelectorAll('details.mobile-nav')];
      const menu = menus[0];
      const summary = menu?.querySelector(':scope > summary');
      const nav = menu?.querySelector(':scope > nav');
      const desktop = document.querySelector('nav.desktop-nav');
      const rect = summary?.getBoundingClientRect();
      return {
        menus: menus.length, summaries: menu?.querySelectorAll(':scope > summary').length,
        summaryText: summary?.textContent.trim(), navLabel: nav?.getAttribute('aria-label'),
        links: nav && [...nav.querySelectorAll('a[href]')].map(a => a.getAttribute('href')),
        scriptCount: document.querySelectorAll('script[src="/assets/mobile-nav-keyboard.js"]').length,
        scriptSrc: document.querySelector('script[src="/assets/mobile-nav-keyboard.js"]')?.src,
        initiallyOpen: menu?.open,
        summaryVisible: !!(rect && rect.width > 0 && rect.height >= 44 &&
          getComputedStyle(summary).visibility === 'visible'),
        desktopHidden: !!(desktop && getComputedStyle(desktop).display === 'none'),
        summaryFocusable: !!(summary && summary.tabIndex >= 0)
      };
    }""")
    validate_mobile_nav_snapshot(snapshot, route)
    summary = page.locator('details.mobile-nav > summary')
    menu = page.locator('details.mobile-nav')
    summary.click()
    if not menu.evaluate('(el) => el.open'):
        raise AssertionError('Mobile menu failed to open: ' + route)
    link = menu.locator('nav a').nth(1)
    link.focus()
    if not link.evaluate('(el) => document.activeElement === el'):
        raise AssertionError('Mobile menu link cannot receive keyboard focus: ' + route)
    page.keyboard.press('ArrowDown')
    if not menu.evaluate('(el) => el.open'):
        raise AssertionError('Non-Escape key unexpectedly closed mobile menu: ' + route)
    page.keyboard.press('Escape')
    if menu.evaluate('(el) => el.open') or not summary.evaluate('(el) => document.activeElement === el'):
        raise AssertionError('Escape failed to close mobile menu and restore focus: ' + route)
    summary.click()
    if not menu.evaluate('(el) => el.open'):
        raise AssertionError('Mobile menu failed to reopen: ' + route)
    page.locator('main#main-content').focus()
    page.keyboard.press('Escape')
    if not menu.evaluate('(el) => el.open'):
        raise AssertionError('Escape outside mobile menu unexpectedly closed it: ' + route)
    summary.click()
    if menu.evaluate('(el) => el.open'):
        raise AssertionError('Native summary failed to close mobile menu: ' + route)
    return True


def check_mobile_nav_no_js(browser):
    """The native disclosure must remain usable if JavaScript is unavailable."""
    context = browser.new_context(viewport={"width": 375, "height": 812},
                                  java_script_enabled=False)
    try:
        page = context.new_page()
        response = page.goto(ORIGIN + "/", wait_until="load", timeout=45000)
        if not response or response.status != 200:
            raise AssertionError('No-JS homepage unavailable')
        check_security_headers(response, "/")
        menu = page.locator('details.mobile-nav')
        summary = menu.locator('summary')
        if menu.count() != 1 or not summary.is_visible() or menu.evaluate('(el) => el.open'):
            raise AssertionError('No-JS native mobile menu initial state invalid')
        summary.click()
        if not menu.evaluate('(el) => el.open') or menu.locator('nav a:visible').count() != 5:
            raise AssertionError('No-JS native mobile menu failed to open')
        summary.click()
        if menu.evaluate('(el) => el.open'):
            raise AssertionError('No-JS native mobile menu failed to close')
    finally:
        context.close()


def validate_live_search_snapshot(s, known_routes, query):
    """Validate live results against the already verified 15-route published index."""
    if (s.get("query") != query or s.get("robots") != "noindex,nofollow" or
            not isinstance(s.get("status"), str) or
            "temporarily unavailable" in s["status"].lower()):
        raise AssertionError("Live search input, privacy or index-loading regression")
    articles, pages = s.get("articles"), s.get("pages")
    if (not isinstance(articles, list) or not isinstance(pages, list) or
            any(not isinstance(x, str) for x in articles + pages) or
            len(set(articles + pages)) != len(articles + pages) or
            any(x not in known_routes for x in articles + pages)):
        raise AssertionError("Live search result outside published route inventory")
    if query == "":
        if (len(articles) != 13 or pages or not s.get("pagesHidden") or
                s.get("nothingVisible") or s["status"] != "Showing 13 articles."):
            raise AssertionError("Empty search did not restore the 13 published articles")
    elif query in ("unfindableqzxyz", "—"):
        if (articles or pages or not s.get("nothingVisible") or
                not s["status"].startswith("0 results")):
            raise AssertionError("No-match or punctuation-only query returned content")
    elif "result" not in s["status"].lower():
        raise AssertionError("Live search result status missing")
    return articles, pages


def check_live_historical_search(page, index, width):
    """Independently exercise the already deployed search on production Chromium."""
    page.wait_for_function(
        "document.querySelector('#search-status')?.textContent === 'Showing 13 articles.'",
        timeout=15000)
    known_routes = {entry["url"] for entry in index}
    def results(query):
        page.locator("#find").fill(query)
        s = {
            "query": page.locator("#find").input_value(),
            "status": page.locator("#search-status").inner_text(),
            "robots": page.locator('meta[name="robots"]').get_attribute("content"),
            "articles": page.locator(".card:visible h3 a").evaluate_all(
                "(nodes) => nodes.map(n => n.getAttribute('href'))"),
            "pages": page.locator("#page-results a").evaluate_all(
                "(nodes) => nodes.map(n => n.getAttribute('href'))"),
            "pagesHidden": page.locator("#page-results").is_hidden(),
            "nothingVisible": page.locator("#nothing").is_visible(),
        }
        return validate_live_search_snapshot(s, known_routes, query)
    for first, second, label in (
            ("Macati", "Makati", "historical place spelling"),
            ("Haciénda", "Hacienda", "diacritics"),
            ("bahay-na-bato", "bahay na bato", "hyphen/space punctuation")):
        a, b = results(first), results(second)
        if a != b or not any(a):
            raise AssertionError("Production search normalization failed: " + label +
                                 " at " + str(width))
    if results("unfindableqzxyz") != ([], []):
        raise AssertionError("Unmatched live query returned results")
    if results("—") != ([], []):
        raise AssertionError("Punctuation-only live query returned results")
    restored, pages = results("")
    if len(restored) != 13 or pages:
        raise AssertionError("Live archive was not restored after clearing search")
    return True


def check_browser(index):
    from playwright.sync_api import sync_playwright
    errors = []
    visits = 0
    gallery_visits = 0
    mobile_nav_visits = 0
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
                if entry["type"] == "article":
                    check_live_reading_column(page, width, entry["url"])
                    check_live_comment_bridge(page, entry["url"])
                if entry["url"] in GALLERY_ROUTES:
                    check_live_gallery(page, entry["url"], *GALLERY_ROUTES[entry["url"]])
                    gallery_visits += 1
                if width == 375:
                    check_live_mobile_nav(page, entry["url"])
                    mobile_nav_visits += 1
                visits += 1
            response = page.goto(ORIGIN + "/", wait_until="domcontentloaded", timeout=45000)
            if not response or response.status != 200:
                raise AssertionError("Homepage unavailable")
            check_security_headers(response, "/")
            if page.locator('meta[name="robots"]').get_attribute("content") != "noindex,nofollow":
                raise AssertionError("Homepage noindex missing")
            if page.evaluate("document.documentElement.scrollWidth > innerWidth + 3"):
                raise AssertionError("Homepage horizontal overflow at width " + str(width))
            check_live_historical_search(page, index, width)
            if width == 375:
                check_live_mobile_nav(page, "/")
                mobile_nav_visits += 1
            check_missing_route(page)
            if width == 375:
                check_live_mobile_nav(page, "/__chm_qa_unpublished_route_20261028__/")
                mobile_nav_visits += 1
            context.close()
        check_mobile_nav_no_js(browser)
        browser.close()
    if errors:
        raise AssertionError("Browser JavaScript exceptions: " + "; ".join(errors[:5]))
    return visits, gallery_visits, mobile_nav_visits

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
    desktop = {"layout": 960, "prose": 638, "sidebar": 225,
               "proseRight": 824, "sidebarLeft": 869,
               "articleBottom": 600, "sidebarTop": 250}
    mobile = {"layout": 375, "prose": 323, "sidebar": 323,
              "proseRight": 349, "sidebarLeft": 26,
              "articleBottom": 900, "sidebarTop": 930}
    assert validate_reading_column_geometry(desktop, 1280, "/test/")
    assert validate_reading_column_geometry(mobile, 375, "/test/")
    bad_cases = [(dict(desktop, prose=828), 1280),
                 (dict(desktop, sidebarLeft=830), 1280),
                 (dict(mobile, prose=370), 375),
                 (dict(mobile, sidebarTop=850), 375),
                 (dict(mobile, layout=420), 375),
                 (dict(desktop, prose=None), 1280)]
    for bad, viewport in bad_cases:
        try:
            validate_reading_column_geometry(bad, viewport, "/test/")
        except AssertionError:
            pass
        else:
            raise AssertionError("Invalid live reading geometry accepted")

    route = '/2023/08/12/cultural-significance-no-1/'
    expected = 'https://casahaciendamakati.wordpress.com' + route
    valid = {'originalCount': 1, 'bridgeCount': 1, 'bridgeLinks': 1,
             'originalHref': expected, 'bridgeHref': expected + '#respond',
             'target': '_blank', 'rel': 'noopener noreferrer',
             'name': 'Read or leave a comment on WordPress ↗',
             'inOriginal': True, 'visible': True, 'keyboardFocusable': True,
             'localCommentForms': 0}
    assert validate_comment_bridge_snapshot(valid, route)
    for field, value in (
            ('originalCount', 2), ('bridgeCount', 0), ('bridgeLinks', 2),
            ('originalHref', 'https://example.invalid/'),
            ('bridgeHref', 'https://example.invalid/#respond'),
            ('target', '_self'), ('rel', 'noopener'), ('name', 'Comment'),
            ('inOriginal', False), ('visible', False),
            ('keyboardFocusable', False), ('localCommentForms', 1)):
        invalid = dict(valid)
        invalid[field] = value
        try:
            validate_comment_bridge_snapshot(invalid, route)
        except AssertionError:
            pass
        else:
            raise AssertionError('Invalid discussion bridge accepted: ' + field)
    valid_nav = {"menus": 1, "summaries": 1, "summaryText": "Menu",
                 "navLabel": "Mobile", "links": ["/", "/about/",
                 "/cultural-significance/", "/#archive",
                 "https://facebook.com/casahaciendamakati"],
                 "scriptCount": 1, "scriptSrc": ORIGIN + "/assets/mobile-nav-keyboard.js",
                 "initiallyOpen": False, "summaryVisible": True,
                 "desktopHidden": True, "summaryFocusable": True}
    assert validate_mobile_nav_snapshot(valid_nav, "/test/")
    for field, value in (
            ("menus", 2), ("summaries", 0), ("summaryText", "Navigation"),
            ("navLabel", None), ("links", ["/"]), ("scriptCount", 0),
            ("scriptSrc", "https://example.invalid/mobile-nav-keyboard.js"),
            ("initiallyOpen", True), ("summaryVisible", False),
            ("desktopHidden", False), ("summaryFocusable", False)):
        bad = dict(valid_nav, **{field: value})
        try:
            validate_mobile_nav_snapshot(bad, "/test/")
        except AssertionError:
            pass
        else:
            raise AssertionError("Invalid mobile navigation accepted: " + field)

    search_routes = {"/2023/08/12/example/", "/about/"}
    good_search = {"query": "Macati", "status": "1 result", "robots": "noindex,nofollow",
                   "articles": ["/2023/08/12/example/"], "pages": [],
                   "pagesHidden": True, "nothingVisible": False}
    assert validate_live_search_snapshot(good_search, search_routes, "Macati") == (
        ["/2023/08/12/example/"], [])
    for field, bad_value in (
            ("query", "Makati"), ("status", "Search temporarily unavailable"),
            ("robots", "index,follow"), ("articles", ["/private/"]),
            ("articles", ["/2023/08/12/example/", "/2023/08/12/example/"]),
            ("pages", ["/2023/08/12/example/"]), ("pages", None)):
        bad = dict(good_search, **{field: bad_value})
        try:
            validate_live_search_snapshot(bad, search_routes, "Macati")
        except AssertionError:
            pass
        else:
            raise AssertionError("Invalid production search accepted: " + field)
    for q in ("unfindableqzxyz", "—"):
        bad = dict(good_search, query=q, status="0 results")
        try:
            validate_live_search_snapshot(bad, search_routes, q)
        except AssertionError:
            pass
        else:
            raise AssertionError("Invalid no-match search accepted: " + q)
    empty = dict(good_search, query="", status="Showing 13 articles.")
    try:
        validate_live_search_snapshot(empty, search_routes, "")
    except AssertionError:
        pass
    else:
        raise AssertionError("Incomplete unfiltered archive accepted")
    print("Production acceptance self-tests PASS: media/index/gallery, 11 HTTP privacy, 12 discussion and 11 mobile-nav negative fixtures plus 10 live-search mutations")

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
    visits, gallery_visits, mobile_nav_visits = check_browser(index)
    print(f"Independent deployed Chromium PASS: {visits}/30 published page visits, desktop/mobile, search, noindex, visible text, console")
    print("Live article reading-column geometry PASS: 26/26 desktop/mobile visits; prose width, sidebar separation and mobile stacking")
    print("Live original WordPress discussion fallback PASS: 26/26 article visits; exact targets, keyboard order, visible links and no local collection")
    print(f"Independent production gallery interaction PASS: {gallery_visits}/4 gallery visits, 10 images per viewport, modal, keyboard, focus, original fallback links")
    print(f"Independent live mobile navigation PASS: {mobile_nav_visits}/17 published/home/404 routes; Escape/focus/outside-focus; no-JS native disclosure")
    print("Independent live historical search PASS: 2/2 desktop/mobile suites; Macati, accents, punctuation, no-results and archive restore")
    print("Production security + X-Robots-Tag PASS: 82 media, JSON/robots, 30 published routes, 2 homepages and 2 HTTP 404 checks")
    print("WordPress historical fidelity, rights, PDFs, native comments, security/performance remain separate acceptance items.")

if __name__ == "__main__":
    main()
