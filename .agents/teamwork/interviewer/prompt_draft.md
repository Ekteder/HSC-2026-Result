Run multiple sub agents in parallel to make it efficient and quick to fetch and present all HSC 2026 college-wise and individual student results for Narail District under Jessore Board, and create a comprehensive results web application for students.

Working directory: /media/sanglap/Movies/2026results/narail_results_app
Integrity mode: development

## Requirements

### R1. Narail District HSC 2026 Result Ingestion
Identify all college EIIN numbers in Narail District that participated in the HSC Examination 2026 under Jessore Board. Fetch college-wise result sheets using the Jessore Board college result endpoint (`https://www.jessoreboard.gov.bd/resultjbh26/result_sheet.php?eiin={eiin}`), and query individual student results across all academic streams (Science, Humanities, Business Studies) using the individual result endpoint (`POST https://www.jessoreboard.gov.bd/resultjbh26/result.php` with `roll={roll}&regno={regno}`). Parse and save all student result records into college-wise JSON files.

### R2. Comprehensive Results Dashboard Web Application
Build a comprehensive result-viewing web application inside the designated working directory, using either plain HTML/CSS/JS or a modern frontend framework with pnpm. The application must feature responsive UI/UX across mobile, tablet, and desktop viewports, with fast individual student search, multi-faceted filtering, and performance analytics across colleges and streams.

## Acceptance Criteria

### Data Extraction and Persistence
- [ ] EIINs for all HSC 2026 participating colleges in Narail District under Jessore Board are identified and documented.
- [ ] Complete college-wise JSON files are generated and stored with valid JSON syntax.
- [ ] Each student entry includes roll number, registration number (if available), GPA, subject grades, and result status for Science, Humanities, and Business Studies streams.
- [ ] Data extraction validates that record counts match the college-wise summary sheets.

### Web Application Features and Responsiveness
- [ ] Application starts and runs locally without errors.
- [ ] Search interface allows looking up individual student results by roll number and registration number.
- [ ] Filter interface allows filtering student records by college, academic stream, GPA range, and pass/fail status.
- [ ] Dashboard displays analytical statistics including college pass rates, GPA-5 counts, and stream distributions.
- [ ] Layout renders correctly and is usable across mobile, tablet, and desktop viewports.
