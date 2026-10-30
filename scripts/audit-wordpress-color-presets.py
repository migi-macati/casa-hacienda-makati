#!/usr/bin/env python3
"""Generated-site Chromium check of source-defined Gutenberg text colors; no remote requests."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

root = Path('public')
css = (root / 'assets/style.css').read_text()
targets = [
    ('2023/08/12/cultural-significance-no-1/index.html',
     '.content .has-primary-color.has-text-color', 5, 'rgb(28, 59, 48)'),
    ('2023/10/21/history-of-barrio-olimpia-makati-rizal/index.html',
     '.content .has-foreground-color.has-text-color', 53, 'rgb(36, 62, 48)'),
    ('2023/10/21/history-of-barrio-olimpia-makati-rizal/index.html',
     '.content .has-black-color.has-text-color', 3, 'rgb(17, 17, 17)'),
    ('2024/10/28/cultural-significance-no-12/index.html',
     '.content .has-primary-color.has-text-color', 1, 'rgb(28, 59, 48)'),
]
with sync_playwright() as pw:
    launch = {'headless': True}
    if os.environ.get('CHROMIUM_PATH'):
        launch['executable_path'] = os.environ['CHROMIUM_PATH']
    browser = pw.chromium.launch(**launch)
    for width in (320, 375, 1280):
        page = browser.new_page(viewport={'width': width, 'height': 812})
        page.route('**/*', lambda route: route.abort())
        for path, selector, count, expected in targets:
            html = (root / path).read_text()
            link = '<link rel="stylesheet" href="/assets/style.css">'
            assert html.count(link) == 1, ('source stylesheet', path)
            html = html.replace(link, '<style>' + css + '</style>')
            page.set_content(html, wait_until='domcontentloaded')
            items = page.locator(selector)
            assert items.count() == count, ('original color classes', path, width)
            colors = items.evaluate_all('nodes => nodes.map(e => getComputedStyle(e).color)')
            assert all(c == expected for c in colors), ('computed color', path, width, colors)
            assert page.locator('meta[name="robots"]').get_attribute('content') == 'noindex,nofollow'
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), ('overflow', path, width)
        page.close()
    browser.close()
print('Gutenberg text colors PASS: source-defined classes and computed styles at 320/375/1280px.')
