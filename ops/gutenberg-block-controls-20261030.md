# Gutenberg published block controls | 2026-10-30 PHT

## Observed source and defect

The locked published Cultural Significance WordPress page contains 12 Gutenberg `wp-block-button__link` anchors, 37 `has-text-align-center` markers, and 12 100px spacers. The imported static stylesheet did not supply WordPress block-theme styles for those button and alignment classes. Consequently, the original editorial CTA treatment and centered headings were absent even though source links and text survived. The large imported spacers also waste substantial vertical space on narrow screens. This is a source/style diagnosis; it does not claim a pixel-identical comparison against the original Newspack theme.

## Implemented scope and verification

The shared stylesheet now restores centered Gutenberg text and figures, provides visible 44px-minimum CTA controls with keyboard focus and hover affordances, and caps only the original 100px Gutenberg spacers to 36px at <=710px. Desktop spacers remain 100px. The 12 original published CTA hrefs and source page HTML are unchanged. The reviewed CSS Git blob is updated in the existing 15-document source lock. A mandatory build gate checks the 12 buttons, 12 spacers, source lock, noindex and 12 fail-closed CSS mutations. Generated-site Chromium tests actual buttons, focus, alignment, spacer heights and overflow at 320/375/1280px.

This is a limited reader-facing WordPress block parity improvement, not full Newspack/carousel fidelity, native comments, manual WCAG certification or a screen-reader test. No image reuse, external WordPress write, PDF alteration, public launch, rights grant or private-draft disclosure. Four private drafts, 13 articles plus two pages, 82 media and noindex must remain unchanged. CHM-B040 rejected historical CS12 operation is not touched or retried. Release only after exact-branch CI, reviewed diff, merge and exact-main production READY; independent final-main live-browser acceptance remains a separate requirement.
