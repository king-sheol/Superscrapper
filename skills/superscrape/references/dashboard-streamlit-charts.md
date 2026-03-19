# Streamlit ECharts Chart Functions

8 chart functions for Streamlit dashboards. Each receives a DataFrame + column names, returns an ECharts option dict.
Pass result to `st_echarts(option, height="450px")`.

```python
import pandas as pd
import numpy as np

CHART_COLORS = ['#60a5fa','#34d399','#fbbf24','#f87171','#a78bfa','#22d3ee','#fb923c','#e879f9']
TOOLTIP_STYLE = {'backgroundColor': '#1e293b', 'borderColor': '#334155', 'textStyle': {'color': '#f1f5f9'}}
ANIMATION = {'animationDuration': 1500, 'animationEasing': 'cubicOut'}


def chart_horizontal_bar(df, name_col, value_col):
    """Top-20 horizontal bar with gradient fill."""
    if df is None or df.empty or name_col not in df.columns or value_col not in df.columns:
        return None
    top = df.nlargest(20, value_col).sort_values(value_col, ascending=True)
    names = top[name_col].astype(str).tolist()
    values = top[value_col].tolist()
    return {
        'tooltip': {**TOOLTIP_STYLE, 'trigger': 'axis', 'axisPointer': {'type': 'shadow'}},
        'grid': {'left': '3%', 'right': '6%', 'bottom': '3%', 'top': '3%', 'containLabel': True},
        'xAxis': {'type': 'value', 'axisLabel': {'color': '#94a3b8'}},
        'yAxis': {'type': 'category', 'data': names, 'axisLabel': {'color': '#e2e8f0', 'width': 120, 'overflow': 'truncate'}},
        'series': [{
            'type': 'bar', 'data': values, 'barMaxWidth': 28, 'itemStyle': {
                'borderRadius': [0, 4, 4, 0],
                'color': {'type': 'linear', 'x': 0, 'y': 0, 'x2': 1, 'y2': 0,
                           'colorStops': [{'offset': 0, 'color': '#60a5fa'}, {'offset': 1, 'color': '#34d399'}]}
            },
            'animationDelay': {'__expr__': 'function(idx){return idx*80}'}
        }],
        **ANIMATION
    }


def chart_radar(df, name_col, numeric_cols):
    """Radar chart for top-3 items across numeric dimensions."""
    if df is None or df.empty or name_col not in df.columns:
        return None
    valid_cols = [c for c in numeric_cols if c in df.columns]
    if not valid_cols:
        return None
    top = df.nlargest(3, valid_cols[0]).head(3)
    indicators = [{'name': c[:10], 'max': float(df[c].max()) * 1.1 or 1} for c in valid_cols]
    series_data = []
    for i, (_, row) in enumerate(top.iterrows()):
        series_data.append({
            'value': [float(row.get(c, 0)) for c in valid_cols],
            'name': str(row[name_col])[:20],
            'lineStyle': {'width': 2},
            'areaStyle': {'opacity': 0.15},
            'itemStyle': {'color': CHART_COLORS[i % len(CHART_COLORS)]}
        })
    return {
        'tooltip': {**TOOLTIP_STYLE},
        'legend': {'data': [d['name'] for d in series_data], 'bottom': 0, 'textStyle': {'color': '#e2e8f0'}},
        'radar': {'indicator': indicators, 'radius': '70%', 'axisName': {'color': '#94a3b8'},
                  'splitArea': {'areaStyle': {'color': ['rgba(30,41,59,0.5)', 'rgba(15,23,42,0.5)']}}},
        'series': [{'type': 'radar', 'data': series_data}],
        **ANIMATION
    }


def chart_scatter(df, x_col, y_col, name_col, color_col=None):
    """Scatter plot, optionally grouped by color_col. Log x-axis if range > 100x."""
    if df is None or df.empty or x_col not in df.columns or y_col not in df.columns:
        return None
    x_min, x_max = df[x_col].min(), df[x_col].max()
    use_log = x_max > 0 and x_min > 0 and (x_max / x_min) > 100
    series = []
    if color_col and color_col in df.columns:
        for i, (grp, gdf) in enumerate(df.groupby(color_col)):
            series.append({
                'type': 'scatter', 'name': str(grp),
                'data': [[float(r[x_col]), float(r[y_col]), str(r[name_col])] for _, r in gdf.iterrows()],
                'symbolSize': 10, 'itemStyle': {'color': CHART_COLORS[i % len(CHART_COLORS)]}
            })
    else:
        series.append({
            'type': 'scatter', 'name': y_col,
            'data': [[float(r[x_col]), float(r[y_col]), str(r[name_col])] for _, r in df.iterrows()],
            'symbolSize': 10, 'itemStyle': {'color': CHART_COLORS[0]}
        })
    return {
        'tooltip': {**TOOLTIP_STYLE, 'formatter': '{c}'},
        'legend': {'textStyle': {'color': '#e2e8f0'}, 'bottom': 0},
        'xAxis': {'type': 'log' if use_log else 'value', 'name': x_col, 'axisLabel': {'color': '#94a3b8'}},
        'yAxis': {'type': 'value', 'name': y_col, 'axisLabel': {'color': '#94a3b8'}},
        'series': series,
        **ANIMATION
    }


def chart_line(df, date_col, value_col):
    """Area line chart with gradient fill and dataZoom slider."""
    if df is None or df.empty or date_col not in df.columns or value_col not in df.columns:
        return None
    sorted_df = df.sort_values(date_col)
    dates = sorted_df[date_col].astype(str).tolist()
    values = sorted_df[value_col].tolist()
    return {
        'tooltip': {**TOOLTIP_STYLE, 'trigger': 'axis'},
        'xAxis': {'type': 'category', 'data': dates, 'axisLabel': {'color': '#94a3b8'}},
        'yAxis': {'type': 'value', 'axisLabel': {'color': '#94a3b8'}},
        'dataZoom': [{'type': 'slider', 'start': 0, 'end': 100, 'height': 20, 'bottom': 5}],
        'grid': {'bottom': '15%'},
        'series': [{
            'type': 'line', 'data': values, 'smooth': True, 'symbol': 'none',
            'lineStyle': {'width': 2, 'color': '#60a5fa'},
            'areaStyle': {'color': {'type': 'linear', 'x': 0, 'y': 0, 'x2': 0, 'y2': 1,
                'colorStops': [{'offset': 0, 'color': 'rgba(96,165,250,0.4)'}, {'offset': 1, 'color': 'rgba(96,165,250,0.02)'}]}}
        }],
        **ANIMATION
    }


def chart_boxplot(df, category_col, value_col):
    """Box plot with quartile computation per category."""
    if df is None or df.empty or category_col not in df.columns or value_col not in df.columns:
        return None
    groups = df.groupby(category_col)[value_col]
    categories, box_data = [], []
    for name, vals in groups:
        v = vals.dropna().sort_values()
        if len(v) < 5:
            continue
        q1, q2, q3 = float(np.percentile(v, 25)), float(np.percentile(v, 50)), float(np.percentile(v, 75))
        box_data.append([float(v.min()), q1, q2, q3, float(v.max())])
        categories.append(str(name)[:15])
    if not categories:
        return None
    return {
        'tooltip': {**TOOLTIP_STYLE, 'trigger': 'item'},
        'xAxis': {'type': 'category', 'data': categories, 'axisLabel': {'color': '#94a3b8'}},
        'yAxis': {'type': 'value', 'axisLabel': {'color': '#94a3b8'}},
        'series': [{'type': 'boxplot', 'data': box_data,
                    'itemStyle': {'color': '#1e293b', 'borderColor': '#60a5fa', 'borderWidth': 2}}],
        **ANIMATION
    }


def chart_treemap(df, category_col, value_col):
    """Treemap aggregated by category."""
    if df is None or df.empty or category_col not in df.columns or value_col not in df.columns:
        return None
    agg = df.groupby(category_col)[value_col].sum().reset_index()
    agg = agg[agg[value_col] > 0].sort_values(value_col, ascending=False)
    if agg.empty:
        return None
    children = [{'name': str(row[category_col]), 'value': float(row[value_col]),
                 'itemStyle': {'color': CHART_COLORS[i % len(CHART_COLORS)]}}
                for i, (_, row) in enumerate(agg.iterrows())]
    return {
        'tooltip': {**TOOLTIP_STYLE},
        'series': [{'type': 'treemap', 'data': children, 'roam': False,
                    'label': {'show': True, 'color': '#f1f5f9', 'fontSize': 12},
                    'breadcrumb': {'show': False},
                    'levels': [{'itemStyle': {'borderColor': '#0f172a', 'borderWidth': 2, 'gapWidth': 2}}]}],
        **ANIMATION
    }


def chart_donut(df, category_col, value_col=None):
    """Donut chart with 50% inner radius, outside labels, vertical legend."""
    if df is None or df.empty or category_col not in df.columns:
        return None
    if value_col and value_col in df.columns:
        agg = df.groupby(category_col)[value_col].sum().reset_index()
        data = [{'name': str(row[category_col]), 'value': float(row[value_col])} for _, row in agg.iterrows()]
    else:
        counts = df[category_col].value_counts()
        data = [{'name': str(k), 'value': int(v)} for k, v in counts.items()]
    if not data:
        return None
    return {
        'tooltip': {**TOOLTIP_STYLE, 'trigger': 'item', 'formatter': '{b}: {c} ({d}%)'},
        'legend': {'orient': 'vertical', 'right': 10, 'top': 'center', 'textStyle': {'color': '#e2e8f0'}},
        'color': CHART_COLORS,
        'series': [{'type': 'pie', 'radius': ['50%', '75%'], 'center': ['40%', '50%'], 'data': data,
                    'label': {'show': True, 'formatter': '{b} {d}%', 'color': '#94a3b8'},
                    'emphasis': {'itemStyle': {'shadowBlur': 10, 'shadowColor': 'rgba(0,0,0,0.5)'}}}],
        **ANIMATION
    }


def chart_stacked_bar(df, category_col, sub_col, value_col):
    """Stacked bar chart from pivot matrix."""
    if df is None or df.empty:
        return None
    for c in [category_col, sub_col, value_col]:
        if c not in df.columns:
            return None
    pivot = df.pivot_table(index=category_col, columns=sub_col, values=value_col, aggfunc='sum', fill_value=0)
    categories = [str(c) for c in pivot.index.tolist()]
    series = []
    for i, col in enumerate(pivot.columns):
        series.append({
            'name': str(col), 'type': 'bar', 'stack': 'total',
            'data': pivot[col].tolist(), 'barMaxWidth': 40,
            'itemStyle': {'color': CHART_COLORS[i % len(CHART_COLORS)]}
        })
    return {
        'tooltip': {**TOOLTIP_STYLE, 'trigger': 'axis', 'axisPointer': {'type': 'shadow'}},
        'legend': {'textStyle': {'color': '#e2e8f0'}, 'bottom': 0},
        'grid': {'left': '3%', 'right': '4%', 'bottom': '12%', 'containLabel': True},
        'xAxis': {'type': 'category', 'data': categories, 'axisLabel': {'color': '#94a3b8', 'rotate': 30}},
        'yAxis': {'type': 'value', 'axisLabel': {'color': '#94a3b8'}},
        'series': series,
        **ANIMATION
    }
```
