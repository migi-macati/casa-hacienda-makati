# WordPress homepage parity and migration decisions — 2026-10-11 23:37 PHT

## Evidence and scope
Compared the public WordPress homepage (https://casahaciendamakati.wordpress.com/, retrieved 2026-10-11), public WordPress About (https://casahaciendamakati.wordpress.com/about/) and Cultural Significance (https://casahaciendamakati.wordpress.com/cultural-significance/) against current GitHub main HTML `public/index.html`, `public/about/index.html` and `public/cultural-significance/index.html`. This is a **source-level editorial inventory**, not proof of byte-for-byte parity, live browser rendering, historical accuracy, or rights.

## Homepage editorial parity
| WordPress homepage section | New homepage disposition | Decision / verification |
| --- | --- | --- |
| Hero “Embark on a Journey Through Makati’s Past” and introduction | Replaced by “A house that tells Makati’s story” with archival photo and concise site introduction | Intentional redesign candidate; verify owner editorial approval before declaring homepage copy parity. |
| “Unveiling the legacy”: twelve thematic article summaries | Not repeated on new homepage; twelve themed summaries and article links exist in `public/cultural-significance/index.html` | Function appears relocated. Verify all 12 links, text, dates, captions and accessibility. |
| Historical passage attributed to Don Juan Bonifacio, dated 26 October 1831, with cited Escoto reference | Exact attribution passage not present in new homepage HTML | Preserve provenance and decide whether to restore as sourced quotation, link to a research page, or document an intentional omission. Do not invent the quotation or source. |
| “A treasure uncovered” discovery narrative and 12 May 2021 site-inspection photo | Section not present in new homepage HTML | Determine whether it survives in another page; if not, editorial decision required on restoration/relocation. |
| “Follow our social media pages!” and Instagram/Facebook calls to action | New header links to Facebook; original full section absent | Decide whether to restore Instagram and context; no Facebook posting or social-account changes authorized. |
| WordPress signup/footer widgets | Not reproduced | Platform-dependent features; determine if subscriptions/comments data require export or replacement, rather than silently counting them as migrated. |

## Confirmed site structure
- New homepage provides navigation to About, Cultural Significance and a searchable 13-article archive.
- WordPress About sections LOCATION, NAME, AGE and CURRENT STATE appear in migrated `public/about/index.html`, with two empty-alt historical photos; full paragraph-level parity remains to be tested.
- WordPress Cultural Significance displays 12 article themes and source text; new `public/cultural-significance/index.html` contains the first and twelfth theme headings and the 12 linked-article structure. No. 12 title link and No. 5 empty anchor were corrected on PR #18, but PR #18 remains unmerged as of this audit.
- Homepage changes are not automatically migration defects: homepage redesign may be intentional. Published articles and two WordPress pages require stricter content fidelity than the redesigned landing page.

## Next acceptance steps
1. Build a normalized text/date/permalink comparison for all 13 posts and 2 pages from the owner-supplied WordPress WXR, with human review of captions, embedded links, footnotes and historical claims.
2. Decide whether the 1831 quotation and discovery narrative should appear on the homepage or an archival research page; preserve citations and original wording if restored.
3. Confirm public comment counts, four private drafts, media provenance/permissions, and whether WordPress-only subscription features are intentionally excluded.
4. Compare actual mobile rendering and performance against WordPress once a browser-accessible production endpoint is available.

WordPress remains the reference site. Keep its content intact and preserve noindex until the owner makes a rights/readiness decision.
