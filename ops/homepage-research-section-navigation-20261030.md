# Homepage research-section navigation | 2026-10-30 PHT

The homepage's evidence sections and archive were separated by a long scroll. This change adds one labeled, text-only contextual navigation directly after the hero. Six native fragment links target the existing timeline, sources, places, people, events and 13-article archive. Links have 44px minimum height, visible keyboard focus and scroll offset for the sticky header. They function without JavaScript. No new historical assertion, image, carousel, article, PDF, media asset or external link is introduced.

The mandatory production build now validates exact section identities, link labels and destinations, noindex, 13 article cards and accessible search status, with 11 fail-closed mutations. The existing search/privacy Chromium workflow tests all six fragment links by keyboard at desktop and mobile widths. This is a reader-facing homepage navigation improvement; it does not certify manual screen-reader usability, WordPress visual parity, archival identity or reproduction rights.

Original WordPress remains read-only; four private drafts, 82 media, noindex and launch restrictions are unchanged. CHM-B040's safety-rejected historical CS12 operation is not touched or retried. Only mark this DEPLOYED after exact-head CI, PR review, merge and authenticated exact-main READY production; full migration acceptance remains pending.
