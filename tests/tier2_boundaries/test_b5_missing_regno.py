# tests/tier2_boundaries/test_b5_missing_regno.py
"""
Tier 2 — Boundary Case B5: Missing Registration Number Handling
Verifies graceful handling of candidates without registration numbers (empty string,
None, or 'Not Available') without rendering crashes, null-pointer exceptions,
or broken UI modals.
"""
import unittest
from tests.helpers.data_loader import DataLoader
from tests.helpers.query_engine import QueryEngine

class TestB5MissingRegno(unittest.TestCase):
    def setUp(self):
        self.loader = DataLoader.get_instance()
        self.students = self.loader.get_raw_student_records()
        if not self.students:
            self.students = self.loader.get_all_students()

    def test_missing_regno_gracefully_represented(self):
        """B5.1: Verify registration number field in student records is either None, empty string, or string."""
        for s in self.students[:50]:
            reg = s.get("reg_no") or s.get("regno")
            # Must not be undefined or arbitrary object
            self.assertTrue(reg is None or isinstance(reg, str))

    def test_search_functions_when_candidate_has_no_regno(self):
        """B5.2: Verify search by roll number succeeds when registration number is missing/blank."""
        candidates_without_reg = [
            s for s in self.students if not (s.get("reg_no") or s.get("regno"))
        ]
        self.assertGreater(len(candidates_without_reg), 0, "No candidates without registration number found")
        sample = candidates_without_reg[0]
        roll = str(sample.get("roll"))

        results = QueryEngine.filter_students(self.students, search_term=roll)
        self.assertGreater(len(results), 0)
        self.assertEqual(str(results[0].get("roll")), roll)

    def test_query_with_empty_or_whitespace_regno_does_not_crash(self):
        """B5.3: Verify querying with whitespace or empty search strings does not crash filter engine."""
        results = QueryEngine.filter_students(self.students, search_term="")
        self.assertEqual(len(results), len(self.students))

        results_ws = QueryEngine.filter_students(self.students, search_term="   ")
        self.assertEqual(len(results_ws), len(self.students))

    def test_filter_pipeline_with_none_fields(self):
        """B5.4: Verify filter pipeline handles student objects with None fields without TypeError."""
        mock_students = [
            {"roll": "999001", "name": None, "reg_no": None, "stream": None, "status": None, "gpa": None},
            {"roll": "999002", "name": "TEST", "reg_no": "", "stream": "Science", "status": "PASSED", "gpa": 4.5}
        ]
        filtered = QueryEngine.filter_students(mock_students, stream="Science", min_gpa=4.0)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["roll"], "999002")

    def test_kpi_calculation_with_missing_gpa_or_status(self):
        """B5.5: Verify calculate_kpi handles records with None or malformed GPA without crashing."""
        malformed = [
            {"roll": "1", "status": None, "gpa": None},
            {"roll": "2", "status": "FAIL", "gpa": "invalid"},
            {"roll": "3", "status": "PASSED", "gpa": 5.0}
        ]
        kpi = QueryEngine.calculate_kpi(malformed)
        self.assertEqual(kpi["total"], 3)
        self.assertEqual(kpi["passed"], 1)
        self.assertEqual(kpi["failed"], 2)
        self.assertEqual(kpi["gpa5_count"], 1)

if __name__ == "__main__":
    unittest.main()
