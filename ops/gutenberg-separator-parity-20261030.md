# Original Gutenberg separator visual fidelity — 2026-10-30 PHT

Scope: restore 25 existing WordPress `wp-block-separator` horizontal rules across 13 locked published articles and two informational pages, using CSS only. Original source inventory has 25 separator elements, all with `has-alpha-channel-opacity`; 5 in Cultural Significance No. 1, 3 in the Barrio Olimpia article, 1 in No. 12. No article, source media, PDF or private-draft change.

Problem: the migration retained original Gutenberg classes but omitted their separator rules, leaving browser-default horizontal-rule styling. The scoped rule restores a 100px centered line with a 2px bottom border and honors the original alpha-channel-opacity class. It uses the existing text color and no external asset. This is a conservative Gutenberg block approximation; pixel-exact original Newspack theme fidelity is **not** claimed.

Verification: mandatory source-locked 25-element inventory and 11 fail-closed mutation fixtures in `scripts/test-wordpress-separators.mjs`; generated-site Chromium computed-style and horizontal-overflow checks at 320, 375 and 1280px across three representative published routes, with all external requests blocked. All 15 documents remain pinned, with stylesheet blob updated atomically. Require exact-head CI, reviewed PR diff, preview, merge and exact-main Vercel production before marking DEPLOYED. No separate final-production Chromium verification is implied by branch build.

Constraints: original WordPress READ-ONLY; four private drafts remain private, 82 source media unchanged, 13 articles and two pages preserved, noindex and robots unchanged. No Facebook operations or remote embeds, third-party image reproduction, paid services, rights/attribution/privacy authorization, or public launch. CHM-B040 safety-rejected historical CS12 operation must not be retried or bypassed. This CSS-only visual treatment is not a historical claim or CS12 content/PDF/parcel modification.

Still open: original Newspack global theme/carousel parity, per-asset rights, manual screen-reader WCAG, PDF accessibility, native comments, field CWV/INP, source-critical archives and full migration acceptance.
