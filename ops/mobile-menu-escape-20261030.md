# Optional mobile menu Escape handling — 2026-10-30 PHT

## Scope
The 17 public routes retain their native no-JavaScript `<details>` navigation and existing first-focus skip link. A dependency-free deferred script closes the mobile menu on Escape only when the open menu contains keyboard focus, restores focus to its `<summary>`, and does not intercept Escape while a modal `<dialog>` is active. All five original navigation links, public content, article bodies, source media, PDFs, noindex, private drafts, and WordPress remain unchanged. No new third-party code or service.

## Acceptance
- `scripts/test-mobile-nav.mjs` executes the actual shipped browser script in an isolated DOM-like runtime and fails closed if the script reference is absent or duplicated.
- `scripts/audit-mobile-nav.py` preserves the existing 34 route/viewport checks with JavaScript disabled and adds one generated-site Chromium Escape/focus interaction with JavaScript enabled.
- Existing mandatory build, privacy, WCAG, WordPress visual, PDF, media, external-link, production-browser, and heritage CI must all pass at the exact final branch head. Preview and final diff require review before merge. Production remains DEPLOYED only after authenticated READY exact main SHA; the new Escape behavior needs independent live browser verification after deployment.
- The source-lock and four private drafts must not be modified. CHM-B040 historical CS12 safety-rejected operation remains prohibited and untouched.

## Limits
This is a focused keyboard improvement, not a manual screen-reader WCAG certification or full WordPress theme/carousel parity. The original WordPress site is read-only. Rights and public-launch decisions remain with the owner.
