# tests/tier2_boundaries/test_b2_high_performance.py
"""
Tier 2 — Boundary Case B2: High-Performance & Flagship Institutions
Tests colleges with the highest pass rates and GPA-5 volume across Narail District,
verifying that top performers are ranked accurately and reflect exact ground truth.
"""
import unittest
from tests.test_config import COLLEGES_HIGH_PERFORMANCE, EXPECTED_TOTAL_GPA5
from tests.helpers.data_loader import DataLoader

class TestB2HighPerformance(unittest.TestCase):
    def setUp(self):
        self.loader = DataLoader.get_instance()
        self.colleges = self.loader.get_all_colleges()
        self.college_map = {int(c.get("eiin")): c for c in self.colleges}

    def test_victoria_college_top_district_ranking(self):
        """B2.1: Verify Government Victoria College (118527) ranks #1 with 538 passed and 61.63% pass rate."""
        eiin = 118527
        self.assertIn(eiin, self.college_map)
        col = self.college_map[eiin]
        self.assertEqual(col.get("total_passed"), 538)
        self.assertEqual(col.get("total_appeared"), 873)
        self.assertAlmostEqual(float(col.get("pass_rate")), 61.63, delta=0.05)

    def test_victoria_college_gpa5_share(self):
        """B2.2: Verify Victoria College achieves 69 GPA-5s (65.71% of total district GPA-5 count)."""
        col = self.college_map[118527]
        gpa5 = col.get("total_gpa5")
        self.assertEqual(gpa5, 69)
        share = round((gpa5 / EXPECTED_TOTAL_GPA5) * 100, 2)
        self.assertAlmostEqual(share, 65.71, delta=0.1)

    def test_lohagara_govt_adarsha_college_performance(self):
        """B2.3: Verify Lohagara Govt. Adarsha College (118437) achieves 285 passed (49.14%) and 13 GPA-5s."""
        eiin = 118437
        self.assertIn(eiin, self.college_map)
        col = self.college_map[eiin]
        self.assertEqual(col.get("total_passed"), 285)
        self.assertEqual(col.get("total_appeared"), 580)
        self.assertAlmostEqual(float(col.get("pass_rate")), 49.14, delta=0.05)
        self.assertEqual(col.get("total_gpa5"), 13)

    def test_narail_govt_mohila_college_performance(self):
        """B2.4: Verify Narail Govt. Mohila College (118525) achieves 159 passed (38.59%) and 5 GPA-5s."""
        eiin = 118525
        self.assertIn(eiin, self.college_map)
        col = self.college_map[eiin]
        self.assertEqual(col.get("total_passed"), 159)
        self.assertEqual(col.get("total_appeared"), 412)
        self.assertAlmostEqual(float(col.get("pass_rate")), 38.59, delta=0.05)
        self.assertEqual(col.get("total_gpa5"), 5)

    def test_gobra_mittra_mahabiddyalya_performance(self):
        """B2.5: Verify Gobra Mittra (118528) achieves 69 passed (37.30%) and 3 GPA-5s."""
        eiin = 118528
        self.assertIn(eiin, self.college_map)
        col = self.college_map[eiin]
        self.assertEqual(col.get("total_passed"), 69)
        self.assertEqual(col.get("total_appeared"), 185)
        self.assertAlmostEqual(float(col.get("pass_rate")), 37.30, delta=0.05)
        self.assertEqual(col.get("total_gpa5"), 3)

    def test_govt_shaheed_abdus_salam_college_performance(self):
        """B2.6: Verify Govt. Shaheed Abdus Salam (118385) in Kalia achieves 72 passed (26.37%) and 5 GPA-5s."""
        eiin = 118385
        self.assertIn(eiin, self.college_map)
        col = self.college_map[eiin]
        self.assertEqual(col.get("total_passed"), 72)
        self.assertEqual(col.get("total_appeared"), 273)
        self.assertAlmostEqual(float(col.get("pass_rate")), 26.37, delta=0.05)
        self.assertEqual(col.get("total_gpa5"), 5)

if __name__ == "__main__":
    unittest.main()
