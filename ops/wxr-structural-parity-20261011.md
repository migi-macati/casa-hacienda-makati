# WordPress WXR structural parity — 2026-10-11 23:37 PHT

**Source:** Owner-supplied `casahaciendamakati.WordPress.2026-10-10.xml` (WordPress export generated 2026-10-10 02:54 UTC). Parsed locally with XML namespaces, without publishing or copying the private export into this repository. Compared published records against current GitHub main HTML. This is an inventory and metadata check, **not full-text or visual parity**.

## Export counts
| WXR item type/status | Count | Disposition |
| --- | ---: | --- |
| Published posts | 13 | All 13 corresponding dated paths present in `public/`; each retains original-publication link and a visible original date in source. |
| Published pages | 2 | About and Cultural Significance paths present. |
| Editorial drafts | 4 | 1 draft post and 3 draft pages. Keep private; **draft titles and contents are deliberately omitted from this public audit**. |
| Attachments | 82 | Matches media manifest asset count; does not establish byte integrity, reuse rights, or alt-text completeness. |
| Exported `wp:comment` elements | 0 | No comments included in WXR. This does **not** independently verify live WordPress comment counts or subscriptions. |
| Total WXR `item` records | 115 | Includes WordPress themes/navigation/global-style records beyond public content. |

## Published post routes confirmed in GitHub source
| WordPress publication date | Article | Preserved route |
| --- | --- | --- |
| 2023-08-12 | Cultural Significance No. 1 | `/2023/08/12/cultural-significance-no-1/` |
| 2023-08-12 | No. 2 | `/2023/08/12/cultural-significance-no-2/` |
| 2023-08-12 | No. 3 | `/2023/08/12/cultural-significance-no-3/` |
| 2023-10-21 | History of Barrio Olimpia | `/2023/10/21/history-of-barrio-olimpia-makati-rizal/` |
| 2023-10-21 | No. 4 | `/2023/10/21/cultural-significance-no-4/` |
| 2023-10-21 | No. 5 | `/2023/10/21/cultural-significance-no-5/` |
| 2023-10-21 | No. 6 | `/2023/10/21/cultural-significance-no-6/` |
| 2023-10-21 | No. 7 | `/2023/10/21/cultural-significance-no-7/` |
| 2023-10-21 | No. 8 | `/2023/10/21/cultural-significance-no-7-2/` (original WordPress slug, retained intentionally) |
| 2023-10-21 | No. 9 | `/2023/10/21/cultural-significance-no-9/` |
| 2023-10-21 | No. 10 | `/2023/10/21/cultural-significance-no-10/` |
| 2024-02-06 | No. 11 | `/2024/02/06/cultural-significance-no-11/` |
| 2024-10-28 | No. 12 | `/2024/10/28/cultural-significance-no-12/` |

All 13 source HTML pages contain `<article class="content">`, the WordPress original-publication URL, the matching date text, and `noindex,nofollow`. Their checked-in `<title>` values are generic templates; `scripts/normalize-metadata.mjs` creates unique page titles and canonical URLs during build. Inspect built output rather than mistaking raw source for deployed metadata.

## Still unverified
1. Full text, caption, internal/external link, citation, inline media, footnote and postmeta parity for each published item.
2. Exported image bytes versus deployed files, attribution and reuse permissions, informative alt text, and mobile rendering.
3. Draft privacy in the deployed build, and whether live WordPress has comments absent from WXR.
4. Redirect behavior, live endpoints, search quality, browser accessibility, performance and security response headers.

**Safeguards:** No draft content or commenter information has been copied to this public repository. Keep WordPress and noindex intact until owner approval.
