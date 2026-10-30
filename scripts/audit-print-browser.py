#!/usr/bin/env python3
"""Read-only generated-site Chromium print-mode audit. Does not create PDF derivatives."""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

root=Path('public')
lock=json.loads(Path('ops/published-search-sources.json').read_text())
css=(root/'assets/style.css').read_text()
assert len(lock['documents'])==15
with sync_playwright() as pw:
    launch={'headless':True}
    if os.environ.get('CHROMIUM_PATH'):
        launch['executable_path']=os.environ['CHROMIUM_PATH']
    browser=pw.chromium.launch(**launch)
    for width in (375,1280):
        page=browser.new_page(viewport={'width':width,'height':812})
        page.route('**/*',lambda route:route.abort())
        for doc in lock['documents']:
            html=(root/doc['file']).read_text()
            link='<link rel="stylesheet" href="/assets/style.css">'
            assert html.count(link)==1,('stylesheet identity',doc['file'])
            html=html.replace(link,'<style>'+css+'</style>')
            page.set_content(html,wait_until='domcontentloaded')
            article=page.locator('article.content')
            assert article.count()==1,('article',doc['file'])
            before=article.inner_text()
            links=article.locator('a').count()
            assert page.locator('.siteheader').evaluate('(e)=>getComputedStyle(e).display')!='none'
            page.emulate_media(media='print')
            assert page.locator('.siteheader').evaluate('(e)=>getComputedStyle(e).display')=='none'
            assert page.locator('.layout').evaluate('(e)=>getComputedStyle(e).display')=='block'
            assert article.evaluate('(e)=>getComputedStyle(e).display')!='none'
            assert page.locator('body').evaluate('(e)=>getComputedStyle(e).backgroundColor')=='rgb(255, 255, 255)'
            assert article.inner_text()==before,('published text changed in print',doc['file'],width)
            assert article.locator('a').count()==links,('links missing',doc['file'],width)
            assert all(v=='none' for v in article.locator('.wp-block-spacer').evaluate_all(
                '(els)=>els.map(e=>getComputedStyle(e).display)')),('spacer',doc['file'],width)
            assert page.locator('meta[name="robots"]').get_attribute('content')=='noindex,nofollow'
            page.emulate_media(media='screen')
            assert page.locator('.siteheader').evaluate('(e)=>getComputedStyle(e).display')!='none'
        page.close()
    browser.close()
print('Print-mode Chromium PASS: 15 published documents at 375/1280px; source text/links retained; no PDF generated.')
