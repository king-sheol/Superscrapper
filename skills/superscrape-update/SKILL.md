---
name: superscrape-update
description: >
  Use when the user wants to update or refresh data from a previous superscrape run.
  Triggers on "обнови данные", "пересобери", "refresh data", "update scrape", "re-scrape",
  or when the user references a previous data collection and wants fresh data from the same sources.
---

# Superscrape Update — Refresh Existing Data Collection

Re-scrape sources from a previous data collection to get updated data.
Preserves the same columns and sources, but collects fresh values.

## When to Use

- User has a previous superscrape output and wants updated data
- Prices or ratings may have changed since last collection
- User wants to track changes over time

## Workflow

### Step 1: Find Previous Run

Look for previous output directories:
- Check `output/*/report.md` for metadata (sources, columns, topic)
- If multiple runs exist, ask user which one to update
- If not found, ask for the path

### Step 2: Extract Previous Configuration

From the previous report.md and data files, extract:
- **Topic**: what was researched
- **Columns**: what fields were collected
- **Sources**: which URLs were used
- **Confidence levels**: which sources were reliable

### Step 3: Confirm with User

Use AskUserQuestion:
```
"Обновляю данные по теме '[topic]'. Вот что было в прошлый раз:"
- Sources: [list]
- Columns: [list]
- Records: N
"Использовать те же источники и колонки? Или хочешь изменить?"
```

### Step 4: Re-scrape

Dispatch **scraper** subagents for each confirmed source (in parallel).
Use the same column list as the previous run.

### Step 5: Merge & Compare

- Normalize new data using the same process as Phase 4 of main skill
- Run **data-quality-reviewer**
- Compare with previous data:
  - What changed? (price increases/decreases, new entries, removed entries)
  - Highlight significant changes in the report

### Step 6: Regenerate Output

- Generate updated report.md with a "Changes Since Last Run" section
- Regenerate CSV/XLSX with fresh data
- Ask if dashboard should be regenerated too

### Step 7: Verify

Run standard verification checks.
Show comparison summary: "N prices changed, M new entries, K removed."
