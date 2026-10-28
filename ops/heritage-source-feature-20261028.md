# Source-register homepage feature: limited institutional records — 2026-10-28

## Evidence and scope
A public, accessible, text-only homepage section is proposed as a **partial** sources feature. It cites only three identifiable institutional catalogue/marker records:
1. NHCP 1937 San Pedro Macati historical marker, https://philhistoricsites.nhcp.gov.ph/registry_database/san-pedro-macati/ . The inscription is a retrospective account of 1607, 1620 and 1768, not an original seventeenth-century deed or proof of Olympia construction.
2. NHCP 1991 Makati marker, https://philhistoricsites.nhcp.gov.ph/registry_database/makati/ . The 1608 encomienda reference is distinct from the 1607 donation.
3. British Library Add MS 17641 C, record 040-002027896, https://searcharchives.bl.uk/catalog/040-002027896 . The catalogued 1775 Manila-environs map is attributed to Diono. Kelley. The sheet itself was not inspected; no site depiction, physical building age or map reproduction is claimed.

The records distinguish event dates, later source dates, institutional metadata, and site-specific proof. The feature does **not** assert that the 1775 map depicts the surviving Casa Hacienda. The 1800 Add MS 17641 D is a different item and is deliberately excluded.

## Engineering and safeguards
The homepage has one marked `sources` section, a named region, three accessible records with direct institutional links, and an existing article-index link. There is no JS, animation, media, new route, PDF derivative, or change to the original WordPress site. Inline CSS adapts from three columns to one at <=920px; global CSS and locked published article sources are untouched. `scripts/test-heritage-sources.mjs` is part of the mandatory build and fails closed on 10 negative fixtures (noindex, count, archival identity, source limits, allowlist, media and accessible naming). The feature remains **PENDING independently deployed browser/source/manual-screen-reader acceptance**, not a completed comprehensive source database.

Preserve 13 posts + 2 pages, four private drafts, 82 media, noindex/robots. Owner rights, attribution, privacy and public launch decisions remain open. Do not retry CHM-B040 safety-rejected historical operation. Source research remains in `ops/heritage-map-source-register-20261028.md` and `ops/heritage-timeline-evidence-20261028.md`.
