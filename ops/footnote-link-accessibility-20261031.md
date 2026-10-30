# Original No. 10 footnote link accessibility — 2026-10-31 PHT

## Observed defect

The source-locked published Cultural Significance No. 10 contains 13 WordPress footnote references. Four two-digit numbers are split by markup: the hyperlink contains only “1”, while the trailing 0/1/2/3 is outside the link. The visible reference looks like 10–13, but its keyboard target and screen-reader link name cover only the first digit. This is a real generated-reader accessibility defect, independent of the historical claims.

## Bounded repair

After restoring the original 13 source-note destinations, the build now repairs only the generated No. 10 HTML. It keeps the original visible numbers and source-note UUID targets, puts the full two-digit number inside each link, and gives all 13 reference links descriptive programmatic names (“Go to source note N”). The original published article Git blob, historical text, note contents, backlinks, media and PDFs remain unchanged. No. 12 and its historical CHM-B040 safety-rejected operation are untouched. The source WordPress site remains read-only.

Mandatory tests pin the original source blob, verify the 13 original ordinals and four split links, reject 11 negative mutations, and verify idempotence. Generated-site Chromium checks accessible link names, all 13 note destinations/backlinks, keyboard activation, noindex and no overflow at 320/375/1280px, with JavaScript disabled and external requests aborted. These checks are **not** a manual screen-reader certification or full WCAG/PDF remediation. Require nine exact-head workflows, reviewed diff, preview READY, merge and exact-main production READY before calling this DEPLOYED. Final-production independent browser verification remains a separate gate.

Four private drafts, 82 media assets, 13 posts and two pages, noindex, rights and public-launch decisions remain unchanged. Do not retry or bypass CHM-B040.
