# OAuth test variant

Independent of the working no-auth Home Assistant app. A **different OpenAI tunnel ID** is required.

## Configuring the OAuth origin (version 0.1.13+)

Set `HA_OAUTH_ORIGIN` in the add-on configuration to the URL used by your browser for Home Assistant:

- `http://dawnha.local` — **existing local HTTP default** (kept for compatibility). Other local HTTP hostnames and ports are supported.
- `https://your-host.example` — an externally accessible HTTPS origin, such as a reverse proxy, Home Assistant Cloud, or Tailscale Serve. **Experimental**: token and revocation routing from the container to that HTTPS origin is not yet end-to-end verified.

The value must be an origin only (scheme, hostname and optional port; no path). It must match a configured Home Assistant URL, otherwise discovery may return missing or relative metadata. All connections through this test app are private to the selected OpenAI tunnel.

HTTP mode creates a container-only `/etc/hosts` entry and a loopback HTTP proxy, with a narrowly scoped Harpoon hostname rule. HTTPS mode uses a local MCP proxy but advertises the configured external issuer and explicitly permits OAuth discovery and forwarding to that HTTPS origin; the app must be able to reach it. In both modes, bearer tokens are forwarded to Home Assistant Core; no Supervisor token is supplied.

The `MCP_SERVER_URL` is derived automatically; previously saved values are ignored, so upgrading from versions 0.1.11/0.1.12 does not require changing that option.

**Security:** Plain HTTP is for local experiments only. Prefer HTTPS for normal use. Neither mode is production-ready until browser authorization, token exchange, refresh, and per-user access control are verified.

## Installation

1. Install **OpenAI Secure MCP Tunnel (OAuth Test)** from this repository alongside the working no-auth app.
2. Enter a separate OpenAI tunnel ID and restricted runtime API key.
3. For an external URL, set `HA_OAUTH_ORIGIN` before starting. Leave the default to retain local-HTTP behavior.
4. Start the app and inspect `oauth_setup` / `oauth_probe` logs, then try ChatGPT OAuth discovery.
