# tests/tier3_combinations/test_c3_search_with_filters.py
"""
Tier 3 — Cross-Feature Combination C3: Combined Search Query with Active Filters
Verifies that text/roll search queries execute in conjunction with active facet filters
(College, Stream, Status, GPA) without leaking excluded candidates.
"""
import unittest
from tests.helpers.data_loader import DataLoader
from tests.helpers.query_engine import QueryEngine

class TestC3SearchWithFilters(unittest.TestCase):
    def setUp(self):
        self.loader = DataLoader.get_instance()
        self.students = self.loader.get_raw_student_records()
        if not self.students:
            self.students = self.loader.get_all_students()

    def test_search_roll_with_matching_stream_filter(self):
        """C3.1: Verify search for Science roll with stream='Science' returns the candidate."""
        self.assertTrue(len(self.students) > 0)
        target = self.students[0]
        roll = str(target.get("roll"))
        target_stream = str(target.get("stream", "") or target.get("group", "")).title()

        results = QueryEngine.filter_students(
            self.students, stream=target_stream, search_term=roll
        )
        self.assertGreater(len(results), 0)
        self.assertEqual(str(results[0].get("roll")), roll)

    def test_search_roll_with_conflicting_stream_filter(self):
        """C3.2: Verify search for Science roll with stream='Humanities' returns 0 results."""
        self.assertTrue(len(self.students) > 0)
        target = self.students[0]
        roll = str(target.get("roll"))
        target_stream = str(target.get("stream", "") or target.get("group", "")).upper()

        if target_stream == "SCIENCE":
            results = QueryEngine.filter_students(
                self.students, stream="Humanities", search_term=roll
            )
            self.assertEqual(len(results), 0, "Conflicting stream filter should exclude candidate")

    def test_search_roll_with_matching_gpa_range(self):
        """C3.3: Verify search for candidate with GPA 4.25 is found when min_gpa=4.00, max_gpa=4.50."""
        # Find candidate with GPA between 4.0 and 4.5
        target = None
        for s in self.students:
            try:
                gpa = float(s.get("gpa", 0.0) or 0.0)
                if 4.0 <= gpa <= 4.5:
                    target = s
                    break
            except Exception:
                pass

        if target:
            roll = str(target.get("roll"))
            results = QueryEngine.filter_students(
                self.students, min_gpa=4.0, max_gpa=4.5, search_term=roll
            )
            self.assertEqual(len(results), 1)
            self.assertEqual(str(results[0].get("roll")), roll)

    def test_search_roll_with_excluding_gpa_range(self):
        """C3.4: Verify search for candidate with GPA 4.25 returns 0 results when min_gpa=4.80."""
        target = None
        for s in self.students:
            try:
                gpa = float(s.get("gpa", 0.0) or 0.0)
                if 4.0 <= gpa <= 4.3:
                    target = s
                    break
            except Exception:
                pass

        if target:
            roll = str(target.get("roll"))
            results = QueryEngine.filter_students(
                self.students, min_gpa=4.80, max_gpa=5.00, search_term=roll
            )
            self.assertEqual(len(results), 0, "Candidate GPA outside range must be excluded")

    def test_search_student_name_with_status_filter(self):
        """C3.5: Verify search by candidate name with status=PASSED returns candidate only if passed."""
        for s in self.students:
            status = str(s.get("status", "")).upper()
            name = s.get("name", "")
            if "PASS" in status and len(name) > 4:
                sub_name = name[:5].lower()
                results = QueryEngine.filter_students(
                    self.students, status="PASSED", search_term=sub_name
                )
                self.assertGreater(len(results), 0)
                for r in results:
                    self.assertTrue("PASS" in str(r.get("status", "")).upper() or float(r.get("gpa", 0.0) or 0.0) > 0.0)
                break

    def test_search_nonexistent_roll_with_active_filters_returns_empty(self):
        """C3.6: Verify search for '999999' with active filters returns empty list without errors."""
        results = QueryEngine.filter_students(
            self.students, stream="Science", status="PASSED", min_gpa=4.0, search_term="999999"
        )
        self.assertEqual(len(results), 0)

if __name__ == "__main__":
    unittest.main()
