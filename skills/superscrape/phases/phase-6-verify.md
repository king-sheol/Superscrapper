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

# CSV parses without errors
python -c "import csv; r=csv.reader(open('{output_dir}/data.csv')); print(f'{sum(1 for _ in r)-1} rows')"

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

For EACH URL in `phase5e_done.json` → `deploy_urls[]`:

1. **Open the URL** using preview tools (preview_start for localhost, or navigate to remote URL)
2. **Take screenshot** of the rendered dashboard
3. **Check for**:
   - Page loads without errors (no blank page, no 404, no Python traceback)
   - Data table is visible and populated (not empty)
   - Charts render (not blank containers)
   - No raw HTML tags visible in table cells (e.g., literal `<span>` text)
   - Russian text displays correctly (not mojibake/replacement characters)
   - All resources load (CSS, JS — no broken styles from wrong paths)
4. **GitHub Pages specific**:
   - Check that relative paths work (CSS/JS/fonts load correctly without server-side routing)
   - Verify ECharts and AG Grid CDN scripts load (not blocked by CORS or mixed content)
   - Check page doesn't show GitHub 404 template
   - Verify data is embedded in HTML (not loaded from external file that won't exist on GH Pages)
5. **Streamlit on VPS specific**: warn if no authentication is configured (open to public internet)
6. **Both**: take at least ONE screenshot per deployed dashboard and describe what you see to the user

If ANY visual check fails → report as CRITICAL issue in final summary. Do NOT silently approve.

If preview tools are unavailable, explicitly state: "Visual verification SKIPPED — preview tools unavailable. Manual check recommended at: {url}"

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

## Next

Pipeline complete. No next phase.
