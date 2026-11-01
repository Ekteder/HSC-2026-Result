# tests/tier4_real_world/test_r3_officer_gpa5_export.py
"""
Tier 4 — Real-World Scenario R3: District Education Officer GPA 5.00 Honors Export
Simulates an education officer generating an exhaustive honor roll of all 105 GPA 5.00
achievers across Narail District for board scholarship distribution and merit ceremonies.
"""
import unittest
from tests.test_config import EXPECTED_TOTAL_GPA5, EXPECTED_STREAM_BREAKDOWN, EXPECTED_UPAZILA_BREAKDOWN
from tests.helpers.data_loader import DataLoader

class TestR3OfficerGpa5Export(unittest.TestCase):
    def setUp(self):
        self.loader = DataLoader.get_instance()
        self.colleges = self.loader.get_all_colleges()

    def test_district_total_gpa5_honorees_count(self):
        """R3.1: Verify education officer export list contains exactly 105 GPA 5.00 candidates."""
        total_gpa5 = sum(c.get("total_gpa5", 0) for c in self.colleges)
        self.assertEqual(
            total_gpa5, EXPECTED_TOTAL_GPA5,
            f"Expected {EXPECTED_TOTAL_GPA5} total GPA 5 achievers, got {total_gpa5}"
        )

    def test_gpa5_distribution_across_eleven_participating_colleges(self):
        """R3.2: Verify exactly 11 colleges produced GPA 5.00 achievers and 13 produced zero."""
        colleges_with_gpa5 = [c for c in self.colleges if c.get("total_gpa5", 0) > 0]
        colleges_zero_gpa5 = [c for c in self.colleges if c.get("total_gpa5", 0) == 0]

        self.assertEqual(len(colleges_with_gpa5), 11, "Expected exactly 11 colleges with GPA-5")
        self.assertEqual(len(colleges_zero_gpa5), 13, "Expected exactly 13 colleges with 0 GPA-5")

    def test_exact_gpa5_counts_for_all_eleven_merit_institutions(self):
        """R3.3: Verify exact ground truth GPA 5 counts for each of the 11 merit institutions."""
        expected_gpa5_map = {
            118527: 69,  # Victoria College
            118437: 13,  # Lohagara Govt Adarsha
            118525: 5,   # Narail Govt Mohila
            118385: 5,   # Govt Shaheed Abdus Salam
            118436: 3,   # Laxmipasha Ideal Women
            118528: 3,   # Gobra Mittra
            118530: 2,   # Maijpara College
            118440: 2,   # Itna Higher Secondary
            118383: 1,   # Munshi Manik Mia
            118438: 1,   # Nabaganga Mahavidyalaya
            118523: 1    # Ballartop Ideal
        }
        actual_map = {int(c.get("eiin")): c.get("total_gpa5", 0) for c in self.colleges if c.get("total_gpa5", 0) > 0}
        self.assertEqual(actual_map, expected_gpa5_map)
        self.assertEqual(sum(actual_map.values()), 105)

    def test_gpa5_upazila_representation(self):
        """R3.4: Verify upazila GPA-5 distribution: Sadar 80 (76.19%), Lohagara 19 (18.10%), Kalia 6 (5.71%)."""
        sadar_gpa5 = sum(c.get("total_gpa5", 0) for c in self.colleges if "Sadar" in c.get("upazila", ""))
        lohagara_gpa5 = sum(c.get("total_gpa5", 0) for c in self.colleges if "Lohagara" in c.get("upazila", ""))
        kalia_gpa5 = sum(c.get("total_gpa5", 0) for c in self.colleges if "Kalia" in c.get("upazila", "") or "Naragati" in c.get("upazila", ""))

        self.assertEqual(sadar_gpa5, EXPECTED_UPAZILA_BREAKDOWN["Narail Sadar"]["gpa5"])
        self.assertEqual(lohagara_gpa5, EXPECTED_UPAZILA_BREAKDOWN["Lohagara"]["gpa5"])
        self.assertEqual(kalia_gpa5, EXPECTED_UPAZILA_BREAKDOWN["Kalia"]["gpa5"])

    def test_gpa5_stream_representation(self):
        """R3.5: Verify stream GPA-5 distribution: Science 56 (53.33%), Humanities 45 (42.86%), Business 4 (3.81%)."""
        sci_gpa5 = sum(c.get("stream_stats", {}).get("Science", {}).get("gpa5", 0) for c in self.colleges)
        hum_gpa5 = sum(c.get("stream_stats", {}).get("Humanities", {}).get("gpa5", 0) for c in self.colleges)
        bus_gpa5 = sum(c.get("stream_stats", {}).get("Business Studies", {}).get("gpa5", 0) for c in self.colleges)

        self.assertEqual(sci_gpa5, EXPECTED_STREAM_BREAKDOWN["Science"]["gpa5"])
        self.assertEqual(hum_gpa5, EXPECTED_STREAM_BREAKDOWN["Humanities"]["gpa5"])
        self.assertEqual(bus_gpa5, EXPECTED_STREAM_BREAKDOWN["Business Studies"]["gpa5"])

if __name__ == "__main__":
    unittest.main()
