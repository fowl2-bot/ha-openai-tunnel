# Disposable systemd/cgroup test. NOT for production use.
FROM debian:trixie-slim
ARG BUILD_VERSION=0.1.0
ARG BUILD_ARCH=amd64
LABEL io.hass.version="${BUILD_VERSION}" \
      io.hass.type="app" \
      io.hass.arch="${BUILD_ARCH}"
ENV container=docker \
    DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install -y --no-install-recommends systemd dbus \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /etc/systemd/system/multi-user.target.wants
COPY start-probe.sh /usr/local/bin/start-probe.sh
COPY unit-probe.sh /usr/local/bin/unit-probe.sh
COPY haos-systemd-probe.service /etc/systemd/system/haos-systemd-probe.service
RUN chmod +x /usr/local/bin/start-probe.sh /usr/local/bin/unit-probe.sh \
    && ln -s /etc/systemd/system/haos-systemd-probe.service \
       /etc/systemd/system/multi-user.target.wants/haos-systemd-probe.service
STOPSIGNAL SIGRTMIN+3
CMD ["/usr/local/bin/start-probe.sh"]
