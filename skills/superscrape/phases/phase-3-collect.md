# Phase 3: Collect Data from Sources

## Pre-check

```bash
cat {output_dir}/_state/sources.json
```

Must contain approved sources list. If missing, go back to Phase 2.

## Instructions

### 1. Plan Credit Budget

Calculate credit budget per source based on total available credits and number of sources. Prefer APIs over scraping when available.

### 2. Dispatch Scraper Subagents

Dispatch one **scraper** subagent per approved source (max 5 parallel). Each agent:
- Works with ONE source only
- Uses Firecrawl CLI (search, scrape, map, crawl, agent)
- If a public API was found for this source, use it preferentially
- Returns structured data matching the agreed column list
- Saves output to `{output_dir}/.firecrawl/`

### 3. Incremental Save (CRITICAL)

After EACH scraper agent returns:
1. Parse the JSON data block from the agent's response
2. Immediately save to `{output_dir}/_state/raw_data_{source_slug}.json`
3. Report progress in chat: "N/M sources collected"

Do NOT wait for all agents to finish before saving. Each agent's data is saved individually.

### 4. Rate Limit Handling

If a rate limit is hit mid-collection:
1. Save all data collected so far (individual raw_data files)
2. Tell the user which sources succeeded and which remain
3. Wait or ask user how to proceed

### 5. Error Handling (Root Cause)

For each failed source, diagnose systematically:
- HTTP 404 → verify URL, try `firecrawl map` on domain, find alternative page
- Rate limit → increase pause between requests, retry
- JS-only rendering → use `firecrawl scrape URL --wait-for 3000`
- Geo-block → find alternative source
- No data found → mark N/A with explanation
- Report all issues to the user

### 6. Checkpoint (MANDATORY)

After all agents complete (or rate limit pause), show preview to user:
```
Collected N records from M sources. First 3 records per source:
| Name | Col2 | Col3 | Source | Date |
| ...  | ...  | ...  | ...    | ...  |
Data looks correct? Columns match?
```

Wait for user confirmation.

### 7. Save State

Update `.superscrape-session.json` — add 3 to completed_phases.

## Done

All raw_data files saved. User confirmed data preview.

Phase 3 complete.
