# Live historical-search production verification — 2026-10-30 PHT

## Scope and rationale
PR #100 shipped published-only homepage search normalization for Macati/Makati, diacritics and hyphen/space punctuation. Its generated-site Chromium tests passed, but the exact-main production behavior had not been independently tested. This release extends the **existing** read-only production Chromium/media acceptance gate to exercise those same reader-facing queries against the deployed homepage at 1280 and 375 px.

## Fail-closed acceptance
The production gate first checks the existing SHA-attested published index (13 articles and two pages), noindex HTTP and HTML directives, all 82 media hashes and existing article/keyboard/gallery checks. It now verifies Macati/Makati, Haciénda/Hacienda and bahay-na-bato/bahay na bato return identical nonempty published results; unmatched and punctuation-only queries return zero with a visible notice; clearing the input restores exactly 13 article cards and hides page matches. All returned URLs must belong to the 15 published routes, without duplicates or search-fallback errors. Ten synthetic negative mutations cover unexpected routes, duplicates, missing index, privacy regression and incorrect empty/no-match behavior.

## Boundaries
This is independent production QA of existing search, not semantic search, a source rewrite, WordPress theme parity, rights authorization, screen-reader certification or full migration acceptance. No published article/page body, PDF, image, private draft, original WordPress site, noindex policy or public launch state is changed. CHM-B040 safety-rejected operation remains prohibited. Require reviewed exact-head CI, squash merge and authenticated exact-main READY deployment before recording DEPLOYED; direct browser checks cover only the current production alias.
