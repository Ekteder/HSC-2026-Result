# tests/tier2_boundaries/test_b1_low_pass_colleges.py
"""
Tier 2 — Boundary Case B1: Low and Zero Pass Rate Colleges
Tests handling of extreme low-performing institutions including Makrail Karim Khalek (0.00%),
Juralia Bahumukhi (4.17%), Birshestra Noormohammad (13.33%), Laxmipasha (14.41%),
and Habokhali (14.52%), verifying no division-by-zero or NaN rendering bugs.
"""
import unittest
from tests.test_config import COLLEGES_ZERO_OR_LOW_PASS
from tests.helpers.data_loader import DataLoader
from tests.helpers.query_engine import QueryEngine

class TestB1LowPassColleges(unittest.TestCase):
    def setUp(self):
        self.loader = DataLoader.get_instance()
        self.colleges = self.loader.get_all_colleges()
        self.college_map = {int(c.get("eiin")): c for c in self.colleges}

    def test_makrail_karim_khalek_zero_percent_pass_rate(self):
        """B1.1: Verify Makrail Karim Khalek (EIIN 118404) has exactly 0 passed examinees and 0.00% pass rate."""
        eiin = 118404
        self.assertIn(eiin, self.college_map)
        col = self.college_map[eiin]
        self.assertEqual(col.get("total_passed"), 0)
        self.assertEqual(float(col.get("pass_rate")), 0.0)
        self.assertEqual(col.get("total_gpa5"), 0)
        self.assertEqual(col.get("total_appeared"), 49)

    def test_juralia_bahumukhi_single_passing_student(self):
        """B1.2: Verify Juralia Bahumukhi (EIIN 118522) has exactly 1 passed candidate out of 24 (4.17%)."""
        eiin = 118522
        self.assertIn(eiin, self.college_map)
        col = self.college_map[eiin]
        self.assertEqual(col.get("total_passed"), 1)
        self.assertEqual(col.get("total_appeared"), 24)
        self.assertAlmostEqual(float(col.get("pass_rate")), 4.17, delta=0.05)

    def test_birshestra_noormohammad_low_pass_rate(self):
        """B1.3: Verify Birshestra Noormohammad (EIIN 131996) has 6 passed candidates out of 45 (13.33%)."""
        eiin = 131996
        self.assertIn(eiin, self.college_map)
        col = self.college_map[eiin]
        self.assertEqual(col.get("total_passed"), 6)
        self.assertEqual(col.get("total_appeared"), 45)
        self.assertAlmostEqual(float(col.get("pass_rate")), 13.33, delta=0.05)

    def test_laxmipasha_low_pass_with_gpa5_anomaly(self):
        """B1.4: Verify Laxmipasha (EIIN 118436) has 34 passed out of 236 (14.41%) yet achieves 3 GPA-5s."""
        eiin = 118436
        self.assertIn(eiin, self.college_map)
        col = self.college_map[eiin]
        self.assertEqual(col.get("total_passed"), 34)
        self.assertEqual(col.get("total_appeared"), 236)
        self.assertAlmostEqual(float(col.get("pass_rate")), 14.41, delta=0.05)
        self.assertEqual(col.get("total_gpa5"), 3)

    def test_habokhali_adarsha_pass_metrics(self):
        """B1.5: Verify Habokhali Adarsha (EIIN 118531) has 9 passed out of 62 (14.52%)."""
        eiin = 118531
        self.assertIn(eiin, self.college_map)
        col = self.college_map[eiin]
        self.assertEqual(col.get("total_passed"), 9)
        self.assertEqual(col.get("total_appeared"), 62)
        self.assertAlmostEqual(float(col.get("pass_rate")), 14.52, delta=0.05)

    def test_empty_results_kpi_calculation_safety(self):
        """B1.6: Verify QueryEngine.calculate_kpi handles empty student lists safely without ZeroDivisionError."""
        kpi = QueryEngine.calculate_kpi([])
        self.assertEqual(kpi["total"], 0)
        self.assertEqual(kpi["passed"], 0)
        self.assertEqual(kpi["pass_rate"], 0.0)
        self.assertEqual(kpi["gpa5_count"], 0)

if __name__ == "__main__":
    unittest.main()
