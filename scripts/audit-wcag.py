#!/usr/bin/env python3
"""Read-only automated WCAG HTML scan of homepage and 15 published routes.

Uses pinned axe-core in Chromium. Does not assess PDF interiors, manual
screen-reader operation, original WordPress visual parity or media rights.
"""
import argparse
import json
import re
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

ORIGIN = 'https://casa-hacienda-makati.vercel.app'
AXE = Path('node_modules/axe-core/axe.min.js')
TAGS = ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa']
VIEWPORTS = [(1280, 800), (375, 812)]

def validate_routes(index):
    if not isinstance(index, list) or len(index) != 15:
        raise AssertionError('Expected exactly 15 published routes')
    if sum(isinstance(x, dict) and x.get('type') == 'article' for x in index) != 13:
        raise AssertionError('Expected 13 published articles')
    if sum(isinstance(x, dict) and x.get('type') == 'page' for x in index) != 2:
        raise AssertionError('Expected 2 published pages')
    routes = [x['url'] for x in index]
    if len(set(routes)) != 15 or set(x['url'] for x in index if x['type'] == 'page') != {'/about/', '/cultural-significance/'}:
        raise AssertionError('Unexpected or duplicate published route')
    for route in routes:
        if not isinstance(route, str) or not re.fullmatch(r'/[a-z0-9/-]+/', route) or '//' in route or '..' in route:
            raise AssertionError('Unsafe published route')
    return ['/'] + routes

def summarize(scans):
    violations = [{'route': scan['route'], 'viewport': scan['viewport'], **v}
                  for scan in scans for v in scan['violations']]
    serious = [v for v in violations if v.get('impact') in {'critical', 'serious'}]
    return {'scans': len(scans), 'violations': len(violations),
            'serious_or_critical': len(serious),
            'by_rule': dict(sorted(Counter(v['id'] for v in violations).items())),
            'failing': serious}

def fetch_index():
    req = urllib.request.Request(ORIGIN + '/search-index.json',
                                 headers={'User-Agent': 'CasaHaciendaA11yReadOnlyQA/1.0'})
    with urllib.request.urlopen(req, timeout=35) as response:
        if response.status != 200 or urllib.parse.urlsplit(response.url).netloc != urllib.parse.urlsplit(ORIGIN).netloc:
            raise AssertionError('Search index did not resolve on the authorized origin')
        data = response.read(2 * 1024 * 1024 + 1)
    if len(data) > 2 * 1024 * 1024:
        raise AssertionError('Search index exceeds size cap')
    return json.loads(data)

def audit(routes):
    from playwright.sync_api import sync_playwright
    if not AXE.is_file():
        raise AssertionError('Pinned axe-core 4.10.3 missing')
    results = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        for width, height in VIEWPORTS:
            context = browser.new_context(viewport={'width': width, 'height': height})
            page = context.new_page()
            for route in routes:
                response = page.goto(ORIGIN + route, wait_until='load', timeout=45000)
                if not response or response.status != 200 or urllib.parse.urlsplit(response.url).netloc != urllib.parse.urlsplit(ORIGIN).netloc:
                    raise AssertionError('Published route unavailable: ' + route)
                page.wait_for_function("getComputedStyle(document.querySelector('.brand img')).width === '44px'", timeout=15000)
                if page.locator('meta[name="robots"]').get_attribute('content') != 'noindex,nofollow':
                    raise AssertionError('Noindex missing: ' + route)
                page.add_script_tag(path=str(AXE))
                result = page.evaluate('''async tags => {
                  const result = await window.axe.run(document, {
                    runOnly: {type:'tag', values:tags},
                    resultTypes: ['violations','incomplete']
                  });
                  return {
                    violations: result.violations.map(v => ({
                      id:v.id, impact:v.impact, description:v.help, count:v.nodes.length,
                      nodes:v.nodes.slice(0,12).map(n => ({
                        target:n.target, summary:(n.failureSummary||'').slice(0,450)
                      }))
                    })),
                    incomplete: result.incomplete.map(v => ({
                      id:v.id, impact:v.impact, count:v.nodes.length
                    }))
                  };
                }''', TAGS)
                results.append({'route': route, 'viewport': f'{width}x{height}', **result})
                print(f"Automated WCAG {len(results)}/{len(routes)*len(VIEWPORTS)}: {route} {width}px, violations={len(result['violations'])}", flush=True)
            context.close()
        browser.close()
    return results

def self_test():
    index = ([{'url': f'/2023/10/21/test-{i}/', 'type': 'article'} for i in range(13)] +
             [{'url': '/about/', 'type': 'page'}, {'url': '/cultural-significance/', 'type': 'page'}])
    assert len(validate_routes(index)) == 16
    for bad in (index[:-1], index + [index[0]],
                index[:-1] + [{'url': '/private/', 'type': 'page'}]):
        try:
            validate_routes(bad)
        except AssertionError:
            pass
        else:
            raise AssertionError('Unauthorized route fixture accepted')
    scans = [{'route':'/', 'viewport':'375x812', 'violations':[
                {'id':'color-contrast','impact':'serious'},
                {'id':'region','impact':'moderate'}]},
             {'route':'/about/', 'viewport':'1280x800', 'violations':[]}]
    s = summarize(scans)
    assert (s['scans'], s['violations'], s['serious_or_critical']) == (2, 2, 1)
    assert s['by_rule'] == {'color-contrast':1, 'region':1}
    print('WCAG scanner self-tests PASS: route closure and severity gate')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('--output', default='wcag-accessibility-audit.json')
    parser.add_argument('--gate', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    routes = validate_routes(fetch_index())
    scans = audit(routes)
    summary = summarize(scans)
    Path(args.output).write_text(json.dumps({
        'scope':'homepage + 13 published articles + 2 published pages',
        'method':'axe-core 4.10.3, WCAG 2.0/2.1/2.2 A/AA tags, Chromium desktop/mobile',
        'limitations':'Automated HTML scan only; PDF tags/OCR, manual screen-reader testing and visual WordPress parity remain unverified',
        'summary':summary, 'results':scans
    }, ensure_ascii=False, indent=2) + '\n')
    print('WCAG audit summary: ' + json.dumps({k:v for k,v in summary.items() if k != 'failing'}))
    if args.gate and summary['serious_or_critical']:
        raise SystemExit('Serious or critical accessibility violations; inspect audit artifact')

if __name__ == '__main__':
    main()
