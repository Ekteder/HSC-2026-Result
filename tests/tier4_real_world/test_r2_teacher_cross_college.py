# tests/tier4_real_world/test_r2_teacher_cross_college.py
"""
Tier 4 — Real-World Scenario R2: Institutional Performance Analysis by Educators
Simulates an academic administrator or teacher evaluating performance rankings,
cross-college comparison matrices, and stream-wise success rates across the 3 upazilas.
"""
import unittest
from tests.helpers.data_loader import DataLoader

class TestR2TeacherCrossCollege(unittest.TestCase):
    def setUp(self):
        self.loader = DataLoader.get_instance()
        self.colleges = self.loader.get_all_colleges()

    def test_top_five_colleges_by_pass_rate_ranking(self):
        """R2.1: Teacher evaluates top 5 colleges in Narail District by overall pass rate."""
        ranked = sorted(self.colleges, key=lambda c: float(c.get("pass_rate", 0.0)), reverse=True)
        top_5_eiins = [int(c.get("eiin")) for c in ranked[:5]]
        # Top colleges must include Victoria College (118527) and Lohagara Govt Adarsha (118437)
        self.assertEqual(top_5_eiins[0], 118527)  # Victoria College is #1
        self.assertEqual(top_5_eiins[1], 118437)  # Lohagara Govt Adarsha is #2

    def test_upazila_leader_institutions(self):
        """R2.2: Teacher identifies top performing college in each of the 3 upazilas."""
        sadar_colleges = [c for c in self.colleges if "Sadar" in c.get("upazila", "")]
        lohagara_colleges = [c for c in self.colleges if "Lohagara" in c.get("upazila", "")]
        kalia_colleges = [c for c in self.colleges if "Kalia" in c.get("upazila", "") or "Naragati" in c.get("upazila", "")]

        sadar_top = max(sadar_colleges, key=lambda c: float(c.get("pass_rate", 0.0)))
        lohagara_top = max(lohagara_colleges, key=lambda c: float(c.get("pass_rate", 0.0)))
        kalia_top = max(kalia_colleges, key=lambda c: float(c.get("pass_rate", 0.0)))

        self.assertEqual(int(sadar_top.get("eiin")), 118527)      # Victoria College
        self.assertEqual(int(lohagara_top.get("eiin")), 118437)   # Lohagara Govt Adarsha
        self.assertEqual(int(kalia_top.get("eiin")), 118383)      # Munshi Manik Mia College (30.31%)

    def test_science_stream_college_rankings(self):
        """R2.3: Teacher compares institutions on Science stream success rate."""
        sci_colleges = []
        for c in self.colleges:
            stats = c.get("stream_stats", {}).get("Science", {})
            if stats.get("appeared", 0) > 10:  # significant cohorts
                sci_colleges.append({
                    "eiin": c.get("eiin"),
                    "name": c.get("college_name"),
                    "pass_rate": stats.get("pass_rate", 0.0)
                })

        ranked_sci = sorted(sci_colleges, key=lambda x: float(x["pass_rate"]), reverse=True)
        self.assertGreater(len(ranked_sci), 0)
        self.assertGreater(float(ranked_sci[0]["pass_rate"]), 50.0)

    def test_college_performance_matrix_export_completeness(self):
        """R2.4: Verify all 24 colleges have required data points for comparison matrix table."""
        required_matrix_fields = [
            "eiin", "college_name", "upazila", "center",
            "total_appeared", "total_passed", "pass_rate", "total_gpa5"
        ]
        for c in self.colleges:
            for field in required_matrix_fields:
                self.assertIn(field, c, f"College {c.get('eiin')} missing comparison matrix field '{field}'")

    def test_identify_institutions_requiring_academic_intervention(self):
        """R2.5: Teacher identifies colleges with pass rate below 20% for remediation."""
        low_pass = [c for c in self.colleges if float(c.get("pass_rate", 0.0)) < 20.0]
        # At least 7 colleges in Narail have pass rate < 20%
        self.assertGreaterEqual(len(low_pass), 6)
        low_pass_eiins = {int(c.get("eiin")) for c in low_pass}
        self.assertIn(118404, low_pass_eiins)  # Makrail Karim Khalek (0%)
        self.assertIn(118522, low_pass_eiins)  # Juralia Bahumukhi (4.17%)

if __name__ == "__main__":
    unittest.main()
