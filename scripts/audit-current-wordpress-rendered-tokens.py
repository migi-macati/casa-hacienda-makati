#!/usr/bin/env python3
"""Read-only computed-style comparison: current WordPress vs migrated public routes."""
import argparse
import copy
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

ORIGINAL = "https://casahaciendamakati.wordpress.com"
MIGRATED = "https://casa-hacienda-makati.vercel.app"
ROUTES = ("/about/", "/cultural-significance/",
          "/2023/08/12/cultural-significance-no-1/",
          "/2023/10/21/history-of-barrio-olimpia-makati-rizal/")
WIDTHS = (320, 375, 1280)
CSS_HOSTS = {"casahaciendamakati.wordpress.com", "s0.wp.com", "s1.wp.com",
             "s2.wp.com", "c0.wp.com", "c1.wp.com", "c2.wp.com",
             "fonts.wp.com", "fonts.googleapis.com", "fonts.gstatic.com"}
EXPECTED = {
    "/about/": {"spacing70": 1},
    "/cultural-significance/": {"spacing60": 1, "frames": 12},
    "/2023/08/12/cultural-significance-no-1/": {"separators": 5, "galleryImages": 3},
    "/2023/10/21/history-of-barrio-olimpia-makati-rizal/": {
        "separators": 3, "galleryImages": 7, "spacing70": 29},
}
SNAPSHOT = r"""() => {
  const root = document.querySelector('article.content') ||
    document.querySelector('.entry-content') ||
    document.querySelector('.wp-block-post-content') ||
    document.querySelector('article') || document.querySelector('main') || document.body;
  const box = e => e.getBoundingClientRect();
  const sample = e => {
    const s = getComputedStyle(e), b = box(e);
    return {width: +b.width.toFixed(2), display: s.display,
      fontFamily: s.fontFamily, fontSize: s.fontSize, color: s.color,
      lineHeight: s.lineHeight, paddingBottom: s.paddingBottom,
      marginTop: s.marginTop, borderBottomWidth: s.borderBottomWidth,
      borderBottomStyle: s.borderBottomStyle, gridColumns: s.gridTemplateColumns};
  };
  const selectors = {
    separators: '.wp-block-separator',
    frames: 'p.has-border-color.has-base-border-color',
    primary: '.has-primary-color.has-text-color',
    foreground: '.has-foreground-color.has-text-color',
    black: '.has-black-color.has-text-color',
    spacing60: '[style*="spacing--60"]',
    spacing70: '[style*="spacing--70"]',
    galleries: '.wp-block-gallery.has-nested-images'
  };
  const counts = {}, first = {};
  for (const [key, selector] of Object.entries(selectors)) {
    const elements = [...root.querySelectorAll(selector)];
    counts[key] = elements.length;
    first[key] = elements.length ? sample(elements[0]) : null;
  }
  const h1 = [...document.querySelectorAll('h1')].find(e=>box(e).width>0);
  const paragraph = [...root.querySelectorAll('p')].find(e=>
    box(e).width>0 && (e.textContent||'').trim().length>80);
  const styles = getComputedStyle(document.documentElement);
  return {
    title: h1?.textContent.replace(/\s+/g,' ').trim() || '',
    titleStyle: h1 ? sample(h1) : null,
    paragraph: paragraph ? sample(paragraph) : null,
    contentWidth: +box(root).width.toFixed(2),
    tokens: {'60': styles.getPropertyValue('--wp--preset--spacing--60').trim(),
             '70': styles.getPropertyValue('--wp--preset--spacing--70').trim()},
    counts, first,
    galleryImages: [...root.querySelectorAll(selectors.galleries)]
      .reduce((n,e)=>n+e.querySelectorAll(':scope > figure.wp-block-image').length,0),
    stylesheets: document.styleSheets.length,
    overflow: document.documentElement.scrollWidth > innerWidth+2,
    scrollWidth: document.documentElement.scrollWidth,
    viewportWidth: innerWidth,
    robots: document.querySelector('meta[name="robots"]')?.content || null
  };
}"""

def validate(route, width, which, record):
    assert route in ROUTES and width in WIDTHS and which in ("original", "migrated")
    expected_host = urlsplit(ORIGINAL if which == "original" else MIGRATED).hostname
    assert record["status"] == 200 and record["host"] == expected_host
    assert record["title"] and record["titleStyle"] and record["stylesheets"] >= 1
    assert record["contentWidth"] > 0
    if which == "migrated":
        assert not record["overflow"], (route, width, record.get("scrollWidth"), record.get("viewportWidth"))
        assert record["robots"] == "noindex,nofollow"
        assert re.fullmatch(r"noindex\s*,\s*nofollow", record["header"] or "", re.I)
        for key, value in EXPECTED[route].items():
            got = record["galleryImages"] if key == "galleryImages" else record["counts"][key]
            assert got == value, (route, key, got, value)

def assert_current_original_parity(route, width, pair):
    """Require measured, source-scoped Gutenberg token parity, not template/theme parity."""
    assert route in ROUTES and width in WIDTHS
    a, b = pair["original"], pair["migrated"]
    def close_px(first_key, property_name, expected, label):
        left = a["first"][first_key]
        right = b["first"][first_key]
        assert left is not None and right is not None, (route, width, label, "missing element")
        x = float(str(left[property_name]).removesuffix("px"))
        y = float(str(right[property_name]).removesuffix("px"))
        tolerance = 0.1 if label == "separator border" else 0.8
        assert abs(x - expected) <= tolerance and abs(y - expected) <= tolerance and abs(x - y) <= tolerance, (
            route, width, label, x, y, expected)
    if route in ("/2023/08/12/cultural-significance-no-1/",
                 "/2023/10/21/history-of-barrio-olimpia-makati-rizal/"):
        expected_count = EXPECTED[route]["separators"]
        assert a["counts"]["separators"] == b["counts"]["separators"] == expected_count, (
            route, width, "separator source inventory")
        close_px("separators", "width", min(168, width * .13), "separator width")
        close_px("separators", "borderBottomWidth", 1, "separator border")
        assert a["first"]["separators"]["borderBottomStyle"] == "solid"
        assert b["first"]["separators"]["borderBottomStyle"] == "solid"
    if route == "/cultural-significance/":
        assert a["counts"]["spacing60"] == b["counts"]["spacing60"] == 1, (
            route, width, "heading spacing-60 source inventory")
        close_px("spacing60", "paddingBottom", min(168, width * .13), "heading spacing-60")
    if route == "/about/":
        assert a["counts"]["spacing70"] == b["counts"]["spacing70"] == 1, (
            route, width, "About spacing-70 source inventory")
        close_px("spacing70", "marginTop", 54.08, "About spacing-70")


def self_test():
    assert len(ROUTES) == 4 and len(set(ROUTES)) == 4 and len(WIDTHS) == 3
    assert not any(r.endswith("cultural-significance-no-12/") for r in ROUTES)
    assert not any("facebook" in host for host in CSS_HOSTS)
    base = {"status":200,"host":urlsplit(MIGRATED).hostname,"title":"Title",
            "titleStyle":{"fontFamily":"serif","fontSize":"24px"},
            "stylesheets":1,"contentWidth":620,"overflow":False,
            "robots":"noindex,nofollow","header":"noindex,nofollow",
            "counts":{"spacing70":1},"galleryImages":0}
    validate("/about/", 375, "migrated", base)
    mutations = [
      ("status",lambda x:x.update(status=404)),
      ("host",lambda x:x.update(host="invalid.test")),
      ("title",lambda x:x.update(title="")),
      ("stylesheet",lambda x:x.update(stylesheets=0)),
      ("width",lambda x:x.update(contentWidth=0)),
      ("overflow",lambda x:x.update(overflow=True)),
      ("robots",lambda x:x.update(robots="index,follow")),
      ("header",lambda x:x.update(header=None)),
      ("spacing",lambda x:x["counts"].update(spacing70=0))]
    for name, mutate in mutations:
        bad=copy.deepcopy(base); mutate(bad)
        try: validate("/about/", 375, "migrated", bad)
        except (AssertionError, KeyError, TypeError): pass
        else: raise AssertionError("Failed to reject mutation: "+name)
    # Independent parity fixtures reject regressions in either origin or in the migration.
    separator = {"counts": {"separators": 5}, "first": {"separators": {
        "width": 48.75, "borderBottomWidth": "1px", "borderBottomStyle": "solid"}}}
    pair = {"original": copy.deepcopy(separator), "migrated": copy.deepcopy(separator)}
    route = "/2023/08/12/cultural-significance-no-1/"
    assert_current_original_parity(route, 375, pair)
    parity_mutations = [
      ("migration-width", lambda p: p["migrated"]["first"]["separators"].update(width=100)),
      ("original-width", lambda p: p["original"]["first"]["separators"].update(width=100)),
      ("migration-border", lambda p: p["migrated"]["first"]["separators"].update(borderBottomWidth="2px")),
      ("original-border", lambda p: p["original"]["first"]["separators"].update(borderBottomStyle="none")),
      ("missing-original-separator", lambda p: p["original"]["counts"].update(separators=4)),
      ("missing-migrated-separator", lambda p: p["migrated"]["first"].update(separators=None)),
    ]
    for name, mutate in parity_mutations:
        bad = copy.deepcopy(pair); mutate(bad)
        try: assert_current_original_parity(route, 375, bad)
        except (AssertionError, KeyError, TypeError, ValueError): pass
        else: raise AssertionError("Failed to reject parity mutation: " + name)
    for path, token, property_name, value, expected in (
        ("/cultural-significance/", "spacing60", "paddingBottom", "48.75px", 48.75),
        ("/about/", "spacing70", "marginTop", "54.08px", 54.08)):
        record = {"counts": {token: 1}, "first": {token: {property_name: value}}}
        matched = {"original": copy.deepcopy(record), "migrated": copy.deepcopy(record)}
        assert_current_original_parity(path, 375, matched)
        for which in ("original", "migrated"):
            bad = copy.deepcopy(matched)
            bad[which]["first"][token][property_name] = "36px"
            try: assert_current_original_parity(path, 375, bad)
            except (AssertionError, KeyError, TypeError, ValueError): pass
            else: raise AssertionError("Failed to reject " + which + " " + token + " regression")
    print("Rendered-token self-test: 9 base + 10 parity fail-closed mutations PASS")

def capture():
    from playwright.sync_api import sync_playwright
    rows=[];blocked=0
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        try:
            for width in WIDTHS:
                context=browser.new_context(viewport={"width":width,"height":850},
                    java_script_enabled=False,reduced_motion="reduce",service_workers="block")
                def restrict(route):
                    nonlocal blocked
                    request=route.request;u=urlsplit(request.url)
                    host_ok=u.hostname in CSS_HOSTS or u.hostname==urlsplit(MIGRATED).hostname
                    doc_ok=request.resource_type!="document" or u.hostname in (
                        urlsplit(ORIGINAL).hostname,urlsplit(MIGRATED).hostname)
                    if u.scheme=="https" and host_ok and doc_ok and request.resource_type in (
                        "document","stylesheet","font"):
                        route.continue_()
                    else:
                        blocked+=1;route.abort()
                context.route("**/*",restrict)
                page=context.new_page()
                for route in ROUTES:
                    pair={}
                    for which,origin in (("original",ORIGINAL),("migrated",MIGRATED)):
                        response=page.goto(origin+route,wait_until="domcontentloaded",timeout=45000)
                        assert response is not None
                        page.wait_for_selector("h1",timeout=15000)
                        page.wait_for_load_state("load",timeout=15000)
                        page.evaluate("() => Promise.race([document.fonts.ready,new Promise(r=>setTimeout(r,3000))])")
                        page.wait_for_timeout(250)
                        data=page.evaluate(SNAPSHOT)
                        data.update(status=response.status,host=urlsplit(page.url).hostname,
                                    header=response.headers.get("x-robots-tag"))
                        print("CSS diagnostic",which,route,width,"scroll",data.get("scrollWidth"),"viewport",data.get("viewportWidth"),flush=True)
                        validate(route,width,which,data)
                        pair[which]=data
                    assert_current_original_parity(route, width, pair)
                    rows.append({"route":route,"width":width,**pair})
                context.close()
        finally: browser.close()
    assert len(rows)==12
    return rows,blocked

def output(rows,blocked,directory):
    directory.mkdir(parents=True,exist_ok=True)
    (directory/"current-wordpress-rendered-tokens.json").write_text(json.dumps({
        "scope":"4 published routes x 3 widths x 2 read-only origins",
        "status":"source_scoped_current_gutenberg_token_parity_not_exact_theme_parity",
        "blockedNonCSSFontDocumentRequests":blocked,"pairs":rows},indent=2)+"\n")
    lines=["# Current WordPress rendered CSS versus migrated site","",
      "24 restricted read-only Chromium visits, no images, scripts, social requests or screenshots.",
      "Current active theme does not establish historic authoring theme. Missing source selectors are inconclusive.",
      "Strict parity passed for 5+3 source-defined separators, Cultural Significance spacing-60 and About spacing-70 at 320/375/1280px. Other styling differences remain unaccepted.","",
      "| Route | Width | Original spacing 60 | Migrated spacing 60 | Original separator width/border | Migrated separator width/border |",
      "|---|---:|---|---|---|---|"]
    for row in rows:
        a=row["original"];b=row["migrated"]
        def separator(x):
            e=x["first"]["separators"]
            return "not observed" if e is None else str(e["width"])+"px / "+e["borderBottomWidth"]+" "+e["borderBottomStyle"]
        lines.append("| "+row["route"]+" | "+str(row["width"])+" | "+
                     (a["tokens"]["60"] or "undefined")+" | "+(b["tokens"]["60"] or "undefined")+
                     " | "+separator(a)+" | "+separator(b)+" |")
    lines+=["","Inspect JSON counts and computed styles before proposing any CSS change.",
      "This does not certify theme, gallery interaction, media rights, manual screen-reader, PDF or field CWV parity."]
    (directory/"current-wordpress-rendered-tokens.md").write_text("\n".join(lines)+"\n")
    print("Rendered-token parity PASS: 12 paired route/width checks, 24 HTTP 200 visits; blocked requests:",blocked)

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--self-test",action="store_true")
    parser.add_argument("--output-dir",default="visual-lab-evidence")
    args=parser.parse_args()
    if args.self_test: self_test()
    else:
        rows,blocked=capture()
        output(rows,blocked,Path(args.output_dir))
