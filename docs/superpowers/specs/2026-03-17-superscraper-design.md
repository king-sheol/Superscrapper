# Superscraper — Universal Data Collection & Analysis Plugin

> **Date:** 2026-03-17
> **Status:** Implemented
> **Type:** Claude Code Plugin

## Purpose

Superscraper is a Claude Code plugin that autonomously discovers sources, scrapes data, normalizes it, and produces structured analytical outputs — reports, Excel files, and interactive dashboards — when the user asks to collect, compare, or research data on any topic.

## Problem Statement

Collecting and analyzing web data requires multiple manual steps: finding sources, scraping pages, cleaning data, building tables, writing analysis, and creating visualizations. Each step is error-prone and time-consuming. Users need a single command that handles the entire pipeline end-to-end.

## Architecture

### Plugin Structure

```
Superscrapper/
├── .claude-plugin/plugin.json       — Plugin manifest
├── skills/
│   ├── superscrape/                 — Main skill: 6-phase workflow
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── report-format.md     — Analytical report template
│   │       ├── xlsx-generator.md    — CSV + XLSX generation (openpyxl)
│   │       └── dashboard-template.md — Streamlit + HTML templates
│   ├── superscrape-dashboard/       — Regenerate dashboard from existing data
│   │   └── SKILL.md
│   └── superscrape-update/          — Refresh data from previous collection
│       └── SKILL.md
├── agents/
│   ├── scraper.md                   — Collects data from one source
│   ├── report-writer.md             — Generates analytical report
│   ├── dashboard-generator.md       — Creates XLSX + dashboards
│   ├── data-quality-reviewer.md     — Validates data quality
│   └── report-reviewer.md          — Reviews report quality
├── commands/superscrape.md          — /superscrape entry point
└── hooks/                           — SessionStart auto-activation
    ├── hooks.json
    └── session-start
```

### Why a Plugin (Not a Skill)

- Multiple entry points: `/superscrape`, `/superscrape-dashboard`, `/superscrape-update`
- Custom subagents with specialized tools and instructions
- Hooks for auto-activation on trigger phrases
- Extensible architecture for future features

## Workflow: 6 Phases

### Phase 1: Accept & Clarify
- Parse topic, data type, scope from user request
- Determine columns (3 mandatory: name, source URL, collection date)
- If additional columns unclear → AskUserQuestion with suggestions based on data type
- Confirm column list before proceeding

### Phase 2: Source Discovery (2-3 parallel agents)
- Agent 1: Firecrawl search for main topic (aggregators, official sites)
- Agent 2: Firecrawl search for APIs + topic
- Agent 3: Firecrawl search for reviews/comparisons + topic
- **Checkpoint**: present sources to user, get confirmation

### Phase 3: Data Collection (up to 5 parallel scraper agents)
- Each agent works one source via Firecrawl MCP
- API-first strategy when public APIs found
- Rate limiting between requests
- Root cause error handling:
  - HTTP 403/429 → 5s wait + single retry
  - HTTP 5xx → 3s wait + single retry
  - Empty response → retry with JS rendering mode
  - Timeout → increase timeout + single retry
  - Other errors → log and stop (no infinite retries)
- **Checkpoint**: show data preview, confirm columns look correct

### Phase 4: Normalize & Validate
- Merge data from all scrapers
- Defense-in-depth validation (4 layers):
  1. Format: data types, encodings, units
  2. Duplicates: deduplication by key fields
  3. Ranges: numbers within bounds, dates valid
  4. Cross-check: data from different sources consistent
- Fill gaps as N/A with explanation
- Dispatch data-quality-reviewer subagent (review loop, max 3 iterations)
- Analyze: leaders, patterns, anomalies, market context
- Assign source confidence levels (High/Medium/Low)

### Phase 5: Generate Output
- **5a**: Report + data files (parallel agents: report-writer + dashboard-generator for CSV/XLSX)
- **5b**: Dashboard choice via AskUserQuestion (Streamlit / HTML / both / none)
- **5c**: Generate chosen dashboard(s) via dashboard-generator subagent
- **5d**: Auto-deploy onboarding:
  - Streamlit on VPS: ask for SSH details → scp + docker compose up → verify
  - HTML on GitHub Pages: ask for repo details → gh repo create + push + enable Pages → verify
  - Fallback to instructions only when no access
- **5e**: Report review loop (report-reviewer subagent, max 3 iterations)

### Phase 6: Verify & Present
Evidence-based verification of all outputs:
- report.md exists and non-empty
- data.csv parses without errors
- data.xlsx opens with openpyxl
- dashboard.py passes syntax check
- requirements.txt has all dependencies
- docker-compose.yml is valid YAML
- Show evidence to user + final summary

## Output Files

Each run generates a dated directory: `output/YYYY-MM-DD-{topic-slug}/`

| File | Purpose |
|------|---------|
| report.md | Analytical document (6 mandatory sections) |
| data.csv | Raw data |
| data.xlsx | Formatted Excel (auto-width, filters, color scales, metadata sheet) |
| dashboard.py | Streamlit dashboard (if chosen) |
| dashboard.html | Static HTML dashboard (if chosen) |
| Dockerfile | Docker image for Streamlit |
| docker-compose.yml | VPS deployment |
| nginx.conf | Reverse proxy config |
| requirements.txt | Python dependencies |

## Subagents

| Agent | Purpose | Tools | Output |
|-------|---------|-------|--------|
| scraper | Collect data from one source | Firecrawl, Read, Write | Structured data + issues |
| report-writer | Write analytical report | Write, Read | report.md |
| dashboard-generator | Generate XLSX + dashboards | Write, Bash, Read | CSV, XLSX, dashboard files |
| data-quality-reviewer | Validate data quality | Read (read-only) | Approved / Issues Found |
| report-reviewer | Review report quality | Read (read-only) | Approved / Issues Found |

All agents inherit the parent model. Reviewer agents are intentionally restricted to read-only tools to prevent them from modifying the files they review.

## Report Format

6 mandatory sections: Title/Metadata → Overview (WHAT/HOW TO READ/KEY INSIGHT/CONCLUSION) → Data Table → Analysis (Leaders, Patterns, Anomalies, Market Context) → Conclusions & Recommendations → Confidence Map.

Rules: numbers need context, N/A explained, insights specific, recommendations actionable, sources linked.

## Dashboard Architecture

### Decision Table: Data Type → Visualization

| Data Type | Primary Chart | Comparison Chart |
|-----------|---------------|------------------|
| Rating/comparison | Horizontal bar (sorted) | Radar chart (top 5) |
| Prices/ranges | Box plot / violin | Scatter (price vs metric) |
| Time series | Line chart | Area chart (stacked) |
| Geographic | Choropleth / bubble map | Bar by region |
| Categories + numbers | Grouped bar | Heatmap (correlations) |

### KPI Cards (auto-selected)
- Numeric columns: min, max, average, median
- Ratings: leader name + average score
- Prices: range + median
- Always: total records, sources count, collection date

### Styling
- Dark theme (Catppuccin Mocha palette)
- Plotly template: `plotly_dark`
- Color palette: `px.colors.qualitative.Set2`
- Both Streamlit and HTML dashboards use same visual language

## Superpowers Patterns Used

| Pattern | Where Applied |
|---------|--------------|
| Dispatching parallel agents | Phases 2, 3, 5a, 5c |
| Interactive checkpoints (AskUserQuestion) | After source discovery, after data collection, dashboard choice |
| TodoWrite progress tracking | All 6 phases |
| Spec-document-reviewer loop | Data quality review (Phase 4) |
| Code-reviewer loop | Report review (Phase 5e) |
| Defense-in-depth validation | 4-layer data validation (Phase 4) |
| Systematic debugging (root cause) | Scraping error handling (Phase 3) |
| Verification before completion | Evidence checks (Phase 6) |

## Prerequisites

- **Firecrawl MCP** plugin installed and configured
- **Python 3.8+** with pip (for XLSX generation and Streamlit)

### Firecrawl MCP Tool Reference

Tool names depend on plugin configuration (typically prefixed `mcp__firecrawl__`). Exact names are discovered at runtime.

| Action | Tool Pattern | Usage |
|--------|-------------|-------|
| Web search | `firecrawl_search` / `search` | Find sources by topic. Args: `query`, `limit` |
| Scrape page | `firecrawl_scrape` / `scrape` | Extract content from URL. Args: `url`, `formats` |
| Crawl site | `firecrawl_crawl` / `crawl` | Crawl multiple pages. Args: `url`, `limit` |
| Extract data | `firecrawl_extract` / `extract` | Extract structured data. Args: `urls`, `prompt` |
| Fetch page | `firecrawl_fetch` / `fetch` | Simple page fetch (for APIs). Args: `url` |

## Activation

- **Slash command**: `/superscrape <topic>`
- **Auto-activation**: Trigger phrases in Russian and English (собери данные, найди информацию, сравни, research, compare, scrape, etc.)
- **SessionStart hook**: Injects plugin context for auto-activation awareness

## Additional Skills

- `/superscrape-dashboard` — Regenerate dashboard from existing CSV/XLSX data
- `/superscrape-update` — Re-scrape same sources, highlight changes vs previous run, and add a "Changes Since Last Run" section to the report
