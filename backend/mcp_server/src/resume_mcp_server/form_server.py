"""Loopback-only, fixed-asset server for the synthetic form."""

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

FORM = Path(__file__).resolve().parents[4] / "data/synthetic/mcp-spike/form.html"


class FormHandler(BaseHTTPRequestHandler):
    def _valid_host(self) -> bool:
        hosts = self.headers.get_all("Host", [])
        allowed = {f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}"}
        return len(hosts) == 1 and hosts[0].lower() in allowed

    def do_GET(self) -> None:
        if not self._valid_host():
            self.send_error(403)
            return
        if self.path not in ("/", "/form.html"):
            self.send_error(404)
            return
        content = FORM.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(content)

    def do_POST(self) -> None:
        self.send_error(405)

    def log_message(self, format, *args) -> None:
        # Never echo paths or request data into process logs.
        return


def create_form_server(*, port: int = 8765) -> ThreadingHTTPServer:
    return ThreadingHTTPServer(("127.0.0.1", port), FormHandler)


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve the synthetic form on loopback")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    server = create_form_server(port=args.port)
    try:
        server.serve_forever()
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
