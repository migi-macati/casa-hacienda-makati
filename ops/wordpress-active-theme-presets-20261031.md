# Current WordPress theme and Gutenberg design-token evidence — 2026-10-31 05:36 PHT

## Direct read-only evidence

The authenticated WordPress.com **read-only** site-editor context for `casahaciendamakati.wordpress.com` returned:

- `theme.active`: stylesheet `pub/twentytwentyfour`, display name **Twenty Twenty-Four**. This is the **currently active theme**, not proof of the theme used when the articles were originally authored or when a prior migration snapshot was captured.
- `theme.presets`: base `#f9f9f9`, base-2 `#ffffff`, contrast `#111111`, contrast-2 `#636363`, contrast-3 `#A4A4A4`, accent `#cfcabe`, accent-2 `#c2a990`, accent-3 `#d8613c`, accent-4 `#b1c5a4`, accent-5 `#b5bdbc`. WordPress default black is `#000000`.
- Theme spacing slug `60` is **`min(10.5rem, 13vw)`**. Default spacing slug `70` is **`3.38rem`**. Theme spacing `50` is `min(6.5rem, 8vw)`. These are not interchangeable with generic WordPress core fallbacks.
- The current theme declares **620px content width** and **1280px wide width**; `Inter` is its body family and `Cardo` its heading family. The global typography uses medium font size, line-height 1.55, and global block gap 1.2rem.
- The current `core/separator` block style specifies a **1px** solid bottom border, current text color mapped to contrast, and width `var(--wp--preset--spacing--60)` for ordinary separators. Current `core/gallery` sets bottom margin `var(--wp--preset--spacing--50)`.

Evidence retrieval: WordPress.com site-editor context, `theme.active`, `theme.presets`, and `theme.styles` GET operations, 2026-10-31 PHT. No site write, plugin change, media retrieval, private-content retrieval, or social action was performed.

## Implications for earlier migration repairs

1. `ops/gutenberg-spacing-presets-20261030.md` restored static-site `--wp--preset--spacing--60: 2.25rem` as a **generic core fallback**. That value is **not** the current WordPress theme's `60` token. The restored `70: 3.38rem` agrees with the current WordPress default `70`. Existing generated-site CSS/Chromium gates show that declarations resolve, but cannot certify **current-original visual parity**.
2. `ops/gutenberg-separator-parity-20261030.md` used a conservative fixed **100px/2px** separator. The current theme instead specifies `min(10.5rem, 13vw)` width and **1px** border. Neither value should be silently substituted until comparing the actual source-rendered page, including possible legacy inline/block styles and theme history.
3. `ops/gutenberg-text-colors-20261030.md` used local `primary`, `foreground`, and `black` fallbacks. The current theme's returned palette **does not define** `primary` or `foreground` slugs, even though those classes occur in locked article HTML. This is consistent with legacy markup but **does not identify** the historic authoring theme. Current WordPress default black `#000000` also differs from the migrated conservative `#111` fallback.
4. Prior notes repeatedly refer to “Newspack theme/carousel.” The read-only active-theme query establishes that **Newspack is not the current active theme**. A Newspack-related carousel may be a block/plugin/widget independent of the theme. Neither its provenance nor its asset reproduction rights is established by this query.

## Acceptance decision and safe next verification

Treat **currently active Twenty Twenty-Four**, **possible historic Newspack-related presentation**, and **source-locked legacy Gutenberg classes** as separate evidence layers. Do not retroactively declare earlier repairs wrong or exact. First compare original WordPress **rendered computed styles** and screenshots at 320/375/1280px on the exact published routes that contain `spacing--60`, separators, color classes and galleries. Capture theme stylesheet identity, element box dimensions, palette, fonts, gallery behavior and response date. Record whether current rendered WordPress still contains legacy class styling or plugin output. Only then propose an integrated, source-preserving CSS patch with exact-section mutation fixtures and generated-site and independent production Chromium verification.

This note documents a **new directly verified configuration fact**, not full visual parity, historical theme identity, source-text correction, rights clearance, or public-launch approval. No edits to original WordPress, 13 posts/two pages, four private drafts, 82 media, PDFs, rights, comments, Facebook, or noindex. No CHM-B040 historical CS12 operation or workaround. Do not count this research note as a deployed heritage feature. Vercel daily deployment quota was reported exhausted on 2026-10-31; do not force a deployment, retry the rejected operation, or treat a merged docs-only change as deployed without exact-main READY.
