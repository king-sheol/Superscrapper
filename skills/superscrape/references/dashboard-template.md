# Dashboard Templates

Two dashboard types: Streamlit (for VPS) and static HTML (for GitHub Pages).
Both use the same decision table for choosing visualizations.

## Decision Table: Data Type → Visualization

| Data Type | Primary Chart | Comparison Chart |
|---|---|---|
| Rating/comparison (CRM, laptops) | Horizontal bar chart (sorted by key metric) | Radar chart (top 5) |
| Prices/numeric ranges | Box plot or violin plot | Scatter (price vs metric) |
| Time series (stocks, trends) | Line chart | Area chart (stacked) |
| Geographic data | Choropleth or bubble map | Bar by region |
| Categories + numbers | Grouped bar chart | Heatmap (correlations) |

## KPI Cards (auto-select based on data)

- Numeric columns: show min, max, average, median
- Ratings: show leader name + average score
- Prices: show range (min–max) + median
- Always show: total records count, sources count, collection date

## Streamlit Dashboard Template (dashboard.py)

```python
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json

# Page config
st.set_page_config(
    page_title="TOPIC — Data Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Theme
TEMPLATE = "plotly_dark"
COLORS = px.colors.qualitative.Set2

st.markdown("""
<style>
    .stMetric { background-color: #1e1e2e; padding: 1rem; border-radius: 0.5rem; }
    .stMetric label { color: #cdd6f4; }
    .stMetric [data-testid="stMetricValue"] { color: #89b4fa; font-size: 1.8rem; }
</style>
""", unsafe_allow_html=True)

# Load data
df = pd.read_csv("data.csv")

# Header
st.title("📊 TOPIC")
st.caption(f"Date: DATE | Records: {len(df)} | Sources: N")

# --- KPI Cards ---
# Auto-detect numeric columns and show summary metrics
numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
kpi_cols = st.columns(min(len(numeric_cols) + 1, 4))

kpi_cols[0].metric("Total Records", len(df))
for i, col in enumerate(numeric_cols[:3]):
    kpi_cols[i + 1].metric(
        f"Avg {col.title()}",
        f"{df[col].mean():.1f}",
        f"Range: {df[col].min():.1f} – {df[col].max():.1f}"
    )

# --- Sidebar Filters ---
st.sidebar.header("Filters")
df_filtered = df.copy()

# Auto-detect categorical columns (non-numeric, low cardinality)
cat_cols = [c for c in df.columns if df[c].dtype == "object" and df[c].nunique() < 20
            and c not in ["Source", "Collection Date"]]

for col in cat_cols:
    options = df[col].dropna().unique().tolist()
    selected = st.sidebar.multiselect(col, options, default=options)
    df_filtered = df_filtered[df_filtered[col].isin(selected)]

# --- Primary Visualization ---
# Choose chart type based on data: if there's a clear "name" + numeric → bar chart
st.subheader("Overview")
name_col = df.columns[0]  # First column is typically the object name
if numeric_cols:
    primary_metric = numeric_cols[0]
    fig = px.bar(
        df_filtered.sort_values(primary_metric, ascending=True).tail(20),
        x=primary_metric, y=name_col, orientation="h",
        color=primary_metric, color_continuous_scale="Viridis",
        template=TEMPLATE
    )
    fig.update_layout(colorway=COLORS, height=600)
    st.plotly_chart(fig, use_container_width=True)

# --- Comparison Visualization ---
st.subheader("Comparison")
if len(numeric_cols) >= 2:
    fig2 = px.scatter(
        df_filtered, x=numeric_cols[0], y=numeric_cols[1],
        hover_name=name_col,
        size=numeric_cols[2] if len(numeric_cols) >= 3 else None,
        color=cat_cols[0] if cat_cols else None,
        template=TEMPLATE
    )
    fig2.update_layout(colorway=COLORS)
    st.plotly_chart(fig2, use_container_width=True)

# --- Data Table ---
st.subheader("Full Data")
st.dataframe(df_filtered, use_container_width=True, hide_index=True)

# --- Metadata ---
with st.expander("Sources & Confidence"):
    st.markdown("| Source | Reliability | Justification |")
    st.markdown("|--------|------------|---------------|")
    # Sources table populated from metadata
    st.info("Source confidence data loaded from report metadata")
```

### Streamlit Styling

```python
# Apply dark theme via .streamlit/config.toml or inline:
st.markdown("""
<style>
    .stMetric { background-color: #1e1e2e; padding: 1rem; border-radius: 0.5rem; }
    .stMetric label { color: #cdd6f4; }
    .stMetric [data-testid="stMetricValue"] { color: #89b4fa; font-size: 1.8rem; }
</style>
""", unsafe_allow_html=True)
```

### Plotly Theme

```python
# Use dark template for all charts
template = "plotly_dark"
color_palette = px.colors.qualitative.Set2

# Apply to all figures:
fig.update_layout(template=template, colorway=color_palette)
```

## Static HTML Dashboard Template (dashboard.html)

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>[TOPIC] — Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #1e1e2e; color: #cdd6f4; }
        .container { max-width: 1400px; margin: 0 auto; padding: 2rem; }
        header { text-align: center; margin-bottom: 2rem; }
        header h1 { font-size: 2rem; color: #89b4fa; }
        header p { color: #6c7086; margin-top: 0.5rem; }
        .kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
        .kpi-card { background: #313244; padding: 1.5rem; border-radius: 0.75rem; text-align: center; }
        .kpi-card .label { color: #6c7086; font-size: 0.85rem; text-transform: uppercase; }
        .kpi-card .value { color: #89b4fa; font-size: 2rem; font-weight: bold; margin: 0.5rem 0; }
        .kpi-card .detail { color: #a6adc8; font-size: 0.85rem; }
        .chart-section { background: #313244; border-radius: 0.75rem; padding: 1.5rem; margin-bottom: 1.5rem; }
        .chart-section h2 { color: #cdd6f4; font-size: 1.2rem; margin-bottom: 1rem; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 1rem; }
        th { background: #45475a; color: #cdd6f4; padding: 0.75rem; text-align: left; cursor: pointer; }
        th:hover { background: #585b70; }
        td { padding: 0.75rem; border-bottom: 1px solid #45475a; }
        tr:hover { background: #45475a33; }
        .search-box { width: 100%; padding: 0.75rem; background: #45475a; border: none; color: #cdd6f4; border-radius: 0.5rem; margin-bottom: 1rem; font-size: 1rem; }
        .search-box::placeholder { color: #6c7086; }
        .confidence { display: inline-block; padding: 0.2rem 0.6rem; border-radius: 0.25rem; font-size: 0.8rem; }
        .confidence.high { background: #a6e3a133; color: #a6e3a1; }
        .confidence.medium { background: #f9e2af33; color: #f9e2af; }
        .confidence.low { background: #f38ba833; color: #f38ba8; }
        @media (max-width: 768px) { .kpi-grid { grid-template-columns: 1fr 1fr; } }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 [TOPIC]</h1>
            <p>Date: [DATE] | Records: [N] | Sources: [M]</p>
        </header>

        <div class="kpi-grid">
            <!-- KPI cards inserted by script -->
        </div>

        <div class="chart-section">
            <h2>Overview</h2>
            <div id="chart-primary"></div>
        </div>

        <div class="chart-section">
            <h2>Comparison</h2>
            <div id="chart-comparison"></div>
        </div>

        <div class="chart-section">
            <h2>Data</h2>
            <input type="text" class="search-box" placeholder="Search..." oninput="filterTable(this.value)">
            <table id="data-table">
                <!-- Table inserted by script -->
            </table>
        </div>

        <div class="chart-section">
            <h2>Sources & Confidence</h2>
            <div id="confidence-map"></div>
        </div>
    </div>

    <script>
    // DATA EMBEDDED HERE AS JSON
    const DATA = [/* array of objects */];
    const METADATA = {/* topic, date, sources with confidence */};

    // Plotly dark layout
    const layout = {
        paper_bgcolor: '#313244',
        plot_bgcolor: '#313244',
        font: { color: '#cdd6f4' },
        xaxis: { gridcolor: '#45475a' },
        yaxis: { gridcolor: '#45475a' },
        margin: { l: 50, r: 20, t: 40, b: 40 }
    };

    // Build KPI cards, charts, and table from DATA
    // (Generated dynamically based on actual columns and data types)

    // Table search/filter
    function filterTable(query) {
        const rows = document.querySelectorAll('#data-table tbody tr');
        query = query.toLowerCase();
        rows.forEach(row => {
            row.style.display = row.textContent.toLowerCase().includes(query) ? '' : 'none';
        });
    }

    // Table sorting
    document.querySelectorAll('#data-table th').forEach((th, idx) => {
        th.addEventListener('click', () => sortTable(idx));
    });

    function sortTable(colIdx) {
        // Sort implementation
    }
    </script>
</body>
</html>
```

## Docker Deployment Files

### Dockerfile
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

### docker-compose.yml
```yaml
version: "3.8"
services:
  dashboard:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data.csv:/app/data.csv:ro
    restart: unless-stopped
```

### nginx.conf
```nginx
server {
    listen 80;
    server_name DOMAIN_HERE;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 86400;
    }
}
```
