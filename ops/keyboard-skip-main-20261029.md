# Keyboard skip-to-main accessibility and CSS visibility review — 2026-10-29

Scope: only the generated navigation enhancer, synthetic navigation tests, read-only browser acceptance, stylesheet and the exact stylesheet source lock. This feature adds a **Skip to main content** link as the first keyboard stop on all 17 generated public HTML routes, including the 404 page, with a programmatically focusable main landmark. It works with JavaScript disabled.

## Computed-visibility and privacy boundary

The reviewed stylesheet diff adds only `.skip-link` and `#main-content` selectors. The skip link is translated above the viewport while unfocused, and becomes visible at a fixed top position when focused, with a 44px minimum target, visible outline, and high stacking order. The main landmark receives only `scroll-margin-top` for sticky-header clearance. No existing article, private-draft, navigation, search-index, image, PDF, or content selector is changed. No new `display:none`, `visibility:hidden`, `opacity:0`, `aria-hidden`, or `inert` is introduced for any content. The source stylesheet SHA is explicitly repinned to `190f1691ec8fb032acf075e17b5bdefdd8603f07` after reviewing this exact diff; this is an authorized accessibility change, not a bypass of search/privacy source closure.

The required generated-site Chromium gate now checks all 17 public routes at 1280px and 375px, JavaScript disabled, first Tab focus, visible in-viewport skip target, Enter fragment navigation, focus transfer to main, five unchanged navigation destinations and noindex. Mandatory source lock, full build, axe WCAG, PDF, WordPress visual, media and independent production-browser workflows must pass on the exact PR head before merge. This file is a candidate record until merge and authenticated exact-main deployment.

No original WordPress writes, no original published article/PDF edits, no rights-uncertain media reuse, no changes to four private drafts, 82 media or noindex. CHM-B040 rejected historical CS12 operation remains prohibited. This change does not resolve original WordPress global carousel parity, manual screen-reader acceptance or full archival acceptance.
