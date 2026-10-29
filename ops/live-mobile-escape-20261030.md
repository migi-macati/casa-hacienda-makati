# Live mobile navigation Escape acceptance — 2026-10-30 PHT

QA-only follow-up to PR #97. The existing deployed mobile navigation uses native `<details>` and a small optional Escape handler. The prior acceptance exercised generated pages, not independently deployed behavior.

The permanent read-only production Chromium gate now verifies all 15 published routes, homepage and HTTP 404 at 375px. It requires exactly one visible native mobile disclosure, five original navigation links, the expected keyboard script, hidden desktop navigation, and initially closed state. It opens the menu, focuses an actual link, checks that a non-Escape key does not dismiss it, then presses Escape and requires closure plus focus restoration to Menu. Escape from outside the disclosure must not close it. It also exercises the native disclosure on the homepage with JavaScript disabled. Eleven synthetic negative fixtures fail closed.

No public content, media, rights, draft, original WordPress, noindex or launch changes. This is automated keyboard behavior acceptance, **not** manual assistive-technology or full WCAG certification. CHM-B040 historical safety rejection remains prohibited and was not retried. The original WordPress site remains read-only, four drafts private, 82 media and global noindex preserved.

Require exact-branch CI, reviewed diff, merge and exact-main production READY. A browser pass against previously deployed PR #97 content establishes live behavior of that content; this QA-only PR does not change public assets.
