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
- Do NOT modify CSS, AG Grid, filters, detail panel, or utility functions.
- Keep all CDN imports unchanged.
