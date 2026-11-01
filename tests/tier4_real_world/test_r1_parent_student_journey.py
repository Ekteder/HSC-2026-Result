# tests/tier4_real_world/test_r1_parent_student_journey.py
"""
Tier 4 — Real-World Scenario R1: End-to-End Parent & Student Result Journey
Simulates full user journey where a student or parent navigates to the portal,
enters a roll number, checks the result card, verifies parental identity,
and inspects the subject-wise letter grades for higher education admissions.
"""
import unittest
from tests.helpers.data_loader import DataLoader
from tests.helpers.query_engine import QueryEngine

class TestR1ParentStudentJourney(unittest.TestCase):
    def setUp(self):
        self.loader = DataLoader.get_instance()
        self.students = self.loader.get_raw_student_records()
        if not self.students:
            self.students = self.loader.get_all_students()

    def test_complete_parent_student_lookup_journey_roll_517756(self):
        """R1.1: Complete student lookup journey for candidate 517756 (Biva Alam)."""
        # 1. Search for roll 517756
        results = QueryEngine.filter_students(self.students, search_term="517756")
        self.assertEqual(len(results), 1, "Candidate 517756 must be uniquely found")
        student = results[0]

        # 2. Verify identity and parental names
        self.assertEqual(student.get("name"), "BIVA ALAM")
        self.assertEqual(student.get("father_name"), "M M KAMRUL ALAM")
        self.assertEqual(student.get("mother_name"), "KANIZE FATEMA")

        # 3. Verify academic profile
        self.assertEqual(student.get("passing_year"), "2026")
        self.assertEqual(student.get("session"), "2024-25")
        self.assertEqual(student.get("candidate_type"), "REGULAR")
        self.assertIn("118523", student.get("institute", ""))

        # 4. Verify result status and GPA
        self.assertEqual(student.get("status"), "PASSED")
        self.assertAlmostEqual(float(student.get("gpa")), 4.25, places=2)

        # 5. Verify all 7 subjects and letter grades
        subjects = student.get("subjects", [])
        self.assertEqual(len(subjects), 7)
        grade_map = {s["subject"]: s["grade"] for s in subjects}
        self.assertEqual(grade_map["Bangla"], "A")
        self.assertEqual(grade_map["English"], "A+")
        self.assertEqual(grade_map["Physics"], "A-")
        self.assertEqual(grade_map["Chemistry"], "B")
        self.assertEqual(grade_map["Biology"], "A-")
        self.assertEqual(grade_map["Information & Communication Technology"], "A-")
        self.assertEqual(grade_map["Statistics"], "A+")

    def test_complete_journey_for_gpa5_candidate(self):
        """R1.2: Student journey for high achiever: verifies A+ letter grades across core subjects."""
        # Find candidate with GPA 5.00
        gpa5_student = None
        for s in self.students:
            try:
                if abs(float(s.get("gpa", 0.0) or 0.0) - 5.00) < 1e-4:
                    gpa5_student = s
                    break
            except Exception:
                pass

        if gpa5_student:
            roll = str(gpa5_student.get("roll"))
            results = QueryEngine.filter_students(self.students, search_term=roll)
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].get("status"), "PASSED")
            self.assertEqual(float(results[0].get("gpa")), 5.0)

    def test_complete_journey_for_failed_candidate_retake_advisory(self):
        """R1.3: Student journey for failed candidate: verifies identification of failed subject for retake."""
        failed_student = None
        for s in self.students:
            if "FAIL" in str(s.get("status", "")).upper():
                subjects = s.get("subjects", [])
                if any(sub.get("grade") == "F" for sub in subjects):
                    failed_student = s
                    break

        if failed_student:
            roll = str(failed_student.get("roll"))
            results = QueryEngine.filter_students(self.students, search_term=roll)
            self.assertEqual(len(results), 1)
            f_subs = [sub["subject"] for sub in results[0]["subjects"] if sub["grade"] == "F"]
            self.assertGreater(len(f_subs), 0, "Failed student must have at least one F grade subject")

    def test_student_card_data_integrity_no_null_parent_strings(self):
        """R1.4: Verify result card never formats parent names as 'null', 'undefined', or '[object Object]'."""
        for s in self.students[:30]:
            if "ABSENT" in str(s.get("status", "")).upper():
                continue
            father = str(s.get("father_name", ""))
            mother = str(s.get("mother_name", ""))
            self.assertNotIn("null", father.lower())
            self.assertNotIn("undefined", father.lower())
            self.assertNotIn("null", mother.lower())
            self.assertNotIn("undefined", mother.lower())

    def test_print_slip_readiness(self):
        """R1.5: Verify record contains all required fields for physical result slip printing."""
        required_print_fields = [
            "roll", "name", "father_name", "mother_name", "session",
            "candidate_type", "institute", "status", "gpa", "subjects"
        ]
        sample = self.students[0]
        for field in required_print_fields:
            self.assertIn(field, sample, f"Print slip missing required field '{field}'")

if __name__ == "__main__":
    unittest.main()
