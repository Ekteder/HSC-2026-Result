# Narail Science Results Dashboard

An interactive, modern, minimalistic examination results analytics dashboard for **7 Science colleges in Narail** (HSC Examination 2026, Board of Intermediate and Secondary Education, Jashore).

Built with **HTML5**, **CSS3**, **Vanilla JavaScript**, and **Chart.js** (via CDN) — with zero frontend frameworks, backend, or database required.

---

## Project Structure

```text
narail-science-results/
│
├── index.html          # Main application layout & views
├── css/
│   └── style.css       # Complete responsive stylesheet
│
├── js/
│   ├── data.js         # Pre-processed & validated dataset (612 students across 7 colleges)
│   ├── dashboard.js    # Overview KPIs, doughnut & bar charts, sortable college table, quick insights
│   ├── students.js     # Complete 612-student database with search, filters, sorting, pagination & detail modal
│   ├── colleges.js     # Individual college cards & detailed college analytics dashboard
│   ├── subjects.js     # Subject-wise grade distribution analysis & cross-college subject comparisons
│   └── app.js          # Navigation controller, mobile drawer & topbar global quick search
│
└── README.md           # Project documentation & usage instructions
```

---

## How to Run the Website

### Option 1: Open Locally (No Server Required)
Because the 7 source JSON files have been parsed and compiled into a self-contained JavaScript dataset (`js/data.js`), you can run the dashboard directly from your filesystem:
1. Locate `index.html` in the project root folder.
2. Double-click `index.html` (or open it in Chrome, Firefox, Edge, or Safari).
3. Ensure you have an active internet connection so the **Chart.js CDN** and **Google Fonts** load properly.

### Option 2: Run with a Local Development Server
If you are running inside a development environment:
```bash
npm run dev
```
Then open `http://localhost:3000` in your browser.

---

## Dataset Summary & Validation

All **7 JSON source files** were inspected, parsed from their embedded HTML grade sheets (`table_info` and `table_result`), standardized, and validated:

| College Name | EIIN | Total Students | Passed | Failed | Absent | Pass Rate | GPA 5.00 |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Government Victoria College, Narail** | 118527 | 336 | 270 | 56 | 10 | 80.36% | 52 |
| **Gobra Mittra College** | 118528 | 26 | 15 | 8 | 3 | 57.69% | 0 |
| **Ballartop Ideal College** | 118523 | 18 | 10 | 7 | 1 | 55.56% | 0 |
| **Narail Govt. Mohila College** | 118525 | 76 | 35 | 35 | 6 | 46.05% | 0 |
| **Lohagara Govt. Adarsha College** | 118437 | 85 | 38 | 40 | 7 | 44.71% | 2 |
| **Maijpara College** | 118530 | 40 | 17 | 23 | 0 | 42.50% | 0 |
| **Abdul Hai City College** | 118526 | 31 | 8 | 22 | 1 | 25.81% | 0 |
| **All 7 Colleges Total** | — | **612** | **393** | **191** | **28** | **64.22%** | **54** |

### Data Processing Rules Enforced
- **Zero Invented Data**: Missing fields (such as Registration Numbers, which are blank in the source HTML) are explicitly displayed as `Not Available`.
- **Parent Names Preserved**: Every student's Father's Name and Mother's Name are extracted and searchable.
- **Result Categories**: `PASS`, `FAIL`, and `ABSENT` are strictly separated (`393 + 191 + 28 = 612`).
- **Missing Grades Exclusion**: Absent students without subject grades are never counted as `F` in subject statistics.
- **GPA Range Filtering**: Students without a numeric GPA (`FAIL` or `ABSENT`) are excluded from numeric GPA filter ranges.
