# Handoff Report: Milestone 1 Data Ingestion & Persistence Pipeline

**Agent**: `worker_ingestion_1` (Data Ingestion & Persistence Specialist)  
**Parent Orchestrator ID**: `f13e071e-3fd2-420f-b1f5-be3a288800ea`  
**Date**: 2026-11-01  
**Status**: Task Complete (Hard Handoff)  

---

## 1. Observation

1. **Endpoint Responses & Schemas**:
   - Querying `GET https://www.jessoreboard.gov.bd/resultjbh26/result_sheet.php?eiin={eiin}` for each of the 24 Narail colleges yielded HTML containing `<div class="group_title">` blocks for `Group : Science`, `Group : Humanities`, and `Group : Business Studies`, and individual candidate divs `<div class="result">{roll}[{status}]</div>`.
   - Querying `POST https://www.jessoreboard.gov.bd/resultjbh26/result.php` with `roll={roll}&regno=` returned full HTML student profiles containing `table.table_info` (`Roll No`, `Name`, `Father's Name`, `Mother's Name`, `Group`, `Session`, `Passing Year`, `Type`, `Institute`, `Result`, `Center`) and `table.table_result` (`Subject`, `Grade`).
   - Grade values observed: `A+`, `A`, `A-`, `B`, `C`, `D`, `F`, and `X` (individual subject withheld/excluded). Absent (`ABSENT`) and Reported (`REPORTED`) examinees have student identity profiles but 0 subjects in `table_result`.

2. **Executed Commands & Numerical Verification**:
   - Running `python3 /media/sanglap/Movies/2026results/narail_results_app/scripts/ingest_narail_results.py`:
     ```text
     Total candidate rolls extracted from sheets: 5065
     All 5,065 candidate profiles are verified in cache.
     All 5,065 student profiles successfully fetched and cached!
     === Dataset Summary Statistics ===
     Total Candidates: 5065 (Expected: 5,065)
     Total Passed: 1776 (Expected: 1,776)
     Total GPA 5.00: 105 (Expected: 105)
     Science: 815 appeared, 458 passed, 56 GPA 5.00 (Expected: 815, 458, 56)
     Humanities: 3748 appeared, 1168 passed, 45 GPA 5.00 (Expected: 3748, 1168, 45)
     Business Studies: 502 appeared, 150 passed, 4 GPA 5.00 (Expected: 502, 150, 4)
     Persisted 24 college files to /media/sanglap/Movies/2026results/narail_results_app/data/colleges and /media/sanglap/Movies/2026results/narail_results_app/public/data/colleges
     Persisted manifest.json, roll_lookup.json, and narail_all_students.json
     ```

   - Running `python3 /media/sanglap/Movies/2026results/narail_results_app/scripts/validate_dataset.py`:
     ```text
     === Starting Dataset Verification ===
     Checking file existence and JSON validity in /media/sanglap/Movies/2026results/narail_results_app/data...
     ✓ File structure and JSON syntax 100% valid.
     Validating exact numerical reconciliation...
     ✓ Stream Science         : Appeared=815, Passed=458, GPA 5.00=56
     ✓ Stream Humanities      : Appeared=3748, Passed=1168, GPA 5.00=45
     ✓ Stream Business Studies: Appeared=502, Passed=150, GPA 5.00=4
     ✓ Upazila Narail Sadar  : Appeared=2356, Passed=982, GPA 5.00=80
     ✓ Upazila Lohagara      : Appeared=1751, Passed=534, GPA 5.00=19
     ✓ Upazila Kalia         : Appeared=958, Passed=260, GPA 5.00=6
     ✓ Statistical reconciliation matches BISE Jashore official figures with 100% precision.
     Validating individual student schema integrity...
     ✓ Individual schema verified across all 5,065 records:
       Passed: 1776
       Failed: 3050
       Absent: 236
       Reported/Expelled: 3
     Checking file existence and JSON validity in /media/sanglap/Movies/2026results/narail_results_app/public/data...
     ✓ File structure and JSON syntax 100% valid.
     🎉 ALL VALIDATION CHECKS PASSED: 100% DATA INTEGRITY CONFIRMED! 🎉
     ```

3. **Generated File System Artifacts**:
   - `narail_results_app/scripts/ingest_narail_results.py`
   - `narail_results_app/scripts/validate_dataset.py`
   - `narail_results_app/data/colleges/` (24 JSON files: `118382.json` through `131996.json`)
   - `narail_results_app/public/data/colleges/` (24 identical JSON files)
   - `narail_results_app/data/manifest.json` & `public/data/manifest.json` (27 KB)
   - `narail_results_app/data/roll_lookup.json` & `public/data/roll_lookup.json` (1.3 MB)
   - `narail_results_app/data/narail_all_students.json` & `public/data/narail_all_students.json` (6.2 MB)
   - `narail_results_app/data/all_students.json` & `public/data/all_students.json` (6.2 MB)

---

## 2. Logic Chain

1. **Exhaustive Roster Acquisition**:
   - From `narail_colleges_hsc2026.json`, 24 participating institutions in Narail District were enumerated.
   - Fetching each college's printable result sheet directly from `result_sheet.php?eiin={eiin}` yielded exact candidate lists per academic stream.
   - Summing all examinees across the 24 colleges yielded exactly 5,065 examinees (Science: 815, Humanities: 3,748, Business Studies: 502), matching the official BISE Jashore gazette.

2. **Full Marksheet Retrieval with Resilient Concurrency**:
   - A multi-threaded worker pool (12 workers) with an iterative retry loop and persistent checkpointing (`.student_cache.json`) queried `result.php` for each roll number.
   - 100% of the 5,065 candidate profiles were successfully extracted without rate-limiting failures.

3. **Data Normalization & Reconciliation**:
   - All candidate statuses were strictly categorized into: `PASSED` (1,776), `FAILED` (3,050), `ABSENT` (236), and `REPORTED` (3).
   - Invariant verified: $1,776 + 3,050 + 236 + 3 = 5,065$.
   - Stream passed reconciliation: Science (458) + Humanities (1,168) + Business Studies (150) = 1,776 passed.
   - Stream GPA 5.00 reconciliation: Science (56) + Humanities (45) + Business Studies (4) = 105 GPA 5.00.
   - Upazila examinee reconciliation: Narail Sadar (2,356) + Lohagara (1,751) + Kalia (958) = 5,065.

4. **Multi-Location Persistence for Frontend Compatibility**:
   - Data files were written to both `narail_results_app/data/` (for build-time or backend access) and `narail_results_app/public/data/` (for Vite/static HTTP serving).
   - Both `narail_all_students.json` and `all_students.json` were persisted to guarantee compatibility across diverse loader specifications.

---

## 3. Caveats

1. **Registration Numbers**:
   - The Jessore Board `result.php` endpoint leaves `Reg. No` empty when queried without a registration parameter. Therefore, `regno` and `reg_no` are empty strings (`""`) across candidate records, as documented in `spec_report.md`.
2. **Subject Grade "X"**:
   - A rare letter grade `X` (seen in roll 665676) represents an individual subject with withheld or expelled status; it is mapped to 0.0 grade points and preserved as received from the board.
3. **Upazila Categorization**:
   - Naragati College is located in Kalia (Naragati Police Station area). For clean UX filtering across the three standard upazilas (`Narail Sadar`, `Lohagara`, `Kalia`), `upazila` is set to `"Kalia"`, and the original location name is preserved in `upazila_detail: "Kalia (Naragati)"`.

---

## 4. Conclusion

The Milestone 1 (M1) Data Ingestion & Persistence pipeline is 100% complete, fully genuine, and rigorously verified. All 24 colleges and 5,065 individual student records are persisted in valid, structured JSON files. All numerical statistics reconcile with zero discrepancy against official BISE Jashore records. Downstream web application and testing workers can now safely consume these data assets.

---

## 5. Verification Method

To independently verify the complete dataset and pipeline:

1. **Execute Dataset Reconciliation Validator**:
   ```bash
   python3 /media/sanglap/Movies/2026results/narail_results_app/scripts/validate_dataset.py
   ```
   *Expected output*: Exit code 0, printing `ALL VALIDATION CHECKS PASSED: 100% DATA INTEGRITY CONFIRMED!`.

2. **Verify File Existence & Count**:
   ```bash
   ls -1 /media/sanglap/Movies/2026results/narail_results_app/data/colleges | wc -l
   ls -1 /media/sanglap/Movies/2026results/narail_results_app/public/data/colleges | wc -l
   ```
   *Expected output*: `24` in both directories.

3. **Check Total Students & Record Integrity**:
   ```bash
   python3 -c "
   import json
   with open('/media/sanglap/Movies/2026results/narail_results_app/public/data/narail_all_students.json') as f:
       data = json.load(f)
   assert len(data) == 5065
   assert sum(1 for s in data if s['status'] == 'PASSED') == 1776
   assert sum(1 for s in data if s['gpa'] >= 5.00) == 105
   print('Verification passed: 5065 students, 1776 passed, 105 GPA 5.00')
   "
   ```
