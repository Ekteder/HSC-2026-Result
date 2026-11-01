# tests/tier5_adversarial/test_adversarial_challenger_2.py
"""
Tier 5 — Adversarial Hardening: Web & Performance Stress Testing (Challenger 2)
Empirically stress-tests the production web application build:
- Ephemeral local HTTP serving under high concurrent load (50 workers, 100 requests)
- Strict HTTP status 200, Content-Type MIME headers, and Content-Length matching
- Bundle completeness (HTML, CSS, JS, manifest, roll lookup, student records, 24 colleges)
- Gzip compression ratio and bitwise SHA-256 round-trip integrity
- Mobile (<640px), Tablet (640-1024px), Desktop (>=1024px), and Print media query rules
- Multi-viewport headless Chrome rendering simulation
"""

import os
import sys
import json
import gzip
import time
import socket
import hashlib
import unittest
import subprocess
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
import http.server
import socketserver
import threading
from bs4 import BeautifulSoup

WORKSPACE_ROOT = "/media/sanglap/Movies/2026results"
APP_DIR = os.path.join(WORKSPACE_ROOT, "narail_results_app")
DIST_DIR = os.path.join(APP_DIR, "dist")
DATA_DIR = os.path.join(DIST_DIR, "data")
ASSETS_DIR = os.path.join(DIST_DIR, "assets")

class ThreadingQuietServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIST_DIR, **kwargs)

    def log_message(self, format, *args):
        pass

    def guess_type(self, path):
        base_type = super().guess_type(path)
        if path.endswith(".js"):
            return "text/javascript"
        if path.endswith(".css"):
            return "text/css"
        if path.endswith(".json"):
            return "application/json"
        if path.endswith(".html"):
            return "text/html; charset=utf-8"
        return base_type

def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        s.listen(1)
        return s.getsockname()[1]

class TestAdversarialChallenger2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.port = find_free_port()
        cls.server = ThreadingQuietServer(("127.0.0.1", cls.port), QuietHandler)
        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.port}"

    @classmethod
    def tearDownClass(cls):
        try:
            threading.Thread(target=cls.server.shutdown, daemon=True).start()
            cls.server.server_close()
        except Exception:
            pass

    def _fetch(self, path: str, headers: dict = None, timeout: float = 8.0):
        url = f"{self.base_url}{path}" if path.startswith("/") else f"{self.base_url}/{path}"
        req_headers = {"User-Agent": "Challenger2-TestSuite"}
        if headers:
            req_headers.update(headers)
        req = urllib.request.Request(url, headers=req_headers)
        t0 = time.perf_counter()
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
            dt = time.perf_counter() - t0
            norm_headers = {k.lower(): v for k, v in resp.headers.items()}
            return resp.status, data, norm_headers, dt

    def test_concurrent_http_serving_under_load(self):
        """Challenger 2.1: Verify HTTP 200 and low latency under 50 concurrent workers."""
        endpoints = [
            "/",
            "/data/manifest.json",
            "/data/roll_lookup.json",
            "/data/narail_all_students.json",
        ]
        js_files = [f for f in os.listdir(ASSETS_DIR) if f.endswith(".js")]
        css_files = [f for f in os.listdir(ASSETS_DIR) if f.endswith(".css")]
        if js_files:
            endpoints.append(f"/assets/{js_files[0]}")
        if css_files:
            endpoints.append(f"/assets/{css_files[0]}")

        total_requests = 100
        concurrency = 50

        def worker_task(idx):
            ep = endpoints[idx % len(endpoints)]
            status, data, headers, dt = self._fetch(ep)
            return status, len(data), dt

        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [executor.submit(worker_task, i) for i in range(total_requests)]
            results = [f.result() for f in as_completed(futures)]

        statuses = [r[0] for r in results]
        durations = [r[2] * 1000.0 for r in results]

        self.assertEqual(statuses.count(200), total_requests, "Not all concurrent requests returned HTTP 200")
        durations.sort()
        p95 = durations[int(len(durations) * 0.95)]
        self.assertLess(p95, 2000.0, f"p95 latency too high: {p95:.1f}ms")

    def test_content_type_and_length_headers(self):
        """Challenger 2.2: Verify MIME Content-Type and Content-Length headers for all assets."""
        js_files = [f for f in os.listdir(ASSETS_DIR) if f.endswith(".js")]
        css_files = [f for f in os.listdir(ASSETS_DIR) if f.endswith(".css")]
        checks = [
            ("/", "text/html"),
            (f"/assets/{css_files[0]}", "text/css"),
            (f"/assets/{js_files[0]}", "text/javascript"),
            ("/data/manifest.json", "application/json"),
            ("/data/roll_lookup.json", "application/json"),
            ("/data/narail_all_students.json", "application/json"),
        ]

        for path, exp_type in checks:
            status, data, headers, _ = self._fetch(path)
            self.assertEqual(status, 200, f"Path {path} returned status {status}")
            ct = headers.get("content-type", "")
            self.assertIn(exp_type, ct, f"Path {path} has unexpected Content-Type: {ct}")
            cl = int(headers.get("content-length", "0"))
            self.assertEqual(cl, len(data), f"Path {path} Content-Length mismatch: {cl} != {len(data)}")

    def test_asset_loading_and_bundle_completeness(self):
        """Challenger 2.3: Verify dist/index.html links resolve to valid files on disk and over HTTP."""
        index_file = os.path.join(DIST_DIR, "index.html")
        self.assertTrue(os.path.isfile(index_file), "Missing dist/index.html")
        with open(index_file, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        # Scripts
        for s in soup.find_all("script", src=True):
            src = s["src"].lstrip("./").lstrip("/")
            status, data, _, _ = self._fetch(src)
            self.assertEqual(status, 200, f"Script {src} failed HTTP GET")
            self.assertGreater(len(data), 1000, f"Script {src} suspiciously small")

        # Stylesheets
        for l in soup.find_all("link", rel="stylesheet"):
            href = l["href"].lstrip("./").lstrip("/")
            status, data, _, _ = self._fetch(href)
            self.assertEqual(status, 200, f"Stylesheet {href} failed HTTP GET")
            self.assertGreater(len(data), 500, f"Stylesheet {href} suspiciously small")

    def test_college_datasets_and_student_roster_integrity(self):
        """Challenger 2.4: Verify all 24 college datasets reconcile with district summary."""
        colleges_dir = os.path.join(DATA_DIR, "colleges")
        self.assertTrue(os.path.isdir(colleges_dir), "Missing dist/data/colleges directory")
        college_files = [f for f in os.listdir(colleges_dir) if f.endswith(".json")]
        self.assertEqual(len(college_files), 24, f"Expected 24 college JSON files, got {len(college_files)}")

        tot_students = 0
        tot_passed = 0
        tot_gpa5 = 0
        for cf in college_files:
            with open(os.path.join(colleges_dir, cf), "r", encoding="utf-8") as f:
                cdata = json.load(f)
            st = cdata.get("statistics", {})
            students = cdata.get("students", [])
            self.assertEqual(len(students), st.get("total_registered"), f"Mismatch in {cf}")
            tot_students += len(students)
            tot_passed += st.get("total_passed", 0)
            tot_gpa5 += st.get("gpa5_count", 0)

        self.assertEqual(tot_students, 5065, "Total students sum != 5065")
        self.assertEqual(tot_passed, 1776, "Total passed sum != 1776")
        self.assertEqual(tot_gpa5, 105, "Total GPA-5 sum != 105")

    def test_gzip_compression_and_sha256_roundtrip(self):
        """Challenger 2.5: Verify gzip compression efficiency and bitwise SHA256 roundtrip fidelity."""
        core_files = [
            os.path.join(DIST_DIR, "index.html"),
            os.path.join(DATA_DIR, "manifest.json"),
            os.path.join(DATA_DIR, "roll_lookup.json"),
            os.path.join(DATA_DIR, "narail_all_students.json"),
        ]
        for f in os.listdir(ASSETS_DIR):
            core_files.append(os.path.join(ASSETS_DIR, f))

        for fpath in core_files:
            with open(fpath, "rb") as f:
                raw = f.read()
            raw_sha = hashlib.sha256(raw).hexdigest()
            comp = gzip.compress(raw, compresslevel=9)
            decomp = gzip.decompress(comp)
            decomp_sha = hashlib.sha256(decomp).hexdigest()

            self.assertEqual(raw_sha, decomp_sha, f"Gzip decompression SHA mismatch on {fpath}")
            # Ensure significant compression on JSON/JS/CSS (> 50%)
            reduction = (1.0 - (len(comp) / len(raw))) * 100.0
            self.assertGreater(reduction, 50.0, f"Low compression on {fpath}: {reduction:.1f}%")

    def test_viewport_meta_tag_and_responsive_breakpoints(self):
        """Challenger 2.6: Verify viewport meta tag and CSS media queries for mobile, tablet, and desktop."""
        index_file = os.path.join(DIST_DIR, "index.html")
        with open(index_file, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
        meta = soup.find("meta", attrs={"name": "viewport"})
        self.assertIsNotNone(meta, "Missing viewport meta tag")
        self.assertIn("width=device-width", meta.get("content", ""))
        self.assertIn("initial-scale=1", meta.get("content", ""))

        css_files = [os.path.join(ASSETS_DIR, f) for f in os.listdir(ASSETS_DIR) if f.endswith(".css")]
        self.assertTrue(len(css_files) > 0, "No built CSS bundle found")
        with open(css_files[0], "r", encoding="utf-8") as f:
            css_text = f.read()

        self.assertIn("min-width:640px", css_text, "Missing tablet breakpoint (min-width: 640px)")
        self.assertIn("min-width:768px", css_text, "Missing tablet breakpoint (min-width: 768px)")
        self.assertIn("min-width:1024px", css_text, "Missing desktop breakpoint (min-width: 1024px)")
        self.assertIn("print", css_text, "Missing print media query (@media print)")
        self.assertIn("overflow-x:auto", css_text, "Missing table overflow containment")

    def test_headless_chrome_viewport_simulation(self):
        """Challenger 2.7: Render index.html via headless Chrome across mobile, tablet, and desktop viewports."""
        chrome_bin = "/usr/bin/google-chrome"
        if not os.path.isfile(chrome_bin):
            self.skipTest("Google Chrome binary not found")

        viewports = [
            ("Mobile", 375, 667),
            ("Tablet", 768, 1024),
            ("Desktop", 1440, 900),
        ]
        for name, w, h in viewports:
            cmd = [
                chrome_bin,
                "--headless",
                "--disable-gpu",
                "--no-sandbox",
                f"--window-size={w},{h}",
                "--dump-dom",
                self.base_url
            ]
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=20)
            self.assertEqual(proc.returncode, 0, f"Headless chrome failed on viewport {name} ({w}x{h})")
            dom = proc.stdout
            self.assertGreater(len(dom), 1000, f"DOM too short on {name}")
            self.assertIn("Narail HSC 2026 Results Portal", dom)
            self.assertIn("hero-search-input", dom)
            self.assertIn("student-modal", dom)

if __name__ == "__main__":
    unittest.main()
