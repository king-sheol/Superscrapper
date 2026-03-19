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

5. **Audit:** Dispatch `dashboard-auditor` agent. If returns Issues → fix and re-audit (max 3 iterations).

This phase is NOT complete until dashboard-auditor returns Approved.

### Visual Preview

After audit is approved, show the user a description of what was generated (file list, key features, size).

## Save State

Write to `_state/phase5c_done.json`: `{ "dashboard_type": "...", "auditor_verdict": "Approved" }`
Update `.superscrape-session.json`: current_phase -> "phase-5d"

## Next

Read `phases/phase-5d-review.md` and continue.
