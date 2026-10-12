# Homepage editorial parity audit — 2026-10-13 00:32 PHT

Scope: public WordPress homepage compared against `public/index.html` on main (commit 68fb8340b940f436b6cbcfeea49c3416b5ae3c78). Source inspection only; rendered replacement homepage remains unverified.

## Verified differences
- WordPress homepage headline: "Embark on a Journey Through Makati’s Past"; replacement homepage headline: "A house that tells Makati’s story." This is a redesign, not necessarily a migration defect.
- WordPress homepage has an introductory "Unveiling the legacy" section, twelve individually summarized cultural-significance subjects, and an "A treasure uncovered" section. Replacement homepage instead has a shorter hero, "The place" section, and an article archive. Verify that original homepage-only prose is preserved somewhere discoverable before final cutover.
- WordPress homepage displays an attributed passage dated 26 October 1831, credited to Don Juan Bonifacio, with a linked reference to Salvador P. Escoto's publication. No corresponding passage appears in the inspected opening replacement homepage source. Preserve original wording and attribution if restored; do not elevate its historical claims without primary-source review.
- WordPress homepage explicitly identifies the 1910 Casa Hacienda image and the 12 May 2021 site inspection image. The replacement hero shows an archival Casa Principal image with contextual caption. Check provenance and rights before modifying captions.
- Replacement source contains `noindex,nofollow`; retain pending owner readiness/rights decision.

## Evidence
- WordPress: https://casahaciendamakati.wordpress.com/ (public homepage inspected 2026-10-13 PHT).
- Repository: https://github.com/migi-macati/casa-hacienda-makati/blob/main/public/index.html
- Live replacement page could not be fetched by the available web inspector; this is a verification gap, not evidence that production is broken.

## Acceptance / next work
1. Inventory homepage-only prose and citation against the WordPress export; distinguish intentional redesign from lost research.
2. Decide where the dated 1831 quotation and attribution belong in the replacement information architecture, with source fidelity review.
3. Test rendered homepage, navigation, and asset URLs in an HTTP/browser-capable environment.
4. Preserve WordPress and noindex. Do not infer rights clearance from successful bundling.

## Blocker queue (reconciled, no new owner approvals assumed)
- CHM-B038 PENDING: PR #27 head 1996b66b passes Vercel status; merge tool safety rejection before GitHub execution. Retry after materially changed circumstances, do not bypass controls. Automation owner. Highest state pr_open, CI successful.
- CHM-B031 PENDING: clean builds fetch 82 media from Vercel mirror/WordPress. Automation owner. Plan local artifact provenance and deterministic build strategy.
- CHM-B006 PENDING: direct public endpoint inspection inaccessible. Automation owner; verify via supported HTTP/browser tool.
- CHM-B028 PENDING: full content, browser, mobile and performance acceptance, including homepage parity. Automation owner.
- CHM-B029 PENDING: deployment file-tree API inspection not supported for this Git deployment; optional, not a blocker to other endpoint tests. Automation owner.
- CHM-B037 PENDING: media provenance, attribution and rights. Automation researches inventory; owner decides rights and noindex.
