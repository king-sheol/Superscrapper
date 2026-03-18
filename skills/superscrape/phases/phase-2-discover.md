# Phase 2: Discover Sources

## Pre-check

```bash
cat {output_dir}/_state/config.json > /dev/null 2>&1 && echo "GATE OK" || echo "GATE FAIL: config.json missing"
```

If GATE FAIL — go back to Phase 1.

## Instructions

### 1. Parallel Search Agents

Dispatch 2-3 search agents in parallel using the Agent tool:

- **Agent 1**: `firecrawl search "{topic}" -o {output_dir}/.firecrawl/search-main.json --json --limit 10` — find aggregators, rating sites, official sources
- **Agent 2**: `firecrawl search "{topic} API" -o {output_dir}/.firecrawl/search-api.json --json --limit 5` — find public APIs (use preferentially if found)
- **Agent 3**: `firecrawl search "{topic} review comparison rating" -o {output_dir}/.firecrawl/search-reviews.json --json --limit 10` — find review and comparison sites

Each agent returns a list of sources with: URL, type (aggregator/official/review/API), estimated data quality (High/Medium/Low).

### 2. Map Top Sources (Credit Economy)

For the top 3 most promising sources, run `firecrawl map` to discover relevant URLs:

```bash
firecrawl map URL --search "{topic}" -o {output_dir}/.firecrawl/map-{slug}.txt
```

**Credit economy rule**: If a source has fewer than 5 relevant URLs, use a single `firecrawl scrape` instead of `firecrawl crawl`.

### 3. Checkpoint — User Confirmation

Use AskUserQuestion to present discovered sources:
```
Found N sources. Here are the best:
- [source 1] — type, ~X entries, quality: High
- [source 2] — type, structured data
- [source 3] — type, ~Y entries, quality: Medium
Which ones to use? Add others?
```

Wait for user confirmation before proceeding.

### 4. Save State

Write `{output_dir}/_state/sources.json`:
```json
{
  "sources": [
    {"url": "...", "type": "...", "quality": "...", "estimated_entries": 0, "approved": true}
  ]
}
```

## Update Session

Update `.superscrape-session.json`: set `current_phase` to `"phase-3"`, add `"phase-2"` to `completed_phases`.

## Done

Sources confirmed by user and saved to sources.json.

Phase 2 complete.
