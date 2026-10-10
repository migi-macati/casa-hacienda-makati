# Casa Hacienda de San Pedro Macati — Comprehensive Website Assessment
Date: 2026-10-10 PHT. Status: preliminary evidence-based baseline, not final acceptance.

## Mission and scope
Document, interpret, and share the history and cultural significance of Casa Hacienda de San Pedro Macati; support informed conservation. Protect evidence integrity, avoid overstating contested claims, preserve original WordPress and keep noindex until owner approval. The site should work for a three-minute introduction, a thirty-minute exploration, and sustained scholarly research.

## Six audiences and their jobs
1. Residents/general public: understand what the Casa is, its location, importance, and current condition.
2. Historians, architects, heritage professionals: inspect primary evidence, citations, images, provenance, alternative interpretations.
3. Students/teachers: follow understandable chronology, maps, glossary, educational resources.
4. Agencies, conservation partners, stakeholders: see verified heritage significance, physical condition, conservation status, responsibilities and proposals.
5. Visitors, journalists, cultural tourists: find practical location and visiting constraints, fact sheets and media permissions.
6. Families, former residents, local contributors: submit recollections, corrections, photographs and evidence with consent and credit.

## Ten weighted dimensions (diagnostic estimates, 1–5)
| Dimension | Weight | Provisional score | Evidence and gap |
|---|---:|---:|---|
| Historical accuracy and scholarship | 20% | 2.5 | 13 substantial articles; 44 missing footnote targets in five articles; complete claim/source verification pending |
| Heritage storytelling and education | 15% | 2.5 | Intro and thematic articles exist; no clearly navigable chronology or educational pathways verified |
| Conservation and public engagement | 15% | 1 | Current condition, responsibilities and contribution pathways need dedicated verified treatment |
| Information architecture and usability | 10% | 3 | Home/About/Significance/archive and full-text search exist; audience task tests pending |
| Digital archive and media integrity | 10% | 2 | 82 bundled assets; item-level provenance, licensing, media endpoints and source fidelity not complete |
| Visual design and identity | 10% | 3 | Heritage-themed layout and mobile CSS; no independent device comparison completed |
| Accessibility and inclusiveness | 5% | 2 | Duplicate H1 fixed; audit found 54 empty alt attributes across 15 content pages; keyboard/contrast testing pending |
| Performance and technical reliability | 5% | 3 | Build QA and Vercel READY demonstrated; live browser, speed and all endpoints not independently verified |
| Search visibility and outreach | 5% | 2 | Search index exists; intentional noindex/robots block; SEO readiness not accepted |
| Governance and sustainability | 5% | 2 | GitHub/Vercel and checkpoint in place; editorial standards, provenance review and durable update workflow need documentation |

Weighted indicative score: 45.5/100. These are editorial judgments, NOT benchmarked measurements. No final historical, accessibility, performance or SEO certification.

## Evidence baseline
- Repository: migi-macati/casa-hacienda-makati. Build pipeline runs media bundling, search-index generation and structural QA.
- Verified preview QA: 17 HTML files (including 404), 13 posts, 82 media assets, 475 local links, 92 image elements, 54 empty alt attributes; audit is structural only.
- PR #6 QA merge 4e9f58b9ce9cf9251d272facc0256a61aa8d3578 matched Vercel READY production dpl_EvZsgEFGvbRwaNLV3vPdpytgBxeU.
- WordPress homepage offers 12 thematic significance stories and a historical overview; new homepage exposes 13 original posts as cards. Full source-by-source comparison remains incomplete.
- Five articles reportedly have 44 broken same-page footnote references (CS1 4, Barrio Olimpia 4, CS10 13, CS11 14, CS12 9). Audit script currently checks absolute-root local paths, not same-page #fragments.
- Direct public rendering of new Vercel domain was inaccessible to the assessment tool; do not interpret this as site downtime.
- README correction PR #7 preview READY at SHA 05b323d77be9cbbd72d3bbe1b9a865c0930017a1 at assessment time; merge state must be checked fresh.
- Original WordPress remains the comparison reference. Drafts must remain private. noindex stays until owner decision.

## Prioritized improvement backlog and acceptance tests
### P0 — Migration defects and evidence integrity (release blockers)
| ID | Improvement | Observable acceptance | Owner |
|---|---|---|---|
| CHM-M01 | Restore 44 footnote destinations and exact source notes | All 44 #references resolve to matching original notes; source text checked against WordPress; automated fragment audit passes | Automation |
| CHM-M02 | Extend build QA to fragment IDs, duplicate IDs and invalid internal anchors | Build fails on intentionally broken test fixture; all 15 migrated content pages pass | Automation |
| CHM-M03 | Full 13-post/2-page migration parity | Per-page comparison worksheet: text, title, date, permalinks, figures, captions, outbound links, citations, metadata; zero unexplained discrepancies | Automation |
| CHM-M04 | Inventory and test 82 assets | Manifest with source, generated path, size/checksum, verified HTTP status and decoded image, provenance/rights/credit; all deployed paths valid | Automation + owner rights |
| CHM-M05 | Preserve drafts and investigate comments | Four drafts absent from public build/search/sitemap; comment export and disposition documented | Automation |
| CHM-M06 | Validate old URL behavior and external dependencies | 13 post and 2 page old/new URL matrix; no broken internal navigation, no unintentional attachment links to WordPress; redirects only where authorized | Automation |
| CHM-M07 | Verify production browser behavior | Exact production SHA READY plus actual mobile/desktop navigation, search (body-only query), images, console and network checks | Automation |
| CHM-M08 | Rights and release gate | Attribution/permissions worksheet resolved by owner; old WordPress remains online; noindex removed only on explicit owner sign-off | Owner |

### P1 — Essential heritage functions (mission-critical, after source integrity)
| ID | Improvement | Observable acceptance | Owner |
|---|---|---|---|
| CHM-H01 | Public-facing introduction and timeline | First-time visitor can answer what/where/why/current status; chronology has cited dated events and links to articles | Editorial |
| CHM-H02 | Explain Olympia Casa versus Poblacion Oficinas | Separate documented identities, maps, source quotations and clearly labeled inference/uncertainty | Editorial |
| CHM-H03 | Research and source library | Each primary item has date, creator, archive/source, rights, transcription where available, and links to claims | Editorial |
| CHM-H04 | Conservation status and options | Dated evidence, present condition, known stakeholders and constraints, proposed vs approved actions clearly differentiated | Editorial + owner |
| CHM-H05 | Responsible contribution process | Tested contact/submission channel, consent and image-rights fields, editorial review and correction procedure; no exposed private data | Owner + build |
| CHM-H06 | Accessibility and mobile usability | Contextual alt audit for all images; WCAG-oriented keyboard/contrast/heading/form checks; phone test matrix passed | Build |
| CHM-H07 | Search and findability | Full-text query tests, zero-results behavior, descriptive titles, contextual navigation, article-to-source pathways | Build |

### P2 — Longer-term enhancements
| ID | Improvement | Observable acceptance |
|---|---|---|
| CHM-L01 | Interactive historic maps and location overlays | Every map layer dated, sourced and clearly distinguished from conjecture |
| CHM-L02 | Historical photograph comparison and architecture gallery | Images captioned, credited, accessible, zoomable and chronologically organized |
| CHM-L03 | Classroom resources, glossary and guided reading | Tested with at least one student and teacher; source links intact |
| CHM-L04 | Oral histories and community collection | Consent, withdrawal, attribution and moderation policy implemented |
| CHM-L05 | Public conservation updates | Dated changelog, cited decisions and transparent status |
| CHM-L06 | Sustainable publishing and backups | Documented editorial roles, automated checks, recovery rehearsal, exportable data |
| CHM-L07 | Performance and design benchmark | Mobile Lighthouse/Web Vitals and task-based comparison with WordPress; measured improvements, no regressions |

## Assessment methodology and decision gates
- Baseline: repo source, WordPress originals, Vercel deployment SHA and logs. Label each finding VERIFIED / INFERRED / NOT TESTED.
- Test representative journeys for all six audiences on small-screen Android, desktop, keyboard and screen reader.
- Preserve historical text during technical migration; substantive corrections require primary/credible secondary evidence and an editorial change log.
- Gate A (migration): all P0 automation tests pass, remaining rights/owner decisions explicit.
- Gate B (heritage usefulness): P1 tasks pass audience journey tests and source-review requirements.
- Gate C (public launch): owner approves rights, conservation representations and indexing. Noindex and original WordPress stay unchanged until then.
- Score again after direct browser, content fidelity and real-device tests. Do not equate a READY deployment with acceptance.

## Research completeness and 100/100 quality target (2026-10-10)
The 100/100 objective is a measured website readiness and evidence-governance target, NOT a claim that historical knowledge can be exhausted. The provisional scholarship 2.5/5 is a site/publication assessment; it is not a quantified fraction of all surviving archival records. Do not equate published article count with research completeness.

### Research coverage audit (status: unverified until source inventory)
- Property chronology and landholding: identify Jesuit estate administration, transfer/ownership chains, parcels and documentary chronology; resolve which references concern the Olympia Casa versus Poblacion Oficinas.
- Architecture and material fabric: plans, typology, alterations, historic photographs, 1910 versus 1926 reconstructions, evidence for dates and original features.
- Geography and cartography: 1775 Dionisio Kelly map and later cadastral/historic maps; georeferencing confidence and boundaries.
- People and labor: tenants, workers, residents, religious orders, family networks and social/economic functions, including perspectives absent from elite institutional records.
- Economic and institutional history: hacienda production, tenancy, local administration, later uses (factory, hospital, orphanage etc.) with separate evidence assessments.
- Heritage significance and comparative context: authenticity, integrity, rarity, comparable surviving casas, criteria used in significance claims.
- Condition and conservation: 2018 fire evidence, present condition, ownership/stewardship, engineering assessments, heritage designations, legal constraints and feasible restoration options.
- Public memory and oral history: ethically gathered recollections, informed consent, provenance and corroboration.
- Source provenance: full bibliographic details, archive/collection/call numbers, manuscript versus transcription, image rights, access URL, reliability and relevant quotations.
- Historiography and uncertainties: contradictory dates, identity claims, translation differences, alternative interpretations and explicitly unresolved questions.

### Research quality acceptance criteria
R01: Inventory every currently cited source in all 13 articles and 2 pages with stable source ID, citation occurrence, repository/archive, date, creator, type, link or call number, access/rights and verification status.
R02: Restore all 44 missing footnotes, audit every internal citation anchor and external source URL; record dead-link substitutes without silently replacing bibliographic references.
R03: Build a claim-to-source matrix for every consequential historical assertion, distinguishing primary documentation, secondary scholarship, inference and oral testimony; unresolved claims labeled.
R04: Cross-check major chronological, geographic, ownership and building-identity claims with independent evidence where feasible; document conflicts and negative findings.
R05: Source-index maps and historical photos with captions, approximate dates, creators, holdings, transformations, permissions and uncertainty.
R06: Create a public, accessible bibliography, chronology, research methods and corrections/change-log pages, with contextual links from the articles.
R07: Publish a clearly sourced conservation dossier with date-of-observation, evidence, missing surveys and explicit distinctions between proposals and official decisions.
R08: Maintain a prioritized unanswered-questions register with next archives/institutions to consult, progress and provenance of each new finding.
R09: External scholarly/heritage review of high-stakes conclusions where practicable, with recorded responses and corrections.
R10: Each source-supported published claim is reproducible from a cited record or transparently labeled as inference; zero known broken citation anchors or unacknowledged source discrepancies.

Research backlog priority: R01–R03 and R05 are P0/P1 source-integrity work; R04, R06–R08 are P1 heritage scholarship; R09–R10 are ongoing quality gates. Continue substantive research without delaying independent migration QA. Missing or inaccessible archives are documented limitations, not invented certainty.
