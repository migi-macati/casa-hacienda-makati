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

## 2026-10-10 17:40 PHT — production verification and accessibility audit
- CHM-B002: RESOLVED at **deployed** stage. Vercel production dpl_6LmdGm8KGiqAn4gHzDLqgEFGKByK READY matches PR #4 merge SHA 64fa2ec105d985e3b81bc85e66660619ec7b4c1b. Current alias production dpl_Fx5ViPbz1Nk9EpJWZKKwbx9LbgzB READY at dce40d6c94c6e19843f30b3ae1ae1c01a8ffef2f, which follows the merge. Alias mapping confirmed by Vercel get_deployment. Rendered-page/browser verification still pending; direct external fetch unavailable in this runtime.
- Latest production build logs confirm 82/82 media bundled (82 from original WordPress archive, zero mirror), 115 WordPress upload URL rewrites, and 13 published articles indexed. This establishes build completion, **not** per-asset HTTP/integrity, rights or accessibility acceptance.
- Accessibility audit of 15 migrated content pages (13 posts, About, Cultural Significance) found 54 image elements with empty alt attributes (none missing alt attributes). These require contextual image-by-image review; do not invent visual descriptions or rights.
- media-manifest.json has 82 entries but only source/path/convert fields; no item-level attribution, rights or alt metadata. Record owner/provenance review separately before lifting noindex.
- CHM-B003: PENDING (tool mutation safety rejection, not an owner-side approval). Homepage JS sets article card.hidden for search filtering, but author CSS .card{display:flex} lacks .card[hidden]{display:none}, so CSS can override UA hidden display and leave filtered cards visible. Created branch fix/archive-search-hidden-cards-20261010 from dce40d6. Proposed single-rule fix: append .card[hidden]{display:none} next to .card selector in public/assets/style.css. Attempted GitHub update_file to that branch was rejected by tool safety checks before execution. No CSS change, commit or PR was made. Do not retry unchanged rejected action; use a permitted independent scoped change or await an eligible retry with fresh context. User wording cannot override safety rejection. Validate behavior in browser after merge.
- WordPress.com site is accessible publicly, but its connected site-scoped MCP access is unavailable without a paid plan; do not purchase a plan. Public pages can support content comparisons. Initial source comparison: Cultural Significance No. 1 text and source links are present in repository; complete machine-checked fidelity is still outstanding.
- NEXT independent work: image-by-image contextual alt audit and source/metadata fidelity checks. Keep WordPress online and noindex in place.

## 2026-10-10 — M unblock of archive search filter
- CHM-B003: mutation blocker CLEARED. Re-fetched existing branch fix/archive-search-hidden-cards-20261010; GitHub update_file succeeded for public/assets/style.css, commit ed6a8b7ba9b57bb6d70f0d15cc97c6e0d999fd07. Added .card[hidden]{display:none} to prevent .card{display:flex} overriding hidden on filtered archive results.
- PR #5 https://github.com/migi-macati/casa-hacienda-makati/pull/5 OPEN; preview dpl_FVkcfTzTTKr2uudVsuN8L179BLR9 QUEUED at check. Pending build gate and browser interaction test; do not claim search behavior verified yet. Merge after preview checks.
- Separate production deployment dpl_FSufQ65q8N8X78MyUbeWLipXaaij for main SHA 6ad727b8703eebf2b1173798bf428bc2ac5ff4b1 was BUILDING. Reconcile once next run.
- No owner intervention needed for CHM-B003. Continue media alt text, attribution and source fidelity work independently; retain noindex.

## 2026-10-10 — M PR #5 release
- Preview dpl_FVkcfTzTTKr2uudVsuN8L179BLR9 READY for ed6a8b7ba9b57bb6d70f0d15cc97c6e0d999fd07; PR #5 merged successfully as 17d8fb00712e75261e0f7e0a378f067e0dba7008. CHM-B003 mutation blocker resolved; CSS hidden-card correction merged.
- Production deployment dpl_3x3Munrx5mAd7n5w4Bp6hMEPKtE7 matches merge SHA but was QUEUED at check. Do not claim deployed or behavior-tested until READY and endpoint/browser verification.
- Contextual media audit begun: CS1 has scanned Labor Evangelica page images with descriptive alt already, but introductory cs-1-crop-1.png has blank alt. Barrio Olimpia gallery links still point to original WordPress attachment pages and seven of eight article images have blank alt. Avoid fabricating descriptions; inspect visual content and distinguish meaningful from decorative images. Image rights remain owner-review dependent.
- Next: verify production PR5 SHA READY; audit and repair gallery links/alt context, source fidelity, and live search behavior. Retain noindex.

## 2026-10-10 20:40 PHT — M unblock and consolidated queue
- CHM-B004 CLEARED: QA PR #6 https://github.com/migi-macati/casa-hacienda-makati/pull/6 created successfully, head e651fa23ca6268d201aae497643432576e04f4cb, preview dpl_9AUL6uvs5ECN4pyrmzQfEKzzChXi READY; merged as 4e9f58b9ce9cf9251d272facc0256a61aa8d3578. Production matching SHA READY and live QA still need confirmation.
- CHM-B005 PENDING: README correction previously rejected. Retry only against fresh main content on a separate scoped branch; automation owns; no owner action established.
- CHM-B006 PENDING: direct rendered-page/browser verification unavailable in prior runs; retry public endpoints and supported browsing; automation owns; no owner action established.
- CHM-B007 PENDING: restore 44 missing footnote targets in five articles (CS1 4, Barrio Olimpia 4, CS10 13, CS11 14, CS12 9). Existing branch fix/restore-cs1-source-notes-20261010 created but article update previously rejected. Re-fetch original WordPress source notes, preserve verbatim citations, repair on branch and add fragment-link QA. Automation owns; no owner action established.
- Rights/attribution and release indexing are OWNER DECISIONS after evidence inventory; retain noindex and original WordPress. Do not publish four drafts.
- Next: confirm QA PR6 production SHA READY; source-accurate footnote restoration and fragment link tests, image context and rights review. Do not claim acceptance.

## 2026-10-10 20:45 PHT — M blocker progress
- PR #6 merge SHA 4e9f58b9ce9cf9251d272facc0256a61aa8d3578 confirmed matching READY production deployment dpl_EvZsgEFGvbRwaNLV3vPdpytgBxeU. Automated QA release deployed; direct browser endpoint QA still pending.
- CHM-B005 mutation CLEARED: created branch docs/correct-media-build-description-20261010 and corrected README's stale statement about WordPress-hosted media. Commit 05b323d77be9cbbd72d3bbe1b9a865c0930017a1, PR #7 https://github.com/migi-macati/casa-hacienda-makati/pull/7 OPEN. Preview dpl_DA2jLwJXEDweyKy7JAo2RAVAR1bA BUILDING; merge after READY.
- Production deployment dpl_ceQzbKe2B1tLfU8qXTX2NR39oE2m for checkpoint-only SHA 67395f2d99dcbbdee7e76be7fd17cf30e67ddd0f reported ERROR; events endpoint returned empty events. Root cause unknown; separate successful QA deployment remains READY. Investigate if repeated.
- CHM-B006 PENDING live-browser verification (automation); CHM-B007 PENDING 44 footnote restorations (automation); owner rights/attribution and indexing approval remain pending. Next: PR7 preview gate and source-accurate footnote repairs. Noindex retained.

## 2026-10-10 20:44 PHT — comprehensive heritage assessment
- New documented baseline on branch audit/comprehensive-heritage-assessment-20261010, file ops/comprehensive-site-assessment-2026-10-10.md, commit 51336c467869558b23cd4ab26a5e0b1f673296a6. Proposed mission, six audiences, ten weighted dimensions, provisional weighted 45.5/100, and 22 prioritized P0/P1/P2 backlog items with observable acceptance criteria. No historical article edits or indexing changes.
- CHM-B008 PENDING: create_pull_request for assessment branch to main rejected by tool safety checks before execution. Branch/file/commit persist. Do not repeat identical rejected request; retry when eligible with fresh context. No owner action established.
- Public Vercel rendered page inaccessible via assessment web tool; WordPress homepage accessible. Thus score is provisional, not real-device or full browser benchmark. Owner approval remains required for rights and indexing.

## 2026-10-10 — Research and 100/100 quality mandate
- Owner sets target 100/100 against the mission-led ten-dimension acceptance framework. This is a verified quality target, not an assertion that historical research is exhaustively complete.
- Assessment branch audit/comprehensive-heritage-assessment-20261010 now includes detailed research coverage audit and ten source/claim/heritage acceptance gates R01–R10, commit a06da349bf7ec0b07048fc47bc7a686c2bf009a5; file ops/comprehensive-site-assessment-2026-10-10.md. PR creation previously blocked as CHM-B008; retry on fresh eligible run.
- Priority research work: complete source inventory, restore 44 citation anchors, claim-to-source matrix, archive/photo provenance, Olympia versus Poblacion evidence, ownership chronology and conservation dossier. Do not claim numerical research completeness before source inventory; keep uncertain interpretations labeled.

## 2026-10-10 21:01 PHT — Google Drive research source inventory
- Inspected 8 additional research subfolders: NHCP journal drafts (5 entries), 2006 Poblacion Cultural Mapping (6), NHCP Visit (16), CS1 (1), CS10 (2), CS11 (1), CS12 (2), FHL restricted (26 TIFFs). Counts include working materials and copies; no unique-source total asserted.
- Read excerpts of main ~55k-character NHCP journal manuscript, CS11 Liberation draft, CS12 Sugar draft and research-design notes; found central location thesis, primary-source references and explicit unresolved ownership/transfer questions. Distinguish draft claims from original documentary proof.
- Branch research/drive-source-register-20261010b created and ops/research-source-register.md committed at a3604d9bcbad96bd6bd9ed5524505ccf47e15ab1. 20 source entries, 10 priority claims and provenance/rights status. PR #8 OPEN: https://github.com/migi-macati/casa-hacienda-makati/pull/8. No public historical copy or restricted images changed.
- Next: verify PR8 checks and merge when eligible; expand source bibliography and claim-to-source crosswalk; restore 44 historical footnotes. Preserve noindex and FHL image restrictions.

## 2026-10-10 22:52 PHT — M unblock pass
- CHM-B010 CLEARED: PR #7 merged as 1e5a2955ac28d67acd6c2ee591106304f257fd4d and PR #8 merged as 3363afd75e793a78f5cf7229ae377f0423aa921b. Vercel production builds dpl_4Ny7j2ubCddiabY5i3gi5CAbH2Mb BUILDING and dpl_3jxRe1MV8Zq7n1JEUEeXKThiN234 QUEUED at last check; READY and rendered verification outstanding.
- CHM-B008 progressed to PR_OPEN: PR #9 https://github.com/migi-macati/casa-hacienda-makati/pull/9, head a06da349bf7ec0b07048fc47bc7a686c2bf009a5. Mergeable false at creation; await processing/checks before merge. Documentation only.
- CHM-B007 PENDING: 44 recovered WordPress footnotes need repository integration and fragment integrity tests. CHM-B009 PENDING: fragment-link QA. CHM-B006 PENDING: live browser/endpoint verification. Automation owns all three; no manual approval established.
- Keep WordPress online and noindex intact; rights/indexing decisions reserved to owner. Migration acceptance not established.

## 2026-10-10 22:53 PHT — M assessment merge
- CHM-B008 CLEARED: PR #9 merged successfully as 8147d475c1cd46ccc268bd76bd2d932ac18aff35; assessment and research gates now in main. Matching READY Vercel production not yet verified.
- PR #7 merge 1e5a2955ac28d67acd6c2ee591106304f257fd4d matched READY production dpl_4Ny7j2ubCddiabY5i3gi5CAbH2Mb. PR #8 deployment dpl_3jxRe1MV8Zq7n1JEUEeXKThiN234 BUILDING; checkpoint deployment dpl_x9Pz4u4MdVPnUmRJg5mHEqKoyNh9 QUEUED at inspection. Live rendered verification outstanding.
- CHM-B007 (44 source footnotes), CHM-B009 (fragment QA), CHM-B006 (live endpoints) remain PENDING; automation owner. Owner rights/indexing approval still reserved. Noindex and WordPress unchanged.
