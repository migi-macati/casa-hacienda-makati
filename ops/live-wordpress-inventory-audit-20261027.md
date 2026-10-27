# Live WordPress to GitHub inventory parity audit

**Inspected:** 2026-10-27 approximately 19:36 PHT. **Read-only evidence:** authenticated WordPress.com `posts.list`, `pages.list`, `media.list`, `comments.list` and GitHub `fetch_file` at exact main `200550c7bb493b744422dfd83a2e4c0eb26545ce`. Scope: Casa Hacienda only. This document records source and inventory evidence, **not** generated-site or browser acceptance.

## Verified source-route parity

- Original WordPress currently returns **13 published posts and 2 published pages**. All **15 original permalink paths** have corresponding `public/<path>/index.html` files at the pinned GitHub main SHA; zero missing routes in this audit.
- All 15 GitHub source files have one `article.content` container, retain HTML `noindex,nofollow`, and have an H1 matching the original WordPress title after entity normalization. This is a **source-level** comparison, not complete article text, media, citation, CSS, search-index or deployed-render parity.
- Source HTML post `<title>` fields can be generic before the build; the authenticated exact-main Vercel build previously reported a successful metadata-normalization step. No deployed-browser metadata inspection is claimed.
- The original WordPress lists all 13 posts with `comment_status=open`. The original comments listing returned **0 comments**. The static migration has no equivalent commenting interface, so functional parity remains pending. Do not invent historical comments.

## Verified media source inventory

- The **live WordPress media library returned 82 items** in one paginated response (82 total). The GitHub `media-manifest.json` at pinned main contains **82 assets** (blob `520bd32b49bbbc61fc44a05a4c3c26684f299481`).
- Normalizing only URL query strings, **all 82 WordPress media `source_url` values matched the manifest's 82 `source` values exactly**: **82/82 matched, 0 unmatched in either direction**.
- WordPress library MIME breakdown: **49 JPEG, 29 PNG, 1 GIF, 3 PDF**. This identifies source formats; the build's converted WebP outputs are separate.
- All **82 WordPress library `alt_text` metadata fields were empty**. Only **3 library captions** contained content in the queried response. This is not the same as HTML image alt text: the exact-main Vercel build separately reported **27 empty HTML alt attributes**, requiring contextual review.
- **Not verified:** source file byte hashes, original media TAR hash, all converted WebP provenance, ownership, license, third-party attribution, privacy of three draft-associated media, PDF accessibility, independent deployed media HTTP access. A matching source URL is **not** proof of any of these.

## Publication boundaries and next actions

The last confirmed production deployment is `dpl_CAoe8GVXXVDSk4piEP2yQDRiFx11`, **READY at exact main** `200550c7bb493b744422dfd83a2e4c0eb26545ce`; state **DEPLOYED, not FULLY LIVE_VERIFIED**. No WordPress, published HTML, private drafts, media, rights, robots or noindex settings were changed by this audit.

Next: independently compare article body text, dates, source notes, and rendered images against the 13+2 originals; verify actual deployed endpoints/browser; recover the original TAR for byte-level media provenance; classify alt text and rights asset by asset; determine whether linking back to WordPress comments is an acceptable migration bridge. Continue coherent search/privacy integration without publishing the incomplete route-only branch. CHM-B006 and operation-specific CHM-B040 remain unresolved. Owner decisions on media rights/privacy and public launch remain separate.

**Evidence status:** complete for the stated 82/82 URL inventory and 15/15 source-route/H1/noindex checks; incomplete for full migration acceptance. Keep the existing hourly automation enabled.
