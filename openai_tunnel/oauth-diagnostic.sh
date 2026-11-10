#!/bin/sh
# Read-only startup check of HA Core OAuth metadata over the HAOS internal network.
# The probe is diagnostic only: failures must never block an existing tunnel.
for name in oauth-authorization-server oauth-protected-resource; do
    url="http://homeassistant/.well-known/$name"
    if body="$(wget -q -T 5 -O - "$url" 2>/dev/null)"; then
        case "$name" in
            oauth-authorization-server) expected='"authorization_endpoint"' ;;
            oauth-protected-resource) expected='"authorization_servers"' ;;
        esac
        if printf '%s' "$body" | grep -Fq "$expected"; then
            printf 'oauth_probe %s reachable: %s\n' "$name" "$body"
        else
            printf 'oauth_probe %s unexpected response: %s\n' "$name" "$body"
        fi
    else
        printf 'oauth_probe %s unavailable at %s (HTTP or network error)\n' "$name" "$url"
    fi
done
exit 0
