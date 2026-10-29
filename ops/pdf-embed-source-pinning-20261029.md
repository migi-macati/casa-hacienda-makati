# PDF embedded-reader source pinning — 2026-10-29 PHT

## Scope and evidence

The existing `scripts/audit-pdf-link-accessibility.py` checks published local PDF URLs, descriptive embedded-reader names, fallback links and noindex. Inspection of its parser found a bypass: a PDF embedded from an external HTTPS URL, protocol-relative URL, relative `.pdf` path or inline `data:application/pdf` URL returned no recognized local target and no error. A PDF reader declaring `type="application/pdf"` with a generic external viewer URL was likewise ignored. Such embeds could evade the local PDF inventory, fallback/accessibility gate and privacy expectations.

This patch fails closed for these PDF-signalled embedded-reader sources in `object`, `iframe` and `embed`, while preserving ordinary external scholarly PDF **anchor citations**. It adds eighteen targeted negative fixtures (six per embedding element) to the existing thirteen, alongside the three valid embedding fixtures. Unrelated non-PDF embedded media is outside this audit's scope; manual review remains required.

## Release and acceptance limits

This is a QA-only change, not a published content change, a PDF remediation, a source-byte transformation, a third-party rights decision or a claim of WCAG/PDF-UA certification. The existing three PDFs/nine pages, four private drafts, 82 media assets, noindex, and read-only original WordPress must remain unchanged. Never retry or bypass CHM-B040's operation-specific safety rejection or edit the original CS12 article to address PDF accessibility.

The latest verified baseline before this branch is main `e2892c70590b8928d7ce70cc9f64d0d9e905a573`, authenticated READY production `dpl_BHHrT963rpFYAXXZUdaTHoTJkz9S`. The PR branch is a candidate until exact-head CI, reviewed diff, merge and exact-main deployment. Independent direct final-SHA browser/robots verification, manual screen reader, original WordPress visual fidelity, native comments, real-user CWV/INP, fully air-gapped dependency installation, historical source provenance and owner rights/public-launch decisions remain outstanding.
