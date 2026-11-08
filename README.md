# OpenAI Secure MCP Tunnel for Home Assistant OS

Minimal Home Assistant OS app repository for running OpenAI's [Secure MCP Tunnel](https://github.com/openai/tunnel-client) alongside Home Assistant.

Version `0.1.1` builds a small local HAOS image using OpenAI's unmodified tunnel-client binary from `ghcr.io/openai/tunnel-client:v0.0.20`, the Home Assistant Alpine base and Nginx. The proxy adapts OpenAI's built-in UI for Home Assistant Ingress. It does **not** install code into Home Assistant Core.

> **Status:** Experimental, personal deployment. The container has started and connected to the OpenAI tunnel control plane; end-to-end ChatGPT MCP access is still being tested. This is not a security audit or a supported OpenAI/Home Assistant product.

## Related projects

Several independent Home Assistant projects package the same [official OpenAI tunnel client](https://github.com/openai/tunnel-client):

| Project | Home Assistant packaging | Main distinction |
| --- | --- | --- |
| **[This project](https://github.com/fowl2-bot/ha-openai-tunnel)** | HAOS app (separate container) | One tunnel client, experimental Ingress access to its built-in web UI |
| **[Home Assistant MCP Tunnel](https://github.com/lukkezen/home-assistant-mcp-tunnel)** | HAOS add-on | Multiple independently configured tunnels; aims to support other providers |
| **[OpenAI Tunnel for HA-MCP](https://github.com/norpol/hass-codex-tunnel-mcp)** | HACS custom integration (runs inside HA Core) | Home Assistant entities and management UI, verified binary updates and rollback; no embedded upstream web UI |

These are community projects, not official OpenAI or Home Assistant integrations. Choose based on whether you prefer a separate HAOS app, multiple tunnels, or native Home Assistant entities.

## Requirements

- Home Assistant OS with app/add-on support, on amd64 or aarch64.
- A tunnel created in your OpenAI Platform account and a runtime API key authorised to use it.
- Home Assistant's **Model Context Protocol Server** integration (Settings → Devices & services → Add integration).
- A ChatGPT account/workspace that permits creating a custom MCP plugin.

## Install

1. Open Home Assistant → **Settings → Apps → Install app** → menu **Repositories**.
2. Add this repository: `https://github.com/fowl2-bot/ha-openai-tunnel`.
3. Install **OpenAI Secure MCP Tunnel**.
4. Under its Configuration tab, set:
   - `CONTROL_PLANE_TUNNEL_ID`: your OpenAI tunnel identifier.
   - `CONTROL_PLANE_API_KEY`: the tunnel's runtime API key. Do not paste it into GitHub issues or chat logs.
   - `MCP_SERVER_URL`: `http://supervisor/core/api/mcp`.
   - `MCP_EXTRA_HEADERS`: `X-Ha-Access: env:SUPERVISOR_TOKEN`.
   - `LOG_LEVEL`: `info`; `LOG_FORMAT`: `struct-text`.
5. Save, start the app, and inspect its Logs tab. Select **Open Web UI** on the app page to see status, recent logs and live log level controls via Home Assistant Ingress. A successful control-plane connection does **not** necessarily mean MCP discovery and authentication succeed end to end.
6. In ChatGPT, create a **custom MCP plugin** using **Tunnel**, select your tunnel and select **No auth** *only when local Home Assistant authentication via the Supervisor proxy is functioning*.

The Supervisor supplies the `SUPERVISOR_TOKEN` environment variable when `homeassistant_api: true` is enabled. The tunnel client is configured to inject that token only into its upstream requests; it is not entered in ChatGPT. Do not paste or hardcode the token.

**Important:** App configuration can persist across upgrades. After updating, inspect both `MCP_SERVER_URL` and `MCP_EXTRA_HEADERS`; new defaults may not replace existing saved values.

## Ingress UI (experimental)

Home Assistant authenticates the UI. The Nginx proxy listens only for Supervisor Ingress traffic on port `8099` (no host port is published). OpenAI's admin/health UI stays bound to the container's loopback on port `8080`, with remote UI access disabled.

OpenAI's UI assumes it is hosted at the web root. Ingress instead uses a per-app prefixed URL. Our Nginx proxy rewrites its root-relative asset URLs, API requests and EventSource endpoints. **This is a fragile compatibility layer, not an upstream-supported base-path mode.** It was syntax-checked but has not yet been tested end to end on HAOS. An upstream UI update could break these substitutions.

To update from the original image-only packaging to `0.1.0`, refresh the Home Assistant app repository and select Update. This changes the app from pulling a prebuilt OpenAI image directly to building a local image with Nginx. Keep a copy of the saved non-secret configuration before updating and avoid publishing screenshots or logs containing keys. The update can fail during local image building; the previous app version should remain available until migration succeeds.

## Security and limitations

- The tunnel is **outbound-only**: no router port forwarding or Tailscale Funnel is required. It nevertheless enables remote API calls through the OpenAI tunnel and must be treated as a privileged access path.
- The Supervisor-provided API token can convey broad Home Assistant privileges. `No auth` in ChatGPT means the tunnel's own access controls and this locally injected token are the authentication boundary; it does **not** mean Home Assistant is anonymously accessible to the internet.
- There is **no per-user OAuth identity or authorisation** in this setup. Do not expose this tunnel to untrusted workspaces or users.
- A container reduces coupling with Home Assistant Core but is **not** a guarantee of least privilege or security. The app uses the Supervisor/Core API proxy and should be treated as highly privileged.
- Credentials entered in the Home Assistant app configuration are sensitive. Protect Home Assistant backups and diagnostic exports.
- The app's version is now independent of the upstream tunnel client's version. The Dockerfile pins upstream client `v0.0.20` but not its image digest; consider digest pinning for stronger reproducibility.
- The Home Assistant MCP server's supported operations, including any configuration writes, depend on its own implementation and the permissions exposed. HAOS host/disk management is not automatically available through MCP.
- This repository is **experimental and not fully tested**; the local Supervisor token header and MCP transport still require end-to-end validation.

## Repository layout

- `repository.yaml` — Home Assistant app repository metadata.
- `openai_tunnel/config.yaml` — HAOS app definition and configuration schema.
- `openai_tunnel/Dockerfile` — locally builds a container with the upstream tunnel client and Nginx.
- `openai_tunnel/ingress.conf` — restrictive Ingress proxy, including path rewriting for OpenAI's built-in UI.

## Troubleshooting

If the tunnel starts but ChatGPT cannot discover the MCP server, check the app logs for `dispatcher received MCP upstream error`. A `401` with `failure_source=target_http` indicates that the upstream Home Assistant endpoint rejected the request, not necessarily that the tunnel failed to connect.

Ensure the saved endpoint is `http://supervisor/core/api/mcp`, not `http://homeassistant/api/mcp`, and that the injected header is `X-Ha-Access: env:SUPERVISOR_TOKEN`.

For debug logging, set `LOG_LEVEL: debug` and `LOG_FORMAT: struct-text` (or `json`); debug logging without a structured log format is rejected by the tunnel client. Avoid posting unredacted debug logs publicly.
