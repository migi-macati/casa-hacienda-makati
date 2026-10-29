# Live noindex response-header acceptance — 2026-10-29

## Scope and observed gap
PR #87 added a global `X-Robots-Tag: noindex, nofollow` rule to `vercel.json`. The existing mandatory production browser gate checked HTML meta robots, robots.txt and security headers, but did **not** inspect the actual `X-Robots-Tag` response on HTML, JSON, PDFs or the 82 media assets. A successful configuration test or READY deployment cannot establish served-header parity.

## Safe QA change
The independent read-only production acceptance script now fails closed when the response header is missing, contradictory, duplicated or changed. `get_bytes()` checks actual served HTTP headers for the search index/provenance, robots.txt, media inventory and every media asset (including all three PDFs); the Chromium page checks cover 30 article/page visits, two homepages and two 404 responses. Positive case-insensitive fixtures and nine negative/duplicate cases run before the live audit. No request changes server state, no external service is added, and no published content or media is modified.

## Interpretation and release gates
This proves only that the tested production deployment served the configured header at audit time. It cannot guarantee deindexing: `robots.txt` Disallow can prevent crawlers from fetching the header, and public URLs may remain discoverable. Preserve both existing restrictions pending a separate owner decision. It does not resolve media rights, four private drafts, WordPress carousel fidelity, comments, manual screen readers, PDF-UA, field performance or historical archival identity. CHM-B040 rejected historical CS12 operation must never be retried or bypassed.

Require reviewed exact-head diff, successful mandatory CI (especially the live production acceptance job), squash merge, and authenticated READY exact-main production. A READY deployment is DEPLOYED, not overall FULLY LIVE_VERIFIED.
