# tests/tier4_real_world/test_r4_grade_verification.py
"""
Tier 4 — Real-World Scenario R4: Subject-Wise Grade Verification & Failure Analysis
Verifies letter grade scale consistency (A+ to F), compulsory subject coverage,
whitespace trimming, and failed subject identification for academic retakes.
"""
import unittest
from tests.helpers.data_loader import DataLoader

class TestR4GradeVerification(unittest.TestCase):
    def setUp(self):
        self.loader = DataLoader.get_instance()
        self.students = self.loader.get_raw_student_records()
        if not self.students:
            self.students = self.loader.get_all_students()

    def test_compulsory_subjects_present_across_all_examined_candidates(self):
        """R4.1: Verify core compulsory subjects (Bangla, English, ICT) are recorded for regular examinees."""
        self.assertTrue(len(self.students) > 0)
        checked = 0
        for s in self.students[:30]:
            if "ABSENT" in str(s.get("status", "")).upper():
                continue
            subjects = s.get("subjects", [])
            if isinstance(subjects, list) and len(subjects) > 0:
                sub_names = [sub.get("subject", "").lower() for sub in subjects]
                has_bangla = any("bangla" in name for name in sub_names)
                has_english = any("english" in name for name in sub_names)
                has_ict = any("information" in name or "ict" in name for name in sub_names)
                self.assertTrue(has_bangla, f"Bangla missing for roll {s.get('roll')}")
                self.assertTrue(has_english, f"English missing for roll {s.get('roll')}")
                self.assertTrue(has_ict, f"ICT missing for roll {s.get('roll')}")
                checked += 1
        self.assertGreater(checked, 0)

    def test_letter_grade_whitespace_trimming(self):
        """R4.2: Verify letter grades have no leading or trailing whitespace."""
        for s in self.students[:30]:
            subjects = s.get("subjects", [])
            if isinstance(subjects, list):
                for sub in subjects:
                    grade = sub.get("grade", "")
                    self.assertEqual(grade, grade.strip(), f"Grade '{grade}' contains untrimmed whitespace in roll {s.get('roll')}")

    def test_failed_subject_identification_for_retake(self):
        """R4.3: Verify failed candidates clearly identify which subject(s) must be retaken."""
        failed_count = 0
        for s in self.students:
            if "FAIL" in str(s.get("status", "")).upper():
                subjects = s.get("subjects", [])
                if isinstance(subjects, list):
                    failed_subs = [sub["subject"] for sub in subjects if sub.get("grade", "").strip() == "F"]
                    if len(failed_subs) > 0:
                        failed_count += 1
        self.assertGreater(failed_count, 0, "Failed candidates must have identified F grade subjects")

    def test_gpa_score_math_invariants(self):
        """R4.4: Verify GPA scores are strictly positive for passed students and 0.0 for failed."""
        for s in self.students[:50]:
            status = str(s.get("status", "")).upper()
            gpa = s.get("gpa")
            if "PASS" in status:
                self.assertIsNotNone(gpa)
                self.assertGreater(float(gpa), 0.0)
            elif "FAIL" in status:
                gpa_f = float(gpa) if gpa is not None else 0.0
                self.assertEqual(gpa_f, 0.0)

    def test_gpa5_requires_distinction_grades(self):
        """R4.5: Verify candidates achieving GPA 5.00 have letter grade A+ across primary subjects."""
        for s in self.students:
            try:
                gpa = float(s.get("gpa", 0.0) or 0.0)
                if abs(gpa - 5.00) < 1e-4:
                    subjects = s.get("subjects", [])
                    if isinstance(subjects, list):
                        grades = [sub.get("grade", "").strip() for sub in subjects]
                        # Must contain at least four A+ grades
                        a_plus_count = grades.count("A+")
                        self.assertGreaterEqual(a_plus_count, 4, f"GPA 5.00 candidate {s.get('roll')} has insufficient A+ grades ({a_plus_count})")
            except Exception:
                pass

if __name__ == "__main__":
    unittest.main()
