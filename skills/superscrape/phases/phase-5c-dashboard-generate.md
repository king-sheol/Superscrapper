# Phase 5c: Generate Dashboard

## Pre-check

```bash
cat {output_dir}/_state/dashboard_choice.json > /dev/null 2>&1 && echo "GATE OK" || echo "GATE FAIL: dashboard_choice.json missing"
```

If GATE FAIL — go back to Phase 5b.

## Instructions

### If choice = "none"

Skip dashboard generation entirely. Mark phase complete and proceed.

### If choice = "streamlit" or "both"

Dispatch **dashboard-generator** subagent (mode: dashboard-only, type: streamlit):
- Generates: `dashboard.py`, `Dockerfile`, `docker-compose.yml`, `nginx.conf`, `requirements.txt`
- Use templates from `references/dashboard-template.md`
- Verify syntax: `python -c "import ast; ast.parse(open('{output_dir}/dashboard.py').read()); print('OK')"`

### If choice = "html" or "both"

Dispatch **dashboard-generator** subagent (mode: dashboard-only, type: html):
- Generates: `dashboard.html` (self-contained with embedded data, interactive filters, search, sorting)
- Use templates from `references/dashboard-template.md`
- Verify: file exists and is non-empty

### If choice = "both"

Run both subagents in parallel.

### Visual Audit

After dashboard-generator completes, dispatch the `dashboard-auditor` subagent:

Prompt: "Audit the dashboard at {output_dir}/dashboard.html (and/or dashboard.py). Read the design system at ${CLAUDE_PLUGIN_ROOT}/skills/superscrape/references/design-system.md first. Output dir: {output_dir}"

If VERDICT: Issues Found -- dashboard-auditor fixes them and re-audits (max 3 iterations).
If VERDICT: Approved -- proceed to Phase 5d.

This phase is NOT complete until dashboard-auditor returns Approved.

### Visual Preview

After audit is approved, show the user a description of what was generated (file list, key features, size).

## Update Session

Update `.superscrape-session.json`: set `current_phase` to `"phase-5d"`, add `"phase-5c"` to `completed_phases`.

## Done

Dashboard files generated (or skipped if choice=none).

Phase 5c complete.
