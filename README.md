# OpenAI Secure MCP Tunnel for Home Assistant OS

Minimal Home Assistant OS app repository for running OpenAI's [Secure MCP Tunnel](https://github.com/openai/tunnel-client) alongside Home Assistant.

It runs OpenAI's published container image (`ghcr.io/openai/tunnel-client`), rather than installing a custom integration into Home Assistant Core. No Dockerfile, startup script, or third-party tunnel executable is included in this repository.

> **Status:** Experimental, personal deployment. The container has started and connected to the OpenAI tunnel control plane; end-to-end ChatGPT MCP access is still being tested. This is not a security audit or a supported OpenAI/Home Assistant product.

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
5. Save, start the app, and inspect its Logs tab. A successful control-plane connection does **not** necessarily mean MCP discovery and authentication succeed end to end.
6. In ChatGPT, create a **custom MCP plugin** using **Tunnel**, select your tunnel and select **No auth** *only when local Home Assistant authentication via the Supervisor proxy is functioning*.

The Supervisor supplies the `SUPERVISOR_TOKEN` environment variable when `homeassistant_api: true` is enabled. The tunnel client is configured to inject that token only into its upstream requests; it is not entered in ChatGPT. Do not paste or hardcode the token.

**Important:** App configuration can persist across upgrades. After updating, inspect both `MCP_SERVER_URL` and `MCP_EXTRA_HEADERS`; new defaults may not replace existing saved values.

## Security and limitations

- The tunnel is **outbound-only**: no router port forwarding or Tailscale Funnel is required. It nevertheless enables remote API calls through the OpenAI tunnel and must be treated as a privileged access path.
- The Supervisor-provided API token can convey broad Home Assistant privileges. `No auth` in ChatGPT means the tunnel's own access controls and this locally injected token are the authentication boundary; it does **not** mean Home Assistant is anonymously accessible to the internet.
- There is **no per-user OAuth identity or authorisation** in this setup. Do not expose this tunnel to untrusted workspaces or users.
- A container reduces coupling with Home Assistant Core but is **not** a guarantee of least privilege or security. The app uses the Supervisor/Core API proxy and should be treated as highly privileged.
- Credentials entered in the Home Assistant app configuration are sensitive. Protect Home Assistant backups and diagnostic exports.
- The app configuration's `version` identifies this packaging, not necessarily the exact image build running underneath. Consider pinning by digest for reproducible deployments.
- The Home Assistant MCP server's supported operations, including any configuration writes, depend on its own implementation and the permissions exposed. HAOS host/disk management is not automatically available through MCP.
- This repository is **experimental and not fully tested**; the local Supervisor token header and MCP transport still require end-to-end validation.

## Repository layout

- `repository.yaml` — Home Assistant app repository metadata.
- `openai_tunnel/config.yaml` — HAOS app definition and configuration schema.

## Troubleshooting

If the tunnel starts but ChatGPT cannot discover the MCP server, check the app logs for `dispatcher received MCP upstream error`. A `401` with `failure_source=target_http` indicates that the upstream Home Assistant endpoint rejected the request, not necessarily that the tunnel failed to connect.

Ensure the saved endpoint is `http://supervisor/core/api/mcp`, not `http://homeassistant/api/mcp`, and that the injected header is `X-Ha-Access: env:SUPERVISOR_TOKEN`.

For debug logging, set `LOG_LEVEL: debug` and `LOG_FORMAT: struct-text` (or `json`); debug logging without a structured log format is rejected by the tunnel client. Avoid posting unredacted debug logs publicly.
