# Phase 6: Verify & Present Results

## Pre-check

Phase 5e must be in completed_phases:

```bash
cat {output_dir}/.superscrape-session.json
```

If "5e" is not in completed_phases, go back to Phase 5e.

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

### 4. Final Summary

Present the completion summary with: topic, total records, number of sources, file list, and deploy URL if applicable.

### 5. Clean Up Session

Delete the session file:
```bash
rm {output_dir}/.superscrape-session.json
```

## Done

All files verified. Phase 5 completion gate passed. Results presented to user.

Phase 6 complete.
