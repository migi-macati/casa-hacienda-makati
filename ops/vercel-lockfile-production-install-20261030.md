# Vercel production installation from committed npm lock — 2026-10-30 PHT

## Defect and correction
The repository committed its audited npm v3 lockfile in PR #95, and GitHub Actions used `npm ci`, but `vercel.json` still specified `npm install`. That allowed the production installation to resolve or rewrite dependencies independently of the committed lock. The production install command is now `npm ci --no-audit --no-fund`. The first production build step also runs the existing registry/cryptographic lockfile audit, which now fail-closes on an unexpected Vercel install/build/output configuration. Eight synthetic Vercel-config mutations are rejected in addition to the existing lockfile negative fixtures.

## Verification required before acceptance
Require all eight exact-head CI workflows, including the full static build and the existing warm-cache network-isolated media rebuild, reviewed final diff, successful preview and squash merge, and authenticated production READY at the exact merged main SHA. A READY deployment establishes DEPLOYED only. It does not establish manual screen-reader or original WordPress parity.

## Boundaries
This does not make npm cold-start air-gapped: initial npm package downloads, native Sharp binaries and the Docker image still require independently verified availability. No original WordPress write, published article/page rewrite, PDF/media/private draft change, image reproduction, noindex change or public-launch decision. Four private drafts, 82 media and the 13+2 published-route closure remain protected. CHM-B040 historical CS12 rejection is not retried or bypassed.
