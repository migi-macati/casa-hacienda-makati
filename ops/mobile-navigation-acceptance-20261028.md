# Native mobile navigation acceptance — 2026-10-28

The original WordPress visual comparison identified a collapsed mobile navigation absent from the migration. This change adds native HTML details/summary navigation on the 15 locked published routes, homepage and 404, preserving all five existing destinations. The desktop navigation remains visible; mobile opens and closes without JavaScript.

Required CI: complete build and 17 routes × 2 viewports in Chromium with JavaScript disabled; noindex, five links, desktop visibility and mobile open/close. Synthetic regressions reject unexpected links, duplicate headers and missing noindex. Search source CSS lock must be updated. No original WordPress, historical content, media, private draft, rights or launch changes.

**Candidate only until green CI, preview, merge and exact-main READY.** Original WordPress full visual/theme/carousel parity remains unverified. CHM-B040 operation-specific safety restriction unchanged.
