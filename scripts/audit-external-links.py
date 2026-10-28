#!/usr/bin/env python3
"""Read-only audit of PUBLIC deployed links, slashless redirects and HTTP timing.

External status is a time-limited observation, not proof of citation invalidity,
ownership, licensing, historical accuracy or browser performance.
"""
import argparse
from collections import Counter
import concurrent.futures
from html.parser import HTMLParser
import html
import ipaddress
import json
from pathlib import Path
import re
import time
from urllib import error, parse, request

ORIGIN = "https://casa-hacienda-makati.vercel.app"
USER_AGENT = "CasaHaciendaPublicLinkAudit/1.0"
MAX_BYTES = 3 * 1024 * 1024

class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

OPENER = request.build_opener(NoRedirect)

class Anchors(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hrefs = []
    def handle_starttag(self, tag, attrs):
        if tag.lower() == "a":
            attributes = dict(attrs)
            if "href" in attributes:
                self.hrefs.append(attributes["href"])

def safe_public_url(raw):
    try:
        parts = parse.urlsplit(raw)
        if parts.scheme.lower() not in ("http", "https") or not parts.hostname:
            return None
        host = parts.hostname.lower().rstrip(".")
        if host == "localhost" or host.endswith((".local", ".internal", ".localhost")):
            return None
        try:
            if not ipaddress.ip_address(host).is_global:
                return None
        except ValueError:
            pass
        if parts.username or parts.password or parts.port not in (None, 80, 443):
            return None
        return parse.urlunsplit((parts.scheme.lower(), parts.netloc.lower(),
                                parts.path or "/", parts.query, ""))
    except (ValueError, TypeError):
        return None

def fetch(url, method="GET", timeout=9):
    started = time.monotonic()
    try:
        req = request.Request(url, method=method, headers={"User-Agent": USER_AGENT})
        with OPENER.open(req, timeout=timeout) as response:
            data = response.read(MAX_BYTES + 1) if method == "GET" else b""
            if len(data) > MAX_BYTES:
                raise ValueError("Response exceeded 3 MiB")
            return {"status": response.status, "location": response.headers.get("Location", ""),
                    "body": data, "elapsed_ms": round((time.monotonic()-started)*1000)}
    except error.HTTPError as exc:
        return {"status": exc.code, "location": exc.headers.get("Location", ""),
                "body": b"", "elapsed_ms": round((time.monotonic()-started)*1000)}
    except (error.URLError, TimeoutError, OSError, ValueError) as exc:
        return {"status": None, "location": "", "body": b"",
                "elapsed_ms": round((time.monotonic()-started)*1000),
                "error": type(exc).__name__}

def classify(status):
    if status is None: return "network_unverified"
    if 200 <= status < 300: return "reachable"
    if 300 <= status < 400: return "redirect_unverified"
    if status in (404, 410): return "missing_observed"
    if status in (401, 403, 429, 451): return "restricted_unverified"
    return "other_unverified"

def extract_external(markup):
    parser = Anchors()
    parser.feed(markup)
    external, invalid = [], []
    for raw in parser.hrefs:
        if raw is None:
            invalid.append("missing href value")
            continue
        raw = html.unescape(raw.strip())
        if raw.startswith("//"):
            raw = "https:" + raw
        if not raw or raw.startswith(("/", "#", "?")) or raw.lower().startswith(("mailto:", "tel:")):
            continue
        normalized = safe_public_url(raw)
        if normalized is None:
            invalid.append("unsafe or malformed scheme")
        elif parse.urlsplit(normalized).hostname != parse.urlsplit(ORIGIN).hostname:
            external.append(normalized)
    return external, invalid

def check_external(url):
    result = fetch(url, "HEAD")
    if result["status"] in (405, 501):
        result = fetch(url, "GET")
    return {"url": url, "status": result["status"], "category": classify(result["status"]),
            "location": result["location"], "elapsed_ms": result["elapsed_ms"],
            **({"error": result["error"]} if "error" in result else {})}

def audit():
    index = fetch(ORIGIN + "/search-index.json")
    if index["status"] != 200:
        raise RuntimeError("Published index unavailable")
    docs = json.loads(index["body"])
    if (len(docs) != 15 or len({d["url"] for d in docs}) != 15 or
        sum(d["type"] == "article" for d in docs) != 13 or
        sum(d["type"] == "page" for d in docs) != 2):
        raise RuntimeError("Published-only index closure failed")
    routes = ["/", *sorted(d["url"] for d in docs)]
    unique, occurrences, invalid, pages, redirects = set(), 0, [], [], []
    for route in routes:
        if not re.fullmatch(r"/[a-zA-Z0-9/_-]*", route) or ".." in route:
            raise RuntimeError("Unsafe published route")
        res = fetch(ORIGIN + route)
        if res["status"] != 200:
            raise RuntimeError(f"Published route {route} HTTP {res['status']}")
        markup = res["body"].decode("utf-8", errors="replace")
        if not re.search(r'<meta\s+name=["\x27]robots["\x27]\s+content=["\x27]noindex,nofollow', markup, re.I):
            raise RuntimeError("Published route missing noindex: " + route)
        links, bad = extract_external(markup)
        occurrences += len(links)
        unique.update(links)
        invalid.extend({"route": route, "reason": item} for item in bad)
        pages.append({"route": route, "html_bytes": len(res["body"]),
                      "observed_ms": res["elapsed_ms"], "external_links": len(links)})
        if route != "/":
            slashless = route.rstrip("/")
            redirect = fetch(ORIGIN + slashless, "HEAD")
            location = redirect["location"]
            resolved = parse.urljoin(ORIGIN + slashless, location) if location else ""
            redirects.append({"route": slashless, "status": redirect["status"],
                              "location": location,
                              "canonical_redirect": redirect["status"] in (301,302,307,308)
                              and resolved == ORIGIN + route})
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        checks = sorted(executor.map(check_external, sorted(unique)), key=lambda x: x["url"])
    return {"schema_version": 1, "origin": ORIGIN, "published_routes": 15,
            "pages": pages, "external_occurrences": occurrences,
            "external_unique": len(unique),
            "external_hosts": len({parse.urlsplit(u).hostname for u in unique}),
            "external_checks": checks, "invalid_links": invalid,
            "redirect_checks": redirects,
            "counts": dict(Counter(x["category"] for x in checks))}

def markdown(result):
    lines = ["# Casa Hacienda public-link, redirect and HTTP observations", "",
             "Read-only observations only. Restricted, redirected and timed-out links are not proven broken.",
             "An observed 404/410 requires editorial confirmation before changing any citation.", "",
             f"Published routes: {result['published_routes']}; external link occurrences: {result['external_occurrences']}; "
             f"unique URLs: {result['external_unique']}; hosts: {result['external_hosts']}.", "",
             "## External HTTP categories", ""]
    lines.extend(f"- {name}: {count}" for name, count in sorted(result["counts"].items()))
    lines.extend(["", "## Observed 404/410 requiring editorial review", ""])
    missing = [item for item in result["external_checks"] if item["category"] == "missing_observed"]
    lines.extend([f"- HTTP {item['status']}: {item['url']}" for item in missing]
                 or ["No 404/410 observed in this run."])
    lines.extend(["", "## Slashless route redirects", ""])
    good = sum(item["canonical_redirect"] for item in result["redirect_checks"])
    lines.append(f"{good}/{len(result['redirect_checks'])} redirect to exact slash-terminated canonical.")
    for item in result["redirect_checks"]:
        if not item["canonical_redirect"]:
            lines.append(f"- {item['route']}: HTTP {item['status']}, Location {item['location'] or '(none)'}")
    lines.extend(["", "## HTML transfer timing (not Core Web Vitals)", ""])
    lines.extend(f"- {item['route']}: {item['html_bytes']} bytes, {item['observed_ms']} ms"
                 for item in result["pages"])
    lines.extend(["", "## Limits", "",
                  "Third-party servers can block HEAD or vary responses by geography and time. "
                  "This does not verify historical claims, media rights, browser performance, "
                  "original WordPress visual parity or accessible PDF text."])
    return "\n".join(lines) + "\n"

def self_test():
    assert safe_public_url("https://example.org/a#x") == "https://example.org/a"
    assert safe_public_url("http://127.0.0.1/") is None
    assert safe_public_url("http://localhost/") is None
    assert safe_public_url("https://example.org:1234/") is None
    assert safe_public_url("javascript:alert(1)") is None
    links, bad = extract_external('<a href="https://example.org/a#x">ok</a>'
                                  '<a href="/about/">local</a><a href="mailto:a@b">mail</a>'
                                  '<a href="javascript:alert(1)">bad</a>')
    assert links == ["https://example.org/a"] and len(bad) == 1
    assert classify(404) == "missing_observed"
    assert classify(403) == "restricted_unverified"
    assert classify(301) == "redirect_unverified"
    assert classify(None) == "network_unverified"
    print("Public-link audit: 10 synthetic assertions PASS")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--output", default="external-link-audit.json")
    p.add_argument("--markdown", default="external-link-audit.md")
    args = p.parse_args()
    if args.self_test:
        self_test()
    else:
        result = audit()
        Path(args.output).write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
        report = markdown(result)
        Path(args.markdown).write_text(report)
        print(report)
        if result["invalid_links"]:
            raise SystemExit("Unsafe public links found; see JSON artifact")
