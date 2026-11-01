# tests/tier3_combinations/test_c2_stream_status_gpa.py
"""
Tier 3 — Cross-Feature Combination C2: Stream, Status, and GPA Range Intersections
Verifies multi-criteria filtering across Academic Stream, Pass/Fail Result Status,
and GPA boundaries simultaneously.
"""
import unittest
from tests.test_config import EXPECTED_STREAM_BREAKDOWN
from tests.helpers.data_loader import DataLoader
from tests.helpers.query_engine import QueryEngine

class TestC2StreamStatusGpa(unittest.TestCase):
    def setUp(self):
        self.loader = DataLoader.get_instance()
        self.colleges = self.loader.get_all_colleges()
        self.students = self.loader.get_raw_student_records()
        if not self.students:
            self.students = self.loader.get_all_students()

    def test_science_passed_gpa5_count(self):
        """C2.1: Verify Science + PASSED + GPA 5.00 equals exactly 56 candidates district-wide."""
        sci_gpa5 = sum(
            c.get("stream_stats", {}).get("Science", {}).get("gpa5", 0)
            for c in self.colleges
        )
        self.assertEqual(sci_gpa5, EXPECTED_STREAM_BREAKDOWN["Science"]["gpa5"])

    def test_humanities_passed_gpa5_count(self):
        """C2.2: Verify Humanities + PASSED + GPA 5.00 equals exactly 45 candidates district-wide."""
        hum_gpa5 = sum(
            c.get("stream_stats", {}).get("Humanities", {}).get("gpa5", 0)
            for c in self.colleges
        )
        self.assertEqual(hum_gpa5, EXPECTED_STREAM_BREAKDOWN["Humanities"]["gpa5"])

    def test_business_studies_passed_gpa5_count(self):
        """C2.3: Verify Business Studies + PASSED + GPA 5.00 equals exactly 4 candidates district-wide."""
        bus_gpa5 = sum(
            c.get("stream_stats", {}).get("Business Studies", {}).get("gpa5", 0)
            for c in self.colleges
        )
        self.assertEqual(bus_gpa5, EXPECTED_STREAM_BREAKDOWN["Business Studies"]["gpa5"])

    def test_science_passed_with_high_gpa_range_filter(self):
        """C2.4: Verify filter pipeline for Stream=Science + Status=PASSED + GPA [4.00, 5.00]."""
        filtered = QueryEngine.filter_students(
            self.students, stream="Science", status="PASSED", min_gpa=4.00, max_gpa=5.00
        )
        for s in filtered:
            self.assertEqual(str(s.get("stream", "") or s.get("group", "")).upper(), "SCIENCE")
            self.assertGreaterEqual(float(s.get("gpa", 0.0) or 0.0), 4.00)
            self.assertLessEqual(float(s.get("gpa", 0.0) or 0.0), 5.00)

    def test_science_failed_students_gpa_zero(self):
        """C2.5: Verify filter pipeline for Stream=Science + Status=FAILED returns only candidates with GPA=0.0."""
        filtered = QueryEngine.filter_students(
            self.students, stream="Science", status="FAILED"
        )
        for s in filtered:
            self.assertEqual(str(s.get("stream", "") or s.get("group", "")).upper(), "SCIENCE")
            gpa = float(s.get("gpa", 0.0) or 0.0)
            self.assertEqual(gpa, 0.0)

    def test_compound_kpi_for_stream_slice(self):
        """C2.6: Verify KPI calculation for Science stream slice matches expected metrics."""
        sci_students = [
            s for s in self.students
            if str(s.get("stream", "") or s.get("group", "")).upper() == "SCIENCE"
        ]
        if sci_students:
            kpi = QueryEngine.calculate_kpi(sci_students)
            self.assertEqual(kpi["total"], len(sci_students))
            self.assertEqual(kpi["passed"] + kpi["failed"], len(sci_students))

if __name__ == "__main__":
    unittest.main()
