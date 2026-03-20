# Phase 4: Normalize, Validate & Analyze

## Pre-check

```bash
ls {output_dir}/_state/raw_data_*.json > /dev/null 2>&1 && echo "GATE OK" || echo "GATE FAIL"
```

If GATE FAIL — return to previous phase.

## Instructions

### 1. Load & Merge

Load all `_state/raw_data_*.json` files and merge into a single dataset. Track which records came from which source.

### 2. Defense-in-Depth Validation (5 Layers)

Apply validation layers sequentially:

**Layer 1 — Format**: Verify data types, encodings, units of measurement. Standardize formats (e.g., currency symbols, date formats, number separators).

**Layer 2 — Duplicates**: Deduplicate by key fields (name + source). When duplicates exist across sources:
- Keep the record from the **highest reliability source** (read `_state/sources.json` for reliability ratings)
- If same reliability: keep the **most complete record** (fewest N/A values)
- If tied: keep record from source with most total records (higher sample = more trustworthy)

**Layer 3 — Ranges**: Check that numbers fall within reasonable bounds. Flag dates outside expected range. Mark out-of-range values for review.

**Layer 4 — Cross-validation & Conflict Resolution**: For each entity (by name) found in 2+ sources, compare numeric values:
- If 3+ sources have the same entity: divergence >30% on any numeric field → flag as "conflicting data"
- If 2 sources have the same entity: divergence >50% → flag as "conflicting data"
- If fewer than 2 sources have overlapping entities → skip cross-validation, note in output: "Cross-validation not possible: insufficient source overlap"

**Conflict resolution strategy** (apply automatically, log decisions):
1. Read `_state/sources.json` to get reliability ratings for each source
2. For conflicting values, resolve by priority:
   - **High reliability source wins** over Medium/Low
   - If same reliability: **most recent data wins** (check collection date)
   - If same date and reliability: **use median** of all values
   - If only 2 values and both High reliability: **keep both as range** (e.g., "2490-2990")
3. Log ALL resolution decisions in conflicts array:

Save conflict flags in normalized.json under a "conflicts" key:
```json
{
  "conflicts": [
    {
      "entity": "Bitrix24",
      "field": "price",
      "values": {"hostinghub.ru": 2490, "vpsbenchmarks.com": 2990},
      "source_reliability": {"hostinghub.ru": "High", "vpsbenchmarks.com": "High"},
      "divergence": "20%",
      "resolution": "range",
      "resolved_value": "2490-2990"
    }
  ]
}
```

Show conflicts AND their resolutions to user in the Phase 4 checkpoint before proceeding.

**Layer 5 — Dead project detection**: For each entity, check if the source URL returned HTTP 404 during collection or if the latest activity date is >6 months old. If so, flag with `"possibly_dead": true` and add reason ("site 404" or "last activity >6mo").

### 3. Fill Gaps

Mark missing data as N/A with an explanation of why it is unavailable (source didn't have it, blocked, inconsistent across sources, etc.).

### 4. Quality Review (MANDATORY)

Dispatch **data-quality-reviewer** subagent. The reviewer checks:
- Completeness (% of cells filled) — **CRITICAL if overall fill rate < 75%**
- Per-column fill rate — **CRITICAL if any agreed column < 30% filled**
- Consistency (cross-source agreement)
- Source reliability (forums/social media flagged as low reliability)
- Anomalies (statistical outliers)
- Returns VERDICT: Approved or Issues Found

**Important**: Pass explicit fill rate thresholds to the reviewer:
"Overall fill rate must be >= 75% to approve. Any agreed column with < 30% fill → CRITICAL."

**If Issues Found**: Fix the flagged issues and re-dispatch the reviewer. Maximum 3 iterations.

**After 3 failed reviews**: If the reviewer still returns "Issues Found" after 3 iterations, use AskUserQuestion: "Quality review failed 3 times. Accept current data quality and proceed, or abort?" If user accepts, set `quality_review` to `"Accepted-with-issues"` and proceed. If abort, stop the pipeline.

Phase 4 is NOT complete until the reviewer returns **VERDICT: Approved** or user explicitly accepts.

### 5. Analyze

With clean data, perform analysis:
- Identify leaders and explain why they lead
- Find patterns across the data
- Flag anomalies and outliers with context
- Compare with market benchmarks where possible
- Assign confidence levels to each source: High / Medium / Low with justification

## Save State

Write to `_state/normalized.json`:
```json
{
  "topic": "...",
  "columns": ["..."],
  "column_types": {"Name": "string", "Price": "number"},
  "records": [...],
  "flags": {
    "conflicting_data": ["entity names with >30% divergence across 3+ sources"],
    "possibly_dead": ["entity names where source 404 or last activity >6mo"]
  },
  "analysis": {
    "leaders": [...],
    "patterns": [...],
    "anomalies": [...],
    "market_context": "..."
  },
  "quality_review": "Approved",
  "sources_used": [...],
  "total_records": 0,
  "collection_date": "YYYY-MM-DD"
}
```
Update `_state/pipeline_metrics.json`:
- Increment `agent_dispatches` by 1 (data-quality-reviewer) + re-dispatch count
- Add `phase_timings.phase_4`: `{ "started": "{ISO}", "ended": "{ISO}", "duration_sec": N }`
- Add `quality_gates.normalization`: `{ "fill_rate": X, "reviewer_verdict": "Approved|Issues Found", "reviewer_iterations": N, "conflicts_found": N, "conflicts_resolved": N }`
Update `.superscrape-session.json`: current_phase -> "phase-5a"

## Next

Read `phases/phase-5a-report-and-data.md` and continue.
