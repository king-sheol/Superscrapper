# Phase 5d: Report Review

## Pre-check

```bash
choice=$(python -c "import json; print(json.load(open('{output_dir}/_state/dashboard_choice.json'))['choice'])" 2>/dev/null)
if [ "$choice" = "none" ] || [ -f {output_dir}/dashboard.py ] || [ -f {output_dir}/dashboard.html ]; then echo "GATE OK"; else echo "GATE FAIL: dashboard files missing for choice=$choice"; fi
```

If GATE FAIL — go back to Phase 5c.

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
