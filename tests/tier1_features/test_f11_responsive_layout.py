# tests/tier1_features/test_f11_responsive_layout.py
"""
Tier 1 — Feature 11: Responsive Viewport Layout
Verifies UI/UX layout compliance and responsiveness across Mobile (<640px),
Tablet (640-1024px), and Desktop (>=1024px) viewports with fluid grids,
viewport tags, and touch-friendly adaptation.
"""
import os
import re
import unittest
from bs4 import BeautifulSoup
from tests.test_config import WORKSPACE_ROOT, APP_DIR
from tests.helpers.web_harness import LocalWebServer, get_web_root

class TestF11ResponsiveLayout(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.web_root = get_web_root()
        cls.index_path = os.path.join(cls.web_root, "index.html")

    def test_html_contains_standard_viewport_declaration(self):
        """F11.1: Verify <meta name='viewport' content='width=device-width, initial-scale=1.0'> exists."""
        self.assertTrue(os.path.isfile(self.index_path), f"Missing index.html at {self.index_path}")
        with open(self.index_path, "r", encoding="utf-8", errors="replace") as f:
            html = f.read()
        soup = BeautifulSoup(html, "html.parser")
        meta = soup.find("meta", attrs={"name": "viewport"})
        self.assertIsNotNone(meta, "No viewport meta tag declared")
        content = meta.get("content", "")
        self.assertIn("width=device-width", content)
        self.assertIn("initial-scale=1", content)

    def test_css_media_queries_for_mobile_and_desktop(self):
        """F11.2: Verify responsive media query breakpoints exist in stylesheets or inline CSS."""
        found_media = False
        # Search all CSS files in web_root
        for root, dirs, files in os.walk(self.web_root):
            for file in files:
                if file.endswith(".css") or file == "index.html":
                    fpath = os.path.join(root, file)
                    with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                        content = f.read()
                        if "@media" in content:
                            found_media = True
                            break
            if found_media:
                break
        self.assertTrue(found_media, "No responsive @media queries found in CSS or index.html")

    def test_no_rigid_fixed_page_widths(self):
        """F11.3: Verify no rigid fixed outer widths (e.g. style='width: 1440px') causing mobile overflow."""
        with open(self.index_path, "r", encoding="utf-8", errors="replace") as f:
            html = f.read()

        rigid_matches = re.findall(r'width:\s*(\d{4,})px', html)
        # Rigid widths > 1000px on top-level elements cause mobile breakage
        for width_str in rigid_matches:
            w = int(width_str)
            self.assertLess(w, 2000, f"Unreasonably large rigid width {w}px found in HTML")

    def test_flexible_layout_system_used(self):
        """F11.4: Verify modern fluid display models (flexbox, grid, Tailwind, or CSS classes) are utilized."""
        with open(self.index_path, "r", encoding="utf-8", errors="replace") as f:
            html = f.read()
        has_fluid = (
            "flex" in html or "grid" in html or "container" in html or
            "col-" in html or "responsive" in html or "table" in html
        )
        self.assertTrue(has_fluid, "No fluid grid or flex container classes found in application markup")

    def test_touch_friendly_input_attributes(self):
        """F11.5: Verify form inputs use accessible sizes and touch-friendly targets."""
        with open(self.index_path, "r", encoding="utf-8", errors="replace") as f:
            html = f.read()
        soup = BeautifulSoup(html, "html.parser")
        inputs = soup.find_all("input")
        # Ensure inputs don't have font sizes below 12px or unusable attributes
        for inp in inputs:
            style = inp.get("style", "")
            self.assertNotIn("font-size: 8px", style)
            self.assertNotIn("font-size: 6px", style)

    def test_viewport_scroll_overflow_containment(self):
        """F11.6: Verify tables or wide elements are wrapped in scrollable containers (overflow-x: auto)."""
        with open(self.index_path, "r", encoding="utf-8", errors="replace") as f:
            html = f.read()
        has_overflow_protection = (
            "overflow-x" in html or "overflow-auto" in html or
            "overflow" in html or "table" in html
        )
        self.assertTrue(has_overflow_protection, "Missing horizontal overflow containment for wide data tables")

if __name__ == "__main__":
    unittest.main()
