# tests/helpers/query_engine.py
"""
Query engine and mathematical verification logic for HSC 2026 results.
Provides independent reference implementations of multi-faceted filtering,
search, and analytical aggregation to verify web app calculations.
"""
from typing import Dict, Any, List, Optional

class QueryEngine:
    @staticmethod
    def filter_students(
        students: List[Dict[str, Any]],
        college_eiin: Optional[Any] = None,
        upazila: Optional[str] = None,
        stream: Optional[str] = None,
        status: Optional[str] = None,
        min_gpa: Optional[float] = None,
        max_gpa: Optional[float] = None,
        search_term: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Filters students list based on multi-faceted criteria."""
        results = []
        for s in students:
            # College EIIN filter
            if college_eiin is not None and str(college_eiin).upper() != "ALL":
                s_eiin = str(s.get("eiin", "") or s.get("college_eiin", ""))
                # Some student objects might embed eiin in institute string e.g. "College Name(118523)"
                if not s_eiin and "institute" in s:
                    import re
                    m = re.search(r'\((\d+)\)', s["institute"])
                    if m:
                        s_eiin = m.group(1)
                if s_eiin and s_eiin != str(college_eiin):
                    continue

            # Upazila filter
            if upazila and upazila.upper() != "ALL":
                s_upazila = str(s.get("upazila", "")).lower()
                if s_upazila and s_upazila != upazila.lower():
                    continue

            # Stream filter
            if stream and stream.upper() != "ALL":
                s_stream = str(s.get("stream", "") or s.get("group", "")).upper()
                target_stream = stream.upper()
                if s_stream != target_stream and not (target_stream in s_stream):
                    continue

            # Status filter
            if status and status.upper() != "ALL":
                s_status = str(s.get("status", "") or s.get("result_status", "")).upper()
                target_status = status.upper()
                if target_status == "PASS" or target_status == "PASSED":
                    if "PASS" not in s_status:
                        continue
                elif target_status == "FAIL" or target_status == "FAILED":
                    if not ("FAIL" in s_status or s_status in ["F1", "F2"]):
                        continue
                elif target_status in ["ABSENT", "ABST"]:
                    if not ("ABS" in s_status):
                        continue
                elif target_status in ["REPORTED", "EXPL", "EXPELLED"]:
                    if not ("REP" in s_status or "EXP" in s_status):
                        continue
                elif s_status != target_status:
                    continue

            # GPA range filter
            gpa_val = s.get("gpa")
            try:
                gpa_float = float(gpa_val) if gpa_val is not None else 0.0
            except (ValueError, TypeError):
                gpa_float = 0.0

            if min_gpa is not None:
                if gpa_float < min_gpa:
                    continue
            if max_gpa is not None:
                if gpa_float > max_gpa:
                    continue

            # Search term filter (matches roll, reg_no, or name)
            if search_term:
                term = str(search_term).strip().lower()
                s_roll = str(s.get("roll", "")).lower()
                s_reg = str(s.get("reg_no", "") or s.get("regno", "") or "").lower()
                s_name = str(s.get("name", "")).lower()
                if term not in s_roll and term not in s_reg and term not in s_name:
                    continue

            results.append(s)
        return results

    @staticmethod
    def calculate_kpi(students: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculates standard KPIs: total, passed, failed, pass_rate, gpa5_count."""
        total = len(students)
        if total == 0:
            return {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "pass_rate": 0.0,
                "gpa5_count": 0
            }

        passed = 0
        failed = 0
        gpa5 = 0

        for s in students:
            st = str(s.get("status", "") or s.get("result_status", "")).upper()
            gpa = s.get("gpa")
            try:
                gpa_f = float(gpa) if gpa is not None else 0.0
            except (ValueError, TypeError):
                gpa_f = 0.0

            if "PASS" in st or gpa_f > 0.0:
                passed += 1
                if abs(gpa_f - 5.0) < 1e-4:
                    gpa5 += 1
            else:
                failed += 1

        pass_rate = round((passed / total) * 100, 2)
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": pass_rate,
            "gpa5_count": gpa5
        }

    @staticmethod
    def calculate_gpa_histogram(students: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculates student counts across GPA grade bands."""
        bands = {
            "5.00": 0,
            "4.00-4.99": 0,
            "3.50-3.99": 0,
            "3.00-3.49": 0,
            "2.00-2.99": 0,
            "1.00-1.99": 0,
            "Fail/0.00": 0
        }
        for s in students:
            st = str(s.get("status", "") or s.get("result_status", "")).upper()
            try:
                gpa = float(s.get("gpa", 0.0) or 0.0)
            except (ValueError, TypeError):
                gpa = 0.0

            if "PASS" not in st or gpa == 0.0:
                bands["Fail/0.00"] += 1
            elif abs(gpa - 5.0) < 1e-4:
                bands["5.00"] += 1
            elif gpa >= 4.0:
                bands["4.00-4.99"] += 1
            elif gpa >= 3.5:
                bands["3.50-3.99"] += 1
            elif gpa >= 3.0:
                bands["3.00-3.49"] += 1
            elif gpa >= 2.0:
                bands["2.00-2.99"] += 1
            elif gpa >= 1.0:
                bands["1.00-1.99"] += 1
            else:
                bands["Fail/0.00"] += 1
        return bands
