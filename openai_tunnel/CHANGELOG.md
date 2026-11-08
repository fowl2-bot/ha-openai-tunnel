# Changelog

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
