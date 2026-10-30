#!/usr/bin/env python3
"""Mandatory Chromium computed-CSS search privacy gate, after complete build."""
import json
import os
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path('public').resolve()
INDEX = json.loads((ROOT / 'search-index.json').read_text())
assert len(INDEX) == 15 and len({x['url'] for x in INDEX}) == 15

VISIBLE_TEXT = r'''() => {
  const article = document.querySelector('article.content');
  if (!article || document.querySelectorAll('article').length !== 1)
    throw new Error('Missing or ambiguous published article');
  const walker = document.createTreeWalker(article, NodeFilter.SHOW_TEXT);
  const parts = [];
  let node;
  while ((node = walker.nextNode())) {
    if (!node.textContent.trim()) continue;
    let visible = true;
    for (let element = node.parentElement; element; element = element.parentElement) {
      const style = getComputedStyle(element);
      if (element.hidden || element.inert || element.getAttribute('aria-hidden') === 'true' ||
          style.display === 'none' || style.visibility === 'hidden' ||
          style.visibility === 'collapse' || style.contentVisibility === 'hidden' ||
          Number(style.opacity) === 0 || /inset\(50%/.test(style.clipPath) ||
          /rect\(0px, 0px, 0px, 0px\)/.test(style.clip) ||
          (style.overflow === 'hidden' && element.getBoundingClientRect().width === 0 &&
           element.getBoundingClientRect().height === 0)) {
        visible = false;
        break;
      }
      if (element === article) break;
    }
    if (visible) parts.push(node.textContent);
  }
  return parts.join(' ').replace(/\s+/g, ' ').trim();
}'''

def norm(s):
    return re.sub(r'\s+', ' ', s).strip()

css = (ROOT / 'assets/style.css').read_text()
assert '@import' not in css.lower(), 'External CSS imports are not allowed in privacy gate'
with sync_playwright() as pw:
    launch_args = {'headless': True}
    if os.environ.get('CHROMIUM_PATH'):
        launch_args['executable_path'] = os.environ['CHROMIUM_PATH']
    browser = pw.chromium.launch(**launch_args)
    page = browser.new_page()
    page.set_content('<style>.css-hidden{display:none}</style><article class="content">'
                     '<p>Public sample</p><p class="css-hidden">SECRET_CSS_ONLY</p></article>')
    assert 'SECRET_CSS_ONLY' in page.locator('article').text_content()
    assert 'SECRET_CSS_ONLY' not in page.evaluate(VISIBLE_TEXT)
    for item in INDEX:
        html_file = ROOT / item['url'].lstrip('/') / 'index.html'
        html = html_file.read_text()
        stylesheet = '<link rel="stylesheet" href="/assets/style.css">'
        assert html.count(stylesheet) == 1, f"Unreviewed stylesheet references: {item['url']}"
        html = html.replace(stylesheet, '<style>' + css + '</style>')
        for viewport in [(1280, 800), (375, 812)]:
            page.set_viewport_size({'width': viewport[0], 'height': viewport[1]})
            page.set_content(html, wait_until='domcontentloaded')
            visible = norm(page.evaluate(VISIBLE_TEXT))
            indexed = norm(item['text'])
            if indexed != visible:
                first = next((i for i,(a,b) in enumerate(zip(indexed,visible)) if a!=b),
                             min(len(indexed),len(visible)))
                raise AssertionError(f"Computed CSS visibility mismatch {item['url']} at {viewport} offset {first}; "
                                     f"index={indexed[max(0,first-35):first+55]!r} "
                                     f"browser={visible[max(0,first-35):first+55]!r}")

    # Generated-homepage search interactions: actual Chromium DOM and pinned public index.
    # This read-only local server never accesses private drafts or the original WordPress.
    import functools
    import http.server
    import threading
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *_args):
            pass

    server = http.server.ThreadingHTTPServer(
        ("127.0.0.1", 0),
        functools.partial(QuietHandler, directory=str(ROOT)),
    )
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    try:
        with page.expect_response(lambda r: r.url.endswith("/search-index.json") and r.status == 200):
            page.goto(f"http://127.0.0.1:{server.server_port}/", wait_until="domcontentloaded")
        page.wait_for_function(
            "document.querySelector('#search-status')?.textContent === 'Showing 13 articles.'"
        )
        assert page.locator('meta[name="robots"]').get_attribute("content") == "noindex,nofollow"
        article_one = page.locator(".card").filter(has=page.locator('h3 a[href="/2023/08/12/cultural-significance-no-1/"]')).first
        original_excerpt = article_one.locator(".cardbody p").inner_text()
        assert "1769" not in original_excerpt, "Fixture must exercise a deep-text match"
        for width in (1280, 375):
            page.set_viewport_size({"width": width, "height": 812})
            def results(query):
                page.locator("#find").fill(query)
                status = page.locator("#search-status").inner_text()
                assert "temporarily unavailable" not in status, ("Index fallback", query)
                articles = page.locator(".card:visible h3 a").evaluate_all(
                    "(nodes) => nodes.map(n => n.getAttribute('href'))"
                )
                pages = page.locator("#page-results a").evaluate_all(
                    "(nodes) => nodes.map(n => n.getAttribute('href'))"
                )
                return articles, pages
            assert results("Macati") == results("Makati"), ("Historical spelling", width)
            assert sum(map(len, results("Makati"))) > 0, ("Expected Makati matches", width)
            assert results("Haciénda") == results("Hacienda"), ("Accented query", width)
            assert sum(map(len, results("Hacienda"))) > 0, ("Expected Hacienda matches", width)
            assert results("bahay-na-bato") == results("bahay na bato"), ("Punctuation", width)
            assert sum(map(len, results("bahay na bato"))) > 0, ("Expected architecture matches", width)
            results("1769")
            assert article_one.is_visible(), ("Deep article match", width)
            contextual = article_one.locator(".cardbody p").inner_text()
            assert "1769" in contextual and contextual != original_excerpt, ("Contextual public excerpt", width)
            assert article_one.locator(".cardbody p img").count() == 0, ("Excerpt must be text-only", width)
            assert results("unfindableqzxyz") == ([], []), ("Unexpected match", width)
            assert page.locator("#nothing").is_visible(), ("No-results notice", width)
            assert results("—") == ([], []), ("Punctuation-only query", width)
            results("")
            assert page.locator(".card:visible").count() == 13, ("Unfiltered archive", width)
            assert page.locator("#page-results").is_hidden(), ("Empty-query pages", width)
            assert article_one.locator(".cardbody p").inner_text() == original_excerpt, ("Summary restored", width)
        page.route("**/search-index.json", lambda route: route.fulfill(status=503, body="Unavailable"))
        page.reload(wait_until="domcontentloaded")
        page.wait_for_function('document.querySelector("#search-status")?.textContent.includes("temporarily unavailable")')
        page.locator("#find").fill("Casa")
        assert page.locator(".card:visible").count() > 0, "Fallback summaries must remain searchable"
        assert article_one.locator(".cardbody p").inner_text() == original_excerpt, "Fallback must retain original public summary"
        page.unroute("**/search-index.json")
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=5)

    browser.close()
print('Chromium search privacy and UI PASS: 15/15 documents, 30 computed-CSS scans and 2 viewport search interaction suites.')
