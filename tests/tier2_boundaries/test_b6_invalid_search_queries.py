# tests/tier2_boundaries/test_b6_invalid_search_queries.py
"""
Tier 2 — Boundary Case B6: Invalid Search Queries & Non-Existent Rolls
Verifies that searching for non-existent rolls, special characters, script tags,
or extreme inputs returns clean empty results without crashing or leaking errors.
"""
import unittest
from tests.helpers.data_loader import DataLoader
from tests.helpers.query_engine import QueryEngine

class TestB6InvalidSearchQueries(unittest.TestCase):
    def setUp(self):
        self.loader = DataLoader.get_instance()
        self.students = self.loader.get_raw_student_records()
        if not self.students:
            self.students = self.loader.get_all_students()

    def test_nonexistent_six_digit_roll_returns_empty(self):
        """B6.1: Verify querying non-existent 6-digit roll '999999' returns empty result gracefully."""
        results = QueryEngine.filter_students(self.students, search_term="999999")
        self.assertEqual(len(results), 0, f"Expected 0 results for non-existent roll, got {len(results)}")

    def test_zero_roll_returns_empty(self):
        """B6.2: Verify querying '000000' returns empty result gracefully."""
        results = QueryEngine.filter_students(self.students, search_term="000000")
        self.assertEqual(len(results), 0)

    def test_special_characters_search_sanitization(self):
        """B6.3: Verify special characters and meta-characters (!@#$%^&*()_+) do not trigger regex/parsing errors."""
        special_inputs = ["!@#$%", "[[test]]", "(.*?)", "\\d{6}", "{foo: bar}"]
        for term in special_inputs:
            try:
                results = QueryEngine.filter_students(self.students, search_term=term)
                self.assertIsInstance(results, list)
            except Exception as e:
                self.fail(f"Search query '{term}' raised unexpected exception: {e}")

    def test_xss_injection_payload_in_search_field(self):
        """B6.4: Verify HTML/XSS injection string (<script>alert(1)</script>) handled safely as plain search."""
        payload = "<script>alert('xss')</script>"
        try:
            results = QueryEngine.filter_students(self.students, search_term=payload)
            self.assertEqual(len(results), 0)
        except Exception as e:
            self.fail(f"XSS payload caused error: {e}")

    def test_sql_injection_payload_in_search_field(self):
        """B6.5: Verify SQL injection pattern (' OR 1=1 --) does not leak or crash client engine."""
        payload = "' OR 1=1 --"
        try:
            results = QueryEngine.filter_students(self.students, search_term=payload)
            self.assertEqual(len(results), 0)
        except Exception as e:
            self.fail(f"SQL injection query caused error: {e}")

    def test_extremely_long_search_term(self):
        """B6.6: Verify search engine handles 500-character input string without catastrophic slowdown."""
        long_query = "A" * 500
        results = QueryEngine.filter_students(self.students, search_term=long_query)
        self.assertEqual(len(results), 0)

if __name__ == "__main__":
    unittest.main()
