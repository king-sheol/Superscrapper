# Design Rules — Dashboard Decision & Quality Guide

Reference for dashboard-designer and dashboard-auditor agents.
Contains ONLY rules and decisions. NO code — code lives in kit files.

- **For HTML code** → read `dashboard-html-kit.md`
- **For Streamlit code** → read `dashboard-streamlit-kit.md`

---

## 1. Decision Table: Data Type → Components

| Data Type | KPI Cards | Primary Chart | Comparison Chart | Table |
|-----------|-----------|---------------|------------------|-------|
| Rating / comparison | Top-1, avg score, total, sources | Horizontal bar (top-20, gradient) | Radar (top-3) | Sort by rating, star renderer |
| Prices | Min/max/median, best value | Scatter (price vs metric) | Boxplot by category | Conditional coloring, currency format |
| Time series | Latest, trend %, min/max | Line (area fill, zoom) | Stacked bar by period | Date format |
| Segment | Leader share, count, total | Treemap | Stacked bar | Group by segment |
| Distribution | Total, top category, spread | Donut (category shares) | Stacked bar (category x sub) | Badges |
| Fallback | Total records, sources, date | Horizontal bar | Scatter | Full table |

### How to pick data type

1. Read `column_types` from `normalized.json` as starting hypothesis
2. Confirm with actual data (see Auto-detection below)
3. If one numeric column clearly dominates (ratings, scores, prices) → matching row
4. If date columns present → Time series
5. If categorical column with <15 unique values + numeric column → Segment
6. If multiple categorical columns dominate → Distribution
7. Otherwise → Fallback

---

## 2. Auto-detection (Dual Verification)

MUST verify column types from two independent sources.

**Source A — normalized.json metadata:**
Read `column_types` object. Keys are column names, values are types.

**Source B — data.csv first 5 rows:**
1. For each column, attempt parseFloat (JS) or pd.to_numeric (Python)
2. If >80% of non-empty values parse as numbers → **numeric**
3. Check for date patterns: YYYY-MM-DD or DD.MM.YYYY → **date**
4. Everything else → **string** (if <15 unique values → **categorical**)

**Conflict resolution:** If A and B disagree → trust Source B (actual data wins).

**Final classification:**
- `name_col` — first string column (label axis)
- `numeric_cols` — all numeric columns (values, KPIs)
- `date_col` — first date column if present
- `category_cols` — categorical columns <15 unique values (filters, grouping)

---

## 3. Layout Rules

| Records | Layout |
|---------|--------|
| < 20 | 2 KPI cards + 1 chart + table |
| 20-50 | 4 KPI cards + 2 charts + table |
| 50+ | 4 KPI cards + 2 charts + table with pagination |

---

## 4. Interaction Rules

- Global filters (sidebar) → update ALL components via single `applyFilters()`
- Click bar/segment in chart → filter table via same `applyFilters()`
- Click table row → slide-in detail panel (right side, 400px)
- Esc key → close detail panel
- Reset button → clear all filters

---

## 5. Number Formatting

| Type | Rule | Example |
|------|------|---------|
| Integer >= 1000 | Use K/M suffixes | 1,500 → "1.5K", 2,300,000 → "2.3M" |
| Currency | Detect symbol from data ($/EUR/RUB), format with symbol | "$49.99", "1 290 RUB" |
| Percentage | One decimal | "45.2%" |
| Rating (0-5) | Stars in table, number in charts | ★★★★☆ (4.0) |
| N/A / empty | Gray badge "N/A", NEVER empty cell | [N/A] in gray |

---

## 6. Anti-patterns (MANDATORY checks)

| Problem | Fix |
|---------|-----|
| Black labels on white background | Dark tooltip: bg #1e293b, text #f1f5f9 |
| Tooltip text overflow | max-width: 400px, word-wrap: break-word |
| Unformatted large numbers | Use formatNumber() — 1K, 1M, $ |
| Empty screen on page load | Show loading skeleton with pulse animation |
| Radar chart with 5+ items | Max 3 items — overlapping areas unreadable |
| Default Streamlit appearance | Inject custom CSS (see Streamlit kit) |
| Cyrillic labels truncated on axes | Abbreviate: max 10 chars. "RU" not "RU" |
| Empty cells for missing data | Gray "N/A" badge |
| Raw BOM in column names | Strip \uFEFF from all column names after loading |

---

## 7. Mandatory Design Rules

### Data Handling
- ALWAYS strip BOM from CSV (\uFEFF)
- ALWAYS set tooltip extraCssText: max-width 400px, word-wrap
- Limit tooltip text to 100 chars + "..."

### Cyrillic/Russian Text
- Radar axis labels: max 10 chars, use abbreviations
- Filter labels: max 15 chars
- AG Grid headers: short names ("Аудитория" not "")
- Hide long-text columns in table, show in detail panel

### Charts
- Radar: max 3 items, radius 70%, line width 2.5, area opacity 0.25
- Bar: ALWAYS use gradient, borderRadius, animationDuration 1500, stagger delay
- All charts: dark background (#1e293b), consistent tooltip styling

### Table (AG Grid)
- Column minWidth: name=200, price=180, rating=90
- domLayout: 'normal' with 600px height container
- Prevent page scroll hijack: ag-body-viewport overflow-y auto

### Badges
- Semantic: (green), (red), / (amber)
- Style: white text, pill shape, 11px font, 2px 8px padding

### Layout
- KPI cards: glassmorphism (blur, rgba bg, subtle border, hover glow)
- Sidebar: border-right separator
- Section headers: font-weight 600, NOT uppercase
- Export button: ghost style, not primary
- Footer: collection date, source count, credits

### Streamlit-specific
- BOM strip in Python
- KPI delta_color="off" for non-trend deltas
- Multiselect default=all options
- Detail expander below table
- Horizontal rules between sections

---

## 8. Docker Deployment Configs

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
