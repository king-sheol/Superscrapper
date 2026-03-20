# Streamlit Dashboard Assembly Instructions

## Prerequisites
- `dashboard-streamlit-base.py` copied to output dir as `dashboard.py`
- `data.csv` exists in output dir
- `design-rules.md` already read (you know data type and chart choices)

## Steps

1. **Copy base template:**
   ```bash
   cp skills/superscrape/references/dashboard-streamlit-base.py {output_dir}/dashboard.py
   ```

2. **Edit config (3 lines):**
   In `dashboard.py`, find and replace:
   - `TITLE = "Dashboard"` -> `TITLE = "{actual topic}"`
   - `CSV_PATH = "data.csv"` -> `CSV_PATH = "data.csv"` (or adjust path)
   - `COLUMNS = {}` -> `COLUMNS = {actual column classification}`
     - Use `"detail_only"` (NOT `"hidden"`) for columns that don't fit in the table grid — they will appear in the detail panel when a row is selected
     - Do NOT suppress any collected data — all columns must be accessible to the user

3. **Add chart functions:**
   Read `dashboard-streamlit-charts.md`. Copy the 2 needed chart functions into `dashboard.py` (above the render_ functions). Also copy the constants (`CHART_COLORS`, `TOOLTIP_STYLE`, `ANIMATION`) and the `import numpy as np` line.

4. **Wire up render functions:**
   Replace placeholder bodies:
   ```python
   def render_primary_chart(df, filtered):
       option = chart_horizontal_bar(filtered, COLUMNS["name"], COLUMNS["numeric"][0])
       if option:
           st_echarts(option, height="450px")

   def render_comparison_chart(df, filtered):
       option = chart_radar(filtered, COLUMNS["name"], COLUMNS["numeric"])
       if option:
           st_echarts(option, height="400px")
   ```

5. **Generate support files:**
   - `requirements.txt`: streamlit>=1.30, streamlit-echarts>=0.4, streamlit-aggrid>=1.2, pandas>=2.0, openpyxl>=3.1
   - `.streamlit/config.toml`:
     ```toml
     [theme]
     base="dark"
     primaryColor="#60a5fa"
     backgroundColor="#0f172a"
     secondaryBackgroundColor="#1e293b"
     textColor="#f1f5f9"
     ```
   - `Dockerfile`: python:3.11-slim, pip install, streamlit run, healthcheck, port 8501
   - `docker-compose.yml`: port 8501, data.csv volume, restart unless-stopped

## Chart Function Mapping
| Data Type    | Primary              | Comparison          |
|--------------|----------------------|---------------------|
| Rating       | chart_horizontal_bar | chart_radar         |
| Prices       | chart_scatter        | chart_boxplot       |
| Time series  | chart_line           | chart_stacked_bar   |
| Segment      | chart_treemap        | chart_stacked_bar   |
| Distribution | chart_donut          | chart_stacked_bar   |
| Fallback     | chart_horizontal_bar | chart_donut         |

## Rules
- Do NOT rewrite the base file. Only edit the 3 config lines and 2 render function bodies.
- Do NOT modify CSS, imports, AG Grid config, filters, or detail panel.
- ALL file operations with `encoding='utf-8'`.

## FORBIDDEN Patterns (will cause auditor rejection)
- Do NOT use `"hidden"` key in COLUMNS — use `"detail_only"` instead
- Do NOT add `visible_cols[:N]` or any hardcoded column limit — AG Grid handles scroll
- Do NOT use `cellRenderer` with HTML strings (raw `<span>` tags) — the base uses `cellStyle` instead
- Do NOT hardcode dates in footer — base template uses `datetime.now()` automatically
- Do NOT add custom filter logic that hides records by default — all filters must start in "show all" state
- Do NOT add `!important` to any CSS you write — the base template CSS is already sufficient

## Responsiveness & Accessibility (read design-rules.md §11-12)
- Streamlit handles basic responsive layout natively
- Verify `st.columns()` calls don't exceed 4 columns (wraps poorly)
- All custom CSS must include mobile overrides if setting fixed widths/heights
- Multiselect filters: default must include ALL options (not a filtered subset)
- KPI metrics: use `st.metric()` with `delta_color="off"` for non-trend values
