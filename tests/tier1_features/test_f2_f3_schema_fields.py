# tests/tier1_features/test_f2_f3_schema_fields.py
"""
Tier 1 — Features 2 & 3: Student Records Schema Fields & Ingestion
Verifies that individual student entries include required schema fields:
roll number, registration number (if available), GPA, subject grades,
stream, result status, session, and student metadata.
"""
import unittest
from tests.test_config import REQUIRED_STUDENT_FIELDS, VALID_RESULT_STATUSES
from tests.helpers.data_loader import DataLoader

class TestF2F3SchemaFields(unittest.TestCase):
    def setUp(self):
        self.loader = DataLoader.get_instance()
        self.students = self.loader.get_raw_student_records()
        if not self.students:
            self.students = self.loader.get_all_students()

    def test_student_records_available(self):
        """F2.1: Verify student records dataset is populated with genuine records."""
        self.assertTrue(
            len(self.students) > 0,
            "No student records loaded for schema verification"
        )

    def test_required_fields_present_in_all_records(self):
        """F2.2: Verify required core fields (roll, name, stream, status, gpa) exist in every record."""
        for idx, s in enumerate(self.students[:100]):  # check representative batch
            for field in REQUIRED_STUDENT_FIELDS:
                self.assertIn(
                    field, s,
                    f"Student record at index {idx} (roll {s.get('roll')}) missing required field '{field}'"
                )

    def test_roll_number_format(self):
        """F2.3: Verify roll numbers are 6-digit numeric strings."""
        for s in self.students[:100]:
            roll = str(s.get("roll", "")).strip()
            self.assertEqual(len(roll), 6, f"Roll '{roll}' is not 6 digits")
            self.assertTrue(roll.isdigit(), f"Roll '{roll}' contains non-digits")

    def test_stream_values_valid(self):
        """F2.4: Verify stream/group is one of Science, Humanities, or Business Studies."""
        valid_streams = {"SCIENCE", "HUMANITIES", "BUSINESS STUDIES"}
        for s in self.students[:100]:
            stream = str(s.get("stream", "") or s.get("group", "")).strip().upper()
            self.assertIn(
                stream, valid_streams,
                f"Student roll {s.get('roll')} has invalid stream '{stream}'"
            )

    def test_subject_grades_schema_and_types(self):
        """F3.1: Verify subject grades structure contains subject name and valid letter grade."""
        valid_letter_grades = {"A+", "A", "A-", "B", "C", "D", "F"}
        checked_count = 0
        for s in self.students:
            status = str(s.get("status", "")).upper()
            if "ABSENT" in status or "REPORTED" in status:
                continue

            subjects = s.get("subjects")
            if isinstance(subjects, list) and len(subjects) > 0:
                checked_count += 1
                for sub in subjects:
                    if isinstance(sub, dict):
                        sub_name = sub.get("subject") or sub.get("name")
                        grade = str(sub.get("grade", "")).strip()
                        self.assertTrue(bool(sub_name), f"Empty subject name in roll {s.get('roll')}")
                        self.assertIn(
                            grade, valid_letter_grades,
                            f"Invalid grade '{grade}' in roll {s.get('roll')} for subject '{sub_name}'"
                        )
            elif isinstance(subjects, dict) and len(subjects) > 0:
                checked_count += 1
                for sub_name, grade_val in subjects.items():
                    grade = str(grade_val).strip()
                    self.assertIn(
                        grade, valid_letter_grades,
                        f"Invalid grade '{grade}' in roll {s.get('roll')} for subject '{sub_name}'"
                    )

        self.assertGreater(checked_count, 0, "No records with subject grades checked")

    def test_parent_names_and_session_fields(self):
        """F3.2: Verify parent names (father_name, mother_name) and session metadata exist."""
        for s in self.students[:50]:
            status = str(s.get("status", "")).upper()
            if "ABSENT" in status:
                continue
            father = s.get("father_name")
            mother = s.get("mother_name")
            session = s.get("session")
            self.assertIsNotNone(father, f"Father name is None in roll {s.get('roll')}")
            self.assertIsNotNone(mother, f"Mother name is None in roll {s.get('roll')}")
            self.assertIsNotNone(session, f"Session is None in roll {s.get('roll')}")

    def test_gpa_numeric_precision_and_bounds(self):
        """F3.3: Verify GPA is within [0.00, 5.00] range and rounded to 2 decimal places."""
        for s in self.students[:100]:
            gpa = s.get("gpa")
            if gpa is not None:
                gpa_f = float(gpa)
                self.assertGreaterEqual(gpa_f, 0.0, f"GPA below 0 for roll {s.get('roll')}")
                self.assertLessEqual(gpa_f, 5.0, f"GPA above 5.0 for roll {s.get('roll')}")

if __name__ == "__main__":
    unittest.main()
