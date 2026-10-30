#!/usr/bin/env python3
"""Test generated gallery enhancement with real Chromium and a local static server."""
import functools
import os
import http.server
import threading
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path('public').resolve()
ROUTES = [
    ('/2023/08/12/cultural-significance-no-1/', 3, False),
    ('/2023/10/21/history-of-barrio-olimpia-makati-rizal/', 7, True),
]
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT))
server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
base = f'http://127.0.0.1:{server.server_port}'
try:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, **({'executable_path': os.environ['CHROMIUM_PATH']} if os.environ.get('CHROMIUM_PATH') else {}))
        for width, height in [(1280, 800), (375, 812), (320, 812)]:
            page = browser.new_page(viewport={'width': width, 'height': height})
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            for route, count, linked in ROUTES:
                page.goto(base + route, wait_until='networkidle')
                gallery = page.locator('article.content .wp-block-gallery')
                assert gallery.count() == 1
                expected_columns = (1 if width <= 350 else 2 if width <= 710 else 4 if linked else 3)
                assert gallery.evaluate('(e) => getComputedStyle(e).display') == 'grid', (route, width, 'grid display')
                actual_columns = gallery.evaluate('(e) => getComputedStyle(e).gridTemplateColumns.split(" ").filter(Boolean).length')
                assert actual_columns == expected_columns, (route, width, actual_columns, expected_columns)
                figures = gallery.locator('figure.wp-block-image')
                assert figures.count() == count, (route, width, 'original gallery figures')
                assert figures.evaluate_all('(nodes) => nodes.every(e => getComputedStyle(e).marginTop === "0px" && e.getBoundingClientRect().width > 0)')
                assert figures.locator('img').evaluate_all('(nodes) => nodes.every(e => getComputedStyle(e).objectFit === "contain" && e.getBoundingClientRect().width > 0 && e.alt.trim())')
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), (route, width, 'document overflow')
                triggers = gallery.locator('a[href]' if linked else 'button.chm-gallery-trigger')
                assert triggers.count() == count, f'{route}: expected {count} triggers'
                if linked:
                    assert all('casahaciendamakati.wordpress.com' in x for x in triggers.evaluate_all('(nodes) => nodes.map(n => n.href)'))
                triggers.first.click()
                dialog = page.locator('dialog.chm-gallery-dialog')
                assert dialog.is_visible(), f'{route}: viewer did not open'
                assert dialog.locator('h2').inner_text() == f'Image 1 of {count}'
                assert dialog.locator('img').get_attribute('alt')
                assert '/media/' in dialog.locator('img').get_attribute('src')
                assert dialog.evaluate('(node) => getComputedStyle(node).position') == 'fixed'
                page.keyboard.press('ArrowRight')
                assert dialog.locator('h2').inner_text() == f'Image 2 of {count}'
                page.keyboard.press('Escape')
                assert not dialog.is_visible()
                assert triggers.first.evaluate('(node) => document.activeElement === node'), 'Focus not restored'
                assert not errors, f'{route}: JS exceptions: {errors}'
            page.close()
        # With JavaScript disabled, the same original seven linked scans remain accessible.
        fallback = browser.new_page(viewport={'width': 375, 'height': 812}, java_script_enabled=False)
        fallback.goto(base + ROUTES[1][0], wait_until='domcontentloaded')
        gallery = fallback.locator('article.content .wp-block-gallery')
        assert gallery.evaluate('(e) => getComputedStyle(e).display') == 'grid'
        assert gallery.locator('a[href]').count() == 7
        assert gallery.evaluate('(e) => getComputedStyle(e).gridTemplateColumns.split(" ").filter(Boolean).length') == 2
        assert fallback.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
        fallback.close()
        browser.close()
finally:
    server.shutdown()
    server.server_close()
print('Gallery browser PASS: 2 galleries, 10 images, 320/375/1280px grid, no-JS fallback, modal navigation, Escape, focus, no overflow or JS errors.')
