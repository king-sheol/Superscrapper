# Phase 2: Discover Sources

## Pre-check

```bash
test -f {output_dir}/_state/config.json && echo "GATE OK" || echo "GATE FAIL"
```

If GATE FAIL — return to previous phase.

## Instructions

### 1. Parallel Search Agents

Dispatch 2-3 search agents in parallel using the Agent tool:

- **Agent 1**: `firecrawl search "{topic}" -o {output_dir}/.firecrawl/search-main.json --json --limit 10` — find aggregators, rating sites, official sources
- **Agent 2**: `firecrawl search "{topic} API" -o {output_dir}/.firecrawl/search-api.json --json --limit 5` — find public APIs (use preferentially if found)
- **Agent 3**: `firecrawl search "{topic} review comparison rating" -o {output_dir}/.firecrawl/search-reviews.json --json --limit 10` — find review and comparison sites

Each agent returns a list of sources with: URL, type (aggregator/official/review/API), estimated data quality (High/Medium/Low).

### 1b. Source Accessibility Check (ZERO Firecrawl credits)

Before mapping, verify top sources are actually reachable using curl (NOT firecrawl — saves credits):
```bash
# HEAD request — costs 0 Firecrawl credits
# First check curl is available (missing on some Windows setups)
curl --version > /dev/null 2>&1 || { echo "curl not available — skipping accessibility check"; exit 0; }
curl -sI -o /dev/null -w "%{http_code}" --max-time 10 URL
```

Interpret HTTP status:
- **200-399**: Accessible → proceed to mapping
- **401/403**: Paywall or login required → mark as "restricted", warn user
- **5xx**: Server down → skip, note in output
- **000 (timeout)**: Possible geo-block or DNS failure → note, try one more time with `--connect-timeout 15`

For sources that return 200, do a quick content check (still zero Firecrawl credits):
```bash
curl -sL --max-time 10 URL | head -c 2000
```
- If output contains "captcha", "challenge", "cf-browser-verification" → mark as "captcha-protected"
- If output contains "access denied", "доступ запрещён", "forbidden" → mark as "restricted"
- If output is empty or <100 bytes → possible geo-block

Only proceed to map sources that are confirmed accessible.

### 2. Map Top Sources (Credit Economy)

For the top 3 most promising sources, run `firecrawl map` to discover relevant URLs:

```bash
firecrawl map URL --search "{topic}" -o {output_dir}/.firecrawl/map-{slug}.txt
```

**Credit economy rule**: If a source has fewer than 5 relevant URLs, use a single `firecrawl scrape` instead of `firecrawl crawl`.

### 3. Checkpoint — User Confirmation

**Source Reliability Classification** — classify each source BEFORE presenting to user:

| Category | Reliability | Examples | Note |
|----------|-------------|----------|------|
| Aggregator/catalog | High | G2, Capterra, hostinghub.ru | Structured, verified data |
| Official site | High | vendor's own pricing page | Authoritative but biased |
| Professional review | Medium | techradar, vc.ru articles | Expert opinion, may be outdated |
| Benchmark/testing | High | vpsbenchmarks.com | Measured data |
| Forum/social media | Low | reddit, pikabu, habr comments | Subjective, unverifiable |
| Blog/opinion | Low | personal blogs, medium posts | Anecdotal |

**Rule**: If a source is classified as **Low reliability**, mark it with ⚠️ in the user presentation and add note: "User-generated content — data may be subjective and unverifiable."

Use AskUserQuestion to present discovered sources:
```
Found N sources. Here are the best:
- [source 1] — type, ~X entries, reliability: High ✅
- [source 2] — type, structured data, reliability: High ✅
- [source 3] — type, ~Y entries, reliability: Medium
- ⚠️ [source 4] — forum/social media, reliability: Low (user-generated, subjective data)
Which ones to use? Add others?
```

Wait for user confirmation before proceeding.

## Save State

Write to `_state/sources.json`:
```json
{
  "sources": [
    {"url": "...", "type": "...", "quality": "...", "reliability": "High|Medium|Low", "estimated_entries": 0, "approved": true}
  ]
}
```
Update `.superscrape-session.json`: current_phase -> "phase-3"