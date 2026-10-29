# Historical-spelling and punctuation-tolerant published search — 2026-10-30 PHT

## Observed problem and change
The existing homepage search used literal lowercase substring matching. A reader entering the historic spelling “Macati”, an accented term, or “bahay-na-bato” could miss indexed text using the modern spelling, unaccented letters, or spaces. This release normalizes query and indexed **published** text with Unicode NFKD, combining-mark removal, punctuation-to-spaces, and the limited historical alias Macati → Makati. It preserves the existing multi-term AND behavior and full-text fallback notice. Punctuation-only searches correctly return no results rather than all pages.

## Independent acceptance
The mandatory search-privacy Chromium workflow now serves the branch-built public directory on loopback and exercises the actual homepage search against the pinned 15-document published index at desktop 1280px and mobile 375px. It compares Macati/Makati, accented/unaccented Hacienda, hyphen/space Bahay-na-Bato, unmatched and punctuation-only queries, restores the 13-card empty-query archive, checks the noindex meta and rejects silent full-text fallback. Existing 30 computed-CSS privacy scans and all other workflows remain required.

## Safety and limits
Only homepage search JavaScript, the existing mandatory browser test and this note change. No original WordPress write, published article/page body, media, PDF, private draft, rights, noindex, robots policy, third-party services or launch status change. The index remains restricted to 13 published articles and two published pages. Search normalization does not provide semantic search, historical source verification, full WordPress visual parity or manual screen-reader acceptance. CHM-B040 remains prohibited. Require reviewed exact-branch CI, preview, squash merge and authenticated READY exact-main production before marking DEPLOYED; READY does not establish full migration acceptance.
