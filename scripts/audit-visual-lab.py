#!/usr/bin/env python3
"""Read-only original WordPress/deployed visual-layout and lab-performance baseline.

Homepage + 15 published routes only, on two origins and desktop/mobile.
Screenshots are representative public pages. No forms, logins or write requests.
Not pixel-exact parity, manual accessibility or field Core Web Vitals.
"""
import argparse
import json
import math
import re
import urllib.parse
import urllib.request
from pathlib import Path

ORIGINAL = 'https://casahaciendamakati.wordpress.com'
DEPLOYED = 'https://casa-hacienda-makati.vercel.app'
VIEWPORTS = [(1280, 800), (375, 812)]
CAPTURE = {'/', '/about/', '/2023/08/12/cultural-significance-no-1/',
           '/2024/10/28/cultural-significance-no-12/'}
METRICS_JS = r'''() => {
 const shown = e => e && e.getBoundingClientRect().width > 0 &&
     e.getBoundingClientRect().height > 0 && getComputedStyle(e).visibility !== 'hidden';
 const h1 = [...document.querySelectorAll('h1')].find(shown);
 const main = document.querySelector('main') || document.querySelector('article') || document.body;
 const prose = [...document.querySelectorAll('main p, article p, .entry-content p, .wp-block-post-content p')]
     .find(e => shown(e) && e.innerText.trim().length > 80);
 const box = e => { const b=e.getBoundingClientRect(); return {
   x:Math.round(b.x),y:Math.round(b.y),width:Math.round(b.width),height:Math.round(b.height)}; };
 const s = h1 ? getComputedStyle(h1) : null;
 const imgs = [...main.querySelectorAll('img')].filter(shown);
 const nav = performance.getEntriesByType('navigation')[0];
 const p = window.__chmVisualLab || {};
 return {
   h1:h1 ? h1.innerText.replace(/\s+/g,' ').trim() : '',
   h1Box:h1 ? box(h1) : null,
   h1Font:s ? {family:s.fontFamily,size:s.fontSize,weight:s.fontWeight,lineHeight:s.lineHeight,color:s.color} : null,
   mainBox:box(main),
   firstLongParagraphBox:prose ? box(prose) : null,
   background:getComputedStyle(document.body).backgroundColor,
   stylesheets:[...document.styleSheets].length,
   images:imgs.length,
   brokenVisibleImages:imgs.filter(i=>i.complete && i.naturalWidth===0).length,
   navLabels:[...document.querySelectorAll('header nav a, nav[aria-label] a')]
       .filter(shown).map(e=>e.innerText.replace(/\s+/g,' ').trim()).filter(Boolean).slice(0,12),
   domContentLoadedMs:nav ? Math.round(nav.domContentLoadedEventEnd) : null,
   loadMs:nav && nav.loadEventEnd ? Math.round(nav.loadEventEnd) : null,
   lcpLabMs:Math.round(p.lcp || 0) || null,
   clsLab:Number((p.cls || 0).toFixed(4)),
   documentHeight:document.documentElement.scrollHeight,
   horizontalOverflow:document.documentElement.scrollWidth > innerWidth + 3
 };
}'''
OBSERVER_JS = r'''(() => {
 window.__chmVisualLab = {lcp:0, cls:0};
 try {new PerformanceObserver(l => {for (const e of l.getEntries())
   window.__chmVisualLab.lcp = Math.max(window.__chmVisualLab.lcp, e.startTime);
 }).observe({type:'largest-contentful-paint',buffered:true});} catch(e) {}
 try {new PerformanceObserver(l => {for (const e of l.getEntries())
   if (!e.hadRecentInput) window.__chmVisualLab.cls += e.value;
 }).observe({type:'layout-shift',buffered:true});} catch(e) {}
})()'''

def valid_routes(index):
    if not isinstance(index, list) or len(index) != 15:
        raise AssertionError('Expected exactly 15 published search documents')
    if sum(isinstance(i,dict) and i.get('type') == 'article' for i in index) != 13:
        raise AssertionError('Expected 13 published articles')
    if {i.get('url') for i in index if i.get('type') == 'page'} != {'/about/', '/cultural-significance/'}:
        raise AssertionError('Expected exactly the two published informational pages')
    paths = [i['url'] for i in index]
    if len(set(paths)) != 15 or any(not isinstance(p,str) or not re.fullmatch(r'/[a-z0-9/-]+/',p)
                                    or '//' in p or '..' in p for p in paths):
        raise AssertionError('Invalid/duplicate/unauthorized route')
    return ['/'] + paths

def clean(s):
    return re.sub(r'\s+', ' ', (s or '').replace('\xa0',' ')).strip().casefold()

def percentile(values, q=0.75):
    v=sorted(x for x in values if isinstance(x,(int,float)) and math.isfinite(x))
    if not v: return None
    return round(v[max(0, math.ceil(q*len(v))-1)], 2)

def compare_pair(original, deployed):
    if not original.get('h1') or not deployed.get('h1'):
        raise AssertionError('One or both rendered pages lack a visible H1')
    if clean(original['h1']) != clean(deployed['h1']):
        return {'h1Match':False, 'originalH1':original['h1'], 'deployedH1':deployed['h1']}
    return {'h1Match':True,
            'h1HorizontalShiftPx':deployed['h1Box']['x']-original['h1Box']['x'],
            'h1VerticalShiftPx':deployed['h1Box']['y']-original['h1Box']['y'],
            'firstLongParagraphWidthDifferencePx':(deployed['firstLongParagraphBox']['width']-original['firstLongParagraphBox']['width'])
                if original.get('firstLongParagraphBox') and deployed.get('firstLongParagraphBox') else None,
            'h1FontSizeMatch':original['h1Font']['size']==deployed['h1Font']['size'],
            'h1FontFamilyMatch':original['h1Font']['family']==deployed['h1Font']['family']}

def self_test():
    idx=[{'url':f'/2023/10/21/published-{i}/','type':'article'} for i in range(13)] + [
        {'url':'/about/','type':'page'}, {'url':'/cultural-significance/','type':'page'}]
    assert len(valid_routes(idx))==16
    for bad in [idx[:-1],idx+[idx[0]],idx[:-1]+[{'url':'/private/','type':'page'}],
                idx[:-1]+[{'url':'//example.com/','type':'page'}]]:
        try: valid_routes(bad)
        except AssertionError: pass
        else: raise AssertionError('Bad route fixture passed')
    assert percentile([10,20,30,40])==30
    assert percentile([10,20,30,40],.95)==40
    assert percentile([]) is None
    a={'h1':'A\xa0 Title','h1Box':{'x':10,'y':20},'mainBox':{'width':100},'firstLongParagraphBox':{'width':100},'h1Font':{'size':'24px','family':'serif'}}
    b={'h1':'A Title','h1Box':{'x':15,'y':27},'mainBox':{'width':130},'firstLongParagraphBox':{'width':130},'h1Font':{'size':'24px','family':'sans-serif'}}
    c=compare_pair(a,b)
    assert c['h1Match'] and c['h1HorizontalShiftPx']==5 and c['firstLongParagraphWidthDifferencePx']==30
    assert c['h1FontSizeMatch'] and not c['h1FontFamilyMatch']
    assert not compare_pair(a,{**b,'h1':'Different'})['h1Match']
    print('Visual parity/lab performance self-tests PASS: routes, unsafe paths, percentile, H1/layout')

def fetch_index():
    req=urllib.request.Request(DEPLOYED+'/search-index.json',headers={'User-Agent':'CasaHaciendaReadOnlyVisualQA/1.0'})
    with urllib.request.urlopen(req,timeout=40) as r:
        if r.status!=200 or urllib.parse.urlsplit(r.url).netloc!=urllib.parse.urlsplit(DEPLOYED).netloc:
            raise AssertionError('Published search index did not resolve on production origin')
        raw=r.read(2*1024*1024+1)
    if len(raw)>2*1024*1024: raise AssertionError('Oversized search index')
    return json.loads(raw)

def capture(routes, out):
    from playwright.sync_api import sync_playwright
    rows=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True)
        for width,height in VIEWPORTS:
            context=browser.new_context(viewport={'width':width,'height':height},
                                        device_scale_factor=1,locale='en-US',reduced_motion='reduce')
            context.add_init_script(OBSERVER_JS)
            page=context.new_page()
            for route in routes:
                pair={}
                for key,origin in [('original',ORIGINAL),('deployed',DEPLOYED)]:
                    response=page.goto(origin+route,wait_until='domcontentloaded',timeout=45000)
                    if not response or response.status!=200 or urllib.parse.urlsplit(page.url).netloc!=urllib.parse.urlsplit(origin).netloc:
                        raise AssertionError(f'{key} published route unavailable or redirected cross-origin: {route}')
                    page.wait_for_function("document.readyState !== 'loading' && document.querySelector('h1')",timeout=15000)
                    try: page.evaluate('() => Promise.race([document.fonts.ready, new Promise(r=>setTimeout(r,5000))])')
                    except Exception: pass
                    if key=='deployed':
                        page.wait_for_function("getComputedStyle(document.querySelector('.brand img')).width === '44px'",timeout=15000)
                        if page.locator('meta[name="robots"]').get_attribute('content')!='noindex,nofollow':
                            raise AssertionError('Production noindex missing: '+route)
                    page.wait_for_timeout(700)
                    m=page.evaluate(METRICS_JS)
                    if not m['h1'] or not m['stylesheets']:
                        raise AssertionError(f'{key} route has missing H1 or stylesheets: {route}')
                    m.update({'status':response.status,'finalUrl':page.url})
                    if route in CAPTURE:
                        name=('home' if route=='/' else route.strip('/').replace('/','-'))
                        filename=f'{key}-{width}-{name}.png'
                        page.screenshot(path=str(out/filename),animations='disabled',full_page=False,timeout=30000)
                        m['screenshot']=filename
                    pair[key]=m
                pair['comparison']=compare_pair(pair['original'],pair['deployed'])
                rows.append({'route':route,'viewport':f'{width}x{height}',**pair})
                print(f'Visual baseline {len(rows)}/{len(routes)*len(VIEWPORTS)}: {route} {width}px H1-match={pair["comparison"]["h1Match"]}',flush=True)
            context.close()
        browser.close()
    return rows

def summary(rows):
    return {'routeViewportPairs':len(rows),
            'h1Matches':sum(x['comparison']['h1Match'] for x in rows),
            'originalLoaded':sum(x['original']['status']==200 for x in rows),
            'deployedLoaded':sum(x['deployed']['status']==200 for x in rows),
            'deployedOverflow':sum(x['deployed']['horizontalOverflow'] for x in rows),
            'deployedBrokenVisibleImages':sum(x['deployed']['brokenVisibleImages'] for x in rows),
            'deployedLabLcpP75MsByViewport':{
                vp:percentile([x['deployed']['lcpLabMs'] for x in rows if x['viewport']==vp])
                for vp in sorted(set(x['viewport'] for x in rows))},
            'deployedLabClsP75ByViewport':{
                vp:percentile([x['deployed']['clsLab'] for x in rows if x['viewport']==vp])
                for vp in sorted(set(x['viewport'] for x in rows))}}

def write_markdown(out,rows,stats):
    lines=['# Original WordPress versus deployed visual-layout and lab-performance baseline','',
           'Scope: homepage, 13 published articles, 2 published pages; desktop 1280×800 and mobile 375×812.',
           'Both origins are read-only. Screenshots capture only public published content.','',
           '**Diagnostic baseline, not pixel-exact visual parity or field Core Web Vitals.**',
           'The original WordPress theme and migrated design can differ intentionally. Browser viewport screenshots require manual review.',
           'LCP/CLS are single-run, unthrottled headless Chromium lab observations; no INP, p75 real-user data, or PDF interior accessibility is measured.','',
           '## Results','',
           f"- Matched public route/viewport pairs: {stats['routeViewportPairs']}",
           f"- Original HTTP 200: {stats['originalLoaded']}; deployed HTTP 200: {stats['deployedLoaded']}",
           f"- Normalized visible H1 matches: {stats['h1Matches']}/{stats['routeViewportPairs']}",
           f"- Deployed horizontal overflow observations: {stats['deployedOverflow']}",
           f"- Deployed broken visible image observations: {stats['deployedBrokenVisibleImages']}",
           f"- Deployed lab LCP page-sample p75 by viewport (ms): {stats['deployedLabLcpP75MsByViewport']}",
           f"- Deployed lab CLS page-sample p75 by viewport: {stats['deployedLabClsP75ByViewport']}",
           '', '## Layout comparisons', '',
           '| Route | Viewport | H1 match | H1 x shift | H1 y shift | First long paragraph width difference | WP font → migrated font |',
           '|---|---|---|---:|---:|---:|---|']
    for x in rows:
        c=x['comparison']; a=x['original']; b=x['deployed']
        lines.append(f"| \u0060{x['route']}\u0060 | {x['viewport']} | {'yes' if c['h1Match'] else 'NO'} | {c.get('h1HorizontalShiftPx','n/a')} | {c.get('h1VerticalShiftPx','n/a')} | {c.get('firstLongParagraphWidthDifferencePx','n/a')} | {a['h1Font']['size']} {a['h1Font']['family'].split(',')[0]} → {b['h1Font']['size']} {b['h1Font']['family'].split(',')[0]} |")
    lines += ['', '## Screenshot evidence', '',
              'Representative viewport captures for homepage, About, Cultural Significance No. 1 and No. 12 are stored in this workflow artifact.',
              'Inspect original/deployed pairs visually; do not infer full theme parity from H1/text/box measurements.',
              '', '## Open acceptance', '',
              'Original WordPress theme and carousel equivalence, manual screen-reader review, three untagged PDFs, native comments, rights/attribution/privacy, true field CWV/INP, and independently deployed heritage features remain unverified.',
              'Noindex remains required; this audit does not authorize public launch.']
    (out/'visual-lab-report.md').write_text('\n'.join(lines)+'\n')

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--self-test',action='store_true')
    p.add_argument('--output-dir',default='visual-lab-evidence')
    args=p.parse_args()
    if args.self_test: self_test(); return
    out=Path(args.output_dir);out.mkdir(parents=True,exist_ok=True)
    routes=valid_routes(fetch_index())
    rows=capture(routes,out)
    stats=summary(rows)
    if stats['routeViewportPairs']!=32 or stats['originalLoaded']!=32 or stats['deployedLoaded']!=32:
        raise AssertionError('Incomplete 16-route × 2-viewport public comparison')
    (out/'visual-lab-data.json').write_text(json.dumps({'scope':'16 public routes × 2 viewports × 2 read-only origins',
        'limitations':'Not pixel parity; unthrottled lab LCP/CLS not field CWV or INP; manual screenshot and screen-reader review pending',
        'summary':stats,'pairs':rows},indent=2,ensure_ascii=False)+'\n')
    write_markdown(out,rows,stats)
    print('Visual/layout lab baseline complete: '+json.dumps(stats),flush=True)

if __name__=='__main__':main()
