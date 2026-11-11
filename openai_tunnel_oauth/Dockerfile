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
RUN rm -f /etc/nginx/http.d/default.conf
COPY ingress.conf /etc/nginx/http.d/default.conf.template
COPY oauth-setup.sh /usr/local/bin/oauth-setup.sh
COPY oauth-diagnostic.sh /usr/local/share/oauth-diagnostic.sh

# Render a validated local proxy configuration at container startup.
# Do not inject Supervisor credentials into the OAuth variant.
CMD ["/command/with-contenv", "/bin/sh", "-ec", ". /usr/local/bin/oauth-setup.sh; export HEALTH_LISTEN_ADDR=127.0.0.1:8080 ALLOW_REMOTE_UI=false; nginx -t; nginx -g 'daemon off;' & sh /usr/local/share/oauth-diagnostic.sh & exec /usr/local/bin/tunnel-client run"]
