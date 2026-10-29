# Article reading-column parity adjustment — 2026-10-29 PHT

## Observed defect and bounded change

The independently executed original WordPress visual lab on 2026-10-28 reported that the migrated article's first long paragraph was about **208 px wider on desktop** than the original WordPress paragraph in sampled published articles. The migrated `.layout` uses a 1,150 px outer maximum with a 225 px sidebar, 45 px gap and 26 px side padding. This yields approximately 828 px of prose at wide desktop sizes, while the original measured prose was approximately 620 px.

Reduce the shared published-article/informational-page `.layout` outer maximum to **960 px**, retaining the existing sidebar, gap and padding. At desktop widths of 1,280 px or greater, the calculated prose width becomes approximately **638 px**, roughly 18 px wider than the prior WordPress sample. This is a deliberately limited typography/layout correction; it is not pixel-perfect WordPress parity and does not claim every source page has identical widths. The existing mobile single-column rule at 920 px remains in place.

## Acceptance and boundaries

Require the exact-head full build, desktop/mobile WCAG, original WordPress visual lab, production browser/media, PDF, offline media, external-link and heritage-inventory workflows before merge. Inspect the WordPress visual lab for published-route load, zero horizontal overflow and broken images; **its current CI workflow measures production, so the PR run against old production cannot prove the new CSS is deployed**. Verify the new CSS on exact-main READY deployment and measure postdeployment rendering in a subsequent independent live audit.

No article text, images, PDF, gallery behavior, media, WordPress content, four private drafts, noindex, rights, indexing or public-launch decisions change. The original WordPress global Newspack carousel, typography family, image placement and comments remain open parity gaps. CHM-B040's operation-specific rejected historical article edit must never be retried or bypassed.
