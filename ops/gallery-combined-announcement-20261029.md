# Gallery combined screen-reader announcement | 2026-10-29 PHT

Scope: two existing published galleries (3 and 7 images). When navigating, a single polite atomic status now contains both the current position and the original figure caption, or the existing image alt text when no caption exists. The visible position heading remains the dialog title but is no longer a second live region. Keyboard instructions mention Escape. The image retains conditional aria-describedby only for distinct source captions.

Validation: mandatory offline shipped-JavaScript runtime regression in this release. The existing independent production Chromium gate must continue to test the **currently deployed baseline** during this feature PR; update that gate in a separate QA-only follow-up **after** this feature is deployed, to avoid a false failure against old production. Full CI, reviewed diff and exact-main READY deployment required. This is automated semantic acceptance, **not** a manual screen-reader test or global WordPress Newspack carousel/theme parity.

No article body, original WordPress, private drafts, media bytes, PDF, noindex, rights or public launch changes. CHM-B040 safety-rejected historical operation remains untouched and must never be retried or bypassed. Four private drafts, 82 media assets and noindex remain protected.
