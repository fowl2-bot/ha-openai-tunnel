# Changelog

## 0.1.11 - 2026-11-10

- Feat: add isolated OAuth test tunnel add-on (#3)

* feat(oauth): add separate test add-on file ingress.conf

* feat(oauth): add separate test add-on file Dockerfile

* feat(oauth): add separate test add-on file config.yaml

* feat(oauth): add separate test add-on file oauth-diagnostic.sh

* feat(oauth): add separate test add-on file README.md

* build: test and release both HAOS tunnel variants

* build: align OAuth test add-on version with existing release

* docs: explain separate experimental OAuth test add-on

* fix(oauth): exclude legacy no-auth server block from isolated proxy

* ci(oauth): validate isolated HAOS app before merge
## 0.1.10 - 2026-11-10

- Test: add HAOS systemd/cgroup feasibility probe (#2)

* test: add systemd feasibility probe (config.yaml)

* test: add systemd feasibility probe (Dockerfile)

* test: add systemd feasibility probe (start-probe.sh)

* test: add systemd feasibility probe (unit-probe.sh)

* test: add systemd feasibility probe (haos-systemd-probe.service)

* test: add systemd feasibility probe (README.md)

* ci: validate disposable HAOS systemd probe image
## 0.1.9 - 2026-11-10

- Test: log local Home Assistant OAuth metadata availability at startup (#1)

* test: add read-only startup probe of internal Home Assistant OAuth metadata

* test: run nonblocking OAuth metadata diagnostics at tunnel startup
## 0.1.8 - 2026-11-09

- Docs: rewrite README with verified setup and honest trade-offs
## 0.1.7 - 2026-11-09

- Fix: proxy MCP locally and return 404 for OAuth discovery metadata

- Docs: explain private MCP proxy, safe logs and upgrade settings

- Release: 0.1.4 with loopback MCP proxy default

- Fix: preserve nginx access logs in HAOS app output

- Fix: return JSON 404 for optional OAuth discovery

- Release: v0.1.5 JSON OAuth discovery fallback

- Docs: explain v0.1.5 JSON 404 OAuth fallback

- Fix: create empty response file for OAuth discovery 404

- Fix: use genuinely empty 404 discovery responses

- Release: v0.1.6 zero-byte OAuth discovery 404

- Docs: update 0.1.6 OAuth discovery workaround

- Ci: resolve HAOS-only supervisor hostname in nginx smoke test
## 0.1.3 - 2026-11-08

- Document related HAOS and HACS tunnel projects in README comparison
## 0.1.2 - 2026-11-08

- Initialize Home Assistant app repository

- Add minimal pinned official tunnel-client HAOS app (v0.0.19)

- Correct HAOS 2026.8+ internal Core API default port

- Allow debug logging by setting structured text log format

- Authenticate MCP via HAOS Supervisor-provided token and internal API proxy

- Use Supervisor Core proxy supported X-Ha-Access header for local MCP authentication

- Document HAOS tunnel app setup, authentication, limitations, and troubleshooting

- Match HAOS app version to published OpenAI tunnel-client image tag

- Add Dockerfile for isolated Ingress proxy

- Add ingress.conf for isolated Ingress proxy

- Pin tested HAOS base and add locally-built app metadata labels

- Enable authenticated HAOS Ingress for locally-built tunnel proxy (0.1.0)

- Require admin-only streaming Ingress and use compatible S6 init settings

- Document Ingress UI, compatibility risks and app image-building migration

- Restore HAOS options and Supervisor token in S6-managed tunnel process

- Release local Ingress app v0.1.1 with S6 environment fix

- Ci: configure git-cliff for incremental HAOS changelog

- Ci: validate and automatically release every main push

- Fix: include non-conventional commits in changelog [skip ci]

- Fix: create changelog on first release, prepend thereafter
