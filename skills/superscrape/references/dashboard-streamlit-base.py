"""
Superscraper Streamlit Dashboard — Base Template v5
====================================================
A complete, standalone Streamlit dashboard with AG Grid, glassmorphism CSS,
detail panel, KPI cards, and chart placeholders. Runs with:
    streamlit run dashboard-streamlit-base.py

Designer agents replace only TITLE, CSV_PATH, COLUMNS, and chart functions.
"""

import streamlit as st
import pandas as pd
import re
import os
from datetime import datetime

# ---------------------------------------------------------------------------
# Optional dependency imports
# ---------------------------------------------------------------------------
try:
    from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode
    HAS_AGGRID = True
except ImportError:
    HAS_AGGRID = False

try:
    from streamlit_echarts import st_echarts
    HAS_ECHARTS = True
except ImportError:
    HAS_ECHARTS = False

# ---------------------------------------------------------------------------
# === CUSTOMIZE BELOW ===
TITLE = "Dashboard"
CSV_PATH = "data.csv"
COLUMNS = {"name": "Название", "numeric": ["Рейтинг"], "categories": ["Бесплатный тариф"], "hidden": ["Ключевые функции", "Интеграции"]}
# ---------------------------------------------------------------------------

# Design tokens
TOKEN_BG = "#0f172a"
TOKEN_SURFACE = "#1e293b"
TOKEN_BORDER = "#334155"
TOKEN_TEXT = "#f1f5f9"
TOKEN_TEXT_SEC = "#94a3b8"
TOKEN_TEXT_MUTED = "#64748b"
TOKEN_ACCENT = "#60a5fa"
CHART_PALETTE = ['#60a5fa', '#34d399', '#fbbf24', '#f87171', '#a78bfa', '#22d3ee', '#fb923c', '#e879f9']

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(page_title=TITLE, layout="wide", initial_sidebar_state="expanded")

# ---------------------------------------------------------------------------
# CSS injection
# ---------------------------------------------------------------------------
CUSTOM_CSS = f"""
<style>
/* ---- Page & sidebar background ---- */
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
    background-color: {TOKEN_BG} !important;
}}
section[data-testid="stSidebar"] {{
    background-color: {TOKEN_BG} !important;
    min-width: 280px !important;
}}
section[data-testid="stSidebar"] > div {{
    background-color: {TOKEN_BG} !important;
}}

/* ---- Hide Streamlit branding ---- */
#MainMenu {{visibility: hidden !important;}}
footer {{visibility: hidden !important;}}
header {{visibility: hidden !important;}}

/* ---- KPI metric cards — glassmorphism ---- */
[data-testid="stMetric"] {{
    background: rgba(30, 41, 59, 0.6);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(96, 165, 250, 0.15);
    border-radius: 12px;
    padding: 1rem 1.25rem;
    transition: box-shadow 0.25s ease;
}}
[data-testid="stMetric"]:hover {{
    box-shadow: 0 0 20px rgba(96, 165, 250, 0.15);
}}
[data-testid="stMetric"] [data-testid="stMetricValue"] {{
    font-size: 2rem !important;
    color: white !important;
}}
[data-testid="stMetric"] [data-testid="stMetricLabel"] {{
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    color: {TOKEN_TEXT_SEC} !important;
    letter-spacing: 0.05em;
}}

/* ---- General text ---- */
h1, h2, h3, h4, p, span, label, .stMarkdown {{
    color: {TOKEN_TEXT} !important;
}}

/* ---- Dividers ---- */
hr {{
    border-color: {TOKEN_BORDER} !important;
}}

/* ---- Inputs — dark bg, blue focus ---- */
input, textarea, select,
[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] div[data-baseweb="select"],
.stSlider {{
    background-color: {TOKEN_SURFACE} !important;
    color: {TOKEN_TEXT} !important;
    border-color: {TOKEN_BORDER} !important;
}}
input:focus, textarea:focus, select:focus {{
    box-shadow: 0 0 0 2px {TOKEN_ACCENT} !important;
    border-color: {TOKEN_ACCENT} !important;
}}

/* ---- Section spacing ---- */
.block-container {{
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
}}
[data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"] {{
    padding: 0.5rem 0;
}}

/* ---- Expander (detail panel) ---- */
details {{
    background-color: {TOKEN_SURFACE} !important;
    border: 1px solid {TOKEN_BORDER} !important;
    border-radius: 8px !important;
}}
details summary {{
    color: {TOKEN_TEXT} !important;
}}

/* ---- Buttons ---- */
.stButton > button {{
    background-color: {TOKEN_SURFACE} !important;
    color: {TOKEN_TEXT} !important;
    border: 1px solid {TOKEN_BORDER} !important;
    border-radius: 8px !important;
}}
.stButton > button:hover {{
    border-color: {TOKEN_ACCENT} !important;
    box-shadow: 0 0 10px rgba(96, 165, 250, 0.2);
}}

/* ---- Caption / footer ---- */
.stCaption, [data-testid="stCaptionContainer"] {{
    color: {TOKEN_TEXT_MUTED} !important;
}}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Data loading with BOM strip
# ---------------------------------------------------------------------------
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    """Load CSV with BOM-safe encoding and clean column names."""
    df = pd.read_csv(path, encoding="utf-8-sig")
    # Explicit BOM removal from column names
    df.columns = [c.replace("\ufeff", "").strip() for c in df.columns]
    return df


def detect_format(series: pd.Series) -> str:
    """Guess column format from values: rating, currency, percent, or plain."""
    sample = series.dropna().head(20)
    if sample.empty:
        return "plain"
    as_str = sample.astype(str)
    if as_str.str.contains(r"[₽\$€]", regex=True).mean() > 0.3:
        return "currency"
    if as_str.str.contains(r"%", regex=True).mean() > 0.3:
        return "percent"
    try:
        nums = pd.to_numeric(sample, errors="coerce").dropna()
        if len(nums) > 0 and nums.max() <= 5 and nums.min() >= 0:
            return "rating"
    except Exception:
        pass
    return "plain"


def format_kpi(value, fmt: str) -> str:
    """Format a KPI value according to its detected type."""
    if pd.isna(value):
        return "N/A"
    if fmt == "rating":
        return f"{value:.1f} / 5"
    if fmt == "currency":
        return f"{value:,.0f} \u20bd"
    if fmt == "percent":
        return f"{value:.1f}%"
    if isinstance(value, float):
        return f"{value:,.2f}"
    return str(value)


# ---------------------------------------------------------------------------
# Chart placeholders (designer replaces these)
# ---------------------------------------------------------------------------
def render_primary_chart(df, filtered):
    """Primary chart: configure in assembly step."""
    st.info("Primary chart: configure in assembly step")


def render_comparison_chart(df, filtered):
    """Comparison chart: configure in assembly step."""
    st.info("Comparison chart: configure in assembly step")


# ---------------------------------------------------------------------------
# AG Grid badge renderers
# ---------------------------------------------------------------------------
BADGE_JS = JsCode("""
function(params) {
    var val = (params.value == null || params.value === '') ? '' : String(params.value).trim();
    var lower = val.toLowerCase();
    var bg = '#475569'; var text = 'N/A';

    if (lower === 'да' || lower === 'yes' || lower === 'true') {
        bg = '#059669'; text = val;
    } else if (lower === 'нет' || lower === 'no' || lower === 'false') {
        bg = '#dc2626'; text = val;
    } else if (lower === 'триал' || lower === 'частично' || lower === 'trial' || lower === 'partial') {
        bg = '#d97706'; text = val;
    } else if (val !== '') {
        return val;
    }

    return '<span style="background:' + bg + ';color:#fff;padding:2px 10px;border-radius:999px;font-size:0.8em;white-space:nowrap;">' + text + '</span>';
}
""") if HAS_AGGRID else None

CATEGORY_VALUES = {"да", "нет", "yes", "no", "true", "false", "триал", "частично", "trial", "partial", "n/a", ""}


def is_badge_column(series: pd.Series) -> bool:
    """Return True if most non-null values look like badge-able categories."""
    sample = series.dropna().astype(str).str.strip().str.lower().head(50)
    if sample.empty:
        return False
    return sample.isin(CATEGORY_VALUES).mean() > 0.6


# ---------------------------------------------------------------------------
# Main app
# ---------------------------------------------------------------------------
def main():
    # --- Load data ---
    if not os.path.exists(CSV_PATH):
        st.error(f"Файл не найден: `{CSV_PATH}`. Положите CSV рядом с дашбордом.")
        st.stop()

    df = load_data(CSV_PATH)
    if df.empty:
        st.warning("CSV загружен, но данных нет.")
        st.stop()

    all_columns = list(df.columns)
    name_col = COLUMNS.get("name", all_columns[0] if all_columns else "name")
    numeric_cols = [c for c in COLUMNS.get("numeric", []) if c in all_columns]
    category_cols = [c for c in COLUMNS.get("categories", []) if c in all_columns]
    hidden_cols = [c for c in COLUMNS.get("hidden", []) if c in all_columns]

    # Ensure numeric columns are actually numeric
    for nc in numeric_cols:
        df[nc] = pd.to_numeric(df[nc].astype(str).str.replace(r"[^\d.,\-]", "", regex=True).str.replace(",", "."), errors="coerce")

    # --- Title ---
    st.title(TITLE)

    # ===================================================================
    # SIDEBAR FILTERS
    # ===================================================================
    with st.sidebar:
        st.header("Фильтры")

        search = st.text_input("Поиск", placeholder="Введите текст для поиска...")

        category_selections = {}
        for cat in category_cols:
            unique_vals = sorted(df[cat].dropna().astype(str).unique().tolist())
            options = ["Все"] + unique_vals
            category_selections[cat] = st.selectbox(cat, options, index=0)

        slider_ranges = {}
        for nc in numeric_cols:
            col_min = float(df[nc].min()) if df[nc].notna().any() else 0.0
            col_max = float(df[nc].max()) if df[nc].notna().any() else 1.0
            if col_min == col_max:
                col_max = col_min + 1.0
            slider_ranges[nc] = st.slider(
                nc,
                min_value=col_min,
                max_value=col_max,
                value=(col_min, col_max),
            )

        if st.button("Сбросить фильтры"):
            st.rerun()

    # ===================================================================
    # Apply filters
    # ===================================================================
    filtered = df.copy()

    if search:
        mask = filtered.astype(str).apply(lambda row: row.str.contains(search, case=False, na=False).any(), axis=1)
        filtered = filtered[mask]

    for cat, sel in category_selections.items():
        if sel != "Все":
            filtered = filtered[filtered[cat].astype(str) == sel]

    for nc, (lo, hi) in slider_ranges.items():
        filtered = filtered[(filtered[nc] >= lo) & (filtered[nc] <= hi) | filtered[nc].isna()]

    # ===================================================================
    # KPI CARDS
    # ===================================================================
    st.subheader("Ключевые показатели")
    kpi_cols = st.columns(4)

    # KPI 1: total records
    with kpi_cols[0]:
        st.metric(label="Всего записей", value=str(len(filtered)))

    # KPI 2–4: auto-compute from numeric columns
    for i, nc in enumerate(numeric_cols[:3]):
        fmt = detect_format(df[nc])
        avg_val = filtered[nc].mean()
        with kpi_cols[i + 1]:
            st.metric(label=f"Средн. {nc}", value=format_kpi(avg_val, fmt))

    # Fill remaining KPI slots if fewer than 3 numeric cols
    for i in range(len(numeric_cols[:3]) + 1, 4):
        with kpi_cols[i]:
            st.metric(label="—", value="—")

    st.divider()

    # ===================================================================
    # CHARTS
    # ===================================================================
    chart_left, chart_right = st.columns(2)
    with chart_left:
        render_primary_chart(df, filtered)
    with chart_right:
        render_comparison_chart(df, filtered)

    st.divider()

    # ===================================================================
    # AG GRID TABLE (or fallback)
    # ===================================================================
    st.subheader("Данные")

    # Determine visible columns: max 8, rest hidden
    visible_candidates = [c for c in all_columns if c not in hidden_cols]
    visible_cols = visible_candidates[:8]
    overflow_hidden = visible_candidates[8:]

    if HAS_AGGRID:
        gb = GridOptionsBuilder.from_dataframe(filtered[visible_cols])

        # Dark theme overrides
        custom_css = {
            ".ag-root-wrapper": {"background-color": TOKEN_SURFACE},
            ".ag-header": {"background-color": TOKEN_BORDER},
            ".ag-header-cell-label": {"color": TOKEN_TEXT},
            ".ag-row": {"background-color": TOKEN_SURFACE, "color": TOKEN_TEXT},
            ".ag-row-hover": {"background-color": f"{TOKEN_BORDER} !important"},
            ".ag-cell": {"color": TOKEN_TEXT},
        }

        # Apply badge renderer to badge-like columns
        for col in visible_cols:
            if col in category_cols or is_badge_column(df[col]):
                gb.configure_column(col, cellRenderer=BADGE_JS)

        gb.configure_selection(selection_mode="single", use_checkbox=False)
        gb.configure_pagination(paginationAutoPageSize=True)
        gb.configure_default_column(resizable=True, sortable=True, filterable=True)

        grid_options = gb.build()

        grid_response = AgGrid(
            filtered[visible_cols],
            gridOptions=grid_options,
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            allow_unsafe_jscode=True,
            theme="alpine",
            custom_css=custom_css,
            height=450,
        )

        selected_rows = grid_response.get("selected_rows", None)
    else:
        # Fallback: plain st.dataframe — strip any HTML tags from values
        display_df = filtered[visible_cols].copy()
        for col in display_df.columns:
            if display_df[col].dtype == object:
                display_df[col] = display_df[col].astype(str).apply(
                    lambda v: re.sub(r"<[^>]+>", "", v) if isinstance(v, str) else v
                )
        st.dataframe(display_df, use_container_width=True, height=450)
        selected_rows = None

    st.divider()

    # ===================================================================
    # DETAIL PANEL
    # ===================================================================
    st.subheader("Детали")

    selected_row = None
    if HAS_AGGRID and selected_rows is not None:
        if isinstance(selected_rows, pd.DataFrame) and not selected_rows.empty:
            selected_row = selected_rows.iloc[0]
        elif isinstance(selected_rows, list) and len(selected_rows) > 0:
            selected_row = pd.Series(selected_rows[0])

    if selected_row is not None:
        row_label = str(selected_row.get(name_col, "Запись"))
        with st.expander(f"Подробности: {row_label}", expanded=True):
            # Find the full row from original df (including hidden cols)
            if name_col in filtered.columns:
                match = filtered[filtered[name_col].astype(str) == str(selected_row.get(name_col, ""))]
            else:
                match = pd.DataFrame()

            if not match.empty:
                full_row = match.iloc[0]
            else:
                full_row = selected_row

            # Show ALL fields including hidden columns
            detail_cols = st.columns(2)
            items = list(full_row.items()) if isinstance(full_row, pd.Series) else []
            # Add hidden columns that may not be in selected_row
            if not match.empty:
                for hc in hidden_cols:
                    if hc in match.columns and hc not in [it[0] for it in items]:
                        items.append((hc, match.iloc[0][hc]))

            for idx, (key, val) in enumerate(items):
                with detail_cols[idx % 2]:
                    display_val = str(val) if not pd.isna(val) else "N/A"
                    # Strip any HTML tags for clean display
                    display_val = re.sub(r"<[^>]+>", "", display_val)
                    st.markdown(
                        f"<div style='margin-bottom:0.5rem;'>"
                        f"<span style='color:{TOKEN_TEXT_SEC};font-size:0.75rem;text-transform:uppercase;'>{key}</span><br/>"
                        f"<span style='color:{TOKEN_TEXT};font-size:1rem;'>{display_val}</span>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
    else:
        st.info("Выберите строку в таблице для просмотра деталей")

    st.divider()

    # ===================================================================
    # FOOTER
    # ===================================================================
    footer_parts = []
    footer_parts.append(f"Записей: {len(filtered)} из {len(df)}")
    footer_parts.append(f"Дата: {datetime.now().strftime('%d.%m.%Y')}")
    footer_parts.append(f"Источник: {os.path.basename(CSV_PATH)}")
    footer_parts.append("Сгенерировано Superscraper")
    st.caption(" | ".join(footer_parts))


if __name__ == "__main__":
    main()
