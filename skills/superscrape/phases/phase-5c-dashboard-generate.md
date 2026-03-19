# Phase 5c: Generate Dashboard

## Pre-check

```bash
test -f {output_dir}/_state/dashboard_choice.json && echo "GATE OK" || echo "GATE FAIL"
```

If GATE FAIL — return to previous phase.

## Instructions

### If choice = "none"

Skip dashboard generation entirely. Mark phase complete and proceed.

### Complexity Branching

Read `complexity` from `_state/dashboard_choice.json` or session JSON.

**COMPLEX** (records >= 50 OR columns >= 12):
1. Dispatch **art-director** subagent first — produce a design brief with layout, color scheme, chart types, and interaction patterns
2. If art-director fails or returns empty: fall back to MEDIUM pipeline below
3. Pass the art-director brief to **dashboard-designer** subagent along with data

**MEDIUM** or **SIMPLE** (or COMPLEX fallback):
1. Dispatch **dashboard-designer** subagent directly with data and standard templates

### If choice = "streamlit" or "both"

Dispatch **dashboard-designer** subagent (type: streamlit):
- Generates: `dashboard.py`, `Dockerfile`, `docker-compose.yml`, `nginx.conf`, `requirements.txt`
- Use templates from `references/design-rules.md`
- Verify syntax: `python -c "import ast; ast.parse(open('{output_dir}/dashboard.py').read()); print('OK')"`

### If choice = "html" or "both"

Dispatch **dashboard-designer** subagent (type: html):
- Generates: `dashboard.html` (self-contained with embedded data, interactive filters, search, sorting)
- Use templates from `references/design-rules.md`
- Verify: file exists and is non-empty

### If choice = "both"

Run both subagents in parallel.

### Visual Audit

After dashboard-designer completes, dispatch the `dashboard-auditor` subagent:

Prompt: "Audit the dashboard at {output_dir}/dashboard.html (and/or dashboard.py). Read the design rules at ${CLAUDE_PLUGIN_ROOT}/skills/superscrape/references/design-rules.md first. Output dir: {output_dir}"

If VERDICT: Issues Found -- dashboard-auditor fixes them and re-audits (max 3 iterations).
If VERDICT: Approved -- proceed.

This phase is NOT complete until dashboard-auditor returns Approved.

### Visual Preview

After audit is approved, show the user a description of what was generated (file list, key features, size).

## Save State

Write to `_state/phase5c_done.json`: `{ "dashboard_type": "...", "auditor_verdict": "Approved" }`
Update `.superscrape-session.json`: current_phase -> "phase-5d"

## Next

Read `phases/phase-5d-review.md` and continue.
