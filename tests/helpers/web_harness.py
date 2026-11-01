# tests/helpers/web_harness.py
"""
Web harness for local HTTP execution testing of the Results Web Application.
Spins up ephemeral local HTTP server and verifies HTTP 200, asset delivery,
DOM element presence, and clean termination.
"""
import os
import socket
import threading
import http.server
import socketserver
import urllib.request
from typing import Optional, Tuple, Dict
from tests.test_config import APP_DIR, WORKSPACE_ROOT

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress standard request logging during test run
        pass

def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        s.listen(1)
        port = s.getsockname()[1]
        return port

def get_web_root() -> str:
    """Returns directory containing the web application entry point (index.html)."""
    # 1. narail_results_app/dist or narail_results_app
    app_dist = os.path.join(APP_DIR, "dist")
    if os.path.isdir(app_dist) and os.path.isfile(os.path.join(app_dist, "index.html")):
        return app_dist
    if os.path.isdir(APP_DIR) and os.path.isfile(os.path.join(APP_DIR, "index.html")):
        return APP_DIR

    # 2. Workspace root
    if os.path.isfile(os.path.join(WORKSPACE_ROOT, "index.html")):
        return WORKSPACE_ROOT

    return WORKSPACE_ROOT

class LocalWebServer:
    def __init__(self, directory: Optional[str] = None):
        self.directory = directory or get_web_root()
        self.port = find_free_port()
        self.httpd = None
        self.thread = None

    def start(self):
        class Handler(QuietHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=self.directory, **kwargs)

        Handler.directory = self.directory
        socketserver.TCPServer.allow_reuse_address = True
        self.httpd = socketserver.TCPServer(("127.0.0.1", self.port), Handler)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()

    def stop(self):
        if self.httpd:
            try:
                threading.Thread(target=self.httpd.shutdown, daemon=True).start()
                self.httpd.server_close()
            except Exception:
                pass

    def get_url(self, path: str = "/") -> str:
        if not path.startswith("/"):
            path = "/" + path
        return f"http://127.0.0.1:{self.port}{path}"

    def fetch(self, path: str = "/") -> Tuple[int, bytes, Dict[str, str]]:
        url = self.get_url(path)
        req = urllib.request.Request(url, headers={"User-Agent": "Narail-E2E-Harness"})
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                code = resp.status
                body = resp.read()
                headers = dict(resp.headers)
                return code, body, headers
        except urllib.error.HTTPError as e:
            return e.code, e.read(), dict(e.headers)
