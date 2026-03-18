# Dashboard Template — Design System & Decision Logic

Reference for the dashboard-generator agent. Contains visualization selection rules,
auto-detection logic, and visual design tokens. Does NOT contain implementation code.

- **For HTML dashboards** → read `dashboard-html-kit.md`
- **For Streamlit dashboards** → read `dashboard-streamlit-kit.md`

---

## 1. Decision Table: Data Type → Visualization

| Data Type | KPI Cards | Primary Chart | Comparison Chart | Table |
|-----------|-----------|---------------|------------------|-------|
| Rating / comparison | Top-1, avg score, total, sources | ECharts horizontal bar (gradient) | ECharts radar (top 5) | AG Grid: sort by rating |
| Prices | Min / max / median, best value | ECharts scatter | ECharts boxplot | AG Grid: conditional coloring |
| Time series | Latest, trend %, min / max | ECharts line (area fill) | ECharts heatmap | AG Grid (plain values) |
| Segment | Leader share, count, total | ECharts treemap / sunburst | ECharts stacked bar | AG Grid: group by segment |
| Fallback | total records, sources, date | Horizontal bar | Scatter | Full AG Grid |

### How to pick the data type

1. If `normalized.json` contains `column_types` — use them as the starting hypothesis.
2. Confirm with the actual data (see Auto-detection below).
3. If one numeric column clearly dominates (ratings, scores, prices) — pick the matching row.
4. If there are date columns — pick Time series.
5. If there is a categorical column with <15 unique values and a numeric column — pick Segment.
6. Otherwise — Fallback.

---

## 2. Auto-detection Rules (Dual Verification)

The agent MUST verify column types from two independent sources before choosing charts.

### Source A — normalized.json metadata

Read `column_types` from `normalized.json`. Example:
```json
{
  "column_types": {
    "name": "string",
    "rating": "numeric",
    "price": "numeric",
    "category": "categorical",
    "date": "date"
  }
}
```

### Source B — data.csv first 5 rows

1. Read the first 5 data rows from `data.csv`.
2. For each column, attempt `parseFloat(value)` (JS) or `pd.to_numeric(value)` (Python).
3. If **>80%** of non-empty values parse as numbers → mark column as **numeric**.
4. Check for date patterns: `YYYY-MM-DD` or `DD.MM.YYYY` → mark as **date**.
5. Everything else → **string** (if <15 unique values → **categorical**).

### Conflict resolution

If Source A and Source B disagree on a column type → **trust Source B** (actual data wins).

### Final column classification

After verification, classify each column:
- **name_col** — first string column (used as label axis)
- **numeric_cols** — all numeric columns (used for values, KPIs)
- **date_col** — first date column if present
- **category_cols** — categorical columns with <15 unique values (used for filters, grouping)

---

## 3. Color Palette

```
Dark base:     #0f172a   (page background)
Surface:       #1e293b   (cards, chart backgrounds)
Border:        #334155   (dividers, grid lines)
Text primary:  #f1f5f9
Text secondary:#94a3b8
```

Chart colors (8-color cycle, use in order):

| Index | Hex       | Usage example          |
|-------|-----------|------------------------|
| 0     | `#60a5fa` | Primary bars, main line |
| 1     | `#34d399` | Secondary series        |
| 2     | `#fbbf24` | Warnings, third series  |
| 3     | `#f87171` | Negative, alerts        |
| 4     | `#a78bfa` | Fifth series            |
| 5     | `#22d3ee` | Sixth series            |
| 6     | `#fb923c` | Seventh series          |
| 7     | `#e879f9` | Eighth series           |

Gradient for bar charts: from `#60a5fa` (left/bottom) to `#3b82f6` (right/top).

---

## 4. Typography

Font stack (system fonts, no external loading):

```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
```

Numeric values MUST use:
```css
font-variant-numeric: tabular-nums;
```

This ensures columns of numbers align vertically.

Size scale:
- Page title: 1.5rem, font-weight 700
- Section title: 1.125rem, font-weight 600
- KPI value: 2rem, font-weight 700
- KPI label: 0.75rem, uppercase, letter-spacing 0.05em
- Body / table: 0.875rem
- Small / caption: 0.75rem

---

## 5. Kit File Pointers

The design tokens and decision table above are shared by ALL dashboard types.
Implementation details live in separate kit files:

| Dashboard type | Kit file | When to use |
|----------------|----------|-------------|
| Static HTML | `dashboard-html-kit.md` | GitHub Pages, no server needed |
| Streamlit | `dashboard-streamlit-kit.md` | VPS with Docker, interactive |

The dashboard-generator agent reads THIS file first (for decisions), then reads the
appropriate kit file (for code snippets).

---

## 6. Docker Deployment Configs

Used when deploying Streamlit dashboards to the user's VPS.

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
