# tests/tier1_features/test_f10_analytics_dashboard.py
"""
Tier 1 — Feature 10: Analytics Dashboard Statistics
Verifies district summary KPIs, college pass rate leaderboard rankings,
stream distributions, and GPA grade histogram distributions.
"""
import unittest
from tests.test_config import (
    EXPECTED_TOTAL_REGISTERED,
    EXPECTED_TOTAL_PASSED,
    EXPECTED_TOTAL_GPA5,
    EXPECTED_DISTRICT_PASS_RATE_APPEARED,
    EXPECTED_DISTRICT_PASS_RATE_ENROLLED,
    EXPECTED_STREAM_BREAKDOWN
)
from tests.helpers.data_loader import DataLoader
from tests.helpers.query_engine import QueryEngine

class TestF10AnalyticsDashboard(unittest.TestCase):
    def setUp(self):
        self.loader = DataLoader.get_instance()
        self.colleges = self.loader.get_all_colleges()

    def test_district_overall_pass_rate_calculation(self):
        """F10.1: Verify district-wide pass rate computes to 35.06% (enrolled) or 36.78% (appeared)."""
        tot_enrolled = sum(c.get("total_appeared", 0) for c in self.colleges)
        tot_passed = sum(c.get("total_passed", 0) for c in self.colleges)
        pass_rate_enrolled = round((tot_passed / tot_enrolled) * 100, 2)
        self.assertEqual(pass_rate_enrolled, EXPECTED_DISTRICT_PASS_RATE_ENROLLED)

    def test_college_pass_rate_leaderboard_ordering(self):
        """F10.2: Verify Government Victoria College ranks #1 with 61.63% pass rate."""
        ranked = sorted(self.colleges, key=lambda c: c.get("pass_rate", 0.0), reverse=True)
        top_college = ranked[0]
        self.assertEqual(int(top_college.get("eiin")), 118527)
        self.assertAlmostEqual(float(top_college.get("pass_rate")), 61.63, delta=0.1)

    def test_gpa5_leaderboard_ordering(self):
        """F10.3: Verify Government Victoria College has the highest GPA 5 count (69)."""
        ranked = sorted(self.colleges, key=lambda c: c.get("total_gpa5", 0), reverse=True)
        top_college = ranked[0]
        self.assertEqual(int(top_college.get("eiin")), 118527)
        self.assertEqual(top_college.get("total_gpa5"), 69)

    def test_stream_distribution_breakdown(self):
        """F10.4: Verify stream volume distribution: Humanities > Science > Business Studies."""
        sci_tot = sum(c.get("stream_stats", {}).get("Science", {}).get("appeared", 0) for c in self.colleges)
        hum_tot = sum(c.get("stream_stats", {}).get("Humanities", {}).get("appeared", 0) for c in self.colleges)
        bus_tot = sum(c.get("stream_stats", {}).get("Business Studies", {}).get("appeared", 0) for c in self.colleges)

        self.assertGreater(hum_tot, sci_tot)
        self.assertGreater(sci_tot, bus_tot)
        self.assertEqual(sci_tot, EXPECTED_STREAM_BREAKDOWN["Science"]["appeared"])
        self.assertEqual(hum_tot, EXPECTED_STREAM_BREAKDOWN["Humanities"]["appeared"])
        self.assertEqual(bus_tot, EXPECTED_STREAM_BREAKDOWN["Business Studies"]["appeared"])

    def test_district_grade_histogram_buckets(self):
        """F10.5: Verify aggregate grade histogram counts sum to total examinees across all 24 colleges."""
        gpa_buckets = {
            "gpa_5_0": 0, "gpa_4_to_5": 0, "gpa_3_5_to_4": 0,
            "gpa_3_to_3_5": 0, "gpa_2_to_3": 0, "gpa_1_to_2": 0, "failed_or_zero": 0
        }
        for c in self.colleges:
            b = c.get("gpa_breakdown", {})
            for k in gpa_buckets:
                gpa_buckets[k] += b.get(k, 0)

        total_in_buckets = sum(gpa_buckets.values())
        self.assertEqual(total_in_buckets, EXPECTED_TOTAL_REGISTERED)
        self.assertEqual(gpa_buckets["gpa_5_0"], EXPECTED_TOTAL_GPA5)

    def test_zero_pass_rate_college_identification(self):
        """F10.6: Verify Makrail Karim Khalek Solaiman Institution (118404) correctly registers 0.00% pass rate."""
        makrail = self.loader.get_college_by_eiin(118404)
        self.assertIsNotNone(makrail)
        self.assertEqual(makrail.get("total_passed"), 0)
        self.assertEqual(float(makrail.get("pass_rate")), 0.0)

if __name__ == "__main__":
    unittest.main()
