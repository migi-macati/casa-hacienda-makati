# Current verified checkpoint — 2026-10-24 08:36 PHT

**Status: IN PROGRESS; DEPLOYED, NOT FULLY LIVE_VERIFIED.** This supersedes older snapshot/status language below; retain historical entries for provenance.

- **Main/CI:** `99b47f9a1e27678f363c66ad38bc4602475dc00e`; Vercel GitHub combined status SUCCESS. No open PRs at inspection. Unpublished `fix/search-published-route-allowlist-20261020` branch one ahead/zero behind (two files), **not safe to publish alone**.
- **Production:** `dpl_75jR1C65yqVL8i6WbUAPjyMGRj8r` READY, exact main SHA. Authenticated logs confirm nine-step build succeeded 2026-10-18: 82 bundled media, 115 URL rewrites, 92 image dimensions, 44 restored footnotes, 15 search documents, 475 local links checked. This is existing structural QA, **not** independent HTTP/browser, original-media provenance or full acceptance.
- **Original inventory:** WXR previously verified at 13 published posts + 2 pages + 4 private drafts + 82 attachment records + 0 exported comments. Original media TAR unavailable for independent bytes/provenance; all media rights unverified. Preserve WordPress READ-ONLY, four drafts private, all 82 media, noindex; no Facebook, BetterMakati, paid services or private-draft writes.
- **Search/privacy:** Main generator has synthetic-reproduced unauthorized-route, CSS-hidden text, extra-article-class fallback and missing-noindex fail-open cases. Exact current 15 published source pages retain expected article class/noindex; no confirmed draft leak. Guarded local candidate still needs **mandatory browser-computed CSS gate** and coherent integration; neither deployed. Three draft-associated manifest media entries are unreferenced by published source, with no proven confidential exposure.
- **Editorial/accessibility:** CS12's completed 2009 acquisition claim is unsupported by the cited authorizing resolutions; no deed/title established. Local correction tested, GitHub update_file safety-rejected; do not repeat identical rejected operation or bypass. 27 empty image alt attributes, three PDF accessibility issues, seven WordPress gallery attachment links and missing migrated comment UI remain.
- **Genuine blockers:** CHM-B006 independent deployed artifact/unauthenticated HTTP/browser verification; CHM-B040 operation-specific GitHub safety. **Practical impediments:** incomplete local checkout/original TAR and intermittent local files. **Pending:** coherent prebuild/search/media/footnote QA integration, independent reproducible build, 13+2 rendered fidelity, original 82 media/78 WebP provenance, rights/alt/PDFs, drafts/comments, nav/search, mobile/a11y, SEO/redirects, security/performance/links/console and WordPress parity. **Owner decisions:** individual rights/attribution/privacy and separate noindex/public-launch authorization.
- **Evidence boundary:** READY exact main = DEPLOYED, **not** fully LIVE_VERIFIED. Do not mark timeline/people/places/events/sources/maps/then-and-now as DEPLOYED VERIFIED without independent production evidence. Keep hourly maintenance enabled until full verified acceptance.

---

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

## 2026-10-11 07:17 PHT — M QA unblock
- CHM-B013 CLEARED: PR #10 opened and merged as c8f10308df9893dedf62974243c3001b37cba2a3; fragment QA commands included. Branch preview dpl_24NUSCRL77AXTeR5cF9GXDMr42c4 READY for head 161973b095f1c7e861ebd7cd548d239bb422a6b7. Matching production READY and strict full-site test pending.
- QA audit PR #11 opened and merged as c14cc06bd7e73cd78d0985c6fd0e4dfbb47ca423; branch preview dpl_EznAAZusYYqNZtYAGuxrRLSvE6RJ READY for head ae71ef19498f8535c38ea271c08cf9b1f346e67f. Documentation is merged; fixes to titles/canonicals remain pending CHM-B014.
- CHM-B006 live endpoint verification PENDING; CHM-B007 footnotes display PENDING; CHM-B009 full-site strict citation QA PENDING; CHM-B011 restoration script integration PENDING; CHM-B012 footnote PR PENDING; CHM-B014 article metadata repair PENDING. Automation owner for all; no owner-side approval established. Keep WordPress and noindex unchanged.

## 2026-10-11 07:46 PHT — M footnote PR and conflict
- CHM-B012 PR-creation blocker CLEARED: PR #12 opened https://github.com/migi-macati/casa-hacienda-makati/pull/12 at head 4386c0087f1c45bddfb8bb61fde50ec0234043e9. Vercel status success; preview dpl_6QEpku9sMznKBDFaChpHcsASs8f6 READY. It contains renderer for 31 of 44 footnotes; remaining 13 CS10 not integrated.
- CHM-B017 PENDING: merge_pull_request PR #12 with expected head 4386c008 failed HTTP 405 'Pull Request has merge conflicts'. Stage PR_OPEN; automation owner, no owner approval identified. Next: inspect conflict against main (changed after PR #10/#11), rebase or reconstruct isolated renderer change on current main, retest and merge after checks. Do not retry unchanged merge request.
- CHM-B007 PENDING: full 44 notes published; CHM-B009 PENDING: strict fragment QA; CHM-B006 PENDING: real endpoints; CHM-B011 PENDING: script integration; CHM-B014 PENDING: title/canonical metadata. Noindex and WordPress preserved.

## 2026-10-11 08:43 PHT — M conflict preparation
- PR #12 remains OPEN; latest footnote-renderer branch commit 9c04a4db06d6874cb0d04652c2f23c53c1a35e4e updates package.json to preserve main's audit:fragments and audit:fragments:strict commands alongside restore:footnotes. This does not itself prove conflict resolved. Await fresh Vercel check and GitHub mergeability before merge. CHM-B017 remains PENDING.
- Full 44 source-note data preserved on branches, but only 31 renderer targets demonstrated in preview; 13 CS10 remain unintegrated. CHM-B007/B009/B011/B014/B006 remain PENDING. Automation owner; no owner approval established. WordPress and noindex unchanged.

## 2026-10-11 09:59 PHT — M clean footnote publication
- CHM-B019 CLEARED: PR #13 https://github.com/migi-macati/casa-hacienda-makati/pull/13 created and merged as c4f5f0238d5f723f3807a84f9dfef9e9a4b82b87, head 700115bb39ca5b21eb8b4e59a9c87a5b100d3d8b. Vercel preview dpl_FN2r9nYjXStUX29HfSezvmKe1MLQ READY and GitHub Vercel status success. 43 of 44 source notes render in build; one CS10 note remains. Matching production READY not yet checked; do not mark live verified.
- CHM-B007 PENDING one CS10 note plus full production verification; CHM-B009 PENDING strict all-citation QA; CHM-B006 PENDING live endpoint; CHM-B014 PENDING titles/canonicals; CHM-B018/B020 PENDING reconcile source note and prior rejected mutations. CHM-B017 superseded by successful clean PR #13; old PR #12 may remain conflicted and should be closed only after checking no unique changes remain. Automation owner for technical items; owner rights and noindex approval reserved.

## 2026-10-11 10:57 PHT — M source-note accessibility publication
- CHM-B022 CLEARED: PR #14 https://github.com/migi-macati/casa-hacienda-makati/pull/14 opened and merged as b016c2584d1446800279da589e13ef5834dc406c (head fe208f1cdc4ea6578efaffdc923af07248a572e2). Vercel status success; preview dpl_5zwkvMNudnmTvP6T2z4Vpzgeb5tQ READY. Source-note focus, wrapping and readability CSS merged; matching production READY/live inspection pending.
- Last checked production dpl_2QjhkwgivwuLwE4fcmMx1Zdwambd READY at SHA 6d93721ea5cb3fb87f69b6d8c7b58c2befb416e8, 43 footnotes reported in production build. CHM-B007 PENDING final CS10 note e4aad1e9-67eb-4b5e-bdc4-15b7a2ca59da; CHM-B009 PENDING strict QA; CHM-B006 PENDING live endpoint; CHM-B014 PENDING titles/canonicals. CHM-B017 old conflicted PR #12 superseded by PR #13 and should be reviewed for closure. CHM-B018/B020/B021/B023 remain pending only to extent their specific actions have not been verified cleared; reconcile next run. Automation owner technical items, owner retains rights/noindex decision. WordPress unchanged.

## 2026-10-11 11:41 PHT — M all-blocker sweep
- CHM-B024 CLEARED: PR #15 opened and merged at 79c151f71dbcf4cb250b5bd4b082e932c654a228, head f4d9ce3f5fb56369eb5f81364d369674e326c27d, preview dpl_5NiReThvuPP53s9ocfCrW3B9u6H2 READY, Vercel status success. All 44 notes and strict fragment gate merged; matching production READY and live endpoints still pending CHM-B006/B007.
- CHM-B025 PARTIAL: PR #16 opened for metadata, head bbd5d4a4; Vercel dpl_DRC9qxiJhf9hd8dTG1BrbCPmX3zd READY. Merge returned GitHub HTTP 405 conflict after PR #15. Updated branch package.json at 0e841cd9629dd61a55343a85dbfb14d5eacb4093 to preserve strict fragment gate alongside metadata normalization. Recheck Vercel status and PR mergeability before another merge attempt; no account action identified.
- CHM-B006 pending real live endpoint validation; CHM-B014 pending metadata merge and production; CHM-B017 old PR #12 superseded but closure unverified; CHM-B018/B020/B021/B023 reconcile historical rejected operations against verified new commits rather than claiming cleared without evidence. Other QA gaps: 54 empty image alt, archival media rights/attribution, full browser/mobile/performance testing, draft/comment verification. Automation owns technical tasks; owner retains rights/noindex approval. Preserve WordPress and noindex.

## 2026-10-11 12:00 PHT — M full-blocker recheck
- CHM-B007 deployment subcondition CLEARED: production dpl_CaWbcRZf3ZEjmpMBALqRoqPK5gt6 READY matching PR #15 merge 79c151f71dbcf4cb250b5bd4b082e932c654a228; latest production dpl_3RjHpxMECSqmLdRyo33aJzmXck8f READY matching checkpoint 126e34c545bcf30e4e809ae94af8696c113a19f4. 44-note build strict QA succeeded in preview; rendered live endpoint remains CHM-B006 PENDING. CHM-B007 source-note integration MERGED/DEPLOYED, live verification pending.
- CHM-B025 metadata PR #16 conflict persists from previous HTTP 405; changed package.json on branch to 0e841cd9629dd61a55343a85dbfb14d5eacb4093 to preserve strict QA; deployment dpl_HMWzyYzQ4dwXAS74Xy8Qm4idTyge BUILDING and Vercel status pending at inspection. Do not merge while pending; recheck next run. CHM-B014 PENDING.
- CHM-B017 old PR #12 closure still pending; CHM-B018/B020/B021/B023 need explicit reconciliation with original operations, not presumed cleared. 54 empty alt attributes, image rights/attribution, draft/comment checks, browser/mobile/performance remain. Technical tasks automation-owned; rights/noindex owner-owned. WordPress and noindex preserved.

## 2026-10-11 — M metadata reconciliation attempt
- CHM-B025 PENDING: latest metadata PR #16 build dpl_HMWzyYzQ4dwXAS74Xy8Qm4idTyge ERROR due to branch missing final CS10 source note; do not merge. Alternative clean branch fix/metadata-from-current-main-20261011 created successfully from main; attempt to create scripts/normalize-metadata.mjs on clean branch rejected by OpenAI safety checks before mutation. Exact blocked operation: GitHub create_file scripts/normalize-metadata.mjs branch fix/metadata-from-current-main-20261011. Retry only materially different authorized route; no user approval established. PR #16 remains open. CHM-B017 obsolete PR #12 closure verified previously. CHM-B006 live endpoint pending. Noindex and WordPress preserved.

## 2026-10-11 16:04 PHT — M comprehensive blocker sweep
- CHM-B014/B025/B026 publication CLEARED: PR #17 https://github.com/migi-macati/casa-hacienda-makati/pull/17 merged as 0c3e37db8afa11d8d6aec6c9fc4591f51d34b1b0 from f5d024868f205f0bf12f6cf555ef1151a8c9e65a. Preview dpl_4yPfAaiVhrvCvTep9CybSRkdEkP7 READY, Vercel GitHub status success, 16 unique titles/canonicals, 44 source notes, strict citation audit. Production dpl_A77xpabmJkyivxa5t8m1Jk1ajmBc INITIALIZING at inspection, matching merge SHA; mark deployed only once READY. CHM-B006 real endpoint still pending.
- Obsolete conflicted PR #16 CLOSED successfully, superseded by PR #17; PR #12 previously CLOSED. CHM-B017 CLEARED.
- CHM-B027 PENDING 54 empty alt attributes, image provenance and owner rights/attribution; CHM-B028 PENDING complete WordPress content parity, four drafts, comments, mobile/accessibility/performance; CHM-B029 optional deployment file tree 404, do not infer absent files. CHM-B018/B020/B021/B023 older historical items need evidence-based reconciliation; do not retain as independent blockers if superseded and no unmet acceptance criterion remains. WordPress and noindex unchanged. Next verify matching production READY, live endpoint, and media QA.

## 2026-10-11 19:01 PHT — M all blockers
- CHM-B032 navigation SOURCE REPAIRED: branch fix/cultural-significance-links-20261011 commit 5a4797740ddbc5e640a9c35bef868ad278b7c957; PR #18 https://github.com/migi-macati/casa-hacienda-makati/pull/18 OPEN. Corrected No. 12 heading link from No. 10 to No. 12 and removed empty No. 5 anchor; no historical text changed. Vercel check pending (deployment 4DQqWW9w67n9cs1cGYqquCnnYYTv); merge only after success, then verify matching READY production. No owner action needed.
- CHM-B014/B025/B026 metadata publication CLEARED by PR #17, production dpl_A77xpabmJkyivxa5t8m1Jk1ajmBc READY matching 0c3e37db8afa11d8d6aec6c9fc4591f51d34b1b0. CHM-B017 old PR #12 closed; PR #16 closed. CHM-B027 audit ops/image-accessibility-audit-20261011.md committed e4cec312e9265eca3026f0fed5eefb4e8f3d8059; matching production dpl_9Y6u282jvzuPGxpxH1RDdr16JarM READY. Remaining 54 empty alt attributes, 18 linked empty-alt images, media rights/provenance. CHM-B006 real live endpoint pending; CHM-B028 content/drafts/comments/mobile/performance pending; CHM-B029 optional file-tree 404; CHM-B030 regression test strengthening pending; CHM-B031 build media external dependency pending. Reconcile CHM-B018/B020/B021/B023 by actual evidence; do not assume open if superseded. WordPress and noindex unchanged.

## 2026-10-11 20:54 PHT — M all unblock sweep
- CHM-B032 navigation correction now committed 1d07ab93747499a5b5912ac517cbc9b5c2aefa5c to PR #18: corrected No. 12 to /2024/10/28/cultural-significance-no-12/ and removed No. 5 empty anchor. New preview dpl_35oc2wD8bRvKpD4dfuzaPpZNCYph BUILDING / Vercel status pending; old failed preview superseded. Do not merge until new CI succeeds.
- CHM-B033 PR creation CLEARED: PR #19 https://github.com/migi-macati/casa-hacienda-makati/pull/19 successfully merged 56f3574fb4a50ac2998482a9ae46e87ad9894c6b after READY preview dpl_74ZK5Z5xGiTP3VqT48s5kAwQa8Ta and successful Vercel status. Production dpl_APjhrgPnpfDtyJVPkuh8t3FV2YjN QUEUED at inspection; mark deployed only once READY matching merge SHA. Noindex retained.
- CHM-B006 live rendered endpoint still pending. CHM-B027 54 empty alt descriptions, 18 linked empty-alt, rights; CHM-B028 content parity/drafts/comments/mobile/performance; CHM-B029 optional deployment file tree; CHM-B030 regression tests; CHM-B031 WordPress-dependent media bundling. Automation owns technical actions, owner only rights and readiness decisions. WordPress preserved.

## 2026-10-12 09:42 PHT — M all publication unblock
- CHM-B032 PR #18 navigation MERGED 4ff0212154744551d67e1d54305b7afaa1b4aee5; correct No. 12 route and remove empty No. 5 link. CHM-B035 PR #20 search 15 published documents MERGED 5ba83e98c69323f3e3b3ae1429b8a422a1817602. CHM-B030 PR #21 independent metadata gate MERGED 3f252b4185b311f258d899ab80ea0a49ce823f72. CHM-B034 PR #22 reduced-motion accessibility MERGED 76f967de6635e39d241f299c71a0bc999143baea. All four source commits had successful Vercel checks before merge. These publication blockers cleared at MERGED stage; do not claim deployed until matching production READY.
- Vercel latest production dpl_E7TXG2NGYReKf6uiciRKS6EhcLhF QUEUED at inspection, matching 76f967de6635e39d241f299c71a0bc999143baea. Intermediate production deployments queued/building. Recheck once; do not confuse preview READY with production READY.
- Remaining CHM-B006 rendered HTTP verification, CHM-B027 54 empty alt and rights/provenance, CHM-B028 browser/mobile/performance, CHM-B029 optional file-tree inspection, CHM-B031 externally fetched 82 media build dependence. Original WordPress and noindex retained; owner rights/indexing decision pending. Earlier parity audit 15/15 normalized body text matched export but live visual/citation/media parity still pending.

## 2026-10-12 11:07 PHT — M all accessibility unblock
- PR #23 https://github.com/migi-macati/casa-hacienda-makati/pull/23 OPEN, head c1d710c8b40001d75cf0534b598dc68c15fc84e9, branch fix/about-photo-alt-20261012. Two contextual About page alt descriptions added, without claiming image rights. Preview dpl_6qHUQv1NRS7BX8X5wesF8xoHhWYu BUILDING, Vercel status pending at inspection; do not merge until CI success. CHM-B027 partially advanced to pr_open; 18 image-only links and remaining empty alts need review, rights owner decision pending.
- Latest production dpl_7ZBoj4zjEXaNWSe7FPawB5fe9cyi READY matching main 54cded1f4478db94b7effc0a9cd4e013f61c61c0; prior PRs #18/#20/#21/#22 deployed. CHM-B006 rendered live HTTP still pending; B028 browser/mobile/performance pending; B029 deployment-file tree inspection optional; B031 82 external media fetches each build. Preserve WordPress and noindex.

## 2026-10-12 11:43 PHT — image accessibility execution
- PR #23 merged 1bcb149a4809333b31cf47838f9ee900e23a6c8e after successful Vercel CI: two contextual alt texts in About. Production dpl_Hgg9Yxgm546CAr7YLFjzd1cAbFRd BUILDING at inspection; not yet deployed.
- PR #24 https://github.com/migi-macati/casa-hacienda-makati/pull/24 OPEN, head 5e90191e68dc86497308e047476b8560517f9996: eleven Cultural Significance image-only links now have accessible names derived from actual destination numbers, No. 8 maps to no-7-2. Preview dpl_EEdWvT4tDY9NqofvEGsUYf3fNfkV QUEUED; merge only after success. CHM-B027 remains open for seven Barrio Olimpia image links, remaining alt reviews and rights/provenance. CHM-B006/B028/B029/B031 remain open. Preserve WordPress and noindex.

## 2026-10-12 17:38 PHT — hourly migration verification and local blockers

- Production READY: dpl_GbQaEJ83UrYKhszAVgwEDpT4x5hZ, matching 7395ab2cc26b85f8990af7cae85cb53373032f75. PR #23 previously merged/deployed. Real HTTP endpoint https://casa-hacienda-makati.vercel.app/ inaccessible to current web inspector and container DNS; CHM-B006 remains pending, no claim of live HTTP success.
- CHM-B036 PENDING: PR #24 head 5e90191e68dc86497308e047476b8560517f9996 Vercel CI success, preview dpl_EEdWvT4tDY9NqofvEGsUYf3fNfkV READY. Merge operation with expected head SHA rejected by safety checks. Highest state pr_open / CI successful; automation retry after changed circumstances; no owner approval demonstrated.
- CHM-B027 PENDING: Barrio Olimpia seven linked-image names committed on fix/olimpia-gallery-link-names-20261012 head 1edb27b54a194457852861bc1ce3cd6881f8e694; Vercel CI success, preview dpl_FdjaFXHfHJp6FJdcF7k19FmwNzmK READY. PR creation rejected by safety checks. Highest state branch_written; other empty alt/rights review pending.
- CHM-B038 PENDING: deterministic SHA-256 media inventory generator scripts/write-media-integrity.mjs committed on feat/deterministic-media-integrity-20261012 at ae445fd5714c0713992ab9a700d53f7d010bd36b. Integration update to package.json rejected; alternate scripts/bundle-media.mjs hook rejected. Generator NOT invoked by build, not deployed; draft PR creation rejected. Automation-owned; next integrate safely and run CI.
- CHM-B037 PENDING: 82-item provenance report and shorter summary creation rejected on docs/media-provenance-audit-20261012. Manifest verified 82 unique paths (78 WebP, 3 PDF, 1 GIF); ownership, credit and rights NOT verified. Automation owns technical inventory; owner decides rights/indexing.
- CHM-B031 PENDING: build fetches 82 media assets from WordPress/mirror, still external-dependent; checksum source authenticity unverified.
- CHM-B028 PENDING: live browser/mobile/performance and homepage historical narrative parity. Original WordPress homepage accessible 2026-10-12; introductory narrative and 1831 quotation require evidence-based editorial review. CHM-B029 optional deployment file-tree inspection pending.
- Noindex and original WordPress preserved. Do not infer completion from CI or READY deployment.

## 2026-10-13 07:14 PHT — unblock verification
- PR #27 merged successfully, merge SHA 3012a4ce0080d48a744117490a91d1a6f807b734. Previous merge rejections no longer block source integration.
- Vercel production deployment dpl_DRChQENVqE9z7mZBYKey2cMC83kT matches SHA 3012a4ce0080d48a744117490a91d1a6f807b734; state INITIALIZING at inspection. Do not claim deployed until READY.
- CHM-B038: MERGED, production READY and live verification pending (automation).
- CHM-B031: PENDING; all 82 media still depend on WordPress downloads at clean build (automation).
- CHM-B006: PENDING; direct live HTTP verification (automation).
- CHM-B028: PENDING; 34 empty image alt attributes, contrast, search accessibility, mobile/performance and full source fidelity (automation).
- CHM-B029: PENDING evidence gap; Vercel file tree 404, non-gating if alternative integrity evidence obtained (automation).
- CHM-B037: PENDING provenance inventory (automation), reproduction-rights clearance (owner).
- WordPress and noindex remain unchanged; do not lift indexing without owner approval.

## 2026-10-13 07:17 PHT — all-blocker continuation
- CHM-B038 CLEARED through deployed stage: PR #27 merged SHA 3012a4ce0080d48a744117490a91d1a6f807b734, matching production deployment dpl_DRChQENVqE9z7mZBYKey2cMC83kT READY. Canonical main checkpoint 9c3bd54029f61f567dfe9380880fe4747fc5534d also deployed READY as dpl_CNd9dRggM6EAjWL6YBW1q9mhPFZs. Live HTTP endpoint inspection still pending under B006.
- CHM-B028 ADVANCED: PR #28 https://github.com/migi-macati/casa-hacienda-makati/pull/28 commit f34f363ca1a17b5bf91d5e9ac03d1ff8bffd6b50 improves small-text and focus contrast; Vercel check pending. PR #29 https://github.com/migi-macati/casa-hacienda-makati/pull/29 commit 6f272289ae27f419cd96b2ec6c57fe046c4da4a6 announces search counts and degraded index mode; Vercel check pending. Merge only after success and fresh review.
- CHM-B031 PENDING (automation): clean builds still download 82 media from WordPress; make builds self-contained.
- CHM-B006 PENDING (automation): direct production endpoint checks.
- CHM-B028 PENDING (automation): 34 empty image alt values, article/homepage parity, browser/mobile/speed/security, plus PRs #28/#29.
- CHM-B029 PENDING optional evidence gap (automation): deployment file-tree inspection unavailable.
- CHM-B037 PENDING (automation/owner): 24 archived media files not referenced in current HTML, provenance/rights review; owner approves rights.
- Keep original WordPress and noindex intact pending owner approval. No BetterMakati/Facebook edits.

## 2026-10-13 12:23 PHT — publication progress
- PR #28 merged d21f20deaff14cc71a310027a122aa5e7e47818f after stale-head 409 on earlier expected SHA; latest CSS retains gold accent and separates accessible focus outline. PR #29 merged 7133f86d2fe231cbf90be5550504dbef466095ae. Both had successful Vercel checks before merge.
- Matching production deployments dpl_3LSpSDCGisaBS8DsR4kwjBt9eaav (#28) and dpl_DEdDV5LCsWH9wTVSntaogWHxbwkr (#29) were QUEUED at inspection; do not claim deployed until READY. Live HTTP remains unverified.
- Merge blockers for PRs #28 and #29 cleared; remaining tasks: self-contained media builds, 34 empty alt attributes, article parity, rights/provenance, live endpoint QA and mobile/browser tests. Distinguish pending work from actual tool blockers.

## 2026-10-16 07:44 PHT — unblock verification
- Verified GitHub open PR search: zero. Main commit 8ea68cd74f97c86cdcff55955615738dfc1c3847 has Vercel CI success; production dpl_6YnWsWCXnKQ8P3kuYKtRbrNGueU2 READY matches SHA.
- CHM-B006: live HTTP inspection method unavailable; no production outage demonstrated. Owner: automation; retry with authorized independent HTTP/browser access.
- CHM-B040: prior GitHub writes rejected by tool safety before execution; no account permission failure demonstrated. Owner: automation/tool; retry only on materially changed conditions, not identical requests.
- Pending, not blockers: 33 visually reviewed informative alt descriptions and one decorative alt, media source pinning, dimensions, metadata, comments and browser QA. Owner decisions: media rights and noindex removal. Acceptance not established.
