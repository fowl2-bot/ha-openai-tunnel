#!/bin/sh
# Read-only check of local OAuth proxy, without logging tokens.
# The DNS alias is container-only; Nginx proxies requests to HA Core.
url_base="http://dawnha.local"
for name in oauth-authorization-server oauth-protected-resource; do
    url="$url_base/.well-known/$name"
    if body="$(wget -q -T 5 -O - "$url" 2>/dev/null)"; then
        case "$name" in
            oauth-authorization-server)
                required='"authorization_endpoint"'
                ;;
            oauth-protected-resource)
                required='"authorization_servers"'
                ;;
        esac
        if printf '%s' "$body" | grep -Fq "$required" &&
           printf '%s' "$body" | grep -Fq "$url_base"; then
            printf 'oauth_probe %s ready on same origin %s\n' "$name" "$url_base"
        else
            printf 'oauth_probe %s unexpected metadata on %s\n' "$name" "$url_base"
        fi
    else
        printf 'oauth_probe %s failed from same-origin proxy %s\n' "$name" "$url_base"
    fi
done
exit 0
