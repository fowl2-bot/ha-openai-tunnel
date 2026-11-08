# Keep the upstream OpenAI client unchanged; add only an Ingress reverse proxy.
FROM ghcr.io/openai/tunnel-client:v0.0.20 AS tunnel

FROM ghcr.io/home-assistant/base:3.24

RUN apk add --no-cache nginx && mkdir -p /run/nginx

COPY --from=tunnel /usr/bin/tunnel-client /usr/local/bin/tunnel-client
COPY ingress.conf /etc/nginx/http.d/default.conf

# The OpenAI UI stays loopback-only; only Nginx is reachable by Supervisor.
CMD ["/bin/sh", "-ec", "export HEALTH_LISTEN_ADDR=127.0.0.1:8080 ALLOW_REMOTE_UI=false; nginx && exec /usr/local/bin/tunnel-client run"]
