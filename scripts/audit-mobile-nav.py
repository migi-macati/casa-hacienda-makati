#!/usr/bin/env python3
"""Generated-site Chromium acceptance for native mobile navigation, JavaScript disabled."""
import functools,http.server,json,re,threading
from pathlib import Path
from playwright.sync_api import sync_playwright
index=json.loads(Path('public/search-index.json').read_text())
assert len(index)==15 and sum(x.get('type')=='article' for x in index)==13 and sum(x.get('type')=='page' for x in index)==2
paths=[x['url'] for x in index]
assert len(set(paths))==15 and all(re.fullmatch(r'/[a-z0-9/-]+/',p) for p in paths)
paths=['/']+paths+['/404.html']
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(Path('public').resolve())))
threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True)
  for width in (1280,375):
   context=browser.new_context(viewport={'width':width,'height':812},java_script_enabled=False)
   page=context.new_page()
   for route in paths:
    response=page.goto(f'http://127.0.0.1:{server.server_port}{route}',wait_until='load',timeout=45000)
    assert response and response.status==200,route
    assert page.locator('meta[name="robots"]').get_attribute('content')=='noindex,nofollow',route
    desktop=page.locator('nav.desktop-nav')
    mobile=page.locator('details.mobile-nav')
    assert desktop.count()==mobile.count()==1,route
    assert desktop.locator('a').count()==mobile.locator('nav a').count()==5,route
    if width==1280:
     assert desktop.is_visible() and not mobile.is_visible(),route
    else:
     assert not desktop.is_visible() and mobile.locator('summary').is_visible() and not mobile.locator('nav').is_visible(),route
     mobile.locator('summary').click()
     assert mobile.locator('nav').is_visible() and all(a.is_visible() for a in mobile.locator('nav a').all()),route
     mobile.locator('summary').click()
     assert not mobile.locator('nav').is_visible(),route
    print(f'Native nav PASS {width}px {route}',flush=True)
   context.close()
  browser.close()
finally:
 server.shutdown()
 server.server_close()
print('Native mobile nav browser PASS: 17 routes × 2 viewports, no JavaScript.')
