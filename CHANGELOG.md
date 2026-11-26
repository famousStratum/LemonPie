# Changelog

## 0.3.3 (2026-11-26)

<!-- Release notes generated using configuration in .github/release.yml at main -->

## What's Changed
### New Features
* feat: add API key management and LEMONPIE_API_KEY override by @famousStratum in https://github.com/famousStratum/LemonPie/pull/65


**Full Changelog**: https://github.com/famousStratum/LemonPie/compare/v0.3.2...v0.3.3

## 0.3.2 (2026-11-25)

<!-- Release notes generated using configuration in .github/release.yml at main -->

## What's Changed
### Other Changes
* docs: add agent knowledge base and clean up source docs by @famousStratum in https://github.com/famousStratum/LemonPie/pull/50
* ci(changelog): configure GitHub API changelog generation by @famousStratum in https://github.com/famousStratum/LemonPie/pull/52
* docs: add AGENTS.md and SECURITY.md | update ROADMAP.md by @famousStratum in https://github.com/famousStratum/LemonPie/pull/58
* docs: move and clean knowledge-base by @famousStratum in https://github.com/famousStratum/LemonPie/pull/60
* deps: migrate httpx to httpx2 by @famousStratum in https://github.com/famousStratum/LemonPie/pull/61
* docs: add installation and quickstart sections to readme by @famousStratum in https://github.com/famousStratum/LemonPie/pull/63


**Full Changelog**: https://github.com/famousStratum/LemonPie/compare/v0.3.1...v0.3.2

## [0.3.1](https://github.com/famousStratum/LemonPie/compare/v0.3.0...v0.3.1) (2026-11-15)


### Features

* add --dry-run flag for previewing actions ([b432c2e](https://github.com/famousStratum/LemonPie/commit/b432c2e115c323af9ee13c13da560891873328ba))
* add --dry-run flag to preview actions without executing them ([dab6f25](https://github.com/famousStratum/LemonPie/commit/dab6f2527f753375d1489d51610aef743980051f))


### Bug Fixes

* add autouse mock_argv fixture to prevent CI test failures ([3b7745f](https://github.com/famousStratum/LemonPie/commit/3b7745ffd605068c49b3ccbf296e35265e741f28))


### Documentation

* create a doc for feature ideas ([#45](https://github.com/famousStratum/LemonPie/issues/45)) ([9e83b95](https://github.com/famousStratum/LemonPie/commit/9e83b95456b6657f17b1d3442cf1c984049671a7))
* update README description and --dry-run status ([999159f](https://github.com/famousStratum/LemonPie/commit/999159f9782039d4049e448121ccbae4538ea779))

## [0.3.0](https://github.com/famousStratum/LemonPie/compare/v0.2.0...v0.3.0) (2026-11-11)


### ⚠ BREAKING CHANGES

* add multi-backend support for OpenAI-compatible inference servers; existing server configuration formats may require updating ([#42](https://github.com/famousStratum/LemonPie/issues/42))

### Features

* add multi-backend support for OpenAI-compatible inference servers ([#42](https://github.com/famousStratum/LemonPie/issues/42)) ([f1cadb6](https://github.com/famousStratum/LemonPie/commit/f1cadb622fdacf4c1e48074e094f27cb62aa79b8))

## [0.2.0](https://github.com/famousStratum/LemonPie/compare/v0.2.0-rc2...v0.2.0) (2026-11-11)


### Documentation

* make all links absolute in README.md ([#40](https://github.com/famousStratum/LemonPie/issues/40)) ([3ec603e](https://github.com/famousStratum/LemonPie/commit/3ec603e4861008303ccdedc6736dbb178fe52c8c))

## [0.2.0-rc2](https://github.com/famousStratum/LemonPie/compare/v0.2.0-rc1...v0.2.0-rc2) (2026-11-01)


### Features

* add interactive setup wizard via lmConfig --init ([#37](https://github.com/famousStratum/LemonPie/issues/37)) ([a9cc56d](https://github.com/famousStratum/LemonPie/commit/a9cc56db38ee17735fbdd6d607a34cd06e352372))


### Documentation

* document lmConfig --init in README and docs ([#38](https://github.com/famousStratum/LemonPie/issues/38)) ([b1d0bd9](https://github.com/famousStratum/LemonPie/commit/b1d0bd95f1e96be12a4dea24ef79a5711deebdf1))
* reorganise roadmap into design documents and add a command reference ([#34](https://github.com/famousStratum/LemonPie/issues/34)) ([a382aac](https://github.com/famousStratum/LemonPie/commit/a382aac6d480963fce7f4486926e315a51741aaf))

## [0.2.0-rc1](https://github.com/famousStratum/LemonPie/compare/v0.2.0-beta.1...v0.2.0-rc1) (2026-09-22)


### Miscellaneous Chores

* ignore .test-env/ ([#32](https://github.com/famousStratum/LemonPie/issues/32)) ([3045077](https://github.com/famousStratum/LemonPie/commit/30450770de3441e5e4e078c5151abd9763d5098f))

## [0.2.0-beta.1](https://github.com/famousStratum/LemonPie/compare/v0.2.0-alpha.3...v0.2.0-beta.1) (2026-09-22)


### Bug Fixes

* prevent session ID collisions during session creation ([#27](https://github.com/famousStratum/LemonPie/issues/27)) ([7864136](https://github.com/famousStratum/LemonPie/commit/7864136b6dc200e1e682b61252eadc74e99ac66a))

## [0.2.0-alpha.3](https://github.com/famousStratum/LemonPie/compare/v0.2.0-alpha.2...v0.2.0-alpha.3) (2026-09-21)


### Bug Fixes

* fix model alias lookup and remove dead session-loading code ([#23](https://github.com/famousStratum/LemonPie/issues/23)) ([65152bf](https://github.com/famousStratum/LemonPie/commit/65152bf9d6df0d91addad5aa72f73145383b99d9))

## [0.2.0-alpha.2](https://github.com/famousStratum/LemonPie/compare/lemonpie-cli-v0.2.0-alpha.1...lemonpie-cli-v0.2.0-alpha.2) (2026-09-21)


### Features

* **cli:** enhance error handling, model defaults, timeouts, and connection status ([9147dc0](https://github.com/famousStratum/LemonPie/commit/9147dc0293065f0b2227ac8f36cdacf0502ca7c4))
* **cli:** improve connection error handling, timeouts, and documentation ([83e2659](https://github.com/famousStratum/LemonPie/commit/83e2659182717d82feb28be4b85d14e85679d751))
* **paths:** depend on platformdirs for config/session paths; bump requires-python to &gt;=3.11 ([6fbf8e9](https://github.com/famousStratum/LemonPie/commit/6fbf8e92d27cbec20c57f404aecf99940329b238))


### Bug Fixes

* **build:** explicitly specify hatchling wheel package directory ([705980a](https://github.com/famousStratum/LemonPie/commit/705980a9eda1672829119db0fcd2aab4a9c04101))
* **build:** specify hatchling package target ([b759f2d](https://github.com/famousStratum/LemonPie/commit/b759f2d086bccb7b39d456844d1bb7403410e8d4))
* **cli:** import missing resolve_session in main entrypoint ([f5c4c5a](https://github.com/famousStratum/LemonPie/commit/f5c4c5ae1cc7ade21ba41eb92a9ecc640a7fe969))
* **cli:** reorder main entrypoint control flow and fix argument handling ([3a182d2](https://github.com/famousStratum/LemonPie/commit/3a182d2485af36f8a98a28cb41459f968fc9f4d4))
* **cli:** reorder main entrypoint control flow and resolve model assignment ([ad944f9](https://github.com/famousStratum/LemonPie/commit/ad944f93e2661eb3f2cc1abfe6cdeedc04f6ee86))
* **cli:** resolve NameError in main entrypoint ([532d661](https://github.com/famousStratum/LemonPie/commit/532d6617ff589de5f5def690e6390b1341517f84))


### Documentation

* add roadmap section to README and initial state-machine design doc ([fa9b000](https://github.com/famousStratum/LemonPie/commit/fa9b0009aaca85cbcd3e5a6f1e1c6c4d3bc40196))
* update README for src/ layout and platformdirs ([a15cde2](https://github.com/famousStratum/LemonPie/commit/a15cde25a08c49d11366bc64c31aa80da9590838))
* update README.md ([cf7a046](https://github.com/famousStratum/LemonPie/commit/cf7a0468474cc6bb47dbf33148a6b18d11b44fdf))
* update roadmap in README.md ([d0a3316](https://github.com/famousStratum/LemonPie/commit/d0a33167361efd400682f54780aaf3fff738e41d))
