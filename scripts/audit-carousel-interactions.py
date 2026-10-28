#!/usr/bin/env python3
"""Read-only WordPress carousel interaction observations and migrated no-JS link acceptance.

Only public homepages; never submit forms, follow carousel links, or publish media.
This diagnostic does not certify WCAG, rights, or WordPress visual parity.
"""
import argparse
import json
import re
import urllib.parse
from pathlib import Path

ORIGINAL = "https://casahaciendamakati.wordpress.com"
DEPLOYED = "https://casa-hacienda-makati.vercel.app"
SELECTOR = ".wp-block-newspack-blocks-carousel"
VIEWPORTS = ((1280, 800), (375, 812))
MOTIONS = ("reduce", "no-preference")
SNAPSHOT_JS = r"""() => {
 const root = document.querySelector('.wp-block-newspack-blocks-carousel');
 if (!root) return {present:false};
 const shown = e => {const r=e.getBoundingClientRect(),s=getComputedStyle(e);
   return r.width>0 && r.height>0 && s.visibility!=='hidden' && s.display!=='none';};
 const kind = e => {
   const t=[e.getAttribute('aria-label'),e.getAttribute('title'),e.innerText,
      String(e.className||'')].filter(Boolean).join(' ').toLowerCase();
   if (/pause|stop/.test(t)) return 'pause';
   if (/resume|play/.test(t)) return 'play';
   if (/previous|prev/.test(t)) return 'previous';
   if (/next/.test(t)) return 'next';
   if (/slide|pagination|bullet/.test(t)) return 'pagination';
   return 'unlabeled';
 };
 const buttons=[...root.querySelectorAll('button,[role="button"]')];
 const slides=[...root.querySelectorAll('.swiper-slide')];
 const wrapper=root.querySelector('.swiper-wrapper');
 return {
   present:true, images:root.querySelectorAll('img').length,
   autoplayClass:root.classList.contains('wp-block-newspack-blocks-carousel__autoplay-playing'),
   reducedMotion:matchMedia('(prefers-reduced-motion: reduce)').matches,
   activeSlideIndices:slides.flatMap((e,i)=>e.classList.contains('swiper-slide-active')?[i]:[]),
   wrapperTransform:wrapper?getComputedStyle(wrapper).transform:null,
   visibleLinks:[...root.querySelectorAll('a[href]')].filter(shown).length,
   controls:buttons.map((e,i)=>({index:i,kind:kind(e),visible:shown(e),
     disabled:e.disabled||e.getAttribute('aria-disabled')==='true'})),
   documentOverflow:document.documentElement.scrollWidth>innerWidth+3
 };
}"""

def check_inventory(raw):
    assert raw.get("observedSlides") == 12
    assert raw.get("verifiedMedia") == 12 and raw.get("uniqueVerifiedMedia") == 12
    assert raw.get("publishedDestinations") == 12
    slides = raw["slides"]
    assert len(slides) == 12
    paths = [s["publishedDestination"] for s in slides]
    assert len(set(paths)) == 12
    assert all(re.fullmatch(r"/[a-z0-9/-]+/", p) and "//" not in p and ".." not in p
               for p in paths)
    assert all(s["mediaMatch"] == "verified_manifest" and
               s["destinationMatch"] == "published" for s in slides)
    return set(paths)

def changed(before, after):
    return (before.get("activeSlideIndices") != after.get("activeSlideIndices")
            or before.get("wrapperTransform") != after.get("wrapperTransform"))

def first_control(snapshot, kind):
    return next((c["index"] for c in snapshot.get("controls", [])
                 if c["kind"] == kind and c["visible"] and not c["disabled"]), None)

def read_only(context):
    # Even third-party analytics and tracking requests cannot write to WordPress.
    context.route("**/*", lambda route: route.continue_()
                  if route.request.method in ("GET", "HEAD") else route.abort())

def same_origin(url, origin):
    u, base = urllib.parse.urlsplit(url), urllib.parse.urlsplit(origin)
    return u.scheme == base.scheme and u.netloc == base.netloc

def visible_destinations(page, origin):
    hrefs = page.eval_on_selector_all("a[href]", "(nodes)=>nodes.filter(e=>{const r=e.getBoundingClientRect();return r.width>0&&r.height>0}).map(e=>e.href)")
    paths = set()
    for href in hrefs:
        if same_origin(href, origin):
            u = urllib.parse.urlsplit(href)
            if not u.query:
                paths.add(u.path)
    return paths

def sample(original_targets):
    from playwright.sync_api import sync_playwright
    observations, fallbacks = [], []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        for width, height in VIEWPORTS:
            for motion in MOTIONS:
                context = browser.new_context(viewport={"width":width,"height":height},
                    locale="en-US",reduced_motion=motion)
                read_only(context)
                page = context.new_page()
                response = page.goto(ORIGINAL+"/",wait_until="domcontentloaded",timeout=45000)
                if not response or response.status != 200 or not same_origin(page.url, ORIGINAL):
                    raise AssertionError("Original public homepage unavailable or redirected")
                page.wait_for_function("document.querySelectorAll('.wp-block-newspack-blocks-carousel img').length===12",timeout=20000)
                root = page.locator(SELECTOR)
                root.scroll_into_view_if_needed(timeout=10000)
                page.wait_for_timeout(800)
                before = page.evaluate(SNAPSHOT_JS)
                if not before["present"] or before["images"] != 12 or before["reducedMotion"] != (motion=="reduce"):
                    raise AssertionError("Original carousel DOM or reduced-motion observation changed")
                page.wait_for_timeout(6000)
                after_wait = page.evaluate(SNAPSHOT_JS)
                pause_index = first_control(after_wait,"pause")
                pause = {"available":pause_index is not None,"activated":False,"playingAfter":None}
                if pause_index is not None:
                    try:
                        root.locator('button,[role="button"]').nth(pause_index).click(timeout=4000)
                        page.wait_for_timeout(350)
                        pause.update(activated=True,playingAfter=page.evaluate(SNAPSHOT_JS)["autoplayClass"])
                    except Exception:
                        pause["error"] = "control could not be activated"
                next_index = first_control(page.evaluate(SNAPSHOT_JS),"next")
                nxt = {"available":next_index is not None,"clicked":False,
                       "clickChanged":None,"enterChanged":None,"enterFocused":None}
                if next_index is not None:
                    control = root.locator('button,[role="button"]').nth(next_index)
                    try:
                        b = page.evaluate(SNAPSHOT_JS)
                        control.click(timeout=4000)
                        page.wait_for_timeout(650)
                        a = page.evaluate(SNAPSHOT_JS)
                        nxt.update(clicked=True,clickChanged=changed(b,a))
                        control.focus(timeout=4000)
                        nxt["enterFocused"] = control.evaluate("(e)=>document.activeElement===e")
                        b = page.evaluate(SNAPSHOT_JS)
                        page.keyboard.press("Enter")
                        page.wait_for_timeout(650)
                        nxt["enterChanged"] = changed(b,page.evaluate(SNAPSHOT_JS))
                    except Exception:
                        nxt["error"] = "control could not be activated"
                observations.append({"viewport":width,"motion":motion,
                    "before":before,"afterWait":after_wait,
                    "observedMovementDuringSixSeconds":changed(before,after_wait),
                    "pause":pause,"next":nxt})
                context.close()
                print(f"Original carousel behavior {width}px {motion}: controls sampled",flush=True)
            for origin in (ORIGINAL,DEPLOYED):
                context=browser.new_context(viewport={"width":width,"height":height},
                    locale="en-US",java_script_enabled=False)
                read_only(context)
                page=context.new_page()
                response=page.goto(origin+"/",wait_until="domcontentloaded",timeout=45000)
                if not response or response.status != 200 or not same_origin(page.url,origin):
                    raise AssertionError("Public no-JS homepage unavailable or redirected")
                if origin==DEPLOYED and page.locator('meta[name="robots"]').get_attribute("content")!="noindex,nofollow":
                    raise AssertionError("Migrated noindex lost without JavaScript")
                paths=visible_destinations(page,origin)
                covered=original_targets & paths
                if origin==DEPLOYED and covered!=original_targets:
                    raise AssertionError(f"Migrated no-JS homepage lost {len(original_targets-covered)} published carousel destinations")
                fallbacks.append({"origin":"original" if origin==ORIGINAL else "deployed",
                    "viewport":width,"publishedDestinationsVisible":len(covered),
                    "expectedDestinations":len(original_targets),
                    "carouselDomPresent":page.locator(SELECTOR).count()>0,
                    "noindexVerified":origin==DEPLOYED})
                context.close()
                print(f"No-JS public homepage {origin} {width}px: {len(covered)}/12 visible destinations",flush=True)
        browser.close()
    return observations,fallbacks

def write_report(out, observations, fallbacks):
    data={"scope":"Original public homepage carousel, two viewports and motion settings; migrated/original no-JS homepage",
          "limitations":"Observed browser behavior only; 6-second sample cannot prove no autoplay. No screenshots, media redistribution, rights clearance, manual screen-reader or pixel parity.",
          "observations":observations,"noJavaScript":fallbacks}
    (out/"carousel-behavior.json").write_text(json.dumps(data,indent=2)+"\n")
    lines=["# Read-only original carousel interaction and no-JavaScript navigation audit","",
      "Original WordPress and migrated public homepages only. No forms, login, writes, screenshots or image redistribution.",
      "**This is diagnostic, not carousel visual parity, WCAG certification or media rights clearance.**",
      "Six seconds without slide movement cannot establish that autoplay is absent; hidden controls and focus behavior need manual review.","",
      "| Viewport | Motion preference | Autoplay class initially | Movement in 6s | Pause activated | Next click changed | Enter changed |",
      "|---|---|---|---|---|---|---|"]
    for x in observations:
        p=x["pause"];n=x["next"]
        lines.append(f"| {x['viewport']}px | {x['motion']} | {x['before']['autoplayClass']} | {x['observedMovementDuringSixSeconds']} | {p['activated']} | {n['clickChanged']} | {n['enterChanged']} |")
    lines += ["","## No-JavaScript public navigation","",
       "| Origin | Viewport | Original 12 article destinations visible |",
       "|---|---|---:|"]
    for x in fallbacks:
        lines.append(f"| {x['origin']} | {x['viewport']}px | {x['publishedDestinationsVisible']}/12 |")
    lines += ["","Only the migrated no-JavaScript 12/12 destination coverage and noindex are acceptance gates; WordPress behavior is recorded without forcing a copy of inaccessible or motion-heavy interaction.",
      "Media manifest matches do not grant reproduction rights. The global image carousel remains rights-gated.",
      "Preserve four private drafts, 82 original media, and noindex. No public launch authorization."]
    (out/"carousel-behavior.md").write_text("\n".join(lines)+"\n")

def self_test():
    raw={"observedSlides":12,"verifiedMedia":12,"uniqueVerifiedMedia":12,
         "publishedDestinations":12,"slides":[{"publishedDestination":f"/2023/10/21/cs-{i}/",
         "mediaMatch":"verified_manifest","destinationMatch":"published"} for i in range(12)]}
    assert len(check_inventory(raw))==12
    try: check_inventory({**raw,"slides":[*raw["slides"][:-1],raw["slides"][0]]})
    except AssertionError: pass
    else: raise AssertionError("Duplicate carousel destination passed")
    try: check_inventory({**raw,"slides":[*raw["slides"][:-1],{**raw["slides"][0],"publishedDestination":"/private/../"}]})
    except AssertionError: pass
    else: raise AssertionError("Unsafe carousel destination passed")
    assert changed({"activeSlideIndices":[0],"wrapperTransform":"matrix(1)"},{"activeSlideIndices":[1],"wrapperTransform":"matrix(1)"})
    assert not changed({"activeSlideIndices":[0],"wrapperTransform":"none"},{"activeSlideIndices":[0],"wrapperTransform":"none"})
    assert first_control({"controls":[{"index":2,"kind":"next","visible":True,"disabled":False}]},"next")==2
    assert first_control({"controls":[{"index":2,"kind":"next","visible":False,"disabled":False}]},"next") is None
    assert same_origin(ORIGINAL+"/",ORIGINAL) and not same_origin("https://evil.example/",ORIGINAL)
    print("Carousel interaction audit self-tests PASS: verified public routes, controls, movement, origins")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--output-dir",default="visual-lab-evidence")
    args=p.parse_args()
    if args.self_test: self_test(); return
    out=Path(args.output_dir)
    out.mkdir(parents=True,exist_ok=True)
    inventory=json.loads((out/"carousel-source-inventory.json").read_text())
    targets=check_inventory(inventory)
    observations,fallbacks=sample(targets)
    if len(observations)!=4 or len(fallbacks)!=4:
        raise AssertionError("Incomplete desktop/mobile and motion/no-JS observations")
    write_report(out,observations,fallbacks)
    print("Carousel interaction and migrated no-JS navigation audit PASS",flush=True)

if __name__=="__main__":
    main()
