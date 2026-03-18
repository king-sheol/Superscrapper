# Phase 1: Accept Task & Clarify Columns

## Pre-check

```bash
firecrawl --status | grep Authenticated
```

Must show "Authenticated". If not, go back to Phase 0.

## Instructions

### 1. Parse User Request

Identify from the user's message:
- **Topic**: what to research
- **Scope**: how many items, geography, time period
- **Data type**: rating/comparison, price monitoring, market research, competitor analysis

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
  "created": "YYYY-MM-DD",
  "topic": "...",
  "completed_phases": [0, 1]
}
```

## Done

config.json and session file saved. Columns confirmed by user.

Phase 1 complete.
