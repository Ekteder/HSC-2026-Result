# Dispatch: Milestone 1 Data Ingestion Worker (worker_ingestion_1)

## Identity
- Role: Data Ingestion & Persistence Specialist
- Working directory: /media/sanglap/Movies/2026results/.agents/teamwork/worker_ingestion_1
- Parent Conversation ID: f13e071e-3fd2-420f-b1f5-be3a288800ea

## Mandatory Reading
- Read `/media/sanglap/Movies/2026results/.agents/teamwork/ORIGINAL_REQUEST.md` before starting.
- Read `/media/sanglap/Movies/2026results/.agents/teamwork/orchestrator/PROJECT.md`.
- Read `/media/sanglap/Movies/2026results/.agents/teamwork/survey_spec_miner_1/spec_report.md` (Contains exact endpoint schemas and parsing logic).
- Read `/media/sanglap/Movies/2026results/.agents/teamwork/survey_explorer_2/narail_colleges_hsc2026.json` and `narail_colleges_report.md` (Contains the 24 colleges and roll numbers).

## Write Ownership
You exclusively own:
- `/media/sanglap/Movies/2026results/narail_results_app/scripts/`
- `/media/sanglap/Movies/2026results/narail_results_app/data/`
- `/media/sanglap/Movies/2026results/narail_results_app/public/data/`
Do NOT edit files outside these paths.

## Mandatory Integrity Warning
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## Objective & Tasks
1. Write a resilient, high-throughput Python ingestion pipeline:
   - Read the 24 Narail college EIINs from `/media/sanglap/Movies/2026results/.agents/teamwork/survey_explorer_2/narail_colleges_hsc2026.json`.
   - Fetch the college result sheet for each EIIN (`https://www.jessoreboard.gov.bd/resultjbh26/result_sheet.php?eiin={eiin}`).
   - Extract all candidate rolls across Science, Humanities, and Business Studies streams.
   - For every student roll, query `POST https://www.jessoreboard.gov.bd/resultjbh26/result.php` with `roll={roll}&regno=` using multi-threaded concurrency (recommended 12-16 workers with retry and backoff) to fetch the student profile (Name, Father, Mother, Session, Type, GPA, Result Status) and all individual subject grades.
2. Structure and save the data:
   - Save college-wise JSON files in `/media/sanglap/Movies/2026results/narail_results_app/public/data/colleges/{eiin}.json` and `/media/sanglap/Movies/2026results/narail_results_app/data/colleges/{eiin}.json`.
   - Save consolidated dataset in `narail_all_students.json`.
   - Save metadata manifest in `manifest.json`.
   - Save rapid search lookup in `roll_lookup.json`.
3. Validation:
   - Validate that all 24 colleges are generated.
   - Verify that all student entries include roll, registration number (or empty string/Not Available), GPA, subject grades, and result status.
   - Reconcile exact counts: 5,065 total students, 1,776 passed, 105 GPA-5.00 achievers across Science (815), Humanities (3,748), and Business Studies (502).
   - Write and run a standalone validation script `validate_dataset.py` that verifies 100% data integrity.

## Outputs
- Update your `progress.md` regularly with `Last visited: [timestamp]`.
- Write your final handoff to `/media/sanglap/Movies/2026results/.agents/teamwork/worker_ingestion_1/handoff.md` with verification commands and output.
- Send a completion message to parent upon finishing.
