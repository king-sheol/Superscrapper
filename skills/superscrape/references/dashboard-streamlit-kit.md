# Dashboard Streamlit Kit — Complete Code Snippets

Reference for the dashboard-generator agent when building **Streamlit** dashboards.
Read `dashboard-template.md` FIRST for decision table and design tokens.

All snippets below are COMPLETE and WORKING. The agent copies them into a single
`dashboard.py` file, replacing placeholders with actual data and column names.

ECharts chart configs are **structurally identical** to the HTML kit (same JSON
keys/values), but wrapped as Python dicts passed to `st_echarts()`.

---

## 1. Dependencies — requirements.txt

```text
streamlit>=1.30
streamlit-echarts>=0.4
streamlit-aggrid>=1.2
pandas>=2.0
openpyxl>=3.1
```

---

## 2. Theme Config — .streamlit/config.toml

```toml
[theme]
base = "dark"
primaryColor = "#60a5fa"
backgroundColor = "#0f172a"
secondaryBackgroundColor = "#1e293b"
textColor = "#e2e8f0"
```

The dashboard-generator must create this file alongside `dashboard.py`.

---

## 3. Base Template — Imports & Setup

```python
import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="{{TOPIC}} — Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Color palette (same 8 colors as HTML kit) ───────────────
CHART_COLORS = [
    "#60a5fa", "#34d399", "#fbbf24", "#f87171",
    "#a78bfa", "#22d3ee", "#fb923c", "#e879f9",
]
DARK_BG = "#1e293b"

# ── Load data ────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("data.csv")
    return df

df = load_data()

# ── Auto-detect column types ────────────────────────────────
numeric_cols = df.select_dtypes(include="number").columns.tolist()
categorical_cols = [
    c for c in df.select_dtypes(include="object").columns
    if df[c].nunique() < 15
]
date_cols = [
    c for c in df.columns
    if df[c].dtype == "object" and pd.to_datetime(df[c], errors="coerce").notna().mean() > 0.8
]
name_col = next(
    (c for c in df.columns if c not in numeric_cols and c not in date_cols), df.columns[0]
)
```

**Placeholders the dashboard-generator must replace:**
- `{{TOPIC}}` — research topic title
- Column classifications may be hardcoded instead of auto-detected if `config.json` provides them

---

## 4. KPI Cards — st.metric

```python
# ── KPI Cards ────────────────────────────────────────────────
def render_kpis(data: pd.DataFrame):
    cols = st.columns(min(4, 1 + len(numeric_cols)))

    # Always show total records
    cols[0].metric("Total Records", len(data), delta=f"of {len(df)}")

    for idx, col_name in enumerate(numeric_cols[:3]):
        values = pd.to_numeric(data[col_name], errors="coerce").dropna()
        if values.empty:
            continue
        avg = values.mean()
        vmin, vmax = values.min(), values.max()

        if idx == 0:
            cols[1].metric(f"Avg {col_name}", f"{avg:.1f}", delta=f"min {vmin:.1f} / max {vmax:.1f}")
        elif idx == 1:
            cols[2].metric(f"Max {col_name}", f"{vmax:.1f}", delta=f"avg {avg:.1f}")
        elif idx == 2:
            cols[3].metric(f"Min {col_name}", f"{vmin:.1f}", delta=f"avg {avg:.1f}")
```

---

## 5. Sidebar Filters — st.sidebar

```python
# ── Sidebar Filters ──────────────────────────────────────────
def render_sidebar(data: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filters")

    search = st.sidebar.text_input("Search all data", "")
    if search:
        mask = data.apply(
            lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1
        )
        data = data[mask]

    for col_name in categorical_cols:
        unique_vals = sorted(data[col_name].dropna().unique().tolist())
        selected = st.sidebar.multiselect(col_name, unique_vals, default=[])
        if selected:
            data = data[data[col_name].isin(selected)]

    return data
```

---

## 6. Charts — Python dicts for st_echarts

All charts share these conventions:
- Dark background `#1e293b`
- Color palette from design tokens
- `animationDuration: 1500` with `animationEasing: "cubicOut"`
- ECharts options are plain Python dicts (structurally identical to JS in HTML kit)

### a. chartHorizontalBar

```python
def chart_horizontal_bar(data: pd.DataFrame, name_col: str, value_col: str):
    sorted_df = data.nlargest(20, value_col)
    names = sorted_df[name_col].tolist()[::-1]
    values = sorted_df[value_col].tolist()[::-1]

    option = {
        "backgroundColor": DARK_BG,
        "animationDuration": 1500,
        "animationEasing": "cubicOut",
        "grid": {"left": "20%", "right": "8%", "top": "5%", "bottom": "5%"},
        "xAxis": {
            "type": "value",
            "axisLine": {"lineStyle": {"color": "#334155"}},
            "axisLabel": {"color": "#94a3b8"},
            "splitLine": {"lineStyle": {"color": "#334155"}},
        },
        "yAxis": {
            "type": "category",
            "data": names,
            "axisLine": {"lineStyle": {"color": "#334155"}},
            "axisLabel": {"color": "#f1f5f9", "fontSize": 12},
        },
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {"type": "shadow"},
            "backgroundColor": DARK_BG,
            "borderColor": "#334155",
            "textStyle": {"color": "#f1f5f9"},
        },
        "series": [
            {
                "type": "bar",
                "data": values,
                "itemStyle": {
                    "color": {
                        "type": "linear",
                        "x": 0, "y": 0, "x2": 1, "y2": 0,
                        "colorStops": [
                            {"offset": 0, "color": "#60a5fa88"},
                            {"offset": 1, "color": "#60a5fa"},
                        ],
                    },
                    "borderRadius": [0, 4, 4, 0],
                },
                "emphasis": {"itemStyle": {"color": "#93c5fd"}},
                "barMaxWidth": 30,
            }
        ],
    }
    st_echarts(option, height="450px")
```

### b. chartRadar

```python
def chart_radar(data: pd.DataFrame, name_col: str, numeric_cols_list: list):
    top5 = data.nlargest(5, numeric_cols_list[0])

    indicator = []
    for col in numeric_cols_list:
        max_val = pd.to_numeric(data[col], errors="coerce").max()
        indicator.append({"name": col, "max": float(max_val * 1.1) if max_val else 100})

    series_data = []
    for idx, (_, row) in enumerate(top5.iterrows()):
        series_data.append({
            "value": [float(row[c]) if pd.notna(row[c]) else 0 for c in numeric_cols_list],
            "name": str(row[name_col]),
            "lineStyle": {"color": CHART_COLORS[idx % len(CHART_COLORS)]},
            "areaStyle": {"color": CHART_COLORS[idx % len(CHART_COLORS)], "opacity": 0.15},
            "itemStyle": {"color": CHART_COLORS[idx % len(CHART_COLORS)]},
        })

    option = {
        "backgroundColor": DARK_BG,
        "animationDuration": 1500,
        "animationEasing": "cubicOut",
        "legend": {
            "data": top5[name_col].tolist(),
            "bottom": 0,
            "textStyle": {"color": "#94a3b8"},
        },
        "tooltip": {
            "backgroundColor": DARK_BG,
            "borderColor": "#334155",
            "textStyle": {"color": "#f1f5f9"},
        },
        "radar": {
            "indicator": indicator,
            "shape": "polygon",
            "axisName": {"color": "#94a3b8", "fontSize": 11},
            "splitLine": {"lineStyle": {"color": "#334155"}},
            "splitArea": {"areaStyle": {"color": ["transparent"]}},
            "axisLine": {"lineStyle": {"color": "#334155"}},
        },
        "series": [{"type": "radar", "data": series_data}],
    }
    st_echarts(option, height="450px")
```

### c. chartScatter

```python
def chart_scatter(data: pd.DataFrame, x_col: str, y_col: str, name_col: str, color_col: str = None):
    if color_col:
        groups = data.groupby(color_col)
    else:
        groups = [("All", data)]

    series = []
    for idx, (key, group) in enumerate(groups):
        series.append({
            "name": str(key),
            "type": "scatter",
            "data": [
                {"value": [float(r[x_col]) if pd.notna(r[x_col]) else 0,
                           float(r[y_col]) if pd.notna(r[y_col]) else 0],
                 "name": str(r[name_col])}
                for _, r in group.iterrows()
            ],
            "symbolSize": 10,
            "itemStyle": {"color": CHART_COLORS[idx % len(CHART_COLORS)]},
            "emphasis": {"itemStyle": {"borderColor": "#fff", "borderWidth": 2}},
        })

    option = {
        "backgroundColor": DARK_BG,
        "animationDuration": 1500,
        "animationEasing": "cubicOut",
        "grid": {"left": "10%", "right": "5%", "top": "10%", "bottom": "10%"},
        "legend": {
            "show": color_col is not None,
            "top": 0,
            "textStyle": {"color": "#94a3b8"},
        },
        "tooltip": {
            "trigger": "item",
            "backgroundColor": DARK_BG,
            "borderColor": "#334155",
            "textStyle": {"color": "#f1f5f9"},
        },
        "xAxis": {
            "name": x_col,
            "nameTextStyle": {"color": "#94a3b8"},
            "axisLine": {"lineStyle": {"color": "#334155"}},
            "axisLabel": {"color": "#94a3b8"},
            "splitLine": {"lineStyle": {"color": "#334155", "type": "dashed"}},
        },
        "yAxis": {
            "name": y_col,
            "nameTextStyle": {"color": "#94a3b8"},
            "axisLine": {"lineStyle": {"color": "#334155"}},
            "axisLabel": {"color": "#94a3b8"},
            "splitLine": {"lineStyle": {"color": "#334155", "type": "dashed"}},
        },
        "series": series,
    }
    st_echarts(option, height="400px")
```

### d. chartLine

```python
def chart_line(data: pd.DataFrame, date_col: str, value_col: str):
    sorted_df = data.sort_values(date_col)
    dates = sorted_df[date_col].astype(str).tolist()
    values = pd.to_numeric(sorted_df[value_col], errors="coerce").fillna(0).tolist()

    option = {
        "backgroundColor": DARK_BG,
        "animationDuration": 1500,
        "animationEasing": "cubicOut",
        "grid": {"left": "8%", "right": "5%", "top": "10%", "bottom": "18%"},
        "tooltip": {
            "trigger": "axis",
            "backgroundColor": DARK_BG,
            "borderColor": "#334155",
            "textStyle": {"color": "#f1f5f9"},
        },
        "xAxis": {
            "type": "category",
            "data": dates,
            "axisLine": {"lineStyle": {"color": "#334155"}},
            "axisLabel": {"color": "#94a3b8", "rotate": 30},
        },
        "yAxis": {
            "type": "value",
            "name": value_col,
            "nameTextStyle": {"color": "#94a3b8"},
            "axisLine": {"lineStyle": {"color": "#334155"}},
            "axisLabel": {"color": "#94a3b8"},
            "splitLine": {"lineStyle": {"color": "#334155", "type": "dashed"}},
        },
        "dataZoom": [
            {"type": "inside", "start": 0, "end": 100},
            {
                "type": "slider", "start": 0, "end": 100, "bottom": 5,
                "borderColor": "#334155",
                "backgroundColor": "#0f172a",
                "fillerColor": "rgba(96,165,250,0.2)",
                "handleStyle": {"color": "#60a5fa"},
                "textStyle": {"color": "#94a3b8"},
            },
        ],
        "series": [
            {
                "type": "line",
                "data": values,
                "smooth": True,
                "symbol": "circle",
                "symbolSize": 6,
                "lineStyle": {"color": "#60a5fa", "width": 2},
                "itemStyle": {"color": "#60a5fa"},
                "areaStyle": {
                    "color": {
                        "type": "linear",
                        "x": 0, "y": 0, "x2": 0, "y2": 1,
                        "colorStops": [
                            {"offset": 0, "color": "rgba(96,165,250,0.3)"},
                            {"offset": 1, "color": "rgba(96,165,250,0.02)"},
                        ],
                    }
                },
                "emphasis": {"itemStyle": {"borderColor": "#fff", "borderWidth": 2}},
            }
        ],
    }
    st_echarts(option, height="450px")
```

### e. chartBoxplot

```python
def chart_boxplot(data: pd.DataFrame, category_col: str, value_col: str):
    import numpy as np

    groups = data.groupby(category_col)[value_col].apply(
        lambda x: pd.to_numeric(x, errors="coerce").dropna().tolist()
    ).to_dict()

    categories = list(groups.keys())

    def quartiles(arr):
        arr = sorted(arr)
        n = len(arr)
        if n == 0:
            return [0, 0, 0, 0, 0]
        return [
            arr[0],
            arr[int(n * 0.25)],
            arr[int(n * 0.5)],
            arr[int(n * 0.75)],
            arr[-1],
        ]

    box_data = [quartiles(groups[cat]) for cat in categories]

    option = {
        "backgroundColor": DARK_BG,
        "animationDuration": 1500,
        "animationEasing": "cubicOut",
        "grid": {"left": "10%", "right": "5%", "top": "8%", "bottom": "10%"},
        "tooltip": {
            "trigger": "item",
            "backgroundColor": DARK_BG,
            "borderColor": "#334155",
            "textStyle": {"color": "#f1f5f9"},
        },
        "xAxis": {
            "type": "category",
            "data": categories,
            "axisLine": {"lineStyle": {"color": "#334155"}},
            "axisLabel": {"color": "#94a3b8"},
        },
        "yAxis": {
            "type": "value",
            "name": value_col,
            "nameTextStyle": {"color": "#94a3b8"},
            "axisLine": {"lineStyle": {"color": "#334155"}},
            "axisLabel": {"color": "#94a3b8"},
            "splitLine": {"lineStyle": {"color": "#334155", "type": "dashed"}},
        },
        "series": [
            {
                "name": value_col,
                "type": "boxplot",
                "data": box_data,
                "itemStyle": {"color": DARK_BG, "borderColor": "#60a5fa"},
                "emphasis": {"itemStyle": {"borderColor": "#93c5fd", "borderWidth": 2}},
            }
        ],
    }
    st_echarts(option, height="400px")
```

### f. chartTreemap

```python
def chart_treemap(data: pd.DataFrame, category_col: str, value_col: str):
    agg = data.groupby(category_col).agg(
        total=(value_col, lambda x: pd.to_numeric(x, errors="coerce").sum()),
        count=(value_col, "count"),
    ).reset_index()

    treemap_data = [
        {
            "name": str(row[category_col]),
            "value": float(row["total"]),
            "count": int(row["count"]),
            "itemStyle": {"color": CHART_COLORS[idx % len(CHART_COLORS)]},
        }
        for idx, (_, row) in enumerate(agg.iterrows())
    ]

    option = {
        "backgroundColor": DARK_BG,
        "animationDuration": 1500,
        "animationEasing": "cubicOut",
        "tooltip": {
            "backgroundColor": DARK_BG,
            "borderColor": "#334155",
            "textStyle": {"color": "#f1f5f9"},
        },
        "series": [
            {
                "type": "treemap",
                "data": treemap_data,
                "roam": False,
                "width": "100%",
                "height": "100%",
                "label": {
                    "show": True,
                    "color": "#f1f5f9",
                    "fontSize": 13,
                    "fontWeight": "bold",
                },
                "breadcrumb": {"show": False},
                "levels": [
                    {
                        "itemStyle": {
                            "borderColor": DARK_BG,
                            "borderWidth": 3,
                            "gapWidth": 3,
                        }
                    }
                ],
            }
        ],
    }
    st_echarts(option, height="400px")
```

---

## 7. Table — streamlit-aggrid

```python
def render_table(data: pd.DataFrame):
    gb = GridOptionsBuilder.from_dataframe(data)
    gb.configure_default_column(
        filterable=True, sortable=True, resizable=True, min_column_width=80
    )
    gb.configure_selection(selection_mode="single", use_checkbox=False)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=50)

    for col in numeric_cols:
        gb.configure_column(col, type=["numericColumn"], precision=2)

    grid_options = gb.build()

    grid_response = AgGrid(
        data,
        gridOptions=grid_options,
        theme="alpine-dark",
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        height=500,
        fit_columns_on_grid_load=True,
    )

    # Detail expander for selected row
    selected = grid_response.get("selected_rows", None)
    if selected is not None and len(selected) > 0:
        row = selected.iloc[0] if hasattr(selected, "iloc") else selected[0]
        with st.expander(f"Details: {row.get(name_col, 'Selected Row')}", expanded=True):
            for key, value in row.items():
                st.markdown(f"**{key}:** {value}")
```

---

## 8. Assembly Instructions

The dashboard-generator agent assembles the final `dashboard.py` by following these steps:

### Step 1: Analyze data
1. Read `config.json` for `column_types`.
2. Read first 5 rows of `data.csv`.
3. Apply dual-verification rules from `dashboard-template.md` section 2.
4. Classify columns into: `name_col`, `numeric_cols`, `date_cols`, `categorical_cols`.
5. Pick data type from the decision table.

### Step 2: Copy base template (section 3)
Replace `{{TOPIC}}` with the actual topic. Hardcode column classifications if
`config.json` provides reliable types.

### Step 3: Add KPI cards function (section 4)

### Step 4: Add sidebar filters function (section 5)

### Step 5: Add chart functions needed (section 6)
Based on the decision table row, include only the chart functions required.

### Step 6: Add table function (section 7)

### Step 7: Create main layout
Assemble the main page flow:

```python
# ── Header ───────────────────────────────────────────────────
st.title("{{TOPIC}}")
st.caption("Date: {{DATE}} · Records: {{N_RECORDS}} · Sources: {{SOURCES}}")

# ── Sidebar → filtered data ─────────────────────────────────
filtered_df = render_sidebar(df)

# ── KPI Cards ────────────────────────────────────────────────
render_kpis(filtered_df)

# ── Primary Chart ────────────────────────────────────────────
st.subheader("Overview")
# Call the chosen primary chart function, e.g.:
# chart_horizontal_bar(filtered_df, name_col, numeric_cols[0])

# ── Comparison Chart ─────────────────────────────────────────
st.subheader("Comparison")
# Call the chosen comparison chart function, e.g.:
# chart_radar(filtered_df, name_col, numeric_cols)

# ── Data Table ───────────────────────────────────────────────
st.subheader("Data")
render_table(filtered_df)
```

### Step 8: Create supporting files
1. `requirements.txt` (from section 1)
2. `.streamlit/config.toml` (from section 2)
3. `Dockerfile`, `docker-compose.yml`, `nginx.conf` (from `dashboard-template.md` section 6)

### Step 9: Validate
Ensure the dashboard:
- Has no syntax errors (`python -c "import ast; ast.parse(open('dashboard.py').read())"`)
- All chart functions receive correct column names matching `data.csv` headers
- `requirements.txt` lists all imports
- `.streamlit/config.toml` is present for dark theme

---

## 9. Docker Files

Docker deployment configs are defined in `dashboard-template.md` section 6.
The dashboard-generator copies them verbatim:

- **Dockerfile** — `python:3.11-slim`, installs requirements, runs `streamlit run dashboard.py`
- **docker-compose.yml** — maps port 8501, mounts `data.csv` read-only, restart policy
- **nginx.conf** — reverse proxy with WebSocket upgrade support
