#!/usr/bin/env bash
# Call only AFTER the source and packaged-application checks pass.
set -euo pipefail
image=${1:?usage: bash ci/publish.sh IMAGE}
docker push "$image"
python3 ci/record_release.py "$image"
if [[ -n "${GITHUB_STEP_SUMMARY:-}" ]]; then
  {
    printf '```text\n'
    cat release.txt
    printf '```\n'
  } >> "$GITHUB_STEP_SUMMARY"
fi
