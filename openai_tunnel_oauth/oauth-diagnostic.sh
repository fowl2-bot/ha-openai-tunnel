#!/bin/sh
# Read-only OAuth metadata validation through the local Nginx proxy.
# No user tokens or credentials are sent or logged.
if [ "${HA_OAUTH_SCHEME:-http}" = "http" ]; then
    url_base="${HA_OAUTH_ORIGIN}"
else
    url_base="http://127.0.0.1:8098"
fi
for name in oauth-authorization-server oauth-protected-resource; do
    url="$url_base/.well-known/$name"
    if body="$(wget -q -T 5 -O - "$url" 2>/dev/null)"; then
        case "$name" in
            oauth-authorization-server) required='"authorization_endpoint"' ;;
            oauth-protected-resource) required='"authorization_servers"' ;;
        esac
        if printf '%s' "$body" | grep -Fq "$required" &&
           printf '%s' "$body" | grep -Fq "$HA_OAUTH_ORIGIN"; then
            printf 'oauth_probe %s valid for configured origin %s\n' "$name" "$HA_OAUTH_ORIGIN"
        else
            printf 'oauth_probe %s invalid metadata for configured origin %s\n' "$name" "$HA_OAUTH_ORIGIN"
        fi
    else
        printf 'oauth_probe %s failed for configured origin %s\n' "$name" "$HA_OAUTH_ORIGIN"
    fi
done
exit 0
