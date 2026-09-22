#!/usr/bin/env bash
# Run from the repository root. Accept a tag OR a complete digest reference.
set -euo pipefail
image=${1:?usage: bash ci/verify_image.sh IMAGE}
container=""
cleanup() {
  if [[ -n "$container" ]]; then
    docker logs "$container" || true
    docker rm -f "$container" >/dev/null || true
  fi
}
trap cleanup EXIT
container=$(docker run -d --platform linux/amd64 \
  -p 127.0.0.1::8000 "$image")
address=$(docker port "$container" 8000/tcp)
python3 smoke_test.py "http://$address"
