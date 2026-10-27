# Independent deployed HTTP acceptance — 2026-10-28 01:37 PHT

Scope: production alias `https://casa-hacienda-makati.vercel.app`, GitHub main `4fdcaa976153ae6baeee80f0b56a49e12ea5d9f4`, Vercel production `dpl_HhYbqZVvaosNX6pr7dKMamg1ZXak` READY at exact SHA and GitHub Vercel CI SUCCESS. Read-only requests through the authorized Vercel deployment URL fetcher. Independent live HTTP checks, **not** browser-rendered fidelity or full launch acceptance.

## Observed HTTP results

- `/search-index.json`: HTTP 200; **15 unique routes** (13 articles, two informational pages); nonempty titles and texts.
- All **15 published routes**: HTTP 200, HTML, nonempty H1/title, exact production-alias canonical, `noindex,nofollow`, no missing/empty image alt. Their 76 images all have nonempty alt. All 13 article pages contain original WordPress discussion bridges; **44** restored source-note list items across the articles.
- Homepage: HTTP 200, noindex, exact canonical, nonempty H1/title; 15 images with nonempty alt.
- Explicit `/404.html`: HTTP 200 and noindex; this **does not** establish the status of nonexistent routes.
- `/robots.txt`: HTTP 200, `User-agent: *` and `Disallow: /`.
- `/media-integrity.json`: HTTP 200, schema 1, **82 unique asset paths**, positive lengths and SHA256-formatted digests. This checks published inventory structure, not independently served bytes.
- Four sampled WebP assets and all three PDFs: HTTP 200, matching content types, WebP/PDF signatures and `Content-Length` equal to the published integrity manifest. Sampled responses have HSTS, `nosniff` and `X-Frame-Options: SAMEORIGIN`. The connector text-decodes binary responses, so **served-media SHA256 equality remains unverified**.

## Routes independently checked

`/2023/08/12/cultural-significance-no-1/`, `/2023/08/12/cultural-significance-no-2/`, `/2023/08/12/cultural-significance-no-3/`, `/2023/10/21/cultural-significance-no-10/`, `/2023/10/21/cultural-significance-no-4/`, `/2023/10/21/cultural-significance-no-5/`, `/2023/10/21/cultural-significance-no-6/`, `/2023/10/21/cultural-significance-no-7/`, `/2023/10/21/cultural-significance-no-7-2/`, `/2023/10/21/cultural-significance-no-9/`, `/2023/10/21/history-of-barrio-olimpia-makati-rizal/`, `/2024/02/06/cultural-significance-no-11/`, `/2024/10/28/cultural-significance-no-12/`, `/about/`, `/cultural-significance/`.

Media samples: `/media/2022/06/casa-principal-colored.webp`, `/media/2022/06/casa-principal-with-fhl-watermark.webp`, `/media/2023/10/cs-7.6.webp`, `/media/2024/10/1000000268.webp`, `/media/2024/04/2009-120.pdf`, `/media/2024/04/2009-174.pdf`, `/media/2024/04/2012decision_ebcaseno_12-12-275_december.pdf`.

## Acceptance boundary

**CHM-B006 narrowed:** Authorized deployed HTTP access is now demonstrated, and 15/15 published routes pass basic independent HTTP acceptance. Browser-computed CSS, rendered original WordPress fidelity, mobile/console/a11y, navigation behavior, redirects, and deployed media byte parity are still outstanding. Do not mark CHM-B006 fully resolved or heritage features `DEPLOYED VERIFIED` on HTTP-only evidence.

**Search/privacy still unsafe:** The deployed index currently lists exactly the 15 published routes, but the generator still has synthetic fail-open unauthorized-route, CSS-hidden text, extra-class fallback and missing-noindex cases. Do not merge the partial route-only branch. Require coherent prebuild source/route closure, computed-CSS browser visibility, postbuild privacy audit and reproducible full build before publishing a replacement.

**CHM-B040 unchanged:** Earlier operation-specific GitHub safety rejection on CS12 correction; never retry or bypass. Media rights/attribution/privacy and noindex/public launch remain owner decisions. Original WordPress remains read-only, four private drafts private, all 82 media retained. No private draft metadata or associations disclosed.

This audit is a new independent HTTP acceptance result; it does not modify source content, indexing policy or media.