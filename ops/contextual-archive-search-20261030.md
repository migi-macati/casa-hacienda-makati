# Contextual excerpts for published archive search | 2026-10-30

The homepage already searches the fail-closed index of 13 published articles and two pages, but article cards always showed fixed opening summaries even when a match occurred deep in an article.

This change shows a short text-only excerpt from the existing locked published article text around the first matching query term in each visible article card. The original summary is restored when the query clears, when only a title matches, or when the public index is unavailable. It does not modify article bodies, titles, media, PDFs, WordPress, private drafts or search-index provenance. Excerpts use textContent, never HTML injection or external search services. Historical spelling, accent and punctuation normalization is preserved.

The mandatory Chromium search/privacy workflow now checks a deep-body 1769 match, excerpt restoration, text-only rendering and the network-failure summary fallback at desktop and mobile widths. Existing 30 computed-visibility scans, 15-document source lock, 82-media integrity and noindex gates remain required. This is a search usability improvement, not WordPress carousel parity or historical verification.

CHM-B040 historical CS12 safety-rejected operation remains unchanged and must never be retried or bypassed. No new rights, public-launch authorization or privacy decisions are inferred. Full acceptance still requires WordPress fidelity, manual screen-reader/PDF checks, field CWV/INP and archival evidence.
