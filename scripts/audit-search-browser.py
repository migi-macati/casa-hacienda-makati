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
    browser.close()
print('Chromium search privacy PASS: 15/15 documents, desktop and mobile computed CSS; synthetic CSS-hidden case excluded.')
