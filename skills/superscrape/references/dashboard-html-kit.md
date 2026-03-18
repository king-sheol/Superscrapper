# Dashboard HTML Kit — Complete Code Snippets

Reference for the dashboard-generator agent when building **static HTML** dashboards.
Read `dashboard-template.md` FIRST for decision table and design tokens.

All snippets below are COMPLETE and WORKING. The agent copies them into a single
`dashboard.html` file, replacing placeholders with actual data and column names.

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
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            font-variant-numeric: tabular-nums;
            background: #0f172a;
            color: #f1f5f9;
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
        .badge-yes { background: #059669; color: #fff; border-radius: 9999px; font-size: 11px; padding: 2px 8px; }
        .badge-no { background: #dc2626; color: #fff; border-radius: 9999px; font-size: 11px; padding: 2px 8px; }
        .badge-partial { background: #d97706; color: #fff; border-radius: 9999px; font-size: 11px; padding: 2px 8px; }
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
        #detail-panel.open {
            transform: translateX(0);
        }
        #detail-overlay {
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.5);
            z-index: 40;
            display: none;
        }
        #detail-overlay.open {
            display: block;
        }
    </style>
</head>
<body class="bg-base min-h-screen">

    <!-- Header -->
    <header class="border-b border-border px-6 py-4">
        <h1 class="text-2xl font-bold text-white">{{TOPIC}}</h1>
        <p class="text-sm text-slate-400 mt-1">
            Date: {{DATE}} &middot; Records: <span id="record-count">0</span> &middot; Sources: {{SOURCES}}
        </p>
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

    <script>
    // === GLOBAL STATE ===
    // The dashboard-generator replaces this with actual data
    const allData = {{DATA_JSON}};
    let filteredData = [...allData];
    let activeFilters = {};
    let gridApi = null;
    let chartInstances = {};

    // Column classification (filled by dashboard-generator)
    const COLUMNS = {{COLUMNS_JSON}};
    // Example: { name: 'product', numeric: ['rating','price'], date: null, categories: ['brand','type'] }
    </script>

    <!-- Remaining <script> sections follow below -->

</body>
</html>
```

**Placeholders the dashboard-generator must replace:**
- `{{TOPIC}}` — research topic title
- `{{DATE}}` — collection date
- `{{SOURCES}}` — number of sources
- `{{DATA_JSON}}` — `JSON.stringify(data)` from data.csv
- `{{COLUMNS_JSON}}` — column classification object

---

## 2. KPI Cards — renderKPIs()

Insert this inside the main `<script>` block.

```javascript
function renderKPIs(data) {
    const container = document.getElementById('kpi-grid');
    container.innerHTML = '';

    const kpis = [];

    // Always show total records
    kpis.push({
        label: 'Total Records',
        value: data.length,
        detail: 'filtered',
        icon: 'database'
    });

    // Auto-detect numeric columns and compute stats
    COLUMNS.numeric.forEach(function(col, idx) {
        var values = data.map(function(r) { return parseFloat(r[col]); }).filter(function(v) { return !isNaN(v); });
        if (values.length === 0) return;

        var sum = values.reduce(function(a, b) { return a + b; }, 0);
        var avg = sum / values.length;
        var max = Math.max.apply(null, values);
        var min = Math.min.apply(null, values);

        // First numeric col: show avg; second: show max; third: show min
        if (idx === 0) {
            kpis.push({ label: 'Avg ' + col, value: avg.toFixed(1), detail: 'min ' + min.toFixed(1) + ' / max ' + max.toFixed(1), icon: 'trending-up' });
        } else if (idx === 1) {
            kpis.push({ label: 'Max ' + col, value: max.toFixed(1), detail: 'avg ' + avg.toFixed(1), icon: 'arrow-up-right' });
        } else if (idx === 2) {
            kpis.push({ label: 'Min ' + col, value: min.toFixed(1), detail: 'avg ' + avg.toFixed(1), icon: 'arrow-down-right' });
        }
    });

    // Render cards with countUp animation
    kpis.forEach(function(kpi) {
        var card = document.createElement('div');
        card.className = 'glass-card rounded-xl p-4';
        card.innerHTML =
            '<div class="flex items-center gap-2 mb-2">' +
                '<i data-lucide="' + kpi.icon + '" class="w-4 h-4 text-slate-400"></i>' +
                '<span class="text-xs uppercase tracking-wider text-slate-400">' + kpi.label + '</span>' +
            '</div>' +
            '<div class="text-2xl font-bold text-white kpi-value" data-target="' + kpi.value + '">0</div>' +
            '<div class="text-xs text-slate-500 mt-1">' + kpi.detail + '</div>';
        container.appendChild(card);
    });

    // Initialize Lucide icons for new elements
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
            // Ease out cubic
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

## 3. Charts — 6 Chart Type Functions

All charts share these conventions:
- Dark background `#1e293b`
- Color palette from design tokens
- `animationDuration: 1500` with `animationEasing: 'cubicOut'`
- Responsive via `window.addEventListener('resize', ...)`
- Click handler calls `applyFilters()` for chart-to-table filtering

Insert all functions inside the main `<script>` block.

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
        xAxis: {
            type: 'value',
            axisLine: { lineStyle: { color: '#334155' } },
            axisLabel: { color: '#94a3b8' },
            splitLine: { lineStyle: { color: '#334155' } }
        },
        yAxis: {
            type: 'category',
            data: names,
            axisLine: { lineStyle: { color: '#334155' } },
            axisLabel: { color: '#f1f5f9', fontSize: 12 }
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'shadow' },
            backgroundColor: '#1e293b',
            borderColor: '#334155',
            textStyle: { color: '#f1f5f9' },
            extraCssText: 'max-width: 400px; white-space: normal; word-wrap: break-word;'
        },
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
            emphasis: {
                itemStyle: { color: '#93c5fd' }
            },
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

    // Take top 3 items (not 5 — overlapping areas are unreadable)
    var top3 = data.slice().sort(function(a, b) {
        return parseFloat(b[numericCols[0]]) - parseFloat(a[numericCols[0]]);
    }).slice(0, 3);

    // Short label mapping for Cyrillic/long text (max 10 chars)
    function shortLabel(text) {
        if (!text || text.length <= 10) return text;
        return text.substring(0, 10);
    }

    // Build indicator with max values
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
        tooltip: {
            backgroundColor: '#1e293b',
            borderColor: '#334155',
            textStyle: { color: '#f1f5f9' },
            extraCssText: 'max-width: 400px; white-space: normal; word-wrap: break-word;'
        },
        radar: {
            indicator: indicator,
            radius: '70%',
            shape: 'polygon',
            axisName: { color: '#94a3b8', fontSize: 11 },
            splitLine: { lineStyle: { color: '#334155' } },
            splitArea: { areaStyle: { color: ['transparent'] } },
            axisLine: { lineStyle: { color: '#334155' } }
        },
        series: [{
            type: 'radar',
            data: seriesData
        }]
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

    // Group by colorCol if provided
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
        legend: {
            show: !!colorCol,
            top: 0,
            textStyle: { color: '#94a3b8' }
        },
        tooltip: {
            trigger: 'item',
            backgroundColor: '#1e293b',
            borderColor: '#334155',
            textStyle: { color: '#f1f5f9' },
            formatter: function(params) {
                return '<strong>' + params.name + '</strong><br/>' +
                       xCol + ': ' + params.value[0] + '<br/>' +
                       yCol + ': ' + params.value[1];
            }
        },
        xAxis: {
            name: xCol,
            nameTextStyle: { color: '#94a3b8' },
            axisLine: { lineStyle: { color: '#334155' } },
            axisLabel: { color: '#94a3b8' },
            splitLine: { lineStyle: { color: '#334155', type: 'dashed' } }
        },
        yAxis: {
            name: yCol,
            nameTextStyle: { color: '#94a3b8' },
            axisLine: { lineStyle: { color: '#334155' } },
            axisLabel: { color: '#94a3b8' },
            splitLine: { lineStyle: { color: '#334155', type: 'dashed' } }
        },
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

    // Sort by date
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
        tooltip: {
            trigger: 'axis',
            backgroundColor: '#1e293b',
            borderColor: '#334155',
            textStyle: { color: '#f1f5f9' }
        },
        xAxis: {
            type: 'category',
            data: dates,
            axisLine: { lineStyle: { color: '#334155' } },
            axisLabel: { color: '#94a3b8', rotate: 30 }
        },
        yAxis: {
            type: 'value',
            name: valueCol,
            nameTextStyle: { color: '#94a3b8' },
            axisLine: { lineStyle: { color: '#334155' } },
            axisLabel: { color: '#94a3b8' },
            splitLine: { lineStyle: { color: '#334155', type: 'dashed' } }
        },
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
            emphasis: {
                itemStyle: { borderColor: '#fff', borderWidth: 2 }
            }
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

    // Group values by category
    var groups = {};
    data.forEach(function(row) {
        var cat = row[categoryCol] || 'Other';
        if (!groups[cat]) groups[cat] = [];
        var v = parseFloat(row[valueCol]);
        if (!isNaN(v)) groups[cat].push(v);
    });

    var categories = Object.keys(groups);

    // Compute quartile stats for each category
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

    var boxData = categories.map(function(cat) {
        return quartiles(groups[cat]);
    });

    chart.setOption({
        backgroundColor: '#1e293b',
        animationDuration: 1500,
        animationEasing: 'cubicOut',
        grid: { left: '10%', right: '5%', top: '8%', bottom: '10%' },
        tooltip: {
            trigger: 'item',
            backgroundColor: '#1e293b',
            borderColor: '#334155',
            textStyle: { color: '#f1f5f9' },
            formatter: function(params) {
                var d = params.data;
                return '<strong>' + params.name + '</strong><br/>' +
                       'Min: ' + d[1] + '<br/>Q1: ' + d[2] + '<br/>Median: ' + d[3] +
                       '<br/>Q3: ' + d[4] + '<br/>Max: ' + d[5];
            }
        },
        xAxis: {
            type: 'category',
            data: categories,
            axisLine: { lineStyle: { color: '#334155' } },
            axisLabel: { color: '#94a3b8' }
        },
        yAxis: {
            type: 'value',
            name: valueCol,
            nameTextStyle: { color: '#94a3b8' },
            axisLine: { lineStyle: { color: '#334155' } },
            axisLabel: { color: '#94a3b8' },
            splitLine: { lineStyle: { color: '#334155', type: 'dashed' } }
        },
        series: [{
            name: valueCol,
            type: 'boxplot',
            data: boxData,
            itemStyle: {
                color: '#1e293b',
                borderColor: '#60a5fa'
            },
            emphasis: {
                itemStyle: { borderColor: '#93c5fd', borderWidth: 2 }
            }
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

    // Aggregate values by category
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
        tooltip: {
            backgroundColor: '#1e293b',
            borderColor: '#334155',
            textStyle: { color: '#f1f5f9' },
            formatter: function(params) {
                return '<strong>' + params.name + '</strong><br/>' +
                       'Total ' + valueCol + ': ' + params.value.toFixed(1) + '<br/>' +
                       'Count: ' + params.data.count;
            }
        },
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
                itemStyle: {
                    borderColor: '#1e293b',
                    borderWidth: 3,
                    gapWidth: 3
                }
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

---

## 4. Table — renderTable()

```javascript
function renderTable(data) {
    var columns = Object.keys(data[0] || {});

    // Column minWidth map (design rules)
    var MIN_WIDTH_MAP = { name: 200, price: 180, rating: 90 };
    // Badge color map for Да/Нет/Триал values
    var BADGE_MAP = {
        'Да': 'badge-yes', 'да': 'badge-yes', 'Yes': 'badge-yes',
        'Нет': 'badge-no', 'нет': 'badge-no', 'No': 'badge-no',
        'Триал': 'badge-partial', 'триал': 'badge-partial', 'Частично': 'badge-partial', 'частично': 'badge-partial'
    };
    // Hide long-text columns (show in detail panel instead)
    var HIDDEN_COLS = ['Ключевые функции', 'Интеграции', 'key_features', 'integrations'];

    var columnDefs = columns.filter(function(col) {
        return HIDDEN_COLS.indexOf(col) === -1;
    }).map(function(col) {
        var isNumeric = COLUMNS.numeric.indexOf(col) !== -1;
        var colLower = col.toLowerCase();
        var minW = MIN_WIDTH_MAP[colLower] || (col === COLUMNS.name ? 200 : 100);
        return {
            headerName: col,
            field: col,
            sortable: true,
            filter: true,
            resizable: true,
            minWidth: minW,
            cellStyle: isNumeric ? { textAlign: 'right' } : null,
            valueFormatter: isNumeric ? function(params) {
                var v = parseFloat(params.value);
                return isNaN(v) ? params.value : v.toFixed(2);
            } : null,
            cellRenderer: function(params) {
                var cls = BADGE_MAP[params.value];
                if (cls) return '<span class="' + cls + '">' + params.value + '</span>';
                // Truncate long text in cells
                var text = String(params.value || '');
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

## 5. Filters — initFilters() & applyFilters()

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
        // Search filter: match any field
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
    applyFilters();
}
```

**Note:** `renderPrimaryChart(data)` and `renderComparisonChart(data)` are wrapper
functions the dashboard-generator creates based on the decision table. Example:

```javascript
function renderPrimaryChart(data) {
    // For rating data type:
    chartHorizontalBar('chart-primary', data, COLUMNS.name, COLUMNS.numeric[0]);
}
function renderComparisonChart(data) {
    // For rating data type:
    chartRadar('chart-comparison', data, COLUMNS.name, COLUMNS.numeric);
}
```

---

## 6. Detail Panel — showDetailPanel() & closeDetailPanel()

```javascript
function showDetailPanel(rowData) {
    var panel = document.getElementById('detail-panel');
    var overlay = document.getElementById('detail-overlay');
    var title = document.getElementById('detail-title');
    var content = document.getElementById('detail-content');

    // Set title to the name column value
    title.textContent = rowData[COLUMNS.name] || 'Details';

    // Build field list
    var html = '<div class="space-y-3">';
    Object.keys(rowData).forEach(function(key) {
        var value = rowData[key];
        var isNumeric = COLUMNS.numeric.indexOf(key) !== -1;
        html += '<div class="border-b border-border pb-2">' +
                    '<div class="text-xs uppercase tracking-wider text-slate-400">' + key + '</div>' +
                    '<div class="text-sm text-white mt-0.5' + (isNumeric ? ' font-mono' : '') + '">' +
                        (value !== null && value !== undefined ? value : '—') +
                    '</div>' +
                '</div>';
    });

    // "Open Source" link if a URL field exists
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

    // Re-init Lucide icons inside panel
    lucide.createIcons();

    // Open panel
    panel.classList.add('open');
    overlay.classList.add('open');
}

function closeDetailPanel() {
    document.getElementById('detail-panel').classList.remove('open');
    document.getElementById('detail-overlay').classList.remove('open');
}

// Close on Escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') closeDetailPanel();
});
```

---

## 7. Assembly Instructions

The dashboard-generator agent assembles the final `dashboard.html` by following these steps:

### Step 1: Analyze data
1. Read `normalized.json` for `column_types`.
2. Read first 5 rows of `data.csv`.
3. Apply dual-verification rules from `dashboard-template.md` section 2.
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
2. Common chart setup (CHART_COLORS, initChart, resize handler)
3. renderKPIs
4. The chart functions needed (based on decision table row)
5. renderTable + exportCsv
6. initFilters + applyFilters + resetFilters
7. showDetailPanel + closeDetailPanel + Esc handler

### Step 5: Create wrapper functions
Based on the chosen data type, create `renderPrimaryChart(data)` and
`renderComparisonChart(data)` that call the appropriate chart function.

### Step 6: Add initialization code at the end of the script
```javascript
// Initialize everything on page load
(function() {
    initFilters();
    applyFilters(); // This triggers renderKPIs, charts, and table
    lucide.createIcons();
})();
```

### Step 7: Validate
Ensure the HTML file:
- Has no syntax errors (all tags closed, all JS semicolons in place)
- All chart containers have explicit height styles
- `allData` JSON is valid and not truncated
- Column names in COLUMNS match the actual data keys exactly
