#!/bin/sh
# Sourced from /command/with-contenv. Validate origin before templating.
set -eu
: "${HA_OAUTH_ORIGIN:=http://dawnha.local}"
HA_OAUTH_ORIGIN="${HA_OAUTH_ORIGIN%/}"
case "$HA_OAUTH_ORIGIN" in
    http://*) HA_OAUTH_SCHEME=http; authority="${HA_OAUTH_ORIGIN#http://}" ;;
    https://*) HA_OAUTH_SCHEME=https; authority="${HA_OAUTH_ORIGIN#https://}" ;;
    *) echo "oauth_setup: HA_OAUTH_ORIGIN must be an http(s) origin" >&2; exit 1 ;;
esac
case "$authority" in
    ""|*[!a-zA-Z0-9.:-]*) echo "oauth_setup: invalid OAuth hostname/port" >&2; exit 1 ;;
esac
host="${authority%%:*}"
case "$host" in
    ""|.*|*..*|*.) echo "oauth_setup: invalid OAuth hostname" >&2; exit 1 ;;
esac
if ! printf '%s' "$host" | grep -Eq '^[a-zA-Z0-9][a-zA-Z0-9.-]*$'; then
    echo "oauth_setup: invalid OAuth hostname" >&2
    exit 1
fi
# IPv6 literals and URLs with paths, credentials or query strings are disallowed.
if [ "$authority" != "$host" ]; then
    port="${authority#*:}"
    case "$port" in ""|*[!0-9]*) echo "oauth_setup: invalid origin port" >&2; exit 1 ;; esac
    if [ "$port" -lt 1 ] || [ "$port" -gt 65535 ]; then
        echo "oauth_setup: origin port out of range" >&2
        exit 1
    fi
else
    if [ "$HA_OAUTH_SCHEME" = "http" ]; then port=80; else port=443; fi
fi

# HA's URL discovery matches the literal request Host and port.
# The proxy-to-Core leg is HTTP, so without an explicit :443 HA would
# incorrectly read the HTTPS issuer's Host as port 80 and return a 404.
# Keep custom origin ports unchanged.
upstream_authority="$authority"
if [ "$HA_OAUTH_SCHEME" = "https" ] && [ "$authority" = "$host" ]; then
    upstream_authority="$host:443"
fi

if [ "$HA_OAUTH_SCHEME" = "http" ]; then
    listen_port="$port"
    # Container-only hostname override (does not affect browsers/HAOS).
    printf '127.0.0.1 %s\n' "$host" >> /etc/hosts
    MCP_SERVER_URL="$HA_OAUTH_ORIGIN/mcp"
    host_regex="$(printf '%s' "$host" | sed 's/[.]/[.]/g')"
    HARPOON_HOSTS_INCLUDE_REGEX="^$host_regex$"
    export HARPOON_HOSTS_INCLUDE_REGEX
else
    # For HTTPS, the local proxy handles MCP + discovery, while Harpoon
    # forwards token/revocation calls to the specifically approved HTTPS origin.
    # This requires that the app can reach that origin over HTTPS.
    listen_port=8098
    MCP_SERVER_URL="http://127.0.0.1:8098/mcp"
    MCP_OAUTH_TRUSTED_ORIGINS="$HA_OAUTH_ORIGIN"
    HARPOON_OAUTH_FORWARD_ORIGINS="$HA_OAUTH_ORIGIN"
    export MCP_OAUTH_TRUSTED_ORIGINS HARPOON_OAUTH_FORWARD_ORIGINS
fi
export HA_OAUTH_ORIGIN HA_OAUTH_SCHEME MCP_SERVER_URL HARPOON_ALLOW_PLAINTEXT_HTTP=true
sed -e "s|__HA_LISTEN_PORT__|$listen_port|g" \
    -e "s|__HA_OAUTH_HOST__|$host|g" \
    -e "s|__HA_OAUTH_AUTHORITY__|$upstream_authority|g" \
    /etc/nginx/http.d/default.conf.template > /etc/nginx/http.d/default.conf
printf 'oauth_setup: issuer=%s mcp=%s mode=%s\n' "$HA_OAUTH_ORIGIN" "$MCP_SERVER_URL" "$HA_OAUTH_SCHEME"
