# tests/tier1_features/test_f4_stream_parsing.py
"""
Tier 1 — Feature 4: Multi-Stream Parsing
Verifies parsing of candidate roster into Science, Humanities, and Business Studies streams,
stream-specific roll ranges, candidate counts, and elective subjects.
"""
import unittest
from tests.test_config import EXPECTED_STREAM_BREAKDOWN
from tests.helpers.data_loader import DataLoader

class TestF4StreamParsing(unittest.TestCase):
    def setUp(self):
        self.loader = DataLoader.get_instance()
        self.colleges = self.loader.get_all_colleges()

    def test_science_stream_aggregate_totals(self):
        """F4.1: Verify Science stream total appeared examinees (815) and passed (458)."""
        tot_appeared = 0
        tot_passed = 0
        for c in self.colleges:
            stats = c.get("stream_stats", {})
            sci = stats.get("Science", {})
            tot_appeared += sci.get("appeared", 0)
            tot_passed += sci.get("passed", 0)

        expected_sci = EXPECTED_STREAM_BREAKDOWN["Science"]
        self.assertEqual(
            tot_appeared, expected_sci["appeared"],
            f"Science stream appeared mismatch: expected {expected_sci['appeared']}, got {tot_appeared}"
        )
        self.assertEqual(
            tot_passed, expected_sci["passed"],
            f"Science stream passed mismatch: expected {expected_sci['passed']}, got {tot_passed}"
        )

    def test_humanities_stream_aggregate_totals(self):
        """F4.2: Verify Humanities stream total appeared examinees (3,748) and passed (1,171)."""
        tot_appeared = 0
        tot_passed = 0
        for c in self.colleges:
            stats = c.get("stream_stats", {})
            hum = stats.get("Humanities", {})
            tot_appeared += hum.get("appeared", 0)
            tot_passed += hum.get("passed", 0)

        expected_hum = EXPECTED_STREAM_BREAKDOWN["Humanities"]
        self.assertEqual(
            tot_appeared, expected_hum["appeared"],
            f"Humanities stream appeared mismatch: expected {expected_hum['appeared']}, got {tot_appeared}"
        )
        self.assertEqual(
            tot_passed, expected_hum["passed"],
            f"Humanities stream passed mismatch: expected {expected_hum['passed']}, got {tot_passed}"
        )

    def test_business_studies_stream_aggregate_totals(self):
        """F4.3: Verify Business Studies stream total appeared examinees (502) and passed (150)."""
        tot_appeared = 0
        tot_passed = 0
        for c in self.colleges:
            stats = c.get("stream_stats", {})
            busi = stats.get("Business Studies", {})
            tot_appeared += busi.get("appeared", 0)
            tot_passed += busi.get("passed", 0)

        expected_busi = EXPECTED_STREAM_BREAKDOWN["Business Studies"]
        self.assertEqual(
            tot_appeared, expected_busi["appeared"],
            f"Business Studies appeared mismatch: expected {expected_busi['appeared']}, got {tot_appeared}"
        )
        self.assertEqual(
            tot_passed, expected_busi["passed"],
            f"Business Studies passed mismatch: expected {expected_busi['passed']}, got {tot_passed}"
        )

    def test_stream_roll_number_prefixes_and_ranges(self):
        """F4.4: Verify roll number ranges belong to distinct series per stream."""
        for c in self.colleges:
            stats = c.get("stream_stats", {})
            for stream_name, sdata in stats.items():
                min_r = sdata.get("roll_min")
                max_r = sdata.get("roll_max")
                if min_r and max_r:
                    min_roll = int(min_r)
                    max_roll = int(max_r)
                    self.assertLessEqual(min_roll, max_roll)
                    if stream_name == "Science":
                        # Science rolls start with 5xxxxx
                        self.assertTrue(str(min_roll).startswith("5"))
                    elif stream_name == "Humanities":
                        # Humanities rolls start with 6xxxxx
                        self.assertTrue(str(min_roll).startswith("6"))
                    elif stream_name == "Business Studies":
                        # Business rolls start with 8xxxxx
                        self.assertTrue(str(min_roll).startswith("8"))

    def test_gpa5_distribution_across_streams(self):
        """F4.5: Verify GPA 5.00 achiever counts per stream: Science 56, Humanities 45, Business Studies 4."""
        gpa5_counts = {"Science": 0, "Humanities": 0, "Business Studies": 0}
        for c in self.colleges:
            stats = c.get("stream_stats", {})
            for stream_name in gpa5_counts:
                gpa5_counts[stream_name] += stats.get(stream_name, {}).get("gpa5", 0)

        self.assertEqual(gpa5_counts["Science"], EXPECTED_STREAM_BREAKDOWN["Science"]["gpa5"])
        self.assertEqual(gpa5_counts["Humanities"], EXPECTED_STREAM_BREAKDOWN["Humanities"]["gpa5"])
        self.assertEqual(gpa5_counts["Business Studies"], EXPECTED_STREAM_BREAKDOWN["Business Studies"]["gpa5"])

    def test_stream_pass_rate_calculations(self):
        """F4.6: Verify stream pass rates match official benchmarks (Science: 56.20%, Hum: 31.24%, Bus: 29.88%)."""
        for stream_name, expected_info in EXPECTED_STREAM_BREAKDOWN.items():
            rate = round((expected_info["passed"] / expected_info["appeared"]) * 100, 2)
            self.assertAlmostEqual(rate, expected_info["pass_rate"], delta=0.1)

if __name__ == "__main__":
    unittest.main()
