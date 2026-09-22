"""Synthetic scoring service: package/delivery exercise, not a trained model."""

import json
import math
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit


def classify(value):
    """The contract includes the boundary: a score of 0.5 is positive."""
    if not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError("value must be a finite number between 0 and 1")
    return "positive" if value >= 0.5 else "negative"


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        request = urlsplit(self.path)
        if request.path == "/health":
            status, payload = 200, {"status": "ok"}
        elif request.path == "/score":
            try:
                value = float(parse_qs(request.query)["value"][0])
                status, payload = 200, {"label": classify(value)}
            except (KeyError, ValueError):
                status, payload = 400, {"error": "supply value between 0 and 1"}
        else:
            status, payload = 404, {"error": "not found"}
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
