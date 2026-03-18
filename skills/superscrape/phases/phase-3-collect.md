# Phase 3: Collect Data from Sources

## Pre-check

```bash
cat {output_dir}/_state/sources.json > /dev/null 2>&1 && echo "GATE OK" || echo "GATE FAIL: sources.json missing"
```

If GATE FAIL — go back to Phase 2.

## Instructions

### 1. Plan Credit Budget

Read `{output_dir}/_state/credits.json` to get `initial_credits`. Read `{output_dir}/_state/sources.json` to count approved sources.

Calculate per-source budget: `floor(initial_credits / number_of_sources)`.

Include this budget in each scraper subagent prompt: "You have N credits for this source. Do not exceed this budget." Prefer APIs over scraping when available (APIs cost 0 credits).

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
3. Message the user: **"N/M sources collected"** (e.g. "2/5 sources collected")

Do NOT wait for all agents to finish before saving. Each agent's data is saved individually.

### 4. Rate Limit Handling

If a rate limit is hit mid-collection:
1. Save all data collected so far (individual raw_data files)
2. Message: **"Rate limit reached, data saved. Say 'continue' when ready."**
3. Tell the user which sources succeeded and which remain
4. Wait for user to say "continue" before retrying remaining sources

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

## Update Session

Update `.superscrape-session.json`: set `current_phase` to `"phase-4"`, add `"phase-3"` to `completed_phases`.

## Done

All raw_data files saved. User confirmed data preview.

Phase 3 complete.
