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

## 2026-10-10 — article accessibility repair
- Full-text search PR #3 merged as 71634857062d42aacc90aa0129e3ea802deff298; Vercel production deployment dpl_8GzXqF1q6okEm6TmgFXRHFhNxoUH READY and subsequent main deployment dpl_6GYR3c8NTrdvd6tJhf4T3c7Q2KUD READY. Direct search endpoint/browser interaction not yet independently verified.
- PR #4 https://github.com/migi-macati/casa-hacienda-makati/pull/4 fixes duplicate H1 in 12 Cultural Significance posts. GitHub branch files re-fetched: each of 12 has exactly one H1. Barrio Olimpia already had one H1. Preview deployments queued at last check; merge after build READY.
- Pending: audit image alt text and image rights/attribution, source fidelity, comments, original WordPress comparison, browser QA, final SEO/indexing decision.

## 2026-10-10 17:35 PHT — M unblock pass
- Cleared CHM-B001 (PR #4 merge pending): preview Vercel dpl_FhW5jHdTh56fRFo951Df2qB7XniK READY for head 96a43c215e037aadc17e3efbee1ff2aab2571cab. PR #4 successfully merged as 64fa2ec105d985e3b81bc85e66660619ec7b4c1b. Source audit on branch showed one H1 for all 12 affected articles.
- CHM-B002 (pending automated verification, not owner intervention): production deployment dpl_6LmdGm8KGiqAn4gHzDLqgEFGKByK for merge SHA 64fa2ec105d985e3b81bc85e66660619ec7b4c1b was BUILDING. Recheck once on next run, then verify rendered pages.
- No owner action currently required for PR #4. Continue independent image alt-text audit and content fidelity comparison; keep noindex until final approval.

## 2026-10-10 — M production and image audit
- CHM-B002 deployment gate cleared: PR #4 merge 64fa2ec105d985e3b81bc85e66660619ec7b4c1b matched READY production dpl_6LmdGm8KGiqAn4gHzDLqgEFGKByK; newer checkpoint commit dce40d6c94c6e19843f30b3ae1ae1c01a8ffef2f matched READY production dpl_Fx5ViPbz1Nk9EpJWZKKwbx9LbgzB. Rendered-page and browser QA still pending, not conflated with deployment.
- Fresh GitHub source audit of 13 article HTML files: 59 img elements; 39 have missing/empty alt. This is ARTICLE subset only, not whole-site total. Distribution: CS1 1/5, CS2 1/2, CS3 1/2, Barrio Olimpia 7/8, CS4 1/2, CS5 1/2, CS6 1/2, CS7 7/8, CS8 4/5, CS9 1/2, CS10 7/8, CS11 1/6, CS12 6/7. Many blank alt attributes inherited from WordPress; determine which images are decorative versus informative using image context, then supply factual descriptions; avoid guessing subject or attribution from filenames.
- New priority CHM-QA-ALT: contextual visual review and appropriate alt text across articles/pages; separate owner review for uncertain media rights. Continue content fidelity and search endpoint QA. No account-side unblock needed.
