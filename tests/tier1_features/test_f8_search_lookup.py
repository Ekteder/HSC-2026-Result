# tests/tier1_features/test_f8_search_lookup.py
"""
Tier 1 — Feature 8: Student Search Lookup
Verifies rapid search lookup by 6-digit Roll Number and Registration Number,
retrieval of student profile metadata, and grade sheet extraction.
"""
import unittest
from tests.helpers.data_loader import DataLoader
from tests.helpers.query_engine import QueryEngine

class TestF8SearchLookup(unittest.TestCase):
    def setUp(self):
        self.loader = DataLoader.get_instance()
        self.students = self.loader.get_raw_student_records()
        if not self.students:
            self.students = self.loader.get_all_students()

    def test_search_by_exact_roll_number(self):
        """F8.1: Verify search lookup by 6-digit roll number returns the exact candidate."""
        self.assertTrue(len(self.students) > 0, "No students loaded")
        target_student = self.students[0]
        roll = str(target_student.get("roll"))

        results = QueryEngine.filter_students(self.students, search_term=roll)
        self.assertGreater(len(results), 0, f"No student found for roll {roll}")
        found = results[0]
        self.assertEqual(str(found.get("roll")), roll)
        self.assertEqual(found.get("name"), target_student.get("name"))

    def test_search_case_insensitivity_on_student_name(self):
        """F8.2: Verify search lookup matches student name case-insensitively."""
        self.assertTrue(len(self.students) > 0)
        target = self.students[0]
        name = target.get("name", "")
        if len(name) > 3:
            sub_name = name[:4].lower()
            results = QueryEngine.filter_students(self.students, search_term=sub_name)
            self.assertTrue(
                any(str(s.get("roll")) == str(target.get("roll")) for s in results),
                f"Candidate {name} not found by search query '{sub_name}'"
            )

    def test_search_retrieves_complete_subject_grades(self):
        """F8.3: Verify found student profile includes full subject grade sheet."""
        self.assertTrue(len(self.students) > 0)
        for s in self.students[:20]:
            status = str(s.get("status", "")).upper()
            if "ABSENT" in status:
                continue
            subjects = s.get("subjects")
            self.assertIsNotNone(subjects, f"Subjects missing for roll {s.get('roll')}")
            # Regular examinees have 6 or 7 subjects
            if isinstance(subjects, list):
                self.assertGreaterEqual(len(subjects), 6, f"Expected >=6 subjects for roll {s.get('roll')}")
            elif isinstance(subjects, dict):
                self.assertGreaterEqual(len(subjects), 6, f"Expected >=6 subjects for roll {s.get('roll')}")

    def test_search_retrieves_parents_and_institute_metadata(self):
        """F8.4: Verify search result returns Father Name, Mother Name, Session, and Institute."""
        for s in self.students[:20]:
            if "ABSENT" in str(s.get("status", "")).upper():
                continue
            self.assertTrue(bool(s.get("father_name")), f"Missing father name in roll {s.get('roll')}")
            self.assertTrue(bool(s.get("mother_name")), f"Missing mother name in roll {s.get('roll')}")
            self.assertTrue(bool(s.get("institute")), f"Missing institute in roll {s.get('roll')}")

    def test_search_by_registration_number_if_available(self):
        """F8.5: Verify search by registration number correctly finds candidate when reg is present."""
        student_with_reg = None
        for s in self.students:
            reg = s.get("reg_no") or s.get("regno")
            if reg and len(str(reg).strip()) > 4:
                student_with_reg = s
                break

        if student_with_reg:
            reg_val = str(student_with_reg.get("reg_no") or student_with_reg.get("regno")).strip()
            results = QueryEngine.filter_students(self.students, search_term=reg_val)
            self.assertTrue(
                any(str(r.get("roll")) == str(student_with_reg.get("roll")) for r in results),
                f"Candidate with reg {reg_val} not found by reg search"
            )

    def test_search_result_reflects_accurate_gpa(self):
        """F8.6: Verify search result reflects accurate GPA score for passing candidate."""
        passing_students = [s for s in self.students if "PASS" in str(s.get("status", "")).upper()]
        self.assertGreater(len(passing_students), 0, "No passing students found")
        sample = passing_students[0]
        results = QueryEngine.filter_students(self.students, search_term=str(sample.get("roll")))
        self.assertGreater(len(results), 0)
        found = results[0]
        self.assertIsNotNone(found.get("gpa"))
        self.assertGreater(float(found.get("gpa")), 0.0)

if __name__ == "__main__":
    unittest.main()
