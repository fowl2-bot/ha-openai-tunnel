#!/bin/sh
# Read-only diagnostics, without authentication or secrets.
# Errors are informative only and never block the tunnel.
for name in oauth-authorization-server oauth-protected-resource; do
    url="http://homeassistant/.well-known/$name"
    if body="$(wget -q -T 5 -O - --header='Host: dawnha.local' "$url" 2>/dev/null)"; then
        case "$name" in
            oauth-authorization-server) expected='"authorization_endpoint"' ;;
            oauth-protected-resource) expected='"authorization_servers"' ;;
        esac
        if printf '%s' "$body" | grep -Fq "$expected" &&
           printf '%s' "$body" | grep -Fq 'http://dawnha.local'; then
            printf 'oauth_probe %s reachable with Host dawnha.local\n' "$name"
        else
            printf 'oauth_probe %s unexpected metadata: %s\n' "$name" "$body"
        fi
    else
        printf 'oauth_probe %s unavailable via homeassistant with Host dawnha.local\n' "$name"
    fi
done
if wget -q -T 5 -O /dev/null http://dawnha.local/.well-known/oauth-authorization-server 2>/dev/null; then
    echo 'oauth_probe dawnha.local directly reachable from add-on'
else
    echo 'oauth_probe dawnha.local not directly reachable from add-on (Harpoon routing may require adjustment)'
fi
exit 0
