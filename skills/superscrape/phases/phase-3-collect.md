# Phase 3: Collect Data from Sources

## Pre-check

```bash
test -f {output_dir}/_state/sources.json && echo "GATE OK" || echo "GATE FAIL"
```

If GATE FAIL — return to previous phase.

## Instructions

### 1. Firecrawl Credit Budget

Read `{output_dir}/_state/firecrawl_credits.json` → get initial_credits. Read `{output_dir}/_state/sources.json` to count approved sources.

- If credits = 0 → STOP. Tell user: "No Firecrawl credits. Run `firecrawl --status` to check."
- If credits < source_count → STOP. Tell user: "Not enough credits (N) for M sources. Reduce sources or add credits."
- If credits < source_count × 5 → per_source = floor(credits / source_count). Warn user: "Limited budget: {per_source} requests per source."
- Otherwise → per_source = 5

Pass per_source limit to each scraper agent prompt. Prefer APIs over scraping when available (APIs cost 0 credits).

### 2. Dispatch Scraper Subagents

Dispatch one **scraper** subagent per approved source. **MUST dispatch ALL scrapers in a single message using multiple parallel Agent tool calls** (max 5). Each Agent call gets its own source — but all calls go in ONE message so they run concurrently. Do NOT dispatch sequentially one-by-one — parallel execution saves significant time.

Each agent:
- Works with ONE source only
- Uses Firecrawl CLI (search, scrape, map, crawl, agent)
- If a public API was found for this source, use it preferentially
- Returns structured data matching the agreed column list
- Saves output to `{output_dir}/.firecrawl/`
- Gets source reliability rating from `_state/sources.json` — pass to agent for logging

### 3. Incremental Save (CRITICAL)

After EACH scraper agent returns:
1. Parse the JSON data block from the agent's response
2. Immediately save to `{output_dir}/_state/raw_data_{source_slug}.json`
3. Print progress to chat: "✅ {source_name}: {records} записей ({n}/{total} источников)"

Do NOT wait for all agents to finish before saving. Each agent's data is saved individually.

### 4. Dead Project Detection

If a scraper returns FAIL with HTTP 404:
1. Log to `{output_dir}/_state/errors.json`:
   ```json
   {"source": "url", "error": "404", "timestamp": "ISO", "action": "skipped"}
   ```
2. Report to user and continue with remaining sources

### 5. Rate Limit Handling

If a scraper agent returns FAIL with rate limit (HTTP 429):
1. Print: "⚠️ Rate limit достигнут. Данные сохранены в _state/. Скажи 'продолжай' когда будешь готов."
2. Save all collected data to `_state/` so session can resume
3. Tell the user which sources succeeded and which remain
4. Wait for user to say "continue"/"продолжай" before retrying remaining sources

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
Update `_state/pipeline_metrics.json`:
- Increment `agent_dispatches` by number of scraper agents dispatched
- Add `phase_timings.phase_3`: `{ "started": "{ISO}", "ended": "{ISO}", "duration_sec": N }`
- Add `quality_gates.collection`: `{ "sources_attempted": M, "sources_succeeded": N, "total_records": R }`
Update `.superscrape-session.json`: current_phase -> "phase-4"

## Next

Read `phases/phase-4-normalize.md` and continue.
