# Phase 5c: Generate Dashboard

## Pre-check

```bash
test -f {output_dir}/_state/dashboard_choice.json && echo "GATE OK" || echo "GATE FAIL"
```

If GATE FAIL — return to previous phase.

## Instructions

### If choice = "none"

Skip dashboard generation entirely. Mark phase complete and proceed.

### Dashboard Generation (base+assembly pattern)

1. Read `_state/dashboard_choice.json` → get choice (streamlit/html/both/none)

2. **Complexity check:**
   - Count rows in data.csv → records
   - Count columns → columns
   - If records >= 50 OR columns >= 12 → COMPLEX
     - Try dispatch `dashboard-art-director` agent → get creative brief
     - If art-director not available → proceed without brief (MEDIUM fallback)
   - Else → SIMPLE/MEDIUM

3. **For Streamlit (choice = "streamlit" or "both"):**
   a. Copy `skills/superscrape/references/dashboard-streamlit-base.py` to `{output_dir}/dashboard.py`
   b. Dispatch `dashboard-designer` agent with prompt:
      "Read `dashboard-streamlit-assembly.md` and follow the steps to customize the base template.
       Output dir: {output_dir}. Topic: {topic}. Data: {output_dir}/data.csv."
      If COMPLEX: also pass the art-director's creative brief.

4. **For HTML (choice = "html" or "both"):**
   a. Copy `skills/superscrape/references/dashboard-html-base.html` to `{output_dir}/dashboard.html`
   b. Dispatch `dashboard-designer` agent with prompt:
      "Read `dashboard-html-assembly.md` and follow the steps to customize the base template.
       Output dir: {output_dir}. Topic: {topic}. Data: {output_dir}/data.csv."

5. **Audit:** Dispatch `dashboard-auditor` agent with explicit instructions:
   - "Run the FULL code audit checklist from your prompt. Pay special attention to:
     (a) No hidden columns — ALL collected data must be accessible to the user
     (b) No hardcoded column limits (e.g., `[:8]`)
     (c) No raw HTML tags in table cells — check JsCode/cellRenderer output
     (d) Default filter state must show ALL records, not a subset
     (e) Filter logic must use exact match for boolean fields
     (f) Footer date must be dynamic, not hardcoded
     (g) Count `!important` in CSS — flag if >5
     Reject if ANY critical check fails."
   - If returns Issues → fix and re-audit (max 3 iterations).

This phase is NOT complete until dashboard-auditor returns Approved.

### Smoke Tests (MANDATORY — run BEFORE audit)

Run these automated checks. ALL must pass before dispatching auditor:

**For Streamlit:**
```bash
# 1. Syntax check
python -c "import ast; ast.parse(open('{output_dir}/dashboard.py', encoding='utf-8').read()); print('SYNTAX OK')"

# 2. Import check (catches missing dependencies)
python -c "
import sys; sys.path.insert(0, '{output_dir}')
# Verify no raw HTML string patterns in cellRenderer
import re
code = open('{output_dir}/dashboard.py', encoding='utf-8').read()
if 'cellRenderer' in code and '<span' in code:
    print('FAIL: raw HTML in cellRenderer — use cellStyle instead')
    sys.exit(1)
if 'hidden' in code and 'COLUMNS' in code and '\"hidden\"' in code:
    print('FAIL: COLUMNS has hidden key — use detail_only')
    sys.exit(1)
if re.search(r'visible_cols\[:\d+\]', code):
    print('FAIL: hardcoded column limit found')
    sys.exit(1)
print('PATTERN CHECK OK')
"

# 3. Data load check
python -c "
import pandas as pd
df = pd.read_csv('{output_dir}/data.csv', encoding='utf-8-sig')
print(f'DATA OK: {len(df)} rows, {len(df.columns)} cols')
"
```

**For HTML:**
```bash
# 1. File not empty
test -s {output_dir}/dashboard.html && echo "HTML EXISTS OK"

# 2. Basic structure check
python -c "
html = open('{output_dir}/dashboard.html', encoding='utf-8').read()
checks = [
    ('</html>' in html, 'closing html tag'),
    ('echarts' in html.lower(), 'ECharts library'),
    ('ag-grid' in html.lower() or 'agGrid' in html, 'AG Grid library'),
    ('allData' in html and '[]' not in html.split('allData')[1][:5], 'data injected'),
]
failed = [name for ok, name in checks if not ok]
if failed:
    print(f'FAIL: missing {failed}')
    exit(1)
print('HTML STRUCTURE OK')
"
```

If ANY smoke test fails → fix the issue BEFORE dispatching auditor. Do not waste auditor iterations on code that doesn't even parse.

### Visual Preview

After audit is approved, show the user a description of what was generated (file list, key features, size).

## Save State

Write to `_state/phase5c_done.json`: `{ "dashboard_type": "...", "auditor_verdict": "Approved" }`
Update `_state/pipeline_metrics.json`:
- Increment `agent_dispatches` by N (art-director? + designer(s) + auditor × iterations)
- Add `phase_timings.phase_5c`: `{ "started": "{ISO}", "ended": "{ISO}", "duration_sec": N }`
- Add `quality_gates.dashboard`: `{ "smoke_tests_passed": N, "smoke_tests_total": M, "auditor_verdict": "Approved", "auditor_iterations": K }`
- Add `smoke_tests`: `{ "syntax": "OK|FAIL", "pattern_check": "OK|FAIL", "data_load": "OK|FAIL", "html_structure": "OK|FAIL" }`
Update `.superscrape-session.json`: current_phase -> "phase-5d"

## Next

Read `phases/phase-5d-review.md` and continue.
