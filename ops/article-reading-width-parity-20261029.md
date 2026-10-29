# Article reading-column parity adjustment — 2026-10-29 PHT

## Observed defect and bounded change

The independently executed original WordPress visual lab on 2026-10-28 reported that the migrated article's first long paragraph was about **208 px wider on desktop** than the original WordPress paragraph in sampled published articles. The migrated `.layout` uses a 1,150 px outer maximum with a 225 px sidebar, 45 px gap and 26 px side padding. This yields approximately 828 px of prose at wide desktop sizes, while the original measured prose was approximately 620 px.

Reduce the shared published-article/informational-page `.layout` outer maximum to **960 px**, retaining the existing sidebar, gap and padding. At desktop widths of 1,280 px or greater, the calculated prose width becomes approximately **638 px**, roughly 18 px wider than the prior WordPress sample. This is a deliberately limited typography/layout correction; it is not pixel-perfect WordPress parity and does not claim every source page has identical widths. The existing mobile single-column rule at 920 px remains in place.

## Acceptance and boundaries

Require the exact-head full build, desktop/mobile WCAG, original WordPress visual lab, production browser/media, PDF, offline media, external-link and heritage-inventory workflows before merge. Inspect the WordPress visual lab for published-route load, zero horizontal overflow and broken images; **its current CI workflow measures production, so the PR run against old production cannot prove the new CSS is deployed**. Verify the new CSS on exact-main READY deployment and measure postdeployment rendering in a subsequent independent live audit.

No article text, images, PDF, gallery behavior, media, WordPress content, four private drafts, noindex, rights, indexing or public-launch decisions change. The original WordPress global Newspack carousel, typography family, image placement and comments remain open parity gaps. CHM-B040's operation-specific rejected historical article edit must never be retried or bypassed.

## Completed local computed-visibility review (2026-10-29 ~21:43 PHT)

Executed Chromium 10-context synthetic layout smoke with JavaScript disabled and reduced motion: 1,280/960/920/710/375 px × original and revised exact `.layout` selector/breakpoint rules. At 1,280 px, article prose narrowed from **828 px to 638 px** (−190 px). At 960, 920, 710 and 375 px, computed prose widths remained unchanged. All ten contexts retained visible paragraph text, an available source link, and no horizontal overflow. This is a **local computed-style fixture**, not a full-page WordPress or deployed screenshot comparison; see local `/mnt/data/chm_reading_column_computed_review_20261029.json`.

The required `ops/published-search-sources.json` stylesheet Git blob attestation is updated from the old CSS blob to `d3a48ff18168f95ec1dae1a0676f22d51718f8c9` **after this visibility review**. The 15 published HTML source hashes and route closure are unchanged. This satisfies the intended CSS-change review gate without disabling, weakening or bypassing it.
