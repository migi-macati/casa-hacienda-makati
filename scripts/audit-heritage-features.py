#!/usr/bin/env python3
"""Conservative read-only deployed heritage feature inventory; not feature acceptance."""
import argparse
import json
import re
import urllib.parse
import urllib.request
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

ORIGIN = "https://casa-hacienda-makati.vercel.app"
FEATURES = ("timeline", "people", "places", "events", "sources", "maps", "then-and-now")

class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links, self.markers = [], set()
        self.h1, self.cards, self.noindex = 0, 0, False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "meta" and a.get("name", "").lower() == "robots":
            self.noindex |= "noindex" in [v.strip() for v in a.get("content", "").lower().split(",")]
        if tag == "h1":
            self.h1 += 1
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        if tag == "article" and "card" in (a.get("class") or "").split():
            self.cards += 1
        if tag in ("main", "section", "article") and a.get("data-heritage-feature") in FEATURES:
            self.markers.add(a["data-heritage-feature"])

def routes(index):
    if not isinstance(index, list) or len(index) != 15:
        raise ValueError("Expected 15 published documents")
    types = Counter(x.get("type") for x in index if isinstance(x, dict))
    if types != {"article": 13, "page": 2}:
        raise ValueError("Published types differ from 13 posts and 2 pages")
    paths = [x["url"] for x in index]
    if len(set(paths)) != 15 or {x["url"] for x in index if x["type"] == "page"} != {"/about/", "/cultural-significance/"}:
        raise ValueError("Missing, duplicate or unexpected public page")
    if any(not isinstance(p, str) or not re.fullmatch(r"/[a-z0-9/-]+/", p) or "//" in p or ".." in p for p in paths):
        raise ValueError("Unsafe published route")
    return ["/"] + paths

def fetch(path):
    req = urllib.request.Request(ORIGIN + path, headers={"User-Agent": "CasaHaciendaReadOnlyHeritageQA/1.0"})
    with urllib.request.urlopen(req, timeout=35) as response:
        if response.status != 200 or urllib.parse.urlsplit(response.url).netloc != urllib.parse.urlsplit(ORIGIN).netloc:
            raise AssertionError("HTTP failure or cross-origin redirect: " + path)
        body = response.read(2000001)
        if len(body) > 2000000:
            raise AssertionError("Oversized response: " + path)
        return body.decode("utf-8", "replace")

def inspect(path, html):
    p = Page()
    p.feed(html)
    if not p.noindex or p.h1 != 1:
        raise AssertionError("Missing noindex or unique H1: " + path)
    feature_links, external = set(), 0
    for raw in p.links:
        u = urllib.parse.urlsplit(urllib.parse.urljoin(ORIGIN + path, raw))
        if u.scheme not in ("http", "https"):
            continue
        if u.netloc != urllib.parse.urlsplit(ORIGIN).netloc:
            external += 1
        for feature in FEATURES:
            if u.netloc == urllib.parse.urlsplit(ORIGIN).netloc and u.path == "/" + feature + "/":
                feature_links.add(feature)
    return {"route": path, "noindex": p.noindex, "h1Count": p.h1,
            "linkCount": len(p.links), "externalLinksNotVerifiedAsSources": external,
            "articleCards": p.cards, "markedSections": sorted(p.markers),
            "featureRouteLinks": sorted(feature_links)}

def summarize(rows):
    published = {r["route"] for r in rows}
    features = {}
    for name in FEATURES:
        features[name] = {
            "dedicatedPublishedRoute": "/" + name + "/" in published,
            "markedSections": [r["route"] for r in rows if name in r["markedSections"]],
            "linksToDedicatedRoute": [r["route"] for r in rows if name in r["featureRouteLinks"]],
            "independentlyVerifiedDeployed": False,
            "acceptance": "PENDING_INDEPENDENT_FEATURE_QA"
        }
    return {"publicRoutesAudited": len(rows), "homepageArticleCards": next(r["articleCards"] for r in rows if r["route"] == "/"),
            "features": features, "limitations": "Article prose, links and candidate markers are not verified standalone features."}

def output(folder, rows, summary):
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "heritage-coverage.json").write_text(json.dumps({"summary": summary, "routes": rows}, indent=2) + "\n")
    lines = ["# Deployed heritage feature inventory", "",
             "Read-only audit of homepage, 13 published articles and two pages. This is NOT historical or functional acceptance.",
             "Published prose may discuss people, places, maps or events without providing a dedicated accessible feature.", "",
             "Audited public routes: " + str(summary["publicRoutesAudited"]) + "/16",
             "Homepage published article cards: " + str(summary["homepageArticleCards"]),
             "All routes: HTTP 200, unique H1, noindex (fail-closed).", "",
             "| Feature | Dedicated public route | Marked sections | Independently verified |",
             "|---|---|---:|---|"]
    for name, feature in summary["features"].items():
        lines.append("| " + name + " | " + ("yes" if feature["dedicatedPublishedRoute"] else "no") +
                     " | " + str(len(feature["markedSections"])) + " | PENDING |")
    lines += ["", "A route or marker is a discovery signal, never proof of accurate history, sources, interaction or accessibility.",
              "No WordPress, media, rights, private drafts, noindex or launch changes are authorized.",
              "Next: research, build and independently verify each evidence-grounded heritage feature."]
    (folder / "heritage-coverage.md").write_text("\n".join(lines) + "\n")

def self_test():
    docs = [{"type": "article", "url": "/2023/08/12/published-" + str(i) + "/"} for i in range(13)] + [
        {"type": "page", "url": "/about/"}, {"type": "page", "url": "/cultural-significance/"}]
    assert len(routes(docs)) == 16
    for bad in (docs[:-1], docs + [docs[0]], docs[:-1] + [{"type": "page", "url": "//evil.test/"}]):
        try: routes(bad)
        except ValueError: pass
        else: raise AssertionError("Unsafe route index passed")
    html = '<meta name="robots" content="noindex,nofollow"><h1>Public</h1><section data-heritage-feature="timeline"><a href="/timeline/">Timeline</a><a href="https://example.org">External</a></section><article class="card"></article>'
    p = inspect("/", html)
    assert p["markedSections"] == ["timeline"] and p["featureRouteLinks"] == ["timeline"]
    assert p["articleCards"] == 1 and p["externalLinksNotVerifiedAsSources"] == 1
    try: inspect("/", html.replace("noindex,nofollow", "index,follow"))
    except AssertionError: pass
    else: raise AssertionError("Indexable page passed")
    s = summarize([p] + [dict(p, route=r) for r in routes(docs)[1:]])
    assert not s["features"]["timeline"]["dedicatedPublishedRoute"]
    assert not s["features"]["timeline"]["independentlyVerifiedDeployed"]
    print("Heritage inventory self-tests PASS: public closure, privacy, markers, no false acceptance")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--output-dir", default="heritage-evidence")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    rows = [inspect(route, fetch(route)) for route in routes(json.loads(fetch("/search-index.json")))]
    summary = summarize(rows)
    if len(rows) != 16:
        raise AssertionError("Incomplete public-route audit")
    output(Path(args.output_dir), rows, summary)
    print("Deployed heritage inventory PASS: " + json.dumps({"routes": len(rows),
        "homepageCards": summary["homepageArticleCards"],
        "dedicatedPublishedRoutes": [name for name, f in summary["features"].items() if f["dedicatedPublishedRoute"]]}))

if __name__ == "__main__":
    main()
