# tests/tier2_boundaries/test_b4_edge_rolls.py
"""
Tier 2 — Boundary Case B4: Stream Edge Roll Numbers
Verifies lowest and highest roll numbers for Science (517503 to 522733),
Humanities (664448 to 682211), and Business Studies (810146 to 812518),
verifying boundary inclusion and correct college affiliation.
"""
import unittest
from tests.test_config import EXPECTED_STREAM_BREAKDOWN
from tests.helpers.data_loader import DataLoader

class TestB4EdgeRolls(unittest.TestCase):
    def setUp(self):
        self.loader = DataLoader.get_instance()
        self.colleges = self.loader.get_all_colleges()

    def test_science_stream_minimum_roll(self):
        """B4.1: Verify lowest Science roll number across Narail District is 517503."""
        sci_min_rolls = []
        for c in self.colleges:
            stats = c.get("stream_stats", {}).get("Science", {})
            r = stats.get("roll_min")
            if r:
                sci_min_rolls.append(int(r))

        district_sci_min = min(sci_min_rolls)
        self.assertEqual(
            district_sci_min,
            EXPECTED_STREAM_BREAKDOWN["Science"]["roll_min"],
            f"Expected lowest Science roll {EXPECTED_STREAM_BREAKDOWN['Science']['roll_min']}, got {district_sci_min}"
        )

    def test_science_stream_maximum_roll(self):
        """B4.2: Verify highest Science roll number across Narail District is 522733."""
        sci_max_rolls = []
        for c in self.colleges:
            stats = c.get("stream_stats", {}).get("Science", {})
            r = stats.get("roll_max")
            if r:
                sci_max_rolls.append(int(r))

        district_sci_max = max(sci_max_rolls)
        self.assertEqual(
            district_sci_max,
            EXPECTED_STREAM_BREAKDOWN["Science"]["roll_max"],
            f"Expected highest Science roll {EXPECTED_STREAM_BREAKDOWN['Science']['roll_max']}, got {district_sci_max}"
        )

    def test_humanities_stream_minimum_roll(self):
        """B4.3: Verify lowest Humanities roll number across Narail District is 664448."""
        hum_min_rolls = []
        for c in self.colleges:
            stats = c.get("stream_stats", {}).get("Humanities", {})
            r = stats.get("roll_min")
            if r:
                hum_min_rolls.append(int(r))

        district_hum_min = min(hum_min_rolls)
        self.assertEqual(
            district_hum_min,
            EXPECTED_STREAM_BREAKDOWN["Humanities"]["roll_min"],
            f"Expected lowest Humanities roll {EXPECTED_STREAM_BREAKDOWN['Humanities']['roll_min']}, got {district_hum_min}"
        )

    def test_humanities_stream_maximum_roll(self):
        """B4.4: Verify highest Humanities roll number across Narail District is 682211."""
        hum_max_rolls = []
        for c in self.colleges:
            stats = c.get("stream_stats", {}).get("Humanities", {})
            r = stats.get("roll_max")
            if r:
                hum_max_rolls.append(int(r))

        district_hum_max = max(hum_max_rolls)
        self.assertEqual(
            district_hum_max,
            EXPECTED_STREAM_BREAKDOWN["Humanities"]["roll_max"],
            f"Expected highest Humanities roll {EXPECTED_STREAM_BREAKDOWN['Humanities']['roll_max']}, got {district_hum_max}"
        )

    def test_business_studies_stream_minimum_roll(self):
        """B4.5: Verify lowest Business Studies roll number across Narail District is 810146."""
        bus_min_rolls = []
        for c in self.colleges:
            stats = c.get("stream_stats", {}).get("Business Studies", {})
            r = stats.get("roll_min")
            if r:
                bus_min_rolls.append(int(r))

        district_bus_min = min(bus_min_rolls)
        self.assertEqual(
            district_bus_min,
            EXPECTED_STREAM_BREAKDOWN["Business Studies"]["roll_min"],
            f"Expected lowest Business Studies roll {EXPECTED_STREAM_BREAKDOWN['Business Studies']['roll_min']}, got {district_bus_min}"
        )

    def test_business_studies_stream_maximum_roll(self):
        """B4.6: Verify highest Business Studies roll number across Narail District is 812518."""
        bus_max_rolls = []
        for c in self.colleges:
            stats = c.get("stream_stats", {}).get("Business Studies", {})
            r = stats.get("roll_max")
            if r:
                bus_max_rolls.append(int(r))

        district_bus_max = max(bus_max_rolls)
        self.assertEqual(
            district_bus_max,
            EXPECTED_STREAM_BREAKDOWN["Business Studies"]["roll_max"],
            f"Expected highest Business Studies roll {EXPECTED_STREAM_BREAKDOWN['Business Studies']['roll_max']}, got {district_bus_max}"
        )

if __name__ == "__main__":
    unittest.main()
