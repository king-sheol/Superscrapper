# Phase 5b: Dashboard Choice (MANDATORY)

**This phase is MANDATORY. Do not skip.**

## Pre-check

```bash
test -f {output_dir}/report.md && test -f {output_dir}/data.csv && test -f {output_dir}/data.xlsx && echo "GATE OK" || echo "GATE FAIL"
```

If GATE FAIL — return to previous phase.

## Instructions

### 1. Compute Complexity

Read `_state/normalized.json` and compute:

```
records = total_records count
columns = length of columns array

if records < 20 AND columns < 8  -> SIMPLE
if records < 50 AND columns < 12 -> MEDIUM
else                              -> COMPLEX
```

Save complexity to session JSON (`complexity` field).

### 2. Ask User

Use AskUserQuestion — do NOT skip this step, do NOT assume a choice:

```
Report and data are ready. Which dashboard to generate?
+-- Streamlit (for VPS) -- interactive, with filters and charts (Recommended)
+-- HTML (for GitHub Pages) -- static, fast loading
+-- Both options
+-- No dashboard -- report and Excel only
```

### 3. Save Choice

Save `{output_dir}/_state/dashboard_choice.json`:
```json
{"choice": "streamlit|html|both|none", "complexity": "SIMPLE|MEDIUM|COMPLEX"}
```

## Save State

Write to `_state/dashboard_choice.json`: choice + complexity
Update `.superscrape-session.json`: current_phase -> "phase-5c", complexity -> computed value

## Next

Read `phases/phase-5c-dashboard-generate.md` and continue.
