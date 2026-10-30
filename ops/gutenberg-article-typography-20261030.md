# Published WordPress article typography | 2026-10-30 PHT

## Observed migration defect
The original published article HTML retains Gutenberg typography classes, but the migrated stylesheet defined only small/medium presets. The locked 13 article sources contain 12 extra-large and four large headings (12 of 13 routes), plus 72 small and eight medium instances. Without the large presets, the original emphasized article headings fall back to generic h2/h3 sizing. This is a source-preserving visual hierarchy repair, not a claim of exact original Newspack theme pixel parity.

## Implementation and acceptance
Scope large 28–36px and extra-large 32–42px responsive styles to article .content; preserve existing 14px small and 20px medium styles. Lock the stylesheet Git blob; add 11 fail-closed fixtures and mandatory build gate; verify actual computed font sizes, line heights and overflow in Chromium at 320/375/1280px on Cultural Significance Nos. 1, 11 and 12. All 13 original published article source files remain unchanged. Browser gate runs against the generated site; live exact-main acceptance remains separate.

## Limits
No media reproduction or per-asset rights decision, private-draft disclosure, original WordPress or Facebook operations, PDFs, native comments, noindex/public-launch change, or CHM-B040 retry. This does not close manual screen-reader WCAG, original carousel/theme parity, field CWV/INP or historical-source gaps.
