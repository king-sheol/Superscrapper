# Superscraper v4: Design System Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace inconsistent dashboard generation with a design system that guarantees visual quality across all dashboards.

**Architecture:** Three reference files (design-rules.md, dashboard-html-kit.md, dashboard-streamlit-kit.md) replace four overlapping files. Dashboard pipeline splits into designer + auditor agents. SKILL.md becomes thin orchestrator pointing to phase files.

**Tech Stack:** ECharts 5, AG Grid Community 31, Tailwind CSS (CDN), Lucide Icons, streamlit-echarts, streamlit-aggrid

**Spec:** `docs/superpowers/specs/2026-03-19-superscraper-v4-design-system.md`

---

## Chunk 1: Design System Foundation (design-rules.md + cleanup)

### Task 1: Create design-rules.md

**Files:**
- Create: `skills/superscrape/references/design-rules.md`
- Delete: `skills/superscrape/references/dashboard-template.md` (after content migrated)
- Delete: `skills/superscrape/references/design-system.md` (after tokens migrated)
- Delete: `docs/DASHBOARD_DESIGN_SYSTEM.md`

- [ ] **Step 1: Write design-rules.md**

Create `skills/superscrape/references/design-rules.md` (~100 lines) containing:

1. Decision table (6 rows: Rating, Prices, Time series, Segment, Distribution, Fallback) mapping data type → KPI cards, primary chart, comparison chart, table config
2. Auto-detection rules with dual verification (metadata + CSV first 5 rows)
3. Layout rules (record count → component layout)
4. Interaction rules (filters → applyFilters, chart click → filter, row click → panel)
5. Anti-patterns list (7 items from spec section 4.1)
6. Number formatting rules (integers, currency, percentages, ratings, N/A)

Source content from:
- `dashboard-template.md` sections 1-2 (decision table, auto-detection)
- `design-system.md` section 3G (anti-patterns — but use CANONICAL palette from spec)
- Spec section 4.1 (all rules)

Do NOT include: color values, CSS code, component code — those live in kit files.

- [ ] **Step 2: Verify design-rules.md is self-contained**

Read the file back. Confirm:
- Decision table has all 6 data types
- Auto-detection has dual verification (metadata + CSV)
- Layout rules cover <20, 20-50, 50+ records
- All 7 anti-patterns listed with correct alternatives
- Number formatting covers all 5 types
- No color hex values or CSS (those belong in kit files)
- Total ~100 lines

- [ ] **Step 3: Delete superseded files**

```bash
cd "C:/Users/OF-1/Documents/Claude Workspace/Code/Superscrapper"
git rm skills/superscrape/references/dashboard-template.md
git rm skills/superscrape/references/design-system.md
git rm docs/DASHBOARD_DESIGN_SYSTEM.md
```

- [ ] **Step 4: Commit**

```bash
git add skills/superscrape/references/design-rules.md
git commit -m "feat: add design-rules.md, remove 3 superseded design files

design-rules.md consolidates decision table, auto-detection,
layout rules, anti-patterns, and number formatting.
Removes dashboard-template.md, design-system.md, and
docs/DASHBOARD_DESIGN_SYSTEM.md per v4 spec."
```

---

## Chunk 2: HTML Component Library (dashboard-html-kit.md rewrite)

### Task 2: Rewrite dashboard-html-kit.md — Base & CSS

**Files:**
- Rewrite: `skills/superscrape/references/dashboard-html-kit.md`

- [ ] **Step 1: Write base HTML section**

Rewrite section 1 (Base HTML) of dashboard-html-kit.md. Keep the existing structure but update:
- Add loading skeleton CSS (animated pulse placeholder)
- Add responsive sidebar CSS (collapse to drawer on mobile via media query)
- Add footer styles
- Ensure CANONICAL palette from spec (page bg `#0f172a`, surface `#1e293b`, border `#334155`)
- Add N/A badge style (gray `#475569` background)
- Add rating stars CSS
- Add progress bar CSS for cells
- Verify all existing styles are correct (glassmorphism, AG Grid dark, badges, detail panel)

- [ ] **Step 2: Write new chart components**

Add to section 3 (Charts):
- `chartDonut()` — ECharts pie with inner radius 50%, labels outside showing name + percentage, same tooltip/animation/click conventions as other charts
- `chartStackedBar()` — ECharts bar with stack:'total', grouped by category, legend, optional percentage mode, same conventions

Both must use CHART_COLORS palette, dark backgrounds, animationDuration 1500, click-to-filter via applyFilters().

- [ ] **Step 3: Enhance renderKPIs with trend indicators**

Update section 2 (KPI Cards):
- Add trend indicator (▲ green / ▼ red) when comparison data available
- Format large numbers using formatNumber() utility

- [ ] **Step 4: Enhance renderTable with cell renderers**

Update section 4 (Table):
- Rating stars renderer: detect columns with "rating" or "score" in name, values 0-5 → show ★★★★☆
- Progress bar renderer: detect percentage columns → show colored bar in cell
- Currency formatter: detect price columns → format with $ or detected currency symbol
- Number formatter: use formatNumber() for all numeric cells

- [ ] **Step 5: Add range slider filter**

Add to section 5 (Filters):
- `initRangeSliders()` — for each numeric column, create a dual-handle range slider
- Min/max auto-detected from data
- On change: calls applyFilters()
- Styled with Tailwind: dark track, blue handles

- [ ] **Step 6: Write utility functions**

Add new section 6 (Utilities):
- `formatNumber(value, type)` — type: 'integer' (1K/1M), 'currency' ($49.99), 'percent' (45.2%), 'rating' (★★★★☆)
- `formatDate(value, locale)` — detect YYYY-MM-DD or DD.MM.YYYY, format per locale
- `renderLoadingSkeleton()` — insert animated pulse placeholders into KPI, chart, table containers
- `renderEmptyState(message)` — "No data matching filters" with icon, shown when filteredData.length === 0
- `renderErrorState(containerId, message)` — "Failed to load chart" fallback if ECharts init fails
- `renderFooter(metadata)` — date, source count, Firecrawl credits used, "Generated by Superscraper"

- [ ] **Step 7: Update assembly instructions**

Update section 7 (Assembly Instructions):
- Reference new components (donut, stacked bar, range sliders, utilities)
- Add step: "Call renderLoadingSkeleton() immediately, then replace with real data"
- Add step: "Always call renderFooter() at the end"
- Add step: "Wrap chart init in try/catch, call renderErrorState on failure"

- [ ] **Step 8: Verify completeness**

Read entire file. Confirm all 20 components from spec section 4.2 exist:
1-6: existing charts (horizontal bar, radar, scatter, line, boxplot, treemap) ✓
7-8: new charts (donut, stacked bar) ✓
9: KPI with trends ✓
10: table with 4 renderers ✓
11: filters (dropdown + search) ✓
12: range sliders ✓
13: detail panel ✓
14-19: utilities (formatNumber, formatDate, skeleton, empty, error, footer) ✓
20: assembly instructions ✓

All use CANONICAL palette. No conflicting colors.

- [ ] **Step 9: Commit**

```bash
git add skills/superscrape/references/dashboard-html-kit.md
git commit -m "feat: rewrite HTML kit with 20 components, design tokens baked in

New: donut chart, stacked bar, range sliders, formatNumber,
formatDate, loading skeleton, empty/error states, footer.
Enhanced: KPI trends, table cell renderers (stars, progress,
currency), responsive sidebar, N/A badges."
```

---

## Chunk 3: Streamlit Component Library (dashboard-streamlit-kit.md rewrite)

### Task 3: Rewrite dashboard-streamlit-kit.md

**Files:**
- Rewrite: `skills/superscrape/references/dashboard-streamlit-kit.md`

- [ ] **Step 1: Write custom CSS injection block**

First section: complete CSS that overrides Streamlit defaults:
- `.stApp` background → `#0f172a`
- Metric card styling (font-size, uppercase labels, tracking)
- Sidebar width 280px
- Hide Streamlit branding (#MainMenu, footer)
- Section dividers color
- DataFrame border-radius
- Custom badge HTML styles (yes/no/partial)
- N/A badge style

- [ ] **Step 2: Write ECharts config templates**

Section for each chart type (horizontal bar, radar, scatter, line, boxplot, treemap, donut, stacked bar). Each as a Python dict that gets passed to `st_echarts()`. Configs IDENTICAL to HTML kit JSON — same colors, same animations, same tooltips. This ensures both dashboards look the same.

- [ ] **Step 3: Write AG Grid config**

Section for AG Grid via `streamlit-aggrid`:
- Column definitions with same renderers as HTML (badges via cellRenderer JS, currency format, number format)
- Dark theme config matching HTML kit
- Row selection → st.session_state for detail display

- [ ] **Step 4: Write KPI, filters, detail, footer sections**

- KPI: `st.metric()` with delta for trends + custom CSS
- Filters: `st.selectbox` for categories, `st.slider` for numeric ranges, `st.text_input` for search — all in sidebar
- Detail: `st.expander` below table showing all fields for selected row
- Footer: `st.caption` with metadata
- Number formatting: same `formatNumber()` logic in Python

- [ ] **Step 5: Write assembly instructions for Streamlit**

Step-by-step guide:
1. Load data.csv, strip BOM
2. Classify columns (same dual verification as HTML)
3. Inject custom CSS
4. Render KPI metrics in `st.columns(4)`
5. Render charts via `st_echarts()` with decision-table-selected configs
6. Render AG Grid table
7. Handle row selection → expander
8. Render footer

- [ ] **Step 6: Write requirements.txt template**

```
streamlit>=1.30
streamlit-echarts>=0.4
streamlit-aggrid>=1.2
pandas>=2.0
openpyxl>=3.1
```

- [ ] **Step 7: Commit**

```bash
git add skills/superscrape/references/dashboard-streamlit-kit.md
git commit -m "feat: rewrite Streamlit kit with custom CSS, ECharts configs, AG Grid

Matching visual quality with HTML kit. Custom CSS overrides
Streamlit defaults. ECharts configs identical to HTML version.
AG Grid with same column renderers. Requirements.txt template."
```

---

## Chunk 4: Agent Updates

### Task 4: Rename dashboard-generator → dashboard-designer

**Files:**
- Rename: `agents/dashboard-generator.md` → `agents/dashboard-designer.md`

- [ ] **Step 1: Create dashboard-designer.md from generator**

Read `agents/dashboard-generator.md`. Create `agents/dashboard-designer.md` with:
- Updated name in frontmatter: `dashboard-designer`
- Updated description: references design-rules.md and kit files
- Updated instructions: "Read design-rules.md for WHAT to build, then read the appropriate kit file for HOW"
- Remove any instruction about inventing styles or choosing colors
- Add: "Copy code blocks from kit file. Replace placeholders. Do NOT modify design tokens."
- Phase 5c references updated to dispatch `superscraper:dashboard-designer`

- [ ] **Step 2: Delete old dashboard-generator.md**

```bash
git rm agents/dashboard-generator.md
```

- [ ] **Step 3: Commit**

```bash
git add agents/dashboard-designer.md
git commit -m "feat: rename dashboard-generator to dashboard-designer

Narrows role to mechanical assembly from kit components.
No style invention — copies from kit with baked-in tokens."
```

### Task 5: Create dashboard-art-director.md

**Files:**
- Create: `agents/dashboard-art-director.md`

- [ ] **Step 1: Write art-director agent**

Create `agents/dashboard-art-director.md` with frontmatter:
- name: dashboard-art-director
- description: "Creative director for COMPLEX dashboards. Analyzes data and produces a creative brief for the dashboard-designer."
- tools: Read, Bash (for data analysis)

Instructions:
1. Receive data summary (record count, column types, unique values per category)
2. Analyze: what matters most? What segments exist? What should be highlighted?
3. Output creative brief with: emphasis, segmentation, layout recommendation, hide/show columns, special considerations
4. Brief format: structured markdown with clear sections

- [ ] **Step 2: Commit**

```bash
git add agents/dashboard-art-director.md
git commit -m "feat: add dashboard-art-director agent for COMPLEX dashboards"
```

### Task 6: Update scraper.md

**Files:**
- Edit: `agents/scraper.md`

- [ ] **Step 1: Add strict JSON output format**

Read `agents/scraper.md`. Add to the end of instructions:

"ALWAYS end your response with a JSON block:
```json
{
  "source": "...",
  "status": "SUCCESS|PARTIAL|FAIL",
  "records_count": N,
  "data": [...],
  "issues": [...],
  "confidence": "High|Medium|Low"
}
```"

- [ ] **Step 2: Add credit limit**

Add rule: "Maximum 5 Firecrawl CLI requests (search + scrape combined) per source. If you need more, stop and report what you have."

- [ ] **Step 3: Commit**

```bash
git add agents/scraper.md
git commit -m "feat: add strict JSON output and credit limit to scraper agent"
```

### Task 7: Update reviewer agents with VERDICT format

**Files:**
- Edit: `agents/data-quality-reviewer.md`
- Edit: `agents/report-reviewer.md`

- [ ] **Step 1: Add VERDICT format to data-quality-reviewer.md**

Add to end of instructions:
"ALWAYS end your response with exactly one of:
`## VERDICT: Approved` or `## VERDICT: Issues Found` followed by bullet list of issues with severity (CRITICAL/WARNING/INFO)."

- [ ] **Step 2: Add VERDICT format to report-reviewer.md**

Same addition.

- [ ] **Step 3: Commit**

```bash
git add agents/data-quality-reviewer.md agents/report-reviewer.md
git commit -m "feat: add mandatory VERDICT format to reviewer agents"
```

### Task 8: Enhance dashboard-auditor.md

**Files:**
- Edit: `agents/dashboard-auditor.md`

- [ ] **Step 1: Update auditor checklist**

Read `agents/dashboard-auditor.md`. Add to checklist:
- Check: tooltips not overflowing (max-width applied)
- Check: numbers formatted (no raw 1000000, use K/M)
- Check: no empty states visible when data exists
- Check: footer present with metadata
- Check: N/A values shown as gray badges, not empty
- Check: responsive sidebar collapses on narrow viewport
- Reference `design-rules.md` for anti-patterns to check against
- Add VERDICT format (same as other reviewers)

- [ ] **Step 2: Commit**

```bash
git add agents/dashboard-auditor.md
git commit -m "feat: enhance dashboard-auditor with design-rules checklist"
```

---

## Chunk 5: Orchestrator & Phase Updates

### Task 9: Rewrite SKILL.md as thin orchestrator

**Files:**
- Rewrite: `skills/superscrape/SKILL.md`

- [ ] **Step 1: Write new SKILL.md**

Rewrite to ~80 lines containing ONLY:
1. Frontmatter (name, description with trigger phrases)
2. CRITICAL RULES table (7 rules, compact)
3. Resume Protocol (check `.superscrape-session.json`, determine phase, load it)
4. Phase Table (11 rows: phase → file → gate condition)
5. TodoWrite initialization template (11 phases)
6. Output directory format
7. Session file format (version: 4, with complexity field)

Remove ALL phase-specific content. Each phase lives in its own file.

- [ ] **Step 2: Verify orchestrator is complete**

Read back. Confirm:
- All 7 CRITICAL RULES present
- Phase table has 11 entries matching spec
- Resume protocol checks `output/*/.superscrape-session.json`
- Session file includes `version: 4` and `complexity` field
- Total ~80 lines

- [ ] **Step 3: Commit**

```bash
git add skills/superscrape/SKILL.md
git commit -m "refactor: rewrite SKILL.md as thin orchestrator (~80 lines)

All phase-specific logic moved to phases/*.md files.
Orchestrator contains only: critical rules, resume protocol,
phase table with gates, TodoWrite template."
```

### Task 10: Update phase files with gate checks, state saves, and quality improvements

**Files:**
- Edit: all 11 `skills/superscrape/phases/phase-*.md` files

**Note:** Phase files already exist from v3. This task edits them in place. The spec's "NEW" label refers to the v3 change.

- [ ] **Step 1: Add pre-check to each phase file**

For each phase file, add at the top (after frontmatter/title):

```
## Pre-check
Run: `test -f output/{dir}/_state/{required_file} && echo "GATE OK" || echo "GATE FAIL"`
If GATE FAIL → do not proceed, return to previous phase.
```

Use `test -f` for file existence gates, `grep -q` for content gates (Phase 4 quality_review).

- [ ] **Step 2: Add state save to each phase file**

For each phase file, add at the end:

```
## Save State
Write to `_state/{file}.json`: [specific content for this phase]
Update `.superscrape-session.json`: current_phase → next phase

## Next
Read `phases/phase-{next}.md` and continue.
```

- [ ] **Step 3: Update Phase 5b with complexity computation**

Add to phase-5b-dashboard-choice.md:
- Compute complexity (SIMPLE/MEDIUM/COMPLEX) based on record count and column count
- Save complexity to `.superscrape-session.json`
- Pass complexity to Phase 5c

- [ ] **Step 4: Update Phase 5c to reference dashboard-designer**

Change dispatch from `superscraper:dashboard-generator` to `superscraper:dashboard-designer`.
Add complexity branching:
- If COMPLEX → dispatch art-director first, pass brief to designer
- If art-director fails or returns unusable brief → fallback to MEDIUM pipeline (designer uses decision table directly)
- If SIMPLE/MEDIUM → dispatch designer directly

- [ ] **Step 5: Add dead project detection to Phase 3**

Add to phase-3-collect.md:
- After each scraper agent returns, check status field
- If FAIL with 404 → log to `_state/errors.json` with root cause: "Source returned 404, likely dead project"
- If FAIL with timeout or empty → log root cause
- Show progress after each agent: "3/5 sources collected (1 failed: DTF.ru 404)"

- [ ] **Step 6: Add cross-validation to Phase 4**

Add to phase-4-normalize.md (after merge, before quality reviewer):
- For each entity found in 3+ sources, compare numeric values
- If >30% discrepancy → add `"conflicting_data": true` flag to that record in normalized.json
- Include discrepancy details in quality reviewer input

- [ ] **Step 7: Add Firecrawl credit economy**

Phase 0 (phase-0-onboarding.md):
- After `firecrawl --status`, parse and record available credits in `_state/credits.json`
- If credits < 20 → warn user: "Low Firecrawl credits (X remaining). May not complete all sources."

Phase 3 (phase-3-collect.md):
- Read credits from `_state/credits.json`
- Distribute evenly: max_per_source = min(5, total_credits / source_count)
- Pass credit limit to each scraper agent in prompt

- [ ] **Step 8: Add UX improvements to phase files**

Phase 3 checkpoint (phase-3-collect.md):
- After all scrapers complete, show first 3 records from each source
- AskUserQuestion: "Data looks correct? Proceed to normalization?"

Rate limit handling (phase-3-collect.md):
- If rate limit detected → save current state → tell user: "Rate limit reached. Data saved. Say 'continue' when ready."

Phase 5b + 5e mandatory (phase-5b, phase-5e):
- Both already separate files (cannot be skipped by design)
- Add explicit: "This phase is MANDATORY. Do not skip."

- [ ] **Step 9: Commit**

```bash
git add skills/superscrape/phases/
git commit -m "feat: add gate checks, state saves, complexity scaling to all phases"
```

---

## Chunk 6: Sync Cache & Push

### Task 11: Sync plugin cache and push

**Files:**
- Sync: `~/.claude/plugins/cache/king-sheol/superscraper/1.0.0/`

- [ ] **Step 1: Sync all files to plugin cache**

```bash
rsync -av --delete \
  --exclude='.git' --exclude='output' --exclude='docs' --exclude='.claude' \
  "C:/Users/OF-1/Documents/Claude Workspace/Code/Superscrapper/" \
  "C:/Users/OF-1/.claude/plugins/cache/king-sheol/superscraper/1.0.0/"
```

- [ ] **Step 2: Verify cache has all new files**

```bash
ls -la ~/.claude/plugins/cache/king-sheol/superscraper/1.0.0/agents/
ls -la ~/.claude/plugins/cache/king-sheol/superscraper/1.0.0/skills/superscrape/references/
ls -la ~/.claude/plugins/cache/king-sheol/superscraper/1.0.0/skills/superscrape/phases/
```

Confirm:
- `dashboard-designer.md` exists (not dashboard-generator.md)
- `dashboard-art-director.md` exists
- `design-rules.md` exists (not dashboard-template.md, not design-system.md)
- All 11 phase files present

- [ ] **Step 3: Push to GitHub**

```bash
cd "C:/Users/OF-1/Documents/Claude Workspace/Code/Superscrapper"
git push
```

- [ ] **Step 4: Commit sync confirmation**

Verify no uncommitted changes remain:
```bash
git status
```

---

## Execution Notes

**Task dependencies:**
- Task 1 (design-rules) must complete before Tasks 2-3 (kit files reference it)
- Tasks 2 and 3 (HTML kit, Streamlit kit) are independent of each other
- Tasks 4-8 (agents) are independent of each other and of Tasks 2-3
- Task 9 (orchestrator) can run in parallel with Tasks 2-8
- Task 10 (phases) depends on Task 9 (orchestrator defines phase table)
- Task 11 (sync) must be last

**Parallel execution opportunities:**
- After Task 1: Tasks 2, 3, 4, 5, 6, 7, 8, 9 can all run in parallel
- After Task 9: Task 10
- After all: Task 11

**No tests:** This is a prompt-only codebase (all .md files). Quality is verified by spec review + real test run after deployment.

**Validation:** After Task 11, restart Claude Code and run `/superscrape CRM systems` to verify the full pipeline works with the new design system.
