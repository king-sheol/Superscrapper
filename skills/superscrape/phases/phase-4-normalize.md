# Phase 4: Normalize, Validate & Analyze

## Pre-check

```bash
ls {output_dir}/_state/raw_data_*.json
```

Must find at least one raw data file. If none exist, go back to Phase 3.

## Instructions

### 1. Load & Merge

Load all `_state/raw_data_*.json` files and merge into a single dataset. Track which records came from which source.

### 2. Defense-in-Depth Validation (4 Layers)

Apply validation layers sequentially:

**Layer 1 — Format**: Verify data types, encodings, units of measurement. Standardize formats (e.g., currency symbols, date formats, number separators).

**Layer 2 — Duplicates**: Deduplicate by key fields (name + source). Keep the most complete record when duplicates exist across sources.

**Layer 3 — Ranges**: Check that numbers fall within reasonable bounds. Flag dates outside expected range. Mark out-of-range values for review.

**Layer 4 — Cross-check**: Compare data from different sources. If 3+ sources report the same field with >30% discrepancy, flag for manual review. Note which source values are most likely correct.

### 3. Fill Gaps

Mark missing data as N/A with an explanation of why it is unavailable (source didn't have it, blocked, inconsistent across sources, etc.).

### 4. Quality Review (MANDATORY)

Dispatch **data-quality-reviewer** subagent. The reviewer checks:
- Completeness (% of cells filled)
- Consistency (cross-source agreement)
- Anomalies (statistical outliers)
- Returns VERDICT: Approved or Issues Found

**If Issues Found**: Fix the flagged issues and re-dispatch the reviewer. Maximum 3 iterations. Phase 4 is NOT complete until the reviewer returns **VERDICT: Approved**.

### 5. Analyze

With clean data, perform analysis:
- Identify leaders and explain why they lead
- Find patterns across the data
- Flag anomalies and outliers with context
- Compare with market benchmarks where possible
- Assign confidence levels to each source: High / Medium / Low with justification

### 6. Save State

Write `{output_dir}/_state/normalized.json`:
```json
{
  "topic": "...",
  "columns": ["..."],
  "column_types": {"Name": "string", "Price": "number", ...},
  "records": [...],
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

Update `.superscrape-session.json` — add 4 to completed_phases.

## Done

Data normalized, validated (quality review Approved), and analyzed.

Phase 4 complete.
