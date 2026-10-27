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
        for width, height in [(1280, 800), (375, 812)]:
            page = browser.new_page(viewport={'width': width, 'height': height})
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            for route, count, linked in ROUTES:
                page.goto(base + route, wait_until='networkidle')
                gallery = page.locator('article.content .wp-block-gallery')
                assert gallery.count() == 1
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
        browser.close()
finally:
    server.shutdown()
    server.server_close()
print('Gallery browser PASS: 2 galleries, 10 images, desktop/mobile; modal navigation, Escape, focus, fallback links, no JS errors.')
