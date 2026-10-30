#!/usr/bin/env python3
"""Read-only generated-site Chromium check for original Significance Gutenberg borders."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

root = Path('public')
css = (root / 'assets/style.css').read_text()
html = (root / 'cultural-significance/index.html').read_text()
stylesheet = '<link rel="stylesheet" href="/assets/style.css">'
assert html.count(stylesheet) == 1, 'exact local stylesheet reference'
assert html.count('<meta name="robots" content="noindex,nofollow">') == 1
html = html.replace(stylesheet, '<style>' + css + '</style>')
with sync_playwright() as pw:
    launch = {'headless': True}
    if os.environ.get('CHROMIUM_PATH'):
        launch['executable_path'] = os.environ['CHROMIUM_PATH']
    browser = pw.chromium.launch(**launch)
    for width in (320, 375, 1280):
        page = browser.new_page(viewport={'width': width, 'height': 812})
        page.route('**/*', lambda route: route.abort())
        page.set_content(html, wait_until='domcontentloaded')
        rows = page.locator('article.content p.has-border-color.has-base-border-color')
        assert rows.count() == 12, ('original frames', width)
        details = rows.evaluate_all('''nodes => nodes.map(e => {
          const s = getComputedStyle(e);
          const b = e.getBoundingClientRect();
          return {style:s.borderTopStyle,width:s.borderTopWidth,color:s.borderTopColor,
                  right:b.right,left:b.left,visible:b.width > 0 && b.height > 0};
        })''')
        assert all(d['style'] == 'solid' and d['width'] == '15px'
                   and d['color'] == 'rgb(252, 249, 241)' and d['visible']
                   for d in details), ('computed Gutenberg frames', width, details)
        assert all(d['left'] >= -1 and d['right'] <= width + 1 for d in details), ('frame viewport', width)
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), ('document overflow', width)
        assert page.locator('article.content .wp-block-button__link[href]').count() == 12, ('published links', width)
        assert page.locator('meta[name="robots"]').get_attribute('content') == 'noindex,nofollow'
        page.close()
    browser.close()
print('Significance border browser PASS: 12 original frames at 320/375/1280px, no overflow, links and noindex retained.')
