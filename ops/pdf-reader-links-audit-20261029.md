# Public PDF reader-link and fallback audit (2026-10-29, 12:xx PHT)

## Verified previous-run PDF inventory

The archived exact-branch GitHub Actions evidence from run 40812939692, artifact 12870777740, was downloaded and its JSON inspected. Three public source PDFs remain unchanged in the 82-asset migration inventory: **9 pages total, 7 pages without an extractable text layer**. The 2009-120 scan has 2/2 textless pages; 2009-174 has extractable text on both pages; the 2012 decision has 5/5 textless pages. **All three lack a document structure tree and /Lang declaration** according to pypdf 5.9.0. These are automated indicators, not proof of compliance or a substitute for manual screen-reader/PDF-UA evaluation.

## This change

The new independent `scripts/audit-pdf-link-accessibility.py` runs **after the complete existing build** in `.github/workflows/pdf-accessibility.yml`. It reads the 17 generated public HTML routes and three exact PDF manifest identities, without editing any page or PDF. It requires:
- all public-media PDF references to be local, pinned and free of unexpected origins, query strings and fragments;
- meaningful accessible names for PDF links and embedded objects, with any generic Download link described by an existing document-title element;
- a same-block accessible fallback link for every embedded PDF;
- noindex on PDF-linking pages and preservation of the two previously published resolution links in the original public article;
- a JSON artifact reporting referenced/unlinked PDFs, PDF links and embeds, plus explicit manual-review requirement.

The 2012 source PDF may remain in the published media manifest without being linked from the HTML. This audit does not infer historical accuracy or reproduction rights from its presence. Seven synthetic negative mutations fail closed; a valid labelled embedded PDF with download fallback passes. An unrelated external PDF citation is ignored.

## Restrictions and acceptance

No OCR, document derivatives, source-media changes, article rewriting, private-draft access, original WordPress writes, Facebook, noindex relaxation, or public launch. **CHM-B040 safety-rejected historical CS12 operation remains prohibited; this is a read-only QA check and must not become a route to modify that article.** Reader-facing PDF accessibility and original WordPress fidelity still require manual assistive-technology and visual review. This audit neither repairs the seven textless pages nor establishes per-asset rights.

Candidate only until exact-final-branch CI, reviewed diff, merge and exact-main Vercel READY. READY exact main is DEPLOYED, never full LIVE_VERIFIED.
