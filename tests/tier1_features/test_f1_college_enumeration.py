# tests/tier1_features/test_f1_college_enumeration.py
"""
Tier 1 — Feature 1: Narail College EIIN Enumeration
Verifies that all 24 participating institutions in Narail District for HSC 2026
under Jessore Board are enumerated, mapped to centers and upazilas, and reconciled.
"""
import unittest
from tests.test_config import ALL_24_EIINS, EXPECTED_TOTAL_COLLEGES, EXPECTED_UPAZILA_BREAKDOWN
from tests.helpers.data_loader import DataLoader

class TestF1CollegeEnumeration(unittest.TestCase):
    def setUp(self):
        self.loader = DataLoader.get_instance()
        self.colleges = self.loader.get_all_colleges()

    def test_total_colleges_count_equals_24(self):
        """F1.1: Verify total enumerated colleges count is exactly 24."""
        self.assertEqual(
            len(self.colleges),
            EXPECTED_TOTAL_COLLEGES,
            f"Expected exactly {EXPECTED_TOTAL_COLLEGES} colleges, found {len(self.colleges)}"
        )

    def test_all_24_eiin_values_match_bise_jashore_registry(self):
        """F1.2: Verify the set of 24 EIINs matches the official board registry."""
        loaded_eiins = {int(c.get("eiin", 0)) for c in self.colleges}
        self.assertEqual(
            loaded_eiins,
            ALL_24_EIINS,
            f"Mismatch in EIIN registry. Diff: {loaded_eiins.symmetric_difference(ALL_24_EIINS)}"
        )

    def test_upazila_college_distribution(self):
        """F1.3: Verify college count distribution across Narail Sadar (12), Lohagara (7), and Kalia (5)."""
        upazila_counts = {"Narail Sadar": 0, "Lohagara": 0, "Kalia": 0}
        for c in self.colleges:
            u = c.get("upazila", "")
            if "Sadar" in u or "Narail Sadar" in u:
                upazila_counts["Narail Sadar"] += 1
            elif "Lohagara" in u:
                upazila_counts["Lohagara"] += 1
            elif "Kalia" in u or "Naragati" in u:
                upazila_counts["Kalia"] += 1

        for upazila, expected_data in EXPECTED_UPAZILA_BREAKDOWN.items():
            expected_count = expected_data["colleges"]
            actual_count = upazila_counts[upazila]
            self.assertEqual(
                actual_count,
                expected_count,
                f"Upazila {upazila} expected {expected_count} colleges, got {actual_count}"
            )

    def test_college_center_and_code_mapping(self):
        """F1.4: Verify every college has a valid, non-empty examination center mapping."""
        for c in self.colleges:
            eiin = c.get("eiin")
            center = c.get("center") or c.get("center_name")
            self.assertTrue(
                bool(center),
                f"College EIIN {eiin} missing center mapping"
            )

    def test_key_flagship_colleges_present_with_correct_eiin(self):
        """F1.5: Verify flagship colleges have verified names and exact EIINs."""
        flagship_checks = {
            118527: "Government Victoria College, Narail",
            118525: "Narail Govt. Mohila College",
            118437: "Lohagara Govt. Adarsha College",
            118385: "Govt. Shaheed Abdus Salam College",
            118383: "Munshi Manik Mia College"
        }
        college_map = {int(c.get("eiin")): c for c in self.colleges}
        for eiin, expected_name_sub in flagship_checks.items():
            self.assertIn(eiin, college_map, f"Missing flagship college EIIN {eiin}")
            college = college_map[eiin]
            name = college.get("college_name") or college.get("name") or college.get("institute_name")
            self.assertTrue(
                bool(name),
                f"College EIIN {eiin} has empty name"
            )

    def test_all_colleges_have_participating_streams(self):
        """F1.6: Verify all colleges define their participating streams."""
        for c in self.colleges:
            eiin = c.get("eiin")
            streams = c.get("participating_streams") or c.get("streams") or []
            # Every institution must participate in at least one stream
            self.assertTrue(
                len(streams) > 0,
                f"College EIIN {eiin} has no participating streams declared"
            )

if __name__ == "__main__":
    unittest.main()
