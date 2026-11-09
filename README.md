# OpenAI Secure MCP Tunnel for Home Assistant OS

**Connect ChatGPT to Home Assistant without exposing Home Assistant to the public internet.**

This community HAOS app runs the [official OpenAI Secure MCP Tunnel client](https://github.com/openai/tunnel-client) in a separate container. It makes an **outbound HTTPS connection** to OpenAI, receives MCP requests from ChatGPT, and forwards them to Home Assistant's built-in MCP server.

You don't need router port forwarding, a public Home Assistant URL, or a manually created Home Assistant access token. You **do** need an OpenAI tunnel and a runtime API key.

> **Status: experimental, with working read-only access.** On **9 November 2026**, ChatGPT successfully queried a Home Assistant OS 18.4 / Core 2026.11.0 installation (amd64) through this app: system information, integration status, and entity searches. Device control, configuration writes, extended uptime, and the Ingress web UI have **not** been verified end to end. This is neither an official OpenAI nor an official Home Assistant product.

## Is this the right option?

This is deliberately simple: **one tunnel, one MCP endpoint, one separate HAOS app**. It packages OpenAI's unmodified Go tunnel-client binary and an Nginx proxy; it installs nothing into Home Assistant Core.

| Option | Why choose it | Trade-off |
| --- | --- | --- |
| **This app** | Keep the tunnel in a separate HAOS container, with straightforward configuration and logs | Extra Nginx layer, one tunnel, experimental web UI, manually managed upstream client version, high-privilege Home Assistant access |
| [Home Assistant MCP Tunnel](https://github.com/lukkezen/home-assistant-mcp-tunnel) | Manage **multiple independent tunnels** from one HAOS add-on | A different community-managed add-on, with a broader configuration and lifecycle model |
| [OpenAI Tunnel for HA-MCP](https://github.com/norpol/hass-codex-tunnel-mcp) | Prefer **native Home Assistant entities and controls**, plus verified binary downloads, automatic updates, and rollback | A HACS custom integration running inside Home Assistant Core; it supervises a Go subprocess and uses an HA token or OAuth |
| [Official tunnel-client](https://github.com/openai/tunnel-client) on another host | Already have an always-on machine that can reach HA, and want no HAOS app | You manage its service, credentials, updates, and HA authentication yourself |

The alternatives aren't dependencies. The comparison reflects their project documentation checked in November 2026. **If native Home Assistant controls are your priority, consider the HACS integration first.**

## What you'll need

1. **Home Assistant OS**, amd64 or aarch64, with the [built-in MCP server](https://www.home-assistant.io/integrations/mcp_server/) enabled. Find it under **Settings → Devices & services**. This app connects to the main `/api/mcp` endpoint.
2. A tunnel created in [OpenAI Platform → Tunnels](https://platform.openai.com/settings/organization/tunnels), associated with the ChatGPT workspace that will use it.
3. A **runtime API key** from [OpenAI Platform → API keys](https://platform.openai.com/settings/organization/api-keys) with **Tunnels Read + Use** permission. Creating or managing a tunnel separately requires **Tunnels Read + Manage**. Don't use a Platform admin key as the runtime key.
4. A ChatGPT workspace/account allowed to create custom MCP apps; enable developer mode if required.

OpenAI's [Secure MCP Tunnel guide](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels) explains setup, workspace association, and permissions.

## Installation

1. In Home Assistant, open **Settings → Apps → Install app → ⋮ → Repositories** and add:
   `https://github.com/fowl2-bot/ha-openai-tunnel`
2. Install **OpenAI Secure MCP Tunnel** from that repository.
3. In its **Configuration** tab, set or confirm:

   | Setting | Value |
   | --- | --- |
   | `CONTROL_PLANE_TUNNEL_ID` | Your `tunnel_...` identifier |
   | `CONTROL_PLANE_API_KEY` | Your **runtime** API key (secret) |
   | `MCP_SERVER_URL` | `http://127.0.0.1:8098/mcp` |
   | `MCP_EXTRA_HEADERS` | `X-Ha-Access: env:SUPERVISOR_TOKEN` |
   | `LOG_LEVEL` / `LOG_FORMAT` | `info` / `struct-text` |

4. **Save and start** the app. In the **Logs** tab, look for `starting control-plane poller` and a successful MCP session initialization. Make sure there is no `control-plane polling disabled` error.
5. In [ChatGPT Plugins](https://chatgpt.com/plugins), choose **Add custom MCP server → Tunnel**, select the same tunnel, and choose **No auth**. Review the permission warning and create the private app.
6. Test with a **read-only** request, such as asking ChatGPT to find an entity in Home Assistant. Successful calls produce Nginx log entries resembling `mcp_proxy "POST /mcp" status=200 upstream=200`.

**"No auth" applies to the ChatGPT-facing app, not to Home Assistant.** The locally running app still authenticates to Home Assistant through the Supervisor. Only associate the OpenAI tunnel with workspaces you trust.

**Upgrading from an older version?** HAOS preserves saved settings. Check `MCP_SERVER_URL` and `MCP_EXTRA_HEADERS` after updating: new defaults may not override previously saved values.

## How it works

~~~text
ChatGPT → OpenAI-hosted tunnel endpoint
                 ↕ outbound polling and responses (HTTPS)
HAOS app: official tunnel-client
          → Nginx (loopback only)
          → Supervisor Core API proxy
          → Home Assistant MCP server (/api/mcp)
~~~

Nginx serves two separate purposes:

- **MCP proxy:** Listens only on `127.0.0.1:8098`. Forwards `/mcp` to `http://supervisor/core/api/mcp`, passing an `X-Ha-Access` header populated by `SUPERVISOR_TOKEN`. It returns an empty-body HTTP 404 on local OAuth metadata discovery paths.
- **Optional Ingress UI:** Port `8099` proxies the upstream client's local admin interface through authenticated Home Assistant Ingress. It rewrites root-relative URLs and JavaScript references, which is **fragile, experimental, and not verified end to end**. A broken UI does not mean the MCP tunnel is broken.

The empty-body 404 is the configuration that worked in our deployment. **We have not established that an empty body is necessary**: upstream code intends to treat any all-404 metadata discovery as optional, and non-empty 404 variants also started the poller in our logs. See [upstream issue #109](https://github.com/openai/tunnel-client/issues/109) for the misleading discovery/readiness diagnostics.

## Security and limitations

**The convenience comes with significant privileges.**

- **Private doesn't mean risk-free.** No inbound port or public HA endpoint is required, but authorized OpenAI clients can send requests to your home via the OpenAI-hosted service. Protect tunnel/workspace permissions and credentials.
- **Administrator access.** The Supervisor Core API proxy executes requests with **Home Assistant administrator privileges**. This app does **not** use a least-privileged HA user. It also cannot attribute actions to individual ChatGPT users using Home Assistant user identities. Avoid shared/untrusted workspaces.
- **Limit exposed MCP tools.** Home Assistant's main MCP endpoint can offer broad reading and action capabilities. Review its tool selection and, where available in your HA version, configure read-only operation. This app currently hardwires the main endpoint, not individual API paths such as `/api/mcp/assist`.
- **Protect secrets.** The runtime API key lives in HAOS app settings and the Supervisor token is available to the container. Protect backups and diagnostic exports. Don't paste credentials into issues, logs, or screenshots.
- **Updates aren't automatic for the upstream client.** The [Dockerfile](openai_tunnel/Dockerfile) currently copies official `tunnel-client v0.0.20`. The app's own version is separate. Upstream images are tag-pinned, not digest-pinned.
- **Only Home Assistant MCP tools are available.** The tunnel does not automatically provide HAOS disk administration, app installation, or other Supervisor-management operations.
- **This is for private use.** OpenAI Secure MCP Tunnel does not provide a public plugin-submission mechanism.

## Troubleshooting

| Symptom | What it means / what to check |
| --- | --- |
| `🟢 tunnel-client started`, but ChatGPT fails | The process started; that line **does not prove polling is working**. Check for `control-plane polling disabled` and attempt a read-only tool call. |
| `WARN OAuth discovery failed ... 404` | May be **normal** when a no-OAuth MCP server has no metadata. Look for subsequent polling and successful requests, not this warning alone. |
| `POST /mcp` returns `401` | Verify the loopback URL and `X-Ha-Access: env:SUPERVISOR_TOKEN`. Don't print the actual token. |
| An initial `POST /mcp` returns `400`, or `GET /mcp` returns `405` | Can be part of the client's startup probes, not a failed user tool call. |
| ChatGPT says `App setup was rate limited` | The wording doesn't establish the actual cause. Check polling, workspace association, and local requests. If it persists, contact [OpenAI Support](https://help.openai.com/) with a time and timezone, not your credentials. |
| Ingress UI stays blank or shows a loading screen | The UI proxy is experimental. Use the HAOS app's **Logs** tab instead; MCP works independently of the UI. |

To investigate further, set `LOG_LEVEL: debug` and `LOG_FORMAT: struct-text` (or `json`). The Nginx access log includes request paths, methods, status codes, and durations, **not headers or query strings**. Other logs can contain sensitive information; review before sharing.

## Updates, tests and source

Refresh the app repository in HAOS, then select **Update**. See the [app changelog](openai_tunnel/CHANGELOG.md).

GitHub Actions validates metadata, builds amd64/aarch64 images, smoke-tests the amd64 Nginx configuration and client version, and generates releases/changelog entries. **It does not test real HAOS runtime behavior, the ARM64 runtime, device control, or Ingress UI functionality.**

Source: [HAOS app configuration](openai_tunnel/config.yaml) · [Dockerfile](openai_tunnel/Dockerfile) · [Nginx configuration](openai_tunnel/ingress.conf) · [release workflow](.github/workflows/release.yml).
