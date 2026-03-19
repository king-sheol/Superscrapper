# Dashboard Streamlit Kit — Complete Code Snippets

Reference for the dashboard-designer agent when building **Streamlit** dashboards.
Read `design-rules.md` FIRST for decision table, layout rules, and anti-patterns.

All snippets below are COMPLETE and WORKING. The agent copies them into a single
`dashboard.py` file, replacing placeholders with actual data and column names.

ECharts chart configs are **structurally identical** to the HTML kit (same JSON
keys/values), but wrapped as Python dicts passed to `st_echarts()`.

**CANONICAL color palette (8 colors — single source of truth):**
`#60a5fa, #34d399, #fbbf24, #f87171, #a78bfa, #22d3ee, #fb923c, #e879f9`

---

## 1. Custom CSS Injection — MUST be first after page_config

This block overrides Streamlit defaults to match the design system.
Insert immediately after `st.set_page_config()`.

```python
# ── Custom CSS — inject FIRST ───────────────────────────────
st.markdown("""
<style>
    /* Dark theme override */
    .stApp { background-color: #0f172a; }

    /* KPI metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #f1f5f9;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8;
    }
    [data-testid="stMetricDelta"] {
        font-size: 0.75rem;
    }

    /* Glassmorphism metric containers */
    [data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.6);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(96, 165, 250, 0.15);
        border-radius: 12px;
        padding: 1rem;
        transition: all 0.3s ease;
    }
    [data-testid="stMetric"]:hover {
        border-color: rgba(96, 165, 250, 0.4);
        box-shadow: 0 0 20px rgba(96, 165, 250, 0.1);
    }

    /* Sidebar min-width + border */
    [data-testid="stSidebar"] {
        min-width: 280px;
        border-right: 1px solid #334155;
    }
    [data-testid="stSidebar"] > div { background-color: #0f172a; }

    /* Hide Streamlit branding */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }

    /* Section dividers */
    hr { border-color: #334155; margin: 2rem 0; }

    /* DataFrame / table styling */
    .stDataFrame {
        border: 1px solid #334155;
        border-radius: 12px;
        overflow: hidden;
    }

    /* Section headers — font-weight 600, NOT uppercase */
    .stMarkdown h2, .stMarkdown h3 {
        font-weight: 600;
        color: #f1f5f9;
    }

    /* Expander styling */
    [data-testid="stExpander"] {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
    }

    /* Selectbox / input styling */
    .stSelectbox > div > div,
    .stMultiSelect > div > div,
    .stTextInput > div > div > input {
        background-color: #1e293b;
        border-color: #334155;
        color: #f1f5f9;
    }
</style>
""", unsafe_allow_html=True)
```

### Badge HTML Styles

Use these inline HTML snippets for badge rendering in tables and detail panels:

```python
# ── Badge helpers ────────────────────────────────────────────
def badge_html(value: str) -> str:
    """Return styled badge HTML for yes/no/partial/N-A values."""
    v = str(value).strip().lower()
    BADGE_MAP = {
        # Green — yes/affirmative
        "yes": ("#059669", "Yes"), "да": ("#059669", "Да"),
        "true": ("#059669", "Yes"),
        # Red — no/negative
        "no": ("#dc2626", "No"), "нет": ("#dc2626", "Нет"),
        "false": ("#dc2626", "No"),
        # Amber — partial/trial
        "partial": ("#d97706", "Partial"), "частично": ("#d97706", "Частично"),
        "trial": ("#d97706", "Trial"), "триал": ("#d97706", "Триал"),
    }
    if v in BADGE_MAP:
        color, label = BADGE_MAP[v]
        return (
            f'<span style="background:{color};color:#fff;border-radius:9999px;'
            f'font-size:11px;padding:2px 8px;font-weight:500;">{label}</span>'
        )
    # N/A badge — gray
    if v in ("", "nan", "none", "n/a", "na", "-", "—"):
        return (
            '<span style="background:#475569;color:#cbd5e1;border-radius:9999px;'
            'font-size:11px;padding:2px 8px;">N/A</span>'
        )
    return str(value)
```

---

## 2. Dependencies — requirements.txt

```text
streamlit>=1.30
streamlit-echarts>=0.4
streamlit-aggrid>=1.2
pandas>=2.0
openpyxl>=3.1
```

---

## 3. Theme Config — .streamlit/config.toml

```toml
[theme]
base = "dark"
primaryColor = "#60a5fa"
backgroundColor = "#0f172a"
secondaryBackgroundColor = "#1e293b"
textColor = "#e2e8f0"
```

The dashboard-designer must create this file alongside `dashboard.py`.

---

## 4. Base Template — Imports & Setup

```python
import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="{{TOPIC}} — Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS (section 1) — INSERT HERE ─────────────────────

# ── Color palette (same 8 colors as HTML kit) ────────────────
CHART_COLORS = [
    "#60a5fa", "#34d399", "#fbbf24", "#f87171",
    "#a78bfa", "#22d3ee", "#fb923c", "#e879f9",
]
DARK_BG = "#1e293b"

# ── Number formatting ────────────────────────────────────────
def format_number(value, fmt_type: str = "auto") -> str:
    """Format numbers consistently. Same logic as HTML kit formatNumber().
    fmt_type: 'auto' | 'currency_usd' | 'currency_eur' | 'currency_rub' | 'percent' | 'rating' | 'integer'
    """
    if pd.isna(value):
        return "N/A"
    try:
        v = float(value)
    except (ValueError, TypeError):
        return str(value)

    if fmt_type == "percent":
        return f"{v:.1f}%"
    if fmt_type == "rating":
        return f"{v:.1f}"
    if fmt_type.startswith("currency"):
        symbols = {"currency_usd": "$", "currency_eur": "EUR ", "currency_rub": ""}
        suffix = " RUB" if fmt_type == "currency_rub" else ""
        prefix = symbols.get(fmt_type, "")
        if abs(v) >= 1_000_000:
            return f"{prefix}{v / 1_000_000:.1f}M{suffix}"
        if abs(v) >= 1_000:
            return f"{prefix}{v / 1_000:.1f}K{suffix}"
        return f"{prefix}{v:,.2f}{suffix}"
    # auto / integer
    if abs(v) >= 1_000_000:
        return f"{v / 1_000_000:.1f}M"
    if abs(v) >= 1_000:
        return f"{v / 1_000:.1f}K"
    if v == int(v):
        return f"{int(v):,}"
    return f"{v:.1f}"


# ── Load data ────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("data.csv")
    # BOM fix — strip \uFEFF from column names
    df.columns = [c.replace('\ufeff', '') for c in df.columns]
    return df

df = load_data()

# ── Auto-detect column types ─────────────────────────────────
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

**Placeholders the dashboard-designer must replace:**
- `{{TOPIC}}` — research topic title
- Column classifications may be hardcoded instead of auto-detected if `config.json` provides them

---

## 5. KPI Cards — st.metric with custom CSS

```python
# ── KPI Cards ────────────────────────────────────────────────
def render_kpis(data: pd.DataFrame):
    cols = st.columns(min(4, 1 + len(numeric_cols)))

    # Always show total records
    cols[0].metric(
        "Total Records",
        format_number(len(data)),
        delta=f"of {format_number(len(df))}",
        delta_color="off",
    )

    for idx, col_name in enumerate(numeric_cols[:3]):
        values = pd.to_numeric(data[col_name], errors="coerce").dropna()
        if values.empty:
            continue
        avg = values.mean()
        vmin, vmax = values.min(), values.max()

        if idx == 0:
            cols[1].metric(
                f"Avg {col_name}",
                format_number(avg),
                delta=f"min {format_number(vmin)} / max {format_number(vmax)}",
                delta_color="off",
            )
        elif idx == 1:
            cols[2].metric(
                f"Max {col_name}",
                format_number(vmax),
                delta=f"avg {format_number(avg)}",
                delta_color="off",
            )
        elif idx == 2:
            cols[3].metric(
                f"Min {col_name}",
                format_number(vmin),
                delta=f"avg {format_number(avg)}",
                delta_color="off",
            )
```

---

## 6. Sidebar Filters — st.sidebar

```python
# ── Sidebar Filters ──────────────────────────────────────────
def render_sidebar(data: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filters")

    # Text search
    search = st.sidebar.text_input("Search all data", "")
    if search:
        mask = data.apply(
            lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1
        )
        data = data[mask]

    # Categorical dropdowns (multiselect, default=all)
    for col_name in categorical_cols:
        unique_vals = sorted(data[col_name].dropna().unique().tolist())
        label = col_name[:15] if len(col_name) > 15 else col_name
        selected = st.sidebar.multiselect(label, unique_vals, default=unique_vals)
        if selected and len(selected) < len(unique_vals):
            data = data[data[col_name].isin(selected)]

    # Numeric range sliders
    for col_name in numeric_cols[:3]:
        values = pd.to_numeric(data[col_name], errors="coerce").dropna()
        if values.empty or values.min() == values.max():
            continue
        label = col_name[:15] if len(col_name) > 15 else col_name
        vmin, vmax = float(values.min()), float(values.max())
        selected_range = st.sidebar.slider(
            label,
            min_value=vmin,
            max_value=vmax,
            value=(vmin, vmax),
        )
        data = data[
            pd.to_numeric(data[col_name], errors="coerce").between(
                selected_range[0], selected_range[1], inclusive="both"
            )
            | data[col_name].isna()
        ]

    return data
```

---

## 7. Charts — Python dicts for st_echarts

All charts share these conventions:
- Dark background `#1e293b`
- Color palette from CHART_COLORS (canonical 8 colors)
- `animationDuration: 1500` with `animationEasing: "cubicOut"`
- Tooltip: dark bg, bordered, constrained width, word-wrap
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
            "extraCssText": "max-width: 400px; white-space: normal; word-wrap: break-word;",
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
                            {"offset": 0, "color": "#3b82f6"},
                            {"offset": 1, "color": "#60a5fa"},
                        ],
                    },
                    "borderRadius": [0, 6, 6, 0],
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
    # Top 3 only (not 5 — overlapping areas are unreadable)
    top3 = data.nlargest(3, numeric_cols_list[0])

    def short_label(text: str) -> str:
        return text[:10] if len(text) > 10 else text

    indicator = []
    for col in numeric_cols_list:
        max_val = pd.to_numeric(data[col], errors="coerce").max()
        indicator.append({
            "name": short_label(col),
            "max": float(max_val * 1.1) if max_val else 100,
        })

    series_data = []
    for idx, (_, row) in enumerate(top3.iterrows()):
        series_data.append({
            "value": [float(row[c]) if pd.notna(row[c]) else 0 for c in numeric_cols_list],
            "name": str(row[name_col]),
            "lineStyle": {"color": CHART_COLORS[idx % len(CHART_COLORS)], "width": 2.5},
            "areaStyle": {"color": CHART_COLORS[idx % len(CHART_COLORS)], "opacity": 0.25},
            "itemStyle": {"color": CHART_COLORS[idx % len(CHART_COLORS)]},
        })

    option = {
        "backgroundColor": DARK_BG,
        "animationDuration": 1500,
        "animationEasing": "cubicOut",
        "legend": {
            "data": top3[name_col].tolist(),
            "bottom": 0,
            "textStyle": {"color": "#94a3b8"},
        },
        "tooltip": {
            "backgroundColor": DARK_BG,
            "borderColor": "#334155",
            "textStyle": {"color": "#f1f5f9"},
            "extraCssText": "max-width: 400px; white-space: normal; word-wrap: break-word;",
        },
        "radar": {
            "indicator": indicator,
            "radius": "70%",
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
            "extraCssText": "max-width: 400px; white-space: normal; word-wrap: break-word;",
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
            "extraCssText": "max-width: 400px; white-space: normal; word-wrap: break-word;",
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
            "extraCssText": "max-width: 400px; white-space: normal; word-wrap: break-word;",
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
            "extraCssText": "max-width: 400px; white-space: normal; word-wrap: break-word;",
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

### g. chartDonut

```python
def chart_donut(data: pd.DataFrame, category_col: str, value_col: str):
    agg = data.groupby(category_col).agg(
        total=(value_col, lambda x: pd.to_numeric(x, errors="coerce").sum()),
    ).reset_index().sort_values("total", ascending=False)

    donut_data = [
        {
            "name": str(row[category_col]),
            "value": float(row["total"]),
            "itemStyle": {"color": CHART_COLORS[idx % len(CHART_COLORS)]},
        }
        for idx, (_, row) in enumerate(agg.iterrows())
    ]

    option = {
        "backgroundColor": DARK_BG,
        "animationDuration": 1500,
        "animationEasing": "cubicOut",
        "tooltip": {
            "trigger": "item",
            "backgroundColor": DARK_BG,
            "borderColor": "#334155",
            "textStyle": {"color": "#f1f5f9"},
            "extraCssText": "max-width: 400px; white-space: normal; word-wrap: break-word;",
        },
        "legend": {
            "orient": "vertical",
            "right": "5%",
            "top": "center",
            "textStyle": {"color": "#94a3b8"},
        },
        "series": [
            {
                "type": "pie",
                "radius": ["50%", "75%"],
                "center": ["40%", "50%"],
                "avoidLabelOverlap": True,
                "label": {
                    "show": True,
                    "position": "outside",
                    "color": "#94a3b8",
                    "fontSize": 12,
                    "formatter": "{b}: {d}%",
                },
                "labelLine": {
                    "show": True,
                    "lineStyle": {"color": "#475569"},
                },
                "emphasis": {
                    "label": {"show": True, "fontSize": 14, "fontWeight": "bold", "color": "#f1f5f9"},
                    "itemStyle": {"shadowBlur": 10, "shadowOffsetX": 0, "shadowColor": "rgba(0,0,0,0.5)"},
                },
                "data": donut_data,
            }
        ],
    }
    st_echarts(option, height="400px")
```

### h. chartStackedBar

```python
def chart_stacked_bar(data: pd.DataFrame, category_col: str, sub_col: str, value_col: str):
    """Stacked bar chart: categories on X-axis, sub-groups as stacked series."""
    pivot = data.pivot_table(
        index=category_col, columns=sub_col, values=value_col,
        aggfunc=lambda x: pd.to_numeric(x, errors="coerce").sum(),
    ).fillna(0)

    categories = pivot.index.tolist()
    sub_groups = pivot.columns.tolist()

    series = [
        {
            "name": str(sg),
            "type": "bar",
            "stack": "total",
            "data": [float(pivot.loc[cat, sg]) for cat in categories],
            "itemStyle": {"color": CHART_COLORS[idx % len(CHART_COLORS)]},
            "emphasis": {"focus": "series"},
            "barMaxWidth": 40,
        }
        for idx, sg in enumerate(sub_groups)
    ]

    option = {
        "backgroundColor": DARK_BG,
        "animationDuration": 1500,
        "animationEasing": "cubicOut",
        "grid": {"left": "8%", "right": "5%", "top": "12%", "bottom": "10%"},
        "legend": {
            "top": 0,
            "textStyle": {"color": "#94a3b8"},
        },
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {"type": "shadow"},
            "backgroundColor": DARK_BG,
            "borderColor": "#334155",
            "textStyle": {"color": "#f1f5f9"},
            "extraCssText": "max-width: 400px; white-space: normal; word-wrap: break-word;",
        },
        "xAxis": {
            "type": "category",
            "data": categories,
            "axisLine": {"lineStyle": {"color": "#334155"}},
            "axisLabel": {"color": "#94a3b8", "rotate": 30},
        },
        "yAxis": {
            "type": "value",
            "axisLine": {"lineStyle": {"color": "#334155"}},
            "axisLabel": {"color": "#94a3b8"},
            "splitLine": {"lineStyle": {"color": "#334155", "type": "dashed"}},
        },
        "series": series,
    }
    st_echarts(option, height="400px")
```

---

## 8. Table — streamlit-aggrid

```python
def render_table(data: pd.DataFrame):
    # Hide long-text columns from table (show in detail panel)
    HIDDEN_COLS = ["Ключевые функции", "Интеграции", "key_features", "integrations"]
    visible_cols = [c for c in data.columns if c not in HIDDEN_COLS]
    display_df = data[visible_cols].copy()

    gb = GridOptionsBuilder.from_dataframe(display_df)
    gb.configure_default_column(
        filterable=True, sortable=True, resizable=True, min_column_width=80
    )
    gb.configure_selection(selection_mode="single", use_checkbox=False)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=50)

    # Column-specific minWidth and formatters (design rules)
    MIN_WIDTH_MAP = {"name": 200, "price": 180, "rating": 90}
    for col in visible_cols:
        col_lower = col.lower()
        if col == name_col:
            gb.configure_column(col, min_column_width=200)
        elif col_lower in MIN_WIDTH_MAP:
            gb.configure_column(col, min_column_width=MIN_WIDTH_MAP[col_lower])

    # Numeric columns: right-align, 2 decimal places
    for col in numeric_cols:
        if col in visible_cols:
            gb.configure_column(col, type=["numericColumn"], precision=2)

    # Badge renderer for yes/no/partial columns (JsCode for AG Grid)
    badge_renderer = JsCode("""
    function(params) {
        var v = (params.value || '').toString().trim().toLowerCase();
        var map = {
            'yes': '#059669', 'да': '#059669', 'true': '#059669',
            'no': '#dc2626', 'нет': '#dc2626', 'false': '#dc2626',
            'partial': '#d97706', 'частично': '#d97706', 'trial': '#d97706', 'триал': '#d97706'
        };
        var naVals = ['', 'nan', 'none', 'n/a', 'na', '-', '—', 'null', 'undefined'];
        if (map[v]) {
            return '<span style="background:' + map[v] + ';color:#fff;border-radius:9999px;font-size:11px;padding:2px 8px;">' + params.value + '</span>';
        }
        if (naVals.indexOf(v) !== -1) {
            return '<span style="background:#475569;color:#cbd5e1;border-radius:9999px;font-size:11px;padding:2px 8px;">N/A</span>';
        }
        return params.value;
    }
    """)

    # Currency formatter
    currency_renderer = JsCode("""
    function(params) {
        var v = parseFloat(params.value);
        if (isNaN(v)) return '<span style="background:#475569;color:#cbd5e1;border-radius:9999px;font-size:11px;padding:2px 8px;">N/A</span>';
        if (v >= 1000000) return (v / 1000000).toFixed(1) + 'M';
        if (v >= 1000) return (v / 1000).toFixed(1) + 'K';
        return v.toFixed(2);
    }
    """)

    # Rating stars renderer
    rating_renderer = JsCode("""
    function(params) {
        var v = parseFloat(params.value);
        if (isNaN(v)) return '<span style="background:#475569;color:#cbd5e1;border-radius:9999px;font-size:11px;padding:2px 8px;">N/A</span>';
        var full = Math.floor(v);
        var half = (v - full) >= 0.5 ? 1 : 0;
        var empty = 5 - full - half;
        return '<span style="color:#fbbf24;font-size:14px;">' +
            '\u2605'.repeat(full) + (half ? '\u00bd' : '') + '\u2606'.repeat(empty) +
            '</span> <span style="color:#94a3b8;font-size:11px;">(' + v.toFixed(1) + ')</span>';
    }
    """)

    # Apply badge renderer to categorical yes/no columns
    for col in categorical_cols:
        unique_lower = set(data[col].dropna().astype(str).str.lower().unique())
        badge_vals = {"yes", "no", "да", "нет", "partial", "частично", "trial", "триал", "true", "false"}
        if unique_lower & badge_vals:
            gb.configure_column(col, cellRenderer=badge_renderer, unsafe_allow_html=True)

    grid_options = gb.build()

    # AG Grid dark theme overrides
    custom_css = {
        ".ag-theme-alpine-dark": {
            "--ag-background-color": "#1e293b",
            "--ag-header-background-color": "#334155",
            "--ag-odd-row-background-color": "#1e293b",
            "--ag-row-hover-color": "#334155",
            "--ag-border-color": "#334155",
            "--ag-foreground-color": "#f1f5f9",
            "--ag-secondary-foreground-color": "#94a3b8",
        },
        ".ag-body-viewport": {"overflow-y": "auto !important"},
    }

    grid_response = AgGrid(
        display_df,
        gridOptions=grid_options,
        theme="alpine-dark",
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        height=600,
        fit_columns_on_grid_load=True,
        allow_unsafe_jscode=True,
        custom_css=custom_css,
    )

    # Store selected row in session_state for detail panel
    selected = grid_response.get("selected_rows", None)
    if selected is not None and len(selected) > 0:
        row_display = selected.iloc[0] if hasattr(selected, "iloc") else selected[0]
        st.session_state["selected_row"] = row_display
```

---

## 9. Detail Panel — st.expander below table

```python
def render_detail_panel(data: pd.DataFrame):
    """Show selected row details in an expander below the table."""
    selected = st.session_state.get("selected_row", None)
    if selected is None:
        return

    row_name = selected.get(name_col, "Selected Row")

    # Find full row from original data (includes hidden columns)
    full_row = (
        data[data[name_col] == row_name].iloc[0]
        if row_name in data[name_col].values
        else selected
    )

    with st.expander(f"Details: {row_name}", expanded=True):
        for key, value in full_row.items():
            val_str = str(value) if pd.notna(value) else None
            rendered = badge_html(val_str) if val_str else badge_html("")
            st.markdown(f"**{key}:** {rendered}", unsafe_allow_html=True)
```

---

## 10. Footer — st.caption with metadata

```python
def render_footer():
    st.divider()
    st.caption(
        "Date: {{DATE}} | Records: {{N_RECORDS}} | Sources: {{SOURCES}} | "
        "Generated by Superscraper"
    )
```

---

## 11. Assembly Instructions

The dashboard-designer agent assembles the final `dashboard.py` by following these steps:

### Step 1: Analyze data
1. Read `normalized.json` for `column_types`.
2. Read first 5 rows of `data.csv`.
3. Apply dual-verification rules from `design-rules.md` section 2.
4. Classify columns into: `name_col`, `numeric_cols`, `date_cols`, `categorical_cols`.
5. Pick data type from the decision table.

### Step 2: Copy base template (section 4)
Replace `{{TOPIC}}` with the actual topic. Hardcode column classifications if
`config.json` provides reliable types.

### Step 3: Insert custom CSS block (section 1) — immediately after set_page_config

### Step 4: Add badge_html helper (section 1)

### Step 5: Add format_number function (section 4)

### Step 6: Add KPI cards function (section 5)

### Step 7: Add sidebar filters function (section 6)

### Step 8: Add chart functions needed (section 7)
Based on the decision table row, include only the chart functions required.
All 8 chart types available: horizontalBar, radar, scatter, line, boxplot, treemap, donut, stackedBar.

### Step 9: Add table function (section 8)

### Step 10: Add detail panel function (section 9)

### Step 11: Create main layout

```python
# ── Header ───────────────────────────────────────────────────
st.title("{{TOPIC}}")
st.caption("Date: {{DATE}} | Records: {{N_RECORDS}} | Sources: {{SOURCES}}")

# ── Sidebar -> filtered data ─────────────────────────────────
filtered_df = render_sidebar(df)

# ── KPI Cards ────────────────────────────────────────────────
render_kpis(filtered_df)

st.divider()

# ── Primary Chart ────────────────────────────────────────────
st.subheader("Overview")
# Call the chosen primary chart function, e.g.:
# chart_horizontal_bar(filtered_df, name_col, numeric_cols[0])

st.divider()

# ── Comparison Chart ─────────────────────────────────────────
st.subheader("Comparison")
# Call the chosen comparison chart function, e.g.:
# chart_radar(filtered_df, name_col, numeric_cols)

st.divider()

# ── Data Table ───────────────────────────────────────────────
st.subheader("Data")
render_table(filtered_df)

# ── Detail Panel (below table) ───────────────────────────────
render_detail_panel(df)

# ── Footer ───────────────────────────────────────────────────
render_footer()
```

### Step 12: Create supporting files
1. `requirements.txt` (from section 2)
2. `.streamlit/config.toml` (from section 3)
3. `Dockerfile`, `docker-compose.yml`, `nginx.conf` (from `design-rules.md` section 8)

### Step 13: Validate
Ensure the dashboard:
- Has no syntax errors (`python -c "import ast; ast.parse(open('dashboard.py').read())"`)
- All chart functions receive correct column names matching `data.csv` headers
- `requirements.txt` lists all imports
- `.streamlit/config.toml` is present for dark theme
- Custom CSS block is inserted immediately after `set_page_config()`
- All tooltips have `extraCssText` with max-width and word-wrap
- Badge renderer handles N/A values (gray #475569)

---

## 12. Docker Files

Docker deployment configs are defined in `design-rules.md` section 8.
The dashboard-designer copies them verbatim:

- **Dockerfile** — `python:3.11-slim`, installs requirements, runs `streamlit run dashboard.py`
- **docker-compose.yml** — maps port 8501, mounts `data.csv` read-only, restart policy
- **nginx.conf** — reverse proxy with WebSocket upgrade support
