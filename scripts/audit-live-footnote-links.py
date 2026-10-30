#!/usr/bin/env python3
"""Independent read-only production acceptance for 13 No. 10 source-note links.

No source writes, external requests, PDF derivatives, or manual screen-reader claim.
"""
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright

ORIGIN = 'https://casa-hacienda-makati.vercel.app'
ROUTE = '/2023/10/21/cultural-significance-no-10/'
REF = re.compile(r'<sup data-fn="([0-9a-f-]{36})" class="fn"><a href="#\1" id="\1-link" aria-label="Go to source note (\d+)">(\d+)</a></sup>')

def validate_html(html):
    assert '<meta name="robots" content="noindex,nofollow">' in html, 'noindex meta'
    assert len(re.findall(r'<sup\b[^>]*\bdata-fn=', html)) == 13, '13 original references'
    matches = REF.findall(html)
    assert len(matches) == 13, 'all links contain complete numerals and labels'
    ids = set()
    for i, (uid, name, visible) in enumerate(matches, 1):
        assert uid not in ids and name == visible == str(i), ('number/name/unique id', i)
        ids.add(uid)
        assert f'<li id="{uid}">' in html, ('source-note destination', i)
        assert f'href="#{uid}-link"' in html, ('return link', i)
    return matches

def self_test():
    ids = [f'{i:08x}-1111-2222-3333-444444444444' for i in range(1, 14)]
    fixture = '<meta name="robots" content="noindex,nofollow">'
    fixture += ''.join(f'<sup data-fn="{u}" class="fn"><a href="#{u}" id="{u}-link" aria-label="Go to source note {i}">{i}</a></sup>'
                       for i, u in enumerate(ids, 1))
    fixture += ''.join(f'<li id="{u}">Note <a href="#{u}-link">Return</a></li>' for u in ids)
    assert len(validate_html(fixture)) == 13
    u = ids[9]
    mutations = [
        fixture.replace('noindex,nofollow', 'index,follow'),
        fixture.replace('Go to source note 10', 'Go to source note 1'),
        fixture.replace('>10</a>', '>1</a>0'),
        fixture.replace('>11</a>', '>12</a>'),
        fixture.replace(f'href="#{u}"', 'href="#wrong"'),
        fixture.replace(f'id="{u}-link"', 'id="wrong-link"'),
        fixture.replace(f'<li id="{u}">', '<li id="wrong">'),
        fixture.replace(f'href="#{u}-link"', 'href="#wrong"'),
        fixture.replace('aria-label="Go to source note 13"', 'aria-label="Go to note 13"'),
        fixture.replace(f'data-fn="{u}"', 'data-fn="wrong"'),
        fixture.replace(f'<sup data-fn="{u}"', '<sup data-fn="00000000-0000-0000-0000-000000000000"')
    ]
    for i, mutated in enumerate(mutations):
        assert mutated != fixture, ('mutation changed fixture', i)
        try:
            validate_html(mutated)
        except AssertionError:
            continue
        raise AssertionError(f'Unsafe footnote mutation accepted: {i}')
    print('Live footnote synthetic PASS: 13 references, 11 fail-closed fixtures')

def audit():
    records = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        for width in (320, 375, 1280):
            for js in (False, True):
                context = browser.new_context(viewport={'width': width, 'height': 812},
                                              java_script_enabled=js, reduced_motion='reduce')
                external = []
                def restrict(route):
                    u = urlsplit(route.request.url)
                    if route.request.method not in ('GET', 'HEAD') or u.scheme != 'https' or u.netloc != urlsplit(ORIGIN).netloc:
                        external.append(route.request.url.split('?')[0])
                        route.abort()
                    else:
                        route.continue_()
                context.route('**/*', restrict)
                page = context.new_page()
                response = page.goto(ORIGIN + ROUTE, wait_until='domcontentloaded', timeout=45000)
                assert response and response.status == 200 and page.url == ORIGIN + ROUTE
                headers = response.headers
                assert 'noindex' in headers.get('x-robots-tag', '').lower()
                assert 'nofollow' in headers.get('x-robots-tag', '').lower()
                matches = validate_html(response.text())
                refs = page.locator('article.content sup[data-fn]')
                assert refs.count() == 13
                for i, (uid, _, _) in enumerate(matches, 1):
                    ref = refs.nth(i - 1)
                    anchor = ref.locator('a')
                    assert ref.inner_text().strip() == anchor.inner_text().strip() == str(i)
                    assert anchor.get_attribute('aria-label') == f'Go to source note {i}'
                    assert page.get_by_role('link', name=f'Go to source note {i}', exact=True).count() == 1
                    assert page.locator(f'section.source-notes li[id="{uid}"]').count() == 1
                tenth = refs.nth(9).locator('a')
                tenth.focus()
                assert tenth.evaluate('(e) => document.activeElement === e')
                tenth.press('Enter')
                assert page.evaluate('location.hash').lstrip('#') == matches[9][0]
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
                assert not external, ('external requests blocked', external)
                records.append({'width': width, 'javascript': js, 'references': 13,
                                'noindex_header': True, 'noindex_meta': True,
                                'external_requests': 0, 'keyboard': 'pass'})
                print(f'LIVE source notes PASS: {width}px JS={js}, 13 links', flush=True)
                context.close()
        browser.close()
    Path('artifacts').mkdir(exist_ok=True)
    Path('artifacts/live-footnote-links.json').write_text(json.dumps({
        'scope': 'No. 10 published route, 13 original source-note links',
        'checks': records,
        'limitations': 'Programmatic accessible-name/keyboard checks; not manual screen-reader acceptance or PDF remediation'
    }, indent=2) + '\n')
    print('Independent live footnote PASS: 6 production browser visits, 13 links per visit, noindex and no external requests')

if __name__ == '__main__':
    if sys.argv[1:] == ['--self-test']:
        self_test()
    elif not sys.argv[1:]:
        audit()
    else:
        raise SystemExit('Usage: audit-live-footnote-links.py [--self-test]')
