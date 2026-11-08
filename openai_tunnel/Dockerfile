# Ingress edition: OpenAI's pinned binary plus a small Nginx proxy.
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

# S6 strips the container environment from CMD unless with-contenv restores it.
# Admin UI listens only on loopback; Supervisor ingress connects through Nginx.
CMD ["/command/with-contenv", "/bin/sh", "-ec", "export HEALTH_LISTEN_ADDR=127.0.0.1:8080 ALLOW_REMOTE_UI=false; nginx && exec /usr/local/bin/tunnel-client run"]
