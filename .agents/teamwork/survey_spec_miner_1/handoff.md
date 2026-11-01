# Handoff Report: Jessore Board API Specification

**Sender**: survey_spec_miner_1 (Jessore Board API Spec Miner)  
**Recipient**: orchestrator (f13e071e-3fd2-420f-b1f5-be3a288800ea)  
**Date**: 2026-11-01  
**Handoff Type**: Hard (Task Complete)  

---

## 1. Observation

1. **College Result Sheet Endpoint**:
   - Command: `curl -sI "https://www.jessoreboard.gov.bd/resultjbh26/result_sheet.php?eiin=118437"`
   - Output: HTTP/2 200, `server: nginx`, `content-type: text/html; charset=UTF-8`, `x-powered-by: PHP/8.4.27`.
   - Verified on multiple colleges:
     - EIIN 118437: Lohagara Govt. Adarsha College (Center: LOHAGARA - 418), 580 students (Science: 85, Humanities: 375, Business Studies: 120).
     - EIIN 118527: Government Victoria College, Narail (Center: NARAIL - 321), 873 students (Science: 336, Humanities: 347, Business Studies: 190).
     - EIIN 118525: Narail Govt. Mohila College (Center: NARAIL - 320), 412 students (Science: 76, Humanities: 325, Business Studies: 11).
   - Multi-page pagination: large groups span multiple `<div class="page">` elements. Group continuation repeats `<div class="group_title">` on subsequent pages; group end count (`= {count}`) appears exclusively at the conclusion of that group on its final page.
   - Aggregate statistics line: `<div class="group_title">Statistics : </div>` followed by `<div class="group_body">` verbatim:
     `5 = 13, 4 to <5 = 63, 3.5 to <4 = 82, 3 to <3.5 = 76, 2 to <3 = 49, 1 to <2 = 2, 0 = 295,  Total = 580`
   - Unregistered EIIN error behavior: non-existent EIIN (e.g. `999999`) returns HTTP 200 with an empty `<body>` (length 1881 bytes, 0 `.page` tags).
   - Omitted EIIN error behavior: `result_sheet.php` with no parameter returns HTTP 200 with verbatim PHP stack trace:
     `Fatal error: Uncaught mysqli_sql_exception: You have an error in your SQL syntax; check the manual that corresponds to your MariaDB server version for the right syntax to use near 'order by eiin' at line 1 in /vh/g/jb/vhosts/jessoreboard.gov.bd/www/resultjbh26/result_sheet.php:64`.

2. **Individual Student Result Endpoint**:
   - Command: `curl -s -X POST -d "roll=517612&regno=" "https://www.jessoreboard.gov.bd/resultjbh26/result.php"`
   - Output: HTTP/2 200, HTML fragment containing `<div id="resutl_sheet">`, `table.table_info` (12 fields), and `table.table_result` (7 subjects with letter grades).
   - Student info fields: `Roll No` (517612), `Name` (MAHFUJA AKTER MONI), `Reg. No` (""), `Father's Name` (KAZI ROBIUL ISLAM), `Group` (SCIENCE), `Mother's Name` (REKHA BEGUM), `Session` (2024-25), `Passing Year` (2026), `Type` (REGULAR), `Institute` (Lohagara Govt. Adarsha College(118437)), `Result` (GPA=3.92), `Center` (LOHAGARA - 418).
   - Roll validation:
     - Command: `curl -s -X POST -d "roll=999999&regno=" "https://www.jessoreboard.gov.bd/resultjbh26/result.php"`
     - Output: `<div id="resutl_sheet">... 999999 is not valid roll of 2026 HSC</div>`.
   - Registration number validation:
     - When `regno=""` or omitted: succeeds immediately without requiring registration number.
     - When invalid/mismatched `regno` provided (e.g. `regno=1234567890` with valid roll `517612`): returns verbatim text:
       `Roll No. and Registration No. does not match!`.
   - Result status codes & grade sheet behavior:
     - `GPA=x.xx`: Candidate passed. Complete grade sheet returned.
     - `FAIL` (`F1`, `F2`, `Fail`): Candidate failed in 1, 2, or >=3 subjects. Grade sheet returned showing `F` in failed subjects.
     - `ABSENT`: Candidate absent. `table_info` returned, but `table.table_result` omitted.
     - `REPORTED`: Candidate expelled. `table_info` returned with `Type: IRREGULAR`, `table.table_result` omitted.

3. **Concurrency and Throughput Benchmark**:
   - 20 concurrent requests using Python `concurrent.futures.ThreadPoolExecutor(max_workers=20)` completed in 2.52 seconds.
   - All 20 returned status 200 with complete HTML payloads.
   - Zero rate limits (no HTTP 429, no HTTP 503, no CAPTCHA).

---

## 2. Logic Chain

1. **Discovery of Registration Number Independence**:
   - Observation: Querying `POST result.php` with `roll=517612&regno=` returns the complete student record including all 7 subject grades.
   - Observation: `function.js` executes `$.post("result.php", {roll:roll, regno:regno}, ...)` without checking `regno.length == 10` before submission.
   - Inference: Workers do not need to hunt for student registration cards or bypass registration barriers. Workers can scrape the full student directory by extracting rolls from `result_sheet.php` and fetching individual results with `regno=""`.

2. **Stream Grouping & Multi-Page Pagination Invariants**:
   - Observation: Page 1 of EIIN 118437 contains Science (85 students) and the first 105 Humanities students. Page 2 contains 210 Humanities students. Page 3 contains the remaining 60 Humanities students, followed by `= 375`.
   - Inference: Parsers MUST treat stream groupings as stateful across pages, aggregating students until the group changes or finishes. Sum of stream counts equals total appeared students in statistics block.

3. **Validation & Integrity Invariants**:
   - Observation: In EIIN 118437, Science (85) + Humanities (375) + Business Studies (120) = 580.
   - Observation: Statistics `5=13 + 4to<5=63 + 3.5to<4=82 + 3to<3.5=76 + 2to<3=49 + 1to<2=2 + 0=295` = 580.
   - Inference: Workers can run automated reconciliation: `len(parsed_students) == declared_counts[stream]` and `sum(stream_totals) == statistics['total']`. Any discrepancy indicates parsing truncation.

---

## 3. Caveats

1. **Marks vs. Letter Grades**:
   - The board portal states: `Reg. No. (For Marks)`. When `regno` is omitted, the board returns letter grades (`A+`, `A`, `A-`, `B`, `C`, `D`, `F`) rather than numeric marks (e.g. 85/100). Because registration numbers are withheld behind institution login credentials, numerical percentage marks cannot be obtained without candidate registration cards. However, letter grades, GPAs, and pass/fail statuses are 100% accessible.
2. **Whitespace in Letter Grades**:
   - Certain grades in `table.table_result` contain trailing spaces (e.g. `<td>A </td>`). All parser implementations must use `.strip()`.

---

## 4. Conclusion

1. The Jessore Board HSC 2026 result endpoints are fully open, unauthenticated, and highly performant.
2. Complete college-wise student rosters with academic streams (Science, Humanities, Business Studies) can be fetched via `result_sheet.php?eiin={eiin}`.
3. Complete individual student profiles (Student Name, Father, Mother, Session, Type, GPA, Subject Grades) can be fetched via `POST result.php` using `roll={roll}&regno=`.
4. The specifications, regex patterns, and Python parsers documented in `spec_report.md` are verified against live production data and ready for immediate deployment in Phase 1 ingestion pipelines.

---

## 5. Verification Method

To independently verify all findings, execute the following commands from the repository root:

1. **Verify College Sheet Parsing**:
   ```bash
   python3 -c "
   import requests
   from bs4 import BeautifulSoup
   r = requests.get('https://www.jessoreboard.gov.bd/resultjbh26/result_sheet.php?eiin=118437')
   assert r.status_code == 200
   soup = BeautifulSoup(r.text, 'html.parser')
   results = soup.find_all('div', class_='result')
   assert len(results) == 580, f'Expected 580 students, found {len(results)}'
   print('Verified college sheet: 580 students successfully parsed!')
   "
   ```

2. **Verify Individual Student Lookup Without Reg No**:
   ```bash
   python3 -c "
   import requests
   from bs4 import BeautifulSoup
   r = requests.post('https://www.jessoreboard.gov.bd/resultjbh26/result.php', data={'roll': '517612', 'regno': ''})
   assert r.status_code == 200
   soup = BeautifulSoup(r.text, 'html.parser')
   name = [tds[3].text.strip() for tr in soup.find('table', class_='table_info').find_all('tr') for tds in [tr.find_all('td')] if len(tds) >= 4 and 'Roll No' in tds[0].text][0]
   assert name == 'MAHFUJA AKTER MONI'
   subjects = len(soup.find('table', class_='table_result').find_all('tr')) - 1
   assert subjects == 7
   print(f'Verified student: {name} with {subjects} subjects!')
   "
   ```

3. **Inspect Full Spec Report**:
   Read `/media/sanglap/Movies/2026results/.agents/teamwork/survey_spec_miner_1/spec_report.md`.
