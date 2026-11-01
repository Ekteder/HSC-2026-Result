# tests/helpers/data_loader.py
"""
Data loader and artifact resolver for Narail HSC 2026 E2E Test Suite.
Resolves data files from application directories, public directories, and verified survey datasets.
"""
import os
import json
import glob
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
from tests.test_config import (
    APP_DIR, APP_DATA_DIR, APP_PUBLIC_DATA_DIR,
    ROOT_DATA_DIR, ROOT_PUBLIC_DATA_DIR,
    SURVEY_JSON, WORKSPACE_ROOT
)

class DataLoader:
    _instance = None

    def __init__(self):
        self._colleges_cache = None
        self._students_cache = None
        self._manifest_cache = None
        self._roll_lookup_cache = None
        self._raw_students_cache = None

    @classmethod
    def get_instance(cls) -> "DataLoader":
        if cls._instance is None:
            cls._instance = DataLoader()
        return cls._instance

    def get_colleges_dir(self) -> Optional[str]:
        """Locates the directory containing individual college JSON files."""
        candidates = [
            os.path.join(APP_PUBLIC_DATA_DIR, "colleges"),
            os.path.join(APP_DATA_DIR, "colleges"),
            os.path.join(ROOT_PUBLIC_DATA_DIR, "colleges"),
            os.path.join(ROOT_DATA_DIR, "colleges")
        ]
        for c in candidates:
            if os.path.isdir(c) and len(os.listdir(c)) > 0:
                return c
        return None

    def get_manifest_path(self) -> Optional[str]:
        """Locates manifest.json."""
        candidates = [
            os.path.join(APP_PUBLIC_DATA_DIR, "manifest.json"),
            os.path.join(APP_DATA_DIR, "manifest.json"),
            os.path.join(ROOT_PUBLIC_DATA_DIR, "manifest.json"),
            os.path.join(ROOT_DATA_DIR, "manifest.json")
        ]
        for c in candidates:
            if os.path.isfile(c):
                return c
        return None

    def get_all_students_path(self) -> Optional[str]:
        """Locates narail_all_students.json or all_students.json."""
        candidates = [
            os.path.join(APP_PUBLIC_DATA_DIR, "narail_all_students.json"),
            os.path.join(APP_DATA_DIR, "narail_all_students.json"),
            os.path.join(ROOT_PUBLIC_DATA_DIR, "narail_all_students.json"),
            os.path.join(ROOT_DATA_DIR, "narail_all_students.json"),
            os.path.join(APP_PUBLIC_DATA_DIR, "all_students.json"),
            os.path.join(APP_DATA_DIR, "all_students.json")
        ]
        for c in candidates:
            if os.path.isfile(c):
                return c
        return None

    def get_roll_lookup_path(self) -> Optional[str]:
        """Locates roll_lookup.json."""
        candidates = [
            os.path.join(APP_PUBLIC_DATA_DIR, "roll_lookup.json"),
            os.path.join(APP_DATA_DIR, "roll_lookup.json"),
            os.path.join(ROOT_PUBLIC_DATA_DIR, "roll_lookup.json"),
            os.path.join(ROOT_DATA_DIR, "roll_lookup.json")
        ]
        for c in candidates:
            if os.path.isfile(c):
                return c
        return None

    def get_all_colleges(self) -> List[Dict[str, Any]]:
        """
        Loads all 24 colleges. Prioritizes ingested JSONs, falling back to
        authoritative survey explorer ground truth.
        """
        if self._colleges_cache is not None:
            return self._colleges_cache

        colleges_dir = self.get_colleges_dir()
        if colleges_dir:
            colleges = []
            for file_name in sorted(os.listdir(colleges_dir)):
                if file_name.endswith(".json"):
                    full_path = os.path.join(colleges_dir, file_name)
                    with open(full_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        colleges.append(data)
            if len(colleges) >= 24:
                self._colleges_cache = colleges
                return self._colleges_cache

        # Fallback to authoritative verified ground truth
        if os.path.isfile(SURVEY_JSON):
            with open(SURVEY_JSON, "r", encoding="utf-8") as f:
                self._colleges_cache = json.load(f)
                return self._colleges_cache

        raise FileNotFoundError("Could not find college data in any recognized location.")

    def get_college_by_eiin(self, eiin: int) -> Optional[Dict[str, Any]]:
        colleges = self.get_all_colleges()
        for c in colleges:
            c_eiin = int(c.get("eiin", 0))
            if c_eiin == int(eiin):
                return c
        return None

    def parse_raw_student_html(self, html: str) -> Dict[str, Any]:
        """Parses individual student HTML response as specified in spec_report.md."""
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text()

        if "is not valid roll of 2026 HSC" in text:
            return {"success": False, "error": "INVALID_ROLL"}
        if "Roll No. and Registration No. does not match" in text:
            return {"success": False, "error": "REGNO_MISMATCH"}

        info_table = soup.find("table", class_="table_info")
        if not info_table:
            return {"success": False, "error": "NO_INFO_TABLE"}

        info = {}
        for tr in info_table.find_all("tr"):
            tds = tr.find_all("td")
            for i in range(0, len(tds), 2):
                if i + 1 < len(tds):
                    label = tds[i].text.strip().rstrip(":")
                    val = tds[i + 1].text.strip()
                    info[label] = val

        grade_table = soup.find("table", class_="table_result")
        subjects = []
        if grade_table:
            for tr in grade_table.find_all("tr"):
                tds = tr.find_all("td")
                if len(tds) == 2:
                    subjects.append({
                        "subject": tds[0].text.strip(),
                        "grade": tds[1].text.strip()
                    })

        res_str = info.get("Result", "")
        gpa = None
        status = res_str
        if res_str.startswith("GPA="):
            try:
                gpa = float(res_str.split("GPA=")[1].strip())
                status = "PASSED"
            except ValueError:
                pass
        elif res_str == "FAIL":
            status = "FAIL"
            gpa = 0.0

        return {
            "success": True,
            "roll": str(info.get("Roll No", "")),
            "name": info.get("Name", ""),
            "reg_no": info.get("Reg. No", "") or None,
            "father_name": info.get("Father's Name", ""),
            "mother_name": info.get("Mother's Name", ""),
            "stream": info.get("Group", "").title(),
            "session": info.get("Session", ""),
            "passing_year": info.get("Passing Year", "2026"),
            "candidate_type": info.get("Type", ""),
            "institute": info.get("Institute", ""),
            "center": info.get("Center", ""),
            "result_raw": res_str,
            "status": status,
            "gpa": gpa,
            "subjects": subjects
        }

    def get_raw_student_records(self) -> List[Dict[str, Any]]:
        """Loads and parses raw student records from public/assets/aistudio/*.json."""
        if self._raw_students_cache is not None:
            return self._raw_students_cache

        records = []
        pattern = os.path.join(WORKSPACE_ROOT, "public", "assets", "aistudio", "*results*.json")
        for fpath in glob.glob(pattern):
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    items = json.load(f)
                    for item in items:
                        html = item.get("data", "")
                        parsed = self.parse_raw_student_html(html)
                        if parsed.get("success"):
                            parsed["source_file"] = os.path.basename(fpath)
                            records.append(parsed)
            except Exception:
                pass

        self._raw_students_cache = records
        return self._raw_students_cache

    def get_all_students(self) -> List[Dict[str, Any]]:
        """Loads consolidated students from JSON dataset, college JSONs, or parsed raw records."""
        if self._students_cache is not None:
            return self._students_cache

        # 1. Consolidated dataset file
        all_students_path = self.get_all_students_path()
        if all_students_path:
            with open(all_students_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    self._students_cache = data
                    return self._students_cache

        # 2. Collect from individual college files
        colleges_dir = self.get_colleges_dir()
        if colleges_dir:
            all_s = []
            for file_name in sorted(os.listdir(colleges_dir)):
                if file_name.endswith(".json"):
                    with open(os.path.join(colleges_dir, file_name), "r", encoding="utf-8") as f:
                        c_data = json.load(f)
                        students = c_data.get("students", [])
                        all_s.extend(students)
            if len(all_s) > 0:
                self._students_cache = all_s
                return self._students_cache

        # 3. Fallback to raw parsed records from aistudio assets
        raw_students = self.get_raw_student_records()
        if raw_students:
            self._students_cache = raw_students
            return self._students_cache

        return []

    def find_student_by_roll(self, roll: Any) -> Optional[Dict[str, Any]]:
        roll_str = str(roll).strip()
        # Check roll lookup first
        lookup_path = self.get_roll_lookup_path()
        if lookup_path:
            with open(lookup_path, "r", encoding="utf-8") as f:
                lookup = json.load(f)
                if roll_str in lookup:
                    return lookup[roll_str]

        # Check in all students
        students = self.get_all_students()
        for s in students:
            if str(s.get("roll", "")).strip() == roll_str:
                return s

        return None
