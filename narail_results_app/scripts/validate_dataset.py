#!/usr/bin/env python3
"""
Comprehensive Validation Script for HSC 2026 Narail District Results.
Strictly verifies that parsed datasets adhere to official BISE Jashore statistics:
- 24 participating institutions
- Exactly 5,065 total examinees
- Exactly 1,776 passed candidates
- Exactly 105 GPA 5.00 achievers
- Stream counts: Science (815), Humanities (3,748), Business Studies (502)
- Upazila counts: Narail Sadar (2,356), Lohagara (1,751), Kalia (958)
- Every student record contains roll, stream, GPA, status, and subjects.
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("validate_dataset")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(APP_DIR, "data")
PUBLIC_DATA_DIR = os.path.join(APP_DIR, "public", "data")

EXPECTED_EIINS = [
    118382, 118383, 118384, 118385, 118386, 118404, 118435, 118436,
    118437, 118438, 118439, 118440, 118521, 118522, 118523, 118524,
    118525, 118526, 118527, 118528, 118529, 118530, 118531, 131996
]

EXPECTED_STREAMS = {
    "Science": {"appeared": 815, "passed": 458, "gpa5": 56},
    "Humanities": {"appeared": 3748, "passed": 1168, "gpa5": 45},
    "Business Studies": {"appeared": 502, "passed": 150, "gpa5": 4}
}

EXPECTED_UPAZILAS = {
    "Narail Sadar": {"colleges": 12, "appeared": 2356, "passed": 982, "gpa5": 80},
    "Lohagara": {"colleges": 7, "appeared": 1751, "passed": 534, "gpa5": 19},
    "Kalia": {"colleges": 5, "appeared": 958, "passed": 260, "gpa5": 6}
}


def test_file_existence_and_json_validity(target_dir: str):
    logger.info(f"Checking file existence and JSON validity in {target_dir}...")
    manifest_path = os.path.join(target_dir, "manifest.json")
    roll_lookup_path = os.path.join(target_dir, "roll_lookup.json")
    all_students_path = os.path.join(target_dir, "narail_all_students.json")

    assert os.path.exists(manifest_path), f"Missing {manifest_path}"
    assert os.path.exists(roll_lookup_path), f"Missing {roll_lookup_path}"
    assert os.path.exists(all_students_path), f"Missing {all_students_path}"

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    with open(roll_lookup_path, "r", encoding="utf-8") as f:
        lookup = json.load(f)
    with open(all_students_path, "r", encoding="utf-8") as f:
        all_students = json.load(f)

    colleges_dir = os.path.join(target_dir, "colleges")
    assert os.path.isdir(colleges_dir), f"Missing colleges directory at {colleges_dir}"

    college_files = os.listdir(colleges_dir)
    assert len(college_files) == 24, f"Expected 24 college files in {colleges_dir}, found {len(college_files)}"

    for eiin in EXPECTED_EIINS:
        cf = os.path.join(colleges_dir, f"{eiin}.json")
        assert os.path.exists(cf), f"Missing college file for EIIN {eiin} at {cf}"
        with open(cf, "r", encoding="utf-8") as f:
            cdata = json.load(f)
            assert cdata.get("eiin") == eiin or cdata.get("eiin") == str(eiin), f"EIIN mismatch in {cf}"

    logger.info("✓ File structure and JSON syntax 100% valid.")
    return manifest, lookup, all_students


def test_dataset_reconciliation(all_students: List[Dict[str, Any]], manifest: Dict[str, Any], lookup: Dict[str, Any]):
    logger.info("Validating exact numerical reconciliation...")

    # 1. Total examinees
    total_students = len(all_students)
    assert total_students == 5065, f"Expected 5,065 students, got {total_students}"
    assert len(lookup) == 5065, f"Expected 5,065 lookup entries, got {len(lookup)}"

    # 2. Passed & GPA 5.00
    passed_students = [s for s in all_students if s["status"] == "PASSED"]
    gpa5_students = [s for s in passed_students if s["gpa"] >= 5.00]

    assert len(passed_students) == 1776, f"Expected 1,776 passed students, got {len(passed_students)}"
    assert len(gpa5_students) == 105, f"Expected 105 GPA 5.00 students, got {len(gpa5_students)}"

    # 3. Stream counts
    for s_name, exp in EXPECTED_STREAMS.items():
        s_list = [s for s in all_students if s["stream"] == s_name]
        s_passed = [s for s in s_list if s["status"] == "PASSED"]
        s_gpa5 = [s for s in s_passed if s["gpa"] >= 5.00]

        assert len(s_list) == exp["appeared"], f"Stream {s_name} appeared mismatch: expected {exp['appeared']}, got {len(s_list)}"
        assert len(s_passed) == exp["passed"], f"Stream {s_name} passed mismatch: expected {exp['passed']}, got {len(s_passed)}"
        assert len(s_gpa5) == exp["gpa5"], f"Stream {s_name} GPA 5 mismatch: expected {exp['gpa5']}, got {len(s_gpa5)}"
        logger.info(f"✓ Stream {s_name:16}: Appeared={len(s_list)}, Passed={len(s_passed)}, GPA 5.00={len(s_gpa5)}")

    # 4. Upazila counts
    for u_name, exp in EXPECTED_UPAZILAS.items():
        u_list = [s for s in all_students if s["upazila"] == u_name]
        u_passed = [s for s in u_list if s["status"] == "PASSED"]
        u_gpa5 = [s for s in u_passed if s["gpa"] >= 5.00]

        assert len(u_list) == exp["appeared"], f"Upazila {u_name} appeared mismatch: expected {exp['appeared']}, got {len(u_list)}"
        assert len(u_passed) == exp["passed"], f"Upazila {u_name} passed mismatch: expected {exp['passed']}, got {len(u_passed)}"
        assert len(u_gpa5) == exp["gpa5"], f"Upazila {u_name} GPA 5 mismatch: expected {exp['gpa5']}, got {len(u_gpa5)}"
        logger.info(f"✓ Upazila {u_name:14}: Appeared={len(u_list)}, Passed={len(u_passed)}, GPA 5.00={len(u_gpa5)}")

    # 5. Manifest reconciliation
    m_sum = manifest["summary"]
    assert m_sum["total_colleges"] == 24, "Manifest total colleges != 24"
    assert m_sum["total_examinees"] == 5065, "Manifest total examinees != 5065"
    assert m_sum["total_passed"] == 1776, "Manifest total passed != 1776"
    assert m_sum["gpa5_count"] == 105, "Manifest GPA 5 count != 105"

    logger.info("✓ Statistical reconciliation matches BISE Jashore official figures with 100% precision.")


def test_individual_student_integrity(all_students: List[Dict[str, Any]]):
    logger.info("Validating individual student schema integrity...")

    seen_rolls = set()
    status_counts = {"PASSED": 0, "FAILED": 0, "ABSENT": 0, "REPORTED": 0}

    for idx, s in enumerate(all_students):
        roll = s.get("roll")
        assert roll and len(str(roll)) == 6, f"Invalid roll at index {idx}: {roll}"
        assert roll not in seen_rolls, f"Duplicate roll detected: {roll}"
        seen_rolls.add(roll)

        # Names & Parents
        assert s.get("name"), f"Missing student name for roll {roll}"
        assert "father_name" in s, f"Missing father_name field for roll {roll}"
        assert "mother_name" in s, f"Missing mother_name field for roll {roll}"

        # Stream & College
        assert s.get("stream") in EXPECTED_STREAMS, f"Unknown stream for roll {roll}: {s.get('stream')}"
        assert s.get("eiin") in EXPECTED_EIINS, f"Unknown EIIN for roll {roll}: {s.get('eiin')}"
        assert s.get("college_name"), f"Missing college name for roll {roll}"
        assert s.get("upazila") in EXPECTED_UPAZILAS, f"Unknown upazila for roll {roll}: {s.get('upazila')}"

        # Status & GPA
        status = s.get("status")
        assert status in status_counts, f"Invalid status for roll {roll}: {status}"
        status_counts[status] += 1

        gpa = s.get("gpa")
        assert isinstance(gpa, (int, float)), f"GPA is not a number for roll {roll}: {gpa}"

        if status == "PASSED":
            assert 1.00 <= gpa <= 5.00, f"Passed student with out-of-range GPA for roll {roll}: {gpa}"
        elif status in ["FAILED", "ABSENT", "REPORTED"]:
            assert gpa == 0.0, f"Non-passed student has non-zero GPA for roll {roll}: {gpa}"

        # Subjects
        subs = s.get("subjects")
        assert isinstance(subs, list), f"Subjects is not a list for roll {roll}"
        if status in ["PASSED", "FAILED"]:
            assert len(subs) > 0, f"Examinee with status {status} has 0 subjects for roll {roll}"
            for sub in subs:
                assert "name" in sub or "subject" in sub, f"Missing subject title in roll {roll}"
                assert "grade" in sub, f"Missing grade in roll {roll}"
                assert sub["grade"] in ["A+", "A", "A-", "B", "C", "D", "F", "X"], f"Invalid grade {sub['grade']} in roll {roll}"

    logger.info(f"✓ Individual schema verified across all 5,065 records:")
    logger.info(f"  Passed: {status_counts['PASSED']}")
    logger.info(f"  Failed: {status_counts['FAILED']}")
    logger.info(f"  Absent: {status_counts['ABSENT']}")
    logger.info(f"  Reported/Expelled: {status_counts['REPORTED']}")


def main():
    logger.info("=== Starting Dataset Verification ===")
    try:
        # Validate data/ directory
        manifest, lookup, all_students = test_file_existence_and_json_validity(DATA_DIR)
        test_dataset_reconciliation(all_students, manifest, lookup)
        test_individual_student_integrity(all_students)

        # Validate public/data/ directory
        pub_manifest, pub_lookup, pub_students = test_file_existence_and_json_validity(PUBLIC_DATA_DIR)
        test_dataset_reconciliation(pub_students, pub_manifest, pub_lookup)
        test_individual_student_integrity(pub_students)

        logger.info("==================================================================")
        logger.info("🎉 ALL VALIDATION CHECKS PASSED: 100% DATA INTEGRITY CONFIRMED! 🎉")
        logger.info("==================================================================")
        sys.exit(0)
    except AssertionError as e:
        logger.error(f"❌ VALIDATION ASSERTION FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ UNEXPECTED VALIDATION ERROR: {e}", exc_info=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
