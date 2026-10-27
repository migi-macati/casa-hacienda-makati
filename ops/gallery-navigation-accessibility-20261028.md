# Gallery navigation accessibility candidate — 2026-10-28

Scope: the two already-published WordPress galleries only, containing 3 and 7 images. The original WordPress site remains read-only. This change does not add or remove media, rewrite original attachment destinations, alter published article source text, grant media rights, change noindex, or touch private drafts.

The build injects a local CSS/JavaScript progressive enhancement into the two generated HTML routes after media bundling. Existing seven original WordPress attachment links remain available without JavaScript and with modified-click navigation. The three originally unlinked images gain keyboard-operable triggers. A native dialog supplies next/previous controls, image descriptions, Escape close and focus restoration. Source routes and alt attributes are fail-closed at build time.

Verification requires the existing full build and computed-CSS privacy workflow plus a new local-server Playwright desktop/mobile gallery interaction gate. The source content lock remains unchanged because only generated HTML is enhanced. Preview and production status must be checked separately; this document alone is not deployment verification.

Outstanding: original WordPress theme/visual parity, three untagged PDFs with seven pages lacking extractable text, native comments, external links, redirects, performance, rights and attribution. Highest state remains DEPLOYED, not FULLY LIVE_VERIFIED, until full acceptance.
