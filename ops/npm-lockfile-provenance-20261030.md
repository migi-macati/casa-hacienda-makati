# npm lockfile provenance and review artifact — 2026-10-30 PHT

## Scope and rationale
The prior network-isolated media rebuild regenerates package-lock.json using npm install before its offline npm ci. That proves warm-cache reinstallation but leaves the resolved tarball origins and integrity values unexamined and does not retain the lock for independent review. The repository does not yet commit a lockfile.

This change adds a dependency-free preflight after npm install that requires npm lockfile v3, exact package.json root dependencies and exact Sharp version, pinned semver versions, SHA integrity, and HTTPS tarballs from registry.npmjs.org only for every dependency. Ten synthetic negative mutations fail closed. The generated lockfile is retained as a short-lived CI artifact for independent examination and possible subsequent repository commit. The existing network-isolated npm ci, native Sharp load, offline WordPress media rebuild, and full generated-tree byte comparison remain mandatory.

## Acceptance and limits
The PR must pass the exact-head full build and all existing independent workflows. Review the generated lockfile artifact before using it as a committed source of truth; the artifact alone does not make dependency installation cold-start air-gapped. Warming npm's cache and downloading the Node container still require a network; the Docker tag is not digest-pinned. Registry HTTPS and SHA integrity are source constraints, not proof of publisher authenticity, dependency safety, or license clearance. No new dependency or paid service is introduced.

No published article, HTML, CSS, PDF, original WordPress media, private draft, WordPress source, indexing, or public-launch settings change. Four private drafts, 82 media and noindex are preserved. CHM-B040's historical CS12 safety rejection remains prohibited and must not be retried or bypassed.

## Follow-up
Retrieve the successful CI lockfile artifact, inspect its package graph, integrity and host entries, then commit the verified lockfile with npm ci as the initial installation path and repeat all gates. Separately, establish a truly cold-start, offline-capable dependency and runtime bundle only after confirming redistribution rights and binary provenance. Do not claim full migration acceptance from this QA improvement.
