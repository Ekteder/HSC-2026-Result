# Dispatch: Narail College EIIN Researcher (survey_explorer_2)

## Identity
- Role: Narail College EIIN Researcher
- Working directory: /media/sanglap/Movies/2026results/.agents/teamwork/survey_explorer_2
- Parent Conversation ID: f13e071e-3fd2-420f-b1f5-be3a288800ea

## Objective
Identify and exhaustively enumerate all college EIIN numbers in Narail District that participated in the HSC Examination 2026 under Jessore Board.

## Mandatory Reading
- Read `/media/sanglap/Movies/2026results/.agents/teamwork/ORIGINAL_REQUEST.md` before starting.

## Specific Tasks
1. Search and identify all colleges in Narail District (Narail Sadar, Lohagara, Kalia Upazilas).
   - Use web search, Jessore Board institution directories, BANBEIS, Ministry of Education, or district administration portals.
2. For every candidate EIIN, verify whether it participated in HSC 2026 by testing the Jessore Board college result endpoint:
   `https://www.jessoreboard.gov.bd/resultjbh26/result_sheet.php?eiin={eiin}`
   - Does it return an active HSC 2026 result sheet with students?
   - Or does it return "No Result Found" / empty sheet?
3. Compile a definitive list of participating Narail District colleges including:
   - EIIN number
   - College Name
   - Upazila / Thana (Narail Sadar, Lohagara, Kalia)
   - Participating streams (Science, Humanities, Business Studies)
   - Approximate student count (total appeared / passed from result sheet header)
4. Check for any colleges that may have been recently established or have alternate EIINs to ensure zero omission.

## Outputs
- Update your `progress.md` regularly with `Last visited: [timestamp]`.
- Write detailed inventory to `/media/sanglap/Movies/2026results/.agents/teamwork/survey_explorer_2/narail_colleges_report.md`.
- Write your final handoff to `/media/sanglap/Movies/2026results/.agents/teamwork/survey_explorer_2/handoff.md`.
- Send a completion message to parent upon finishing.


## 2026-11-01T12:32:28Z
You are survey_explorer_2, the Narail College EIIN Researcher.
Your working directory is: /media/sanglap/Movies/2026results/.agents/teamwork/survey_explorer_2
Your parent orchestrator conversation ID is: f13e071e-3fd2-420f-b1f5-be3a288800ea

MANDATORY FIRST STEP:
Read /media/sanglap/Movies/2026results/.agents/teamwork/ORIGINAL_REQUEST.md and /media/sanglap/Movies/2026results/.agents/teamwork/survey_explorer_2/DISPATCH.md.

Objective:
Identify and exhaustively enumerate all college EIIN numbers in Narail District (Narail Sadar, Lohagara, Kalia Upazilas) that participated in the HSC Examination 2026 under Jessore Board.
Use tools (web search, Jessore Board institution directories, banbeis/education directories, test queries against https://www.jessoreboard.gov.bd/resultjbh26/result_sheet.php?eiin={eiin}) to verify that each college has active HSC 2026 examination results.

Document for each college:
- EIIN
- College Name
- Upazila/Thana
- Participating streams (Science, Humanities, Business Studies)
- Summary statistics (appeared, passed, failed, GPA 5 count) from the result sheet.

Maintain your progress.md with timestamps.
When complete, write your comprehensive report to:
/media/sanglap/Movies/2026results/.agents/teamwork/survey_explorer_2/narail_colleges_report.md
and write your handoff to:
/media/sanglap/Movies/2026results/.agents/teamwork/survey_explorer_2/handoff.md
Send a completion message back to f13e071e-3fd2-420f-b1f5-be3a288800ea.
