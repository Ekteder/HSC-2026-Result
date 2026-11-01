# Jessore Board HSC 2026 API & Response Specification Report

**Document Version**: 1.0.0  
**Date**: 2026-11-01  
**Author**: survey_spec_miner_1 (Jessore Board API Spec Miner)  
**Target Board**: Board of Intermediate and Secondary Education, Jashore (Jessore Board)  
**Exam**: Higher Secondary Certificate (HSC) Examination 2026  
**Publication Date**: 31 October, 2026  

---

## 1. Executive Summary

This report establishes the complete, authoritative technical specification for interacting with and extracting data from the Jessore Board HSC 2026 examination result endpoints:
1. **College-Wise Result Sheet Endpoint**: `GET https://www.jessoreboard.gov.bd/resultjbh26/result_sheet.php?eiin={eiin}`
2. **Individual Student Result Endpoint**: `POST https://www.jessoreboard.gov.bd/resultjbh26/result.php` with `roll={roll}&regno={regno}`

All findings are backed by empirical testing on live board servers running PHP 8.4.27 on Nginx and MariaDB.

---

## 2. Features Discovered

| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|----------|---------|-------------|--------|---------|----------------|----------------|
| 1 | College Result | Result Sheet by EIIN | Retrieves printable multi-page HTML result sheet containing college metadata, center, stream-wise roll numbers with status/GPA, and summary stats | Query param: `eiin` (numeric, e.g. `118437`, `118527`) | HTML document (`text/html`) with `.page` divs, stream groupings, and `.result` tags | If invalid/non-existent EIIN: HTTP 200 with empty `<body>`. If empty/missing: PHP MySQL syntax error. | Live HTTP GET probe |
| 2 | College Result | Multi-page Stream Continuation | Academic streams with large student cohorts (e.g. Humanities) paginate across multiple `.page` divs; group end count (`= {count}`) appears only on the final page of that group | Query param: `eiin` | Sequential `<div class="data">` blocks with `.group_title` and `.group_body` | N/A (valid multi-page rendering) | Live probe of EIIN 118437 & 118527 |
| 3 | College Result | Stream Counts & Totals | Each stream declares its total student count at the end of its group body in format `= {count}` | Query param: `eiin` | Trailing text `= {count}` in final `.group_body` for that stream | Omitted on intermediate continuation pages | DOM traversal & regex testing |
| 4 | College Result | Aggregate Statistics Block | Summary line providing GPA distribution (`5`, `4 to <5`, `3.5 to <4`, `3 to <3.5`, `2 to <3`, `1 to <2`, `0`, `Total`) | Query param: `eiin` | `<div class="group_title">Statistics : </div>` followed by `<div class="group_body">` | Always at bottom of last page | Live parsing of Narail colleges |
| 5 | Individual Result | Individual Student Lookup | Retrieves complete student record (Name, Parents, College, Stream, Session, Type, GPA, Subject Grades) | Form POST: `roll` (6 digits) & optional `regno` | HTML fragment with `#resutl_sheet`, `.table_info`, and `.table_result` | If roll invalid: returns `{roll} is not valid roll of 2026 HSC`. If regno mismatch: returns `Roll No. and Registration No. does not match!`. | Live HTTP POST probe |
| 6 | Individual Result | Regno-Optional Lookup | Student result and complete grade sheet are accessible WITHOUT registration number (empty `regno=""` or omitted `regno`) | Form POST: `roll={roll}&regno=` | Complete HTML table info + grade sheet | Matches without requiring registration card number | Live parameter elimination test |
| 7 | Individual Result | Mismatched Regno Detection | If non-empty `regno` is submitted that does not match the roll, board rejects the query | Form POST: `roll={roll}&regno={mismatched}` | Text: `Roll No. and Registration No. does not match!` | Fails with explicit mismatch warning | Live test with incorrect regno |
| 8 | Individual Result | Subject-wise Grade Mapping | Table of subjects and letter grades (`A+`, `A`, `A-`, `B`, `C`, `D`, `F`) achieved by candidate | Form POST: `roll` | `<table class="table_result">` with `<th>Subject</th><th>Grade</th>` | Empty / absent for `ABSENT` and `REPORTED` students | Live inspection across streams |
| 9 | Individual Result | Special Status Handling | Delineates candidate statuses: Passed (`GPA=x.xx`), Failed (`FAIL`), Absent (`ABSENT`), Expelled/Reported (`REPORTED`) | Form POST: `roll` | Status in `.table_info` `Result` cell | No grade sheet table generated for `ABSENT` or `REPORTED` | Live probe of rolls across status codes |
| 10 | Portal Navigation | Client-side Lookup Portal | Landing page offering roll/reg input with auto-trigger on 6-digit roll | GET `/resultjbh26/` | HTML page loading `function.js` | JavaScript length checks on roll (6) and regno (10) | Live inspection of portal source |
| 11 | Portal Navigation | Institute Sheet Prompt | Redirector prompt for institute EIIN | GET `/resultjbh26/insresult.php` | JavaScript `prompt()` redirecting to `result_sheet.php?eiin={eiin}` | Prompts browser user | Live curl to `insresult.php` |

---

## 3. Edge Cases

| # | Feature | Input | Observed Behavior |
|---|---------|-------|-------------------|
| 1 | College Result Sheet | Non-existent EIIN (`999999` or `118320`) | Returns HTTP 200 with empty `<body oncontextmenu="return false;" onload="Javascript: window.print();"></body>` (no `.page` divs, length 1881 bytes). |
| 2 | College Result Sheet | Missing EIIN (`result_sheet.php`) | Returns HTTP 200 with PHP Fatal Error: `mysqli_sql_exception: You have an error in your SQL syntax ... near 'order by eiin' at line 1 in .../result_sheet.php:64`. |
| 3 | College Result Sheet | Non-numeric EIIN (`eiin=abc`) | Returns HTTP 200 with empty `<body>` (treated as 0 or unmatched string). |
| 4 | College Result Sheet | HTTP POST to `result_sheet.php` | Returns HTTP 200 with PHP SQL exception; endpoint only accepts query parameter via `GET`. |
| 5 | Individual Result | HTTP GET to `result.php?roll=517612` | Returns HTTP 200 with body `is not valid roll of 2026 HSC` because `result.php` reads strictly `$_POST['roll']`. |
| 6 | Individual Result | Non-existent 6-digit roll (`999999`) | Returns HTTP 200 with `#resutl_sheet` containing `999999 is not valid roll of 2026 HSC`. |
| 7 | Individual Result | Empty / Missing roll (`roll=""` or `{}`) | Returns HTTP 200 with `#resutl_sheet` containing `is not valid roll of 2026 HSC`. |
| 8 | Individual Result | Valid roll (`517612`) with non-matching `regno` | Returns HTTP 200 with text `Roll No. and Registration No. does not match!` (unclosed HTML tag). |
| 9 | Individual Result | Valid roll (`517612`) with empty `regno=""` | Returns HTTP 200 with complete student info and 7 subject grades; `Reg. No` field is empty string. |
| 10 | Individual Result | Absent candidate (`517615`) | Returns HTTP 200 with `Result: ABSENT`. No `Grade Sheet` (`table.table_result`) is generated in DOM. |
| 11 | Individual Result | Expelled / Reported candidate (`665968`) | Returns HTTP 200 with `Result: REPORTED`, `Type: IRREGULAR`. No `Grade Sheet` is generated. |
| 12 | Individual Result | Failed candidate with 1 fail (`517614`) | In sheet: `517614[F1  ]`. In individual: `Result: FAIL`. Grade sheet lists 7 subjects; 1 subject has grade `F`. |
| 13 | Individual Result | Failed candidate with 2 fails (`517613`) | In sheet: `517613[F2  ]`. In individual: `Result: FAIL`. Grade sheet lists 7 subjects; 2 subjects have grade `F`. |
| 14 | Individual Result | Failed candidate with >=3 fails (`517619`) | In sheet: `517619[Fail]`. In individual: `Result: FAIL`. Grade sheet lists 7 subjects; 4 subjects have grade `F`. |
| 15 | Individual Result | Trailing whitespace in letter grades | Grades like `<td>A </td>` contain trailing space; requires string trimming (`.strip()`) to avoid matching bugs. |

---

## 4. College-Wise Result Sheet Specification

### 4.1 Request Details
- **URL**: `https://www.jessoreboard.gov.bd/resultjbh26/result_sheet.php`
- **Method**: `GET`
- **Query Parameter**: `eiin` (6-digit institutional identifier, e.g. `118437`)
- **Headers Required**: None. Standard HTTP/1.1 or HTTP/2 client headers (e.g. `User-Agent: curl/8.5.0` or `requests/2.x`).
- **Cookies / Auth**: None. Publicly accessible.

### 4.2 Response Details
- **HTTP Status**: `200 OK`
- **Content-Type**: `text/html; charset=UTF-8`
- **Server**: `nginx`, PHP `8.4.27`
- **Structure**: Printable document containing one or more `<div class="page">` elements.

```html
<div class="page">
    <div class="page_body">
        <div class="head">
            <div class="logo"><img src="logo.png" /></div>
            <div class="title">
                <div class="title1">Board of Intermediate and Secondary Education, Jashore</div>
                <div class="title2">Higher Secondary Certificate Examination, 2026</div>
                <div class="title3">Result Sheet</div>
            </div>
            <div class="page_no">Page 1</div>
            <div style="clear: both;"></div>
        </div>
        <div class="sub_title">
            Center: LOHAGARA - 418<br/>
            Institute: Lohagara Govt. Adarsha College (118437)
        </div>
        <div class="data">
            <div class="group_title">Group : Science</div>
            <div class="group_body">
                <div class="result">517612[3.92]</div>
                <div class="result">517613[F2  ]</div>
                ...
                 = 85
            </div>
            <div class="group_title">Group : Humanities</div>
            <div class="group_body">
                <div class="result">665746[3.58]</div>
                ...
            </div>
        </div>
        <div class="footer">
            <table>
                <tr>
                    <td>Date of Publication of Results: 31 October, 2026</td>
                    <td>
                        <img src="hossenali.png"><br>
                        Professor S. M. Hossain Ali<br>
                        Controller of Examinations
                    </td>
                </tr>
            </table>
        </div>
    </div>
</div>
```

### 4.3 Key Components and Regex Extraction

#### A. College Name, EIIN, and Center
Extracted from `<div class="sub_title">`:
- **Institute & EIIN Regex**: `r'Institute:\s*(.*?)\s*\((\d+)\)'`
  - Group 1: Institute Name (e.g. `Lohagara Govt. Adarsha College`)
  - Group 2: EIIN (e.g. `118437`)
- **Center Name & Code Regex**: `r'Center:\s*([A-Za-z\s]+?)\s*-\s*(\d+)'`
  - Group 1: Center Name (e.g. `LOHAGARA`)
  - Group 2: Center Code (e.g. `418`)

#### B. Academic Streams & Student Rolls
Within `<div class="data">`:
- Streams are signaled by `<div class="group_title">`:
  - `Group : Science`
  - `Group : Humanities`
  - `Group : Business Studies`
  - `Statistics : `
- Immediately followed by `<div class="group_body">`.
- **Note on Multi-page continuation**: When a stream spans multiple pages, `<div class="group_title">` is repeated on each page. The parser MUST append students to the same group list across pages.
- **Group count indicator**: At the end of the concluding page for a group, the text contains `= {count}` (e.g. `= 85`, `= 375`, `= 120`). Intermediate pages do NOT have this count.
- **Student result item**: `<div class="result">{roll}[{status}]</div>`
  - **Item Regex**: `r'^(\d{6})\s*\[(.*?)\]$'`
  - Group 1: 6-digit Roll Number
  - Group 2: Status code / GPA string (4 chars, space-padded for F1/F2)

#### C. Result Status Encoding Matrix
| Sheet Code | Meaning | Equivalent Individual Status | GPA Value | Notes |
|------------|---------|------------------------------|-----------|-------|
| `5.00` | Passed with highest distinction | `PASSED` (`GPA=5.00`) | 5.00 | A+ in all required counted subjects |
| `[x.xx]` | Passed with GPA `x.xx` | `PASSED` (`GPA=x.xx`) | Float (`x.xx`) | e.g. `3.92`, `2.75`, `4.58` |
| `F1  ` | Failed in 1 subject | `FAIL` | 0.00 / None | Space-padded: `F1  `. 1 subject grade is `F`. |
| `F2  ` | Failed in 2 subjects | `FAIL` | 0.00 / None | Space-padded: `F2  `. 2 subject grades are `F`. |
| `Fail` | Failed in 3 or more subjects | `FAIL` | 0.00 / None | 3+ subject grades are `F`. |
| `Abst` | Absent from examination | `ABSENT` | 0.00 / None | No subject grades recorded. |
| `Expl` | Expelled / Reported | `REPORTED` | 0.00 / None | No subject grades recorded. |

#### D. Summary Statistics Parsing
Extracted from `<div class="group_body">` following `<div class="group_title">Statistics : </div>`:
- **Format String**: `5 = 13, 4 to <5 = 63, 3.5 to <4 = 82, 3 to <3.5 = 76, 2 to <3 = 49, 1 to <2 = 2, 0 = 295,  Total = 580`
- **Regex**:
  `r'5\s*=\s*(\d+),\s*4 to <5\s*=\s*(\d+),\s*3\.5 to <4\s*=\s*(\d+),\s*3 to <3\.5\s*=\s*(\d+),\s*2 to <3\s*=\s*(\d+),\s*1 to <2\s*=\s*(\d+),\s*0\s*=\s*(\d+),\s*Total\s*=\s*(\d+)'`
- **Mathematical Invariant**:
  $$\text{Passed} = (\text{gpa5}) + (\text{gpa4}) + (\text{gpa35}) + (\text{gpa3}) + (\text{gpa2}) + (\text{gpa1})$$
  $$\text{Failed} = \text{gpa0}$$
  $$\text{Total} = \text{Passed} + \text{Failed} = \sum \text{Students in all streams}$$

---

## 5. Individual Student Result Specification

### 5.1 Request Details
- **URL**: `https://www.jessoreboard.gov.bd/resultjbh26/result.php`
- **Method**: `POST`
- **Content-Type**: `application/x-www-form-urlencoded`
- **Payload**:
  - `roll`: 6-digit roll number (e.g. `517612`)
  - `regno`: Optional. Send empty string `regno=` to query result and full grade sheet without registration card.
- **Curl Example**:
  ```bash
  curl -s -X POST -d "roll=517612&regno=" "https://www.jessoreboard.gov.bd/resultjbh26/result.php"
  ```
- **Headers / Auth**: No cookies, sessions, CSRF tokens, or User-Agent headers required.

### 5.2 Response Details
- **HTTP Status**: `200 OK`
- **Content-Type**: `text/html; charset=UTF-8`
- **DOM Container**: `<div id="resutl_sheet">` (note the literal upstream typo `resutl_sheet`).

### 5.3 Extracted Student Metadata (`table.table_info`)
Each row `<tr>` contains 4 `<td>` tags, formatted as `[Label 1, Value 1, Label 2, Value 2]`:

| Row | Label 1 | Target Field | Label 2 | Target Field |
|-----|---------|--------------|---------|--------------|
| 1 | `Roll No` | `roll` (e.g. `517612`) | `Name` | `name` (e.g. `MAHFUJA AKTER MONI`) |
| 2 | `Reg. No` | `reg_no` (empty string if not provided) | `Father's Name` | `father_name` (e.g. `KAZI ROBIUL ISLAM`) |
| 3 | `Group` | `stream` / `group` (`SCIENCE`, `HUMANITIES`, `BUSINESS STUDIES`) | `Mother's Name` | `mother_name` (e.g. `REKHA BEGUM`) |
| 4 | `Session` | `session` (e.g. `2024-25`, `2023-24`) | `Passing Year` | `passing_year` (`2026`) |
| 5 | `Type` | `candidate_type` (`REGULAR`, `IRREGULAR`) | `Institute` | `institute` (e.g. `Lohagara Govt. Adarsha College(118437)`) |
| 6 | `Result` | `result_raw` (`GPA=3.92`, `FAIL`, `ABSENT`, `REPORTED`) | `Center` | `center` (e.g. `LOHAGARA - 418`) |

### 5.4 Subject Grade Sheet (`table.table_result`)
Table exists for all students with examination submissions (omitted only for `ABSENT` and `REPORTED`).
- Header: `<th>Subject</th><th style="width: 100px;">Grade</th>`
- Rows: `<tr><td class="subname">{Subject Name}</td><td>{Letter Grade}</td></tr>`

#### Observed Subject Catalog Across Streams
| Stream | Compulsory Core Subjects | Stream Elective / 4th Subjects Observed |
|--------|--------------------------|-----------------------------------------|
| **Science** | Bangla, English, Information & Communication Technology | Physics, Chemistry, Biology, Higher Mathematics, Geography, Agriculture Studies |
| **Humanities** | Bangla, English, Information & Communication Technology | Civics & Good Govern, Economics, Geography, History, Islamic History & Culture, Logic, Social Work, Sociology, Home Science, Agriculture Studies |
| **Business Studies** | Bangla, English, Information & Communication Technology | Accounting, Business Organization & Management, Production Management & Marketing, Economics, Finance, Banking & Insurance, Home Science, Agriculture Studies |

#### Letter Grade Scale & Invariants
- `A+` (GPA 5.0)
- `A` (GPA 4.0) — **Warning**: Response HTML frequently contains `<td>A </td>` (space-padded). MUST call `.strip()`.
- `A-` (GPA 3.5)
- `B` (GPA 3.0)
- `C` (GPA 2.0)
- `D` (GPA 1.0)
- `F` (GPA 0.0) — Indicates failed subject

---

## 6. Failure Modes & Error Behavior Matrix

| Error Case | Trigger Condition | Exact Response Body Pattern | Status Code |
|------------|-------------------|-----------------------------|-------------|
| **Invalid Roll** | Roll not found in 2026 HSC database (e.g. `999999`, `000000`, `abc`) | `<div id="resutl_sheet">... {roll} is not valid roll of 2026 HSC</div>` | `200 OK` |
| **Empty Roll** | Roll is empty string or omitted in POST | `<div id="resutl_sheet">... is not valid roll of 2026 HSC</div>` | `200 OK` |
| **GET on result.php** | Request made via HTTP GET instead of POST | `<div id="resutl_sheet">... is not valid roll of 2026 HSC</div>` | `200 OK` |
| **Regno Mismatch** | Valid roll supplied, but non-empty `regno` does not match record | `Roll No. and Registration No. does not match!` | `200 OK` |
| **Non-existent EIIN** | EIIN not participating in HSC 2026 (e.g. `999999`, `118320`) | `<body ...>\n            </body>` (no `.page` tags, len ~1881) | `200 OK` |
| **Missing EIIN** | `result_sheet.php` called without `?eiin=` or with empty value | `Fatal error: Uncaught mysqli_sql_exception: You have an error in your SQL syntax` | `200 OK` |

---

## 7. Performance, Concurrency & Rate Limits

1. **Server Architecture**:
   - Web Server: Nginx on Linux
   - Application Runtime: PHP 8.4.27
   - Database: MariaDB / MySQL
2. **Concurrency Benchmark**:
   - Tested concurrency levels: 1, 5, 10, and 20 parallel threads.
   - 20 concurrent requests completed in **2.52 seconds** (aggregate throughput: ~8 requests/second).
   - Zero HTTP 429 (Too Many Requests), zero HTTP 503 (Service Unavailable), and no CAPTCHA challenges were triggered.
3. **Recommended Client Ingestion Settings**:
   - **Worker Pool**: 8 to 12 concurrent workers.
   - **Request Timeout**: 12 seconds per request.
   - **Retry Policy**: Maximum 3 retries with exponential backoff (e.g. 1s, 2s, 4s).
   - **Connection Keep-Alive**: Reuse `requests.Session()` / `http.Agent` with `keep-alive` enabled to minimize TLS handshake overhead.

---

## 8. Reference Parsing Implementation (Python)

```python
"""
Jessore Board HSC 2026 Parser Module
Authoritative parsers for result_sheet.php and result.php
"""
import re
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup

def parse_college_result_sheet(html: str) -> Optional[Dict[str, Any]]:
    """
    Parses full HTML from https://www.jessoreboard.gov.bd/resultjbh26/result_sheet.php?eiin={eiin}
    Returns structured college result with student rolls categorized by stream,
    declared group totals, and aggregate statistics.
    """
    soup = BeautifulSoup(html, 'html.parser')
    pages = soup.find_all('div', class_='page')
    if not pages:
        return None  # College not found or inactive in HSC 2026

    # 1. Parse Institute & Center metadata
    sub_title = soup.find('div', class_='sub_title')
    sub_text = sub_title.text.strip() if sub_title else ''
    
    mc = re.search(r'Center:\s*([A-Za-z\s]+?)\s*-\s*(\d+)', sub_text)
    mi = re.search(r'Institute:\s*(.*?)\s*\((\d+)\)', sub_text)
    
    center_name = mc.group(1).strip() if mc else ''
    center_code = mc.group(2).strip() if mc else ''
    institute_name = mi.group(1).strip() if mi else ''
    eiin = mi.group(2).strip() if mi else ''

    streams = {
        'Science': [],
        'Humanities': [],
        'Business Studies': []
    }
    declared_counts = {}
    stats = None

    # 2. Iterate through all pages and data sections
    for page in pages:
        data = page.find('div', class_='data')
        if not data:
            continue

        current_stream = None
        for child in data.find_all('div', recursive=False):
            classes = child.get('class', [])
            if 'group_title' in classes:
                t = child.text.strip()
                if 'Science' in t: current_stream = 'Science'
                elif 'Humanities' in t: current_stream = 'Humanities'
                elif 'Business' in t: current_stream = 'Business Studies'
                elif 'Statistics' in t: current_stream = 'Statistics'
                else: current_stream = None
            elif 'group_body' in classes:
                if current_stream in streams:
                    for res in child.find_all('div', class_='result'):
                        m = re.match(r'^(\d{6})\s*\[(.*?)\]$', res.text.strip())
                        if m:
                            roll = m.group(1)
                            raw_status = m.group(2).strip()
                            try:
                                gpa = float(raw_status)
                                status = 'PASSED'
                            except ValueError:
                                gpa = 0.0
                                status = raw_status  # F1, F2, Fail, Abst, Expl
                            streams[current_stream].append({
                                'roll': roll,
                                'raw_status': raw_status,
                                'status': status,
                                'gpa': gpa
                            })
                    # Check for trailing count declaration (e.g. "= 85")
                    m_cnt = re.search(r'=\s*(\d+)\s*$', child.text)
                    if m_cnt:
                        declared_counts[current_stream] = int(m_cnt.group(1))

                elif current_stream == 'Statistics':
                    m_stat = re.search(
                        r'5\s*=\s*(\d+),\s*4 to <5\s*=\s*(\d+),\s*3\.5 to <4\s*=\s*(\d+),\s*'
                        r'3 to <3\.5\s*=\s*(\d+),\s*2 to <3\s*=\s*(\d+),\s*1 to <2\s*=\s*(\d+),\s*'
                        r'0\s*=\s*(\d+),\s*Total\s*=\s*(\d+)', child.text
                    )
                    if m_stat:
                        g5, g4, g35, g3, g2, g1, g0, tot = map(int, m_stat.groups())
                        stats = {
                            'gpa_5': g5, 'gpa_4_to_5': g4, 'gpa_35_to_4': g35,
                            'gpa_3_to_35': g3, 'gpa_2_to_3': g2, 'gpa_1_to_2': g1,
                            'gpa_0': g0, 'total': tot,
                            'passed': g5 + g4 + g35 + g3 + g2 + g1,
                            'failed': g0
                        }

    return {
        'eiin': eiin,
        'institute_name': institute_name,
        'center_name': center_name,
        'center_code': center_code,
        'streams': streams,
        'declared_counts': declared_counts,
        'statistics': stats
    }


def parse_individual_student_result(html: str) -> Dict[str, Any]:
    """
    Parses HTML response from POST https://www.jessoreboard.gov.bd/resultjbh26/result.php
    Returns structured student result with profile information and subject grade list.
    """
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text()

    if 'is not valid roll of 2026 HSC' in text:
        return {'success': False, 'error': 'INVALID_ROLL'}
    if 'Roll No. and Registration No. does not match' in text:
        return {'success': False, 'error': 'REGNO_MISMATCH'}

    info_table = soup.find('table', class_='table_info')
    if not info_table:
        return {'success': False, 'error': 'NO_INFO_TABLE'}

    # 1. Parse student profile info table
    info = {}
    for tr in info_table.find_all('tr'):
        tds = tr.find_all('td')
        for i in range(0, len(tds), 2):
            if i + 1 < len(tds):
                label = tds[i].text.strip().rstrip(':')
                val = tds[i+1].text.strip()
                info[label] = val

    # 2. Parse subject grades
    grade_table = soup.find('table', class_='table_result')
    subjects = []
    if grade_table:
        for tr in grade_table.find_all('tr'):
            tds = tr.find_all('td')
            if len(tds) == 2:
                subjects.append({
                    'subject': tds[0].text.strip(),
                    'grade': tds[1].text.strip()  # .strip() is vital for whitespace
                })

    res_str = info.get('Result', '')
    gpa = None
    status = res_str
    if res_str.startswith('GPA='):
        try:
            gpa = float(res_str.split('GPA=')[1].strip())
            status = 'PASSED'
        except ValueError:
            pass

    return {
        'success': True,
        'roll': info.get('Roll No', ''),
        'name': info.get('Name', ''),
        'reg_no': info.get('Reg. No', '') or None,
        'father_name': info.get("Father's Name", ''),
        'mother_name': info.get("Mother's Name", ''),
        'group': info.get('Group', ''),
        'session': info.get('Session', ''),
        'passing_year': info.get('Passing Year', '2026'),
        'candidate_type': info.get('Type', ''),
        'institute': info.get('Institute', ''),
        'center': info.get('Center', ''),
        'result_raw': res_str,
        'status': status,
        'gpa': gpa,
        'subjects': subjects
    }
```

---

## 9. Standard College-Wise JSON Schema

For Phase 1 Workers persisting parsed records, the following standard schema matches all requirements:

```json
{
  "eiin": "118437",
  "institute_name": "Lohagara Govt. Adarsha College",
  "district": "Narail",
  "center_name": "LOHAGARA",
  "center_code": "418",
  "statistics": {
    "total_students": 580,
    "passed": 285,
    "failed": 295,
    "pass_rate_percent": 49.14,
    "gpa_5_count": 13,
    "gpa_distribution": {
      "gpa_5": 13,
      "gpa_4_to_5": 63,
      "gpa_35_to_4": 82,
      "gpa_3_to_35": 76,
      "gpa_2_to_3": 49,
      "gpa_1_to_2": 2,
      "gpa_0": 295
    }
  },
  "stream_summary": {
    "Science": { "total": 85 },
    "Humanities": { "total": 375 },
    "Business Studies": { "total": 120 }
  },
  "students": [
    {
      "roll": "517612",
      "name": "MAHFUJA AKTER MONI",
      "reg_no": null,
      "father_name": "KAZI ROBIUL ISLAM",
      "mother_name": "REKHA BEGUM",
      "stream": "Science",
      "session": "2024-25",
      "passing_year": "2026",
      "candidate_type": "REGULAR",
      "result_status": "PASSED",
      "gpa": 3.92,
      "subjects": [
        { "subject": "Bangla", "grade": "A" },
        { "subject": "English", "grade": "A-" },
        { "subject": "Physics", "grade": "A-" },
        { "subject": "Chemistry", "grade": "A-" },
        { "subject": "Biology", "grade": "A" },
        { "subject": "Information & Communication Technology", "grade": "A" },
        { "subject": "Higher Mathematics", "grade": "B" }
      ]
    }
  ]
}
```
