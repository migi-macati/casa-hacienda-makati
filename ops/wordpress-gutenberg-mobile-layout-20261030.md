# Published Gutenberg responsive layout repair | 2026-10-30 PHT

## Observed source issue and scope

The two published WordPress informational pages retain Gutenberg desktop inline layout declarations in their locked source HTML. The About page includes `padding-right:80px;flex-basis:66.66%` on a column and an inline `font-size:50px` heading. The Cultural Significance page includes `flex-basis:33.33%` columns. The existing responsive site stylesheet previously used `.content .wp-block-column{flex:1;min-width:200px}` without a mobile override for those inline desktop dimensions. On narrow viewports, the fixed gutter takes a substantial share of available reading width. This is a source-code diagnosis, not a claim of independently measured prior live Core Web Vitals.

## Integrated fix and acceptance

At widths at or below 710px, the shared published stylesheet now gives imported Gutenberg columns full available width, clears fixed inline left/right padding, and scales the About page's specifically identified 50px inline heading. Desktop WordPress spacing and heading sizing remain untouched. The stylesheet Git blob is updated in the existing 15-document published search source lock; no article or page HTML, media source, PDF, archive metadata or search text changes.

The mandatory build runs a dedicated 12-mutation fail-closed responsive layout test. The existing generated-site Chromium search/privacy workflow now checks the actual About and Cultural Significance pages at 320px and 375px for column gutter removal and horizontal overflow, plus a desktop 1280px check that the original 80px gutter and 50px heading remain. Passing these automated checks does not constitute manual screen-reader review or full original Newspack visual fidelity.

Original WordPress is read-only. All 13 articles, two pages, four private drafts, 82 media, noindex and owner media rights/public-launch decisions remain unchanged. No original carousel images or unauthorized derivatives are reproduced. CHM-B040's rejected historical CS12 operation is not touched or retried. Count the change as DEPLOYED only after final-head CI, reviewed diff, merge and authenticated exact-main READY production. Manual WCAG, native comments, PDF accessibility, carousel fidelity, real-user performance and archival identity remain pending.
