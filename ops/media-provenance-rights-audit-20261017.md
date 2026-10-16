# Media provenance and rights review (draft)

Prepared 2026-10-17 07:39 PHT. Read-only audit of `media-manifest.json` blob `520bd32b49bbbc61fc44a05a4c3c26684f299481`.

## Manifest evidence
- 82 unique output paths and 82 unique HTTPS WordPress upload source URLs; no duplicates or blanks.
- 49 original JPEG, 29 PNG, 3 PDF, 1 GIF; outputs 78 WebP, 3 PDF, 1 GIF.
- 78 JPEG/PNG files marked for conversion; all 82 original source URLs can be reconstructed exactly from the output relative path and original extension.
- Zero of 82 entries contains explicit rights holder, license, permission, attribution, required credit or authenticated original-byte SHA256. Missing metadata is **not** proof of infringement.
- Filename-only triage: two `watermark` entries, seven likely Barrio Olimpia report scans, three PDFs. These labels require manual confirmation; no license or attribution inferred.

## Outstanding acceptance
For each asset record original file byte count and SHA256 from an independently preserved full-resolution original, creator/rightsholder, permission/license, required credit, dimensions or PDF pages, and actual usage. Separately identify the 24 reported unreferenced archival-only assets by comparing article references; do not infer that set from filenames. Test full-resolution readability of seven report scans.

Generated output hashes matching across three deployments show output stability only. Current clean builds attempt an obsolete Vercel mirror and fall back to WordPress. An independently approved original archive and pin is still required; switching to a mutable production alias would risk circular builds.

**Editorial safeguards:** Keep WordPress unchanged; do not change private drafts, HTML noindex, or robots Disallow:/; rights/readiness signoff remains an owner decision. This is a research checkpoint, not publication clearance.
