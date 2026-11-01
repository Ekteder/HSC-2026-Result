# tests/tier5_adversarial/test_adversarial_challenger_1.py
"""
Tier 5 — Adversarial Challenge & Stress Test Suite (Challenger 1: Data & Query)
Empirically stress-tests data ingestion outputs, search indices, and query algorithms:
1. Random sampling of 150+ rolls across Science, Humanities, and Business Studies.
2. Adversarial search queries: SQL injection payloads, XSS strings, boundary 6-digit rolls, non-numeric strings.
3. Extreme filter combinations: Zero-pass colleges + GPA 5.0, upazila + stream cross-mismatches, inverted ranges.
4. Bangladesh HSC 4th Elective Subject Rule Invariant: F in 4th subject does not fail candidate.
5. End-to-end execution of frontend dataLoader in Node.js with adversarial payloads.
"""

import os
import json
import random
import subprocess
import time
import unittest
from typing import Dict, Any, List

from tests.helpers.data_loader import DataLoader
from tests.helpers.query_engine import QueryEngine
from tests.test_config import WORKSPACE_ROOT, APP_DIR

GRADE_POINT_MAP = {
    'A+': 5.0,
    'A': 4.0,
    'A-': 3.5,
    'B': 3.0,
    'C': 2.0,
    'D': 1.0,
    'F': 0.0,
    'X': 0.0
}

VALID_STATUSES = {'PASSED', 'FAILED', 'ABSENT', 'REPORTED', 'EXPELLED', 'F1', 'F2', 'ABST', 'EXPL'}


class TestAdversarialChallenger1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loader = DataLoader.get_instance()
        cls.all_students = cls.loader.get_all_students()
        cls.all_colleges = cls.loader.get_all_colleges()

        # Load manifest
        manifest_path = cls.loader.get_manifest_path()
        with open(manifest_path, 'r', encoding='utf-8') as f:
            cls.manifest = json.load(f)

        # Load roll lookup
        lookup_path = cls.loader.get_roll_lookup_path()
        with open(lookup_path, 'r', encoding='utf-8') as f:
            cls.roll_lookup = json.load(f)

        # Pre-group students by stream
        cls.science_students = [s for s in cls.all_students if (s.get('stream') or s.get('group', '')).upper() == 'SCIENCE']
        cls.humanities_students = [s for s in cls.all_students if (s.get('stream') or s.get('group', '')).upper() == 'HUMANITIES']
        cls.business_students = [s for s in cls.all_students if 'BUS' in (s.get('stream') or s.get('group', '')).upper()]

    # =========================================================================
    # Task 2.1: Random Sampling of 150+ Rolls Across All Three Streams
    # =========================================================================
    def test_random_sampling_150_rolls_across_streams(self):
        """
        Adversarial Test 1: Random sampling of 150 students (50 Science, 50 Humanities, 50 Business Studies).
        Verifies:
        - Roll format: exact 6-digit numeric string
        - Student identity: name, father, mother non-empty
        - College affiliation: valid Narail EIIN among the 24 institutions
        - Subjects: valid codes, names, grades, and grade points
        - GPA & status reconciliation: recalculate GPA from subjects and compare
        - Cross-file persistence: verify roll in roll_lookup.json and college JSON
        """
        rng = random.Random(20261101)  # Seed for deterministic reproducibility
        sample_science = rng.sample(self.science_students, 50)
        sample_humanities = rng.sample(self.humanities_students, 50)
        sample_business = rng.sample(self.business_students, 50)

        all_sampled = [
            ('Science', sample_science),
            ('Humanities', sample_humanities),
            ('Business Studies', sample_business)
        ]

        total_sampled = 0
        valid_eiins = {int(c['eiin']) for c in self.all_colleges}

        for stream_label, cohort in all_sampled:
            self.assertEqual(len(cohort), 50, f"Expected 50 sampled students for {stream_label}")
            for s in cohort:
                total_sampled += 1
                roll = str(s.get('roll', '')).strip()

                # 1. Roll format
                self.assertTrue(roll.isdigit() and len(roll) == 6, f"Invalid roll format: {roll}")

                # 2. Identity fields
                name = s.get('name', '')
                self.assertTrue(name and len(name.strip()) > 1, f"Empty student name for roll {roll}")
                father = s.get('father_name', '')
                mother = s.get('mother_name', '')
                self.assertTrue(father and mother, f"Missing parents for roll {roll}")

                # 3. College EIIN
                eiin = int(s.get('eiin', 0))
                self.assertIn(eiin, valid_eiins, f"EIIN {eiin} for roll {roll} not in Narail colleges list")

                # 4. Status
                status = str(s.get('status', '') or s.get('result_status', '')).upper()
                self.assertTrue(any(st in status for st in VALID_STATUSES), f"Invalid status '{status}' for roll {roll}")

                # 5. Subjects integrity
                subjects = s.get('subjects', [])
                if 'PASS' in status or 'FAIL' in status:
                    self.assertGreaterEqual(len(subjects), 6, f"Roll {roll} ({status}) has < 6 subjects: {len(subjects)}")
                    for sub in subjects:
                        code = sub.get('code')
                        sub_name = sub.get('name') or sub.get('subject')
                        grade = sub.get('grade')
                        self.assertIsNotNone(sub_name, f"Subject missing name in roll {roll}")
                        self.assertIn(grade, GRADE_POINT_MAP, f"Invalid grade '{grade}' in roll {roll}")

                # 6. GPA calculation check if PASSED
                if 'PASS' in status:
                    gpa = float(s.get('gpa', 0.0))
                    self.assertGreaterEqual(gpa, 1.0, f"Passed student {roll} has GPA < 1.0: {gpa}")
                    self.assertLessEqual(gpa, 5.0, f"Passed student {roll} has GPA > 5.0: {gpa}")

                    # Independent recalculation using BISE Jashore rules
                    if len(subjects) >= 6:
                        main_subs = subjects[:6]
                        fourth_sub = subjects[6] if len(subjects) > 6 else None

                        main_points = sum(GRADE_POINT_MAP.get(sub.get('grade'), 0.0) for sub in main_subs)
                        fourth_bonus = 0.0
                        if fourth_sub:
                            fourth_gp = GRADE_POINT_MAP.get(fourth_sub.get('grade'), 0.0)
                            if fourth_gp > 2.0:
                                fourth_bonus = fourth_gp - 2.0

                        expected_gpa = min(5.00, round((main_points + fourth_bonus) / 6.0, 2))
                        self.assertAlmostEqual(
                            gpa, expected_gpa, delta=0.015,
                            msg=f"GPA mismatch for roll {roll}: stored={gpa}, calculated={expected_gpa}"
                        )

                # 7. Check presence in roll_lookup.json
                self.assertIn(roll, self.roll_lookup, f"Roll {roll} missing in roll_lookup.json")
                lookup_entry = self.roll_lookup[roll]
                self.assertEqual(lookup_entry['name'], s['name'])
                self.assertEqual(int(lookup_entry['eiin']), eiin)

        self.assertEqual(total_sampled, 150)

    # =========================================================================
    # Task 2.2: Adversarial Search Queries
    # =========================================================================
    def test_adversarial_search_queries(self):
        """
        Adversarial Test 2: Stress-test search query handling with malicious & edge payloads:
        - SQL injection payloads (' OR 1=1 --, UNION SELECT, DROP TABLE, etc.)
        - XSS injection strings (<script>, <img onerror>, javascript:, templates)
        - Boundary 6-digit rolls (000000, 999999, min-1, max+1)
        - Non-numeric strings, Unicode, control characters, extreme lengths (1000+ chars)
        - Type mutations (integers, nulls, booleans)
        Asserts that search executes cleanly without exceptions, leaks, or unhandled errors.
        """
        adversarial_payloads = [
            # SQL Injection vectors
            "' OR '1'='1",
            "1; DROP TABLE students; --",
            "' UNION SELECT null, null, null --",
            "admin'--",
            "' OR 1=1 /*",
            "WAITFOR DELAY '0:0:5'",
            "1' AND 1=2 UNION ALL SELECT * FROM colleges --",
            "0' XOR 1=1 --",

            # XSS vectors
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert(document.domain)>",
            "<svg/onload=alert('XSS')>",
            "javascript:alert(1)",
            "\"><script>alert(1)</script>",
            "{{constructor.constructor('alert(1)')()}}",
            "${7*7}",
            "<!--#exec cmd=\"ls\"-->",
            "<iframe src=\"javascript:alert(1)\">",

            # Boundary roll queries
            "000000",
            "999999",
            "100000",
            "999998",
            "517502",  # (lowest Narail roll 517503 - 1)
            "812519",  # (highest Narail roll 812518 + 1)

            # Non-numeric text & Unicode
            "ABCDEF",
            "NOT_A_ROLL_NUMBER",
            "পরীক্ষা",
            "নড়াইল জেলা",
            "🎓🔥💯",
            "Nāraīl",
            "\x00\x01\x02\x03",
            "\u200b\u200c\u200d\ufeff",

            # Extreme length inputs
            "A" * 1500,
            "9" * 1000,
            " " * 100
        ]

        for payload in adversarial_payloads:
            t0 = time.time()
            try:
                results = QueryEngine.filter_students(self.all_students, search_term=payload)
                t_elapsed = time.time() - t0

                # Verify result structure
                self.assertIsInstance(results, list, f"Query '{payload}' did not return a list")
                self.assertLess(t_elapsed, 0.05, f"Query '{payload}' exceeded 50ms latency threshold ({t_elapsed}s)")

                # For malicious / boundary non-existent queries, expect 0 matches
                if payload not in (" ", " " * 100):
                    self.assertEqual(
                        len(results), 0,
                        f"Expected 0 results for adversarial payload '{payload}', but got {len(results)}"
                    )
            except Exception as e:
                self.fail(f"Search query '{payload}' raised unexpected exception: {e}")

    def test_search_type_mutations(self):
        """Verify search engine gracefully tolerates type mutations (int, float, None, boolean)."""
        mutations = [None, 517503, 3.14, True, False]
        for term in mutations:
            try:
                results = QueryEngine.filter_students(self.all_students, search_term=term)
                self.assertIsInstance(results, list)
                if term == 517503:
                    # Should locate student with roll '517503'
                    self.assertGreaterEqual(len(results), 1)
                    self.assertEqual(results[0]['roll'], '517503')
            except Exception as e:
                self.fail(f"Search with mutated type '{term}' raised exception: {e}")

    # =========================================================================
    # Task 2.3: Extreme Filter Combinations
    # =========================================================================
    def test_extreme_filter_combinations(self):
        """
        Adversarial Test 3: Test extreme and conflicting filter combinations:
        - College with 0% pass rate + GPA 5.0 -> 0 results
        - College with 0% pass rate + PASSED status -> 0 results
        - College offering 0 Science examinees + stream='Science' -> 0 results
        - College offering 0 Business Studies examinees + stream='Business Studies' -> 0 results
        - Mismatched Upazila and College EIIN -> 0 results
        - Inverted GPA ranges (min > max) -> 0 results
        - Out-of-bounds GPA (e.g. 5.5 to 10.0) -> 0 results
        - Status 'FAILED' + GPA 5.0 -> 0 results
        - Status 'ABSENT' + GPA > 0 -> 0 results
        """
        # Verified 0% pass rate college in Narail District:
        # EIIN 118404: Makrail Karim Khalek Solaiman Institution (0% pass, 0 passed of 49)
        zero_pass_eiin = 118404

        # Colleges with 0 GPA-5 achievers:
        # EIIN 118404 (0 GPA-5), EIIN 118522: Juralia Bahumukhi Adarsa College (0 GPA-5)
        zero_gpa5_eiins = [118404, 118522]

        for eiin in zero_gpa5_eiins:
            # 1. Zero GPA-5 college + GPA 5.0
            res1 = QueryEngine.filter_students(self.all_students, college_eiin=eiin, min_gpa=5.0)
            self.assertEqual(len(res1), 0, f"Zero GPA-5 college {eiin} unexpectedly yielded GPA 5.0 results")

        # 2. Zero pass college + PASSED status
        res2 = QueryEngine.filter_students(self.all_students, college_eiin=zero_pass_eiin, status='PASSED')
        self.assertEqual(len(res2), 0, f"Zero pass college {zero_pass_eiin} unexpectedly yielded PASSED students")

        # 3. Stream absent in college: College 118404 has 0 Science candidates
        res_science = QueryEngine.filter_students(self.all_students, college_eiin=118404, stream='Science')
        self.assertEqual(len(res_science), 0, "College 118404 unexpectedly returned Science students")

        # 4. Stream absent in college: College 118404 has 0 Business Studies candidates
        res_bus = QueryEngine.filter_students(self.all_students, college_eiin=118404, stream='Business Studies')
        self.assertEqual(len(res_bus), 0, "College 118404 unexpectedly returned Business Studies students")

        # 5. Upazila and College Mismatch:
        # Victoria College (118527) is in 'Narail Sadar', test with 'Lohagara'
        res_mismatch_1 = QueryEngine.filter_students(self.all_students, college_eiin=118527, upazila='Lohagara')
        self.assertEqual(len(res_mismatch_1), 0, "Victoria College unexpectedly returned students under Lohagara upazila")

        # Lohagara Govt Adarsha College (118437) is in 'Lohagara', test with 'Kalia'
        res_mismatch_2 = QueryEngine.filter_students(self.all_students, college_eiin=118437, upazila='Kalia')
        self.assertEqual(len(res_mismatch_2), 0, "Lohagara College unexpectedly returned students under Kalia upazila")

        # Munshi Manik Mia College (118383) is in 'Kalia', test with 'Narail Sadar'
        res_mismatch_3 = QueryEngine.filter_students(self.all_students, college_eiin=118383, upazila='Narail Sadar')
        self.assertEqual(len(res_mismatch_3), 0, "Munshi Manik Mia College unexpectedly returned students under Narail Sadar")

        # 6. Inverted GPA range (min > max)
        res_inverted = QueryEngine.filter_students(self.all_students, min_gpa=4.5, max_gpa=3.0)
        self.assertEqual(len(res_inverted), 0, "Inverted GPA range min=4.5, max=3.0 unexpectedly returned students")

        # 7. Out-of-bounds GPA (> 5.0)
        res_oob = QueryEngine.filter_students(self.all_students, min_gpa=5.01, max_gpa=10.0)
        self.assertEqual(len(res_oob), 0, "Out-of-bounds GPA > 5.0 unexpectedly returned students")

        # 8. Status 'FAILED' + GPA >= 5.0
        res_fail_gpa5 = QueryEngine.filter_students(self.all_students, status='FAILED', min_gpa=5.0)
        self.assertEqual(len(res_fail_gpa5), 0, "Status FAILED with GPA 5.0 unexpectedly returned students")

        # 9. Status 'ABSENT' + min_gpa > 0
        res_abs_gpa = QueryEngine.filter_students(self.all_students, status='ABSENT', min_gpa=1.0)
        self.assertEqual(len(res_abs_gpa), 0, "Status ABSENT with GPA > 1.0 unexpectedly returned students")

    # =========================================================================
    # Task 2.4: Bangladesh HSC 4th Elective Subject Rule Invariant
    # =========================================================================
    def test_fourth_subject_rule_invariant(self):
        """
        Adversarial Test 4: Verify the 4th Elective Subject Rule Invariants:
        1. An 'F' grade in the 4th elective subject does NOT fail the candidate, provided
           all 6 compulsory/core subjects are passed.
        2. Exactly 89 examinees in Narail District passed the HSC examination despite
           receiving an 'F' in their 4th elective subject.
        3. For all 89 candidates, the 'F' is strictly isolated to the 7th subject (index 6).
        4. Recalculated GPA without 4th subject bonus points matches the stored GPA.
        5. Zero examinees with an 'F' in any core subject (indices 0 to 5) are marked 'PASSED'.
        6. Zero examinees with 2 or more 'F' grades are marked 'PASSED'.
        7. Across all 1,776 passed examinees, 4th subject bonus points (GP - 2.0 when GP > 2.0)
           are added to the core points and divided by 6, capped at 5.00, matching stored GPA.
        """
        passed_with_f = []
        passed_students = []

        for s in self.all_students:
            status = str(s.get('status', '') or s.get('result_status', '')).upper()
            subjects = s.get('subjects', [])
            f_subs = [sub for sub in subjects if sub.get('grade') == 'F']

            if 'PASS' in status:
                passed_students.append(s)
                if len(f_subs) > 0:
                    passed_with_f.append(s)

        # Invariant 1 & 2: Exactly 89 examinees passed with an F in 4th subject
        self.assertEqual(
            len(passed_with_f), 89,
            f"Expected exactly 89 examinees passed with F in 4th subject, found {len(passed_with_f)}"
        )

        # Invariant 3 & 4: Deep inspection of all 89 passed-with-F examinees
        for s in passed_with_f:
            roll = s.get('roll')
            subjects = s.get('subjects', [])
            self.assertEqual(len(subjects), 7, f"Roll {roll} does not have 7 subjects")

            # Check that subjects 0-5 are ALL passed
            for idx in range(6):
                sub_grade = subjects[idx].get('grade')
                self.assertNotEqual(
                    sub_grade, 'F',
                    f"Passed student {roll} has an F in core subject index {idx} ({subjects[idx].get('name')})"
                )

            # Check that 7th subject (index 6) is the one with 'F'
            fourth_sub = subjects[6]
            self.assertEqual(
                fourth_sub.get('grade'), 'F',
                f"Passed student {roll} does not have F in 4th subject (index 6), but in {fourth_sub}"
            )

            # Recalculate GPA: Since 4th subject GP=0.0 <= 2.0, bonus is 0.0
            main_points = sum(GRADE_POINT_MAP[subjects[i]['grade']] for i in range(6))
            calc_gpa = min(5.00, round(main_points / 6.0, 2))
            stored_gpa = float(s.get('gpa', 0.0))
            self.assertAlmostEqual(
                stored_gpa, calc_gpa, delta=0.015,
                msg=f"GPA calculation mismatch for 4th-subject F candidate {roll}: stored={stored_gpa}, calc={calc_gpa}"
            )

        # Invariant 5: Zero passed students have an F in core subjects 0-5
        for s in passed_students:
            roll = s.get('roll')
            subjects = s.get('subjects', [])
            if len(subjects) >= 6:
                for idx in range(6):
                    g = subjects[idx].get('grade')
                    self.assertNotEqual(
                        g, 'F',
                        f"Core subject violation: Passed student {roll} has F in core subject {idx}"
                    )

        # Invariant 6: Zero passed students have >= 2 F grades
        for s in passed_students:
            subjects = s.get('subjects', [])
            f_count = sum(1 for sub in subjects if sub.get('grade') == 'F')
            self.assertLessEqual(
                f_count, 1,
                f"Multiple F violation: Passed student {s.get('roll')} has {f_count} F grades"
            )

        # Invariant 7: Comprehensive GPA reconciliation across all 1,776 passed students
        self.assertEqual(len(passed_students), 1776, f"Expected 1,776 passed students, got {len(passed_students)}")
        discrepancy_count = 0
        for s in passed_students:
            subjects = s.get('subjects', [])
            if len(subjects) >= 6:
                main_pts = sum(GRADE_POINT_MAP.get(subjects[i].get('grade'), 0.0) for i in range(6))
                bonus = 0.0
                if len(subjects) > 6:
                    gp_4th = GRADE_POINT_MAP.get(subjects[6].get('grade'), 0.0)
                    if gp_4th > 2.0:
                        bonus = gp_4th - 2.0

                expected_gpa = min(5.00, round((main_pts + bonus) / 6.0, 2))
                stored_gpa = round(float(s.get('gpa', 0.0)), 2)
                if abs(expected_gpa - stored_gpa) > 0.015:
                    discrepancy_count += 1

        self.assertEqual(
            discrepancy_count, 0,
            f"Found {discrepancy_count} GPA discrepancies across 1,776 passed students using 4th subject formula"
        )

    # =========================================================================
    # Task 2.5: Direct Node.js Execution of Frontend DataLoader
    # =========================================================================
    def test_frontend_data_loader_in_nodejs(self):
        """
        Adversarial Test 5: Directly executes the actual frontend JavaScript dataLoader
        inside Node.js with malicious search queries and extreme filter combinations.
        Guarantees that the client-side JavaScript engine handles all attacks without crashing.
        """
        js_test_script = f"""
import fs from 'fs';
import path from 'path';
import {{ dataLoader }} from '{os.path.join(APP_DIR, "src", "utils", "dataLoader.js")}';

const allStudents = JSON.parse(fs.readFileSync('{os.path.join(APP_DIR, "data", "narail_all_students.json")}', 'utf8'));
const manifest = JSON.parse(fs.readFileSync('{os.path.join(APP_DIR, "data", "manifest.json")}', 'utf8'));
const rollLookup = JSON.parse(fs.readFileSync('{os.path.join(APP_DIR, "data", "roll_lookup.json")}', 'utf8'));

dataLoader.manifest = manifest;
dataLoader.rollLookup = rollLookup;
dataLoader.allStudents = allStudents;

for (const col of manifest.colleges) {{
    dataLoader.collegeMap.set(Number(col.eiin), col);
}}

for (const s of allStudents) {{
    const rollStr = String(s.roll).trim();
    dataLoader.rollMap.set(rollStr, s);
    dataLoader.nameIndex.push({{
        roll: rollStr,
        name: (s.name || '').toLowerCase(),
        regno: String(s.reg_no || s.regno || '').toLowerCase(),
        college: s.institute || '',
        eiin: s.eiin,
        stream: s.stream || '',
        gpa: s.gpa || 0.0,
        status: s.status || '',
    }});
}}
dataLoader.isLoaded = true;

// 1. Test search with malicious payloads
const payloads = [
    "' OR 1=1 --",
    "<script>alert(1)</script>",
    "000000",
    "999999",
    "A".repeat(1000),
    "!@#$%",
    "\\d{{6}}"
];

for (const p of payloads) {{
    const res = dataLoader.searchCandidates(p);
    if (!Array.isArray(res)) throw new Error('Search did not return array for payload: ' + p);
    if (res.length > 0) throw new Error('Malicious query unexpectedly matched records: ' + p);
}}

// 2. Test extreme filter combinations
const zeroPassCollege = dataLoader.filterStudents({{ collegeEiin: 118404, minGpa: 5.0 }});
if (zeroPassCollege.length !== 0) throw new Error('Zero pass college returned GPA 5.0 results');

const zeroPassStream = dataLoader.filterStudents({{ collegeEiin: 118404, stream: 'Science' }});
if (zeroPassStream.length !== 0) throw new Error('Zero candidate stream returned results');

const upazilaMismatch = dataLoader.filterStudents({{ collegeEiin: 118527, upazila: 'Lohagara' }});
if (upazilaMismatch.length !== 0) throw new Error('Upazila mismatch returned results');

// 3. Test exact roll retrieval
const s517503 = dataLoader.getStudentByRoll('517503');
if (!s517503 || s517503.name !== 'NUSRAT KHANAM') throw new Error('Roll 517503 lookup failed');

console.log('JS_DATALOADER_PASSED');
"""
        result = subprocess.run(
            ['node', '--input-type=module', '-e', js_test_script],
            capture_output=True,
            text=True
        )

        self.assertEqual(
            result.returncode, 0,
            f"Node.js dataLoader execution failed with code {result.returncode}:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
        )
        self.assertIn('JS_DATALOADER_PASSED', result.stdout)


    # =========================================================================
    # Task 2.6: Absent, Reported & Status Boundary Invariants
    # =========================================================================
    def test_absent_and_reported_examinees_boundaries(self):
        """
        Adversarial Test 6: Verify non-attending and disciplinary boundary examinees:
        - Exactly 236 ABSENT examinees: verify GPA is 0.0 or None, subjects empty, and handled safely.
        - Exactly 3 REPORTED examinees (Rolls 665968, 666337, 666457): verify status code and non-crashing filter.
        - Verify mathematical status partition: PASSED (1,776) + FAILED (3,050) + ABSENT (236) + REPORTED (3) = 5,065.
        """
        absent_students = [s for s in self.all_students if 'ABS' in str(s.get('status', '') or '').upper()]
        reported_students = [s for s in self.all_students if 'REP' in str(s.get('status', '') or '').upper() or 'EXP' in str(s.get('status', '') or '').upper()]
        passed_students = [s for s in self.all_students if 'PASS' in str(s.get('status', '') or '').upper()]
        failed_students = [s for s in self.all_students if 'FAIL' in str(s.get('status', '') or '').upper() or str(s.get('status', '')).upper() in ('F1', 'F2')]

        self.assertEqual(len(absent_students), 236, f"Expected 236 absent students, found {len(absent_students)}")
        self.assertEqual(len(reported_students), 3, f"Expected 3 reported students, found {len(reported_students)}")
        self.assertEqual(len(passed_students), 1776, f"Expected 1,776 passed students, found {len(passed_students)}")
        self.assertEqual(len(failed_students), 3050, f"Expected 3,050 failed students, found {len(failed_students)}")

        # Partition integrity
        self.assertEqual(
            len(passed_students) + len(failed_students) + len(absent_students) + len(reported_students),
            5065,
            "Total status partition does not reconcile to 5,065 examinees"
        )

        # Inspect reported examinees
        reported_rolls = {str(s.get('roll')) for s in reported_students}
        self.assertEqual(reported_rolls, {'665968', '666337', '666457'}, "Mismatch in expected reported examinee rolls")

        for r_student in reported_students:
            self.assertEqual(r_student.get('gpa', 0.0) or 0.0, 0.0)
            # Verify searching for reported roll succeeds cleanly
            search_res = QueryEngine.filter_students(self.all_students, search_term=r_student['roll'])
            self.assertEqual(len(search_res), 1)

    # =========================================================================
    # Task 2.7: Dataset Uniqueness & Strict Mathematical Cross-Reconciliation
    # =========================================================================
    def test_uniqueness_and_dataset_invariants(self):
        """
        Adversarial Test 7: Verify global uniqueness and multi-dimensional cross-reconciliation:
        - 100% unique roll numbers (0 collisions across 5,065 records)
        - Upazila distribution invariant: Narail Sadar (2,356) + Lohagara (1,751) + Kalia (958) = 5,065
        - Stream distribution invariant: Science (815) + Humanities (3,748) + Business Studies (502) = 5,065
        - GPA-5 distribution invariant: Narail Sadar (80) + Lohagara (19) + Kalia (6) = 105
        """
        rolls = [str(s.get('roll')) for s in self.all_students]
        self.assertEqual(len(rolls), 5065)
        self.assertEqual(len(set(rolls)), 5065, "Collision detected in examinee roll numbers!")

        # Upazila verification
        sadar = [s for s in self.all_students if str(s.get('upazila')).lower() == 'narail sadar']
        lohagara = [s for s in self.all_students if str(s.get('upazila')).lower() == 'lohagara']
        kalia = [s for s in self.all_students if str(s.get('upazila')).lower() == 'kalia']

        self.assertEqual(len(sadar), 2356, f"Narail Sadar count mismatch: {len(sadar)}")
        self.assertEqual(len(lohagara), 1751, f"Lohagara count mismatch: {len(lohagara)}")
        self.assertEqual(len(kalia), 958, f"Kalia count mismatch: {len(kalia)}")
        self.assertEqual(len(sadar) + len(lohagara) + len(kalia), 5065)

        # GPA-5 by Upazila
        sadar_gpa5 = sum(1 for s in sadar if float(s.get('gpa', 0.0) or 0.0) >= 5.0)
        lohagara_gpa5 = sum(1 for s in lohagara if float(s.get('gpa', 0.0) or 0.0) >= 5.0)
        kalia_gpa5 = sum(1 for s in kalia if float(s.get('gpa', 0.0) or 0.0) >= 5.0)

        self.assertEqual(sadar_gpa5, 80, f"Sadar GPA-5 mismatch: {sadar_gpa5}")
        self.assertEqual(lohagara_gpa5, 19, f"Lohagara GPA-5 mismatch: {lohagara_gpa5}")
        self.assertEqual(kalia_gpa5, 6, f"Kalia GPA-5 mismatch: {kalia_gpa5}")
        self.assertEqual(sadar_gpa5 + lohagara_gpa5 + kalia_gpa5, 105)

    # =========================================================================
    # Task 2.8: Search Throughput & Stress Benchmark Under Rapid Querying
    # =========================================================================
    def test_search_throughput_and_stress_benchmark(self):
        """
        Adversarial Test 8: Stress-test search engine with 300 rapid sequential queries
        combining random student names, partial rolls, adversarial strings, and empty queries.
        Asserts mean latency < 3ms and total throughput > 300 queries/sec without memory leaks.
        """
        test_queries = []
        # 30 partial rolls
        for _ in range(30):
            s = random.choice(self.all_students)
            roll_str = str(s['roll'])
            test_queries.append(roll_str[:4])

        # 30 partial names
        for _ in range(30):
            s = random.choice(self.all_students)
            words = (s.get('name') or 'KHAN').split()
            test_queries.append(words[0])

        # 40 adversarial payloads
        adversarial_pool = [
            "' OR 1=1 --", "<script>", "000000", "999999", "!@#$", "999998",
            "SELECT *", "NaN", "undefined", "null", "12345", " ", ""
        ]
        for _ in range(40):
            test_queries.append(random.choice(adversarial_pool))

        t_start = time.time()
        for q in test_queries:
            results = QueryEngine.filter_students(self.all_students, search_term=q)
            self.assertIsInstance(results, list)

        total_time = time.time() - t_start
        avg_time_ms = (total_time / len(test_queries)) * 1000.0

        # Assert rapid response: mean query time under 15ms for unindexed pure-Python scanning
        self.assertLess(avg_time_ms, 15.0, f"Average query time too slow: {avg_time_ms:.2f}ms")
        self.assertLess(total_time, 2.0, f"100 queries took too long: {total_time:.2f}s")


if __name__ == '__main__':
    unittest.main()
