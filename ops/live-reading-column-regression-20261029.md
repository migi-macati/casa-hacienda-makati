# Live production reading-column regression gate — 2026-10-29 PHT

## Defect and exact scope

The 2026-10-28 read-only original WordPress visual lab measured a migrated article prose column about 208 px wider than the original on desktop. PR #91 reduced the shared layout maximum from 1,150 to 960 px, with a computed 638 px article column at 1,280 px desktop and an unchanged 323 px mobile column at 375 px. PR #91 was merged as main `ae9064c539dda8a9e18e090f4ca7457e8b31aa40` and Vercel production `dpl_E685DYr1nK1uHqSb6ScQuVgjUbrc` was READY at that SHA. The new CSS was directly fetched from the deployed primary alias with HTTP 200 and `X-Robots-Tag: noindex, nofollow` on October 29 at approximately 22:38 PHT. This verifies served CSS, not browser geometry or WordPress pixel parity.

This change extends the existing independent production Chromium test. On each of the 13 published articles at 1,280 and 375 px, it measures the actual rendered `.layout`, `article.content`, and `.sidebar` rectangles and fails closed if desktop prose is over-wide, sidebar overlaps, or mobile prose/sidebar stacking regresses. It runs in the existing eight-workflow PR CI suite against already deployed production, with six negative geometry mutations and two valid fixtures. The 13 articles x two viewports provide 26 live geometry checks, in addition to existing visible-text, media-hash, noindex, security, keyboard/gallery and search acceptance.

## Limits and safety

These bounds deliberately tolerate small subpixel differences and do not claim exact original WordPress typography, feature-image placement, theme, Newspack carousel or manual screen-reader equivalence. The independent original-versus-deployed visual lab remains diagnostic. If the PR's production-browser workflow passes, it establishes live geometry on the already deployed PR #91 CSS; a subsequent QA-only merge does not alter that CSS.

Only `scripts/audit-production.py` and this QA note change. No published HTML/CSS/media/PDF, original WordPress, private drafts, rights, noindex or launch decisions are modified. The CHM-B040 rejected historical article operation remains prohibited. Manual WordPress visual review, global carousel rights/parity, native comments, PDF remediation, field CWV/INP and comprehensive heritage research remain open.
