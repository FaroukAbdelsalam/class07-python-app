"""Check a running HTTP service, retrying startup but never masking a mismatch."""

import json
import sys
import time
from urllib.error import URLError
from urllib.request import urlopen


def read_json(url):
    with urlopen(url, timeout=2) as response:
        return json.load(response)


def main(base):
    for attempt in range(30):
        try:
            health = read_json(base + "/health")
            break
        except (URLError, TimeoutError, ConnectionError):
            if attempt == 29:
                raise
            time.sleep(0.2)
    if health != {"status": "ok"}:
        raise RuntimeError(f"unexpected health response: {health!r}")
    for value, expected in ((0.2, "negative"), (0.5, "positive"), (0.9, "positive")):
        actual = read_json(f"{base}/score?value={value}")
        if actual != {"label": expected}:
            raise RuntimeError(f"score={value}: expected {expected}, got {actual!r}")
    print("PASS: health + 3 HTTP scoring cases")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 smoke_test.py http://127.0.0.1:8000")
    main(sys.argv[1].rstrip("/"))
