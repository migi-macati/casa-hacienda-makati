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
