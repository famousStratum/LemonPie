# Changelog

## [0.2.0-beta.1](https://github.com/famousStratum/LemonPie/compare/v0.2.0-alpha.3...v0.2.0-beta.1) (2026-09-22)


### Bug Fixes

* eliminate now_ts() double-calls and session ID collisions in session creation ([#27](https://github.com/famousStratum/LemonPie/issues/27)) ([7864136](https://github.com/famousStratum/LemonPie/commit/7864136b6dc200e1e682b61252eadc74e99ac66a))

## [0.2.0-alpha.3](https://github.com/famousStratum/LemonPie/compare/v0.2.0-alpha.2...v0.2.0-alpha.3) (2026-09-21)


### Bug Fixes

* resolve tuple/dict mismatch in model alias lookup and dead code in session loading ([#23](https://github.com/famousStratum/LemonPie/issues/23)) ([65152bf](https://github.com/famousStratum/LemonPie/commit/65152bf9d6df0d91addad5aa72f73145383b99d9))

## [0.2.0-alpha.2](https://github.com/famousStratum/LemonPie/compare/lemonpie-cli-v0.2.0-alpha.1...lemonpie-cli-v0.2.0-alpha.2) (2026-09-21)


### Features

* **cli:** enhance error handling, model defaults, timeouts, and connection status ([9147dc0](https://github.com/famousStratum/LemonPie/commit/9147dc0293065f0b2227ac8f36cdacf0502ca7c4))
* **cli:** improve connection error handling, timeouts, and documentation ([83e2659](https://github.com/famousStratum/LemonPie/commit/83e2659182717d82feb28be4b85d14e85679d751))
* **paths:** Depend on platformdirs for config/session paths; bump requires-python to &gt;=3.11 ([6fbf8e9](https://github.com/famousStratum/LemonPie/commit/6fbf8e92d27cbec20c57f404aecf99940329b238))


### Bug Fixes

* **build:** explicitly specify hatchling wheel package directory ([705980a](https://github.com/famousStratum/LemonPie/commit/705980a9eda1672829119db0fcd2aab4a9c04101))
* **build:** specify hatchling package target ([b759f2d](https://github.com/famousStratum/LemonPie/commit/b759f2d086bccb7b39d456844d1bb7403410e8d4))
* **cli:** import missing resolve_session in main entrypoint ([f5c4c5a](https://github.com/famousStratum/LemonPie/commit/f5c4c5ae1cc7ade21ba41eb92a9ecc640a7fe969))
* **cli:** reorder main entrypoint control flow and fix argument handling ([3a182d2](https://github.com/famousStratum/LemonPie/commit/3a182d2485af36f8a98a28cb41459f968fc9f4d4))
* **cli:** reorder main entrypoint control flow and resolve model assignment ([ad944f9](https://github.com/famousStratum/LemonPie/commit/ad944f93e2661eb3f2cc1abfe6cdeedc04f6ee86))
* **cli:** resolve NameError in main entrypoint ([532d661](https://github.com/famousStratum/LemonPie/commit/532d6617ff589de5f5def690e6390b1341517f84))


### Documentation

* Add roadmap section to README and initial state-machine design doc ([fa9b000](https://github.com/famousStratum/LemonPie/commit/fa9b0009aaca85cbcd3e5a6f1e1c6c4d3bc40196))
* update README for src/ layout and platformdirs ([a15cde2](https://github.com/famousStratum/LemonPie/commit/a15cde25a08c49d11366bc64c31aa80da9590838))
* update README.md ([cf7a046](https://github.com/famousStratum/LemonPie/commit/cf7a0468474cc6bb47dbf33148a6b18d11b44fdf))
* update roadmap in README.md ([d0a3316](https://github.com/famousStratum/LemonPie/commit/d0a33167361efd400682f54780aaf3fff738e41d))
