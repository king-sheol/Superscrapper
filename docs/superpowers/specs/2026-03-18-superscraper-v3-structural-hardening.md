# Superscraper v3: Structural Hardening + Component Library Upgrade

> Date: 2026-03-18
> Status: Draft
> Previous: 2026-03-18-superscraper-v2-optimization.md

## Problem Statement

Test run of Superscraper (Web3 esports games) revealed 17 problems. Root cause: monolithic SKILL.md (421 lines) loses context after rate limits or session breaks. Secondary issue: vanilla JS dashboards lack visual polish for presentations.

Two changes:
1. Split SKILL.md into orchestrator + 11 phase files with resume protocol
2. Replace Plotly.js + vanilla JS with ECharts + AG Grid + Tailwind

## Architecture: Phase-Based Orchestrator

### Current (monolith)
```
skills/superscrape/SKILL.md (421 lines — everything in one file)
```

### New (orchestrator + phases)
```
skills/superscrape/
├── SKILL.md                              (~80 lines — orchestrator only)
├── phases/
│   ├── phase-0-onboarding.md             (~30 lines)
│   ├── phase-1-clarify.md                (~40 lines)
│   ├── phase-2-discover.md               (~45 lines)
│   ├── phase-3-collect.md                (~50 lines)
│   ├── phase-4-normalize.md              (~45 lines)
│   ├── phase-5a-report-and-data.md       (~40 lines)
│   ├── phase-5b-dashboard-choice.md      (~15 lines)
│   ├── phase-5c-dashboard-generate.md    (~30 lines)
│   ├── phase-5d-deploy.md                (~40 lines)
│   ├── phase-5e-review.md                (~30 lines)
│   └── phase-6-verify.md                 (~30 lines)
└── references/
    ├── report-format.md                  (unchanged)
    ├── xlsx-generator.md                 (unchanged)
    ├── dashboard-template.md             (rewritten — decision table + component rules)
    ├── dashboard-html-kit.md             (NEW — full HTML dashboard components)
    └── dashboard-streamlit-kit.md        (NEW — full Streamlit dashboard components)
```

### Orchestrator (SKILL.md) contains only:
1. CRITICAL RULES table (7 rules, compact)
2. Resume Protocol algorithm
3. Phase Table (phase → file → gate condition)
4. TodoWrite initialization template
5. Output directory format

### Each phase file follows this template:
```
# Phase X: [Name]

## Pre-check
[bash gate verification command]

## Instructions
[what to do — 20-40 lines]

## Save state
[what to save to _state/]

## Update session
[update .superscrape-session.json → current_phase = next]

## Next
Read `phases/phase-{X+1}.md` and continue.
```

### Key principle:
Bot reads ONLY the current phase. Context is not polluted with instructions for future phases. Transition between phases is explicit via Read command.

## Resume Protocol

### Session file: `{output_dir}/.superscrape-session.json`
```json
{
  "output_dir": "output/2026-03-17-web3-esports-games",
  "topic": "Web3 blockchain games esports 2026",
  "language": "ru",
  "current_phase": "phase-3",
  "completed_phases": ["phase-0", "phase-1", "phase-2"],
  "created_at": "2026-03-17T19:00:00Z"
}
```

### Algorithm:
1. On start, SKILL.md checks: `cat .superscrape-session.json 2>/dev/null` in CWD
2. If not found, search in `output/*/`
3. If found → Resume mode: read `current_phase` → load corresponding phase file
4. If not found → New session: start with Phase 0
5. Each phase updates session file on start and completion
6. Phase 6 (final) deletes session file

### State files (in output_dir/_state/):
| File | Phase | Contents |
|------|-------|----------|
| `config.json` | Phase 1 | topic, columns, data type, language |
| `sources.json` | Phase 2 | confirmed sources |
| `raw_data_{source_name}.json` | Phase 3 | raw data per source (incremental) |
| `errors.json` | Phase 3 | failed sources with root cause |
| `normalized.json` | Phase 4 | cleaned dataset + analysis + quality_review field |
| `dashboard_choice.json` | Phase 5b | user choice (streamlit/html/both/none) |

### Incremental save in Phase 3:
After EACH scraper agent returns, immediately Write → `_state/raw_data_{source_name}.json`. If 3 of 5 agents complete before rate limit — those 3 sources are saved.

### Resume protection:
If session exists and bot tries to start Phase 1, SKILL.md shows: "Found unfinished session. Continue from Phase X or start over?" via AskUserQuestion.

## CRITICAL RULES (compact table)

| # | Rule |
|---|------|
| 1 | Response language = user's request language |
| 2 | Firecrawl = CLI via Bash ONLY. Never ToolSearch |
| 3 | BANNED: browser tools, WebFetch, WebSearch, Chrome MCP |
| 4 | Phase 5b (dashboard choice) and 5d (deploy) — MANDATORY, never skip |
| 5 | Subagents REQUIRED: scraper, report-writer, dashboard-generator, reviewers |
| 6 | Save _state/ after EVERY phase |
| 7 | Do NOT show final results until Phase 6 complete |

## Gate Checks

Each phase file starts with executable pre-check:
```bash
cat output/{dir}/_state/sources.json > /dev/null 2>&1 && echo "GATE OK" || echo "GATE FAIL: Phase 2 not complete"
```
If GATE FAIL — do not continue, return to previous phase.

### Phase Table with gates:
| Phase | File | Gate (before transition) |
|-------|------|------------------------|
| 0 | phase-0-onboarding.md | firecrawl --status = OK |
| 1 | phase-1-clarify.md | _state/config.json saved |
| 2 | phase-2-discover.md | _state/sources.json saved |
| 3 | phase-3-collect.md | >=1 raw_data_*.json file exists |
| 4 | phase-4-normalize.md | _state/normalized.json with quality_review = Approved |
| 5a | phase-5a-report-and-data.md | report.md + data.csv + data.xlsx exist |
| 5b | phase-5b-dashboard-choice.md | _state/dashboard_choice.json saved |
| 5c | phase-5c-dashboard-generate.md | dashboard file(s) exist |
| 5d | phase-5d-deploy.md | deploy done or user declined |
| 5e | phase-5e-review.md | report-reviewer = Approved |
| 6 | phase-6-verify.md | all checks passed |

## Component Library Upgrade

### Stack
| Component | Library | Version | Size | License |
|-----------|---------|---------|------|---------|
| Charts | Apache ECharts | 5.x | ~1MB | Apache 2.0 |
| Tables | AG Grid Community | latest | ~500KB | MIT |
| Layout/CSS | Tailwind CSS CDN | 3.x | ~300KB | MIT |
| Icons | Lucide Icons | latest | ~10KB per icon | ISC |

### Why ECharts over Plotly:
- Animated transitions (bars grow on load, smooth data updates)
- Gradient fills, glassmorphism tooltips, blur effects
- Native dark theme support (built-in themes)
- 50+ chart types vs Plotly's ~30
- 65k GitHub stars, Apache Foundation, used by Netflix/Alibaba

### Why AG Grid over vanilla JS tables:
- Virtual scrolling (1000+ rows without lag)
- Built-in column filters, sort, resize, pin columns
- CSV export from table directly
- Community edition is MIT licensed, fully featured for read-only use

### CDN Links (HTML dashboard):
```html
<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/ag-grid-community/dist/ag-grid-community.min.js"></script>
<link href="https://cdn.jsdelivr.net/npm/ag-grid-community/styles/ag-grid.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/ag-grid-community/styles/ag-theme-alpine.css" rel="stylesheet">
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://unpkg.com/lucide@latest"></script>
```

### Streamlit dependencies:
```
streamlit>=1.30
streamlit-echarts>=0.4
streamlit-aggrid>=1.2
pandas>=2.0
openpyxl>=3.1
```

## Decision Table: Data Type → Components

### Auto-detection (dual verification):
1. Read column_types from normalized.json (primary signal)
2. Read first 5 rows of data.csv (verification)
3. For each column: parseFloat — if >80% parse → numeric
4. Check for dates: regex YYYY-MM-DD or DD.MM.YYYY
5. If column_types and real data disagree → trust data

### Detection signals:
| Signal | Data type |
|--------|-----------|
| >=3 numeric columns + 1 text (name) | Rating/comparison |
| 1 numeric (price) + categories | Price monitoring |
| date column + numeric | Time series |
| 2+ category columns + numerics | Segment analysis |

### Component mapping:
| Data type | KPI cards | Primary chart | Comparison | Table |
|-----------|-----------|---------------|------------|-------|
| Rating | Top-1 leader, avg score, total count, sources | ECharts horizontal bar (sorted, gradient fill) | ECharts radar (top 5) | AG Grid: all columns, sort by rating |
| Prices | Min/max/median price, best value | ECharts scatter (price vs metric) | ECharts boxplot by category | AG Grid: conditional coloring on prices |
| Time series | Latest value, trend %, min/max for period | ECharts line (area fill, zoom) | ECharts heatmap (day x hour) | AG Grid + ECharts mini sparklines in cells |
| Segment | Leader share, segment count, total | ECharts treemap or sunburst | ECharts stacked bar | AG Grid: group by segment |

### Fallback:
If type not detected → horizontal bar + scatter + full table. Works for any data.

### Sparklines (time series only):
ECharts mini-instances (80x30px) in AG Grid custom cell renderer. Canvas-based, handles virtual scrolling correctly.

## Color Palette

Dark theme base: `#0f172a` (Tailwind slate-900)

### Chart palette (8 colors, high contrast on dark):
```
#60a5fa (blue-400)
#34d399 (emerald-400)
#fbbf24 (amber-400)
#f87171 (red-400)
#a78bfa (violet-400)
#22d3ee (cyan-400)
#fb923c (orange-400)
#e879f9 (fuchsia-400)
```

### Typography:
- System font stack: `-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`
- Numeric alignment: `font-variant-numeric: tabular-nums`
- No custom fonts loaded — zero extra network requests

## Interactivity

### Global filters:
- Dropdown per categorical column
- Range slider per numeric column
- Text search by name
- "Reset all" button
- Single `applyFilters()` function updates everything: KPI recalculates, charts redraw, table filters

### Chart ↔ Table connection (one-directional):
- Click bar in ECharts → calls `applyFilters()` with selected category
- No reverse direction (table click does not highlight chart)

### AG Grid built-in:
- Column filters in headers
- Sort by header click (asc → desc → none)
- Column resize by drag
- CSV export button

### Detail panel:
- Click table row → slide-in panel from right (`position: fixed; right: 0`)
- Shows all fields including long text (comments, URLs)
- "Open source" button → link to source URL
- Close: click outside or Esc
- 15 lines CSS + 10 lines JS

### KPI cards:
- Lucide icon + number + label
- countUp animation on load
- Trend indicator (up/down with color) if comparison data exists

### Responsive:
- Desktop: filter sidebar (collapsible) + main content
- Tablet/Mobile: top bar with "Filters" button → drawer from bottom

## Subagent Changes

### scraper.md — strict output format:
Agent must end response with JSON block:
```json
{
  "source": "DappRadar",
  "status": "SUCCESS|PARTIAL|FAIL",
  "records_count": 15,
  "data": [...],
  "issues": ["DTF.ru returned 404"],
  "confidence": "High|Medium|Low"
}
```
Orchestrator parses this and saves to `_state/raw_data_{source}.json`.

Max 5 Firecrawl requests per source (budget protection).

### dashboard-generator.md — explicit input:
Receives from orchestrator:
- `normalized.json` → data
- `config.json` → columns and types
- `dashboard_choice.json` → streamlit/html/both

### data-quality-reviewer.md and report-reviewer.md — strict verdict:
Must end with:
```
## VERDICT: Approved
```
or
```
## VERDICT: Issues Found
- CRITICAL: ...
- WARNING: ...
```
Orchestrator searches for `VERDICT:` string. If not found — re-ask agent.

### report-writer.md — no changes.

## Quality Improvements

### Cross-validation (Phase 3):
If same entity found in 3+ sources — compare numbers. Divergence >30% → flag as "conflicting data" in normalized.json.

### Dead project detection (Phase 4):
If official site returns 404 or last activity >6 months ago → mark as "possibly dead".

### Firecrawl budget management (Phase 0):
Check `firecrawl --status` → record credit count. In Phase 3 distribute credits evenly across sources.

### Progress reporting:
After each scraper agent completes → message in chat: "3/5 sources collected".
If rate limit hit → explicit message: "Rate limit reached, data saved. Say 'continue' when ready."

## Kit Files Structure

### dashboard-html-kit.md contains:
1. Base section: CDN links, Tailwind config, dark theme CSS, layout grid
2. KPI cards section: HTML template with Lucide icons, countUp JS
3. Charts section: ECharts configs for each chart type from decision table
4. Table section: AG Grid config, dark theme, column definitions, detail panel
5. Filters section: dropdown, range slider, search, applyFilters() function
6. Assembly instructions: how to combine sections based on data type

### dashboard-streamlit-kit.md contains:
1. Imports and theme config (config.toml dark theme)
2. KPI section: st.metric() with delta for trends
3. Charts section: streamlit-echarts with same JSON configs as HTML
4. Table section: streamlit-aggrid config, dark theme
5. Filters section: st.selectbox, st.slider, st.text_input in sidebar
6. Assembly instructions

### Key principle:
ECharts JSON configs are IDENTICAL between HTML and Streamlit kits. Dashboard-generator builds config once, kit determines how to render it.

## What Does NOT Change

- references/report-format.md — works fine
- references/xlsx-generator.md — works fine
- skills/superscrape-dashboard/ — not tested yet, premature to change
- skills/superscrape-update/ — not tested yet, premature to change
- commands/superscrape.md — works fine
- hooks/ — hooks.json and session-start work fine
- plugin.json, marketplace.json — no changes
- 6-phase workflow logic — same logic, just split into files
- 5 subagents — same roles, minor output format changes
- Firecrawl CLI approach — no changes
- Output format — report.md, data.csv, data.xlsx, dashboard files
