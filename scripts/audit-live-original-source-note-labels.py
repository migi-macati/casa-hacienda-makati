#!/usr/bin/env python3
"""Independent read-only production Chromium acceptance for 22 named source-note links.

Three already-published routes only; no WordPress, Facebook, PDF, draft or rights operations.
This tests link names and keyboard activation, not manual screen-reader certification.
"""
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright

ORIGIN = 'https://casa-hacienda-makati.vercel.app'
TARGETS = [
    ('/2023/08/12/cultural-significance-no-1/', 4),
    ('/2023/10/21/history-of-barrio-olimpia-makati-rizal/', 4),
    ('/2024/02/06/cultural-significance-no-11/', 14),
]
REF = re.compile(r'<sup data-fn="([0-9a-f-]{36})" class="fn"><a href="#\1" id="\1-link" aria-label="Go to source note (\d+)">(\d+)</a></sup>')

def validate_html(html, count):
    assert '<meta name="robots" content="noindex,nofollow">' in html, 'noindex meta'
    assert len(re.findall(r'<sup\b[^>]*\bdata-fn=', html)) == count, 'source-note count'
    matches = REF.findall(html)
    assert len(matches) == count, 'every link has exact approved markup'
    ids = set()
    for i, (uid, name, visible) in enumerate(matches, 1):
        assert uid not in ids and name == visible == str(i), ('ordinal/name/unique UUID', i)
        ids.add(uid)
        assert '<li id="' + uid + '">' in html, ('source-note target', i)
        assert 'href="#' + uid + '-link"' in html, ('source-note backlink', i)
    return matches

def self_test():
    for count in (4, 14):
        ids = [f'{i:08x}-1111-2222-3333-444444444444' for i in range(1, count+1)]
        refs = [
            f'<sup data-fn="{uid}" class="fn"><a href="#{uid}" id="{uid}-link" aria-label="Go to source note {i}">{i}</a></sup>'
            for i, uid in enumerate(ids, 1)
        ]
        notes = [
            f'<li id="{uid}">Source <a href="#{uid}-link">Return</a></li>'
            for uid in ids
        ]
        fixture = '<meta name="robots" content="noindex,nofollow">' + ''.join(refs) + ''.join(notes)
        assert len(validate_html(fixture, count)) == count
        uid = ids[0]
        mutations = [
            fixture.replace('noindex,nofollow', 'index,follow'),
            fixture.replace('Go to source note 1', 'Go to source note 99'),
            fixture.replace('>1</a></sup>', '>2</a></sup>'),
            fixture.replace(f'href="#{uid}"', 'href="#wrong"'),
            fixture.replace(f'id="{uid}-link"', 'id="wrong-link"'),
            fixture.replace(f'<li id="{uid}">', '<li id="wrong">'),
            fixture.replace(f'href="#{uid}-link"', 'href="#wrong"'),
            fixture.replace('aria-label="Go to source note 1"', 'aria-label="Source 1"'),
            fixture.replace(refs[0], refs[0] + refs[0]),
            fixture.replace(refs[0], ''),
            fixture.replace(f'data-fn="{uid}"', 'data-fn="00000000-0000-0000-0000-000000000000"'),
            fixture.replace('class="fn"', 'class="wrong"', 1),
        ]
        for i, bad in enumerate(mutations):
            assert bad != fixture, ('fixture mutation', count, i)
            try:
                validate_html(bad, count)
            except AssertionError:
                continue
            raise AssertionError(f'Unsafe live source-note mutation accepted: {count}/{i}')
    print('Independent live source-note self-test PASS: 24 fail-closed fixtures')

def audit():
    evidence = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        for route, count in TARGETS:
            for width in (320, 375, 1280):
                for js in (False, True):
                    context = browser.new_context(viewport={'width':width,'height':812},
                                                  java_script_enabled=js, reduced_motion='reduce')
                    external = []
                    def restrict(request_route):
                        u = urlsplit(request_route.request.url)
                        if request_route.request.method not in ('GET', 'HEAD') or u.scheme != 'https' or u.netloc != urlsplit(ORIGIN).netloc:
                            external.append(request_route.request.url.split('?')[0])
                            request_route.abort()
                        else:
                            request_route.continue_()
                    context.route('**/*', restrict)
                    page = context.new_page()
                    response = page.goto(ORIGIN + route, wait_until='domcontentloaded', timeout=45000)
                    assert response and response.status == 200 and page.url == ORIGIN + route
                    page.wait_for_load_state('load', timeout=20000)
                    page.evaluate('() => Promise.race([document.fonts.ready, new Promise(r=>setTimeout(r,3000))])')
                    assert 'noindex' in response.headers.get('x-robots-tag','').lower()
                    assert 'nofollow' in response.headers.get('x-robots-tag','').lower()
                    matches = validate_html(response.text(), count)
                    refs = page.locator('article.content sup[data-fn]')
                    assert refs.count() == count
                    assert page.locator('section.source-notes li').count() == count
                    for i, (uid, _name, _visible) in enumerate(matches, 1):
                        ref = refs.nth(i-1)
                        a = ref.locator('a')
                        assert ref.inner_text().strip() == str(i)
                        assert a.inner_text().strip() == str(i)
                        assert a.get_attribute('aria-label') == f'Go to source note {i}'
                        assert page.get_by_role('link', name=f'Go to source note {i}', exact=True).count() == 1
                        assert a.get_attribute('href') == '#' + uid
                        assert page.locator('section.source-notes li[id="' + uid + '"]').count() == 1
                        assert page.locator('a.source-backlink[href="#' + uid + '-link"]').count() == 1
                    focus = refs.nth(9 if count > 9 else 0).locator('a')
                    focus.focus()
                    assert focus.evaluate('(e) => document.activeElement === e')
                    focus.press('Enter')
                    assert page.evaluate('location.hash').lstrip('#') == focus.get_attribute('href')[1:]
                    page.wait_for_timeout(250)
                    overflow = page.evaluate("""() => ({
                      scrollWidth: document.documentElement.scrollWidth,
                      viewportWidth: innerWidth,
                      offenders: [...document.querySelectorAll('body *')].filter(e => {
                        const r=e.getBoundingClientRect();
                        return r.width > 0 && r.right > innerWidth+1;
                      }).slice(0,5).map(e=>({tag:e.tagName.toLowerCase(),
                        classes:String(e.className||'').slice(0,80)}))
                    })""")
                    assert overflow['scrollWidth'] <= overflow['viewportWidth'] + 1, (route,width,js,overflow)
                    assert not external, ('third-party requests prohibited', external)
                    evidence.append({'route':route,'count':count,'viewport':width,'javascript':js,
                                     'status':response.status,'noindex':True,'keyboard':True,'external_requests':0})
                    context.close()
        browser.close()
    assert len(evidence) == 18
    Path('artifacts').mkdir(exist_ok=True)
    Path('artifacts/live-original-source-note-labels.json').write_text(json.dumps({
        'scope':'three public source-note routes only','visits':len(evidence),
        'links_per_route':[4,4,14],'manual_screen_reader':'pending',
        'records':evidence
    }, indent=2))
    print('Independent LIVE source-note PASS: 22 links, 18 production Chromium contexts, keyboard/noindex/no overflow.')

if __name__ == '__main__':
    if '--self-test' in sys.argv:
        self_test()
    else:
        audit()
