#!/usr/bin/env python3
"""Read-only production print-mode acceptance for the 15 locked published documents.

This never requests WordPress, Facebook, or other external hosts; never generates
PDFs, image derivatives, or changes source. It checks live CSS, not PDF/UA or
original Newspack print-theme pixel parity.
"""
import copy
import hashlib
import json
import os
import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
ORIGIN = "https://casa-hacienda-makati.vercel.app"
LOCK = json.loads((ROOT / "ops/published-search-sources.json").read_text())
SNAPSHOT = r"""() => {
  const article = document.querySelector('article.content');
  if (!article) throw Error('Published article missing');
  const style = e => getComputedStyle(e);
  const figures = [...article.querySelectorAll('img')];
  const gallery = [...article.querySelectorAll('.wp-block-gallery.has-nested-images')];
  const columns = [...article.querySelectorAll('.wp-block-columns, .wp-block-column')];
  const tableFigure = article.querySelector('.wp-block-table.is-style-stripes');
  const table = tableFigure?.querySelector('table');
  const original = document.querySelector('.original a');
  return {
    robots:document.querySelector('meta[name="robots"]')?.content,
    articles:document.querySelectorAll('article.content').length,
    stylesheets:document.styleSheets.length,
    text:article.innerText,
    links:article.querySelectorAll('a').length,
    images:figures.length,
    originalHref:original?.href,
    originalVisible:original ? style(original).display !== 'none' : false,
    headerHidden:style(document.querySelector('.siteheader')).display === 'none',
    sidebarHidden:style(document.querySelector('.sidebar')).display === 'none',
    footerHidden:style(document.querySelector('footer')).display === 'none',
    layoutBlock:style(document.querySelector('.layout')).display === 'block',
    articleVisible:style(article).display !== 'none',
    bodyWhite:style(document.body).backgroundColor === 'rgb(255, 255, 255)',
    spacersHidden:[...article.querySelectorAll('.wp-block-spacer')].every(e=>style(e).display === 'none'),
    columnsStacked:columns.every(e=>style(e).display === 'block'),
    imagesFit:figures.every(e=>e.getBoundingClientRect().width <= article.getBoundingClientRect().width + 2),
    galleryColumns:gallery.map(e=>style(e).gridTemplateColumns.split(' ').filter(Boolean).length),
    table:tableFigure && table ? {
      overflow:style(tableFigure).overflowX,
      minWidth:style(table).minWidth,
      tableWidth:table.getBoundingClientRect().width,
      figureWidth:tableFigure.getBoundingClientRect().width
    } : null
  };
}"""

def inventory():
    docs = LOCK["documents"]
    assert len(docs) == 15
    assert sum(d["type"] == "article" for d in docs) == 13
    assert sum(d["type"] == "page" for d in docs) == 2
    found = {}
    for doc in docs:
        raw = (ROOT / "public" / doc["file"]).read_bytes()
        digest = hashlib.sha1(b"blob " + str(len(raw)).encode() + bytes([0]) + raw).hexdigest()
        assert digest == doc["gitBlob"], "Source lock mismatch: " + doc["file"]
        html = raw.decode("utf-8")
        assert '<meta name="robots" content="noindex,nofollow">' in html
        original = re.search(r'<div class="original">Original publication: <a href="([^"]+)"', html)
        assert original, "Missing original publication attribution: " + doc["file"]
        assert original.group(1).startswith("https://casahaciendamakati.wordpress.com/")
        route = "/" + doc["file"].removesuffix("index.html")
        found[route] = {
            "original": original.group(1),
            "galleries": html.count("wp-block-gallery has-nested-images"),
            "table": "wp-block-table is-style-stripes" in html,
        }
    assert sum(x["galleries"] for x in found.values()) == 2
    assert sum(x["table"] for x in found.values()) == 1
    return found

def validate(s, source, route, width, allow_previous=False):
    assert width in (375, 1280), "Unreviewed viewport"
    assert s.get("status") == 200, (route, "HTTP status")
    assert re.fullmatch(r"noindex\s*,\s*nofollow", s.get("header") or "", re.I), (route, "noindex HTTP")
    assert s.get("robots") == "noindex,nofollow", (route, "noindex meta")
    assert s.get("articles") == 1 and s.get("stylesheets", 0) >= 1, (route, "published HTML/CSS")
    assert s.get("originalHref") == source["original"] and s.get("originalVisible") is True, (route, "source attribution")
    assert s.get("screenHeaderVisible") is True, (route, "screen styles")
    assert s.get("textPreserved") is True and s.get("linksPreserved") is True and s.get("imagesPreserved") is True, (route, "source content")
    for key in ("headerHidden", "sidebarHidden", "footerHidden", "layoutBlock",
                "articleVisible", "bodyWhite", "spacersHidden", "columnsStacked", "imagesFit"):
        assert s.get(key) is True, (route, key)
    expected_gallery = [2] * source["galleries"]
    if allow_previous and route == "/2023/10/21/history-of-barrio-olimpia-makati-rizal/":
        assert s.get("galleryColumns") in ([2], [4]), (route, "controlled premerge gallery baseline")
    else:
        assert s.get("galleryColumns") == expected_gallery, (route, "gallery print layout")
    if source["table"]:
        t = s.get("table")
        assert t is not None and t["overflow"] == "visible" and t["minWidth"] == "0px", (route, "evidence table print layout")
        assert t["tableWidth"] <= t["figureWidth"] + 2, (route, "evidence table clipping")
    else:
        assert s.get("table") is None, (route, "unexpected table")
    return True

def self_test(sources):
    route = "/2024/10/28/cultural-significance-no-12/"
    source = sources[route]
    sample = {
        "status":200, "header":"noindex,nofollow", "robots":"noindex,nofollow",
        "articles":1, "stylesheets":1, "originalHref":source["original"],
        "originalVisible":True, "screenHeaderVisible":True,
        "textPreserved":True, "linksPreserved":True, "imagesPreserved":True,
        "headerHidden":True, "sidebarHidden":True, "footerHidden":True,
        "layoutBlock":True, "articleVisible":True, "bodyWhite":True,
        "spacersHidden":True, "columnsStacked":True, "imagesFit":True,
        "galleryColumns":[], "table":{"overflow":"visible", "minWidth":"0px",
                                     "tableWidth":320, "figureWidth":320},
    }
    validate(sample, source, route, 375)
    mutations = [
        ("http", lambda x:x.update(status=404)),
        ("header", lambda x:x.update(header="index,follow")),
        ("meta", lambda x:x.update(robots="index,follow")),
        ("source", lambda x:x.update(originalHref="https://example.org/")),
        ("stylesheet", lambda x:x.update(stylesheets=0)),
        ("screen", lambda x:x.update(screenHeaderVisible=False)),
        ("text", lambda x:x.update(textPreserved=False)),
        ("links", lambda x:x.update(linksPreserved=False)),
        ("images", lambda x:x.update(imagesPreserved=False)),
        ("print-header", lambda x:x.update(headerHidden=False)),
        ("print-sidebar", lambda x:x.update(sidebarHidden=False)),
        ("print-body", lambda x:x.update(bodyWhite=False)),
        ("spacers", lambda x:x.update(spacersHidden=False)),
        ("columns", lambda x:x.update(columnsStacked=False)),
        ("scan-width", lambda x:x.update(imagesFit=False)),
        ("table-overflow", lambda x:x["table"].update(overflow="auto")),
        ("table-clipping", lambda x:x["table"].update(tableWidth=600)),
    ]
    for name, change in mutations:
        candidate = copy.deepcopy(sample)
        change(candidate)
        try:
            validate(candidate, source, route, 375)
        except (AssertionError, KeyError, TypeError):
            continue
        raise AssertionError("Print QA negative fixture passed unexpectedly: " + name)
    gallery_route = "/2023/10/21/history-of-barrio-olimpia-makati-rizal/"
    gallery_source = sources[gallery_route]
    gallery_case = copy.deepcopy(sample)
    gallery_case["originalHref"] = gallery_source["original"]
    gallery_case["table"] = None
    gallery_case["galleryColumns"] = [4]
    try:
        validate(gallery_case, gallery_source, gallery_route, 375)
    except AssertionError:
        pass
    else:
        raise AssertionError("Strict postmerge print gallery gate accepted four columns")
    validate(gallery_case, gallery_source, gallery_route, 375, allow_previous=True)
    gallery_case["galleryColumns"] = [3]
    try:
        validate(gallery_case, gallery_source, gallery_route, 375, allow_previous=True)
    except AssertionError:
        pass
    else:
        raise AssertionError("Premerge gallery gate accepted an unknown layout")
    print("Live print QA: 15 pinned sources, 17 negative fixtures, and strict/premerge gallery transition PASS")

def live(sources):
    # Only PRs based on the exact pre-fix main SHA may observe the old 4-column
    # Olympia gallery. After merge (or any subsequent PR), the gate is strict.
    allow_previous = (os.environ.get("GITHUB_EVENT_NAME") == "pull_request"
                      and os.environ.get("CHM_PR_BASE_SHA") == "04e649a2551684537dc1e2b567c4248d8c22180d")
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        evidence = []
        blocked = []
        try:
            context = browser.new_context(service_workers="block", reduced_motion="reduce")
            def project_only(route):
                u = urlsplit(route.request.url)
                if (u.scheme, u.netloc) == ("https", urlsplit(ORIGIN).netloc):
                    route.continue_()
                else:
                    blocked.append(u.netloc)
                    route.abort()
            context.route("**/*", project_only)
            page = context.new_page()
            for route, source in sources.items():
                for width in (375, 1280):
                    page.set_viewport_size({"width":width, "height":812})
                    page.emulate_media(media="screen")
                    response = page.goto(ORIGIN + route, wait_until="domcontentloaded", timeout=45000)
                    assert response is not None, "Missing production response: " + route
                    page.wait_for_function("document.styleSheets.length >= 1", timeout=20000)
                    screen = page.evaluate(SNAPSHOT)
                    page.emulate_media(media="print")
                    printed = page.evaluate(SNAPSHOT)
                    printed.update({
                        "status":response.status,
                        "header":response.headers.get("x-robots-tag"),
                        "screenHeaderVisible":not screen["headerHidden"],
                        "textPreserved":screen["text"] == printed["text"],
                        "linksPreserved":screen["links"] == printed["links"],
                        "imagesPreserved":screen["images"] == printed["images"],
                    })
                    validate(printed, source, route, width, allow_previous=allow_previous)
                    evidence.append({
                        "route":route, "width":width, "status":response.status,
                        "noindex":True, "sourceTextAndLinksPreserved":True,
                        "galleryColumns":printed["galleryColumns"],
                        "tableVisible":bool(printed["table"]),
                    })
            context.close()
        finally:
            browser.close()
    target = ROOT / "artifacts" / "live-print-browser.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps({
        "origin":ORIGIN, "checks":len(evidence), "thirdPartyRequestsBlocked":len(blocked),
        "pdfsGenerated":0, "premergeBaselineAllowed":allow_previous, "results":evidence
    }, indent=2) + chr(10))
    print("Live production print QA:", len(evidence), "Chromium checks PASS; third-party requests blocked:", len(blocked))

if __name__ == "__main__":
    sources = inventory()
    self_test(sources)
    if os.environ.get("CHM_SELF_TEST") != "1":
        live(sources)
