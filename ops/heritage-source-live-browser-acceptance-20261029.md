# Independent deployed source-register browser acceptance — 2026-10-29

## Scope

The source-register homepage section was deployed from PR #62 at main `71864b11e8331429162478936eba87c468e55529`, production `dpl_E9YJqygcEntJZaM93hsUE6BMqYjc` READY. PR #62's previous production browser job ran before the source feature was merged; therefore its success alone did not independently accept the new live feature.

This PR adds a permanent read-only Chromium gate to the existing independent production acceptance workflow. It visits the **current production alias**, not a branch preview, and fails closed if the source section is absent. The gate checks 1280px desktop and 375px mobile, with JavaScript on/off and reduced-motion on/off (eight contexts). Each requires one named region, exactly three records in reviewed order, the exact three HTTPS institutional source URLs and one published research link, historical evidence-limit text, keyboard focus progression, no overflow, no embedded media, 13 article cards and noindex. It records JSON and optional full-page screenshots in a seven-day GitHub Actions artifact. The allowlist has six synthetic negative fixtures.

The source register remains a **partial** sources feature. Passing the browser gate is not a manual screen-reader test, verification of underlying seventeenth-century records, inspection of British Library Add MS 17641 C, clearance of image rights, or full heritage-feature acceptance. No WordPress write, media addition, private-draft write, public launch or safety-rejected operation is authorized.

## Release gate

Before merge: inspect the final PR diff, all exact-head workflows and the production-browser log/artifact; verify Vercel preview READY. After merge: verify authenticated automatic production READY at exact main SHA, and separately attempt independent production HTTP verification. If a DNS/network failure prevents live verification, record it explicitly and retain highest state DEPLOYED rather than FULLY LIVE_VERIFIED.

Existing CHM-B040 operation-specific safety restriction remains. Preserve four private drafts, 82 media assets, 13 published posts, two pages and noindex.
