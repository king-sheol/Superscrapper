# HTML ECharts Chart Functions

8 chart functions for HTML dashboards (vanilla JS). Each calls `initChart(containerId)` and sets option via `chart.setOption()`.
Uses `CHART_COLORS`, `TOOLTIP_STYLE`, `AXIS_STYLE` from base template.

```javascript
function chartHorizontalBar(containerId, data, nameCol, valueCol) {
    if (data.length === 0) { document.getElementById(containerId).innerHTML = '<div class="empty-state">No data available</div>'; return; }
    const chart = initChart(containerId);
    const sorted = [...data].sort((a, b) => (+b[valueCol]) - (+a[nameCol])).slice(0, 20).reverse();
    const names = sorted.map(d => String(d[nameCol]));
    const values = sorted.map(d => +d[valueCol]);
    chart.setOption({
        tooltip: { ...TOOLTIP_STYLE, trigger: 'axis', axisPointer: { type: 'shadow' } },
        grid: { left: '3%', right: '6%', bottom: '3%', top: '3%', containLabel: true },
        xAxis: { type: 'value', axisLabel: { ...AXIS_STYLE } },
        yAxis: { type: 'category', data: names, axisLabel: { ...AXIS_STYLE, width: 120, overflow: 'truncate' } },
        series: [{
            type: 'bar', data: values, barMaxWidth: 28,
            itemStyle: {
                borderRadius: [0, 4, 4, 0],
                color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                    { offset: 0, color: '#60a5fa' }, { offset: 1, color: '#34d399' }
                ])
            },
            animationDelay: idx => idx * 80
        }],
        animationDuration: 1500, animationEasing: 'cubicOut'
    });
    chart.on('click', p => { activeFilters._chartFilter = { col: nameCol, val: names[p.dataIndex] }; applyFilters(); });
}

function chartRadar(containerId, data, nameCol, numericCols) {
    if (data.length === 0) { document.getElementById(containerId).innerHTML = '<div class="empty-state">No data available</div>'; return; }
    const chart = initChart(containerId);
    const top3 = [...data].sort((a, b) => (+b[numericCols[0]]) - (+a[numericCols[0]])).slice(0, 3);
    const maxVals = numericCols.map(c => Math.max(...data.map(d => +d[c] || 0)) * 1.1 || 1);
    const indicators = numericCols.map((c, i) => ({ name: c.slice(0, 10), max: maxVals[i] }));
    const seriesData = top3.map((item, i) => ({
        value: numericCols.map(c => +item[c] || 0),
        name: String(item[nameCol]).slice(0, 20),
        lineStyle: { width: 2 }, areaStyle: { opacity: 0.15 },
        itemStyle: { color: CHART_COLORS[i % CHART_COLORS.length] }
    }));
    chart.setOption({
        tooltip: { ...TOOLTIP_STYLE },
        legend: { data: seriesData.map(d => d.name), bottom: 0, textStyle: { color: '#e2e8f0' } },
        radar: { indicator: indicators, radius: '70%', axisName: { color: '#94a3b8' },
            splitArea: { areaStyle: { color: ['rgba(30,41,59,0.5)', 'rgba(15,23,42,0.5)'] } } },
        series: [{ type: 'radar', data: seriesData }],
        animationDuration: 1500, animationEasing: 'cubicOut'
    });
    chart.on('click', p => { activeFilters._chartFilter = { col: nameCol, val: p.name }; applyFilters(); });
}

function chartScatter(containerId, data, xCol, yCol, nameCol, colorCol) {
    if (data.length === 0) { document.getElementById(containerId).innerHTML = '<div class="empty-state">No data available</div>'; return; }
    const chart = initChart(containerId);
    const xVals = data.map(d => +d[xCol]).filter(v => v > 0);
    const useLog = xVals.length > 0 && (Math.max(...xVals) / Math.min(...xVals)) > 100;
    const series = [];
    if (colorCol) {
        const groups = {};
        data.forEach(d => { const g = d[colorCol] || 'Other'; (groups[g] = groups[g] || []).push(d); });
        Object.keys(groups).forEach((g, i) => {
            series.push({
                type: 'scatter', name: String(g), symbolSize: 10,
                data: groups[g].map(d => [+d[xCol], +d[yCol], String(d[nameCol])]),
                itemStyle: { color: CHART_COLORS[i % CHART_COLORS.length] }
            });
        });
    } else {
        series.push({
            type: 'scatter', name: yCol, symbolSize: 10,
            data: data.map(d => [+d[xCol], +d[yCol], String(d[nameCol])]),
            itemStyle: { color: CHART_COLORS[0] }
        });
    }
    chart.setOption({
        tooltip: { ...TOOLTIP_STYLE, formatter: p => p.value[2] },
        legend: { textStyle: { color: '#e2e8f0' }, bottom: 0 },
        xAxis: { type: useLog ? 'log' : 'value', name: xCol, axisLabel: { ...AXIS_STYLE } },
        yAxis: { type: 'value', name: yCol, axisLabel: { ...AXIS_STYLE } },
        series, animationDuration: 1500, animationEasing: 'cubicOut'
    });
    chart.on('click', p => { activeFilters._chartFilter = { col: nameCol, val: p.value[2] }; applyFilters(); });
}

function chartLine(containerId, data, dateCol, valueCol) {
    if (data.length === 0) { document.getElementById(containerId).innerHTML = '<div class="empty-state">No data available</div>'; return; }
    const chart = initChart(containerId);
    const sorted = [...data].sort((a, b) => String(a[dateCol]).localeCompare(String(b[dateCol])));
    const dates = sorted.map(d => String(d[dateCol]));
    const values = sorted.map(d => +d[valueCol]);
    chart.setOption({
        tooltip: { ...TOOLTIP_STYLE, trigger: 'axis' },
        xAxis: { type: 'category', data: dates, axisLabel: { ...AXIS_STYLE } },
        yAxis: { type: 'value', axisLabel: { ...AXIS_STYLE } },
        dataZoom: [{ type: 'slider', start: 0, end: 100, height: 20, bottom: 5 }],
        grid: { bottom: '15%' },
        series: [{
            type: 'line', data: values, smooth: true, symbol: 'none',
            lineStyle: { width: 2, color: '#60a5fa' },
            areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(96,165,250,0.4)' }, { offset: 1, color: 'rgba(96,165,250,0.02)' }
            ]) }
        }],
        animationDuration: 1500, animationEasing: 'cubicOut'
    });
    chart.on('click', p => { activeFilters._chartFilter = { col: dateCol, val: dates[p.dataIndex] }; applyFilters(); });
}

function chartBoxplot(containerId, data, categoryCol, valueCol) {
    if (data.length === 0) { document.getElementById(containerId).innerHTML = '<div class="empty-state">No data available</div>'; return; }
    const chart = initChart(containerId);
    const groups = {};
    data.forEach(d => { const c = String(d[categoryCol]).slice(0, 15); (groups[c] = groups[c] || []).push(+d[valueCol]); });
    const categories = [], boxData = [];
    Object.entries(groups).forEach(([cat, vals]) => {
        if (vals.length < 5) return;
        vals.sort((a, b) => a - b);
        const q = p => { const i = (vals.length - 1) * p; const lo = Math.floor(i); return vals[lo] + (vals[lo + 1] - vals[lo]) * (i - lo); };
        categories.push(cat);
        boxData.push([vals[0], q(0.25), q(0.5), q(0.75), vals[vals.length - 1]]);
    });
    if (!categories.length) { document.getElementById(containerId).innerHTML = '<div class="empty-state">Insufficient data</div>'; return; }
    chart.setOption({
        tooltip: { ...TOOLTIP_STYLE, trigger: 'item' },
        xAxis: { type: 'category', data: categories, axisLabel: { ...AXIS_STYLE } },
        yAxis: { type: 'value', axisLabel: { ...AXIS_STYLE } },
        series: [{ type: 'boxplot', data: boxData,
            itemStyle: { color: '#1e293b', borderColor: '#60a5fa', borderWidth: 2 } }],
        animationDuration: 1500, animationEasing: 'cubicOut'
    });
    chart.on('click', p => { activeFilters._chartFilter = { col: categoryCol, val: categories[p.dataIndex] }; applyFilters(); });
}

function chartTreemap(containerId, data, categoryCol, valueCol) {
    if (data.length === 0) { document.getElementById(containerId).innerHTML = '<div class="empty-state">No data available</div>'; return; }
    const chart = initChart(containerId);
    const agg = {};
    data.forEach(d => { const c = String(d[categoryCol]); agg[c] = (agg[c] || 0) + (+d[valueCol] || 0); });
    const children = Object.entries(agg).filter(([, v]) => v > 0)
        .sort((a, b) => b[1] - a[1])
        .map(([name, value], i) => ({ name, value, itemStyle: { color: CHART_COLORS[i % CHART_COLORS.length] } }));
    if (!children.length) { document.getElementById(containerId).innerHTML = '<div class="empty-state">No data</div>'; return; }
    chart.setOption({
        tooltip: { ...TOOLTIP_STYLE },
        series: [{ type: 'treemap', data: children, roam: false,
            label: { show: true, color: '#f1f5f9', fontSize: 12 },
            breadcrumb: { show: false },
            levels: [{ itemStyle: { borderColor: '#0f172a', borderWidth: 2, gapWidth: 2 } }] }],
        animationDuration: 1500, animationEasing: 'cubicOut'
    });
    chart.on('click', p => { activeFilters._chartFilter = { col: categoryCol, val: p.name }; applyFilters(); });
}

function chartDonut(containerId, data, categoryCol, valueCol) {
    if (data.length === 0) { document.getElementById(containerId).innerHTML = '<div class="empty-state">No data available</div>'; return; }
    const chart = initChart(containerId);
    const agg = {};
    data.forEach(d => {
        const c = String(d[categoryCol]);
        agg[c] = (agg[c] || 0) + (valueCol ? (+d[valueCol] || 0) : 1);
    });
    const pieData = Object.entries(agg).map(([name, value]) => ({ name, value }));
    if (!pieData.length) { document.getElementById(containerId).innerHTML = '<div class="empty-state">No data</div>'; return; }
    chart.setOption({
        tooltip: { ...TOOLTIP_STYLE, trigger: 'item', formatter: '{b}: {c} ({d}%)' },
        legend: { orient: 'vertical', right: 10, top: 'center', textStyle: { color: '#e2e8f0' } },
        color: CHART_COLORS,
        series: [{ type: 'pie', radius: ['50%', '75%'], center: ['40%', '50%'], data: pieData,
            label: { show: true, formatter: '{b} {d}%', color: '#94a3b8' },
            emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.5)' } } }],
        animationDuration: 1500, animationEasing: 'cubicOut'
    });
    chart.on('click', p => { activeFilters._chartFilter = { col: categoryCol, val: p.name }; applyFilters(); });
}

function chartStackedBar(containerId, data, categoryCol, subCategoryCol, valueCol) {
    if (data.length === 0) { document.getElementById(containerId).innerHTML = '<div class="empty-state">No data available</div>'; return; }
    const chart = initChart(containerId);
    const pivot = {}, subCats = new Set();
    data.forEach(d => {
        const cat = String(d[categoryCol]), sub = String(d[subCategoryCol]);
        subCats.add(sub);
        if (!pivot[cat]) pivot[cat] = {};
        pivot[cat][sub] = (pivot[cat][sub] || 0) + (+d[valueCol] || 0);
    });
    const categories = Object.keys(pivot);
    const subList = [...subCats];
    const series = subList.map((sub, i) => ({
        name: sub, type: 'bar', stack: 'total', barMaxWidth: 40,
        data: categories.map(c => pivot[c][sub] || 0),
        itemStyle: { color: CHART_COLORS[i % CHART_COLORS.length] }
    }));
    chart.setOption({
        tooltip: { ...TOOLTIP_STYLE, trigger: 'axis', axisPointer: { type: 'shadow' } },
        legend: { textStyle: { color: '#e2e8f0' }, bottom: 0 },
        grid: { left: '3%', right: '4%', bottom: '12%', containLabel: true },
        xAxis: { type: 'category', data: categories, axisLabel: { ...AXIS_STYLE, rotate: 30 } },
        yAxis: { type: 'value', axisLabel: { ...AXIS_STYLE } },
        series, animationDuration: 1500, animationEasing: 'cubicOut'
    });
    chart.on('click', p => { activeFilters._chartFilter = { col: categoryCol, val: categories[p.dataIndex] }; applyFilters(); });
}
```
