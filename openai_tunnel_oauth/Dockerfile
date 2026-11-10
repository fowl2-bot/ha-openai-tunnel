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

# S6 strips the container environment from CMD unless with-contenv restores it.
# Admin UI and MCP proxy listen only on loopback; Supervisor ingress uses Nginx.
# Keep nginx in foreground mode (as a background job) so safe access logs reach HAOS Logs.
CMD ["/command/with-contenv", "/bin/sh", "-ec", "export HEALTH_LISTEN_ADDR=127.0.0.1:8080 ALLOW_REMOTE_UI=false HARPOON_ALLOW_PLAINTEXT_HTTP=true; nginx -t; sh /usr/local/share/oauth-diagnostic.sh; nginx -g 'daemon off;' & exec /usr/local/bin/tunnel-client run"]
