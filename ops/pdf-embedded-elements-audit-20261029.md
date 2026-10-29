# Embedded PDF element coverage, 2026-10-29 13:35 PHT

## Observed gap and correction

The existing read-only PDF reader-link gate checked `<object data="...pdf">` but did not inspect PDF URLs inside `<iframe src="...pdf">` or `<embed src="...pdf">`. An unlabeled or unbundled iframe/embed could therefore bypass the PDF accessibility gate if introduced in a later build. This is a preventive test-coverage defect, not evidence that the current 17 published HTML routes contain either element.

The audit now applies the existing pinned-media, local-URL, accessible-name, same-block fallback, and noindex checks to all three PDF embedding elements. It records iframe/embed references in the existing PDF embed count. Valid labeled embeds with fallback links pass; for both newly covered element types, missing names, missing fallback links, and unbundled original WordPress PDF URLs fail closed in self-tests. The existing PDF anchor and object checks remain unchanged.

## Safety and acceptance limits

This change only modifies `scripts/audit-pdf-link-accessibility.py` and its tests, and adds this QA note. The existing PDF GitHub Actions workflow already invokes the script after the full build. It does not edit published articles (especially safety-rejected CHM-B040/CS12), original PDF bytes, WordPress, media inventory, private drafts, rights, robots/noindex, or public-launch settings. No OCR or PDF derivatives are created.

The three PDFs still require manual assistive-technology review and accessible alternatives; seven of nine pages have no extractable text. A passing automated gate is not PDF-UA/WCAG certification. This note is not a deployed release assertion until the branch passes exact-head CI, its diff is reviewed, it is merged, and production is confirmed READY at the new main SHA. Final-SHA independent rendered HTTP verification remains separate.
