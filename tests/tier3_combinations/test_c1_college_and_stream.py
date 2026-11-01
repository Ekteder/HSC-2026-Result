# tests/tier3_combinations/test_c1_college_and_stream.py
"""
Tier 3 — Cross-Feature Combination C1: College AND Stream Intersections
Verifies pairwise filtering and analytical consistency when slicing candidates
by institution and academic stream concurrently.
"""
import unittest
from tests.helpers.data_loader import DataLoader
from tests.helpers.query_engine import QueryEngine

class TestC1CollegeAndStream(unittest.TestCase):
    def setUp(self):
        self.loader = DataLoader.get_instance()
        self.colleges = self.loader.get_all_colleges()
        self.college_map = {int(c.get("eiin")): c for c in self.colleges}

    def test_victoria_college_science_stream_intersection(self):
        """C1.1: Verify College=118527 (Victoria College) AND Stream=Science has 336 examinees."""
        col = self.college_map[118527]
        stats = col.get("stream_stats", {}).get("Science", {})
        self.assertEqual(stats.get("appeared"), 336)
        self.assertGreater(stats.get("passed"), 250)
        self.assertGreaterEqual(stats.get("gpa5"), 50)

    def test_lohagara_govt_adarsha_humanities_intersection(self):
        """C1.2: Verify College=118437 (Lohagara Govt Adarsha) AND Stream=Humanities has 375 examinees and 201 passed."""
        col = self.college_map[118437]
        stats = col.get("stream_stats", {}).get("Humanities", {})
        self.assertEqual(stats.get("appeared"), 375)
        self.assertEqual(stats.get("passed"), 201)

    def test_munshi_manik_mia_business_studies_intersection(self):
        """C1.3: Verify College=118383 (Munshi Manik Mia) AND Stream=Business Studies has 12 examinees."""
        col = self.college_map[118383]
        stats = col.get("stream_stats", {}).get("Business Studies", {})
        self.assertEqual(stats.get("appeared"), 12)
        self.assertEqual(stats.get("passed"), 2)

    def test_narail_govt_mohila_college_science_and_humanities_stats(self):
        """C1.4: Verify College=118525 (Narail Govt Mohila) Science (76 appeared) and Humanities (5 GPA-5s)."""
        col = self.college_map[118525]
        stats = col.get("stream_stats", {})
        self.assertEqual(stats.get("Science", {}).get("appeared"), 76)
        self.assertEqual(stats.get("Humanities", {}).get("gpa5"), 5)

    def test_makrail_karim_khalek_humanities_only_stream(self):
        """C1.5: Verify College=118404 (Makrail Karim Khalek) offers only Humanities stream with 49 candidates."""
        col = self.college_map[118404]
        streams = col.get("participating_streams", [])
        stats = col.get("stream_stats", {})
        self.assertEqual(len(streams), 1)
        self.assertIn("Humanities", streams)
        self.assertEqual(stats.get("Humanities", {}).get("appeared"), 49)
        self.assertEqual(stats.get("Humanities", {}).get("passed"), 0)

    def test_college_streams_sum_equals_college_total_appeared(self):
        """C1.6: Verify the sum of appeared candidates across all streams equals college total appeared for all 24 colleges."""
        for c in self.colleges:
            eiin = c.get("eiin")
            stats = c.get("stream_stats", {})
            stream_sum = sum(s.get("appeared", 0) for s in stats.values())
            self.assertEqual(
                stream_sum, c.get("total_appeared"),
                f"College EIIN {eiin} stream appeared sum ({stream_sum}) != total appeared ({c.get('total_appeared')})"
            )

if __name__ == "__main__":
    unittest.main()
