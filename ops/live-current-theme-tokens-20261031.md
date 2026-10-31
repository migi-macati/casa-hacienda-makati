# Independent live acceptance: current WordPress Gutenberg tokens (2026-10-31 PHT)

Scope: test the **already deployed** #129 CSS correction against the production origin using existing independent Chromium workflow. This is a QA repair and acceptance gate, not a change to public article content, stylesheet, theme, or original WordPress.

## Regression caught before release

The existing `scripts/audit-live-wordpress-recent-parity.py` retained assertions for **100px / 2px** separators and **36px** Cultural Significance heading padding. Those values were correct before #129 but became stale after its measured source-preserving correction. An independent live rerun would falsely reject the new production styling. The mandatory generated-site browser gate in #129 already checks the corrected values.

## Updated acceptance

* Source-lock the 15 original published HTML Git blobs (13 posts, two pages) **and** the reviewed stylesheet Git blob.
* Check all 15 published production routes at 375px and five key routes at 320px and 1280px, for **25 live Chromium visits**, with external origins aborted.
* On each of the 25 original separators, assert **min(168px, 13vw)** computed width and **1px solid** border. At 320/375/1280px the measured target is 41.6/48.75/166.4px, tolerance 0.8px.
* On Cultural Significance, assert responsive spacing-60 heading padding at the same three viewport widths; preserve 12 frames, original galleries, 76 text-color elements, 29 Olympia paragraph indents, five-row Land Bank table, About spacing-70, noindex HTTP header/meta, and no horizontal overflow.
* Reject obsolete 100px / 2px separators, missing separator/border, old 36px heading spacing, and existing color/privacy/source/overflow mutations. Persist a small production computed-style JSON artifact, without screenshots, image copies, draft metadata or external requests.

This independently verifies a **specific deployed Gutenberg repair**. It cannot establish original authoring-theme identity, complete current-theme pixel parity, manual screen-reader WCAG, PDF remediation, native comments, field Core Web Vitals, media reproduction rights, maps/then-and-now, or full migration acceptance.

Original WordPress remains read-only. Four private drafts, 82 media, 13+2 published source documents and noindex must remain intact. No CS12 historical operation or CHM-B040 safety rejection is retried, no Facebook, third-party rights, public launch, paid service or private-draft change. Require exact-head CI, reviewed PR, merge, authenticated exact-main READY deployment, and distinguish a live test of the preceding production from final-main live verification.
