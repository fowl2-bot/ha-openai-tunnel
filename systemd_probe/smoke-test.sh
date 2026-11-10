#!/usr/bin/env bash
set -euo pipefail
: "${IMAGE_TAG:?IMAGE_TAG must reference the built image}"
docker run --rm --entrypoint /bin/sh "$IMAGE_TAG" -ec '
  test -x /usr/local/bin/start-probe.sh
  test -x /usr/local/bin/unit-probe.sh
  test -f /etc/systemd/system/haos-systemd-probe.service
  test -x /lib/systemd/systemd
  sh -n /usr/local/bin/start-probe.sh /usr/local/bin/unit-probe.sh
'
