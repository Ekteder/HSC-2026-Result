# tests/tier2_boundaries/test_b3_nonpassing_statuses.py
"""
Tier 2 — Boundary Case B3: Non-Passing Status Codes
Verifies correct detection, classification, and presentation of non-passing status codes:
F1 (single subject fail), F2 (two subjects fail), Fail (general fail),
Absent (Abst / ABSENT), and Expelled (Expl / REPORTED).
"""
import unittest
from tests.test_config import EXPECTED_TOTAL_ABSENT
from tests.helpers.data_loader import DataLoader
from tests.helpers.query_engine import QueryEngine

class TestB3NonpassingStatuses(unittest.TestCase):
    def setUp(self):
        self.loader = DataLoader.get_instance()
        self.colleges = self.loader.get_all_colleges()
        self.students = self.loader.get_raw_student_records()
        if not self.students:
            self.students = self.loader.get_all_students()

    def test_district_total_absentee_candidates(self):
        """B3.1: Verify total absent candidate count across all colleges reconciles to 236."""
        total_absent = 0
        for c in self.colleges:
            stats = c.get("stream_stats", {})
            for sname, sdata in stats.items():
                total_absent += sdata.get("absent", 0)

        self.assertEqual(
            total_absent, EXPECTED_TOTAL_ABSENT,
            f"Expected {EXPECTED_TOTAL_ABSENT} total absentees, got {total_absent}"
        )

    def test_district_total_reported_expelled_candidates(self):
        """B3.2: Verify total expelled/reported candidates across district equals 3."""
        total_expelled = 0
        for c in self.colleges:
            stats = c.get("stream_stats", {})
            for sname, sdata in stats.items():
                total_expelled += sdata.get("expelled", 0)

        self.assertEqual(
            total_expelled, 3,
            f"Expected exactly 3 expelled/reported examinees across Narail, got {total_expelled}"
        )

    def test_failed_candidates_have_zero_or_none_gpa(self):
        """B3.3: Verify failed candidates are assigned GPA 0.0 or None and never receive passing GPA."""
        failed_students = [
            s for s in self.students
            if "FAIL" in str(s.get("status", "")).upper() or str(s.get("status", "")) in ["F1", "F2"]
        ]
        self.assertGreater(len(failed_students), 0, "No failed students available for testing")
        for s in failed_students:
            gpa = s.get("gpa")
            gpa_f = float(gpa) if gpa is not None else 0.0
            self.assertEqual(
                gpa_f, 0.0,
                f"Failed student roll {s.get('roll')} has non-zero GPA: {gpa}"
            )

    def test_f1_candidate_has_exactly_one_f_grade(self):
        """B3.4: Verify students with single compulsory failure are marked FAIL, while 4th subject F permits passing."""
        failed_with_1_f = 0
        passed_with_4th_subject_f = 0
        for s in self.students:
            subjects = s.get("subjects")
            if isinstance(subjects, list):
                f_count = sum(1 for sub in subjects if sub.get("grade", "").strip() == "F")
                status = str(s.get("status", "")).upper()
                if f_count == 1:
                    if "FAIL" in status or "F1" in status:
                        failed_with_1_f += 1
                    elif "PASS" in status:
                        passed_with_4th_subject_f += 1
        self.assertGreater(failed_with_1_f, 0, "No failed candidates with 1 F grade identified in records")
        # Ensure system correctly permits 4th subject failure without failing the student (as observed in roll 517762)
        self.assertGreaterEqual(passed_with_4th_subject_f, 1)

    def test_f2_candidate_has_exactly_two_f_grades(self):
        """B3.5: Verify students with two failures (F2) have exactly two subjects with letter grade 'F'."""
        f2_found = 0
        for s in self.students:
            subjects = s.get("subjects")
            if isinstance(subjects, list):
                f_count = sum(1 for sub in subjects if sub.get("grade", "").strip() == "F")
                if f_count == 2:
                    f2_found += 1
                    status = str(s.get("status", "")).upper()
                    self.assertTrue(
                        "FAIL" in status or "F2" in status,
                        f"Student {s.get('roll')} with 2 F grades not marked FAIL/F2"
                    )
        self.assertGreater(f2_found, 0, "No candidates with 2 F grades identified in records")

    def test_absent_candidates_have_no_subject_grades(self):
        """B3.6: Verify Absent examinees have empty subject grade lists."""
        absent_students = [
            s for s in self.students
            if "ABSENT" in str(s.get("status", "")).upper() or "ABST" in str(s.get("status", "")).upper()
        ]
        for s in absent_students:
            subjects = s.get("subjects", [])
            self.assertEqual(
                len(subjects), 0,
                f"Absent student roll {s.get('roll')} should have 0 subject grades"
            )

if __name__ == "__main__":
    unittest.main()
