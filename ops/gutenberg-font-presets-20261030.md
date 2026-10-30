# Published Gutenberg font-size parity | 2026-10-30 PHT

## Verified defect and scope
The two imported WordPress pages retain 26 `has-small-font-size` classes (14 About, 12 Cultural Significance) and one `has-medium-font-size` class. The migrated stylesheet did not define either Gutenberg preset. In particular, About's small uppercase LOCATION/NAME headings inherited the much larger generic article h2 size. This is a reader-facing presentation defect, not a source-text error.

## Repair and verification
Scope readable 14px/1.6 small text and 20px/1.55 medium text to published `.content` Gutenberg classes. Preserve original source markup, existing 50px About main-heading responsive fix, all 12 CTA controls, desktop columns, original media and links. Lock the new stylesheet Git blob in the published source manifest. Add mandatory build-time 10 fail-closed negative fixtures, and generated-site Chromium computed-style and overflow checks for both pages at 320px, 375px and 1280px. These checks cannot substitute for manual screen-reader testing.

## Boundaries
No original WordPress writes, private-draft edits or disclosure, Facebook requests, new media/image reproduction, PDF modification, public article text changes, rights authorization, noindex or launch changes. Four private drafts, 82 source media and 13 posts + two published pages remain protected. CHM-B040 safety-rejected historical CS12 operation remains untouched. This fixes only a measured Gutenberg font-preset gap; Newspack theme/carousel fidelity and full WCAG acceptance remain open.
