# Superscraper v4: Design System & Component Library

> Date: 2026-03-19 | Status: Draft | Predecessor: v3-structural-hardening

## 1. Problem Statement

Test run of Superscraper (Web3 esports games) revealed:
- HTML dashboard: black labels on white backgrounds, ugly charts, cheap-looking layout
- Streamlit dashboard: tooltip text overflow, default Streamlit appearance ("looks terrible")
- Dashboard generator produces inconsistent quality because it makes design AND implementation decisions simultaneously

Root cause: no design system, no separation of design from implementation, incomplete component library.

## 2. Changes Overview

### 2.1 Architecture (from v3)

Split SKILL.md into orchestrator + 11 phase files (unchanged from v3 spec):

```
skills/superscrape/
├── SKILL.md                         (~80 lines, orchestrator only)
├── phases/
│   ├── phase-0-onboarding.md
│   ├── phase-1-clarify.md
│   ├── phase-2-discover.md
│   ├── phase-3-collect.md
│   ├── phase-4-normalize.md
│   ├── phase-5a-report-and-data.md
│   ├── phase-5b-dashboard-choice.md
│   ├── phase-5c-dashboard-generate.md
│   ├── phase-5d-review.md           (report-reviewer FIRST)
│   ├── phase-5e-deploy.md           (deploy AFTER review passes)
│   └── phase-6-verify.md
└── references/
    ├── report-format.md             (unchanged)
    ├── xlsx-generator.md            (unchanged)
    ├── design-rules.md              (NEW — replaces dashboard-template.md)
    ├── dashboard-html-kit.md        (REWRITE — full component library)
    └── dashboard-streamlit-kit.md   (REWRITE — full component library)
```

### 2.2 Resume Protocol (from v3)

Session file in output directory (not CWD):

```json
{
  "version": 4,
  "output_dir": "output/2026-03-17-web3-esports-games",
  "topic": "Web3 blockchain games esports 2026",
  "language": "ru",
  "current_phase": "phase-3",
  "completed_phases": ["phase-0", "phase-1", "phase-2"],
  "complexity": "COMPLEX",
  "created_at": "2026-03-17T19:00:00Z"
}
```

- Stored in `output/{dir}/.superscrape-session.json`
- If not found in CWD, search `output/*/`
- Raw data saved per source: `_state/raw_data_{source_name}.json`
- Each phase updates session file at start and completion
- Phase 6 deletes session file
- On resume with existing session: AskUserQuestion "Continue from Phase X or start over?"

### 2.3 Gate Checks

Each phase file starts with executable bash pre-check:

```bash
test -f output/{dir}/_state/sources.json && echo "GATE OK" || echo "GATE FAIL: Phase 2 not complete"
```

For gates requiring content verification (e.g., quality_review field):
```bash
grep -q '"quality_review": "Approved"' output/{dir}/_state/normalized.json 2>/dev/null && echo "GATE OK" || echo "GATE FAIL: quality review not approved"
```

If GATE FAIL — do not proceed, return to previous phase.

Phase table with gates:

| Phase | File | Gate Condition |
|-------|------|---------------|
| 0 | phase-0-onboarding.md | firecrawl --status = OK |
| 1 | phase-1-clarify.md | _state/config.json exists |
| 2 | phase-2-discover.md | _state/sources.json exists |
| 3 | phase-3-collect.md | >=1 raw_data_*.json file |
| 4 | phase-4-normalize.md | _state/normalized.json with "quality_review": "Approved" |
| 5a | phase-5a-report-and-data.md | report.md + data.csv + data.xlsx exist |
| 5b | phase-5b-dashboard-choice.md | _state/dashboard_choice.json exists |
| 5c | phase-5c-dashboard-generate.md | dashboard file(s) exist |
| 5d | phase-5d-review.md | report-reviewer VERDICT: Approved |
| 5e | phase-5e-deploy.md | deploy completed or user declined |
| 6 | phase-6-verify.md | all checks passed |

## 3. Dashboard Pipeline

### 3.1 Agent Roles

**Superpowers pattern: maker + critic loop.**

```
dashboard-designer → code (HTML/Streamlit)
dashboard-auditor → screenshot → compare with design-rules → fix → loop (max 3)
```

Complexity scaling:

| Complexity | Criteria | Pipeline |
|-----------|---------|---------|
| SIMPLE | records < 20 AND columns < 8 | designer → auditor |
| MEDIUM | records < 50 AND columns < 12 | designer → auditor |
| COMPLEX | records >= 50 OR columns >= 12 OR mixed types | art-director → designer → auditor |

Art-director (separate agent) only dispatched for COMPLEX. Makes strategic decisions: what to show/hide, how to segment, visual emphasis.

### 3.2 Dashboard Designer

Reads: `design-rules.md` (WHAT to build) + kit file (HOW to build).
Two Read calls total.

Outputs: complete HTML or Python file, assembled from kit components.
Does NOT invent styles — copies from kit with design tokens baked in.

### 3.3 Dashboard Auditor

Reads: `design-rules.md` (WHAT to check).
Takes screenshot via preview tools.
Compares screenshot against rules and anti-patterns.
Fixes issues directly in code.
Loop: max 3 iterations.

### 3.4 Art Director (COMPLEX only)

Reads: data summary (record count, column types, categories).
Outputs: creative brief:
- What to emphasize (which metrics matter most)
- How to segment (split by region? by category?)
- Which columns to show in table vs hide in detail panel
- Layout recommendation (2-column charts? single wide?)

## 4. Design System: 3 Files

### 4.1 design-rules.md (~100 lines)

**Migration:** This file replaces BOTH `dashboard-template.md` AND `design-system.md`. After implementation:
- `dashboard-template.md` → DELETE (content merged into design-rules.md)
- `design-system.md` → DELETE (tokens moved into kit files, rules into design-rules.md)
- `docs/DASHBOARD_DESIGN_SYSTEM.md` → DELETE (draft, superseded)

Contains ONLY:

**Decision table** (data type → components):

| Data Type | KPI Cards | Primary Chart | Comparison | Table |
|-----------|-----------|--------------|------------|-------|
| Rating/comparison | Top-1, avg, total, sources | Horizontal bar (top-20, gradient) | Radar (top-3) | AG Grid: sort by rating, stars |
| Prices | Min/max/median, best value | Scatter (price vs metric) | Boxplot by category | AG Grid: conditional coloring, currency format |
| Time series | Latest, trend %, min/max | Line (area fill, zoom) | Stacked bar by period | AG Grid: date format |
| Segment | Leader share, count, total | Treemap or sunburst | Stacked bar | AG Grid: group by segment |
| Distribution | Total, top category, spread | Donut (category shares) | Stacked bar (category × sub) | AG Grid: badges |
| Fallback | Total records, sources, date | Horizontal bar | Scatter | Full AG Grid |

**Auto-detection rules** (dual verification — metadata + actual CSV data).

**Layout rules:**
- < 20 records: 2 KPI + 1 chart + table
- 20-50 records: 4 KPI + 2 charts + table
- 50+ records: 4 KPI + 2 charts + table with pagination

**Interaction rules:**
- Global filters (sidebar) → update everything via single `applyFilters()`
- Click bar in chart → filter table (same `applyFilters()`)
- Click table row → slide-in detail panel
- Esc → close panel

**Anti-patterns** (with correct alternatives):
- Black labels on white → use dark tooltip with light text
- Tooltip text overflow → max-width: 400px, word-wrap
- Unformatted numbers → use formatNumber() (1K, 1M, $)
- Empty screen on load → show loading skeleton
- Radar with 5+ items → max 3, overlapping unreadable
- Default Streamlit appearance → inject custom CSS
- Cyrillic labels truncated → abbreviate: max 10 chars on axes

**Number formatting rules:**
- Integers >= 1000: `1,234` or `1.2K` / `1.2M`
- Currency: detect from data ($/EUR/RUB), format with symbol
- Percentages: `XX.X%`
- Ratings: star display (★★★★☆) in table, number in charts
- N/A: show as gray badge "N/A", never empty cell

### 4.2 dashboard-html-kit.md (~400 lines)

Complete, working code for every component with design tokens baked in.

**Base (CDN + layout + CSS):**
- ECharts 5, AG Grid 31, Tailwind CDN, Lucide Icons
- Dark theme CSS (backgrounds, text hierarchy, borders)
- Glassmorphism card styles
- AG Grid dark theme overrides
- Badge styles (yes/no/partial/status)
- Detail panel slide-in CSS
- Loading skeleton CSS
- Responsive sidebar (collapse on mobile)
- Footer styles

**Components (each as copy-paste JS function):**

Charts (all with dark theme, gradient, animation, tooltips, click-to-filter):
1. `chartHorizontalBar()` — sorted, gradient fill, stagger animation (EXISTS, keep)
2. `chartRadar()` — top-3, short labels, polygon (EXISTS, keep)
3. `chartScatter()` — color groups, emphasis (EXISTS, keep)
4. `chartLine()` — area fill, dataZoom, smooth (EXISTS, keep)
5. `chartBoxplot()` — quartile stats (EXISTS, keep)
6. `chartTreemap()` — aggregate by category (EXISTS, keep)
7. `chartDonut()` — NEW: inner radius 50%, labels outside, percentage
8. `chartStackedBar()` — NEW: grouped categories, legend, percentage mode option

KPI:
9. `renderKPIs()` — countUp animation, Lucide icons, trend ▲/▼ (EXISTS, enhance with trend)

Table:
10. `renderTable()` — AG Grid with column types (EXISTS, enhance):
    - Badge renderer for yes/no/status values
    - Rating stars renderer (★★★★☆) for rating columns
    - Progress bar renderer for percentage columns
    - Currency formatter for price columns
    - Number formatter for large numbers

Filters:
11. `initFilters()` + `applyFilters()` + `resetFilters()` — dropdowns + search (EXISTS, keep)
12. `initRangeSliders()` — NEW: for numeric columns (price from-to, rating from-to)

Detail panel:
13. `showDetailPanel()` + `closeDetailPanel()` — slide-in (EXISTS, keep)

Utility:
14. `formatNumber(value, type)` — NEW: handles integers, currency, percent, rating
15. `formatDate(value, locale)` — NEW: localized date display
16. `renderLoadingSkeleton()` — NEW: animated placeholder while data loads
17. `renderEmptyState(message)` — NEW: "no data matching filters" display
18. `renderErrorState(message)` — NEW: "failed to load chart" fallback
19. `renderFooter(metadata)` — NEW: date, sources, credits at bottom

Assembly instructions:
20. Step-by-step guide for dashboard-generator to assemble components

**CANONICAL color palette (8 colors — this is the SINGLE source of truth, overrides any other file):**
`#60a5fa, #34d399, #fbbf24, #f87171, #a78bfa, #22d3ee, #fb923c, #e879f9`
(Tailwind 400-level colors, optimized for dark backgrounds. Any conflicting palettes in design-system.md or dashboard-template.md are superseded by this.)

**CANONICAL background colors:**
- Page background: `#0f172a` (Tailwind slate-900)
- Card/surface: `#1e293b` (Tailwind slate-800)
- Border: `#334155` (Tailwind slate-700)
- Text primary: `#f1f5f9`, secondary: `#94a3b8`, muted: `#64748b`

**Typography (system fonts, unchanged):**
`-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`
`font-variant-numeric: tabular-nums`

### 4.3 dashboard-streamlit-kit.md (~300 lines)

Same components but for Streamlit + custom CSS injection.

**Critical: Custom CSS block** that overrides Streamlit defaults:
```python
st.markdown("""
<style>
    /* Dark theme override */
    .stApp { background-color: #0f172a; }
    /* KPI metric cards */
    [data-testid="stMetricValue"] { font-size: 2rem; font-weight: 700; }
    [data-testid="stMetricLabel"] { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; }
    /* Section dividers */
    hr { border-color: #334155; margin: 2rem 0; }
    /* Sidebar width */
    [data-testid="stSidebar"] { min-width: 280px; }
    /* Hide Streamlit branding */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    /* Table styling */
    .stDataFrame { border: 1px solid #334155; border-radius: 12px; }
</style>
""", unsafe_allow_html=True)
```

**Libraries:**
- `streamlit-echarts` — renders same ECharts configs as HTML version
- `streamlit-aggrid` (v1.2.1, actively maintained) — AG Grid Community
- `pandas`, `openpyxl`

**Components:**
- ECharts configs: identical JSON to HTML kit (shared config = identical look)
- AG Grid: same column defs, dark theme, badge renderers
- KPI: `st.metric()` with custom CSS + delta for trends
- Filters: `st.selectbox`, `st.slider` in sidebar
- Detail: `st.expander` below table for selected row
- Sections: `st.divider()` between blocks
- Footer: `st.caption()` with metadata

## 5. Subagent Changes

### 5.1 scraper.md

Two changes:

**Strict output format:**
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

**Credit limit:** max 5 Firecrawl requests (search/scrape) per source.

### 5.2 data-quality-reviewer.md and report-reviewer.md

Add mandatory verdict format:
```
## VERDICT: Approved
```
or
```
## VERDICT: Issues Found
- CRITICAL: ...
- WARNING: ...
```

Orchestrator searches for `VERDICT:` string. If missing, re-dispatch.

### 5.3 dashboard-generator.md → RENAMED to dashboard-designer.md

The existing `dashboard-generator.md` is renamed to `dashboard-designer.md` and its role is narrowed:
- Reads: `design-rules.md` (decision table) + kit file (code snippets)
- Receives: data + column classification
- If COMPLEX: also reads art-director brief
- Assembles final HTML/Python from kit components
- Does NOT invent styles — copies from kit, replaces placeholders
- Phase 5c dispatches `superscraper:dashboard-designer` (not generator)

There is NO separate dashboard-generator agent. Designer = the only maker agent.

### 5.4 NEW: dashboard-art-director.md

Only dispatched for COMPLEX dashboards (records >= 50 OR columns >= 12).

Receives: data summary (record count, column types, unique values per category).

Outputs creative brief:
- Emphasis: which metrics to highlight in KPI
- Segmentation: how to split data (by region, by tier, by status)
- Layout: 2-column charts, single wide, etc.
- Hide/show: which columns in table vs detail panel
- Special: any data-specific considerations

Fallback: if art-director fails or produces unusable brief, fall back to MEDIUM pipeline (designer uses decision table directly without brief).

### 5.6 dashboard-auditor.md (enhanced)

Enhanced with:
- Screenshot comparison against design-rules anti-patterns
- Checks: tooltips not overflowing, numbers formatted, no empty states visible with data, responsive sidebar works, footer present
- Fix loop: max 3 iterations
- Final VERDICT: Approved or Issues Found

## 6. Quality Improvements

### 6.1 Data Quality

Phase 3 enhancements:
- **Dead project detection:** if source returns 404 or last activity >6 months → flag in _state/errors.json with root cause

Phase 4 enhancements (after merge, before reviewer):
- **Cross-validation:** if same entity found in 3+ sources, compare numbers. >30% discrepancy → flag as "conflicting data" in normalized.json (must happen in Phase 4, not Phase 3, because Phase 3 collects per-source independently)
- data-quality-reviewer MUST be dispatched (gate enforced: normalized.json must contain "quality_review": "Approved")

### 6.2 Firecrawl Credit Economy

Phase 0: check `firecrawl --status`, record available credits.
Phase 3: distribute credits evenly across sources. Max 5 requests per source.
If credits < 20: warn user "Low Firecrawl credits, may not complete all sources."

### 6.3 UX Improvements

- After each scraper agent: show "3/5 sources collected" progress in chat
- If rate limit hit: "Rate limit reached. Data saved to _state/. Say 'continue' when ready."
- Phase 3 checkpoint: show first 3 records from each source, ask "Data looks correct?"
- Phase 5b + 5d: MANDATORY (cannot be skipped, separate phase files)

## 7. Files Changed

| File | Action | Description |
|------|--------|-------------|
| skills/superscrape/SKILL.md | REWRITE | Orchestrator only (~80 lines) |
| skills/superscrape/phases/*.md (11 files) | NEW | One file per phase |
| skills/superscrape/references/design-rules.md | NEW | Replaces dashboard-template.md |
| skills/superscrape/references/dashboard-html-kit.md | REWRITE | Full component library with 20 components |
| skills/superscrape/references/dashboard-streamlit-kit.md | REWRITE | Full Streamlit component library |
| skills/superscrape/references/dashboard-template.md | DELETE | Replaced by design-rules.md |
| skills/superscrape/references/design-system.md | DELETE | Tokens in kit files, rules in design-rules.md |
| docs/DASHBOARD_DESIGN_SYSTEM.md | DELETE | Draft, superseded by design-rules.md |
| agents/scraper.md | EDIT | Add strict JSON output, credit limit |
| agents/dashboard-generator.md | RENAME → dashboard-designer.md | Reads kit + design-rules, assembles dashboard |
| agents/dashboard-art-director.md | NEW | Creative brief for COMPLEX data |
| agents/dashboard-auditor.md | EDIT | Enhanced checklist, screenshot compare |
| agents/data-quality-reviewer.md | EDIT | Add VERDICT format |
| agents/report-reviewer.md | EDIT | Add VERDICT format |

## 8. Complexity Computation

Complexity is computed at the START of Phase 5b (dashboard choice), because that is when normalized.json is available with final record count and column classification.

```
records = len(data)
columns = len(column_types)
mixed = has_date AND has_rating  # or other mixed signals

if records >= 50 or columns >= 12 or mixed:
    complexity = "COMPLEX"
elif records >= 20 or columns >= 8:
    complexity = "MEDIUM"
else:
    complexity = "SIMPLE"
```

Complexity is saved in `.superscrape-session.json` and passed to Phase 5c.

## 9. What Does NOT Change

- report-format.md — works fine
- agents/report-writer.md — works fine, no changes needed
- xlsx-generator.md — works fine
- skills/superscrape-dashboard/ — not tested yet
- skills/superscrape-update/ — not tested yet
- commands/superscrape.md — works fine
- hooks/ — works fine
- plugin.json, marketplace.json — works fine
- 6-phase workflow logic — same phases, split into files
- Firecrawl CLI approach — unchanged
- Output file formats (report.md, data.csv, data.xlsx) — unchanged
