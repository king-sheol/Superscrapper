# Dashboard HTML Kit — Complete Component Library

Reference for the dashboard-designer agent when building **static HTML** dashboards.
Read `design-rules.md` FIRST for decision table and layout rules.

All snippets below are COMPLETE and WORKING. The agent copies them into a single
`dashboard.html` file, replacing placeholders with actual data and column names.

**20 components:** 8 charts, KPI cards, table, filters + range sliders, detail panel,
5 utility functions, footer, assembly instructions.

---

## 1. Base HTML — Head & Body Layout

```html
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{TOPIC}} — Dashboard</title>

    <!-- ECharts 5 -->
    <script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>

    <!-- AG Grid 31 -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/ag-grid-community@31/styles/ag-grid.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/ag-grid-community@31/styles/ag-theme-alpine.css">
    <script src="https://cdn.jsdelivr.net/npm/ag-grid-community@31/dist/ag-grid-community.min.js"></script>

    <!-- Tailwind CSS (dark mode via class) -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    colors: {
                        base:    '#0f172a',
                        surface: '#1e293b',
                        border:  '#334155',
                    }
                }
            }
        };
    </script>

    <!-- Lucide Icons 0.460 -->
    <script src="https://unpkg.com/lucide@0.460"></script>

    <style>
        /* === DESIGN TOKENS === */
        :root {
            --color-base: #0f172a;
            --color-surface: #1e293b;
            --color-border: #334155;
            --color-text: #f1f5f9;
            --color-text-secondary: #94a3b8;
            --color-text-muted: #64748b;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            font-variant-numeric: tabular-nums;
            background: var(--color-base);
            color: var(--color-text);
            margin: 0;
            padding: 0;
        }

        /* AG Grid dark overrides */
        .ag-theme-alpine-dark {
            --ag-background-color: #1e293b;
            --ag-header-background-color: #334155;
            --ag-odd-row-background-color: #1e293b;
            --ag-row-hover-color: #334155;
            --ag-border-color: #334155;
            --ag-foreground-color: #f1f5f9;
            --ag-secondary-foreground-color: #94a3b8;
        }

        /* Glassmorphism KPI cards */
        .glass-card {
            background: rgba(30, 41, 59, 0.6);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(96, 165, 250, 0.15);
            transition: all 0.3s ease;
        }
        .glass-card:hover {
            border-color: rgba(96, 165, 250, 0.4);
            box-shadow: 0 0 20px rgba(96, 165, 250, 0.1);
            transform: translateY(-2px);
        }

        /* AG Grid scroll fix */
        .ag-body-viewport { overflow-y: auto !important; }

        /* Badge constants */
        .badge-yes { background: #059669; color: #fff; border-radius: 9999px; font-size: 11px; padding: 2px 8px; display: inline-block; }
        .badge-no { background: #dc2626; color: #fff; border-radius: 9999px; font-size: 11px; padding: 2px 8px; display: inline-block; }
        .badge-partial { background: #d97706; color: #fff; border-radius: 9999px; font-size: 11px; padding: 2px 8px; display: inline-block; }
        .badge-na { background: #475569; color: #94a3b8; border-radius: 9999px; font-size: 11px; padding: 2px 8px; display: inline-block; }

        /* Rating stars */
        .rating-stars { color: #fbbf24; font-size: 14px; letter-spacing: 1px; white-space: nowrap; }
        .rating-stars .empty { color: #475569; }

        /* Progress bar */
        .progress-bar-container {
            width: 100%;
            height: 8px;
            background: #334155;
            border-radius: 4px;
            overflow: hidden;
        }
        .progress-bar-fill {
            height: 100%;
            border-radius: 4px;
            transition: width 0.6s ease;
        }

        /* KPI trend indicators */
        .trend-up { color: #34d399; font-size: 12px; font-weight: 600; }
        .trend-down { color: #f87171; font-size: 12px; font-weight: 600; }

        /* Loading skeleton */
        .skeleton {
            background: linear-gradient(90deg, #1e293b 25%, #334155 50%, #1e293b 75%);
            background-size: 200% 100%;
            animation: skeleton-pulse 1.5s ease-in-out infinite;
            border-radius: 8px;
        }
        @keyframes skeleton-pulse {
            0% { background-position: 200% 0; }
            100% { background-position: -200% 0; }
        }
        .skeleton-kpi { height: 96px; }
        .skeleton-chart { height: 400px; }
        .skeleton-table { height: 300px; }
        .skeleton-text { height: 16px; margin-bottom: 8px; }
        .skeleton-text-short { width: 60%; }

        /* Empty state */
        .empty-state {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 3rem;
            color: #64748b;
            text-align: center;
        }
        .empty-state i { margin-bottom: 1rem; }

        /* Error state */
        .error-state {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 2rem;
            color: #f87171;
            text-align: center;
            background: rgba(248, 113, 113, 0.05);
            border: 1px dashed #f87171;
            border-radius: 12px;
        }

        /* Detail panel */
        #detail-panel {
            position: fixed;
            top: 0;
            right: 0;
            width: 400px;
            height: 100vh;
            background: #1e293b;
            border-left: 1px solid #334155;
            transform: translateX(100%);
            transition: transform 0.3s ease;
            z-index: 50;
            overflow-y: auto;
            padding: 1.5rem;
        }
        #detail-panel.open { transform: translateX(0); }
        #detail-overlay {
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.5);
            z-index: 40;
            display: none;
        }
        #detail-overlay.open { display: block; }

        /* Range slider */
        .range-slider-track {
            position: relative;
            height: 6px;
            background: #334155;
            border-radius: 3px;
            margin: 12px 0;
        }
        .range-slider-fill {
            position: absolute;
            height: 100%;
            background: #60a5fa;
            border-radius: 3px;
        }
        .range-slider-handle {
            position: absolute;
            top: 50%;
            width: 16px;
            height: 16px;
            background: #60a5fa;
            border: 2px solid #f1f5f9;
            border-radius: 50%;
            transform: translate(-50%, -50%);
            cursor: grab;
            z-index: 2;
        }
        .range-slider-handle:active { cursor: grabbing; }
        .range-slider-labels {
            display: flex;
            justify-content: space-between;
            font-size: 11px;
            color: #94a3b8;
        }

        /* Footer */
        .dashboard-footer {
            border-top: 1px solid #334155;
            padding: 1.5rem;
            margin-top: 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
            color: #64748b;
            font-size: 12px;
        }
        .dashboard-footer a { color: #60a5fa; text-decoration: none; }
        .dashboard-footer a:hover { text-decoration: underline; }

        /* Responsive sidebar */
        @media (max-width: 768px) {
            #filter-sidebar {
                position: fixed;
                top: 0;
                left: 0;
                width: 280px;
                height: 100vh;
                background: #0f172a;
                z-index: 30;
                transform: translateX(-100%);
                transition: transform 0.3s ease;
                padding: 1.5rem;
                border-right: 1px solid #334155;
                overflow-y: auto;
            }
            #filter-sidebar.open { transform: translateX(0); }
            #sidebar-toggle { display: flex !important; }
            #kpi-grid { grid-template-columns: repeat(2, 1fr) !important; }
        }
        @media (min-width: 769px) {
            #sidebar-toggle { display: none !important; }
        }
    </style>
</head>
<body class="bg-base min-h-screen">

    <!-- Header -->
    <header class="border-b border-border px-6 py-4">
        <div class="flex items-center justify-between">
            <div>
                <h1 class="text-2xl font-bold text-white">{{TOPIC}}</h1>
                <p class="text-sm text-slate-400 mt-1">
                    Date: {{DATE}} &middot; Records: <span id="record-count">0</span> &middot; Sources: {{SOURCES}}
                </p>
            </div>
            <button id="sidebar-toggle" onclick="toggleSidebar()"
                    class="items-center gap-1 px-3 py-2 bg-surface border border-border rounded-lg text-sm text-slate-300 hover:bg-border transition"
                    style="display:none;">
                <i data-lucide="sliders-horizontal" class="w-4 h-4"></i> Filters
            </button>
        </div>
    </header>

    <!-- KPI Grid -->
    <div id="kpi-grid" class="grid grid-cols-2 md:grid-cols-4 gap-4 px-6 py-4"></div>

    <!-- Main layout: sidebar filters + content -->
    <div class="flex px-6 gap-6">

        <!-- Sidebar Filters -->
        <aside id="filter-sidebar" class="w-64 flex-shrink-0 space-y-4 pr-6 border-r border-border">
            <div>
                <label class="block text-xs uppercase tracking-wider text-slate-400 mb-1">Search</label>
                <input id="search-input" type="text" placeholder="Search all data..."
                       class="w-full px-3 py-2 bg-surface border border-border rounded-lg text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                       oninput="applyFilters()">
            </div>
            <div id="filter-dropdowns"></div>
            <div id="filter-range-sliders"></div>
            <button onclick="resetFilters()"
                    class="w-full px-3 py-2 bg-surface border border-border rounded-lg text-sm text-slate-300 hover:bg-border transition">
                Reset Filters
            </button>
        </aside>

        <!-- Main content -->
        <main class="flex-1 space-y-6 pb-8">
            <!-- Primary chart -->
            <section class="bg-surface rounded-xl border border-border p-4">
                <h2 class="text-lg font-semibold mb-3">Overview</h2>
                <div id="chart-primary" style="height:450px;"></div>
            </section>

            <!-- Comparison chart -->
            <section class="bg-surface rounded-xl border border-border p-4">
                <h2 class="text-lg font-semibold mb-3">Comparison</h2>
                <div id="chart-comparison" style="height:400px;"></div>
            </section>

            <!-- Table -->
            <section class="bg-surface rounded-xl border border-border p-4">
                <div class="flex items-center justify-between mb-3">
                    <h2 class="text-lg font-semibold">Data</h2>
                    <button onclick="exportCsv()"
                            class="flex items-center gap-1 px-3 py-1.5 bg-transparent border border-border rounded-lg text-sm text-slate-300 hover:bg-surface transition">
                        <i data-lucide="download" class="w-4 h-4"></i> Export CSV
                    </button>
                </div>
                <div id="data-table" class="ag-theme-alpine-dark" style="height:600px;width:100%;"></div>
            </section>
        </main>
    </div>

    <!-- Detail Panel (slide-in) -->
    <div id="detail-overlay" onclick="closeDetailPanel()"></div>
    <div id="detail-panel">
        <div class="flex items-center justify-between mb-4">
            <h3 id="detail-title" class="text-lg font-semibold">Details</h3>
            <button onclick="closeDetailPanel()" class="text-slate-400 hover:text-white">
                <i data-lucide="x" class="w-5 h-5"></i>
            </button>
        </div>
        <div id="detail-content"></div>
    </div>

    <!-- Footer container -->
    <div id="dashboard-footer"></div>

    <script>
    // === GLOBAL STATE ===
    // The dashboard-designer replaces this with actual data
    const allData = {{DATA_JSON}};
    let filteredData = [...allData];
    let activeFilters = {};
    let rangeFilters = {};
    let gridApi = null;
    let chartInstances = {};

    // Column classification (filled by dashboard-designer)
    const COLUMNS = {{COLUMNS_JSON}};
    // Example: { name: 'product', numeric: ['rating','price'], date: null, categories: ['brand','type'] }
    </script>

    <!-- Remaining <script> sections follow below -->

</body>
</html>
```

**Placeholders the dashboard-designer must replace:**
- `{{TOPIC}}` — research topic title
- `{{DATE}}` — collection date
- `{{SOURCES}}` — number of sources
- `{{DATA_JSON}}` — `JSON.stringify(data)` from data.csv
- `{{COLUMNS_JSON}}` — column classification object

---

## 2. Utility Functions — formatNumber, formatDate

Insert these FIRST inside the main `<script>` block (other functions depend on them).

```javascript
// === UTILITY: formatNumber ===
// Types: 'integer', 'currency', 'percent', 'rating'
function formatNumber(value, type) {
    if (value === null || value === undefined || value === '') return '<span class="badge-na">N/A</span>';
    var num = parseFloat(value);
    if (isNaN(num)) return '<span class="badge-na">N/A</span>';

    switch (type) {
        case 'integer':
            if (Math.abs(num) >= 1000000) return (num / 1000000).toFixed(1) + 'M';
            if (Math.abs(num) >= 1000) return (num / 1000).toFixed(1) + 'K';
            return Math.round(num).toLocaleString();
        case 'currency':
            // Detect currency from data if available, default to $
            var symbol = (window._currencySymbol || '$');
            if (Math.abs(num) >= 1000000) return symbol + (num / 1000000).toFixed(1) + 'M';
            if (Math.abs(num) >= 10000) return symbol + (num / 1000).toFixed(1) + 'K';
            return symbol + num.toFixed(2);
        case 'percent':
            return num.toFixed(1) + '%';
        case 'rating':
            var full = Math.floor(num);
            var half = (num - full) >= 0.5 ? 1 : 0;
            var empty = 5 - full - half;
            var stars = '';
            for (var i = 0; i < full; i++) stars += '★';
            if (half) stars += '½';
            for (var j = 0; j < empty; j++) stars += '<span class="empty">★</span>';
            return '<span class="rating-stars">' + stars + '</span>';
        default:
            return Number.isInteger(num) ? num.toLocaleString() : num.toFixed(2);
    }
}

// Plain text version (no HTML, for charts/KPIs)
function formatNumberText(value, type) {
    if (value === null || value === undefined || value === '') return 'N/A';
    var num = parseFloat(value);
    if (isNaN(num)) return 'N/A';

    switch (type) {
        case 'integer':
            if (Math.abs(num) >= 1000000) return (num / 1000000).toFixed(1) + 'M';
            if (Math.abs(num) >= 1000) return (num / 1000).toFixed(1) + 'K';
            return Math.round(num).toLocaleString();
        case 'currency':
            var symbol = (window._currencySymbol || '$');
            if (Math.abs(num) >= 1000000) return symbol + (num / 1000000).toFixed(1) + 'M';
            if (Math.abs(num) >= 10000) return symbol + (num / 1000).toFixed(1) + 'K';
            return symbol + num.toFixed(2);
        case 'percent':
            return num.toFixed(1) + '%';
        case 'rating':
            return num.toFixed(1) + ' / 5';
        default:
            return Number.isInteger(num) ? num.toLocaleString() : num.toFixed(2);
    }
}

// === UTILITY: formatDate ===
function formatDate(value, locale) {
    if (!value) return '<span class="badge-na">N/A</span>';
    locale = locale || 'en';
    var str = String(value).trim();

    // Detect DD.MM.YYYY
    var dotMatch = str.match(/^(\d{1,2})\.(\d{1,2})\.(\d{4})$/);
    if (dotMatch) {
        var d = new Date(dotMatch[3], parseInt(dotMatch[2]) - 1, dotMatch[1]);
        if (!isNaN(d)) return d.toLocaleDateString(locale, { year: 'numeric', month: 'short', day: 'numeric' });
    }

    // Detect YYYY-MM-DD
    var isoMatch = str.match(/^(\d{4})-(\d{1,2})-(\d{1,2})/);
    if (isoMatch) {
        var d2 = new Date(isoMatch[1], parseInt(isoMatch[2]) - 1, isoMatch[3]);
        if (!isNaN(d2)) return d2.toLocaleDateString(locale, { year: 'numeric', month: 'short', day: 'numeric' });
    }

    // Fallback: try native Date parse
    var fallback = new Date(str);
    if (!isNaN(fallback)) return fallback.toLocaleDateString(locale, { year: 'numeric', month: 'short', day: 'numeric' });

    return str;
}
```

---

## 3. Loading, Empty, and Error States

```javascript
// === UTILITY: renderLoadingSkeleton ===
function renderLoadingSkeleton() {
    // KPI skeletons
    var kpiGrid = document.getElementById('kpi-grid');
    kpiGrid.innerHTML = '';
    for (var i = 0; i < 4; i++) {
        var sk = document.createElement('div');
        sk.className = 'skeleton skeleton-kpi';
        kpiGrid.appendChild(sk);
    }

    // Chart skeletons
    var chartPrimary = document.getElementById('chart-primary');
    if (chartPrimary) chartPrimary.innerHTML = '<div class="skeleton skeleton-chart"></div>';
    var chartComparison = document.getElementById('chart-comparison');
    if (chartComparison) chartComparison.innerHTML = '<div class="skeleton skeleton-chart"></div>';

    // Table skeleton
    var table = document.getElementById('data-table');
    if (table) {
        var html = '';
        html += '<div class="skeleton skeleton-text" style="width:100%;margin:16px 0;"></div>';
        for (var j = 0; j < 8; j++) {
            html += '<div class="skeleton skeleton-text' + (j % 3 === 0 ? ' skeleton-text-short' : '') + '" style="margin:8px 16px;"></div>';
        }
        table.innerHTML = html;
    }
}

// === UTILITY: renderEmptyState ===
function renderEmptyState(message) {
    message = message || 'No data matching current filters';
    return '<div class="empty-state">' +
               '<i data-lucide="search-x" class="w-12 h-12"></i>' +
               '<p class="text-base font-medium mt-2">' + message + '</p>' +
               '<p class="text-sm mt-1">Try adjusting your filters or search query</p>' +
           '</div>';
}

// === UTILITY: renderErrorState ===
function renderErrorState(containerId, message) {
    message = message || 'Failed to load this component';
    var container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = '<div class="error-state">' +
                              '<i data-lucide="alert-triangle" class="w-10 h-10"></i>' +
                              '<p class="text-base font-medium mt-2">' + message + '</p>' +
                              '<p class="text-sm mt-1" style="color:#94a3b8;">Check browser console for details</p>' +
                          '</div>';
    lucide.createIcons();
}
```

---

## 4. Footer — renderFooter()

```javascript
// === UTILITY: renderFooter ===
function renderFooter(metadata) {
    metadata = metadata || {};
    var container = document.getElementById('dashboard-footer');
    if (!container) return;

    var date = metadata.date || '{{DATE}}';
    var sources = metadata.sources || '{{SOURCES}}';
    var credits = metadata.credits || '';

    container.innerHTML =
        '<footer class="dashboard-footer px-6">' +
            '<div>' +
                '<span>Generated by Superscraper</span>' +
                (credits ? ' &middot; <span>' + credits + '</span>' : '') +
            '</div>' +
            '<div>' +
                '<span>Collected: ' + date + '</span>' +
                ' &middot; <span>' + sources + ' sources</span>' +
            '</div>' +
        '</footer>';
}
```

---

## 5. KPI Cards — renderKPIs()

Enhanced with trend indicators and formatNumber.

```javascript
function renderKPIs(data) {
    var container = document.getElementById('kpi-grid');
    container.innerHTML = '';

    if (data.length === 0) {
        container.innerHTML = renderEmptyState('No data to display KPIs');
        lucide.createIcons();
        return;
    }

    var kpis = [];

    // Always show total records
    kpis.push({
        label: 'Total Records',
        value: data.length,
        formatted: formatNumberText(data.length, 'integer'),
        detail: 'filtered from ' + allData.length,
        icon: 'database',
        trend: null
    });

    // Auto-detect numeric columns and compute stats
    COLUMNS.numeric.forEach(function(col, idx) {
        var values = data.map(function(r) { return parseFloat(r[col]); }).filter(function(v) { return !isNaN(v); });
        if (values.length === 0) return;

        var sum = values.reduce(function(a, b) { return a + b; }, 0);
        var avg = sum / values.length;
        var max = Math.max.apply(null, values);
        var min = Math.min.apply(null, values);

        // Compute trend: compare first half vs second half average
        var trend = null;
        if (values.length >= 4) {
            var mid = Math.floor(values.length / 2);
            var firstHalf = values.slice(0, mid);
            var secondHalf = values.slice(mid);
            var avgFirst = firstHalf.reduce(function(a, b) { return a + b; }, 0) / firstHalf.length;
            var avgSecond = secondHalf.reduce(function(a, b) { return a + b; }, 0) / secondHalf.length;
            if (avgFirst > 0) {
                var pctChange = ((avgSecond - avgFirst) / avgFirst) * 100;
                if (Math.abs(pctChange) >= 1) {
                    trend = { direction: pctChange > 0 ? 'up' : 'down', value: Math.abs(pctChange).toFixed(1) + '%' };
                }
            }
        }

        // Detect type for formatting
        var fmtType = 'integer';
        var colLower = col.toLowerCase();
        if (colLower.indexOf('price') !== -1 || colLower.indexOf('cost') !== -1 || colLower.indexOf('цена') !== -1) fmtType = 'currency';
        else if (colLower.indexOf('rating') !== -1 || colLower.indexOf('score') !== -1 || colLower.indexOf('рейтинг') !== -1) fmtType = 'rating';
        else if (colLower.indexOf('percent') !== -1 || colLower.indexOf('%') !== -1) fmtType = 'percent';

        if (idx === 0) {
            kpis.push({ label: 'Avg ' + col, value: avg, formatted: formatNumberText(avg, fmtType), detail: 'min ' + formatNumberText(min, fmtType) + ' / max ' + formatNumberText(max, fmtType), icon: 'trending-up', trend: trend });
        } else if (idx === 1) {
            kpis.push({ label: 'Max ' + col, value: max, formatted: formatNumberText(max, fmtType), detail: 'avg ' + formatNumberText(avg, fmtType), icon: 'arrow-up-right', trend: null });
        } else if (idx === 2) {
            kpis.push({ label: 'Min ' + col, value: min, formatted: formatNumberText(min, fmtType), detail: 'avg ' + formatNumberText(avg, fmtType), icon: 'arrow-down-right', trend: null });
        }
    });

    // Render cards with countUp animation
    kpis.forEach(function(kpi) {
        var trendHtml = '';
        if (kpi.trend) {
            var trendClass = kpi.trend.direction === 'up' ? 'trend-up' : 'trend-down';
            var trendArrow = kpi.trend.direction === 'up' ? '▲' : '▼';
            trendHtml = '<span class="' + trendClass + ' ml-2">' + trendArrow + ' ' + kpi.trend.value + '</span>';
        }

        var card = document.createElement('div');
        card.className = 'glass-card rounded-xl p-4';
        card.innerHTML =
            '<div class="flex items-center gap-2 mb-2">' +
                '<i data-lucide="' + kpi.icon + '" class="w-4 h-4 text-slate-400"></i>' +
                '<span class="text-xs uppercase tracking-wider text-slate-400">' + kpi.label + '</span>' +
            '</div>' +
            '<div class="flex items-baseline">' +
                '<div class="text-2xl font-bold text-white kpi-value" data-target="' + kpi.value + '">0</div>' +
                trendHtml +
            '</div>' +
            '<div class="text-xs text-slate-500 mt-1">' + kpi.detail + '</div>';
        container.appendChild(card);
    });

    lucide.createIcons();

    // CountUp animation
    document.querySelectorAll('.kpi-value').forEach(function(el) {
        var target = parseFloat(el.getAttribute('data-target'));
        if (isNaN(target)) {
            el.textContent = el.getAttribute('data-target');
            return;
        }
        var duration = 600;
        var startTime = null;
        function animate(timestamp) {
            if (!startTime) startTime = timestamp;
            var progress = Math.min((timestamp - startTime) / duration, 1);
            var eased = 1 - Math.pow(1 - progress, 3);
            var current = eased * target;
            el.textContent = Number.isInteger(target) ? Math.round(current) : current.toFixed(1);
            if (progress < 1) requestAnimationFrame(animate);
        }
        requestAnimationFrame(animate);
    });
}
```

---

## 6. Charts — 8 Chart Type Functions

All charts share these conventions:
- Dark background `#1e293b`
- Color palette: `#60a5fa, #34d399, #fbbf24, #f87171, #a78bfa, #22d3ee, #fb923c, #e879f9`
- `animationDuration: 1500` with `animationEasing: 'cubicOut'`
- Responsive via `window.addEventListener('resize', ...)`
- Click handler calls `applyFilters()` for chart-to-table filtering
- Tooltip: dark bg, max-width 400px, word-wrap

### Common setup

```javascript
var CHART_COLORS = ['#60a5fa','#34d399','#fbbf24','#f87171','#a78bfa','#22d3ee','#fb923c','#e879f9'];

function initChart(containerId) {
    var dom = document.getElementById(containerId);
    if (!dom) return null;
    if (chartInstances[containerId]) {
        chartInstances[containerId].dispose();
    }
    var chart = echarts.init(dom, null, { renderer: 'canvas' });
    chartInstances[containerId] = chart;
    return chart;
}

var TOOLTIP_STYLE = {
    backgroundColor: '#1e293b',
    borderColor: '#334155',
    textStyle: { color: '#f1f5f9' },
    extraCssText: 'max-width: 400px; white-space: normal; word-wrap: break-word;'
};

var AXIS_STYLE = {
    axisLine: { lineStyle: { color: '#334155' } },
    axisLabel: { color: '#94a3b8' },
    splitLine: { lineStyle: { color: '#334155', type: 'dashed' } }
};

// Responsive resize for all charts
window.addEventListener('resize', function() {
    Object.keys(chartInstances).forEach(function(key) {
        if (chartInstances[key]) chartInstances[key].resize();
    });
});
```

### a. chartHorizontalBar

```javascript
function chartHorizontalBar(containerId, data, nameCol, valueCol) {
    var chart = initChart(containerId);
    if (!chart) return;

    if (data.length === 0) { document.getElementById(containerId).innerHTML = renderEmptyState(); lucide.createIcons(); return; }

    // Sort descending by value, take top 20
    var sorted = data.slice().sort(function(a, b) {
        return parseFloat(b[valueCol]) - parseFloat(a[valueCol]);
    }).slice(0, 20);

    var names = sorted.map(function(r) { return r[nameCol]; }).reverse();
    var values = sorted.map(function(r) { return parseFloat(r[valueCol]) || 0; }).reverse();

    chart.setOption({
        backgroundColor: '#1e293b',
        animationDuration: 1500,
        animationEasing: 'cubicOut',
        grid: { left: '20%', right: '8%', top: '5%', bottom: '5%' },
        xAxis: Object.assign({ type: 'value' }, AXIS_STYLE),
        yAxis: {
            type: 'category',
            data: names,
            axisLine: { lineStyle: { color: '#334155' } },
            axisLabel: { color: '#f1f5f9', fontSize: 12 }
        },
        tooltip: Object.assign({ trigger: 'axis', axisPointer: { type: 'shadow' } }, TOOLTIP_STYLE),
        series: [{
            type: 'bar',
            data: values,
            itemStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                    { offset: 0, color: '#3b82f6' },
                    { offset: 1, color: '#60a5fa' }
                ]),
                borderRadius: [0, 6, 6, 0]
            },
            emphasis: { itemStyle: { color: '#93c5fd' } },
            barMaxWidth: 30,
            animationDelay: function(idx) { return idx * 50; }
        }],
        animationDuration: 1500
    });

    chart.on('click', function(params) {
        activeFilters._chartFilter = { col: nameCol, value: params.name };
        applyFilters();
    });
}
```

### b. chartRadar

```javascript
function chartRadar(containerId, data, nameCol, numericCols) {
    var chart = initChart(containerId);
    if (!chart) return;

    if (data.length === 0) { document.getElementById(containerId).innerHTML = renderEmptyState(); lucide.createIcons(); return; }

    // Take top 3 items (max 3 — overlapping areas unreadable)
    var top3 = data.slice().sort(function(a, b) {
        return parseFloat(b[numericCols[0]]) - parseFloat(a[numericCols[0]]);
    }).slice(0, 3);

    function shortLabel(text) {
        if (!text || text.length <= 10) return text;
        return text.substring(0, 10);
    }

    var indicator = numericCols.map(function(col) {
        var maxVal = Math.max.apply(null, data.map(function(r) { return parseFloat(r[col]) || 0; }));
        return { name: shortLabel(col), max: maxVal * 1.1 || 100 };
    });

    var seriesData = top3.map(function(row, idx) {
        return {
            value: numericCols.map(function(col) { return parseFloat(row[col]) || 0; }),
            name: row[nameCol],
            lineStyle: { color: CHART_COLORS[idx % CHART_COLORS.length], width: 2.5 },
            areaStyle: { color: CHART_COLORS[idx % CHART_COLORS.length], opacity: 0.25 },
            itemStyle: { color: CHART_COLORS[idx % CHART_COLORS.length] }
        };
    });

    chart.setOption({
        backgroundColor: '#1e293b',
        animationDuration: 1500,
        animationEasing: 'cubicOut',
        legend: {
            data: top3.map(function(r) { return r[nameCol]; }),
            bottom: 0,
            textStyle: { color: '#94a3b8' }
        },
        tooltip: TOOLTIP_STYLE,
        radar: {
            indicator: indicator,
            radius: '70%',
            shape: 'polygon',
            axisName: { color: '#94a3b8', fontSize: 11 },
            splitLine: { lineStyle: { color: '#334155' } },
            splitArea: { areaStyle: { color: ['transparent'] } },
            axisLine: { lineStyle: { color: '#334155' } }
        },
        series: [{ type: 'radar', data: seriesData }]
    });

    chart.on('click', function(params) {
        if (params.name) {
            activeFilters._chartFilter = { col: nameCol, value: params.name };
            applyFilters();
        }
    });
}
```

### c. chartScatter

```javascript
function chartScatter(containerId, data, xCol, yCol, nameCol, colorCol) {
    var chart = initChart(containerId);
    if (!chart) return;

    if (data.length === 0) { document.getElementById(containerId).innerHTML = renderEmptyState(); lucide.createIcons(); return; }

    var groups = {};
    data.forEach(function(row) {
        var key = colorCol ? (row[colorCol] || 'Other') : 'All';
        if (!groups[key]) groups[key] = [];
        groups[key].push(row);
    });

    var series = Object.keys(groups).map(function(key, idx) {
        return {
            name: key,
            type: 'scatter',
            data: groups[key].map(function(row) {
                return {
                    value: [parseFloat(row[xCol]) || 0, parseFloat(row[yCol]) || 0],
                    name: row[nameCol]
                };
            }),
            symbolSize: 10,
            itemStyle: { color: CHART_COLORS[idx % CHART_COLORS.length] },
            emphasis: { itemStyle: { borderColor: '#fff', borderWidth: 2 } }
        };
    });

    chart.setOption({
        backgroundColor: '#1e293b',
        animationDuration: 1500,
        animationEasing: 'cubicOut',
        grid: { left: '10%', right: '5%', top: '10%', bottom: '10%' },
        legend: { show: !!colorCol, top: 0, textStyle: { color: '#94a3b8' } },
        tooltip: Object.assign({
            trigger: 'item',
            formatter: function(params) {
                return '<strong>' + params.name + '</strong><br/>' +
                       xCol + ': ' + params.value[0] + '<br/>' +
                       yCol + ': ' + params.value[1];
            }
        }, TOOLTIP_STYLE),
        xAxis: Object.assign({ name: xCol, nameTextStyle: { color: '#94a3b8' } }, AXIS_STYLE),
        yAxis: Object.assign({ name: yCol, nameTextStyle: { color: '#94a3b8' } }, AXIS_STYLE),
        series: series
    });

    chart.on('click', function(params) {
        if (params.name) {
            activeFilters._chartFilter = { col: nameCol, value: params.name };
            applyFilters();
        }
    });
}
```

### d. chartLine

```javascript
function chartLine(containerId, data, dateCol, valueCol) {
    var chart = initChart(containerId);
    if (!chart) return;

    if (data.length === 0) { document.getElementById(containerId).innerHTML = renderEmptyState(); lucide.createIcons(); return; }

    var sorted = data.slice().sort(function(a, b) {
        return new Date(a[dateCol]) - new Date(b[dateCol]);
    });

    var dates = sorted.map(function(r) { return r[dateCol]; });
    var values = sorted.map(function(r) { return parseFloat(r[valueCol]) || 0; });

    chart.setOption({
        backgroundColor: '#1e293b',
        animationDuration: 1500,
        animationEasing: 'cubicOut',
        grid: { left: '8%', right: '5%', top: '10%', bottom: '18%' },
        tooltip: Object.assign({ trigger: 'axis' }, TOOLTIP_STYLE),
        xAxis: {
            type: 'category',
            data: dates,
            axisLine: { lineStyle: { color: '#334155' } },
            axisLabel: { color: '#94a3b8', rotate: 30 }
        },
        yAxis: Object.assign({
            type: 'value',
            name: valueCol,
            nameTextStyle: { color: '#94a3b8' }
        }, AXIS_STYLE),
        dataZoom: [
            { type: 'inside', start: 0, end: 100 },
            {
                type: 'slider', start: 0, end: 100, bottom: 5,
                borderColor: '#334155',
                backgroundColor: '#0f172a',
                fillerColor: 'rgba(96,165,250,0.2)',
                handleStyle: { color: '#60a5fa' },
                textStyle: { color: '#94a3b8' }
            }
        ],
        series: [{
            type: 'line',
            data: values,
            smooth: true,
            symbol: 'circle',
            symbolSize: 6,
            lineStyle: { color: '#60a5fa', width: 2 },
            itemStyle: { color: '#60a5fa' },
            areaStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: 'rgba(96,165,250,0.3)' },
                    { offset: 1, color: 'rgba(96,165,250,0.02)' }
                ])
            },
            emphasis: { itemStyle: { borderColor: '#fff', borderWidth: 2 } }
        }]
    });

    chart.on('click', function(params) {
        if (params.dataIndex !== undefined) {
            var row = sorted[params.dataIndex];
            if (row) showDetailPanel(row);
        }
    });
}
```

### e. chartBoxplot

```javascript
function chartBoxplot(containerId, data, categoryCol, valueCol) {
    var chart = initChart(containerId);
    if (!chart) return;

    if (data.length === 0) { document.getElementById(containerId).innerHTML = renderEmptyState(); lucide.createIcons(); return; }

    var groups = {};
    data.forEach(function(row) {
        var cat = row[categoryCol] || 'Other';
        if (!groups[cat]) groups[cat] = [];
        var v = parseFloat(row[valueCol]);
        if (!isNaN(v)) groups[cat].push(v);
    });

    var categories = Object.keys(groups);

    function quartiles(arr) {
        arr.sort(function(a, b) { return a - b; });
        var n = arr.length;
        var q1 = arr[Math.floor(n * 0.25)] || 0;
        var q2 = arr[Math.floor(n * 0.5)] || 0;
        var q3 = arr[Math.floor(n * 0.75)] || 0;
        var min = arr[0] || 0;
        var max = arr[n - 1] || 0;
        return [min, q1, q2, q3, max];
    }

    var boxData = categories.map(function(cat) { return quartiles(groups[cat]); });

    chart.setOption({
        backgroundColor: '#1e293b',
        animationDuration: 1500,
        animationEasing: 'cubicOut',
        grid: { left: '10%', right: '5%', top: '8%', bottom: '10%' },
        tooltip: Object.assign({
            trigger: 'item',
            formatter: function(params) {
                var d = params.data;
                return '<strong>' + params.name + '</strong><br/>' +
                       'Min: ' + d[1] + '<br/>Q1: ' + d[2] + '<br/>Median: ' + d[3] +
                       '<br/>Q3: ' + d[4] + '<br/>Max: ' + d[5];
            }
        }, TOOLTIP_STYLE),
        xAxis: {
            type: 'category',
            data: categories,
            axisLine: { lineStyle: { color: '#334155' } },
            axisLabel: { color: '#94a3b8' }
        },
        yAxis: Object.assign({
            type: 'value',
            name: valueCol,
            nameTextStyle: { color: '#94a3b8' }
        }, AXIS_STYLE),
        series: [{
            name: valueCol,
            type: 'boxplot',
            data: boxData,
            itemStyle: { color: '#1e293b', borderColor: '#60a5fa' },
            emphasis: { itemStyle: { borderColor: '#93c5fd', borderWidth: 2 } }
        }]
    });

    chart.on('click', function(params) {
        if (params.name) {
            activeFilters._chartFilter = { col: categoryCol, value: params.name };
            applyFilters();
        }
    });
}
```

### f. chartTreemap

```javascript
function chartTreemap(containerId, data, categoryCol, valueCol) {
    var chart = initChart(containerId);
    if (!chart) return;

    if (data.length === 0) { document.getElementById(containerId).innerHTML = renderEmptyState(); lucide.createIcons(); return; }

    var aggregated = {};
    data.forEach(function(row) {
        var cat = row[categoryCol] || 'Other';
        var val = parseFloat(row[valueCol]) || 0;
        if (!aggregated[cat]) aggregated[cat] = { sum: 0, count: 0 };
        aggregated[cat].sum += val;
        aggregated[cat].count += 1;
    });

    var treemapData = Object.keys(aggregated).map(function(cat, idx) {
        return {
            name: cat,
            value: aggregated[cat].sum,
            count: aggregated[cat].count,
            itemStyle: { color: CHART_COLORS[idx % CHART_COLORS.length] }
        };
    });

    chart.setOption({
        backgroundColor: '#1e293b',
        animationDuration: 1500,
        animationEasing: 'cubicOut',
        tooltip: Object.assign({
            formatter: function(params) {
                return '<strong>' + params.name + '</strong><br/>' +
                       'Total ' + valueCol + ': ' + params.value.toFixed(1) + '<br/>' +
                       'Count: ' + params.data.count;
            }
        }, TOOLTIP_STYLE),
        series: [{
            type: 'treemap',
            data: treemapData,
            roam: false,
            width: '100%',
            height: '100%',
            label: {
                show: true,
                formatter: '{b}',
                color: '#f1f5f9',
                fontSize: 13,
                fontWeight: 'bold'
            },
            breadcrumb: { show: false },
            levels: [{
                itemStyle: { borderColor: '#1e293b', borderWidth: 3, gapWidth: 3 }
            }]
        }]
    });

    chart.on('click', function(params) {
        if (params.name) {
            activeFilters._chartFilter = { col: categoryCol, value: params.name };
            applyFilters();
        }
    });
}
```

### g. chartDonut (NEW)

```javascript
function chartDonut(containerId, data, categoryCol, valueCol) {
    var chart = initChart(containerId);
    if (!chart) return;

    if (data.length === 0) { document.getElementById(containerId).innerHTML = renderEmptyState(); lucide.createIcons(); return; }

    // Aggregate by category
    var aggregated = {};
    data.forEach(function(row) {
        var cat = row[categoryCol] || 'Other';
        var val = parseFloat(row[valueCol]) || 1;
        if (!aggregated[cat]) aggregated[cat] = 0;
        aggregated[cat] += val;
    });

    var total = Object.values(aggregated).reduce(function(a, b) { return a + b; }, 0);

    var pieData = Object.keys(aggregated).map(function(cat, idx) {
        return {
            name: cat,
            value: aggregated[cat],
            itemStyle: { color: CHART_COLORS[idx % CHART_COLORS.length] }
        };
    }).sort(function(a, b) { return b.value - a.value; });

    chart.setOption({
        backgroundColor: '#1e293b',
        animationDuration: 1500,
        animationEasing: 'cubicOut',
        tooltip: Object.assign({
            trigger: 'item',
            formatter: function(params) {
                var pct = ((params.value / total) * 100).toFixed(1);
                return '<strong>' + params.name + '</strong><br/>' +
                       valueCol + ': ' + params.value.toFixed(1) + ' (' + pct + '%)';
            }
        }, TOOLTIP_STYLE),
        legend: {
            orient: 'vertical',
            right: '5%',
            top: 'center',
            textStyle: { color: '#94a3b8', fontSize: 12 }
        },
        series: [{
            type: 'pie',
            radius: ['50%', '75%'],
            center: ['40%', '50%'],
            avoidLabelOverlap: true,
            itemStyle: {
                borderRadius: 6,
                borderColor: '#1e293b',
                borderWidth: 2
            },
            label: {
                show: true,
                position: 'outside',
                formatter: function(params) {
                    var pct = ((params.value / total) * 100).toFixed(1);
                    return params.name + '\n' + pct + '%';
                },
                color: '#94a3b8',
                fontSize: 11,
                lineHeight: 16
            },
            labelLine: {
                show: true,
                lineStyle: { color: '#475569' }
            },
            emphasis: {
                itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0, 0, 0, 0.3)' },
                label: { show: true, fontSize: 13, fontWeight: 'bold', color: '#f1f5f9' }
            },
            data: pieData
        }]
    });

    chart.on('click', function(params) {
        if (params.name) {
            activeFilters._chartFilter = { col: categoryCol, value: params.name };
            applyFilters();
        }
    });
}
```

### h. chartStackedBar (NEW)

```javascript
function chartStackedBar(containerId, data, categoryCol, subCategoryCol, valueCol) {
    var chart = initChart(containerId);
    if (!chart) return;

    if (data.length === 0) { document.getElementById(containerId).innerHTML = renderEmptyState(); lucide.createIcons(); return; }

    // Build matrix: categories (x-axis) x subCategories (stacks)
    var categories = [];
    var subCategories = [];
    var catSet = {};
    var subSet = {};
    var matrix = {};

    data.forEach(function(row) {
        var cat = row[categoryCol] || 'Other';
        var sub = subCategoryCol ? (row[subCategoryCol] || 'Other') : 'Total';
        var val = parseFloat(row[valueCol]) || 0;

        if (!catSet[cat]) { catSet[cat] = true; categories.push(cat); }
        if (!subSet[sub]) { subSet[sub] = true; subCategories.push(sub); }

        if (!matrix[sub]) matrix[sub] = {};
        if (!matrix[sub][cat]) matrix[sub][cat] = 0;
        matrix[sub][cat] += val;
    });

    var series = subCategories.map(function(sub, idx) {
        return {
            name: sub,
            type: 'bar',
            stack: 'total',
            data: categories.map(function(cat) { return matrix[sub][cat] || 0; }),
            itemStyle: {
                color: CHART_COLORS[idx % CHART_COLORS.length],
                borderRadius: idx === subCategories.length - 1 ? [4, 4, 0, 0] : [0, 0, 0, 0]
            },
            emphasis: { itemStyle: { opacity: 0.85 } },
            barMaxWidth: 40
        };
    });

    chart.setOption({
        backgroundColor: '#1e293b',
        animationDuration: 1500,
        animationEasing: 'cubicOut',
        grid: { left: '8%', right: '5%', top: '15%', bottom: '10%' },
        legend: {
            top: 0,
            textStyle: { color: '#94a3b8' }
        },
        tooltip: Object.assign({
            trigger: 'axis',
            axisPointer: { type: 'shadow' }
        }, TOOLTIP_STYLE),
        xAxis: {
            type: 'category',
            data: categories,
            axisLine: { lineStyle: { color: '#334155' } },
            axisLabel: { color: '#94a3b8', rotate: categories.length > 8 ? 30 : 0 }
        },
        yAxis: Object.assign({
            type: 'value',
            name: valueCol,
            nameTextStyle: { color: '#94a3b8' }
        }, AXIS_STYLE),
        series: series
    });

    chart.on('click', function(params) {
        if (params.name) {
            activeFilters._chartFilter = { col: categoryCol, value: params.name };
            applyFilters();
        }
    });
}
```

---

## 7. Table — renderTable()

Enhanced with rating stars, progress bar, currency, number formatters, and N/A badge.

```javascript
function renderTable(data) {
    if (data.length === 0) {
        document.getElementById('data-table').innerHTML = renderEmptyState();
        lucide.createIcons();
        return;
    }

    var columns = Object.keys(data[0] || {});

    // Column minWidth map (design rules)
    var MIN_WIDTH_MAP = { name: 200, price: 180, rating: 90 };
    // Badge color map for values
    var BADGE_MAP = {
        'Да': 'badge-yes', 'да': 'badge-yes', 'Yes': 'badge-yes', 'yes': 'badge-yes',
        'Нет': 'badge-no', 'нет': 'badge-no', 'No': 'badge-no', 'no': 'badge-no',
        'Триал': 'badge-partial', 'триал': 'badge-partial', 'Частично': 'badge-partial', 'частично': 'badge-partial',
        'Partial': 'badge-partial', 'partial': 'badge-partial'
    };
    // Hide long-text columns (show in detail panel instead)
    var HIDDEN_COLS = ['Ключевые функции', 'Интеграции', 'key_features', 'integrations', 'description', 'описание'];

    // Detect column types for specialized renderers
    function detectColType(col) {
        var lower = col.toLowerCase();
        if (lower.indexOf('rating') !== -1 || lower.indexOf('score') !== -1 || lower.indexOf('рейтинг') !== -1 || lower.indexOf('оценка') !== -1) return 'rating';
        if (lower.indexOf('price') !== -1 || lower.indexOf('cost') !== -1 || lower.indexOf('цена') !== -1 || lower.indexOf('стоимость') !== -1) return 'currency';
        if (lower.indexOf('percent') !== -1 || lower.indexOf('%') !== -1 || lower.indexOf('share') !== -1 || lower.indexOf('доля') !== -1) return 'percent';
        return null;
    }

    var columnDefs = columns.filter(function(col) {
        return HIDDEN_COLS.indexOf(col) === -1;
    }).map(function(col) {
        var isNumeric = COLUMNS.numeric.indexOf(col) !== -1;
        var colLower = col.toLowerCase();
        var minW = MIN_WIDTH_MAP[colLower] || (col === COLUMNS.name ? 200 : 100);
        var colType = detectColType(col);

        return {
            headerName: col,
            field: col,
            sortable: true,
            filter: true,
            resizable: true,
            minWidth: minW,
            cellStyle: isNumeric ? { textAlign: 'right' } : null,
            cellRenderer: function(params) {
                var val = params.value;

                // N/A badge for empty values
                if (val === null || val === undefined || val === '') {
                    return '<span class="badge-na">N/A</span>';
                }

                // Badge for yes/no values
                var cls = BADGE_MAP[val];
                if (cls) return '<span class="' + cls + '">' + val + '</span>';

                // Rating stars renderer
                if (colType === 'rating') {
                    var num = parseFloat(val);
                    if (!isNaN(num) && num >= 0 && num <= 5) {
                        var full = Math.floor(num);
                        var empty = 5 - full;
                        var stars = '';
                        for (var i = 0; i < full; i++) stars += '★';
                        for (var j = 0; j < empty; j++) stars += '<span class="empty">★</span>';
                        return '<span class="rating-stars">' + stars + '</span> <span style="color:#94a3b8;font-size:11px;">(' + num.toFixed(1) + ')</span>';
                    }
                }

                // Currency formatter
                if (colType === 'currency') {
                    var num2 = parseFloat(val);
                    if (!isNaN(num2)) return formatNumberText(num2, 'currency');
                }

                // Percent / progress bar renderer
                if (colType === 'percent') {
                    var num3 = parseFloat(val);
                    if (!isNaN(num3) && num3 >= 0 && num3 <= 100) {
                        var barColor = num3 >= 70 ? '#34d399' : num3 >= 40 ? '#fbbf24' : '#f87171';
                        return '<div style="display:flex;align-items:center;gap:8px;">' +
                                   '<div class="progress-bar-container" style="flex:1;">' +
                                       '<div class="progress-bar-fill" style="width:' + num3 + '%;background:' + barColor + ';"></div>' +
                                   '</div>' +
                                   '<span style="font-size:11px;color:#94a3b8;min-width:36px;text-align:right;">' + num3.toFixed(1) + '%</span>' +
                               '</div>';
                    }
                }

                // Numeric formatter for large numbers
                if (isNumeric) {
                    var numVal = parseFloat(val);
                    if (!isNaN(numVal)) return formatNumberText(numVal, 'integer');
                }

                // Truncate long text in cells
                var text = String(val);
                if (text.length > 100) return text.substring(0, 100) + '...';
                return text;
            }
        };
    });

    var gridOptions = {
        columnDefs: columnDefs,
        rowData: data,
        pagination: true,
        paginationPageSize: 50,
        domLayout: 'normal',
        animateRows: true,
        defaultColDef: {
            flex: 1,
            minWidth: 80
        },
        onRowClicked: function(event) {
            showDetailPanel(event.data);
        }
    };

    var gridDiv = document.getElementById('data-table');
    gridDiv.innerHTML = '';

    // AG Grid 31 community — createGrid API
    gridApi = agGrid.createGrid(gridDiv, gridOptions);
}

function exportCsv() {
    if (gridApi) {
        gridApi.exportDataAsCsv({ fileName: 'dashboard-export.csv' });
    }
}
```

---

## 8. Filters — initFilters, initRangeSliders, applyFilters

```javascript
function initFilters() {
    var container = document.getElementById('filter-dropdowns');
    container.innerHTML = '';

    COLUMNS.categories.forEach(function(col) {
        var uniqueValues = [];
        var seen = {};
        allData.forEach(function(row) {
            var val = row[col];
            if (val && !seen[val]) {
                seen[val] = true;
                uniqueValues.push(val);
            }
        });
        uniqueValues.sort();

        var wrapper = document.createElement('div');
        wrapper.innerHTML =
            '<label class="block text-xs uppercase tracking-wider text-slate-400 mb-1">' + col + '</label>' +
            '<select data-filter-col="' + col + '" onchange="applyFilters()" ' +
            'class="w-full px-3 py-2 bg-surface border border-border rounded-lg text-sm text-white focus:outline-none focus:ring-1 focus:ring-blue-500">' +
            '<option value="">All</option>' +
            uniqueValues.map(function(v) { return '<option value="' + v + '">' + v + '</option>'; }).join('') +
            '</select>';
        container.appendChild(wrapper);
    });
}

// === NEW: initRangeSliders ===
function initRangeSliders() {
    var container = document.getElementById('filter-range-sliders');
    if (!container) return;
    container.innerHTML = '';

    COLUMNS.numeric.forEach(function(col) {
        var values = allData.map(function(r) { return parseFloat(r[col]); }).filter(function(v) { return !isNaN(v); });
        if (values.length < 3) return;

        var minVal = Math.min.apply(null, values);
        var maxVal = Math.max.apply(null, values);
        if (minVal === maxVal) return;

        var sliderId = 'range-' + col.replace(/[^a-zA-Z0-9]/g, '_');
        rangeFilters[col] = { min: minVal, max: maxVal };

        var wrapper = document.createElement('div');
        wrapper.className = 'mb-4';
        wrapper.innerHTML =
            '<label class="block text-xs uppercase tracking-wider text-slate-400 mb-1">' + col + '</label>' +
            '<div class="range-slider-track" id="' + sliderId + '-track">' +
                '<div class="range-slider-fill" id="' + sliderId + '-fill"></div>' +
                '<div class="range-slider-handle" id="' + sliderId + '-min" data-col="' + col + '" data-handle="min"></div>' +
                '<div class="range-slider-handle" id="' + sliderId + '-max" data-col="' + col + '" data-handle="max"></div>' +
            '</div>' +
            '<div class="range-slider-labels">' +
                '<span id="' + sliderId + '-min-label">' + minVal.toFixed(1) + '</span>' +
                '<span id="' + sliderId + '-max-label">' + maxVal.toFixed(1) + '</span>' +
            '</div>';
        container.appendChild(wrapper);

        // Position handles
        updateRangeSliderUI(sliderId, col, minVal, maxVal, minVal, maxVal);

        // Drag handlers
        var trackEl = document.getElementById(sliderId + '-track');
        ['-min', '-max'].forEach(function(suffix) {
            var handle = document.getElementById(sliderId + suffix);
            var isMin = suffix === '-min';

            handle.addEventListener('mousedown', function(e) {
                e.preventDefault();
                var trackRect = trackEl.getBoundingClientRect();

                function onMove(e2) {
                    var pct = Math.max(0, Math.min(1, (e2.clientX - trackRect.left) / trackRect.width));
                    var val = minVal + pct * (maxVal - minVal);

                    if (isMin) {
                        rangeFilters[col].min = Math.min(val, rangeFilters[col].max - 0.01);
                    } else {
                        rangeFilters[col].max = Math.max(val, rangeFilters[col].min + 0.01);
                    }

                    updateRangeSliderUI(sliderId, col, minVal, maxVal, rangeFilters[col].min, rangeFilters[col].max);
                }

                function onUp() {
                    document.removeEventListener('mousemove', onMove);
                    document.removeEventListener('mouseup', onUp);
                    applyFilters();
                }

                document.addEventListener('mousemove', onMove);
                document.addEventListener('mouseup', onUp);
            });
        });
    });
}

function updateRangeSliderUI(sliderId, col, absMin, absMax, curMin, curMax) {
    var range = absMax - absMin;
    if (range === 0) return;
    var minPct = ((curMin - absMin) / range) * 100;
    var maxPct = ((curMax - absMin) / range) * 100;

    var fill = document.getElementById(sliderId + '-fill');
    var minH = document.getElementById(sliderId + '-min');
    var maxH = document.getElementById(sliderId + '-max');
    var minL = document.getElementById(sliderId + '-min-label');
    var maxL = document.getElementById(sliderId + '-max-label');

    if (fill) { fill.style.left = minPct + '%'; fill.style.width = (maxPct - minPct) + '%'; }
    if (minH) minH.style.left = minPct + '%';
    if (maxH) maxH.style.left = maxPct + '%';
    if (minL) minL.textContent = curMin.toFixed(1);
    if (maxL) maxL.textContent = curMax.toFixed(1);
}

function applyFilters() {
    var searchQuery = (document.getElementById('search-input').value || '').toLowerCase();

    // Collect dropdown filters
    var dropdownFilters = {};
    document.querySelectorAll('[data-filter-col]').forEach(function(select) {
        var col = select.getAttribute('data-filter-col');
        var val = select.value;
        if (val) dropdownFilters[col] = val;
    });

    // Apply all filters
    filteredData = allData.filter(function(row) {
        // Search filter
        if (searchQuery) {
            var matches = false;
            Object.values(row).forEach(function(v) {
                if (String(v).toLowerCase().indexOf(searchQuery) !== -1) matches = true;
            });
            if (!matches) return false;
        }

        // Dropdown filters
        for (var col in dropdownFilters) {
            if (row[col] !== dropdownFilters[col]) return false;
        }

        // Range slider filters
        for (var rCol in rangeFilters) {
            var rf = rangeFilters[rCol];
            var numVal = parseFloat(row[rCol]);
            if (!isNaN(numVal)) {
                if (numVal < rf.min || numVal > rf.max) return false;
            }
        }

        // Chart click filter
        if (activeFilters._chartFilter) {
            var cf = activeFilters._chartFilter;
            if (row[cf.col] !== cf.value) return false;
        }

        return true;
    });

    // Update record count
    document.getElementById('record-count').textContent = filteredData.length;

    // Re-render all components with filtered data
    renderKPIs(filteredData);
    renderPrimaryChart(filteredData);
    renderComparisonChart(filteredData);
    renderTable(filteredData);
}

function resetFilters() {
    document.getElementById('search-input').value = '';
    document.querySelectorAll('[data-filter-col]').forEach(function(select) {
        select.value = '';
    });
    activeFilters = {};

    // Reset range sliders to full range
    COLUMNS.numeric.forEach(function(col) {
        var values = allData.map(function(r) { return parseFloat(r[col]); }).filter(function(v) { return !isNaN(v); });
        if (values.length < 3) return;
        var minVal = Math.min.apply(null, values);
        var maxVal = Math.max.apply(null, values);
        rangeFilters[col] = { min: minVal, max: maxVal };
        var sliderId = 'range-' + col.replace(/[^a-zA-Z0-9]/g, '_');
        updateRangeSliderUI(sliderId, col, minVal, maxVal, minVal, maxVal);
    });

    applyFilters();
}

// Sidebar toggle for mobile
function toggleSidebar() {
    document.getElementById('filter-sidebar').classList.toggle('open');
}
```

**Note:** `renderPrimaryChart(data)` and `renderComparisonChart(data)` are wrapper
functions the dashboard-designer creates based on the decision table. Example:

```javascript
function renderPrimaryChart(data) {
    chartHorizontalBar('chart-primary', data, COLUMNS.name, COLUMNS.numeric[0]);
}
function renderComparisonChart(data) {
    chartRadar('chart-comparison', data, COLUMNS.name, COLUMNS.numeric);
}
```

---

## 9. Detail Panel — showDetailPanel() & closeDetailPanel()

```javascript
function showDetailPanel(rowData) {
    var panel = document.getElementById('detail-panel');
    var overlay = document.getElementById('detail-overlay');
    var title = document.getElementById('detail-title');
    var content = document.getElementById('detail-content');

    title.textContent = rowData[COLUMNS.name] || 'Details';

    var html = '<div class="space-y-3">';
    Object.keys(rowData).forEach(function(key) {
        var value = rowData[key];
        var isNumeric = COLUMNS.numeric.indexOf(key) !== -1;
        var displayValue = (value !== null && value !== undefined && value !== '') ? value : '<span class="badge-na">N/A</span>';
        html += '<div class="border-b border-border pb-2">' +
                    '<div class="text-xs uppercase tracking-wider text-slate-400">' + key + '</div>' +
                    '<div class="text-sm text-white mt-0.5' + (isNumeric ? ' font-mono' : '') + '">' +
                        displayValue +
                    '</div>' +
                '</div>';
    });

    // URL link if exists
    var urlFields = ['url', 'source_url', 'link', 'href', 'source'];
    urlFields.forEach(function(field) {
        var lowerKeys = {};
        Object.keys(rowData).forEach(function(k) { lowerKeys[k.toLowerCase()] = k; });
        var matchedKey = lowerKeys[field];
        if (matchedKey && rowData[matchedKey] && String(rowData[matchedKey]).match(/^https?:\/\//)) {
            html += '<a href="' + rowData[matchedKey] + '" target="_blank" rel="noopener noreferrer" ' +
                    'class="inline-flex items-center gap-1 mt-3 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm transition">' +
                    '<i data-lucide="external-link" class="w-4 h-4"></i> Open Source' +
                    '</a>';
        }
    });

    html += '</div>';
    content.innerHTML = html;
    lucide.createIcons();

    panel.classList.add('open');
    overlay.classList.add('open');
}

function closeDetailPanel() {
    document.getElementById('detail-panel').classList.remove('open');
    document.getElementById('detail-overlay').classList.remove('open');
}

document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') closeDetailPanel();
});
```

---

## 10. Assembly Instructions

The dashboard-designer agent assembles the final `dashboard.html` by following these steps:

### Step 1: Analyze data
1. Read `normalized.json` for `column_types`.
2. Read first 5 rows of `data.csv`.
3. Apply dual-verification rules from `design-rules.md` section 2.
4. Classify columns into: `name`, `numeric[]`, `date`, `categories[]`.
5. Pick data type from the decision table.

### Step 2: Build COLUMNS object
```javascript
const COLUMNS = {
    name: 'product_name',        // first string column
    numeric: ['rating', 'price'], // all numeric columns
    date: null,                   // date column or null
    categories: ['brand', 'type'] // categorical columns (<15 unique values)
};
```

### Step 3: Copy base HTML (section 1)
Replace all `{{placeholders}}` with actual values. Embed `allData` as JSON.

### Step 4: Insert all function code
Copy into a single `<script>` block in this order:
1. Global state + COLUMNS (already in base)
2. Utility functions: formatNumber, formatNumberText, formatDate
3. Loading/empty/error state functions
4. Footer function
5. Common chart setup (CHART_COLORS, initChart, TOOLTIP_STYLE, AXIS_STYLE, resize handler)
6. renderKPIs
7. The chart functions needed (based on decision table row)
8. renderTable + exportCsv
9. initFilters + initRangeSliders + applyFilters + resetFilters + toggleSidebar
10. showDetailPanel + closeDetailPanel + Esc handler

### Step 5: Create wrapper functions
Based on the chosen data type, create `renderPrimaryChart(data)` and
`renderComparisonChart(data)` that call the appropriate chart function.

### Step 6: Add initialization code at the end of the script
```javascript
// Initialize everything on page load
(function() {
    renderLoadingSkeleton();
    setTimeout(function() {
        initFilters();
        initRangeSliders();
        applyFilters(); // This triggers renderKPIs, charts, and table
        renderFooter({ date: '{{DATE}}', sources: '{{SOURCES}}' });
        lucide.createIcons();
    }, 100);
})();
```

### Step 7: Validate
Ensure the HTML file:
- Has no syntax errors (all tags closed, all JS semicolons in place)
- All chart containers have explicit height styles
- `allData` JSON is valid and not truncated
- Column names in COLUMNS match the actual data keys exactly
- BOM stripped from column names: `key.replace(/^\uFEFF/, '')`
- Footer is rendered with correct metadata
- Empty/error states handled for all components
