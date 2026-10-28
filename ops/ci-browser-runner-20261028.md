# Playwright browser CI runner compatibility — 2026-10-28 PHT

During PR #61 exact-head CI, four browser workflows failed **before executing any repository build or browser assertion**. All four failed at `python -m playwright install --with-deps chromium` after successfully installing `playwright==1.57.0` and its Python dependencies. GitHub Actions logs reported:

```
BEWARE: your OS is not officially supported by Playwright; installing dependencies for ubuntu26.04-x64 as a fallback.
Cannot install dependencies for ubuntu26.04-x64 with Playwright 1.57.0-beta-1764944708000!
Failed to install browsers
Error: ERROR: Playwright does not support chromium on ubuntu26.04-x64
```

The four affected workflows used `runs-on: ubuntu-latest`, which now resolved to Ubuntu 26.04. This is an **environment compatibility regression**, not evidence that accessibility, production pages, media or visual parity failed. Initial PR run IDs: search/privacy 40708684971; independent production/browser 40708684892; WordPress visual 40708684814; WCAG 40708684922. The independent heritage inventory, public-link audit and offline-media reproducibility succeeded because they did not install Playwright Chromium.

**Fix:** Pin only the four browser workflows to GitHub-hosted `ubuntu-24.04`, a supported operating system for the existing pinned Playwright version, retaining every browser install, assertion, privacy/media gate and fail-closed behavior. No check was skipped, softened, converted to continue-on-error, or removed. This is a compatibility repair, not a safety bypass. If a new exact-head run still fails, inspect logs and do not merge until it passes.

**Scope:** `.github/workflows/search-privacy.yml`, `production-acceptance.yml`, `visual-parity-lab.yml`, `wcag-audit.yml`. No original WordPress, public site content, private drafts, media, noindex or launch settings changed. Historical CHM-B040 rejected operation remains untouched.
