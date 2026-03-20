# Phase 1: Accept Task & Clarify Columns

## Pre-check

```bash
firecrawl --status 2>&1 | grep -q "Authenticated" && echo "GATE OK" || echo "GATE FAIL"
```

If GATE FAIL — return to previous phase.

## Instructions

### 1. Parse User Request

Identify from the user's message:
- **Topic**: what to research
- **Scope**: how many items, geography, time period
- **Data type**: rating/comparison, price monitoring, market research, competitor analysis

### 1b. Topic Complexity Pre-assessment (advisory)

After parsing the topic, quickly assess scope:

| Signal | Complexity | Action |
|--------|-----------|--------|
| Specific niche (e.g., "VPS hosting in Russia under $50/mo") | Low | Proceed normally |
| Broad category (e.g., "cloud hosting") | Medium | Suggest narrowing: geography, price range, or segment |
| Very broad (e.g., "SaaS tools" or "all hosting providers") | High | Warn: "This topic is very broad. Recommend narrowing to a specific segment for better data quality." |

This is advisory — the user can proceed with any scope.

### 2. Propose Columns

Three columns are always mandatory:
- Name (object/entity name)
- Source URL
- Collection Date

Propose additional topic-specific columns based on data type:
- Rating/comparison: price, rating, features, pros/cons
- Price monitoring: current price, historical price, discount, availability
- Market research: market share, revenue, growth rate, geography
- Competitor analysis: pricing, features, target audience, strengths/weaknesses

### 3. Confirm with User

Use AskUserQuestion to present the proposed columns and get confirmation. Let the user add, remove, or modify columns before proceeding.

**Important**: Present columns in two tiers:
- **Core columns** (always collectible): Name, Source URL, Collection Date, Price, Rating — these are almost always available
- **Extended columns** (may have gaps): specific features, SLA, support details — warn user: "These columns may not be available from all sources, resulting in partial data (N/A values)."

This sets realistic expectations about fill rate before data collection begins.

### 4. Create Output Directory & Save State

```bash
mkdir -p {output_dir}/_state
mkdir -p {output_dir}/.firecrawl
```

Where `{output_dir}` = `output/YYYY-MM-DD-{topic-slug}` (topic in lowercase, spaces to hyphens).

Write `{output_dir}/_state/config.json`:
```json
{
  "topic": "...",
  "data_type": "...",
  "columns": ["Name", "Source URL", "Collection Date", ...],
  "scope": "..."
}
```

Write `{output_dir}/.superscrape-session.json`:
```json
{
  "version": 4,
  "output_dir": "{output_dir}",
  "topic": "{topic}",
  "language": "{detected_language}",
  "complexity": null,
  "current_phase": "phase-1",
  "completed_phases": ["phase-0", "phase-1"],
  "created_at": "{ISO timestamp}"
}
```

Also: if credits.json was saved to a temp location in Phase 0, move it to `{output_dir}/_state/credits.json` now.

## Save State

Write to `_state/config.json`: topic, data_type, columns, scope
Write to `_state/pipeline_metrics.json`:
```json
{
  "started_at": "{ISO timestamp}",
  "agent_dispatches": 0,
  "phase_timings": {},
  "quality_gates": {},
  "smoke_tests": {}
}
```
Update `.superscrape-session.json`: current_phase -> "phase-2"