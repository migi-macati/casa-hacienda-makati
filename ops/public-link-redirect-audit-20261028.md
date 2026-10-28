# Public link and canonical redirect audit — 2026-10-28 09:38 PHT

This change adds a read-only GitHub Actions audit of **only** the 13 published articles, two public pages, and homepage. It verifies the deployed published-only search-index closure, noindex, external anchor inventory, slashless canonical redirect behavior, and observed HTML transfer sizes/timings. It probes each distinct public external link with bounded, concurrent HEAD requests, with GET fallback only when HEAD is unsupported. Redirects are **not followed**, and local/private network targets are excluded.

The resulting JSON and Markdown are GitHub Actions artifacts, not a public content rewrite. 404/410 are observations for editorial review; 401/403/429, redirects, timeouts, and other errors remain **unverified**, never automatically rewritten. No source links, original WordPress content, media rights, private drafts, noindex, or launch settings are changed. Synthetic tests are included. This does not establish WCAG, historical accuracy, media rights, Core Web Vitals or WordPress visual parity.

**Acceptance remains IN PROGRESS; highest baseline DEPLOYED, not FULLY LIVE_VERIFIED.** CHM-B040 remains operation-specific safety-restricted and must not be retried. Owner rights/privacy and public-launch decisions remain open.
