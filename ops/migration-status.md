# Casa Hacienda migration checkpoint

Last inspected: 2026-10-10 (Asia/Manila)
Status: IN PROGRESS; acceptance NOT established.

## Verified
- Vercel production deployment dpl_DfeptNMXQERUReG5WMrjXYAkdsMh is READY for main commit be5461841e26bad72cdf91d4895205b2ad6fa03c.
- package.json builds with `node scripts/bundle-media.mjs` and depends on sharp 0.35.5.
- Production commit message states 82 archival media files are bundled; individual integrity, rights, alt-text and endpoint validation remain unverified.
- Original WordPress archive must remain online; unpublished drafts must stay private.

## Outstanding acceptance
- Compare all 13 published posts and 2 pages against WordPress export for exact text, dates, metadata, links, citations and permalinks.
- Inventory and integrity-test 82 media files; check licensing, attribution, alt text, deployed URLs.
- Verify 4 drafts remain private and investigate comments or missing WordPress data.
- Test full-text search, navigation, responsive layouts, headings, keyboard accessibility, metadata, sitemap, redirects, robots/noindex, security and broken links.
- Benchmark mobile performance and usability against original WordPress site.
- Verify final production commit SHA, rendered pages and endpoints before completion.

## Next action
Inspect existing site source and migration data, then implement highest-priority unblocked improvement on a reviewed branch. Do not lift noindex until content, rights and QA are approved. Record each result here.

## Constraints
Do not modify BetterMakati or Facebook. Never claim complete or error-free without acceptance evidence.

## 2026-10-10 16:21 PHT — heading and metadata fix
- PR #2 https://github.com/migi-macati/casa-hacienda-makati/pull/2 created from fix/page-heading-hierarchy-20261010, head SHA 00b50f29f11cd816ae90e0fad3e9904c3b71c2dd.
- About and Cultural Significance each had two H1 elements; source edits retain the page H1 and demote the WordPress embedded heading to H2. Distinct page titles added. Original historical text preserved.
- Stage: pr_open. Mergeable reported false at creation; do not assume CI failure. Check PR checks and mergeability after GitHub processing; merge only when safe, then verify matching READY production SHA and rendered pages.
- Unfinished: complete content/media verification, full-text search, sitemap/SEO, accessibility, performance, rights review. Keep noindex in place.

## 2026-10-10 — full-text search release
- PR #2 merged as 5a42ae604a9ca6054c767d541a658bf444633d8a and matching Vercel production deployment dpl_Dqyj45YyoqZZMy7LJ6SMxoxruBpZ is READY; rendered-page check remains separate.
- PR #3 https://github.com/migi-macati/casa-hacienda-makati/pull/3 head 6770452c192d0a6c920c2f446adca3c12a3df82d: published-article full-text search index and homepage filter, with summary fallback. Preview dpl_FJNnKHH9G845rRr1DWCHiji1o8KD BUILDING at last check; logs show media bundling underway. Do not merge until checks pass.
- Next: verify preview READY and search-index.json has 13 entries, test a body-only query, then merge PR #3 and verify matching READY production deployment. Continue remaining migration acceptance checks.

## 2026-10-10 — GitHub mutation unblocked
- PR #3 successfully squash-merged into main, SHA 71634857062d42aacc90aa0129e3ea802deff298. Full-text search is merged, not yet production-verified.
- Vercel production deployment dpl_8GzXqF1q6okEm6TmgFXRHFhNxoUH matches this SHA and was INITIALIZING at last check. Verify READY and actual /search-index.json endpoint before declaring published.
- Next: audit and repair article H1 hierarchy, then per-image alt text and attribution. Do not lift noindex until final acceptance.
