# Public link and canonical redirect audit — 2026-10-28 09:38 PHT

This change adds a read-only GitHub Actions audit of **only** the 13 published articles, two public pages, and homepage. It verifies the deployed published-only search-index closure, noindex, external anchor inventory, slashless canonical redirect behavior, and observed HTML transfer sizes/timings. It probes each distinct public external link with bounded, concurrent HEAD requests, with GET fallback only when HEAD is unsupported. Redirects are **not followed**, and local/private network targets are excluded.

The resulting JSON and Markdown are GitHub Actions artifacts, not a public content rewrite. 404/410 are observations for editorial review; 401/403/429, redirects, timeouts, and other errors remain **unverified**, never automatically rewritten. No source links, original WordPress content, media rights, private drafts, noindex, or launch settings are changed. Synthetic tests are included. This does not establish WCAG, historical accuracy, media rights, Core Web Vitals or WordPress visual parity.

**Acceptance remains IN PROGRESS; highest baseline DEPLOYED, not FULLY LIVE_VERIFIED.** CHM-B040 remains operation-specific safety-restricted and must not be retried. Owner rights/privacy and public-launch decisions remain open.

## Verified CI observations — 2026-10-28 09:42 PHT

GitHub Actions public-link run [40616622286](https://github.com/migi-macati/casa-hacienda-makati/actions/runs/40616622286) **SUCCESS** on branch commit `0c31f1b5ea9b1e92654c80dc77e86b0395a4841d`: Python compilation and **10/10 synthetic assertions PASS**. This read-only deployed-site sample found **148 external anchor occurrences**, **80 distinct URLs**, **27 hostnames** across the homepage and 15 published routes. Results: **49 reachable**, **17 redirects not followed**, **8 restricted/unverified**, **3 network-unverified**, and **3 HTTP 404 observed after body-free GET confirmation**. Two 404 observations are the same Bataan Legacy PDF, with and without a tracking parameter; one is a Pacific Wrecks aerial photograph link with a tracking parameter. All **15/15** slashless published routes redirected to the exact canonical slash-terminated URL. Observed HTML fetch timings are runner-dependent and **not Core Web Vitals**.

The three 404 observations, retained verbatim for editorial verification, are:
- `http://bataanlegacy.org/uploads/3/4/7/6/34760003/guerrilla_intelligence_activities_part_1.pdf`
- The same Bataan Legacy PDF URL with an inherited `fbclid` query parameter.
- `https://pacificwrecks.com/airfields/philippines/nichols/1945/aerial-manila-nichols-nielson.html` with an inherited `fbclid` query parameter.

**Do not automatically rewrite these citations.** The original document or image identity, working replacement URL, and attribution must be independently verified. The artifact contains per-URL statuses and redirect observations. Earlier source-HTML inventory (116 occurrences, 64 URLs, 20 hosts) used a different surface; this run measures actual deployed pages including generated navigation and discussion links.
