# tests/tier3_combinations/test_c4_upazila_stream_stats.py
"""
Tier 3 — Cross-Feature Combination C4: Upazila & Stream Cross-Tabulation
Verifies that institutional distributions across Narail Sadar, Lohagara, and Kalia
reconcile across examinees, passing candidates, and GPA-5 recipients.
"""
import unittest
from tests.test_config import EXPECTED_UPAZILA_BREAKDOWN, EXPECTED_TOTAL_REGISTERED, EXPECTED_TOTAL_PASSED
from tests.helpers.data_loader import DataLoader

class TestC4UpazilaStreamStats(unittest.TestCase):
    def setUp(self):
        self.loader = DataLoader.get_instance()
        self.colleges = self.loader.get_all_colleges()

    def test_narail_sadar_upazila_totals(self):
        """C4.1: Verify Narail Sadar (12 colleges) totals: 2,356 enrolled, 982 passed, 80 GPA-5s."""
        sadar_colleges = [c for c in self.colleges if "Sadar" in c.get("upazila", "")]
        self.assertEqual(len(sadar_colleges), 12)
        tot_enrolled = sum(c.get("total_appeared", 0) for c in sadar_colleges)
        tot_passed = sum(c.get("total_passed", 0) for c in sadar_colleges)
        tot_gpa5 = sum(c.get("total_gpa5", 0) for c in sadar_colleges)

        expected = EXPECTED_UPAZILA_BREAKDOWN["Narail Sadar"]
        self.assertEqual(tot_enrolled, expected["enrolled"])
        self.assertEqual(tot_passed, expected["passed"])
        self.assertEqual(tot_gpa5, expected["gpa5"])

    def test_lohagara_upazila_totals(self):
        """C4.2: Verify Lohagara (7 colleges) totals: 1,751 enrolled, 534 passed, 19 GPA-5s."""
        lohagara_colleges = [c for c in self.colleges if "Lohagara" in c.get("upazila", "")]
        self.assertEqual(len(lohagara_colleges), 7)
        tot_enrolled = sum(c.get("total_appeared", 0) for c in lohagara_colleges)
        tot_passed = sum(c.get("total_passed", 0) for c in lohagara_colleges)
        tot_gpa5 = sum(c.get("total_gpa5", 0) for c in lohagara_colleges)

        expected = EXPECTED_UPAZILA_BREAKDOWN["Lohagara"]
        self.assertEqual(tot_enrolled, expected["enrolled"])
        self.assertEqual(tot_passed, expected["passed"])
        self.assertEqual(tot_gpa5, expected["gpa5"])

    def test_kalia_upazila_totals(self):
        """C4.3: Verify Kalia (5 colleges) totals: 958 enrolled, 260 passed, 6 GPA-5s."""
        kalia_colleges = [c for c in self.colleges if "Kalia" in c.get("upazila", "") or "Naragati" in c.get("upazila", "")]
        self.assertEqual(len(kalia_colleges), 5)
        tot_enrolled = sum(c.get("total_appeared", 0) for c in kalia_colleges)
        tot_passed = sum(c.get("total_passed", 0) for c in kalia_colleges)
        tot_gpa5 = sum(c.get("total_gpa5", 0) for c in kalia_colleges)

        expected = EXPECTED_UPAZILA_BREAKDOWN["Kalia"]
        self.assertEqual(tot_enrolled, expected["enrolled"])
        self.assertEqual(tot_passed, expected["passed"])
        self.assertEqual(tot_gpa5, expected["gpa5"])

    def test_upazila_pass_rate_rankings(self):
        """C4.4: Verify upazila pass rate ranking: Narail Sadar (41.68%) > Lohagara (30.50%) > Kalia (27.14%)."""
        sadar_rate = EXPECTED_UPAZILA_BREAKDOWN["Narail Sadar"]["pass_rate"]
        lohagara_rate = EXPECTED_UPAZILA_BREAKDOWN["Lohagara"]["pass_rate"]
        kalia_rate = EXPECTED_UPAZILA_BREAKDOWN["Kalia"]["pass_rate"]

        self.assertGreater(sadar_rate, lohagara_rate)
        self.assertGreater(lohagara_rate, kalia_rate)

    def test_sum_of_upazilas_reconciles_to_100_percent_of_district(self):
        """C4.5: Verify the three upazilas sum to exactly 100% of district examinees and passed students."""
        enrolled_sum = sum(u["enrolled"] for u in EXPECTED_UPAZILA_BREAKDOWN.values())
        passed_sum = sum(u["passed"] for u in EXPECTED_UPAZILA_BREAKDOWN.values())
        self.assertEqual(enrolled_sum, EXPECTED_TOTAL_REGISTERED)
        self.assertEqual(passed_sum, EXPECTED_TOTAL_PASSED)

if __name__ == "__main__":
    unittest.main()
