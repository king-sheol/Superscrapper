# Superscraper v3: Structural Hardening + Component Library Upgrade — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Harden the orchestrator with resume protocol + session versioning + gate checks, and replace Plotly/vanilla JS dashboards with ECharts + AG Grid + Tailwind.

**Architecture:** Existing phase-based orchestrator (SKILL.md + 11 phase files) gets session versioning, credit tracking, and executable gate pre-checks. Dashboard templates are replaced with two kit files (HTML and Streamlit) using ECharts/AG Grid. Subagents get minor format updates.

**Tech Stack:** ECharts 5.x, AG Grid Community 31.x, Tailwind CSS CDN, Lucide Icons 0.460, streamlit-echarts, streamlit-aggrid

**Spec:** `docs/superpowers/specs/2026-03-18-superscraper-v3-structural-hardening.md`

---

## File Map

### Modified files:
| File | Responsibility | Change |
|------|---------------|--------|
| `skills/superscrape/SKILL.md` | Orchestrator | Add session version check, multiple session handling, credits.json to state table |
| `skills/superscrape/phases/phase-0-onboarding.md` | Firecrawl setup | Add credits.json save, executable pre-check |
| `skills/superscrape/phases/phase-1-clarify.md` | Task clarification | Add session file creation, executable pre-check |
| `skills/superscrape/phases/phase-2-discover.md` | Source discovery | Add executable pre-check |
| `skills/superscrape/phases/phase-3-collect.md` | Data collection | Add credit budget distribution, progress reporting, executable pre-check |
| `skills/superscrape/phases/phase-4-normalize.md` | Normalization | Add cross-validation, dead project detection, executable pre-check |
| `skills/superscrape/phases/phase-5a-report-and-data.md` | Report + XLSX | Add executable pre-check |
| `skills/superscrape/phases/phase-5b-dashboard-choice.md` | Dashboard choice | Add executable pre-check |
| `skills/superscrape/phases/phase-5c-dashboard-generate.md` | Dashboard gen | Rewrite to reference new kit files instead of old template |
| `skills/superscrape/phases/phase-5d-review.md` | Report review | Add review cap fallback, executable pre-check |
| `skills/superscrape/phases/phase-5e-deploy.md` | Deploy | Add executable pre-check |
| `skills/superscrape/phases/phase-6-verify.md` | Verification | Add executable pre-check |
| `skills/superscrape/references/dashboard-template.md` | Decision table | Rewrite: remove Plotly code, keep decision table + pointers to kits |
| `agents/dashboard-generator.md` | Dashboard agent | Update to reference kit files, remove Plotly references |
| `agents/report-reviewer.md` | Report reviewer | Verify VERDICT format (already present) |

### New files:
| File | Responsibility |
|------|---------------|
| `skills/superscrape/references/dashboard-html-kit.md` | Complete HTML dashboard code snippets (ECharts + AG Grid + Tailwind) |
| `skills/superscrape/references/dashboard-streamlit-kit.md` | Complete Streamlit dashboard code snippets (streamlit-echarts + streamlit-aggrid) |

### Unchanged files (already have required formats):
| File | Status |
|------|--------|
| `agents/scraper.md` | Already has JSON output format (lines 66-84) — no changes needed |
| `agents/data-quality-reviewer.md` | Already has VERDICT format (lines 99-103) — no changes needed |
| `agents/report-writer.md` | No changes per spec |
| `agents/report-reviewer.md` | Already has VERDICT format — verify only |

### Deferred to future iteration:
| Feature | Reason |
|---------|--------|
| Sparklines in AG Grid cells | Stretch goal per spec — complex lifecycle management, fallback to main line chart |
| Mobile drawer for filters | Basic Tailwind responsive (sidebar collapses on mobile) is sufficient for v3. Full drawer pattern deferred. |

---

## Chunk 1: Orchestrator + Phase Pre-checks

### Task 1: Update SKILL.md — session versioning + credits

**Files:**
- Modify: `skills/superscrape/SKILL.md`

- [ ] **Step 1: Add session version and credits to SKILL.md**

Add `version: 3` check to Resume Protocol section. Add `credits.json` to state files table. Add multiple session handling.

In `skills/superscrape/SKILL.md`, replace the Resume Protocol section (lines 25-32) with:

```markdown
## Resume Protocol

On "продолжай" / "continue" / any resume:

1. Search for `output/*/.superscrape-session.json`
2. If multiple found — sort by `created_at` desc, show user a list via AskUserQuestion: "Found N sessions: [topic1] (Phase X), [topic2] (Phase Y). Which to continue, or start new?"
3. If one found — check `version` field:
   - If missing or < 3 → v2 session. Ask: "Found session from previous plugin version. Start fresh or attempt continue?"
   - If = 3 → resume normally
4. If resume — read `_state/` files to determine last completed phase, re-init TodoWrite from that point
5. If not found or user chooses fresh — start from Phase 0
```

Add `credits.json` row to state files table after line 51:

```markdown
| `credits.json` | Phase 0 | initial Firecrawl credit count |
```

- [ ] **Step 2: Verify SKILL.md is under 100 lines**

Run: `wc -l skills/superscrape/SKILL.md`
Expected: ≤100 lines

- [ ] **Step 3: Commit**

```bash
git add skills/superscrape/SKILL.md
git commit -m "feat(orchestrator): add session v3 versioning, credits tracking, multi-session handling"
```

### Task 2: Add executable pre-checks to all 11 phase files

**Files:**
- Modify: all 11 files in `skills/superscrape/phases/`

Each phase file needs a `## Pre-check` section at the top (after the `# Phase` heading) with a bash command that verifies the previous phase's exit gate. If the check fails, the bot sees "GATE FAIL" and knows to go back.

- [ ] **Step 1: Add pre-check to phase-0-onboarding.md**

Add after the `# Phase 0` heading:

```markdown
## Pre-check
No pre-check — this is the first phase.
```

- [ ] **Step 2: Add pre-check to phase-1-clarify.md**

Add after the heading:

```markdown
## Pre-check
Run: `firecrawl --status 2>&1 | grep -q "Authenticated" && echo "GATE OK" || echo "GATE FAIL: Phase 0 not complete — Firecrawl not authenticated"`
If GATE FAIL — go back to phase-0-onboarding.md.
```

- [ ] **Step 3: Add pre-check to phase-2-discover.md**

```markdown
## Pre-check
Run: `cat {output_dir}/_state/config.json > /dev/null 2>&1 && echo "GATE OK" || echo "GATE FAIL: Phase 1 not complete — config.json missing"`
If GATE FAIL — go back to phase-1-clarify.md.
```

- [ ] **Step 4: Add pre-check to phase-3-collect.md**

```markdown
## Pre-check
Run: `cat {output_dir}/_state/sources.json > /dev/null 2>&1 && echo "GATE OK" || echo "GATE FAIL: Phase 2 not complete — sources.json missing"`
If GATE FAIL — go back to phase-2-discover.md.
```

- [ ] **Step 5: Add pre-check to phase-4-normalize.md**

```markdown
## Pre-check
Run: `ls {output_dir}/_state/raw_data_*.json > /dev/null 2>&1 && echo "GATE OK" || echo "GATE FAIL: Phase 3 not complete — no raw_data files"`
If GATE FAIL — go back to phase-3-collect.md.
```

- [ ] **Step 6: Add pre-check to phase-5a-report-and-data.md**

```markdown
## Pre-check
Run: `grep -q '"quality_review"' {output_dir}/_state/normalized.json 2>/dev/null && echo "GATE OK" || echo "GATE FAIL: Phase 4 not complete — normalized.json missing or no quality_review"`
If GATE FAIL — go back to phase-4-normalize.md.
```

- [ ] **Step 7: Add pre-check to phase-5b-dashboard-choice.md**

```markdown
## Pre-check
Run: `test -f {output_dir}/report.md && test -f {output_dir}/data.csv && test -f {output_dir}/data.xlsx && echo "GATE OK" || echo "GATE FAIL: Phase 5a not complete — report/data files missing"`
If GATE FAIL — go back to phase-5a-report-and-data.md.
```

- [ ] **Step 8: Add pre-check to phase-5c-dashboard-generate.md**

```markdown
## Pre-check
Run: `cat {output_dir}/_state/dashboard_choice.json > /dev/null 2>&1 && echo "GATE OK" || echo "GATE FAIL: Phase 5b not complete — dashboard_choice.json missing"`
If GATE FAIL — go back to phase-5b-dashboard-choice.md.
```

- [ ] **Step 9: Add pre-check to phase-5d-review.md**

```markdown
## Pre-check
Run: `choice=$(cat {output_dir}/_state/dashboard_choice.json 2>/dev/null | grep -o '"choice":"[^"]*"' | cut -d'"' -f4); if [ "$choice" = "none" ]; then echo "GATE OK (no dashboard)"; elif ls {output_dir}/dashboard.* > /dev/null 2>&1; then echo "GATE OK"; else echo "GATE FAIL: Phase 5c not complete — dashboard files missing"; fi`
If GATE FAIL — go back to phase-5c-dashboard-generate.md.
```

- [ ] **Step 10: Add pre-check to phase-5e-deploy.md**

```markdown
## Pre-check
Run: `echo "GATE OK — review phase has no file gate, orchestrator verifies VERDICT"`
Note: The orchestrator checks the report-reviewer's VERDICT before loading this phase. No file-based gate needed.
```

- [ ] **Step 11: Add pre-check to phase-6-verify.md**

```markdown
## Pre-check
Run: `echo "GATE OK — deploy phase has no file gate, orchestrator verifies completion"`
Note: The orchestrator confirms Phase 5e completed (deploy done or user declined) before loading Phase 6.
```

- [ ] **Step 8: Commit**

```bash
git add skills/superscrape/phases/
git commit -m "feat(phases): add executable pre-check gates to all 11 phase files"
```

### Task 3: Update phase-0 to save credits.json

**Files:**
- Modify: `skills/superscrape/phases/phase-0-onboarding.md`

- [ ] **Step 1: Add credit tracking to phase-0**

After the Firecrawl authentication step, add:

```markdown
## Save Firecrawl Credits
After `firecrawl --status` succeeds, parse the credit count and save:
```bash
firecrawl --status 2>&1 | grep -oP '\d+ credits' | grep -oP '\d+' > /tmp/fc_credits.txt
```
Then write `_state/credits.json`:
```json
{"initial": <credit_count>, "timestamp": "<ISO timestamp>"}
```
```

- [ ] **Step 2: REPLACE session file block in phase-1-clarify.md**

The current phase-1-clarify.md (lines 56-63) writes an old v2 session format:
```json
{"created": "YYYY-MM-DD", "topic": "...", "completed_phases": [0, 1]}
```
REPLACE this entire block (lines 56-63) with the v3 format:

```markdown
Write `{output_dir}/.superscrape-session.json`:
```json
{
  "version": 3,
  "output_dir": "{output_dir}",
  "topic": "{topic}",
  "language": "{detected_language}",
  "current_phase": "phase-1",
  "completed_phases": ["phase-0", "phase-1"],
  "created_at": "{ISO timestamp}"
}
```
```

- [ ] **Step 3: Commit**

```bash
git add skills/superscrape/phases/phase-0-onboarding.md skills/superscrape/phases/phase-1-clarify.md
git commit -m "feat(phases): add credit tracking in phase-0, session file creation in phase-1"
```

### Task 3b: Add session file maintenance to all phase files

**Files:**
- Modify: all 11 files in `skills/superscrape/phases/`

Per spec: "Each phase updates session file on start and completion" and "Phase 6 deletes session file."

- [ ] **Step 1: Add session update to each phase file's "Done" section**

At the end of each phase file (before "Phase N complete"), add:

```markdown
## Update Session
Update `.superscrape-session.json`: set `current_phase` to the NEXT phase name, add current phase to `completed_phases`.
```

For phases 0-5e, the pattern is:
```
Update session: current_phase → "phase-{next}", completed_phases += ["phase-{current}"]
```

- [ ] **Step 2: Add session file deletion to phase-6-verify.md**

At the end of phase-6-verify.md, add:

```markdown
## Cleanup
Delete `.superscrape-session.json` — session is complete. Only incomplete sessions should persist for resume.
```

- [ ] **Step 3: Add `{output_dir}` resolution note to SKILL.md**

In the Dispatch Loop section of SKILL.md, add:

```markdown
When reading a phase file, substitute `{output_dir}` with the actual output directory path (from session file or from Phase 1 config). Phase files use `{output_dir}` as a placeholder — the orchestrator resolves it before executing pre-checks.
```

- [ ] **Step 4: Commit**

```bash
git add skills/superscrape/phases/ skills/superscrape/SKILL.md
git commit -m "feat(phases): add session file maintenance to all phases, delete on Phase 6 completion"
```

### Task 4: Update phase-3 with credit budget + progress reporting

**Files:**
- Modify: `skills/superscrape/phases/phase-3-collect.md`

- [ ] **Step 1: Add credit budget calculation**

At the start of phase-3 instructions, add:

```markdown
## Credit Budget
Read `_state/credits.json` → get `initial` count.
Calculate budget per source: `floor(initial / number_of_sources)`.
Include in each scraper agent's prompt: "Budget: max {N} Firecrawl requests for this source."
```

- [ ] **Step 2: Add progress reporting instruction**

After each scraper agent dispatch returns, add:

```markdown
## Progress Reporting
After each scraper agent returns:
1. Save result immediately: `_state/raw_data_{source_slug}.json`
2. Message in chat: "{completed}/{total} sources collected"
3. If rate limit hit: "Rate limit reached, data saved. Say 'continue' when ready."
```

- [ ] **Step 3: Commit**

```bash
git add skills/superscrape/phases/phase-3-collect.md
git commit -m "feat(phase-3): add credit budget distribution and progress reporting"
```

### Task 5: Update phase-4 with cross-validation + dead project detection

**Files:**
- Modify: `skills/superscrape/phases/phase-4-normalize.md`

- [ ] **Step 1: Add cross-validation instruction**

In the normalization instructions, add:

```markdown
## Cross-Validation
During normalization: if the same entity appears in 3+ sources, compare numeric values.
If divergence >30% on any metric — add field `"conflicting_data": true` and note which values differ.
```

- [ ] **Step 2: Add dead project detection**

```markdown
## Dead Project Detection
For each entity: if official site URL returns 404 or if last known activity date is >6 months ago,
add field `"possibly_dead": true` with explanation.
```

- [ ] **Step 3: Add review iteration cap fallback**

Ensure phase-4 includes: after 3 failed reviewer iterations, ask user "Accept current state or abort?" via AskUserQuestion.

- [ ] **Step 4: Commit**

```bash
git add skills/superscrape/phases/phase-4-normalize.md
git commit -m "feat(phase-4): add cross-validation, dead project detection, review cap fallback"
```

---

## Chunk 2: Dashboard Kit Files (HTML)

### Task 6: Rewrite dashboard-template.md

**Files:**
- Modify: `skills/superscrape/references/dashboard-template.md`

- [ ] **Step 1: Replace entire file with decision table + pointers**

Remove all Plotly code, Docker configs. Keep only:
1. Decision table (data type → chart types) from spec
2. Auto-detection rules (dual verification)
3. Color palette (8 colors)
4. Typography (system fonts, tabular-nums)
5. Pointers: "For HTML → read dashboard-html-kit.md", "For Streamlit → read dashboard-streamlit-kit.md"
6. Docker deployment configs (Dockerfile, docker-compose.yml, nginx.conf) — move from old template

```markdown
# Dashboard Configuration

## Decision Table: Data Type → Visualizations

| Data Type | KPI Cards | Primary Chart | Comparison | Table |
|-----------|-----------|---------------|------------|-------|
| Rating/comparison | Top-1, avg score, total, sources | ECharts horizontal bar (gradient) | ECharts radar (top 5) | AG Grid: sort by rating |
| Prices | Min/max/median, best value | ECharts scatter | ECharts boxplot | AG Grid: conditional coloring |
| Time series | Latest, trend %, min/max | ECharts line (area fill) | ECharts heatmap | AG Grid (sparklines optional) |
| Segment | Leader share, count, total | ECharts treemap/sunburst | ECharts stacked bar | AG Grid: group by segment |
| Fallback | total records, sources, date | Horizontal bar | Scatter | Full AG Grid |

## Auto-Detection (Dual Verification)
1. Read column_types from normalized.json
2. Read first 5 rows of data.csv — parseFloat each value
3. If >80% parse as numbers → numeric column
4. Check for dates: YYYY-MM-DD or DD.MM.YYYY
5. If column_types and data disagree → trust data

## Color Palette
Dark theme base: `#0f172a`
Chart colors: `#60a5fa, #34d399, #fbbf24, #f87171, #a78bfa, #22d3ee, #fb923c, #e879f9`

## Typography
Font: `-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`
Numbers: `font-variant-numeric: tabular-nums`

## Kit Files
- HTML dashboard → Read `dashboard-html-kit.md`
- Streamlit dashboard → Read `dashboard-streamlit-kit.md`

## Docker Deployment (for Streamlit)
[Keep existing Dockerfile, docker-compose.yml, nginx.conf from current file]
```

- [ ] **Step 2: Commit**

```bash
git add skills/superscrape/references/dashboard-template.md
git commit -m "refactor(dashboard-template): replace Plotly code with decision table + kit pointers"
```

### Task 7: Create dashboard-html-kit.md

**Files:**
- Create: `skills/superscrape/references/dashboard-html-kit.md`

This is the largest new file. Contains complete working HTML/JS code snippets for each dashboard component.

- [ ] **Step 1: Write the Base section**

CDN links, Tailwind dark theme config, layout grid, system fonts:

```markdown
# HTML Dashboard Kit

## Base

```html
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{TOPIC} — Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/ag-grid-community@31/dist/ag-grid-community.min.js"></script>
    <link href="https://cdn.jsdelivr.net/npm/ag-grid-community@31/styles/ag-grid.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/ag-grid-community@31/styles/ag-theme-alpine.css" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@0.460"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: { extend: { colors: { base: '#0f172a', surface: '#1e293b', border: '#334155' } } }
        }
    </script>
</head>
<body class="bg-base text-slate-200 font-sans" style="font-variant-numeric: tabular-nums">
    <div class="max-w-7xl mx-auto px-4 py-8">
        <header class="text-center mb-8">
            <h1 class="text-3xl font-bold text-blue-400">{TOPIC}</h1>
            <p class="text-slate-500 mt-2">{DATE} | {N} records | {M} sources</p>
        </header>
        <!-- KPI cards -->
        <div id="kpi-grid" class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8"></div>
        <!-- Filter sidebar + main content -->
        <div class="flex flex-col lg:flex-row gap-6">
            <aside id="filters" class="lg:w-64 bg-surface rounded-xl p-4 space-y-4 lg:sticky lg:top-4 lg:self-start"></aside>
            <main class="flex-1 space-y-6">
                <section class="bg-surface rounded-xl p-6"><h2 class="text-lg font-semibold mb-4">Overview</h2><div id="chart-primary" style="height:400px"></div></section>
                <section class="bg-surface rounded-xl p-6"><h2 class="text-lg font-semibold mb-4">Comparison</h2><div id="chart-comparison" style="height:400px"></div></section>
                <section class="bg-surface rounded-xl p-6"><h2 class="text-lg font-semibold mb-4">Data</h2><div id="data-table" style="height:500px" class="ag-theme-alpine-dark"></div></section>
            </main>
        </div>
        <!-- Detail panel -->
        <div id="detail-panel" class="fixed inset-y-0 right-0 w-96 bg-surface shadow-2xl transform translate-x-full transition-transform duration-300 z-50 overflow-y-auto p-6"></div>
    </div>
```
```

- [ ] **Step 2: Write the KPI Cards section**

```markdown
## KPI Cards

```javascript
function renderKPIs(data, numericCols) {
    const grid = document.getElementById('kpi-grid');
    const icons = ['bar-chart-2', 'trending-up', 'hash', 'database'];

    // Always show total records
    const kpis = [{ label: 'Total Records', value: data.length, icon: 'database' }];

    // Auto-detect KPIs from numeric columns
    numericCols.slice(0, 3).forEach((col, i) => {
        const vals = data.map(r => parseFloat(r[col])).filter(v => !isNaN(v));
        if (vals.length === 0) return;
        const avg = (vals.reduce((a,b) => a+b, 0) / vals.length).toFixed(1);
        const max = Math.max(...vals);
        kpis.push({ label: `Avg ${col}`, value: avg, detail: `Max: ${max}`, icon: icons[i+1] || 'hash' });
    });

    grid.innerHTML = kpis.map(k => `
        <div class="bg-surface border border-border rounded-xl p-5 text-center">
            <i data-lucide="${k.icon}" class="w-5 h-5 mx-auto text-slate-500 mb-2"></i>
            <div class="text-sm text-slate-500 uppercase">${k.label}</div>
            <div class="text-2xl font-bold text-blue-400 my-1 count-up">${k.value}</div>
            ${k.detail ? `<div class="text-xs text-slate-400">${k.detail}</div>` : ''}
        </div>
    `).join('');
    lucide.createIcons();

    // countUp animation
    document.querySelectorAll('.count-up').forEach(el => {
        const target = parseFloat(el.textContent);
        if (isNaN(target)) return;
        let current = 0;
        const step = target / 30;
        const timer = setInterval(() => {
            current += step;
            if (current >= target) { el.textContent = target % 1 === 0 ? target : target.toFixed(1); clearInterval(timer); }
            else { el.textContent = current % 1 === 0 ? Math.floor(current) : current.toFixed(1); }
        }, 20);
    });
}
```
```

- [ ] **Step 3: Write the Charts section**

ECharts configs for each chart type. The dashboard-generator selects configs based on decision table.

```markdown
## Charts

### Color palette constant
```javascript
const COLORS = ['#60a5fa','#34d399','#fbbf24','#f87171','#a78bfa','#22d3ee','#fb923c','#e879f9'];
const CHART_BG = '#1e293b';
```

### Horizontal Bar (Rating/Comparison)
```javascript
function chartHorizontalBar(containerId, data, nameCol, valueCol) {
    const chart = echarts.init(document.getElementById(containerId));
    const sorted = [...data].sort((a,b) => parseFloat(a[valueCol]) - parseFloat(b[valueCol]));
    chart.setOption({
        backgroundColor: CHART_BG,
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        grid: { left: '20%', right: '10%', top: 20, bottom: 20 },
        xAxis: { type: 'value', axisLabel: { color: '#94a3b8' }, splitLine: { lineStyle: { color: '#334155' } } },
        yAxis: { type: 'category', data: sorted.map(r => r[nameCol]), axisLabel: { color: '#94a3b8', width: 120, overflow: 'truncate' } },
        series: [{
            type: 'bar', data: sorted.map(r => parseFloat(r[valueCol])),
            itemStyle: { color: new echarts.graphic.LinearGradient(0,0,1,0, [{offset:0, color: COLORS[0]+'88'}, {offset:1, color: COLORS[0]}]), borderRadius: [0,4,4,0] },
            animationDuration: 1500, animationEasing: 'cubicOut'
        }]
    });
    chart.on('click', params => applyFilters({ [nameCol]: params.name }));
    window.addEventListener('resize', () => chart.resize());
    return chart;
}
```

### Radar (Top 5 comparison)
```javascript
function chartRadar(containerId, data, nameCol, numericCols) {
    const chart = echarts.init(document.getElementById(containerId));
    const top5 = [...data].sort((a,b) => parseFloat(b[numericCols[0]]) - parseFloat(a[numericCols[0]])).slice(0, 5);
    const maxVals = numericCols.map(c => Math.max(...data.map(r => parseFloat(r[c]) || 0)));
    chart.setOption({
        backgroundColor: CHART_BG,
        tooltip: {},
        legend: { data: top5.map(r => r[nameCol]), textStyle: { color: '#94a3b8' }, bottom: 0 },
        radar: { indicator: numericCols.map((c, i) => ({ name: c, max: maxVals[i] * 1.1 })), axisName: { color: '#94a3b8' }, splitLine: { lineStyle: { color: '#334155' } }, splitArea: { areaStyle: { color: ['transparent'] } } },
        series: [{ type: 'radar', data: top5.map((r, i) => ({ name: r[nameCol], value: numericCols.map(c => parseFloat(r[c]) || 0), lineStyle: { color: COLORS[i] }, itemStyle: { color: COLORS[i] }, areaStyle: { color: COLORS[i] + '22' } })) }]
    });
    window.addEventListener('resize', () => chart.resize());
    return chart;
}
```

### Scatter (Price vs metric)
```javascript
function chartScatter(containerId, data, xCol, yCol, nameCol, colorCol) {
    const chart = echarts.init(document.getElementById(containerId));
    const categories = colorCol ? [...new Set(data.map(r => r[colorCol]))] : ['All'];
    chart.setOption({
        backgroundColor: CHART_BG,
        tooltip: { trigger: 'item', formatter: p => `${p.data[2]}<br>${xCol}: ${p.data[0]}<br>${yCol}: ${p.data[1]}` },
        legend: colorCol ? { data: categories, textStyle: { color: '#94a3b8' }, bottom: 0 } : undefined,
        xAxis: { name: xCol, nameTextStyle: { color: '#94a3b8' }, axisLabel: { color: '#94a3b8' }, splitLine: { lineStyle: { color: '#334155' } } },
        yAxis: { name: yCol, nameTextStyle: { color: '#94a3b8' }, axisLabel: { color: '#94a3b8' }, splitLine: { lineStyle: { color: '#334155' } } },
        series: categories.map((cat, i) => ({
            type: 'scatter', name: cat,
            data: data.filter(r => !colorCol || r[colorCol] === cat).map(r => [parseFloat(r[xCol]) || 0, parseFloat(r[yCol]) || 0, r[nameCol]]),
            itemStyle: { color: COLORS[i % COLORS.length] }, symbolSize: 12
        }))
    });
    window.addEventListener('resize', () => chart.resize());
    return chart;
}
```

### Line Chart (Time series)
```javascript
function chartLine(containerId, data, dateCol, valueCol) {
    const chart = echarts.init(document.getElementById(containerId));
    const sorted = [...data].sort((a,b) => new Date(a[dateCol]) - new Date(b[dateCol]));
    chart.setOption({
        backgroundColor: CHART_BG,
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: sorted.map(r => r[dateCol]), axisLabel: { color: '#94a3b8' } },
        yAxis: { type: 'value', axisLabel: { color: '#94a3b8' }, splitLine: { lineStyle: { color: '#334155' } } },
        dataZoom: [{ type: 'inside' }, { type: 'slider' }],
        series: [{ type: 'line', data: sorted.map(r => parseFloat(r[valueCol]) || 0), smooth: true,
            areaStyle: { color: new echarts.graphic.LinearGradient(0,0,0,1, [{offset:0, color: COLORS[0]+'66'}, {offset:1, color: 'transparent'}]) },
            lineStyle: { color: COLORS[0], width: 2 }, itemStyle: { color: COLORS[0] } }]
    });
    window.addEventListener('resize', () => chart.resize());
    return chart;
}
```
```

- [ ] **Step 4: Write the AG Grid Table section**

```markdown
## Table (AG Grid)

```javascript
function renderTable(containerId, data, columns) {
    const columnDefs = columns.map(col => ({
        field: col,
        sortable: true, filter: true, resizable: true,
        minWidth: 100,
        // Right-align numeric columns
        ...(data.some(r => !isNaN(parseFloat(r[col]))) ? { type: 'numericColumn', cellStyle: { textAlign: 'right' } } : {})
    }));

    const gridOptions = {
        columnDefs,
        rowData: data,
        defaultColDef: { flex: 1, minWidth: 80, filter: true, sortable: true, resizable: true },
        animateRows: true,
        pagination: true,
        paginationPageSize: 50,
        domLayout: 'normal',
        onRowClicked: (event) => showDetailPanel(event.data, columns),
        // Dark theme overrides
        getRowStyle: params => params.node.rowIndex % 2 === 0 ? { background: '#1e293b' } : { background: '#0f172a' },
    };

    const gridDiv = document.getElementById(containerId);
    new agGrid.Grid(gridDiv, gridOptions);

    // CSV export button
    const exportBtn = document.createElement('button');
    exportBtn.className = 'bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm mb-4';
    exportBtn.textContent = 'Export CSV';
    exportBtn.onclick = () => gridOptions.api.exportDataAsCsv();
    gridDiv.parentElement.insertBefore(exportBtn, gridDiv);

    return gridOptions;
}
```
```

- [ ] **Step 4b: Write remaining chart types (Boxplot, Heatmap, Treemap/Sunburst)**

Add to the Charts section:

```markdown
### Boxplot (Prices by category)
```javascript
function chartBoxplot(containerId, data, categoryCol, valueCol) {
    const chart = echarts.init(document.getElementById(containerId));
    const categories = [...new Set(data.map(r => r[categoryCol]))];
    const boxData = categories.map(cat => {
        const vals = data.filter(r => r[categoryCol] === cat).map(r => parseFloat(r[valueCol])).filter(v => !isNaN(v)).sort((a,b)=>a-b);
        const q1 = vals[Math.floor(vals.length*0.25)], q3 = vals[Math.floor(vals.length*0.75)];
        return [vals[0], q1, vals[Math.floor(vals.length*0.5)], q3, vals[vals.length-1]];
    });
    chart.setOption({
        backgroundColor: CHART_BG, tooltip: { trigger: 'item' },
        xAxis: { type: 'category', data: categories, axisLabel: { color: '#94a3b8' } },
        yAxis: { type: 'value', axisLabel: { color: '#94a3b8' }, splitLine: { lineStyle: { color: '#334155' } } },
        series: [{ type: 'boxplot', data: boxData, itemStyle: { color: COLORS[0], borderColor: COLORS[0] } }]
    });
    window.addEventListener('resize', () => chart.resize());
    return chart;
}
```

### Treemap (Segment analysis)
```javascript
function chartTreemap(containerId, data, categoryCol, valueCol) {
    const chart = echarts.init(document.getElementById(containerId));
    const groups = {};
    data.forEach(r => { const cat = r[categoryCol] || 'Other'; groups[cat] = (groups[cat] || 0) + (parseFloat(r[valueCol]) || 1); });
    chart.setOption({
        backgroundColor: CHART_BG, tooltip: { formatter: '{b}: {c}' },
        series: [{ type: 'treemap', data: Object.entries(groups).map(([name, value], i) => ({ name, value, itemStyle: { color: COLORS[i % COLORS.length] } })),
            label: { color: '#fff' }, breadcrumb: { show: false } }]
    });
    window.addEventListener('resize', () => chart.resize());
    return chart;
}
```

### Heatmap (Time series day×hour — use when date+time data available)
```javascript
function chartHeatmap(containerId, data, dateCol, valueCol) {
    const chart = echarts.init(document.getElementById(containerId));
    // Group data by day and hour for heatmap cells
    const heatData = data.map((r, i) => [i % 7, Math.floor(i / 7), parseFloat(r[valueCol]) || 0]);
    chart.setOption({
        backgroundColor: CHART_BG, tooltip: { position: 'top' },
        grid: { top: 10, bottom: 40, left: 60, right: 20 },
        xAxis: { type: 'category', data: ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'], axisLabel: { color: '#94a3b8' } },
        yAxis: { type: 'category', axisLabel: { color: '#94a3b8' } },
        visualMap: { min: 0, max: Math.max(...heatData.map(d=>d[2])), calculable: true, orient: 'horizontal', left: 'center', bottom: 0, inRange: { color: ['#334155', COLORS[0]] }, textStyle: { color: '#94a3b8' } },
        series: [{ type: 'heatmap', data: heatData, label: { show: false } }]
    });
    window.addEventListener('resize', () => chart.resize());
    return chart;
}
```
```

**Note on Sparklines:** Per spec, sparklines (ECharts mini-instances in AG Grid cells) are a STRETCH GOAL. Skip for v3 implementation. If time series data is present, use the main Line chart for trend visualization. Sparklines can be added in a future iteration.

- [ ] **Step 5: Write the Filters + Detail Panel + Assembly sections**

```markdown
## Filters

```javascript
let allData = [];
let filteredData = [];
let activeFilters = {};
let charts = {};
let gridApi = null;

function initFilters(data, categoricalCols, numericCols) {
    allData = data;
    filteredData = [...data];
    const container = document.getElementById('filters');

    // Text search
    container.innerHTML = `<input type="text" placeholder="Search..." class="w-full bg-base border border-border rounded-lg px-3 py-2 text-sm text-slate-200" oninput="applyFilters({_search: this.value})">`;

    // Categorical dropdowns
    categoricalCols.forEach(col => {
        const values = [...new Set(data.map(r => r[col]).filter(Boolean))].sort();
        const div = document.createElement('div');
        div.innerHTML = `<label class="text-xs text-slate-500 uppercase block mb-1">${col}</label>
            <select class="w-full bg-base border border-border rounded-lg px-2 py-1.5 text-sm text-slate-200" onchange="applyFilters({${col}: this.value})">
                <option value="">All</option>${values.map(v => `<option value="${v}">${v}</option>`).join('')}
            </select>`;
        container.appendChild(div);
    });

    // Reset button
    const resetBtn = document.createElement('button');
    resetBtn.className = 'w-full bg-slate-700 hover:bg-slate-600 text-slate-300 py-2 rounded-lg text-sm mt-2';
    resetBtn.textContent = 'Reset Filters';
    resetBtn.onclick = () => { activeFilters = {}; container.querySelectorAll('select').forEach(s => s.value = ''); container.querySelector('input').value = ''; applyFilters({}); };
    container.appendChild(resetBtn);
}

function applyFilters(newFilter) {
    Object.assign(activeFilters, newFilter);
    filteredData = allData.filter(row => {
        for (const [key, val] of Object.entries(activeFilters)) {
            if (!val || val === '') continue;
            if (key === '_search') { if (!JSON.stringify(row).toLowerCase().includes(val.toLowerCase())) return false; }
            else { if (row[key] !== val) return false; }
        }
        return true;
    });
    // Update all components
    renderKPIs(filteredData, Object.keys(allData[0]).filter(k => allData.some(r => !isNaN(parseFloat(r[k])))));
    // Re-render charts with filteredData (chart-type specific — dashboard-generator fills this in)
    if (gridApi) gridApi.api.setRowData(filteredData);
}
```

## Detail Panel

```javascript
function showDetailPanel(rowData, columns) {
    const panel = document.getElementById('detail-panel');
    panel.innerHTML = `
        <button onclick="closeDetailPanel()" class="absolute top-4 right-4 text-slate-400 hover:text-white text-xl">&times;</button>
        <h3 class="text-xl font-bold text-blue-400 mb-4 pr-8">${rowData[columns[0]]}</h3>
        ${columns.map(col => `<div class="mb-3"><span class="text-xs text-slate-500 uppercase block">${col}</span><span class="text-slate-200">${rowData[col] || 'N/A'}</span></div>`).join('')}
        ${rowData['Source'] ? `<a href="${rowData['Source']}" target="_blank" class="inline-block mt-4 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm">Open Source</a>` : ''}
    `;
    panel.classList.remove('translate-x-full');
}
function closeDetailPanel() { document.getElementById('detail-panel').classList.add('translate-x-full'); }
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeDetailPanel(); });
document.addEventListener('click', e => { const panel = document.getElementById('detail-panel'); if (!panel.contains(e.target) && !e.target.closest('.ag-row')) closeDetailPanel(); });
```

## Assembly Instructions

The dashboard-generator:
1. Starts with the Base HTML template
2. Embeds data as `const DATA = [...]` and `const METADATA = {...}` in a `<script>` tag
3. Auto-detects data type using decision table from dashboard-template.md
4. Copies the appropriate chart functions from this kit
5. Adds `renderKPIs()`, `initFilters()`, `renderTable()`, detail panel code
6. Writes initialization code at the bottom:
```javascript
document.addEventListener('DOMContentLoaded', () => {
    const numericCols = Object.keys(DATA[0]).filter(k => DATA.some(r => !isNaN(parseFloat(r[k]))));
    const catCols = Object.keys(DATA[0]).filter(k => !numericCols.includes(k) && new Set(DATA.map(r=>r[k])).size < 20);
    renderKPIs(DATA, numericCols);
    initFilters(DATA, catCols, numericCols);
    // Charts initialized based on detected data type
    gridApi = renderTable('data-table', DATA, Object.keys(DATA[0]));
});
```
7. Closes the HTML with `</script></body></html>`
```

- [ ] **Step 6: Commit**

```bash
git add skills/superscrape/references/dashboard-html-kit.md
git commit -m "feat: create HTML dashboard kit with ECharts + AG Grid + Tailwind components"
```

---

## Chunk 3: Streamlit Kit + Agent Updates + Sync

### Task 8: Create dashboard-streamlit-kit.md

**Files:**
- Create: `skills/superscrape/references/dashboard-streamlit-kit.md`

- [ ] **Step 1: Write the complete Streamlit kit**

```markdown
# Streamlit Dashboard Kit

## Dependencies
```
streamlit>=1.30
streamlit-echarts>=0.4
streamlit-aggrid>=1.2
pandas>=2.0
openpyxl>=3.1
```

## Theme Config (.streamlit/config.toml)
```toml
[theme]
base = "dark"
primaryColor = "#60a5fa"
backgroundColor = "#0f172a"
secondaryBackgroundColor = "#1e293b"
textColor = "#e2e8f0"
```

## Base Template
```python
import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.set_page_config(page_title="{TOPIC}", page_icon="📊", layout="wide")

COLORS = ['#60a5fa','#34d399','#fbbf24','#f87171','#a78bfa','#22d3ee','#fb923c','#e879f9']

df = pd.read_csv("data.csv")
numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
cat_cols = [c for c in df.columns if df[c].dtype == "object" and df[c].nunique() < 20]
```

## KPI Cards
```python
st.title("📊 {TOPIC}")
st.caption(f"Records: {len(df)} | Sources: N")

cols = st.columns(min(len(numeric_cols) + 1, 4))
cols[0].metric("Total Records", len(df))
for i, col in enumerate(numeric_cols[:3]):
    cols[i+1].metric(f"Avg {col}", f"{df[col].mean():.1f}", delta=f"Range: {df[col].min():.1f}–{df[col].max():.1f}")
```

## Sidebar Filters
```python
st.sidebar.header("Filters")
df_filtered = df.copy()
for col in cat_cols:
    options = df[col].dropna().unique().tolist()
    selected = st.sidebar.multiselect(col, options, default=options)
    df_filtered = df_filtered[df_filtered[col].isin(selected)]
search = st.sidebar.text_input("Search")
if search:
    df_filtered = df_filtered[df_filtered.apply(lambda r: search.lower() in str(r.values).lower(), axis=1)]
```

## Charts (ECharts via streamlit-echarts)
Chart configs are the same JSON structure as the HTML kit. Pass as Python dict to `st_echarts()`.

### Horizontal Bar
```python
option = {
    "backgroundColor": "#1e293b",
    "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
    "grid": {"left": "20%", "right": "10%", "top": 20, "bottom": 20},
    "xAxis": {"type": "value", "axisLabel": {"color": "#94a3b8"}, "splitLine": {"lineStyle": {"color": "#334155"}}},
    "yAxis": {"type": "category", "data": df_sorted[name_col].tolist(), "axisLabel": {"color": "#94a3b8"}},
    "series": [{"type": "bar", "data": df_sorted[value_col].tolist(),
        "itemStyle": {"color": {"type": "linear", "x": 0, "y": 0, "x2": 1, "y2": 0,
            "colorStops": [{"offset": 0, "color": COLORS[0] + "88"}, {"offset": 1, "color": COLORS[0]}]}},
        "barBorderRadius": [0, 4, 4, 0]}]
}
st_echarts(option, height="400px")
```

## Table (AG Grid)
```python
gb = GridOptionsBuilder.from_dataframe(df_filtered)
gb.configure_pagination(paginationAutoPageSize=True)
gb.configure_default_column(filterable=True, sortable=True, resizable=True)
gb.configure_selection('single')
grid_options = gb.build()

grid_response = AgGrid(
    df_filtered, gridOptions=grid_options,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    theme='alpine-dark', height=500, fit_columns_on_grid_load=True
)

# Detail view for selected row
if grid_response.selected_rows is not None and len(grid_response.selected_rows) > 0:
    selected = grid_response.selected_rows.iloc[0]
    with st.expander(f"Details: {selected.iloc[0]}", expanded=True):
        for col in df.columns:
            st.markdown(f"**{col}:** {selected[col]}")
```

### Radar
```python
option_radar = {
    "backgroundColor": "#1e293b",
    "legend": {"data": top5_names, "textStyle": {"color": "#94a3b8"}, "bottom": 0},
    "radar": {"indicator": [{"name": c, "max": float(df[c].max() * 1.1)} for c in numeric_cols_for_radar],
              "axisName": {"color": "#94a3b8"}, "splitLine": {"lineStyle": {"color": "#334155"}}},
    "series": [{"type": "radar", "data": [{"name": row[name_col], "value": [float(row[c]) for c in numeric_cols_for_radar]} for _, row in top5.iterrows()]}]
}
st_echarts(option_radar, height="400px")
```

### Scatter, Line, Boxplot, Heatmap, Treemap
Same JSON structure as HTML kit — pass as Python dict to `st_echarts()`. Replace JS `new echarts.graphic.LinearGradient(...)` with dict `{"type": "linear", "x": 0, "y": 0, "x2": 1, "y2": 0, "colorStops": [...]}`.

All chart configs from the HTML kit have Streamlit equivalents — the JSON structure is identical, only the wrapper differs.

## Assembly Instructions
Same logic as HTML kit — dashboard-generator detects data type, selects chart configs, assembles the .py file.

## Docker Files
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health
ENTRYPOINT ["streamlit", "run", "dashboard.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
```

```yaml
version: "3.8"
services:
  dashboard:
    build: .
    ports: ["8501:8501"]
    volumes: ["./data.csv:/app/data.csv:ro"]
    restart: unless-stopped
```

```nginx
server {
    listen 80;
    server_name DOMAIN;
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }
}
```
```

- [ ] **Step 2: Commit**

```bash
git add skills/superscrape/references/dashboard-streamlit-kit.md
git commit -m "feat: create Streamlit dashboard kit with streamlit-echarts + st-aggrid components"
```

### Task 9: Update dashboard-generator.md agent

**Files:**
- Modify: `agents/dashboard-generator.md`

- [ ] **Step 1: Update agent to reference new kit files**

Replace Plotly references with ECharts/AG Grid. Update the Process section for "dashboard-only" mode:

```markdown
### If mode = "dashboard-only":

1. Read `dashboard-template.md` → get decision table + color palette
2. Read `{output_dir}/_state/config.json` → get column types
3. Read `{output_dir}/data.csv` → verify data types (dual detection per template)
4. Determine visualization types using decision table
5. Based on dashboard_choice:
   - HTML → Read `dashboard-html-kit.md`, assemble dashboard.html
   - Streamlit → Read `dashboard-streamlit-kit.md`, assemble dashboard.py + requirements.txt + Docker files
   - Both → do both
6. Verify generated files
```

Update Rules section — replace:
```
- All Plotly charts use `plotly_dark` template and `Set2` color palette
```
with:
```
- All ECharts use dark theme base #0f172a and palette from dashboard-template.md
- HTML dashboards use ECharts + AG Grid + Tailwind (CDN)
- Streamlit dashboards use streamlit-echarts + streamlit-aggrid
- ECharts configs are structurally identical between HTML and Streamlit
```

- [ ] **Step 2: Commit**

```bash
git add agents/dashboard-generator.md
git commit -m "feat(dashboard-generator): update agent to use ECharts/AG Grid kit files"
```

### Task 10: Sync plugin cache + push to GitHub

**Files:**
- No source changes — deployment step

- [ ] **Step 1: Sync all changed files to plugin cache**

```bash
cp -r skills/ agents/ ~/.claude/plugins/cache/king-sheol/superscraper/1.0.0/
```

- [ ] **Step 2: Push to GitHub**

```bash
git push origin master
```

- [ ] **Step 3: Verify cache has new kit files**

```bash
ls ~/.claude/plugins/cache/king-sheol/superscraper/1.0.0/skills/superscrape/references/
```
Expected: `dashboard-html-kit.md`, `dashboard-streamlit-kit.md`, `dashboard-template.md`, `report-format.md`, `xlsx-generator.md`

---

## Summary

| Chunk | Tasks | Focus |
|-------|-------|-------|
| 1 | Tasks 1-5 (incl. 3b) | Orchestrator hardening: session versioning, pre-checks, session maintenance, credits, cross-validation |
| 2 | Tasks 6-7 | HTML dashboard kit: ECharts + AG Grid + Tailwind (6 chart types + table + filters + detail panel) |
| 3 | Tasks 8-10 | Streamlit kit (all chart types), agent updates, deploy |

Total: 11 tasks, ~40 steps. No new Python code to test (all files are .md prompt templates). Verification = plugin loads and runs correctly on next /superscrape test.

Deferred: sparklines in AG Grid cells, mobile drawer pattern.
