#!/usr/bin/env python3
"""Read-only deployed HTTP, browser and media-byte acceptance; no private routes."""
import concurrent.futures
import hashlib
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ORIGIN = "https://casa-hacienda-makati.vercel.app"

class SameOrigin(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if urllib.parse.urlsplit(newurl).netloc != urllib.parse.urlsplit(ORIGIN).netloc:
            raise AssertionError("Cross-origin redirect rejected")
        return super().redirect_request(req, fp, code, msg, headers, newurl)

OPENER = urllib.request.build_opener(SameOrigin)

def get_bytes(path, cap=45 * 1024 * 1024):
    if not path.startswith("/") or path.startswith("//") or ".." in path.split("/"):
        raise AssertionError("Unsafe relative path")
    req = urllib.request.Request(ORIGIN + path, headers={"User-Agent": "CasaHaciendaReadOnlyQA/1.0"})
    with OPENER.open(req, timeout=40) as res:
        if res.status != 200 or urllib.parse.urlsplit(res.url).netloc != urllib.parse.urlsplit(ORIGIN).netloc:
            raise AssertionError("Unexpected response: " + path)
        data = res.read(cap + 1)
        if len(data) > cap:
            raise AssertionError("Response exceeds size limit: " + path)
        return data

def get_json(path):
    return json.loads(get_bytes(path, 2 * 1024 * 1024))

def norm(s):
    return re.sub(r"\s+", " ", s).strip()

def validate_media(manifest, inventory):
    expected = [a["path"] for a in manifest["assets"]]
    actual = [a["path"] for a in inventory["assets"]]
    if (inventory.get("schema_version") != 1 or len(expected) != 82 or
        len(actual) != 82 or len(set(expected)) != 82 or
        len(set(actual)) != 82 or set(expected) != set(actual)):
        raise AssertionError("Production media inventory closure mismatch")
    for a in inventory["assets"]:
        if (not re.fullmatch(r"/media/[a-zA-Z0-9_./-]+", a["path"]) or
            ".." in a["path"].split("/") or
            not isinstance(a.get("bytes"), int) or a["bytes"] <= 0 or
            not re.fullmatch(r"[0-9a-f]{64}", a.get("sha256", ""))):
            raise AssertionError("Invalid media entry")
    return inventory["assets"]

def check_media(a):
    data = get_bytes(a["path"])
    if len(data) != a["bytes"] or hashlib.sha256(data).hexdigest() != a["sha256"]:
        raise AssertionError("Served-media SHA256 mismatch: " + a["path"])
    if a["path"].endswith(".webp") and not (data[:4] == b"RIFF" and data[8:12] == b"WEBP"):
        raise AssertionError("Invalid served WebP: " + a["path"])
    if a["path"].endswith(".pdf") and not data.startswith(b"%PDF"):
        raise AssertionError("Invalid served PDF: " + a["path"])
    return a["path"]

VISIBLE_TEXT = r"""() => {
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
       visible = false; break;
     }
     if (element === article) break;
   }
   if (visible) parts.push(node.textContent);
 }
 return parts.join(' ').replace(/\s+/g, ' ').trim();
}"""

def validate_index(index, provenance):
    if (not isinstance(index, list) or len(index) != 15 or
        len({a["url"] for a in index}) != 15 or
        sum(a["type"] == "article" for a in index) != 13 or
        sum(a["type"] == "page" for a in index) != 2):
        raise AssertionError("Published route inventory mismatch")
    routes = [a["url"] for a in index]
    if any(not re.fullmatch(r"/[a-z0-9/-]+/", x) or ".." in x for x in routes):
        raise AssertionError("Unexpected published route")
    raw = json.dumps(index, ensure_ascii=False, separators=(",", ":")).encode()
    if (provenance.get("routes") != routes or
        provenance.get("indexSha256") != hashlib.sha256(raw).hexdigest()):
        raise AssertionError("Published search provenance mismatch")
    return index

def check_browser(index):
    from playwright.sync_api import sync_playwright
    errors = []
    visits = 0
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        for width, height in ((1280, 800), (375, 812)):
            context = browser.new_context(viewport={"width": width, "height": height})
            page = context.new_page()
            page.on("pageerror", lambda error: errors.append(str(error)[:160]))
            for entry in index:
                url = ORIGIN + entry["url"]
                response = page.goto(url, wait_until="domcontentloaded", timeout=45000)
                if not response or response.status != 200:
                    raise AssertionError("Published page unavailable: " + entry["url"])
                if page.locator('meta[name="robots"]').get_attribute("content") != "noindex,nofollow":
                    raise AssertionError("Noindex missing: " + entry["url"])
                if page.locator('link[rel="canonical"]').get_attribute("href") != url:
                    raise AssertionError("Canonical mismatch: " + entry["url"])
                if page.locator("h1").count() != 1 or norm(page.locator("h1").inner_text()) != entry["title"]:
                    raise AssertionError("Heading mismatch: " + entry["url"])
                if norm(page.evaluate(VISIBLE_TEXT)) != norm(entry["text"]):
                    raise AssertionError("Browser-visible text mismatch: " + entry["url"])
                if page.locator('img:not([alt]), img[alt=""]').count():
                    raise AssertionError("Image alternative missing: " + entry["url"])
                if page.evaluate("document.documentElement.scrollWidth > innerWidth + 3"):
                    offenders = page.evaluate("""() => [...document.querySelectorAll('body *')].map(e => ({tag:e.tagName,cls:typeof e.className==='string'?e.className.slice(0,90):'',right:Math.round(e.getBoundingClientRect().right),left:Math.round(e.getBoundingClientRect().left),width:Math.round(e.getBoundingClientRect().width)})).filter(x=>x.right>innerWidth+3||x.left< -3).slice(0,12)""")
                    raise AssertionError("Horizontal overflow: " + entry["url"] + " width=" + str(width) + " scrollWidth=" + str(page.evaluate("document.documentElement.scrollWidth")) + " offenders=" + json.dumps(offenders))
                if entry["type"] == "article" and page.locator('a[href*="casahaciendamakati.wordpress.com"]').count() == 0:
                    raise AssertionError("Original discussion bridge missing: " + entry["url"])
                visits += 1
            response = page.goto(ORIGIN + "/", wait_until="domcontentloaded", timeout=45000)
            if not response or response.status != 200:
                raise AssertionError("Homepage unavailable")
            if page.locator('meta[name="robots"]').get_attribute("content") != "noindex,nofollow":
                raise AssertionError("Homepage noindex missing")
            if page.evaluate("document.documentElement.scrollWidth > innerWidth + 3"):
                raise AssertionError("Homepage horizontal overflow at width " + str(width))
            page.locator("#find").fill("orphanage")
            page.wait_for_function('document.querySelector("#search-status").textContent.includes("result")', timeout=15000)
            if page.locator(".card:visible").count() < 1:
                raise AssertionError("Homepage search failed")
            page.locator("#find").fill("zzzzunlikelynonmatch123")
            page.wait_for_function('document.querySelector("#search-status").textContent.startsWith("0 results")', timeout=15000)
            if not page.locator("#nothing").is_visible():
                raise AssertionError("Homepage no-results state missing")
            context.close()
        browser.close()
    if errors:
        raise AssertionError("Browser JavaScript exceptions: " + "; ".join(errors[:5]))
    return visits

def self_test():
    manifest = {"assets": [{"path": f"/media/2023/07/sample{i}.webp"} for i in range(82)]}
    inventory = {"schema_version": 1, "assets": [
        {"path": a["path"], "bytes": 12, "sha256": "a" * 64} for a in manifest["assets"]]}
    assert len(validate_media(manifest, inventory)) == 82
    inventory["assets"][0]["sha256"] = "invalid"
    try:
        validate_media(manifest, inventory)
    except AssertionError:
        pass
    else:
        raise AssertionError("Invalid checksum accepted")
    assert norm(" a \n b ") == "a b"
    print("Production acceptance self-tests PASS: 3 assertions")

def main():
    if sys.argv[1:] == ["--self-test"]:
        self_test(); return
    if len(sys.argv) != 1:
        raise SystemExit("Usage: python scripts/audit-production.py [--self-test]")
    index = validate_index(get_json("/search-index.json"), get_json("/search-provenance.json"))
    manifest = json.loads(Path("media-manifest.json").read_text())
    assets = validate_media(manifest, get_json("/media-integrity.json"))
    if "Disallow: /" not in get_bytes("/robots.txt", 20000).decode():
        raise AssertionError("Robots exclusion missing")
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        verified = list(pool.map(check_media, assets))
    print(f"Independent deployed media SHA256 PASS: {len(verified)}/82")
    visits = check_browser(index)
    print(f"Independent deployed Chromium PASS: {visits}/30 published page visits, desktop/mobile, search, noindex, visible text, console")
    print("WordPress historical fidelity, rights, PDFs, native comments, security/performance remain separate acceptance items.")

if __name__ == "__main__":
    main()
