#!/usr/bin/env python3
"""Generated-site Chromium check for 22 source-note accessible names.
Read-only: no WordPress/Facebook/network calls, no private drafts or PDF changes.
This is automated link-name QA, not manual screen-reader certification.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

TARGETS = [
    ('2023/08/12/cultural-significance-no-1/index.html', 4),
    ('2023/10/21/history-of-barrio-olimpia-makati-rizal/index.html', 4),
    ('2024/02/06/cultural-significance-no-11/index.html', 14),
]
css = Path('public/assets/style.css').read_text()
with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    checks = 0
    for route, count in TARGETS:
        html = Path('public', route).read_text()
        tag = '<link rel="stylesheet" href="/assets/style.css">'
        assert html.count(tag) == 1, route
        html = html.replace(tag, '<style>' + css + '</style>')
        for width in (320, 375, 1280):
            for js in (False, True):
                page = browser.new_page(viewport={'width':width,'height':812},
                                        java_script_enabled=js, reduced_motion='reduce')
                page.route('**/*', lambda request: request.abort())
                page.set_content(html, wait_until='domcontentloaded')
                assert page.locator('meta[name="robots"]').get_attribute('content') == 'noindex,nofollow'
                refs = page.locator('article.content sup[data-fn]')
                assert refs.count() == count
                assert page.locator('section.source-notes li').count() == count
                for n in range(1, count + 1):
                    ref = refs.nth(n-1)
                    anchor = ref.locator('a')
                    assert ref.inner_text().strip() == str(n), (route,n,'visible')
                    assert anchor.inner_text().strip() == str(n), (route,n,'clickable')
                    assert anchor.get_attribute('aria-label') == f'Go to source note {n}'
                    assert page.get_by_role('link', name=f'Go to source note {n}', exact=True).count() == 1
                    uid = anchor.get_attribute('href')[1:]
                    assert page.locator('section.source-notes li[id="' + uid + '"]').count() == 1
                    assert page.locator('a.source-backlink[href="#' + uid + '-link"]').count() == 1
                tenth = refs.nth(9 if count > 9 else 0).locator('a')
                tenth.focus()
                assert tenth.evaluate('(e) => document.activeElement === e')
                tenth.press('Enter')
                assert page.evaluate('location.hash').lstrip('#') == tenth.get_attribute('href')[1:]
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), (route,width)
                checks += 1
                page.close()
    browser.close()
assert checks == 18
print('Source-note browser PASS: 22 named links, 18 viewport/JS checks, keyboard/noindex/no overflow.')
