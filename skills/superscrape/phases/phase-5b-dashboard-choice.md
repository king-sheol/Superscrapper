# Phase 5b: Dashboard Choice (MANDATORY)

## Pre-check

```bash
test -f {output_dir}/report.md && test -f {output_dir}/data.csv && test -f {output_dir}/data.xlsx && echo "GATE OK" || echo "GATE FAIL: report/data files missing"
```

If GATE FAIL — go back to Phase 5a.

## Instructions

Use AskUserQuestion — do NOT skip this step, do NOT assume a choice:

```
Report and data are ready. Which dashboard to generate?
├── Streamlit (for VPS) — interactive, with filters and charts (Recommended)
├── HTML (for GitHub Pages) — static, fast loading
├── Both options
└── No dashboard — report and Excel only
```

Save `{output_dir}/_state/dashboard_choice.json`:
```json
{"choice": "streamlit" | "html" | "both" | "none"}
```

Update `.superscrape-session.json` — add "5b" to completed_phases.

## Done

User's dashboard choice saved.

Phase 5b complete.
