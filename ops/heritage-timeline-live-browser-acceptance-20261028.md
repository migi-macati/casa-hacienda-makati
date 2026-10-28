# Independent deployed timeline browser acceptance (2026-10-28)

This test exercises the **currently deployed** four-entry homepage timeline using independent Chromium requests to the production alias. It does not change published history, media, original WordPress, drafts or rights.

## Acceptance and boundaries

- Eight browser contexts: 1280px desktop and 375px mobile; JavaScript disabled/enabled; reduced motion requested/not requested.
- Require HTTP 200, same-origin homepage, exact `noindex,nofollow`, unique H1, all 13 published article cards, one accessible named timeline region.
- Require ordered 1607, 1608, 1620, 1768 entries and both historical caveats; all four source links must use the two reviewed official NHCP marker registry URLs over HTTPS.
- Require four visible source links, keyboard Tab from first to second source link, no horizontal overflow, correct desktop/mobile menu, and no embedded timeline images, media or scripts.
- Save a JSON result and best-effort full-page screenshot per browser context in a seven-day Actions artifact. Screenshot failure is reported as unavailable and does not override passing browser interaction assertions; the initial element-only screenshot was unstable in Chromium despite all preceding assertions passing. Five fail-closed URL allowlist fixtures are exercised without browser/network calls.

**Not accepted by this gate:** original seventeenth-century deeds, independent historical accuracy of later marker claims, screen-reader announcements by a human, full WCAG conformance, field CWV/INP, the complete Casa Hacienda timeline, or any of the other six heritage features. A PR workflow tests whichever production SHA is live during its run; check the production deployment's exact main SHA separately. Do not mark the entire timeline LIVE_VERIFIED merely because this gate passes.

No changes to four private drafts, 82 media, noindex, original WordPress or public-launch rights. CHM-B040 historical CS12 operation-specific rejection remains untouched and must not be retried or bypassed.
