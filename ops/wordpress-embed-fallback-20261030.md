# WordPress Gutenberg embed fallback | 2026-10-30 PHT

## Verified defect
The 15 locked published source documents include 28 Gutenberg embed wrappers across eight routes. In the exported static HTML these wrappers contain plain-text URLs rather than usable links: 27 existing Facebook post URLs and one WordPress history URL. The original source URLs, including historical account spelling variants and query strings, are preserved exactly; their live availability and historical accuracy have not been verified.

## Reader-facing repair
A fail-closed build-time transform wraps each original URL as a normal external anchor. It neither loads a social-media iframe nor calls any third-party API, and it does not alter the committed source documents. The generated page retains the exact visible URL, accessible native keyboard navigation, focus, noindex and published search text. CSS supplies an identifiable link treatment and mobile wrapping. All 28 URLs are validated against the existing source-host and path inventory before any generated HTML is changed. Ten unsafe/unreviewed URL mutations are rejected.

The automated external-link audit explicitly reports Facebook URLs as `social_not_probed`, without making Facebook HTTP requests. This is an honest limitation, not a claim that the destinations work. The independent generated-site Chromium gate blocks **all external network requests** and verifies 28 links across eight routes at 320, 375 and 1280px. The existing full-build, source lock, media, privacy, WCAG, PDF, visual, heritage and external-link gates remain required.

## Boundaries
No Facebook operations, images, SDKs, iframe embeds, paid services, third-party reproduction rights, WordPress writes, PDF modifications, private-draft metadata, or public-launch changes. Four private drafts, 82 media, 13 posts + two pages and noindex remain unchanged. CHM-B040 rejected historical CS12 operation is untouched. Full Newspack visual/carousel parity, manual screen-reader certification and independent exact-production browser verification remain pending.
