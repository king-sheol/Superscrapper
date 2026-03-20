# Phase 6: Verify & Present Results

## Pre-check

```bash
test -f {output_dir}/_state/phase5e_done.json && echo "GATE OK" || echo "GATE FAIL"
```

If GATE FAIL — return to previous phase.

## Instructions

### 1. Verify All Output Files

Run these checks — ALL must pass:

```bash
# Report exists and is non-empty
test -s {output_dir}/report.md && echo "report.md OK"

# CSV parses without errors (explicit encoding for Windows compatibility)
python -c "import csv; r=csv.reader(open('{output_dir}/data.csv', encoding='utf-8-sig')); print(f'{sum(1 for _ in r)-1} rows')"

# XLSX is valid
python -c "import openpyxl; wb=openpyxl.load_workbook('{output_dir}/data.xlsx'); print(f'{wb.sheetnames}')"
```

If dashboard was generated:
```bash
# Streamlit syntax check
python -c "import ast; ast.parse(open('{output_dir}/dashboard.py').read()); print('OK')"

# HTML exists and is non-empty
test -s {output_dir}/dashboard.html && echo "dashboard.html OK"
```

If deployed:
```bash
# URL returns 200
curl -s -o /dev/null -w "%{http_code}" {deploy_url}
```

### 1b. Visual Verification of ALL Deploy URLs (REQUIRED)

**The orchestrator does NOT have preview tools.** Dispatch `dashboard-auditor` agent for visual verification.

Prompt for auditor:
"Verify deployed dashboards visually. URLs: {deploy_urls from phase5e_done.json}.
For each URL:
1. Use preview_start (for localhost) or curl + code review (for remote URLs)
2. Check: page loads, data table populated, charts render, no raw HTML tags in cells, Russian text OK, all resources load
3. GitHub Pages: verify CDN scripts load (no CORS/mixed content), data embedded in HTML, no 404 template
4. Streamlit on VPS: warn if no auth configured
5. Take at least ONE screenshot per dashboard
Return VERDICT: Approved or Issues Found with specifics."

If auditor returns Issues Found → report as CRITICAL in final summary.
If auditor cannot reach remote URLs (no preview tools for remote) → use curl to check HTTP 200:
```bash
curl -s -o /dev/null -w "%{http_code}" {deploy_url}
```
And state: "Visual verification of remote URL done by HTTP check only. Manual visual check recommended at: {url}"

### 2. Phase 5 Completion Gate

Confirm ALL of these are true:
- Phase 5b was executed (dashboard choice was asked)
- Phase 5d was executed (report review returned Approved)
- Phase 5e was executed (deploy completed or explicitly skipped)

If ANY are missing — go back and complete them. Do NOT present results with incomplete phases.

### 3. Present Evidence to User

Show:
- First 3 rows of the data table
- File list with sizes
- Deploy URL (if applicable)

### 4. Pipeline Metrics Summary

Update `_state/pipeline_metrics.json` → add `completed_at: "{ISO}"` and compute `total_duration_sec`.

Read and present to user:
```
📊 Pipeline Metrics:
- Duration: {total_duration_sec}s ({started_at} → {completed_at})
- Agent dispatches: {agent_dispatches} (scrapers: N, report: 1, designer: M, auditor: K)
- Records: {total_records} from {source_count} sources
- Fill rate: {fill_rate}%
- Quality gates: reviewer={verdict}, auditor={verdict} (iterations: N)
- Smoke tests: {passed}/{total} passed
```

### 5. Generate README.md

Create `{output_dir}/README.md` using the Write tool. Include these sections:

1. **Title**: `# {Topic} — Data Collection Report`
2. **Metadata**: Date, record count, source count, generator version
3. **Files table**: list each output file with description (report.md, data.csv, data.xlsx, dashboard.html, dashboard.py — only files that actually exist)
4. **How to Use**: For HTML: "Open dashboard.html in any browser." For Streamlit: "pip install -r requirements.txt && streamlit run dashboard.py"
5. **Data Format**: encoding (UTF-8 with BOM), column list, N/A convention
6. **Sources**: list with URLs and reliability ratings from sources.json
7. **Deployed At**: deploy URLs from phase5e_done.json, or "Not deployed"

Only include sections relevant to the actual output. Write the file directly — do NOT use a template with nested code fences.

### 6. Final Summary

Present the completion summary with: topic, total records, number of sources, file list, deploy URL if applicable, and security warnings for public deployments.

## Save State

**DELETE** `.superscrape-session.json` — only incomplete sessions should persist on disk:
```bash
rm {output_dir}/.superscrape-session.json
```