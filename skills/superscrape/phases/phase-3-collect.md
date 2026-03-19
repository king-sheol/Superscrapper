# Phase 3: Collect Data from Sources

## Pre-check

```bash
test -f {output_dir}/_state/sources.json && echo "GATE OK" || echo "GATE FAIL"
```

If GATE FAIL — return to previous phase.

## Instructions

### 1. Credit Distribution

Read `{output_dir}/_state/credits.json` to get `initial_credits`. Read `{output_dir}/_state/sources.json` to count approved sources.

Calculate per-source budget:
```
source_count = number of approved sources
max_per_source = min(5, floor(initial_credits / source_count))
```

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
3. Message the user with progress: **"N/M sources collected"** (e.g. "3/5 sources collected")

Do NOT wait for all agents to finish before saving. Each agent's data is saved individually.

### 4. Dead Project Detection

If a scraper returns FAIL with HTTP 404:
1. Log to `{output_dir}/_state/errors.json`:
   ```json
   {"source": "url", "error": "404", "timestamp": "ISO", "action": "skipped"}
   ```
2. Report to user and continue with remaining sources

### 5. Rate Limit Handling

If a rate limit is hit mid-collection:
1. Save all data collected so far (individual raw_data files)
2. Save current state to `_state/` so session can resume
3. Message: **"Rate limit reached, data saved. Say 'continue' when ready."**
4. Tell the user which sources succeeded and which remain
5. Wait for user to say "continue" before retrying remaining sources

### 6. Error Handling (Root Cause)

For each failed source, diagnose systematically:
- HTTP 404 -> verify URL, try `firecrawl map` on domain, find alternative page
- Rate limit -> increase pause between requests, retry
- JS-only rendering -> use `firecrawl scrape URL --wait-for 3000`
- Geo-block -> find alternative source
- No data found -> mark N/A with explanation
- Report all issues to the user

### 7. Checkpoint (MANDATORY)

After all agents complete (or rate limit pause), show preview to user:
```
Collected N records from M sources. First 3 records per source:
| Name | Col2 | Col3 | Source | Date |
| ...  | ...  | ...  | ...    | ...  |
Data looks correct? Columns match?
```

Use AskUserQuestion. Wait for user confirmation.

## Save State

Write to `_state/raw_data_{source_slug}.json`: raw records per source (saved incrementally above)
Write to `_state/errors.json`: any collection errors (if applicable)
Update `.superscrape-session.json`: current_phase -> "phase-4"

## Next

Read `phases/phase-4-normalize.md` and continue.
