# Superscraper v5 Test Fixes Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix 8 bugs found in v4 test run, restructure kit files into base+charts+assembly pattern so agents can't forget components.

**Architecture:** Split monolithic kit files (1100 lines each) into working base templates + chart blocks + assembly instructions. Agent edits 4 values in a working file instead of writing 1000+ lines from scratch. CSS, AG Grid, filters, detail panel baked into base — impossible to forget.

**Tech Stack:** Streamlit + streamlit-echarts + streamlit-aggrid, HTML + ECharts + AG Grid + Tailwind, Firecrawl CLI, Python 3.14

**Spec:** `docs/superpowers/specs/2026-03-19-superscraper-v5-test-fixes.md`

---

## Chunk 1: Base Files (highest impact — fixes C1, C2, C3 + HTML table problem)

### Task 1: Create Streamlit base file

**Files:**
- Create: `skills/superscrape/references/dashboard-streamlit-base.py`
- Delete: `skills/superscrape/references/dashboard-streamlit-kit.md` (after tasks 1-3)

- [ ] **Step 1: Write dashboard-streamlit-base.py**

Complete working Streamlit dashboard with:
- try/except AG Grid import with HAS_AGGRID flag
- Custom CSS injection (dark theme #0f172a, glassmorphism KPI cards, hidden Streamlit branding)
- BOM strip on CSV load
- 4 auto-computed KPI metrics with st.metric
- Sidebar filters (selectbox + slider)
- AG Grid table with dark theme, badge JsCode renderers, max 8 visible columns
- st.dataframe fallback if HAS_AGGRID is False (plain text, no HTML)
- st.expander detail panel below table
- st.divider() between sections
- Footer via st.caption()
- Placeholder functions: render_primary_chart(df, filtered), render_comparison_chart(df, filtered)
- Default config: TITLE = "Dashboard", CSV_PATH = "data.csv", COLUMNS = {...}
- ALL with encoding='utf-8' / 'utf-8-sig'

File must run standalone with `streamlit run dashboard-streamlit-base.py` and show empty/default state.

- [ ] **Step 2: Smoke test base.py**

Run: `cd skills/superscrape/references && streamlit run dashboard-streamlit-base.py --server.headless true`
Expected: Server starts on port 8501 without errors. Page loads with dark theme, sidebar visible, "No data" state shown.

- [ ] **Step 3: Test with real data**

Copy data.csv from `output/2026-03-19-crm-small-business-2026/data.csv` to references dir.
Edit CSV_PATH in base.py to point to it.
Run: `streamlit run dashboard-streamlit-base.py`
Expected: KPI cards show numbers, AG Grid table renders with badges (no `<span st...`), max 8 columns visible, detail expander works.

- [ ] **Step 4: Commit**

```bash
git add skills/superscrape/references/dashboard-streamlit-base.py
git commit -m "feat: create Streamlit base template with AG Grid, CSS, detail panel baked in"
```

---

### Task 2: Create HTML base file

**Files:**
- Create: `skills/superscrape/references/dashboard-html-base.html`
- Delete: `skills/superscrape/references/dashboard-html-kit.md` (after tasks 1-3)

- [ ] **Step 1: Write dashboard-html-base.html**

Complete working HTML dashboard with:
- CDN imports: ECharts 5, AG Grid 31, Tailwind CSS, Lucide Icons
- Full CSS: design tokens as CSS variables, glassmorphism, badges (yes/no/partial/N/A), rating stars, progress bars, trend indicators, loading skeleton, empty/error states, detail panel, range sliders, footer, responsive sidebar
- HTML structure: header, KPI grid, sidebar (search + dropdown filters + range sliders + reset), main (primary chart + comparison chart + AG Grid table), detail panel, footer
- All utility JS: formatNumber, formatNumberText, formatDate, renderLoadingSkeleton, renderEmptyState, renderErrorState, renderFooter
- Common chart setup: CHART_COLORS, initChart, TOOLTIP_STYLE, AXIS_STYLE, resize handler
- renderKPIs with countUp animation and trend indicators
- renderTable with AG Grid: dark theme, badge renderer, rating stars, currency formatter, N/A badges, max 8 visible columns, row click → detail panel
- initFilters, initRangeSliders, applyFilters, resetFilters, toggleSidebar
- showDetailPanel (slide-in right), closeDetailPanel, Esc handler
- Placeholder: `const COLUMNS = {}`, `const allData = []`, `function renderPrimaryChart(){}`, `function renderComparisonChart(){}`
- Init: renderLoadingSkeleton → setTimeout → initFilters + initRangeSliders + applyFilters + renderFooter + lucide.createIcons

File opens in browser and shows loading skeleton → empty state.

- [ ] **Step 2: Smoke test base.html**

Open `dashboard-html-base.html` directly in browser (file:// protocol).
Expected: Dark theme, loading skeleton appears briefly, then empty state. No JS errors in console. AG Grid container visible (empty).

- [ ] **Step 3: Test with real data**

Edit base.html: replace `const allData = []` with JSON data from output/2026-03-19.../data.csv (use python to convert CSV→JSON).
Replace `const COLUMNS = {}` with actual column classification.
Open in browser.
Expected: KPI cards with countUp, bar chart with gradient, AG Grid table with badges and sorting, filters work, detail panel slides in on row click.

- [ ] **Step 4: Commit**

```bash
git add skills/superscrape/references/dashboard-html-base.html
git commit -m "feat: create HTML base template with AG Grid, ECharts, full design system baked in"
```

---

### Task 3: Create charts.md and assembly.md files

**Files:**
- Create: `skills/superscrape/references/dashboard-streamlit-charts.md`
- Create: `skills/superscrape/references/dashboard-streamlit-assembly.md`
- Create: `skills/superscrape/references/dashboard-html-charts.md`
- Create: `skills/superscrape/references/dashboard-html-assembly.md`
- Delete: `skills/superscrape/references/dashboard-streamlit-kit.md`
- Delete: `skills/superscrape/references/dashboard-html-kit.md`

- [ ] **Step 1: Write dashboard-streamlit-charts.md**

8 ECharts chart functions for Streamlit (using streamlit-echarts):
- chart_horizontal_bar(df, name_col, value_col)
- chart_radar(df, name_col, numeric_cols)
- chart_scatter(df, x_col, y_col, name_col, color_col)
- chart_line(df, date_col, value_col)
- chart_boxplot(df, category_col, value_col)
- chart_treemap(df, category_col, value_col)
- chart_donut(df, category_col, value_col)
- chart_stacked_bar(df, category_col, sub_col, value_col)

Each function: receives DataFrame + column names, returns ECharts option dict, uses canonical palette + TOOLTIP_STYLE.

~200 lines total.

- [ ] **Step 2: Write dashboard-streamlit-assembly.md**

30-line instruction for dashboard-designer agent:
1. Copy `dashboard-streamlit-base.py` to output dir as `dashboard.py`
2. Edit TITLE, CSV_PATH, COLUMNS (3 line replacements)
3. Read `dashboard-streamlit-charts.md`, copy needed chart functions
4. Replace render_primary_chart() body with call to chosen chart function
5. Replace render_comparison_chart() body with call to chosen chart function
6. Add `requirements.txt`, `.streamlit/config.toml`, `Dockerfile`, `docker-compose.yml`

Include chart function mapping table (decision table → function name).

- [ ] **Step 3: Write dashboard-html-charts.md**

8 ECharts chart functions for HTML (vanilla JS):
Same function signatures as Streamlit but output ECharts setOption configs.
Each uses initChart(), CHART_COLORS, TOOLTIP_STYLE, AXIS_STYLE.
Include empty state guard, click handler for chart→filter.

~250 lines total.

- [ ] **Step 4: Write dashboard-html-assembly.md**

30-line instruction for dashboard-designer agent:
1. Copy `dashboard-html-base.html` to output dir as `dashboard.html`
2. Edit: replace `const allData = []` with JSON data
3. Edit: replace `const COLUMNS = {}` with column classification
4. Read `dashboard-html-charts.md`, copy needed chart functions into script block
5. Replace renderPrimaryChart() body with call to chosen chart function
6. Replace renderComparisonChart() body with call to chosen chart function

Include chart function mapping table.

- [ ] **Step 5: Commit charts + assembly files (do NOT delete old kits yet — Task 6 needs to update references first)**

```bash
git add skills/superscrape/references/dashboard-streamlit-charts.md skills/superscrape/references/dashboard-streamlit-assembly.md skills/superscrape/references/dashboard-html-charts.md skills/superscrape/references/dashboard-html-assembly.md
git commit -m "feat: add charts + assembly files for base template pattern"
```

---

## Chunk 2: Design Rules & Agent Updates (fixes M1, C2 column priority)

### Task 4: Update design-rules.md

**Files:**
- Modify: `skills/superscrape/references/design-rules.md`

- [ ] **Step 1: Add column priority section**

After current section 5, add:
```markdown
## 6. Column Priority (automatic)

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

- [ ] **Step 2: Add chart fallback rules**

```markdown
## 7. Chart Fallback Rules

- Any chart with <5 data points → replace with donut/bar by nearest category
- Scatter with <30% fill rate → show warning "Shown N of M" + suggest alternative
- Radar with <3 numeric columns → replace with horizontal bar
- When falling back, choose the categorical column with highest fill rate
```

- [ ] **Step 3: Commit**

```bash
git add skills/superscrape/references/design-rules.md
git commit -m "feat: add column priority and chart fallback rules to design-rules"
```

---

### Task 5: Update dashboard-auditor.md

**Files:**
- Modify: `agents/dashboard-auditor.md`

- [ ] **Step 1: Add two-level audit**

Replace current audit process with:
- Level 1: Code audit (MANDATORY) — 11-item checklist from spec
- Level 2: Visual audit (OPTIONAL) — attempt preview tools, skip if unavailable

- [ ] **Step 2: Add code audit checklist**

The 11 items from spec section M3.

- [ ] **Step 3: Commit**

```bash
git add agents/dashboard-auditor.md
git commit -m "feat: add two-level audit (code mandatory + visual optional)"
```

---

### Task 6: Update dashboard-designer.md + delete old kits

**Files:**
- Modify: `agents/dashboard-designer.md`
- Delete: `skills/superscrape/references/dashboard-streamlit-kit.md`
- Delete: `skills/superscrape/references/dashboard-html-kit.md`

- [ ] **Step 1: Update file references in dashboard-designer.md**

Find the section that says "Read design-rules.md for WHAT. Read kit file for HOW." and replace with:

```markdown
## Workflow

1. Read `design-rules.md` → decide WHAT to build (data type, chart types, column priority)
2. Read the appropriate assembly file → follow steps to build:
   - For Streamlit: `dashboard-streamlit-assembly.md`
   - For HTML: `dashboard-html-assembly.md`
3. The assembly file tells you to copy a base template and edit 3-4 values.
   DO NOT write dashboard code from scratch. ALWAYS start from the base template.
```

- [ ] **Step 2: Find and replace all remaining kit references**

Search `agents/dashboard-designer.md` for:
- `dashboard-streamlit-kit.md` → replace with `dashboard-streamlit-assembly.md`
- `dashboard-html-kit.md` → replace with `dashboard-html-assembly.md`

Also update `skills/superscrape-dashboard/SKILL.md` if it references old kit files.

- [ ] **Step 3: Add preview tools permission to dashboard-auditor.md**

In `agents/dashboard-auditor.md`, find the tools section and add:
```
Preview tools (preview_start, preview_screenshot) are PERMITTED for visual verification.
Chrome MCP remains FORBIDDEN.
```

- [ ] **Step 4: Delete old kit files (safe now — all references updated)**

```bash
git rm skills/superscrape/references/dashboard-streamlit-kit.md
git rm skills/superscrape/references/dashboard-html-kit.md
```

- [ ] **Step 5: Commit**

```bash
git add agents/dashboard-designer.md agents/dashboard-auditor.md skills/
git commit -m "refactor: update designer+auditor to base+assembly pattern, delete old kits"
```

---

## Chunk 3: Phase File Updates (fixes M2, C4, M4 + credit budget + progress)

### Task 7: Update SKILL.md — add CRITICAL RULE #8

**Files:**
- Modify: `skills/superscrape/SKILL.md`

- [ ] **Step 1: Add encoding rule**

Add row to CRITICAL RULES table:
```
| 8 | Python open() ALWAYS with encoding='utf-8'. CSV with encoding='utf-8-sig'. No exceptions. |
```

- [ ] **Step 2: Update RULE #3 with auditor exception**

```
| 3 | FORBIDDEN: browser tools, WebFetch, WebSearch, Chrome MCP. EXCEPTION: dashboard-auditor may use preview tools (preview_start, preview_screenshot) for visual verification only. |
```

- [ ] **Step 3: Commit**

```bash
git add skills/superscrape/SKILL.md
git commit -m "feat: add CRITICAL RULE #8 (encoding) and auditor preview exception"
```

---

### Task 8: Update phase-0-onboarding.md

**Files:**
- Modify: `skills/superscrape/phases/phase-0-onboarding.md`

- [ ] **Step 1: Remove VPS setup (moves to phase-5e)**

Remove any VPS/SSH setup from phase-0. Keep only Firecrawl + Python checks.

- [ ] **Step 2: Add Firecrawl credit budget recording**

After firecrawl --status check, parse the output to extract credits:
```
Run: firecrawl --status 2>&1
Parse output for line matching "credits" or "remaining" — extract the number.
Example output: "● Authenticated via stored credentials (525 credits remaining)"
Extract: 525

Save to _state/firecrawl_credits.json:
{"initial_credits": 525, "timestamp": "2026-03-19T..."}

If credits cannot be parsed → save {"initial_credits": -1} and warn user.
```

- [ ] **Step 3: Commit**

```bash
git add skills/superscrape/phases/phase-0-onboarding.md
git commit -m "refactor: remove VPS from phase-0, add Firecrawl credit budget"
```

---

### Task 9: Update phase-3-collect.md

**Files:**
- Modify: `skills/superscrape/phases/phase-3-collect.md`

- [ ] **Step 1: Add credit budget logic**

Before dispatching scraper agents:
```
Read _state/firecrawl_credits.json → initial_credits
If credits = 0 → STOP
If credits < source_count → STOP
If credits < source_count × 5 → per_source = floor(credits / source_count), warn
Else → per_source = 5
Pass per_source limit to each scraper agent prompt
```

- [ ] **Step 2: Add progress reporting**

After each scraper agent completes:
```
Print to chat: "✅ {source_name}: {records} записей ({n}/{total} источников)"
```

- [ ] **Step 3: Add rate limit message**

```
If scraper returns FAIL with rate limit:
Print: "⚠️ Rate limit. Данные сохранены в _state/. Скажи 'продолжай' когда будешь готов."
Save current progress and wait.
```

- [ ] **Step 4: Commit**

```bash
git add skills/superscrape/phases/phase-3-collect.md
git commit -m "feat: add credit budget, progress reporting, rate limit handling"
```

---

### Task 10: Update phase-4-normalize.md

**Files:**
- Modify: `skills/superscrape/phases/phase-4-normalize.md`

- [ ] **Step 1: Add cross-validation rule**

After deduplication, add:
```
Cross-validation:
- For each entity found in 2+ sources:
  - If 3+ sources: divergence >30% on numeric values → flag "conflicting data"
  - If 2 sources: divergence >50% → flag "conflicting data"
- If <2 sources overlap → skip, note "Cross-validation not possible"
- Save flags in normalized.json under "conflicts" key
- Show conflicts to user in Phase 4 checkpoint
```

- [ ] **Step 2: Commit**

```bash
git add skills/superscrape/phases/phase-4-normalize.md
git commit -m "feat: add cross-validation for entities in multiple sources"
```

---

### Task 11: Update phase-5c-dashboard-generate.md

**Files:**
- Modify: `skills/superscrape/phases/phase-5c-dashboard-generate.md`

- [ ] **Step 1: Update to use new assembly pattern**

Replace current instructions with:
```
1. Read dashboard_choice from _state/dashboard_choice.json
2. For Streamlit:
   a. Copy dashboard-streamlit-base.py to output_dir/dashboard.py
   b. Dispatch dashboard-designer with prompt: "Read dashboard-streamlit-assembly.md and follow steps"
3. For HTML:
   a. Copy dashboard-html-base.html to output_dir/dashboard.html
   b. Dispatch dashboard-designer with prompt: "Read dashboard-html-assembly.md and follow steps"
4. Dispatch dashboard-auditor
5. If auditor returns Issues → fix and re-audit (max 3)
```

- [ ] **Step 2: Add explicit complexity check for art-director**

```
Complexity check:
records = count rows in data.csv
columns = count columns
If records >= 50 OR columns >= 12 → COMPLEX
  Try dispatch dashboard-art-director → get creative brief
  If art-director not found → proceed without brief (MEDIUM fallback)
Else → SIMPLE/MEDIUM, skip art-director
```

- [ ] **Step 3: Commit**

```bash
git add skills/superscrape/phases/phase-5c-dashboard-generate.md
git commit -m "refactor: use base+assembly pattern in phase-5c, add art-director dispatch"
```

---

### Task 12: Update phase-5e-deploy.md

**Files:**
- Modify: `skills/superscrape/phases/phase-5e-deploy.md`

- [ ] **Step 1: Add VPS onboarding (moved from phase-0)**

```
VPS deploy flow:
1. Read ~/.claude/superscraper.local.md
2. If has vps_host + ssh_key_configured=true → deploy automatically via SSH
3. If no local.md or no VPS config:
   a. AskUserQuestion: "VPS IP и SSH user?"
   b. Check if SSH key exists: ls ~/.ssh/id_ed25519.pub
   c. If no key: ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N ""
   d. Show user: "Run this in PowerShell: type C:\Users\{user}\.ssh\id_ed25519.pub | ssh {user}@{ip} \"mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys\""
   e. Wait for user to confirm
   f. Verify: ssh -o BatchMode=yes {user}@{ip} "echo ok"
   g. Save to ~/.claude/superscraper.local.md
4. Deprecate ~/.superscrape-servers.json if found
```

- [ ] **Step 2: Add deprecation check for old servers.json**

At the start of the deploy flow, add:
```
Check if ~/.superscrape-servers.json exists.
If found → read VPS config from it, migrate to ~/.claude/superscraper.local.md, then warn:
"Migrated VPS config from deprecated ~/.superscrape-servers.json to ~/.claude/superscraper.local.md"
```

- [ ] **Step 3: Commit**

```bash
git add skills/superscrape/phases/phase-5e-deploy.md
git commit -m "feat: VPS onboarding with SSH key in phase-5e, credentials in local.md"
```

---

## Chunk 4: Infrastructure & Sync

### Task 13: Create install-hooks.sh

**Files:**
- Create: `scripts/install-hooks.sh`

- [ ] **Step 1: Write script**

```bash
#!/bin/bash
HOOK=".git/hooks/post-commit"
CACHE_DIR=$(find "$HOME/.claude/plugins/cache" -path "*/superscraper/*/skills" -maxdepth 5 2>/dev/null | head -1 | sed 's|/skills$||')

if [ -z "$CACHE_DIR" ]; then
    echo "⚠ Plugin cache not found. Skipping hook installation."
    exit 0
fi

cat > "$HOOK" << EOF
#!/bin/bash
CACHE_DIR="$CACHE_DIR"
if [ -d "\$CACHE_DIR" ]; then
    cp -r skills agents commands hooks .claude-plugin "\$CACHE_DIR/" 2>/dev/null
    echo "✓ Plugin cache synced to \$CACHE_DIR"
fi
EOF
chmod +x "$HOOK"
echo "✓ Post-commit hook installed → $CACHE_DIR"
```

Dynamic cache path detection instead of hardcoded version.

- [ ] **Step 2: Test**

Run: `bash scripts/install-hooks.sh`
Expected: "✓ Post-commit hook installed → /path/to/cache"
Verify: `cat .git/hooks/post-commit` shows correct script.

- [ ] **Step 3: Commit**

```bash
git add scripts/install-hooks.sh
git commit -m "feat: add post-commit hook installer for plugin cache sync"
```

---

### Task 14: Create local.md template

**Files:**
- Create: `skills/superscrape/references/local-md-template.md`

- [ ] **Step 1: Write template**

```yaml
---
# Superscraper local settings
# Created automatically on first deploy
vps_host: ""
vps_user: ""
ssh_key_configured: false
github_user: ""
firecrawl_configured: true
---

# Superscraper Local Configuration
This file stores per-machine settings for the Superscraper plugin.
```

- [ ] **Step 2: Commit**

```bash
git add skills/superscrape/references/local-md-template.md
git commit -m "feat: add local.md template for VPS/GitHub credentials"
```

---

## Chunk 5: Sync, Push & Verify

### Task 15: Sync cache and push

- [ ] **Step 1: Run install-hooks.sh**

```bash
bash scripts/install-hooks.sh
```

- [ ] **Step 2: Final commit if anything missed**

```bash
git status
# stage any remaining changes
git push
```

- [ ] **Step 3: Verify cache synced**

```bash
ls ~/.claude/plugins/cache/king-sheol/superscraper/*/skills/superscrape/references/dashboard-streamlit-base.py
```
Expected: file exists.

---

### Task 16: Smoke test base files

- [ ] **Step 1: Test Streamlit base**

```bash
cd skills/superscrape/references
cp ../../../output/2026-03-19-crm-small-business-2026/data.csv .
# Edit CSV_PATH in base.py to "data.csv"
streamlit run dashboard-streamlit-base.py --server.headless true
```
Open http://localhost:8501 — verify dark theme, AG Grid table, badges work, no `<span st...`

- [ ] **Step 2: Test HTML base**

Convert CSV to JSON, inject into base.html, open in browser.
Verify: AG Grid table (not plain HTML table), badges, detail panel, charts.

- [ ] **Step 3: Redeploy to VPS**

```bash
scp output/2026-03-19-crm-small-business-2026/dashboard.py root@46.149.79.21:/opt/streamlit-app/app.py
ssh root@46.149.79.21 "cd /opt/streamlit-app && source venv/bin/activate && pip install -q streamlit-echarts streamlit-aggrid && systemctl restart streamlit"
```

Verify: http://46.149.79.21:8501 shows fixed dashboard.

---

### Task 17: Full verification checklist (matches spec's 18 items)

All items must pass. If any fails → fix and re-verify.

- [ ] **Step 1: Base file smoke tests (spec items 0a-0c)**
- 0a. `streamlit run dashboard-streamlit-base.py` → starts, dark theme, sidebar, empty state
- 0b. Open `dashboard-html-base.html` → dark theme, skeleton, AG Grid container
- 0c. If either fails → fix before proceeding

- [ ] **Step 2: Dashboard quality (spec items 1-6)**
- 1. Streamlit table renders badges via AG Grid (no `<span st...`)
- 2. AG Grid fallback: `pip uninstall streamlit-aggrid -y` → dashboard loads with st.dataframe plain text → `pip install streamlit-aggrid`
- 3. Max 8 columns visible, detail panel/expander shows rest
- 4. Scatter chart: if fill rate <30% → shows donut or warning instead
- 5. CSS applied: dark theme, glassmorphism KPI cards, custom Streamlit overrides
- 6. Detail panel on initial load: shows "Select a row" message, not blank

- [ ] **Step 3: Kit restructure (spec items 7-8)**
- 7. dashboard.py was generated by editing base.py (CSS/imports survived assembly) — check custom CSS block is present in generated file
- 8. dashboard.html was generated by editing base.html (same check)

- [ ] **Step 4: Workflow verification (spec items 9-11)**
- 9. Phase 3 prints "N/M sources collected" progress messages
- 10. Rate limit scenario: explicit message with save confirmation
- 11. All generated Python: `open()` has `encoding='utf-8'`, `read_csv()` has `encoding='utf-8-sig'`

- [ ] **Step 5: Deploy verification (spec item 12)**
- 12. VPS deploy works without manual password entry (SSH key configured)

- [ ] **Step 6: Data quality verification (spec items 13-14)**
- 13. Cross-validation flags present in normalized.json for entities in 2+ sources
- 14. Firecrawl credit budget: no source exceeds allocation

- [ ] **Step 7: Infrastructure verification (spec items 15-18)**
- 15. `bash scripts/install-hooks.sh` creates working hook
- 16. Post-commit hook syncs cache (make a commit, check cache updated)
- 17. Streamlit redeployed to VPS at 46.149.79.21:8501
- 18. New agents (dashboard-art-director, dashboard-designer) discoverable after session restart
