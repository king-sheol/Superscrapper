# HTML Dashboard Assembly Instructions

## Prerequisites
- `dashboard-html-base.html` copied to output dir as `dashboard.html`
- `data.csv` exists in output dir
- `design-rules.md` already read

## Steps

1. **Copy base template:**
   ```bash
   cp skills/superscrape/references/dashboard-html-base.html {output_dir}/dashboard.html
   ```

2. **Inject data (2 edits):**
   - Replace `const allData = [];` with `const allData = [{actual JSON data}];`
   - Replace `const COLUMNS = {};` with `const COLUMNS = {actual column classification};`

3. **Edit metadata:**
   - Replace `{{TOPIC}}` with actual topic (2 occurrences: h1 and title)
   - Replace `{{DATE}}` with collection date
   - Replace `{{SOURCES}}` with source count

4. **Add chart functions:**
   Read `dashboard-html-charts.md`. Copy the 2 needed chart functions into the `<script>` block (before the `renderPrimaryChart` / `renderComparisonChart` placeholders).

5. **Wire up render functions:**
   Replace placeholder bodies:
   ```javascript
   function renderPrimaryChart(data) {
       chartHorizontalBar('chart-primary', data, COLUMNS.name, COLUMNS.numeric[0]);
   }
   function renderComparisonChart(data) {
       chartRadar('chart-comparison', data, COLUMNS.name, COLUMNS.numeric);
   }
   ```

## Chart Function Mapping
| Data Type    | Primary              | Comparison          |
|--------------|----------------------|---------------------|
| Rating       | chartHorizontalBar   | chartRadar          |
| Prices       | chartScatter         | chartBoxplot        |
| Time series  | chartLine            | chartStackedBar     |
| Segment      | chartTreemap         | chartStackedBar     |
| Distribution | chartDonut           | chartStackedBar     |
| Fallback     | chartHorizontalBar   | chartDonut          |

## Rules
- Do NOT rewrite the base file. Only inject data, replace metadata, add chart functions, wire render functions.
- Do NOT modify existing CSS rules, AG Grid config, filters, detail panel, or utility functions.
- You MAY append new CSS rules (e.g., topic-specific chart styling) BEFORE the closing `</style>` tag, but do NOT modify or delete existing rules.
- Keep all CDN imports unchanged.
- The base template already includes: responsive CSS (768px + 480px breakpoints), a11y (focus-visible, aria-labels, semantic HTML), touch targets (44px min). Do NOT duplicate these.

## FORBIDDEN Patterns (will cause auditor rejection)
- Do NOT hide any data columns — all collected columns must be accessible (table, detail panel, or both)
- Do NOT hardcode column count limits
- ECharts: set `grid.left`/`grid.bottom` with enough margin for Cyrillic axis labels (minimum 120px left, 80px bottom)
- ECharts: add null/undefined checks in tooltip formatters to prevent `[object Object]`
- AG Grid: set `autoSizeColumns: true` or `minWidth` per column for Cyrillic content
- Replace `{{DATE}}` with collection date from data, NOT hardcoded
- Ensure AG Grid dark theme CSS covers ALL states (hover, selected, focus) — no white background flashes

## Mobile & Accessibility Requirements (read design-rules.md §11-12)

After wiring chart functions, verify:
1. **Responsive**: KPI grid has `@media (max-width: 768px)` override for 2-col / 1-col layout
2. **a11y**: KPI cards have `aria-label`, chart containers have `role="img" aria-label="{chart description}"`
3. **Semantic HTML**: main content wrapped in `<main>`, sidebar in `<nav>`, sections use `<section>` + `<h2>`
4. **Keyboard**: detail panel closeable with Escape, all buttons focusable
5. **Touch**: buttons and filter controls have `min-height: 44px`
