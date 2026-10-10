# Migration source QA snapshot — 2026-10-11 04:36 PHT

Read-only inspection of all 15 published content-page HTML files on GitHub main (13 posts and two pages), and of `scripts/bundle-media.mjs`.

- All 15 files fetched successfully.
- All 13 article HTML files currently share the title `Casa Hacienda de San Pedro Macati`; the two pages have distinct titles.
- None of the 15 files contains a canonical link element.
- 76 `img src` attributes across the 15 source files reference `casahaciendamakati.wordpress.com/wp-content/uploads/`. These are **source-stage** references, not evidence of live external dependencies: `scripts/bundle-media.mjs` rewrites matching WordPress uploads to local paths during builds, and fails if any upload reference is unmatched. Deployed integrity still requires endpoint verification.
- Five articles have 44 `data-fn` citation references without matching target IDs in main (4 + 4 + 13 + 14 + 9).
- QA branch `qa/check-local-fragment-links-20261011` commit `595f8b9708fd5d849805c3c5c066b7d8a6ed1dc5` has a READY preview, but PR creation was rejected before execution.
- Original WordPress homepage publicly accessible; migrated homepage and `/search-index.json` inaccessible to the web verification tool. No live functionality conclusion.

Next: restore source-note targets, integrate fragment checks, repair article titles and canonical metadata without lifting noindex, and verify deployed media/search/browser behavior. Do not publish four private drafts or restricted images.
