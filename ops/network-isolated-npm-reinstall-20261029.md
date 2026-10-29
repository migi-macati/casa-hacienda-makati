# Network-isolated npm reinstall acceptance — 2026-10-29 PHT

## Defect addressed
The existing offline media reproducibility workflow proves a second generated-site build uses only previously cached **WordPress media**, and that generated files match byte-for-byte. Its initial `npm install` still needs the registry. This leaves a distinct dependency-recovery gap: a build cannot be reproduced after npm dependencies disappear if the registry is unreachable.

## New bounded acceptance
Warm an ephemeral npm cache during the existing initial install, preserve the generated lockfile, delete `node_modules`, then run `npm ci --offline` inside a Docker container started with `--network none`. The container has only the workspace and warm npm cache mounted. It must load the actual Sharp native dependency; the host must also load Sharp and the lockfile must remain byte-identical. The existing pristine-source/verified-media-cache rebuild and complete generated-tree SHA256 comparison then run unchanged. A failure blocks the existing workflow rather than silently falling back to a network install.

The network-isolated phase is genuinely disconnected, but **this does not establish cold-start air-gapped installation**: obtaining the Node container image and warming the npm cache still use a network before isolation, and the generated lockfile is not yet committed. A portable, pinned dependency bundle or verified offline registry mirror would be required for cold-start acceptance. The Node container tag is version-specific but not digest-pinned.

## Safety and scope
Only the existing independent reproducibility workflow and this QA note change. No published HTML, CSS, articles, original PDFs, source media, WordPress, private drafts, indexing or rights decisions change. The four private drafts, 82 media assets and noindex remain untouched. Do not retry or bypass CHM-B040's rejected historical CS12 operation. Require all eight exact-head PR workflows, reviewed diff, READY preview, squash merge and exact-main production before claiming deployment. If the offline install fails, diagnose it on the same branch without weakening the test; do not merge a broken gate.
