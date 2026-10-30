#!/usr/bin/env python3
"""Generated-site Chromium: published Gutenberg embed URLs are keyboard-usable links."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

root = Path('public')
lock = json.loads(Path('ops/published-search-sources.json').read_text())
css = (root / 'assets/style.css').read_text()
total = 0
routes = 0
with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    page = browser.new_page()
    # Never request any original embed host, including Facebook.
    page.route('**/*', lambda route: route.abort())
    for item in lock['documents']:
        markup = (root / item['file']).read_text()
        count = markup.count('class="wp-embed-source-link"')
        if not count:
            continue
        routes += 1
        assert '<meta name="robots" content="noindex,nofollow">' in markup
        markup = markup.replace('<link rel="stylesheet" href="/assets/style.css">',
                                '<style>' + css + '</style>')
        for width in (320, 375, 1280):
            page.set_viewport_size({'width': width, 'height': 800})
            page.set_content(markup, wait_until='domcontentloaded')
            links = page.locator('article.content .wp-block-embed__wrapper a.wp-embed-source-link')
            assert links.count() == count, (item['file'], width, count)
            assert page.locator('article.content .wp-block-embed__wrapper iframe').count() == 0
            for index in range(count):
                link = links.nth(index)
                href = link.get_attribute('href')
                assert href and href.startswith('https://'), (item['file'], href)
                assert link.get_attribute('target') == '_blank'
                assert {'noopener', 'noreferrer'} <= set(link.get_attribute('rel').split())
                assert link.evaluate("(e) => getComputedStyle(e).textDecorationLine.includes('underline')")
                assert link.evaluate("(e) => e.getBoundingClientRect().width <= innerWidth + 1")
                link.focus()
                assert link.evaluate("(e) => document.activeElement === e")
            total += count
    browser.close()
assert routes == 8 and total == 84, (routes, total)
print('Gutenberg external source fallback: 28 links x 3 viewports, 8 routes PASS; no external requests.')
