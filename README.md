# Superscraper

Claude Code plugin for universal web data collection, analysis, and dashboard generation.

## What it does

When you ask to collect, compare, or research data on any topic — Superscraper automatically discovers sources, scrapes data, normalizes it, and produces:

- **Analytical report** (Markdown) with insights, patterns, and recommendations
- **Data files** (CSV + formatted XLSX with color scales and filters)
- **Interactive dashboards** (Streamlit for VPS, HTML for GitHub Pages)
- **Deployment configs** (Dockerfile, docker-compose.yml, nginx.conf)

## Usage

### Slash command
```
/superscrape CRM systems
/superscrape ноутбуки до 100000 рублей
```

### Auto-activation
Just write naturally:
- "собери данные по CRM-системам"
- "сравни ноутбуки до 100к"
- "исследуй рынок электромобилей"
- "найди лучшие VPN-сервисы"

### Additional commands
- `/superscrape-dashboard` — regenerate dashboard from existing data
- `/superscrape-update` — refresh data from previous collection

## How it works

### 6-phase workflow

1. **Accept & Clarify** — understand topic, agree on columns with user
2. **Discover Sources** (2-3 parallel agents) — find aggregators, APIs, review sites
3. **Collect Data** (up to 5 parallel agents) — scrape each source via Firecrawl
4. **Normalize & Validate** — 4-layer defense-in-depth + data quality review loop
5. **Generate Output** — report + XLSX + chosen dashboard(s) + auto-deploy
6. **Verify** — evidence-based checks before claiming completion

### Interactive checkpoints
- After source discovery → user confirms which sources to use
- After data collection → user reviews data preview
- Before dashboard → user chooses type (Streamlit / HTML / both / none)
- Deploy onboarding → plugin deploys automatically, asks only for server details

### Quality assurance (Superpowers patterns)
- **Data quality reviewer** — validates completeness, consistency, anomalies
- **Report reviewer** — checks all sections present, insights specific, numbers contextual
- **Defense-in-depth** — 4-layer data validation (format → duplicates → ranges → cross-check)
- **Root cause error handling** — systematic diagnosis of scraping failures
- **Verification before completion** — evidence over claims

## Prerequisites

- **Firecrawl CLI** installed and authenticated (`npm install -g firecrawl-cli && firecrawl login --browser`)
- **Python 3.8+** with pip (for XLSX generation and Streamlit)

## Plugin structure

```
├── .claude-plugin/plugin.json    — Plugin manifest
├── skills/
│   ├── superscrape/              — Main skill (6-phase workflow)
│   │   ├── SKILL.md
│   │   └── references/           — Report format, XLSX, dashboard templates
│   ├── superscrape-dashboard/    — Regenerate dashboard from existing data
│   └── superscrape-update/       — Refresh data from previous collection
├── agents/
│   ├── scraper.md                — Collects data from one source
│   ├── report-writer.md          — Generates analytical report
│   ├── dashboard-designer.md     — Creates XLSX + dashboards (design-rules + assembly)
│   ├── dashboard-art-director.md — Creative briefs for complex dashboards
│   ├── dashboard-auditor.md      — Visual audit of generated dashboards
│   ├── data-quality-reviewer.md  — Validates data quality
│   └── report-reviewer.md        — Reviews report quality
├── commands/superscrape.md       — /superscrape entry point
└── hooks/                        — SessionStart auto-activation
```

## Output

Each run generates a dated directory:
```
output/YYYY-MM-DD-topic-slug/
├── report.md           — Analytical document
├── data.csv            — Raw data
├── data.xlsx           — Formatted Excel
├── dashboard.py        — Streamlit dashboard
├── dashboard.html      — Static HTML dashboard
├── Dockerfile          — Docker image
├── docker-compose.yml  — VPS deployment
├── nginx.conf          — Reverse proxy config
└── requirements.txt    — Python dependencies
```
