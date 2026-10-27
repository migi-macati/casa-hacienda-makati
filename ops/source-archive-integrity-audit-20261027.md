# Original source archive integrity and privacy-safe audit

Inspected **2026-10-27 ~21:43 PHT** against the owner's original WXR and media TAR. The original files were read-only; neither source archive nor any private-draft metadata is stored in this repository. Reproduce with `python scripts/audit-source-archive.py original.xml original.tar` using the original owner-supplied exports. The script uses Python's standard library, verifies the pinned original export SHA256 values, fails closed on unexpected paths or media signatures, and prints only aggregate counts.

## Verified original-source bytes

- WordPress XML SHA256: `7ca0c47f6435764ceaebb7a2a869546b72d8282c65503dae85bfc9e45a7cd00a`.
- Original TAR SHA256: `2b818bcd0fe0035342c5fce4c11477ed4550e726864df0171a040a135cc974a6`.
- **82/82 WXR attachment paths exactly matched 82/82 regular TAR members**; no missing, unexpected or duplicate paths. All 82 files passed magic-signature checks; 79 original images separately passed Pillow decoding in the local audit. Original bytes: **130,173,654**.
- Formats: **49 JPEG, 29 PNG, 1 GIF, 3 PDF**. The source archive contains **72 unique SHA256 payloads**, including **6 duplicate-payload groups** and **10 redundant duplicate files** representing **22,048,605 repeated source bytes**. Preserve all original 82 filenames and URLs until their references, attribution and archival value are reviewed.
- The earlier independent local conversion of **78 JPEG/PNG to WebP** succeeded using Sharp 0.34.1. Production pins Sharp 0.35.5, so **no deployed WebP byte-equivalence claim** is made.
- Original PDF accessibility remains incomplete: three PDFs are untagged, with **7/9 pages lacking extractable text**. No original was modified or OCR-published.

## New pinned source HTML checks

On GitHub main `38d0f224248cc52daccb3f18f56f12bb6c41e333`, all **17 source HTML files** retain `noindex,nofollow`. Across 92 `img` elements, **27 empty alt attributes** remain, concentrated in published historical articles; **zero linked images with empty alt** were found by the exact source-tag check. There are **44 source-note reference markers** in prebuild HTML. These source checks do not establish CSS-computed visibility, full alt suitability, restored footnote correctness or rendered production acceptance.

## Scope and evidence boundaries

This archive verifier is an **offline source-provenance audit**, not a production build gate or deployed browser test. It does not read private draft bodies, print draft-media relationships, establish rights, or prove that media are appropriate for public distribution. Original source duplicates do not authorize deletion. Deployed asset integrity, privacy, rendered 13+2 parity, accessibility, comments, search, redirects, security, performance and console acceptance remain outstanding.

Keep the original WordPress read-only, four drafts private, 82 media preserved, and noindex unchanged. CHM-B006 independent deployed browser/artifact access and CHM-B040 operation-specific GitHub safety remain unresolved. No heritage feature is marked DEPLOYED VERIFIED.
