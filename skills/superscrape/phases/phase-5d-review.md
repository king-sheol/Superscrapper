# Phase 5d: Report Review

## Pre-check

```bash
python -c "
import json, sys, os
choice = json.load(open('{output_dir}/_state/dashboard_choice.json'))['choice']
if choice == 'none':
    print('GATE OK'); sys.exit(0)
if choice in ('streamlit', 'both') and not os.path.exists('{output_dir}/dashboard.py'):
    print('GATE FAIL: dashboard.py missing'); sys.exit(1)
if choice in ('html', 'both') and not os.path.exists('{output_dir}/dashboard.html'):
    print('GATE FAIL: dashboard.html missing'); sys.exit(1)
print('GATE OK')
"
```

If GATE FAIL — return to previous phase.

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

## Save State

Write to `_state/phase5d_done.json`: `{ "reviewer_verdict": "Approved", "iterations": N }`
Update `.superscrape-session.json`: current_phase -> "phase-5e"