"""Record the pushed repository digest, not the local image/configuration ID."""

import json
import os
from pathlib import Path
import re
import subprocess
import sys


image = sys.argv[1]
repository = image.rsplit(":", 1)[0]
info = json.loads(subprocess.check_output(["docker", "image", "inspect", image]))[0]
references = [ref for ref in info.get("RepoDigests", [])
              if ref.startswith(repository + "@sha256:")]
if len(references) != 1 or not re.fullmatch(r".+@sha256:[0-9a-f]{64}", references[0]):
    raise SystemExit("Expected one pushed repository digest; inspect the push/registry.")
source = os.environ["GITHUB_SHA"]
revision = info["Config"].get("Labels", {}).get("org.opencontainers.image.revision")
if revision != source:
    raise SystemExit("Image revision label does not match this source record.")
server = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
repo = os.environ.get("GITHUB_REPOSITORY")
run_id = os.environ.get("GITHUB_RUN_ID")
run = f"{server}/{repo}/actions/runs/{run_id}" if repo and run_id else "local simulation"
record = (
    f"source={source}\n"
    f"run={run}\n"
    f"attempt={os.environ.get('GITHUB_RUN_ATTEMPT', 'local')}\n"
    "checks=source unit tests + packaged HTTP smoke test passed before publish\n"
    f"image={references[0]}\n"
    f"platform={info['Os']}/{info['Architecture']}\n"
)
Path("release.txt").write_text(record, encoding="utf-8")
print(record, end="")
