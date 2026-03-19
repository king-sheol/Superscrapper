# Superscraper v5 — Test Findings & Fixes

> Based on v4 test run: CRM системы для малого бизнеса 2026 (54 records, 7 sources)

## Test Results Summary

**What worked:** Phase 0-6 flow, parallel agents, _state/ persistence, CRITICAL RULES 1-3 & 6, Firecrawl CLI, Russian language, data quality reviewer, report reviewer.

**What broke:** 8 problems found, 4 critical.

---

## Problems Found

### CRITICAL

#### C1: Streamlit table shows raw HTML tags (`<span st...`)

**Symptom:** Every badge column (Бесплатный тариф, Русский интерфейс, Мобильное, Аудитория, Источник) displays `<span st...` instead of rendered badges.

**Root cause:** `dashboard-streamlit-kit.md` uses HTML badge markup in AG Grid JsCode renderer, but the generated `dashboard.py` uses `st.dataframe()` which does NOT render HTML. The kit file contains the code, but the designer agent didn't use AG Grid — it fell back to st.dataframe.

**Fix:** In `dashboard-streamlit-kit.md`:
- Section "AG Grid config" must be MANDATORY, not optional
- Add explicit rule: "NEVER use st.dataframe for the main table. ALWAYS use AgGrid from streamlit-aggrid."
- Add fallback with try/except at module level:
```python
try:
    from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode
    HAS_AGGRID = True
except ImportError:
    HAS_AGGRID = False
```
All table functions check `HAS_AGGRID` flag. If False → use st.dataframe with plain text (no HTML tags, no badge markup). This prevents crash on import failure.

#### C2: Too many columns visible (14 in one table)

**Symptom:** All columns crammed into table width. Headers truncated ("Беспла...", "Рейтин...", "Аудито..."). Values unreadable.

**Root cause:** Designer agent included all 14 columns. No rule limits visible columns.

**Fix:** In `design-rules.md` add:
```
### Column Priority (automatic)
1. Name column — ALWAYS pinned left
2. First numeric column (from decision table KPI #1)
3. Second numeric column
4. First categorical column (badges)
5. Second categorical column
6-8. Additional if screen width allows
9+. HIDDEN — show only in detail panel

Max visible columns: 8. Everything else → detail panel.
Long text columns (avg >50 chars): ALWAYS hidden.
```

#### C3: No detail panel in Streamlit

**Symptom:** No way to see full CRM info. Hidden columns are just gone.

**Root cause:** `dashboard-streamlit-kit.md` has `st.expander` code but designer didn't include it.

**Fix:** In `dashboard-streamlit-kit.md`:
- Make detail panel MANDATORY in assembly checklist
- Pattern: AG Grid row selection → st.session_state → st.expander below table showing ALL fields including hidden columns

#### C4: SSH deploy requires manual password entry

**Symptom:** User had to manually run scp/ssh in PowerShell, enter password each time.

**Root cause:** No SSH key setup in onboarding. Windows doesn't have sshpass or ssh-copy-id.

**Fix:**
- Move VPS configuration from Phase 0 to Phase 5e (deploy time, not onboarding)
- Store VPS credentials in `~/.claude/superscraper.local.md` (YAML frontmatter)
- On first Streamlit deploy: ask IP + user, generate SSH key, show user one PowerShell command to copy pubkey, verify with `ssh -o BatchMode=yes`, save to local.md
- Subsequent deploys: read local.md, deploy automatically

---

### MEDIUM

#### M1: Scatter chart points clustered

**Symptom:** Most points in top-left corner. Log scale helps but many N/A entries.

**Root cause:** Only 23/54 CRM have both price AND rating. Scatter needs both axes populated.

**Fix:** In `design-rules.md` add fallback rules:
```
### Chart Fallback Rules
- Any chart with <5 data points → replace with donut/bar by nearest category
- Scatter with <30% fill rate → show warning "Shown N of M" + suggest alternative
- Radar with <3 numeric columns → replace with horizontal bar
- When falling back, choose the categorical column with highest fill rate
```

#### M2: Python encoding errors on Windows

**Symptom:** ValueError when parsing prices. cp1251 vs utf-8 mismatch.

**Root cause:** Python on Windows defaults to cp1251, not utf-8.

**Fix:** Add CRITICAL RULE #8 to SKILL.md:
```
| 8 | Python open() ALWAYS with encoding='utf-8'. CSV with encoding='utf-8-sig'. No exceptions. |
```
This is a prompt-level fix. All agents generating Python code will follow this rule.

#### M3: Preview server failed on Windows

**Symptom:** `npx ENOENT`, port conflicts when trying to preview dashboard.

**Fix:** Dashboard-auditor uses two-level audit:
1. Code audit (ALWAYS runs): read generated HTML/Python as text, verify design tokens, tooltips, empty states, footer, encoding
2. Visual audit (OPTIONAL): attempt `python -m http.server` + preview tools. If fails — skip, rely on code audit.

Add exception to CRITICAL RULE #3 (preview tools ONLY, NOT Chrome MCP — auditor's own rules prohibit Chrome MCP):
```
| 3 | BANNED: browser tools, WebFetch, WebSearch, Chrome MCP. EXCEPTION: dashboard-auditor may use preview tools (preview_start, preview_screenshot) for visual verification only. Chrome MCP remains banned for all agents. |
```

**Code audit checklist (MANDATORY, always runs):**
- [ ] AG Grid import present (not st.dataframe for main table)
- [ ] `encoding='utf-8'` in all `open()` calls
- [ ] `encoding='utf-8-sig'` in all `read_csv()` calls
- [ ] Design tokens: #0f172a, #1e293b, #334155 present in CSS
- [ ] Tooltip extraCssText with max-width and word-wrap
- [ ] Empty state handlers for all components
- [ ] Footer with metadata
- [ ] BOM strip (`\uFEFF` removal)
- [ ] Max 8 visible columns in table
- [ ] Detail panel/expander present
- [ ] No raw HTML tags in st.dataframe (if fallback used)

#### M4: Art-director not dispatched for COMPLEX data

**Symptom:** 54 records, 13 columns = COMPLEX threshold. But art-director agent not found in cache.

**Root cause:** New agents added in v4 but cache not synced.

**Fix:**
1. `scripts/install-hooks.sh` — creates post-commit git hook that auto-syncs to plugin cache
2. Phase 5c: explicit complexity check with clear dispatch logic and fallback if agent not available

---

## Architecture Changes

### 1. Kit file restructure: каркас + dynamic blocks

Current problem: kit files are 1100 lines. Agent reads beginning, forgets rest.

New structure for each kit:

**`dashboard-streamlit-base.py`** — complete working Streamlit file with:
- All imports
- Custom CSS injection (CANNOT be forgotten — it's in the file)
- Layout structure (sidebar, main, sections)
- Footer
- Utility functions (format_number, etc.)
- Placeholder functions: `render_primary_chart()`, `render_comparison_chart()`
- Default COLUMNS config

This file runs as-is and shows "configure data" state.

**`dashboard-streamlit-charts.md`** — 8 chart function implementations (~200 lines)

**`dashboard-streamlit-assembly.md`** — 30-line instruction:
1. Copy base.py to output dir
2. Edit TITLE, CSV_PATH, COLUMNS (3 string replacements)
3. Replace `render_primary_chart()` body with a CALL to the chosen chart function from charts.md. Example:
   ```python
   def render_primary_chart(df, filtered):
       chart_horizontal_bar(filtered, COLUMNS["name"], COLUMNS["numeric"][0])
   ```
4. Replace `render_comparison_chart()` body the same way
5. Copy the needed chart function implementations from charts.md into the file (above the render_ functions)
6. Done

**Chart function mapping (decision table → function name):**
- Rating → `chart_horizontal_bar` (primary) + `chart_radar` (comparison)
- Prices → `chart_scatter` (primary) + `chart_boxplot` (comparison)
- Time series → `chart_line` (primary) + `chart_stacked_bar` (comparison)
- Segment → `chart_treemap` (primary) + `chart_stacked_bar` (comparison)
- Fallback → `chart_horizontal_bar` (primary) + `chart_donut` (comparison)

Same pattern for HTML: `dashboard-html-base.html` + `dashboard-html-charts.md` + `dashboard-html-assembly.md`

**IMPORTANT: HTML has the same problem as Streamlit.** Visual audit confirmed: generated HTML uses plain `<table>` instead of AG Grid, despite AG Grid being in the kit. Agent ignored kit components and wrote simpler code. The base.html approach fixes this — AG Grid initialization, CDN imports, dark theme config, all CSS, sidebar, detail panel, footer are baked into base.html. Agent only replaces data and chart functions.

**`dashboard-html-base.html`** must contain:
- All CDN imports (ECharts, AG Grid, Tailwind, Lucide)
- Complete CSS (glassmorphism, badges, detail panel, responsive, skeleton, range sliders)
- HTML structure (header, KPI grid, sidebar, chart containers, AG Grid container, detail panel, footer)
- All utility JS (formatNumber, formatDate, renderLoadingSkeleton, renderEmptyState, renderErrorState, renderFooter)
- AG Grid initialization with dark theme (NOT a plain table)
- Filter system (initFilters, initRangeSliders, applyFilters, resetFilters)
- Detail panel (showDetailPanel, closeDetailPanel)
- Placeholder: `const COLUMNS = {}` and `const allData = []` and `function renderPrimaryChart(){}` and `function renderComparisonChart(){}`

Agent edits: COLUMNS, allData, renderPrimaryChart body, renderComparisonChart body. Everything else untouched.

Key insight: agent edits 4 values in a working file, instead of writing 1000+ lines from scratch. CSS, AG Grid, filters, detail panel cannot be forgotten because they're in the base file.

**Problem with .py base file:** `{{TITLE}}` placeholders are invalid Python.

**Solution:** Use real Python defaults:
```python
# === CUSTOMIZE BELOW ===
TITLE = "Dashboard"           # designer replaces
CSV_PATH = "data.csv"         # designer replaces
COLUMNS = {"name": "name", "numeric": [], "categories": []}  # designer replaces
```
Designer uses Edit tool to replace these 3 lines. Rest of file untouched.

### 2. Design rules additions

Add to `design-rules.md`:
- Column priority algorithm (auto, not hardcoded)
- Chart fallback rules (fill rate < 30%)
- Max visible columns: 8
- CRITICAL RULE #8: Python encoding

### 3. VPS onboarding moved to Phase 5e

- Phase 0: only Firecrawl + Python
- Phase 5e: VPS setup on first Streamlit deploy
- Credentials stored in `~/.claude/superscraper.local.md` (replaces `~/.superscrape-servers.json` which is DEPRECATED and should be removed if found)

### 4. Firecrawl credit budget

Phase 0: record available credits via `firecrawl --status`
Phase 3: distribute evenly across sources. Max 5 requests per source (already in scraper.md). Budget logic:
- If credits = 0 → STOP, tell user "No Firecrawl credits. Run `firecrawl --status` to check."
- If credits < source_count → STOP, tell user "Not enough credits (N) for M sources. Reduce sources or add credits."
- If credits < source_count × 5 → reduce per-source limit: `floor(credits / source_count)`, warn user
- Otherwise → 5 per source

### 5. Progress reporting

Phase 3: after each scraper agent completes, print "N/M sources collected" to chat.
Rate limit: explicit message "Rate limit reached. Data saved to _state/. Say 'continue' when ready."

### 6. Cross-validation

Phase 4: if same entity found in 2+ sources, compare numeric values:
- 3+ sources with same entity: divergence >30% → flag as "conflicting data"
- 2 sources with same entity: divergence >50% → flag as "conflicting data"
- If fewer than 2 sources have overlapping entities → skip cross-validation, note in output: "Cross-validation not possible: insufficient source overlap"

### 7. Post-commit cache sync hook

`scripts/install-hooks.sh`:
```bash
#!/bin/bash
HOOK=".git/hooks/post-commit"
cat > "$HOOK" << 'EOF'
#!/bin/bash
CACHE_DIR="$HOME/.claude/plugins/cache/king-sheol/superscraper/1.0.0"
if [ -d "$CACHE_DIR" ]; then
    cp -r skills agents commands hooks .claude-plugin "$CACHE_DIR/" 2>/dev/null
    echo "✓ Plugin cache synced"
fi
EOF
chmod +x "$HOOK"
echo "Post-commit hook installed"
```

---

## Files to Change

| File | Change |
|------|--------|
| `skills/superscrape/SKILL.md` | Add CRITICAL RULE #8 (encoding) |
| `skills/superscrape/phases/phase-0-onboarding.md` | Remove VPS setup, add Firecrawl credit budget |
| `skills/superscrape/phases/phase-3-collect.md` | Add progress reporting, rate limit message |
| `skills/superscrape/phases/phase-4-normalize.md` | Add cross-validation rule |
| `skills/superscrape/phases/phase-5c-dashboard-generate.md` | Explicit complexity check, art-director dispatch with fallback |
| `skills/superscrape/phases/phase-5e-deploy.md` | VPS onboarding with SSH key, local.md storage |
| `skills/superscrape/references/design-rules.md` | Column priority, chart fallback, max 8 visible columns |
| `skills/superscrape/references/dashboard-streamlit-kit.md` | REWRITE: split into base.py + charts.md + assembly.md |
| `skills/superscrape/references/dashboard-html-kit.md` | REWRITE: split into base.html + charts.md + assembly.md |
| `agents/dashboard-auditor.md` | Two-level audit (code + optional visual), RULE #3 exception |
| `scripts/install-hooks.sh` | NEW: post-commit cache sync |
| `.claude/superscraper.local.md` | NEW: template for VPS/GitHub credentials |

---

## Verification

After implementation, re-run CRM test:

**Base file smoke test (BEFORE full pipeline):**
0a. Run `streamlit run dashboard-streamlit-base.py` — verify it starts, shows empty state with dark theme, CSS applied, sidebar visible
0b. Open `dashboard-html-base.html` in browser — verify it loads, shows loading skeleton, dark theme, AG Grid container visible
0c. If either fails — fix base file before proceeding

**Full pipeline test:**

**Dashboard quality:**
1. Check Streamlit table renders badges via AG Grid (no `<span st...`)
2. Check AG Grid fallback: uninstall streamlit-aggrid, verify dashboard loads with st.dataframe (plain text, no crash)
3. Check max 8 columns visible, detail panel/expander shows rest
4. Check scatter fallback if fill rate < 30% — should show donut or warning
5. Check CSS applied (dark theme, glassmorphism KPI cards, custom Streamlit overrides)
6. Check detail panel on initial load shows empty state message (not blank)

**Kit restructure:**
7. Check dashboard.py is generated by editing base.py (CSS/imports survive assembly)
8. Check HTML dashboard.html is generated by editing base.html (same pattern)

**Workflow:**
9. Check progress messages "N/M sources collected" in chat during Phase 3
10. Check rate limit message with save confirmation
11. Check encoding — verify all `open()` have `encoding='utf-8'`, all `read_csv()` have `encoding='utf-8-sig'`

**Deploy:**
12. Check VPS deploy without manual password (after SSH key setup)

**Data quality:**
13. Check cross-validation flags in normalized.json for entities in 2+ sources
14. Check Firecrawl credit budget — no source exceeds allocation

**Infrastructure:**
15. Check `scripts/install-hooks.sh` creates working post-commit hook
16. Check post-commit hook syncs cache after commit
17. Redeploy Streamlit to VPS (46.149.79.21:8501) with fixed dashboard
18. Verify new agents (dashboard-art-director, dashboard-designer) are discoverable after session restart
