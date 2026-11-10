#!/usr/bin/env bash
set -euo pipefail
: "${IMAGE_TAG:?IMAGE_TAG must reference the built image}"
docker run --rm --add-host homeassistant:127.0.0.1 \
  --entrypoint nginx "$IMAGE_TAG" -t
docker run --rm --entrypoint /usr/local/bin/tunnel-client \
  "$IMAGE_TAG" --version
