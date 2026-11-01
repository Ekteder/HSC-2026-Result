# Project: Narail District HSC 2026 Results System & Web Application

## Architecture Overview
The system consists of two major operational tracks:
1. **Data Ingestion & Validation Track (Backend/ETL)**:
   - Automated parallel fetching of college-wise result sheets from Jessore Board (`result_sheet.php?eiin={eiin}`) for all 24 verified Narail colleges.
   - Parsing of candidate roster into Science, Humanities, and Business Studies streams.
   - High-throughput parallel querying of individual student results (`POST result.php` with `roll={roll}&regno=`) to extract Student Name, Father's Name, Mother's Name, College Name, Roll, Registration Number, Group/Stream, GPA, Subject-wise Letter Grades, and Result Status.
   - Comprehensive cross-validation ensuring candidate counts, passing counts, GPA-5 counts, and stream distributions strictly reconcile with official Jessore Board statistics (5,065 registered, 1,776 passed, 105 GPA 5.00).
   - Persistence of structured college-wise JSON files (`data/colleges/{eiin}.json`), a consolidated index (`data/narail_all_students.json`), and metadata manifest (`data/manifest.json`).

2. **Responsive Results Web Application Track (Frontend)**:
   - Single-page application built inside `/media/sanglap/Movies/2026results/narail_results_app`.
   - Toolchain: Modern frontend framework / Vite + Tailwind CSS + Chart.js, managed with `pnpm` (`pnpm dev`, `pnpm build`, `pnpm preview`), plus standalone zero-dependency Python fallback serving (`pnpm serve`).
   - 3-Tier Client-side Data Architecture:
     - Tier 1: `manifest.json` for instant bootstrap (<25 KB).
     - Tier 2: `roll_lookup.json` for instant $O(1)$ search autocomplete.
     - Tier 3: In-memory structured dataset (~5 MB) enabling sub-4ms multi-faceted filtering.
   - UI/UX Capabilities:
     - Global search hero: Instant Roll and Registration number search, detailed Student Grade Sheet modal.
     - Multi-faceted filter: College selection (all 24 colleges), Upazila (Narail Sadar, Lohagara, Kalia), Stream (Science, Humanities, Business Studies), GPA range presets and sliders, Result Status (Passed, Failed, Absent, Expelled).
     - Analytics Dashboard: Overall district KPI summary (Pass rate, GPA-5 count, stream distribution), interactive college pass rate leaderboard, GPA distribution histograms, sortable performance matrix.
     - Responsive Design: Tailored layouts for mobile (<640px) with bottom nav & card views, tablet (640-1024px), and desktop (≥1024px).

3. **E2E Testing & Quality Gate Track (Opaque-box Verification)**:
   - Test harness covering Tiers 1-5 (Feature Coverage, Boundaries & Corners, Cross-Feature Combinations, Real-World Workload Testing, Adversarial Hardening).
   - All 156 / 156 tests passing with 100% success rate (exit code 0).
   - Forensic Integrity Audit verdict: CLEAN.

---

## Code Layout
```
/media/sanglap/Movies/2026results/
├── narail_results_app/               # Application target directory
│   ├── package.json                  # pnpm package configuration (scripts: dev, build, preview, serve)
│   ├── pnpm-lock.yaml                # Lockfile
│   ├── vite.config.js                # Vite configuration
│   ├── index.html                    # HTML entry point
│   ├── dist/                         # Production build distribution
│   ├── src/                          # Frontend source code
│   │   ├── main.js                   # Application bootstrap
│   │   ├── components/               # SearchHero, StudentModal, AnalyticsDashboard, FilterPanel, StudentTable, CollegeMatrix
│   │   ├── styles/                   # main.css (responsive styles & print sheets)
│   │   └── utils/                    # dataLoader.js (in-memory multi-tiered query engine)
│   ├── public/ / data/               # Static data directory
│   │   ├── manifest.json             # District & college summary metadata
│   │   ├── roll_lookup.json          # Fast lookup index
│   │   ├── narail_all_students.json  # Consolidated dataset (5,065 students)
│   │   └── colleges/                 # 24 College-wise JSON files
│   └── scripts/                      # Data ingestion & validation utilities
│       ├── ingest_narail_results.py  # High-throughput parallel ingestion pipeline
│       └── validate_dataset.py       # Strict mathematical reconciliation validator
└── tests/                            # 5-Tier E2E test suite (156 tests)
    ├── tier1_features/               # F1-F11 coverage (62 tests)
    ├── tier2_boundaries/             # B1-B6 edge cases (35 tests)
    ├── tier3_combinations/           # C1-C4 cross-feature tests (23 tests)
    ├── tier4_real_world/             # R1-R4 scenarios (20 tests)
    ├── tier5_adversarial/            # Adversarial hardening (16 tests)
    └── run_e2e_tests.py              # Master test runner
```

---

## Feature Inventory
| # | Feature | Description | Milestone | Source | Status |
|---|---------|-------------|-----------|--------|--------|
| F1 | Narail College EIIN Enumeration | Exhaustive verification of all 24 participating colleges in Narail District | M1 | ORIGINAL_REQUEST §R1 | VERIFIED |
| F2 | College Result Sheet Ingestion | Parallel fetching of college result sheets from Jessore Board endpoint | M1 | ORIGINAL_REQUEST §R1 | VERIFIED |
| F3 | Individual Student Result Ingestion | Parallel querying of individual student marks & grades via `POST result.php` | M1 | ORIGINAL_REQUEST §R1 | VERIFIED |
| F4 | Multi-Stream Parsing | Extraction of roll, stream (Science, Humanities, Business), GPA, status codes | M1 | ORIGINAL_REQUEST §R1 | VERIFIED |
| F5 | College-wise JSON Persistence | Saving valid individual JSON files per college and consolidated dataset | M1 | ORIGINAL_REQUEST §R1 | VERIFIED |
| F6 | Statistical Data Reconciliation | Validating parsed record counts against summary sheets and board statistics | M1 | ORIGINAL_REQUEST §AC | VERIFIED |
| F7 | Application Local Execution | Fast, error-free local execution via `pnpm` (dev/build/preview) and Python serve | M2 | ORIGINAL_REQUEST §R2 | VERIFIED |
| F8 | Student Search Interface | Fast lookup by Roll and Registration number with grade sheet modal display | M2 | ORIGINAL_REQUEST §R2 | VERIFIED |
| F9 | Multi-Faceted Filter Interface | Filter by college, upazila, academic stream, GPA range, and pass/fail status | M2 | ORIGINAL_REQUEST §R2 | VERIFIED |
| F10 | Analytics Dashboard | District summary KPIs, college pass rate rankings, GPA-5 counts, charts | M2 | ORIGINAL_REQUEST §R2 | VERIFIED |
| F11 | Responsive Viewport Layout | Full UI/UX responsiveness across mobile, tablet, and desktop viewports | M2 | ORIGINAL_REQUEST §AC | VERIFIED |
| F12 | Comprehensive E2E Test Suite | 5-Tier test suite covering data integrity, search, filter, analytics, and UI | M3 | Project Pattern Dual Track | VERIFIED |
| F13 | Adversarial Hardening & Audit | Tier 5 stress testing and forensic integrity audit verification | M4 | Project Pattern Phase 2 | VERIFIED |

---

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Data Ingestion & Persistence Pipeline | Fetch, parse, validate, and store all 24 college datasets & 5,065 student records | None | **DONE** |
| M2 | Results Dashboard Web Application | Build responsive frontend web app with search, filters, analytics, and charts | M1 | **DONE** |
| M3 | E2E Testing Suite (Tiers 1-4) | Build independent opaque-box E2E test suite and publish TEST_READY.md | In parallel with M1/M2 | **DONE** |
| M4 | Final Quality Gate & Forensic Audit | Pass 100% E2E tests, Tier 5 adversarial hardening, and Forensic Integrity Audit | M1, M2, M3 | **DONE** |
