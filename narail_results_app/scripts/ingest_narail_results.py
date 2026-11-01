#!/usr/bin/env python3
"""
High-Throughput Parallel Ingestion Pipeline for HSC 2026 Narail District Results.
Fetches college result sheets and individual student marksheets from BISE Jashore.
Generates validated, structured JSON datasets for all 24 colleges and 5,065 students.
"""

import os
import sys
import re
import json
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("ingest_narail")

# Directories
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(APP_DIR, "data")
PUBLIC_DATA_DIR = os.path.join(APP_DIR, "public", "data")
COLLEGES_DATA_DIR = os.path.join(DATA_DIR, "colleges")
PUBLIC_COLLEGES_DATA_DIR = os.path.join(PUBLIC_DATA_DIR, "colleges")
CACHE_FILE = os.path.join(DATA_DIR, ".student_cache.json")

SOURCE_COLLEGES_PATH = "/media/sanglap/Movies/2026results/.agents/teamwork/survey_explorer_2/narail_colleges_hsc2026.json"

# Endpoints
COLLEGE_SHEET_URL = "https://www.jessoreboard.gov.bd/resultjbh26/result_sheet.php?eiin={eiin}"
INDIVIDUAL_RESULT_URL = "https://www.jessoreboard.gov.bd/resultjbh26/result.php"

# Subject Code Catalog
SUBJECT_CODE_MAP = {
    "Bangla": "101",
    "English": "107",
    "Information & Communication Technology": "275",
    "Physics": "174",
    "Chemistry": "176",
    "Biology": "178",
    "Higher Mathematics": "265",
    "Civics & Good Govern": "269",
    "Economics": "109",
    "History": "304",
    "Islamic History & Culture": "267",
    "Logic": "121",
    "Social Work": "271",
    "Sociology": "117",
    "Home Science": "273",
    "Agriculture Studies": "239",
    "Geography": "125",
    "Accounting": "253",
    "Business Organization & Management": "277",
    "Production Management & Marketing": "286",
    "Finance, Banking & Insurance": "292",
}

GRADE_POINT_MAP = {
    "A+": 5.0,
    "A": 4.0,
    "A-": 3.5,
    "B": 3.0,
    "C": 2.0,
    "D": 1.0,
    "F": 0.0,
}


def create_resilient_session(pool_size: int = 32) -> requests.Session:
    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(
        pool_connections=pool_size,
        pool_maxsize=pool_size,
        max_retries=retries,
    )
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) NarailHSCResultIngestion/1.0"
    })
    return session


def load_cached_students() -> Dict[str, Dict[str, Any]]:
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cached = json.load(f)
                logger.info(f"Loaded {len(cached)} existing student records from cache.")
                return cached
        except Exception as e:
            logger.warning(f"Failed to read cache file: {e}")
    return {}


def save_cached_students(cache: Dict[str, Dict[str, Any]]):
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    temp_file = CACHE_FILE + ".tmp"
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False)
    os.replace(temp_file, CACHE_FILE)


def fetch_and_parse_college_sheet(session: requests.Session, eiin: int) -> Dict[str, Any]:
    url = COLLEGE_SHEET_URL.format(eiin=eiin)
    resp = session.get(url, timeout=25)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    pages = soup.find_all("div", class_="page")
    if not pages:
        raise ValueError(f"No pages found in result sheet for EIIN {eiin}")

    sub_title = soup.find("div", class_="sub_title")
    sub_text = sub_title.text.strip() if sub_title else ""
    mc = re.search(r"Center:\s*([A-Za-z\s]+?)\s*-\s*(\d+)", sub_text)
    mi = re.search(r"Institute:\s*(.*?)\s*\((\d+)\)", sub_text)

    center_name = mc.group(1).strip() if mc else ""
    center_code = mc.group(2).strip() if mc else ""
    institute_name = mi.group(1).strip() if mi else ""

    streams = {
        "Science": [],
        "Humanities": [],
        "Business Studies": []
    }
    declared_counts = {}
    stats = {}

    for page in pages:
        data = page.find("div", class_="data")
        if not data:
            continue

        current_stream = None
        for child in data.find_all("div", recursive=False):
            classes = child.get("class", [])
            if "group_title" in classes:
                t = child.text.strip()
                if "Science" in t:
                    current_stream = "Science"
                elif "Humanities" in t:
                    current_stream = "Humanities"
                elif "Business" in t:
                    current_stream = "Business Studies"
                elif "Statistics" in t:
                    current_stream = "Statistics"
                else:
                    current_stream = None
            elif "group_body" in classes:
                if current_stream in streams:
                    for res in child.find_all("div", class_="result"):
                        m = re.match(r"^(\d{6})\s*\[(.*?)\]$", res.text.strip())
                        if m:
                            roll = m.group(1)
                            raw_status = m.group(2).strip()
                            streams[current_stream].append({
                                "roll": roll,
                                "raw_status": raw_status,
                                "stream": current_stream,
                                "eiin": eiin
                            })
                    m_cnt = re.search(r"=\s*(\d+)\s*$", child.text)
                    if m_cnt:
                        declared_counts[current_stream] = int(m_cnt.group(1))
                elif current_stream == "Statistics":
                    m_stat = re.search(
                        r"5\s*=\s*(\d+),\s*4 to <5\s*=\s*(\d+),\s*3\.5 to <4\s*=\s*(\d+),\s*"
                        r"3 to <3\.5\s*=\s*(\d+),\s*2 to <3\s*=\s*(\d+),\s*1 to <2\s*=\s*(\d+),\s*"
                        r"0\s*=\s*(\d+),\s*Total\s*=\s*(\d+)", child.text
                    )
                    if m_stat:
                        g5, g4, g35, g3, g2, g1, g0, tot = map(int, m_stat.groups())
                        stats = {
                            "gpa_5": g5,
                            "gpa_4_to_5": g4,
                            "gpa_35_to_4": g35,
                            "gpa_3_to_35": g3,
                            "gpa_2_to_3": g2,
                            "gpa_1_to_2": g1,
                            "gpa_0": g0,
                            "total": tot,
                            "passed": g5 + g4 + g35 + g3 + g2 + g1,
                            "failed": g0
                        }

    return {
        "eiin": eiin,
        "institute_name": institute_name,
        "center_name": f"{center_name} - {center_code}" if center_code else center_name,
        "streams": streams,
        "declared_counts": declared_counts,
        "statistics": stats
    }


def fetch_individual_student(session: requests.Session, roll: str) -> Optional[Dict[str, Any]]:
    payload = {"roll": roll, "regno": ""}
    for attempt in range(6):
        try:
            resp = session.post(INDIVIDUAL_RESULT_URL, data=payload, timeout=20)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                text = soup.get_text()
                if "is not valid roll" in text:
                    logger.error(f"Roll {roll} is not valid roll according to server!")
                    return None

                info_table = soup.find("table", class_="table_info")
                if not info_table:
                    time.sleep(0.5 * (attempt + 1))
                    continue

                info = {}
                for tr in info_table.find_all("tr"):
                    tds = tr.find_all("td")
                    for i in range(0, len(tds), 2):
                        if i + 1 < len(tds):
                            label = tds[i].text.strip().rstrip(":")
                            val = tds[i+1].text.strip()
                            info[label] = val

                grade_table = soup.find("table", class_="table_result")
                subjects = []
                if grade_table:
                    for tr in grade_table.find_all("tr"):
                        tds = tr.find_all("td")
                        if len(tds) == 2:
                            sub_name = tds[0].text.strip()
                            grade = tds[1].text.strip()
                            subjects.append({
                                "code": SUBJECT_CODE_MAP.get(sub_name, ""),
                                "name": sub_name,
                                "subject": sub_name,
                                "grade": grade,
                                "point": GRADE_POINT_MAP.get(grade, 0.0)
                            })

                return {
                    "roll": roll,
                    "name": info.get("Name", ""),
                    "regno": info.get("Reg. No", ""),
                    "father_name": info.get("Father's Name", ""),
                    "mother_name": info.get("Mother's Name", ""),
                    "group": info.get("Group", ""),
                    "session": info.get("Session", ""),
                    "passing_year": info.get("Passing Year", "2026"),
                    "type": info.get("Type", "REGULAR"),
                    "institute": info.get("Institute", ""),
                    "center": info.get("Center", ""),
                    "result_raw": info.get("Result", ""),
                    "subjects": subjects
                }
        except Exception as e:
            time.sleep(0.6 * (attempt + 1))

    logger.error(f"Failed to fetch student profile for roll {roll} after 6 attempts")
    return None


def main():
    logger.info("=== Starting Narail HSC 2026 Result Ingestion Pipeline ===")

    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(PUBLIC_DATA_DIR, exist_ok=True)
    os.makedirs(COLLEGES_DATA_DIR, exist_ok=True)
    os.makedirs(PUBLIC_COLLEGES_DATA_DIR, exist_ok=True)

    logger.info(f"Loading reference metadata from {SOURCE_COLLEGES_PATH}...")
    with open(SOURCE_COLLEGES_PATH, "r", encoding="utf-8") as f:
        reference_colleges = json.load(f)

    logger.info(f"Found {len(reference_colleges)} reference colleges.")

    session = create_resilient_session(pool_size=32)

    logger.info("Fetching and parsing college result sheets for all 24 colleges...")
    college_sheets = {}
    all_roster = []

    for idx, ref_col in enumerate(reference_colleges, 1):
        eiin = ref_col["eiin"]
        sheet = fetch_and_parse_college_sheet(session, eiin)
        college_sheets[eiin] = sheet

        total_in_sheet = sum(len(rolls) for rolls in sheet["streams"].values())
        logger.info(
            f"[{idx}/24] EIIN {eiin} ({ref_col['college_name']}): "
            f"Found {total_in_sheet} examinees (Sci: {len(sheet['streams']['Science'])}, "
            f"Hum: {len(sheet['streams']['Humanities'])}, Bus: {len(sheet['streams']['Business Studies'])})"
        )

        for stream_name, student_list in sheet["streams"].items():
            for s in student_list:
                all_roster.append({
                    "roll": s["roll"],
                    "raw_status": s["raw_status"],
                    "stream": stream_name,
                    "eiin": eiin,
                    "ref": ref_col
                })

    logger.info(f"Total candidate rolls extracted from sheets: {len(all_roster)}")
    assert len(all_roster) == 5065, f"Expected 5,065 candidates, found {len(all_roster)}"

    student_cache = load_cached_students()

    # Retry loop until 100% of candidate profiles are fetched
    round_num = 1
    while True:
        missing_rolls = [item["roll"] for item in all_roster if item["roll"] not in student_cache]
        if not missing_rolls:
            logger.info("All 5,065 candidate profiles are verified in cache.")
            break

        logger.info(f"[Round {round_num}] Fetching {len(missing_rolls)} remaining student profiles (12 concurrent workers)...")
        start_time = time.time()
        completed_count = 0

        with ThreadPoolExecutor(max_workers=12) as executor:
            future_to_roll = {
                executor.submit(fetch_individual_student, session, roll): roll
                for roll in missing_rolls
            }

            for future in as_completed(future_to_roll):
                roll = future_to_roll[future]
                try:
                    res = future.result()
                    if res:
                        student_cache[roll] = res
                except Exception as e:
                    logger.error(f"Exception fetching roll {roll}: {e}")

                completed_count += 1
                if completed_count % 200 == 0 or completed_count == len(missing_rolls):
                    elapsed = time.time() - start_time
                    rate = completed_count / elapsed if elapsed > 0 else 0
                    logger.info(f"Progress: {completed_count}/{len(missing_rolls)} ({rate:.1f} req/s). Total in cache: {len(student_cache)}.")
                    save_cached_students(student_cache)

        save_cached_students(student_cache)
        round_num += 1
        time.sleep(1)

    logger.info("All 5,065 student profiles successfully fetched and cached!")

    # Assemble structured records
    logger.info("Assembling college and consolidated datasets...")

    all_students_flat = []
    college_student_map = {ref["eiin"]: [] for ref in reference_colleges}
    roll_lookup = {}

    stream_counts = {"Science": 0, "Humanities": 0, "Business Studies": 0}
    stream_passed = {"Science": 0, "Humanities": 0, "Business Studies": 0}
    stream_gpa5 = {"Science": 0, "Humanities": 0, "Business Studies": 0}
    total_passed = 0
    total_gpa5 = 0

    for item in all_roster:
        roll = item["roll"]
        eiin = item["eiin"]
        stream = item["stream"]
        raw_status = item["raw_status"]
        ref_col = item["ref"]

        profile = student_cache.get(roll, {})

        status = "FAILED"
        gpa = 0.0

        try:
            gpa_val = float(raw_status)
            status = "PASSED"
            gpa = round(gpa_val, 2)
        except ValueError:
            if raw_status == "Abst":
                status = "ABSENT"
                gpa = 0.0
            elif raw_status == "Expl":
                status = "REPORTED"
                gpa = 0.0
            else:
                status = "FAILED"
                gpa = 0.0

        if status == "PASSED":
            total_passed += 1
            stream_passed[stream] += 1
            if gpa >= 5.00:
                total_gpa5 += 1
                stream_gpa5[stream] += 1

        stream_counts[stream] += 1

        raw_upazila = ref_col.get("upazila", "")
        clean_upazila = "Kalia" if "Kalia" in raw_upazila else raw_upazila

        student_record = {
            "roll": roll,
            "regno": profile.get("regno", "") or "",
            "reg_no": profile.get("regno", "") or "",
            "name": profile.get("name", ""),
            "father_name": profile.get("father_name", ""),
            "mother_name": profile.get("mother_name", ""),
            "stream": stream,
            "group": profile.get("group", stream.upper()),
            "session": profile.get("session", "2024-25"),
            "passing_year": profile.get("passing_year", "2026"),
            "type": profile.get("type", "REGULAR"),
            "candidate_type": profile.get("type", "REGULAR"),
            "status": status,
            "result_status": status,
            "result": status,
            "raw_status": raw_status,
            "gpa": gpa,
            "eiin": eiin,
            "college_name": ref_col["college_name"],
            "institute": ref_col["college_name"],
            "upazila": clean_upazila,
            "upazila_detail": raw_upazila,
            "center": ref_col["center"],
            "subjects": profile.get("subjects", [])
        }

        all_students_flat.append(student_record)
        college_student_map[eiin].append(student_record)

        roll_lookup[roll] = {
            "roll": roll,
            "name": student_record["name"],
            "college": ref_col["college_name"],
            "eiin": eiin,
            "stream": stream,
            "gpa": gpa,
            "status": status,
            "n": student_record["name"],
            "e": eiin,
            "s": stream,
            "g": gpa,
            "st": status
        }

    logger.info("=== Dataset Summary Statistics ===")
    logger.info(f"Total Candidates: {len(all_students_flat)} (Expected: 5,065)")
    logger.info(f"Total Passed: {total_passed} (Expected: 1,776)")
    logger.info(f"Total GPA 5.00: {total_gpa5} (Expected: 105)")
    logger.info(f"Science: {stream_counts['Science']} appeared, {stream_passed['Science']} passed, {stream_gpa5['Science']} GPA 5.00 (Expected: 815, 458, 56)")
    logger.info(f"Humanities: {stream_counts['Humanities']} appeared, {stream_passed['Humanities']} passed, {stream_gpa5['Humanities']} GPA 5.00 (Expected: 3748, 1168, 45)")
    logger.info(f"Business Studies: {stream_counts['Business Studies']} appeared, {stream_passed['Business Studies']} passed, {stream_gpa5['Business Studies']} GPA 5.00 (Expected: 502, 150, 4)")

    assert len(all_students_flat) == 5065, "Total students mismatch!"
    assert total_passed == 1776, "Total passed mismatch!"
    assert total_gpa5 == 105, "Total GPA 5.00 mismatch!"
    assert stream_counts["Science"] == 815, "Science appeared mismatch!"
    assert stream_counts["Humanities"] == 3748, "Humanities appeared mismatch!"
    assert stream_counts["Business Studies"] == 502, "Business Studies appeared mismatch!"
    assert stream_passed["Science"] == 458, "Science passed mismatch!"
    assert stream_passed["Humanities"] == 1168, "Humanities passed mismatch!"
    assert stream_passed["Business Studies"] == 150, "Business Studies passed mismatch!"
    assert stream_gpa5["Science"] == 56, "Science GPA 5 mismatch!"
    assert stream_gpa5["Humanities"] == 45, "Humanities GPA 5 mismatch!"
    assert stream_gpa5["Business Studies"] == 4, "Business Studies GPA 5 mismatch!"

    # 6. Build and write individual college JSON files
    colleges_manifest_list = []
    upazila_stats = {
        "Narail Sadar": {"colleges_count": 0, "appeared": 0, "passed": 0, "gpa5": 0},
        "Lohagara": {"colleges_count": 0, "appeared": 0, "passed": 0, "gpa5": 0},
        "Kalia": {"colleges_count": 0, "appeared": 0, "passed": 0, "gpa5": 0}
    }

    for ref_col in reference_colleges:
        eiin = ref_col["eiin"]
        students = college_student_map[eiin]

        raw_upazila = ref_col.get("upazila", "")
        clean_upazila = "Kalia" if "Kalia" in raw_upazila else raw_upazila

        col_appeared = len(students)
        col_passed = sum(1 for s in students if s["status"] == "PASSED")
        col_failed = col_appeared - col_passed
        col_gpa5 = sum(1 for s in students if s["status"] == "PASSED" and s["gpa"] >= 5.00)
        col_pass_rate = round((col_passed / col_appeared * 100), 2) if col_appeared > 0 else 0.0

        stream_breakdown = {}
        stream_summary = {}
        for s_name in ["Science", "Humanities", "Business Studies"]:
            s_students = [s for s in students if s["stream"] == s_name]
            s_app = len(s_students)
            s_pass = sum(1 for s in s_students if s["status"] == "PASSED")
            s_fail = s_app - s_pass
            s_g5 = sum(1 for s in s_students if s["status"] == "PASSED" and s["gpa"] >= 5.00)
            s_rate = round((s_pass / s_app * 100), 2) if s_app > 0 else 0.0

            key_lower = s_name.lower().replace(" ", "_")
            stream_breakdown[key_lower] = {
                "appeared": s_app,
                "passed": s_pass,
                "failed": s_fail,
                "gpa5": s_g5,
                "pass_rate": s_rate
            }
            stream_summary[s_name] = {
                "total": s_app,
                "passed": s_pass,
                "failed": s_fail,
                "gpa5": s_g5,
                "pass_rate": s_rate
            }

        gpa_dist = {
            "gpa_5": col_gpa5,
            "gpa_4_to_5": sum(1 for s in students if s["status"] == "PASSED" and 4.00 <= s["gpa"] < 5.00),
            "gpa_35_to_4": sum(1 for s in students if s["status"] == "PASSED" and 3.50 <= s["gpa"] < 4.00),
            "gpa_3_to_35": sum(1 for s in students if s["status"] == "PASSED" and 3.00 <= s["gpa"] < 3.50),
            "gpa_2_to_3": sum(1 for s in students if s["status"] == "PASSED" and 2.00 <= s["gpa"] < 3.00),
            "gpa_1_to_2": sum(1 for s in students if s["status"] == "PASSED" and 1.00 <= s["gpa"] < 2.00),
            "gpa_0": col_failed
        }

        college_data = {
            "eiin": eiin,
            "college_name": ref_col["college_name"],
            "name": ref_col["college_name"],
            "bengali_name": ref_col.get("bengali_name", ""),
            "center": ref_col["center"],
            "upazila": clean_upazila,
            "upazila_detail": raw_upazila,
            "established": ref_col.get("established", ""),
            "total_registered": col_appeared,
            "total_appeared": col_appeared,
            "total_passed": col_passed,
            "total_failed": col_failed,
            "total_gpa5": col_gpa5,
            "pass_rate": col_pass_rate,
            "participating_streams": ref_col.get("participating_streams", []),
            "stream_stats": ref_col.get("stream_stats", {}),
            "gpa_breakdown": ref_col.get("gpa_breakdown", {}),
            "statistics": {
                "total_registered": col_appeared,
                "total_appeared": col_appeared,
                "total_passed": col_passed,
                "total_failed": col_failed,
                "pass_rate": col_pass_rate,
                "gpa5_count": col_gpa5,
                "stream_breakdown": stream_breakdown,
                "gpa_distribution": gpa_dist
            },
            "stream_summary": stream_summary,
            "students": students
        }

        p1 = os.path.join(COLLEGES_DATA_DIR, f"{eiin}.json")
        p2 = os.path.join(PUBLIC_COLLEGES_DATA_DIR, f"{eiin}.json")
        for p in [p1, p2]:
            with open(p, "w", encoding="utf-8") as f:
                json.dump(college_data, f, ensure_ascii=False, indent=2)

        if clean_upazila in upazila_stats:
            upazila_stats[clean_upazila]["colleges_count"] += 1
            upazila_stats[clean_upazila]["appeared"] += col_appeared
            upazila_stats[clean_upazila]["passed"] += col_passed
            upazila_stats[clean_upazila]["gpa5"] += col_gpa5

        colleges_manifest_list.append({
            "eiin": eiin,
            "name": ref_col["college_name"],
            "bengali_name": ref_col.get("bengali_name", ""),
            "upazila": clean_upazila,
            "center": ref_col["center"],
            "total_appeared": col_appeared,
            "total_passed": col_passed,
            "total_failed": col_failed,
            "pass_rate": col_pass_rate,
            "gpa5_count": col_gpa5,
            "stream_summary": stream_summary,
            "gpa_distribution": gpa_dist
        })

    for u_name, u_stat in upazila_stats.items():
        u_stat["pass_rate"] = round((u_stat["passed"] / u_stat["appeared"] * 100), 2) if u_stat["appeared"] > 0 else 0.0

    manifest_data = {
        "district": "Narail",
        "board": "Board of Intermediate and Secondary Education, Jashore",
        "exam": "Higher Secondary Certificate Examination 2026",
        "publication_date": "31 October, 2026",
        "summary": {
            "total_colleges": len(reference_colleges),
            "total_examinees": len(all_students_flat),
            "total_appeared": len(all_students_flat),
            "total_passed": total_passed,
            "total_failed": len(all_students_flat) - total_passed,
            "pass_rate": round(total_passed / len(all_students_flat) * 100, 2),
            "gpa5_count": total_gpa5,
            "streams": {
                "Science": {
                    "appeared": stream_counts["Science"],
                    "passed": stream_passed["Science"],
                    "failed": stream_counts["Science"] - stream_passed["Science"],
                    "gpa5": stream_gpa5["Science"],
                    "pass_rate": round(stream_passed["Science"] / stream_counts["Science"] * 100, 2)
                },
                "Humanities": {
                    "appeared": stream_counts["Humanities"],
                    "passed": stream_passed["Humanities"],
                    "failed": stream_counts["Humanities"] - stream_passed["Humanities"],
                    "gpa5": stream_gpa5["Humanities"],
                    "pass_rate": round(stream_passed["Humanities"] / stream_counts["Humanities"] * 100, 2)
                },
                "Business Studies": {
                    "appeared": stream_counts["Business Studies"],
                    "passed": stream_passed["Business Studies"],
                    "failed": stream_counts["Business Studies"] - stream_passed["Business Studies"],
                    "gpa5": stream_gpa5["Business Studies"],
                    "pass_rate": round(stream_passed["Business Studies"] / stream_counts["Business Studies"] * 100, 2)
                }
            },
            "upazilas": upazila_stats
        },
        "colleges": colleges_manifest_list
    }

    for p in [os.path.join(DATA_DIR, "manifest.json"), os.path.join(PUBLIC_DATA_DIR, "manifest.json")]:
        with open(p, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, ensure_ascii=False, indent=2)

    for p in [os.path.join(DATA_DIR, "roll_lookup.json"), os.path.join(PUBLIC_DATA_DIR, "roll_lookup.json")]:
        with open(p, "w", encoding="utf-8") as f:
            json.dump(roll_lookup, f, ensure_ascii=False)

    for name in ["narail_all_students.json", "all_students.json"]:
        for d in [DATA_DIR, PUBLIC_DATA_DIR]:
            p = os.path.join(d, name)
            with open(p, "w", encoding="utf-8") as f:
                json.dump(all_students_flat, f, ensure_ascii=False)

    logger.info("=== Pipeline Completed Successfully! ===")
    logger.info(f"Persisted 24 college files to {COLLEGES_DATA_DIR} and {PUBLIC_COLLEGES_DATA_DIR}")
    logger.info("Persisted manifest.json, roll_lookup.json, and narail_all_students.json")


if __name__ == "__main__":
    main()
