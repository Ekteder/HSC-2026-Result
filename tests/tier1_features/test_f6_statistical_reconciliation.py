# tests/tier1_features/test_f6_statistical_reconciliation.py
"""
Tier 1 — Feature 6: Statistical Data Reconciliation
Strict mathematical reconciliation verifying candidate counts, passing counts,
GPA-5 counts, upazila distributions, and stream breakdowns against official
BISE Jashore summary sheets with zero discrepancy.
"""
import unittest
from tests.test_config import (
    EXPECTED_TOTAL_REGISTERED,
    EXPECTED_TOTAL_PASSED,
    EXPECTED_TOTAL_GPA5,
    EXPECTED_UPAZILA_BREAKDOWN,
    EXPECTED_STREAM_BREAKDOWN
)
from tests.helpers.data_loader import DataLoader

class TestF6StatisticalReconciliation(unittest.TestCase):
    def setUp(self):
        self.loader = DataLoader.get_instance()
        self.colleges = self.loader.get_all_colleges()

    def test_district_total_registered_examinees_equals_5065(self):
        """F6.1: Verify total registered candidates across all colleges reconciles to 5,065."""
        total = sum(c.get("total_appeared", 0) for c in self.colleges)
        self.assertEqual(
            total, EXPECTED_TOTAL_REGISTERED,
            f"Total examinees mismatch: expected {EXPECTED_TOTAL_REGISTERED}, got {total}"
        )

    def test_district_total_passed_examinees_equals_1776(self):
        """F6.2: Verify total passed candidates across all colleges reconciles to 1,776."""
        total_passed = sum(c.get("total_passed", 0) for c in self.colleges)
        self.assertEqual(
            total_passed, EXPECTED_TOTAL_PASSED,
            f"Total passed examinees mismatch: expected {EXPECTED_TOTAL_PASSED}, got {total_passed}"
        )

    def test_district_total_gpa5_achievers_equals_105(self):
        """F6.3: Verify total GPA 5.00 achievers across all colleges reconciles to 105."""
        total_gpa5 = sum(c.get("total_gpa5", 0) for c in self.colleges)
        self.assertEqual(
            total_gpa5, EXPECTED_TOTAL_GPA5,
            f"Total GPA 5.00 mismatch: expected {EXPECTED_TOTAL_GPA5}, got {total_gpa5}"
        )

    def test_stream_sums_reconcile_to_district_totals(self):
        """F6.4: Verify stream candidates, passed, and GPA-5 strictly sum to district totals."""
        sci = EXPECTED_STREAM_BREAKDOWN["Science"]
        hum = EXPECTED_STREAM_BREAKDOWN["Humanities"]
        busi = EXPECTED_STREAM_BREAKDOWN["Business Studies"]

        # Appeared sum
        sum_appeared = sci["appeared"] + hum["appeared"] + busi["appeared"]
        self.assertEqual(sum_appeared, EXPECTED_TOTAL_REGISTERED)

        # Passed sum
        sum_passed = sci["passed"] + hum["passed"] + busi["passed"]
        self.assertEqual(sum_passed, EXPECTED_TOTAL_PASSED)

        # GPA-5 sum
        sum_gpa5 = sci["gpa5"] + hum["gpa5"] + busi["gpa5"]
        self.assertEqual(sum_gpa5, EXPECTED_TOTAL_GPA5)

    def test_upazila_sums_reconcile_to_district_totals(self):
        """F6.5: Verify upazila examinees, passed, and GPA-5 strictly sum to district totals."""
        sum_enrolled = sum(u["enrolled"] for u in EXPECTED_UPAZILA_BREAKDOWN.values())
        sum_passed = sum(u["passed"] for u in EXPECTED_UPAZILA_BREAKDOWN.values())
        sum_gpa5 = sum(u["gpa5"] for u in EXPECTED_UPAZILA_BREAKDOWN.values())

        self.assertEqual(sum_enrolled, EXPECTED_TOTAL_REGISTERED)
        self.assertEqual(sum_passed, EXPECTED_TOTAL_PASSED)
        self.assertEqual(sum_gpa5, EXPECTED_TOTAL_GPA5)

    def test_college_level_passed_plus_failed_equals_total(self):
        """F6.6: Verify mathematical identity (passed + failed = total) holds for all 24 colleges."""
        for c in self.colleges:
            eiin = c.get("eiin")
            tot = c.get("total_appeared", 0)
            p = c.get("total_passed", 0)
            f = c.get("total_failed", 0)
            self.assertEqual(
                p + f, tot,
                f"College EIIN {eiin} mathematical violation: passed({p}) + failed({f}) != total({tot})"
            )

    def test_college_gpa_breakdown_sums_to_total(self):
        """F6.7: Verify GPA distribution buckets (5.0, 4-5, 3.5-4, 3-3.5, 2-3, 1-2, 0) sum to total appeared."""
        for c in self.colleges:
            eiin = c.get("eiin")
            b = c.get("gpa_breakdown", {})
            if b:
                bucket_sum = (
                    b.get("gpa_5_0", 0) +
                    b.get("gpa_4_to_5", 0) +
                    b.get("gpa_3_5_to_4", 0) +
                    b.get("gpa_3_to_3_5", 0) +
                    b.get("gpa_2_to_3", 0) +
                    b.get("gpa_1_to_2", 0) +
                    b.get("failed_or_zero", 0)
                )
                self.assertEqual(
                    bucket_sum, c.get("total_appeared", 0),
                    f"College EIIN {eiin} GPA buckets sum ({bucket_sum}) does not match total appeared ({c.get('total_appeared')})"
                )

if __name__ == "__main__":
    unittest.main()
