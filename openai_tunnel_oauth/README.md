# OAuth test variant

This is a separate Home Assistant OS app cloned from **OpenAI Secure MCP Tunnel**. It never replaces the existing working no-auth app.

- **Use a different OpenAI tunnel ID** from the working app. Both may share the same restricted runtime API key if its permissions allow both tunnels.
- The proxy talks directly to Home Assistant Core at `http://homeassistant/api/mcp`, passing each caller's `Authorization: Bearer` token. No `SUPERVISOR_TOKEN` or `X-Ha-Access` injection.
- OAuth discovery is forwarded to HA Core with `Host: dawnha.local`, matching the verified local Home Assistant URL.
- This is a **local HTTP experiment**, not a production-secure OAuth deployment. Browser access and token refresh through OpenAI Harpoon are **unverified**; ChatGPT may reject the HTTP issuer.
- The OAuth token target `http://dawnha.local` must be resolvable from the app for Harpoon forwarding. Startup logs include `oauth_probe` checks for this.
- The only inbound HTTP listener is on container loopback; the admin UI uses the authenticated HAOS Ingress listener.

## Start

1. Refresh the HAOS app repository and install **OpenAI Secure MCP Tunnel (OAuth Test)** alongside the existing app.
2. Create a **new** OpenAI tunnel in the same workspace and enter its ID and restricted runtime key in this app's configuration.
3. Start the new app and inspect `oauth_probe` and `OAuth discovery` logs before attempting to add an OAuth-authenticated ChatGPT plugin.

The original no-auth add-on remains independent and can keep running.
