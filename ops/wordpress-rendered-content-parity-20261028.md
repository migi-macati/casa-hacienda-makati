# WordPress published-content versus deployed article parity — 2026-10-28 05:32 PHT

Scope: original `casahaciendamakati.wordpress.com` READ-ONLY public WordPress content API, and authenticated `casa-hacienda-makati.vercel.app` deployed HTML. Exact pre-audit main `c10cf77367359dadc266324ff46d7b2ed45715cf` was READY with Vercel CI SUCCESS. This is a content/structure audit, **not** original WordPress visual-theme or screen-reader acceptance.

## Method

Read all 13 published WordPress posts and both published pages through the authenticated **read-only** WordPress content API. Independently fetched all 15 deployed public routes through authenticated Vercel HTTP. Compared ordered content blocks `p,h1–h6,li,figcaption,blockquote` containing at least 24 normalized characters, stripping footnote-reference `sup` tags, decoding HTML entities, normalizing whitespace and common typographic quotes/dashes. Compared the number of inline images inside the body. Excluded WordPress's dynamic Newspack related-post carousel from article-body comparison, using balanced div removal; it is a theme/related-content feature and is **not** equivalent to a migrated native carousel. This deliberately does not compare image visual placement, CSS, layout, WordPress theme, gallery behavior, captions, exact HTML markup, or comments.

## Results

| Public route | Text blocks WordPress / deployed | Inline images WordPress / deployed | Difference |
|---|---:|---:|---|
| /2023/08/12/cultural-significance-no-1/ | 18 / 18 | 4 / 4 | None |
| /2023/08/12/cultural-significance-no-2/ | 12 / 12 | 1 / 1 | None |
| /2023/08/12/cultural-significance-no-3/ | 11 / 11 | 1 / 1 | None |
| /2023/10/21/cultural-significance-no-10/ | 21 / 21 | 7 / 7 | None |
| /2023/10/21/cultural-significance-no-4/ | 16 / 16 | 1 / 1 | None |
| /2023/10/21/cultural-significance-no-5/ | 12 / 12 | 1 / 1 | None |
| /2023/10/21/cultural-significance-no-6/ | 21 / 21 | 1 / 1 | None |
| /2023/10/21/cultural-significance-no-7/ | 27 / 27 | 7 / 7 | None |
| /2023/10/21/cultural-significance-no-7-2/ | 18 / 18 | 4 / 4 | One smart-quote rendering discrepancy |
| /2023/10/21/cultural-significance-no-9/ | 32 / 32 | 1 / 1 | None |
| /2023/10/21/history-of-barrio-olimpia-makati-rizal/ | 38 / 38 | 7 / 7 | None |
| /2024/02/06/cultural-significance-no-11/ | 37 / 37 | 5 / 5 | None |
| /2024/10/28/cultural-significance-no-12/ | 35 / 35 | 6 / 6 | Three whitespace differences before a full stop in restored footnotes |
| /about/ | 15 / 15 | 2 / 2 | None |
| /cultural-significance/ | 38 / 38 | 13 / 13 | None |

All **15/15** body routes returned HTTP 200. Ordered block counts and inline image counts match on every route: **351/351** normalized public content blocks and **61/61** inline images structurally accounted for. **347/351** blocks matched exactly after normalization. Four differences were typographic only: one WordPress-rendered smart closing quote on Cultural Significance No. 8, and three spaces before a full stop in Cultural Significance No. 12 source-note citations. No missing or reordered substantive body block was detected. This does not establish byte-for-byte markup or full original WordPress visual fidelity.

The original WXR raw post text contains the two apostrophes in the No. 8 phrase, while the public WordPress rendered-content API displays a closing smart double quote. This PR changes the migrated source's visible quote to match the WordPress **rendered** content and updates its pinned Git blob in the published-search source lock in the same atomic commit. The three No. 12 citation-space differences remain pending; no historical CS12 write or safety-rejected operation was attempted.

## Acceptance still open

The WordPress Newspack carousel on the original is excluded from this body-only comparison and remains a navigation/functionality parity item. Original-theme visual and responsive screenshot comparison, gallery links, accessible PDF transcripts/tagging, native comments, external-link and redirect checks, security, performance, full offline reproducibility and media rights/attribution/privacy remain open. Independently deployed Chromium and all 82 served-media SHA256 checks were previously verified in PR #43. Preserve four private drafts, all 82 media, noindex, and original WordPress READ-ONLY. **Highest state DEPLOYED, not FULLY LIVE_VERIFIED.** Do not disclose private-draft metadata or associations; no public-launch authorization.
