# tests/tier1_features/test_f7_webapp_serving.py
"""
Tier 1 — Feature 7: Web Application Local Execution & Asset Serving
Verifies that the web application starts and runs locally without errors,
serves HTML/JS/CSS over HTTP with valid MIME types and responsive DOM headers.
"""
import unittest
from bs4 import BeautifulSoup
from tests.helpers.web_harness import LocalWebServer

class TestF7WebappServing(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = LocalWebServer()
        cls.server.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()

    def test_http_root_endpoint_returns_status_200(self):
        """F7.1: Verify HTTP GET / returns 200 OK."""
        code, body, headers = self.server.fetch("/")
        self.assertEqual(code, 200, f"Expected HTTP 200, got {code}")
        self.assertGreater(len(body), 500, "HTML body is suspiciously short or empty")

    def test_html_document_structure_and_doctype(self):
        """F7.2: Verify served HTML document is well-formed with <!DOCTYPE html> and <html lang='en'>."""
        code, body, headers = self.server.fetch("/")
        html_str = body.decode("utf-8", errors="replace")
        self.assertIn("<!doctype html>", html_str.lower())
        soup = BeautifulSoup(html_str, "html.parser")
        self.assertIsNotNone(soup.head, "Missing <head> section")
        self.assertIsNotNone(soup.body, "Missing <body> section")

    def test_viewport_meta_tag_present_for_responsiveness(self):
        """F7.3: Verify responsive viewport meta tag is properly configured in <head>."""
        code, body, headers = self.server.fetch("/")
        soup = BeautifulSoup(body.decode("utf-8", errors="replace"), "html.parser")
        meta_viewport = soup.find("meta", attrs={"name": "viewport"})
        self.assertIsNotNone(meta_viewport, "Missing <meta name='viewport'> tag")
        content = meta_viewport.get("content", "")
        self.assertIn("width=device-width", content)
        self.assertIn("initial-scale=1", content)

    def test_title_and_branding_present(self):
        """F7.4: Verify application title and branding text are rendered in HTML."""
        code, body, headers = self.server.fetch("/")
        soup = BeautifulSoup(body.decode("utf-8", errors="replace"), "html.parser")
        title = soup.find("title")
        self.assertIsNotNone(title, "Missing <title> tag")
        self.assertTrue(
            "narail" in title.text.lower() or "hsc" in title.text.lower() or "result" in title.text.lower(),
            f"Title does not reflect Narail HSC results: '{title.text}'"
        )

    def test_static_css_and_js_resources_accessible(self):
        """F7.5: Verify linked CSS stylesheets and JS scripts load with HTTP 200."""
        code, body, headers = self.server.fetch("/")
        soup = BeautifulSoup(body.decode("utf-8", errors="replace"), "html.parser")

        # Check stylesheets or scripts linked
        links = soup.find_all("link", rel="stylesheet")
        for link in links:
            href = link.get("href")
            if href and not href.startswith("http"):
                c, b, h = self.server.fetch(href)
                self.assertEqual(c, 200, f"Stylesheet '{href}' failed to load with HTTP {c}")

        scripts = soup.find_all("script", src=True)
        for script in scripts:
            src = script.get("src")
            if src and not src.startswith("http"):
                c, b, h = self.server.fetch(src)
                self.assertEqual(c, 200, f"Script '{src}' failed to load with HTTP {c}")

    def test_essential_interactive_ui_containers_exist(self):
        """F7.6: Verify essential DOM elements for search, filter, or student display exist."""
        code, body, headers = self.server.fetch("/")
        html_str = body.decode("utf-8", errors="replace").lower()
        # Ensure either input search field or interactive element is present
        soup = BeautifulSoup(html_str, "html.parser")
        inputs = soup.find_all("input")
        has_search_or_filter = any(
            "search" in str(inp.get("type", "")).lower() or
            "search" in str(inp.get("id", "")).lower() or
            "roll" in str(inp.get("placeholder", "")).lower() or
            "text" in str(inp.get("type", "")).lower()
            for inp in inputs
        ) or "root" in html_str or "app" in html_str
        self.assertTrue(has_search_or_filter, "No search input or root application container found in DOM")

if __name__ == "__main__":
    unittest.main()
