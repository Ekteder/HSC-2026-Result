# Dispatch: Jessore Board API Spec Miner (survey_spec_miner_1)

## Identity
- Role: Jessore Board API Spec Miner
- Working directory: /media/sanglap/Movies/2026results/.agents/teamwork/survey_spec_miner_1
- Parent Conversation ID: f13e071e-3fd2-420f-b1f5-be3a288800ea

## Objective
Thoroughly probe and document the specifications, request/response formats, data structures, and behaviors of the Jessore Board HSC 2026 result endpoints:
1. College-wise result sheet endpoint: `https://www.jessoreboard.gov.bd/resultjbh26/result_sheet.php?eiin={eiin}`
2. Individual student result endpoint: `POST https://www.jessoreboard.gov.bd/resultjbh26/result.php` with `roll={roll}&regno={regno}`

## Mandatory Reading
- Read `/media/sanglap/Movies/2026results/.agents/teamwork/ORIGINAL_REQUEST.md` before starting.

## Specific Tasks
1. Test live network requests to `https://www.jessoreboard.gov.bd/resultjbh26/result_sheet.php?eiin={eiin}` using sample valid EIINs (e.g. from Jessore/Narail board colleges such as Narail Victoria College 118437 or others). Inspect the raw HTML structure. Document how the college name, summary stats, student roll numbers, GPA, stream (Science, Humanities, Business Studies), and pass/fail indicators are encoded.
2. Test live requests to `POST https://www.jessoreboard.gov.bd/resultjbh26/result.php` with sample roll and regno. Inspect HTML or JSON response. Document:
   - What fields are returned (Student Name, Father's Name, Mother's Name, College Name, Roll, Reg No, Group/Stream, GPA, Subject-wise Grades/Marks).
   - What headers/cookies/CSRF tokens (if any) are required.
   - What is returned when invalid or missing roll/regno is supplied.
   - What is returned if regno is omitted or empty.
3. Investigate endpoint rate limits, timeout thresholds, concurrency limits, and retry recommendations.
4. Formulate the parsing schema: regex or DOM parsing selectors for extracting all required fields.

## Outputs
- Update your `progress.md` regularly with `Last visited: [timestamp]`.
- Write detailed findings to `/media/sanglap/Movies/2026results/.agents/teamwork/survey_spec_miner_1/spec_report.md`.
- Write your final handoff to `/media/sanglap/Movies/2026results/.agents/teamwork/survey_spec_miner_1/handoff.md`.
- Send a completion message to parent upon finishing.


## 2026-11-01T12:32:17Z
You are survey_spec_miner_1, the Jessore Board API Spec Miner.
Your working directory is: /media/sanglap/Movies/2026results/.agents/teamwork/survey_spec_miner_1
Your parent orchestrator conversation ID is: f13e071e-3fd2-420f-b1f5-be3a288800ea

MANDATORY FIRST STEP:
Read /media/sanglap/Movies/2026results/.agents/teamwork/ORIGINAL_REQUEST.md and /media/sanglap/Movies/2026results/.agents/teamwork/survey_spec_miner_1/DISPATCH.md.

Objective:
Investigate and document the exact request and response specifications for:
1. College-wise result sheet: https://www.jessoreboard.gov.bd/resultjbh26/result_sheet.php?eiin={eiin}
2. Individual student result: POST https://www.jessoreboard.gov.bd/resultjbh26/result.php with roll={roll}&regno={regno}

Test live requests using curl or python to inspect the actual response payloads from Jessore Board (e.g. test with sample EIINs from Jessore/Narail board colleges such as Narail Victoria College 118437, Narail Govt City College 118438, etc.).
Document the exact HTML/JSON structure, fields, tables, student roll lists, GPA format, stream separation (Science, Humanities, Business Studies), subject codes and grade mappings, rate limits, and failure responses.

Maintain your progress.md with timestamps.
When complete, write your comprehensive spec report to:
/media/sanglap/Movies/2026results/.agents/teamwork/survey_spec_miner_1/spec_report.md
and write your handoff to:
/media/sanglap/Movies/2026results/.agents/teamwork/survey_spec_miner_1/handoff.md
Send a completion message back to f13e071e-3fd2-420f-b1f5-be3a288800ea.
