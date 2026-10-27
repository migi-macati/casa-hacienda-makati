# Published-link semantics and accessibility repair — 2026-10-28

Scope: three already published WordPress articles, the build's structural audit, and synthetic regression tests. No historical assertions, media rights, original WordPress content, noindex, draft data or public-launch settings changed.

The source markup contained two empty `<a></a>` elements and 15 visually labeled family names rendered as anchors without `href`. The empty anchors were removed; the family labels became noninteractive `<span>` elements with the same classes and visible text. The original visible text of all three articles was compared before and after and remained identical.

The build now tests for missing/empty anchor destinations, executable/data URL schemes, and missing `noopener noreferrer` on new-window links. Ten synthetic cases cover valid and invalid anchors. The published-source Git blob lock is updated atomically with the HTML and test changes. The full build, computed-CSS, and production browser workflows remain the final merge gates.

This does not resolve the separate three inherited HTTP PDF citations, WordPress carousel/gallery parity, inaccessible PDF contents, media rights, native commenting, redirects or historical accuracy. Highest state remains DEPLOYED until independent acceptance.
