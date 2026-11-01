# tests/tier1_features/test_f5_json_syntax.py
"""
Tier 1 — Feature 5: Valid JSON Syntax in Datasets
Verifies valid JSON syntax in all college JSON files, consolidated datasets,
manifest metadata, and raw examination assets with proper UTF-8 character encoding.
"""
import os
import json
import glob
import unittest
from tests.test_config import (
    SURVEY_JSON, WORKSPACE_ROOT, APP_DIR,
    APP_PUBLIC_DATA_DIR, ROOT_PUBLIC_DATA_DIR
)
from tests.helpers.data_loader import DataLoader

class TestF5JsonSyntax(unittest.TestCase):
    def setUp(self):
        self.loader = DataLoader.get_instance()

    def test_master_survey_json_syntax(self):
        """F5.1: Verify master college dataset JSON parses cleanly without syntax errors."""
        self.assertTrue(os.path.isfile(SURVEY_JSON), f"Master dataset {SURVEY_JSON} missing")
        with open(SURVEY_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertIsInstance(data, list)
            self.assertEqual(len(data), 24)

    def test_metadata_json_syntax(self):
        """F5.2: Verify metadata.json parses cleanly with valid schema."""
        meta_path = os.path.join(WORKSPACE_ROOT, "metadata.json")
        if os.path.isfile(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.assertIsInstance(data, dict)
                self.assertIn("name", data)

    def test_package_json_syntax(self):
        """F5.3: Verify package.json syntax in workspace and application directories."""
        pkg_paths = [
            os.path.join(WORKSPACE_ROOT, "package.json"),
            os.path.join(APP_DIR, "package.json")
        ]
        found = False
        for p in pkg_paths:
            if os.path.isfile(p):
                found = True
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.assertIsInstance(data, dict)
                    self.assertIn("scripts", data)
        self.assertTrue(found, "At least one package.json must exist and be valid JSON")

    def test_raw_student_asset_json_syntax(self):
        """F5.4: Verify raw student result JSON asset files parse cleanly."""
        pattern = os.path.join(WORKSPACE_ROOT, "public", "assets", "aistudio", "*.json")
        files = glob.glob(pattern)
        self.assertGreater(len(files), 0, "Expected at least one raw results JSON asset file")
        for fpath in files:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.assertIsInstance(data, list)
                for item in data[:5]:
                    self.assertIn("roll", item)
                    self.assertIn("data", item)

    def test_college_json_files_if_generated(self):
        """F5.5: Verify any generated college JSON files in colleges/ have valid JSON syntax."""
        colleges_dir = self.loader.get_colleges_dir()
        if colleges_dir:
            json_files = [f for f in os.listdir(colleges_dir) if f.endswith(".json")]
            for jf in json_files:
                fpath = os.path.join(colleges_dir, jf)
                with open(fpath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.assertIsInstance(data, dict)
                    self.assertIn("eiin", data)

    def test_utf8_encoding_bengali_characters(self):
        """F5.6: Verify UTF-8 Bengali character strings are valid and not corrupted."""
        colleges = self.loader.get_all_colleges()
        for c in colleges:
            bengali_name = c.get("bengali_name") or ""
            if bengali_name:
                # Ensure no replacement character (U+FFFD) or raw escaped question marks
                self.assertNotIn("\ufffd", bengali_name)
                # Ensure non-empty unicode string
                self.assertGreater(len(bengali_name), 3)

if __name__ == "__main__":
    unittest.main()
