#!/usr/bin/env python3
"""Generated-site Chromium accessibility checks for original No. 10 footnote links.

Read-only. No source article writes, OCR, PDF derivatives, social fetches, or third-party requests.
This checks programmatic link names and keyboard activation, not manual screen-reader output.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

route = Path('public/2023/10/21/cultural-significance-no-10/index.html')
html = route.read_text()
css = Path('public/assets/style.css').read_text()
link = '<link rel="stylesheet" href="/assets/style.css">'
assert html.count(link) == 1
html = html.replace(link, '<style>' + css + '</style>')
with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    for width in (320, 375, 1280):
        page = browser.new_page(viewport={'width': width, 'height': 812},
                                java_script_enabled=False)
        page.route('**/*', lambda request: request.abort())
        page.set_content(html, wait_until='domcontentloaded')
        assert page.locator('meta[name="robots"]').get_attribute('content') == 'noindex,nofollow'
        refs = page.locator('article.content sup[data-fn]')
        assert refs.count() == 13
        assert page.locator('section.source-notes li').count() == 13
        for n in range(1, 14):
            ref = refs.nth(n - 1)
            anchor = ref.locator('a')
            assert ref.inner_text().strip() == str(n), ('visible numeral', n)
            assert anchor.inner_text().strip() == str(n), ('complete clickable numeral', n)
            assert anchor.get_attribute('aria-label') == f'Go to source note {n}'
            assert page.get_by_role('link', name=f'Go to source note {n}', exact=True).count() == 1
            target = anchor.get_attribute('href')[1:]
            assert page.locator('section.source-notes li[id="' + target + '"]').count() == 1
            assert page.locator('a.source-backlink[href="#' + target + '-link"]').count() == 1
        tenth = refs.nth(9).locator('a')
        tenth.focus()
        assert tenth.evaluate('(e) => document.activeElement === e')
        tenth.press('Enter')
        assert page.evaluate('location.hash').lstrip('#') == tenth.get_attribute('href')[1:]
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), width
        page.close()
    browser.close()
print('Footnote browser PASS: 13 accessible references, four two-digit links, 320/375/1280px, keyboard, noindex and no overflow.')
