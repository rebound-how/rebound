# Changelog

All notable changes to `reliably-app` are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.6.1] - 2026-04-15

### Fixed

- Moved the `gcp` and `full` dependency sets from `[dependency-groups]` to
  `[project.optional-dependencies]` so that `reliably-app[gcp,full]` resolves
  correctly when the package is installed from PyPI. Dependency groups are not
  included in built wheel/sdist metadata (by spec), which caused installers to
  warn that the extras did not exist.

- Build with Python 3.14

---

## [0.6.0] - prior release

Initial tracked release.
