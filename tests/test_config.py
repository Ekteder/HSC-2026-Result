# tests/test_config.py
"""
Central configuration, paths, and authoritative ground truth data for the Narail HSC 2026 E2E Test Suite.
"""
import os
from typing import Dict, Any, Set, Tuple

# Base Directories
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APP_DIR = os.path.join(WORKSPACE_ROOT, "narail_results_app")
APP_DATA_DIR = os.path.join(APP_DIR, "data")
APP_PUBLIC_DATA_DIR = os.path.join(APP_DIR, "public", "data")
ROOT_DATA_DIR = os.path.join(WORKSPACE_ROOT, "data")
ROOT_PUBLIC_DATA_DIR = os.path.join(WORKSPACE_ROOT, "public", "data")

# Authoritative Survey & Ground Truth Data
SURVEY_DIR = os.path.join(WORKSPACE_ROOT, ".agents", "teamwork", "survey_explorer_2")
SURVEY_JSON = os.path.join(SURVEY_DIR, "narail_colleges_hsc2026.json")
SURVEY_REPORT = os.path.join(SURVEY_DIR, "narail_colleges_report.md")
SPEC_REPORT = os.path.join(WORKSPACE_ROOT, ".agents", "teamwork", "survey_spec_miner_1", "spec_report.md")
ORIGINAL_REQUEST = os.path.join(WORKSPACE_ROOT, ".agents", "teamwork", "ORIGINAL_REQUEST.md")
PROJECT_MD = os.path.join(WORKSPACE_ROOT, ".agents", "teamwork", "orchestrator", "PROJECT.md")

# Ground Truth Official BISE Jashore Constants (Published 31 October 2026)
EXPECTED_TOTAL_COLLEGES = 24
EXPECTED_TOTAL_REGISTERED = 5065
EXPECTED_TOTAL_APPEARED = 4829
EXPECTED_TOTAL_ABSENT = 236
EXPECTED_TOTAL_PASSED = 1776
EXPECTED_TOTAL_GPA5 = 105
EXPECTED_DISTRICT_PASS_RATE_APPEARED = 36.78
EXPECTED_DISTRICT_PASS_RATE_ENROLLED = 35.06

# Upazila Breakdown Ground Truth
EXPECTED_UPAZILA_BREAKDOWN = {
    "Narail Sadar": {
        "colleges": 12,
        "enrolled": 2356,
        "passed": 982,
        "pass_rate": 41.68,
        "gpa5": 80
    },
    "Lohagara": {
        "colleges": 7,
        "enrolled": 1751,
        "passed": 534,
        "pass_rate": 30.50,
        "gpa5": 19
    },
    "Kalia": {
        "colleges": 5,
        "enrolled": 958,
        "passed": 260,
        "pass_rate": 27.14,
        "gpa5": 6
    }
}

# Stream Breakdown Ground Truth
EXPECTED_STREAM_BREAKDOWN = {
    "Science": {
        "appeared": 815,
        "passed": 458,
        "failed_absent": 357,
        "pass_rate": 56.20,
        "gpa5": 56,
        "roll_min": 517503,
        "roll_max": 522733
    },
    "Humanities": {
        "appeared": 3748,
        "passed": 1168,
        "failed_absent": 2580,
        "pass_rate": 31.16,
        "gpa5": 45,
        "roll_min": 664448,
        "roll_max": 682211
    },
    "Business Studies": {
        "appeared": 502,
        "passed": 150,
        "failed_absent": 352,
        "pass_rate": 29.88,
        "gpa5": 4,
        "roll_min": 810146,
        "roll_max": 812518
    }
}

# Exhaustive Master EIIN List for Narail District (24 Colleges)
ALL_24_EIINS: Set[int] = {
    118382, 118383, 118384, 118385, 118386,
    118404, 118435, 118436, 118437, 118438, 118439, 118440,
    118521, 118522, 118523, 118524, 118525, 118526, 118527, 118528, 118529, 118530, 118531,
    131996
}

# Key College Benchmarks for Boundary Testing
COLLEGES_ZERO_OR_LOW_PASS = [
    {"eiin": 118404, "name": "Makrail Karim Khalek Solaiman Institution", "pass_rate": 0.00, "passed": 0, "gpa5": 0},
    {"eiin": 118522, "name": "Juralia Bahumukhi Adarsa College", "pass_rate": 4.17, "passed": 1, "gpa5": 0},
    {"eiin": 131996, "name": "Birshestra Noormohammad Mahabiddyalya", "pass_rate": 13.33, "passed": 6, "gpa5": 0},
    {"eiin": 118436, "name": "Laxmipasha Ideal Women College", "pass_rate": 14.41, "passed": 34, "gpa5": 3},
    {"eiin": 118531, "name": "Habokhali Adarsha Mahabiddalay", "pass_rate": 14.52, "passed": 9, "gpa5": 0}
]

COLLEGES_HIGH_PERFORMANCE = [
    {"eiin": 118527, "name": "Government Victoria College, Narail", "pass_rate": 61.63, "passed": 538, "gpa5": 69},
    {"eiin": 118437, "name": "Lohagara Govt. Adarsha College", "pass_rate": 49.14, "passed": 285, "gpa5": 13},
    {"eiin": 118525, "name": "Narail Govt. Mohila College", "pass_rate": 38.59, "passed": 159, "gpa5": 5},
    {"eiin": 118528, "name": "Gobra Mittra Mahabiddyalya", "pass_rate": 37.30, "passed": 69, "gpa5": 3},
    {"eiin": 118385, "name": "Govt. Shaheed Abdus Salam College", "pass_rate": 26.37, "passed": 72, "gpa5": 5}
]

# Non-passing Status Codes Specified by BISE Jashore
VALID_RESULT_STATUSES = {"PASSED", "FAIL", "F1", "F2", "ABSENT", "REPORTED", "Abst", "Expl"}

# Required Schema Fields in Student Record
REQUIRED_STUDENT_FIELDS = {
    "roll", "name", "stream", "gpa", "status"
}
RECOMMENDED_STUDENT_FIELDS = {
    "roll", "name", "stream", "gpa", "status", "father_name", "mother_name", "session", "subjects"
}
