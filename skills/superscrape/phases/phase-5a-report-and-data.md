# Phase 5a: Generate Report & Data Files

## Pre-check

```bash
test -f {output_dir}/_state/normalized.json && echo "GATE OK" || echo "GATE FAIL"
```

If GATE FAIL — return to previous phase.

## Instructions

### 1. Dispatch Two Subagents in Parallel

Pass this metadata to BOTH agents:
- `topic`: from config.json
- `date`: collection date (YYYY-MM-DD)
- `output_dir`: path to output directory
- `headers`: column names from normalized.json
- `data`: all records from normalized.json
- `sources`: list of {url, reliability, justification}
- `analysis`: {leaders, patterns, anomalies, market_context}
- `confidence_map`: list of {source, level, reason}

**Agent 1 — report-writer** subagent:
- Generates `{output_dir}/report.md`
- Use format from `references/report-format.md`

**Agent 2 — dashboard-designer** subagent (mode: data-only):
- Generates `{output_dir}/data.csv` and `{output_dir}/data.xlsx`
- Use XLSX instructions from `references/xlsx-generator.md`

MUST use Agent tool. Do NOT generate these files directly in the main context.

### 2. Verify Output

```bash
test -f {output_dir}/report.md && test -f {output_dir}/data.csv && test -f {output_dir}/data.xlsx && echo "OK"
```

All three files must exist and be non-empty.

## Save State

Write to `_state/phase5a_done.json`: `{ "report": true, "csv": true, "xlsx": true }`
Update `_state/pipeline_metrics.json`:
- Increment `agent_dispatches` by 2 (report-writer + dashboard-designer data-only)
- Add `phase_timings.phase_5a`: `{ "started": "{ISO}", "ended": "{ISO}", "duration_sec": N }`
Update `.superscrape-session.json`: current_phase -> "phase-5b"

## Next

Read `phases/phase-5b-dashboard-choice.md` and continue.
