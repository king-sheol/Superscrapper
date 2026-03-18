# Phase 5d: Report Review

## Pre-check

Dashboard files must exist (or dashboard_choice = "none"):

```bash
cat {output_dir}/_state/dashboard_choice.json
```

If choice is not "none", verify the dashboard file(s) exist. If missing, go back to Phase 5c.

## Instructions

### Dispatch Report Reviewer

Dispatch **report-reviewer** subagent. The reviewer checks:
- All required sections present in report.md
- Numbers have context (good/bad, above/below market average)
- Insights are specific, not generic platitudes
- Data references match actual records
- Returns VERDICT: Approved or Issues Found

### Review Loop

**If VERDICT: Issues Found**:
1. Fix the flagged issues in report.md
2. Re-dispatch the report-reviewer
3. Maximum 3 iterations

Phase 5d is NOT complete until report-reviewer returns **VERDICT: Approved**.

Update `.superscrape-session.json` — add "5d" to completed_phases.

## Done

Report review passed (VERDICT: Approved).

Phase 5d complete.
