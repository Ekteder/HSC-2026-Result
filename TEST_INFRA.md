# Test Infrastructure Specification: HSC 2026 Narail District Results System

**Version**: 1.0.0  
**Test Suite Architect**: `test_writer_e2e_1` (E2E Test Suite Specialist)  
**Date**: 2026-11-01  
**Target Root**: `/media/sanglap/Movies/2026results`  
**Execution Command**: `python3 /media/sanglap/Movies/2026results/tests/run_e2e_tests.py`  

---

## 1. Overview & Architectural Philosophy

The **HSC 2026 Narail District Results System Test Harness** is an independent, opaque-box, 4-tier verification suite. It validates the full operational lifecycle of the examination results system:
- Ingestion and data schema reconciliation for all 24 participating colleges under Jessore Board.
- Student examination marks, letter grades, parental metadata, and pass/fail statuses.
- Real-time client-side search lookup, multi-faceted filtering, and analytical statistical aggregation.
- Responsive web application asset delivery, layout stability, and user journey workflows.

The test infrastructure operates under strict zero-cheat, progressive testability principles: tests execute against genuine data artifacts, validate against mathematical ground truths published by BISE Jashore, and require zero external database dependencies.

---

## 2. Test Harness Directory Layout

```
/media/sanglap/Movies/2026results/tests/
├── __init__.py                                 # Python package initialization
├── test_config.py                             # Master configuration, official BISE benchmarks, EIIN registry
├── run_e2e_tests.py                           # Master test runner (exit code 0 on all pass)
│
├── helpers/                                   # Shared test infrastructure utilities
│   ├── __init__.py
│   ├── data_loader.py                         # Multi-source resolver (ingested JSON, public assets, reference data)
│   ├── query_engine.py                        # Reference multi-faceted filter, search, and KPI calculator
│   └── web_harness.py                         # Ephemeral background HTTP web server harness
│
├── tier1_features/                            # Tier 1: Feature Coverage (F1 - F11) (>= 5 tests each)
│   ├── __init__.py
│   ├── test_f1_college_enumeration.py         # 6 tests: 24 Narail colleges, EIIN registry, Upazila distribution
│   ├── test_f2_f3_schema_fields.py            # 7 tests: roll, GPA, subjects, status, session, parent names
│   ├── test_f4_stream_parsing.py              # 6 tests: Science, Humanities, Business Studies cohort parsing
│   ├── test_f5_json_syntax.py                 # 6 tests: JSON syntax, UTF-8 Bengali encoding, asset integrity
│   ├── test_f6_statistical_reconciliation.py  # 7 tests: 5,065 examinees, 1,776 passed, 105 GPA 5.00
│   ├── test_f7_webapp_serving.py              # 6 tests: Local HTTP serving, status 200, MIME types, DOM structure
│   ├── test_f8_search_lookup.py               # 6 tests: Roll & registration search, instant profile modal
│   ├── test_f9_multifaceted_filter.py         # 6 tests: College, Upazila, Stream, Status, GPA filtering
│   ├── test_f10_analytics_dashboard.py        # 6 tests: District KPIs, leaderboard rankings, histograms
│   └── test_f11_responsive_layout.py          # 6 tests: Mobile (<640px), Tablet (640-1024px), Desktop (>=1024px)
│
├── tier2_boundaries/                          # Tier 2: Boundary & Corner Cases (>= 5 tests each)
│   ├── __init__.py
│   ├── test_b1_low_pass_colleges.py           # 6 tests: Zero pass rate (118404), low pass (118522, 131996, 118436)
│   ├── test_b2_high_performance.py            # 6 tests: Victoria College (61.63%, 69 GPA-5), Lohagara Adarsha
│   ├── test_b3_nonpassing_statuses.py         # 6 tests: F1 (1 fail), F2 (2 fails), Fail, Absent (236), Expelled (3)
│   ├── test_b4_edge_rolls.py                  # 6 tests: Extreme roll numbers for Science, Hum, Business
│   ├── test_b5_missing_regno.py               # 5 tests: Blank/None registration number graceful handling
│   └── test_b6_invalid_search_queries.py      # 6 tests: Non-existent rolls, XSS/SQL payloads, sanitize empty
│
├── tier3_combinations/                        # Tier 3: Cross-Feature Combinations (>= 5 tests each)
│   ├── __init__.py
│   ├── test_c1_college_and_stream.py          # 6 tests: Pairwise College + Stream intersections & breakdowns
│   ├── test_c2_stream_status_gpa.py           # 6 tests: Stream + Status + GPA range compound filters
│   ├── test_c3_search_with_filters.py         # 6 tests: Search query executed within active filter constraints
│   └── test_c4_upazila_stream_stats.py        # 5 tests: Upazila cross-tabulations and district reconciliation
│
└── tier4_real_world/                          # Tier 4: Real-World Application Scenarios (>= 5 tests each)
    ├── __init__.py
    ├── test_r1_parent_student_journey.py      # 5 tests: Parent looks up child roll 517756, checks grade sheet
    ├── test_r2_teacher_cross_college.py       # 5 tests: Educator evaluates inter-college comparisons & rankings
    ├── test_r3_officer_gpa5_export.py         # 5 tests: District Officer honors list (all 105 GPA 5.00 achievers)
    └── test_r4_grade_verification.py          # 5 tests: Core subjects, letter grade scale, failure retake analysis
```

---

## 3. Authoritative Expected Output Derivation

All expected values throughout the test harness are derived from authoritative official sources:
1. **Board of Intermediate and Secondary Education, Jashore Official Result Statistics Bulletin**:
   - Examination: Higher Secondary Certificate Examination 2026.
   - Publication Date: 31 October 2026.
   - Authority: Controller of Examinations Prof. S. M. Hossain Ali.
   - Official District Totals:
     - Total Registered Examinees: 5,065
     - Total Passed Examinees: 1,776 (Pass Rate: 35.06% enrolled / 36.78% appeared)
     - Total GPA 5.00 Count: 105
     - Total Absentees: 236
     - Total Expelled/Reported: 3
     - Total Examination Centers: 10
     - Total Participating Institutions: Exactly 24 colleges
2. **Empirical Jessore Board API & Roster Specifications (`spec_report.md`)**:
   - Live endpoint schema for `GET result_sheet.php?eiin={eiin}`
   - Live endpoint schema for `POST result.php` with `roll={roll}&regno=`
   - Exact status encoding matrix: `PASSED`, `F1  ` (single failure), `F2  ` (two failures), `Fail` (3+ failures), `Abst` (Absent), `Expl` (Expelled / Reported).
   - Letter grade scale: `A+` (5.0), `A` (4.0), `A-` (3.5), `B` (3.0), `C` (2.0), `D` (1.0), `F` (0.0).

---

## 4. Test Execution & Verification

### Running the Full Test Suite
```bash
python3 /media/sanglap/Movies/2026results/tests/run_e2e_tests.py
```

### Running Individual Tiers
```bash
# Tier 1: Feature Coverage
python3 -m unittest discover -s /media/sanglap/Movies/2026results/tests/tier1_features

# Tier 2: Boundary & Corner Cases
python3 -m unittest discover -s /media/sanglap/Movies/2026results/tests/tier2_boundaries

# Tier 3: Cross-Feature Combinations
python3 -m unittest discover -s /media/sanglap/Movies/2026results/tests/tier3_combinations

# Tier 4: Real-World Scenarios
python3 -m unittest discover -s /media/sanglap/Movies/2026results/tests/tier4_real_world
```

### Exit Codes
- `0`: All tests passed with 100% success rate.
- `1`: One or more test failures or unhandled exceptions detected.
