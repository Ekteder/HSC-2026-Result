# tests/tier1_features/test_f9_multifaceted_filter.py
"""
Tier 1 — Feature 9: Multi-Faceted Filter Engine
Verifies client-side filtering across College EIIN, Upazila, Academic Stream,
Result Status, and GPA range boundaries.
"""
import unittest
from tests.helpers.data_loader import DataLoader
from tests.helpers.query_engine import QueryEngine

class TestF9MultifacetedFilter(unittest.TestCase):
    def setUp(self):
        self.loader = DataLoader.get_instance()
        self.students = self.loader.get_raw_student_records()
        if not self.students:
            self.students = self.loader.get_all_students()

    def test_filter_by_college_eiin(self):
        """F9.1: Verify filtering by college EIIN returns candidates exclusively from that institution."""
        self.assertTrue(len(self.students) > 0)
        sample = self.students[0]
        # EIIN might be in college_eiin, eiin, or institute name
        eiin = sample.get("eiin") or sample.get("college_eiin")
        if not eiin and "institute" in sample:
            import re
            m = re.search(r'\((\d+)\)', sample["institute"])
            if m:
                eiin = m.group(1)

        if eiin:
            filtered = QueryEngine.filter_students(self.students, college_eiin=eiin)
            self.assertGreater(len(filtered), 0)
            for s in filtered:
                s_inst = s.get("institute", "")
                self.assertIn(str(eiin), str(s.get("eiin", "") or s.get("college_eiin", "") or s_inst))

    def test_filter_by_academic_stream(self):
        """F9.2: Verify filtering by stream (Science) returns only Science candidates."""
        filtered_sci = QueryEngine.filter_students(self.students, stream="Science")
        for s in filtered_sci:
            s_stream = str(s.get("stream", "") or s.get("group", "")).upper()
            self.assertEqual(s_stream, "SCIENCE")

    def test_filter_by_status_passed_and_failed(self):
        """F9.3: Verify filtering by status PASSED vs FAILED partitions candidates cleanly."""
        passed = QueryEngine.filter_students(self.students, status="PASSED")
        failed = QueryEngine.filter_students(self.students, status="FAILED")

        for s in passed:
            st = str(s.get("status", "")).upper()
            self.assertTrue("PASS" in st or float(s.get("gpa", 0.0) or 0.0) > 0.0)

        for s in failed:
            st = str(s.get("status", "")).upper()
            self.assertTrue("FAIL" in st or st in ["F1", "F2"])

    def test_filter_by_gpa_range(self):
        """F9.4: Verify filtering by GPA range [4.00, 5.00] includes only candidates in that bracket."""
        gpa_4_to_5 = QueryEngine.filter_students(self.students, min_gpa=4.00, max_gpa=5.00)
        for s in gpa_4_to_5:
            gpa = float(s.get("gpa", 0.0) or 0.0)
            self.assertGreaterEqual(gpa, 4.00)
            self.assertLessEqual(gpa, 5.00)

    def test_filter_gpa_5_exact(self):
        """F9.5: Verify filtering by min_gpa=5.00 and max_gpa=5.00 returns only GPA 5.00 achievers."""
        gpa5_list = QueryEngine.filter_students(self.students, min_gpa=5.00, max_gpa=5.00)
        for s in gpa5_list:
            gpa = float(s.get("gpa", 0.0) or 0.0)
            self.assertAlmostEqual(gpa, 5.00, places=2)

    def test_combined_stream_and_status_filter(self):
        """F9.6: Verify compound filter: Stream=Science AND Status=PASSED."""
        sci_passed = QueryEngine.filter_students(self.students, stream="Science", status="PASSED")
        for s in sci_passed:
            s_stream = str(s.get("stream", "") or s.get("group", "")).upper()
            st = str(s.get("status", "")).upper()
            self.assertEqual(s_stream, "SCIENCE")
            self.assertTrue("PASS" in st or float(s.get("gpa", 0.0) or 0.0) > 0.0)

if __name__ == "__main__":
    unittest.main()
