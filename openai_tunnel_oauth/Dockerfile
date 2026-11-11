# OAuth experiment: OpenAI's pinned binary plus a user-authenticated Nginx proxy.
FROM ghcr.io/openai/tunnel-client:v0.0.20 AS tunnel

FROM ghcr.io/home-assistant/base:3.22

ARG BUILD_VERSION
ARG BUILD_ARCH

LABEL io.hass.version="${BUILD_VERSION}" \
      io.hass.type="app" \
      io.hass.arch="${BUILD_ARCH}"

RUN apk add --no-cache nginx && mkdir -p /run/nginx

COPY --from=tunnel /usr/bin/tunnel-client /usr/local/bin/tunnel-client
COPY ingress.conf /etc/nginx/http.d/default.conf
COPY oauth-diagnostic.sh /usr/local/share/oauth-diagnostic.sh

# The OAuth issuer is http://dawnha.local. Resolve it *inside this container*
# to the local Nginx listener; browsers still reach the real Home Assistant.
# This makes the MCP and authorization-server origins identical and permits
# the tunnel's narrowly scoped private-host Harpoon registration.
# Existing 0.1.11 users may have the old MCP URL saved in HAOS options.
CMD ["/command/with-contenv", "/bin/sh", "-ec", "printf '127.0.0.1 dawnha.local\\n' >> /etc/hosts; export HEALTH_LISTEN_ADDR=127.0.0.1:8080 ALLOW_REMOTE_UI=false HARPOON_ALLOW_PLAINTEXT_HTTP=true HARPOON_HOSTS_INCLUDE_REGEX='^dawnha[.]local$'; if [ \"$MCP_SERVER_URL\" = \"http://127.0.0.1:8098/mcp\" ]; then export MCP_SERVER_URL=http://dawnha.local/mcp; fi; nginx -t; nginx -g 'daemon off;' & sh /usr/local/share/oauth-diagnostic.sh; exec /usr/local/bin/tunnel-client run"]
