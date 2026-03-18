# Superscraper v2: Phase Decomposition Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Split monolithic SKILL.md (421 lines) into orchestrator (~80 lines) + 11 phase files, update 4 subagents with strict output contracts, add resume protocol with session file.

**Architecture:** Orchestrator SKILL.md contains only critical rules, resume protocol, phase table, and dispatch loop. Each phase is a separate .md file loaded via `Read` on demand. Session state persisted in output dir.

**Tech Stack:** Claude Code plugin (markdown skill files + subagent definitions), Firecrawl CLI, Python/openpyxl

**Spec:** `docs/superpowers/specs/2026-03-18-superscraper-v2-optimization.md`

---

## Chunk 1: Orchestrator + Phase Files

### Task 1: Create phases directory and orchestrator

**Files:**
- Rewrite: `skills/superscrape/SKILL.md` (421 → ~80 lines)
- Create: `skills/superscrape/phases/` (directory)

- [ ] **Step 1: Create the new orchestrator SKILL.md**

Replace the entire `skills/superscrape/SKILL.md` with the orchestrator below. **Note:** The content below contains nested code fences. When writing the actual file, use the Write tool directly — do not copy-paste from this plan. The inner fences (bash, json) are part of the file content.

```markdown
---
name: superscrape
description: >
  Use when the user asks to collect data, scrape information, research a topic, compare options,
  find market data, gather statistics, build a comparison table, analyze competitors, monitor prices,
  or any variation of "собери данные", "найди информацию", "сравни", "исследуй рынок", "парсинг",
  "scrape", "research", "compare". Also triggers on requests like "сделай обзор", "найди лучшие",
  "покажи рейтинг", "проанализируй рынок". Do NOT trigger for simple web searches or single-page reads.
---

# Superscrape — Universal Data Collection & Analysis

## CRITICAL RULES

| # | Rule |
|---|------|
| 1 | Response language = user's conversation language. ALL output in that language. |
| 2 | Firecrawl = CLI only via Bash (`firecrawl search/scrape/map/crawl`). NEVER use ToolSearch. |
| 3 | BANNED: browser tools (Claude_in_Chrome, WebFetch, WebSearch, Chrome MCP). Even on resume. If Firecrawl credits exhausted → STOP and tell user. |
| 4 | Phase 5b (dashboard choice) and 5e (deploy) are MANDATORY. Do NOT skip. (Note: spec says "5d" for deploy but spec's phase numbering was corrected — 5d=review, 5e=deploy.) |
| 5 | Subagents REQUIRED: scraper, report-writer, dashboard-generator, data-quality-reviewer, report-reviewer. Do NOT generate files directly. |
| 6 | Save _state/ after EVERY phase. Phase is NOT done until state file written. |
| 7 | NO final results before Phase 6 completes. Evidence before assertions. |

## Resume Protocol

```bash
ls output/*/.superscrape-session.json 2>/dev/null | head -1
```

1. If session file found → read it → AskUserQuestion: "Found session at Phase X. Resume or start fresh?"
2. If resume → re-initialize TodoWrite from completed_phases → Read phase file for current_phase
3. If fresh or no session → new session, start Phase 0

Session file is ALWAYS inside output dir. Single source of truth for progress.

## Firecrawl CLI Reference

| Action | Command |
|--------|---------|
| Search | `firecrawl search "query" -o .firecrawl/file.json --json` |
| Scrape | `firecrawl scrape URL -o .firecrawl/file.md` |
| Map | `firecrawl map URL --search "keyword" -o .firecrawl/urls.txt` |
| Crawl | `firecrawl crawl URL --wait --limit N -o .firecrawl/file.json` |

Parallel: `firecrawl scrape URL1 -o f1.md & firecrawl scrape URL2 -o f2.md & wait`

## Phase Table

| Phase | File | Gate |
|-------|------|------|
| 0 | phases/phase-0-onboarding.md | firecrawl authenticated + python available |
| 1 | phases/phase-1-clarify.md | _state/config.json saved |
| 2 | phases/phase-2-discover.md | _state/sources.json saved |
| 3 | phases/phase-3-collect.md | ≥1 raw_data_*.json file in _state/ |
| 4 | phases/phase-4-normalize.md | _state/normalized.json with quality_review=Approved |
| 5a | phases/phase-5a-report-and-data.md | report.md + data.csv + data.xlsx exist |
| 5b | phases/phase-5b-dashboard-choice.md | _state/dashboard_choice.json saved |
| 5c | phases/phase-5c-dashboard-generate.md | dashboard file(s) exist or choice=none |
| 5d | phases/phase-5d-review.md | report-reviewer VERDICT: Approved |
| 5e | phases/phase-5e-deploy.md | deploy done or user declined |
| 6 | phases/phase-6-verify.md | all verification checks passed |

## Output Directory

`{CWD}/output/YYYY-MM-DD-{topic-slug}/`

## TodoWrite Init

```
Phase 0: Firecrawl onboarding
Phase 1: Clarify topic and columns
Phase 2: Discover sources
Phase 3: Collect data
Phase 4: Normalize and validate
Phase 5a: Generate report + data files
Phase 5b: Dashboard choice
Phase 5c: Generate dashboard
Phase 5d: Review report
Phase 5e: Deploy
Phase 6: Verify and present
```

## Dispatch Loop

After each phase completes:
1. Update .superscrape-session.json (mark completed, set next phase)
2. Update TodoWrite (mark current done, next in_progress)
3. Consult Phase Table → Read next phase file → execute it

Phase files end with "Phase X complete." — orchestrator controls all transitions.

## Start

Read `phases/phase-0-onboarding.md` and begin.
```

- [ ] **Step 2: Verify orchestrator line count**

Run: `wc -l skills/superscrape/SKILL.md`
Expected: ~80 lines (±10)

- [ ] **Step 3: Commit orchestrator**

```bash
git add skills/superscrape/SKILL.md
git commit -m "refactor: replace monolithic SKILL.md with ~80-line orchestrator"
```

---

### Task 2: Create Phase 0 and Phase 1 files

**Files:**
- Create: `skills/superscrape/phases/phase-0-onboarding.md`
- Create: `skills/superscrape/phases/phase-1-clarify.md`

- [ ] **Step 1: Write phase-0-onboarding.md**

```markdown
# Phase 0: Firecrawl & Python Onboarding

## Pre-check
None — this is the first phase.

## Instructions

1. Run `firecrawl --status` via Bash
2. Handle result:
   - **"command not found"**: Run `npm install -g firecrawl-cli`. If npm missing → tell user to install Node.js.
   - **"Not authenticated"**: Run `firecrawl login --browser`. Guide user through signup. If browser fails → tell user to visit firecrawl.dev, get API key, run `firecrawl login -k <KEY>`. Verify with `firecrawl --status`.
   - **"Authenticated"**: Note credits count from output.
3. Run `python --version`. Need 3.8+. If missing → inform user.
4. Run `pip install openpyxl --quiet 2>/dev/null` to ensure XLSX dependency.

## Save state

Create output directory and session file:
```bash
mkdir -p output/YYYY-MM-DD-{topic-slug}/_state
```

Write `.superscrape-session.json` in output dir:
```json
{
  "output_dir": "output/YYYY-MM-DD-{topic-slug}",
  "topic": "",
  "language": "{user's language}",
  "current_phase": "phase-0",
  "completed_phases": [],
  "firecrawl_credits_start": {credits from status},
  "created_at": "{ISO timestamp}"
}
```

**Decision:** Do NOT create the output directory in Phase 0. Defer to Phase 1 when topic is known. Phase 0 only checks tools. The session file is created in Phase 1 after the directory exists.

## Done
Phase 0 complete.
```

- [ ] **Step 2: Write phase-1-clarify.md**

```markdown
# Phase 1: Accept Task & Clarify Columns

## Pre-check
```bash
firecrawl --status 2>&1 | grep -q "Authenticated" && echo "GATE OK" || echo "GATE FAIL: Firecrawl not authenticated"
```
If GATE FAIL → STOP. Report failure. Ask user how to proceed.

## Instructions

1. Parse user request → extract topic, scope, data type (rating/comparison, prices, market research, competitor analysis)
2. Propose columns. 3 always required: Name, Source URL, Collection Date. Add topic-specific columns.
3. AskUserQuestion: "Columns look right? Suggest additions if needed."
4. If user suggests more → add them.
5. AskUserQuestion: confirm final column list.
6. Finalize output directory name using topic slug.

## Save state

Update `.superscrape-session.json`:
- Set `topic`, `current_phase: "phase-1"`, add `"phase-0"` to completed_phases
- Finalize `output_dir` path with proper topic slug

Write `_state/config.json`:
```json
{
  "topic": "...",
  "data_type": "rating|comparison|prices|market_research|competitor",
  "columns": ["Name", "Genre", ..., "Source URL", "Collection Date"],
  "scope": "...",
  "language": "ru"
}
```

## Done
Phase 1 complete.
```

- [ ] **Step 3: Commit**

```bash
git add skills/superscrape/phases/phase-0-onboarding.md skills/superscrape/phases/phase-1-clarify.md
git commit -m "feat: add phase-0 (onboarding) and phase-1 (clarify) files"
```

---

### Task 3: Create Phase 2 and Phase 3 files

**Files:**
- Create: `skills/superscrape/phases/phase-2-discover.md`
- Create: `skills/superscrape/phases/phase-3-collect.md`

- [ ] **Step 1: Write phase-2-discover.md**

```markdown
# Phase 2: Discover Sources

## Pre-check
```bash
cat {output_dir}/_state/config.json > /dev/null 2>&1 && echo "GATE OK" || echo "GATE FAIL: Phase 1 not completed (config.json missing)"
```
If GATE FAIL → STOP. Report failure. Ask user how to proceed.

## Instructions

1. Read `_state/config.json` for topic and scope.
2. Dispatch 2-3 parallel agents via Agent tool, each running Firecrawl search:
   - Agent 1: `firecrawl search "{topic}" --limit 10 --json` — find main sources
   - Agent 2: `firecrawl search "API {topic}" --limit 5 --json` — find public APIs
   - Agent 3: `firecrawl search "review comparison rating {topic}" --limit 10 --json` — find review sites
3. Compile unique sources, rank by quality (aggregators > APIs > official > reviews).
4. Credit economy: run `firecrawl map` on top 3 sources. If map returns <5 URLs → plan single scrape instead of crawl.
5. AskUserQuestion: present sources table with URL, type, estimated quality. Get user confirmation.

## Save state

Update `.superscrape-session.json`: current_phase → "phase-2", add "phase-1" to completed.

Write `_state/sources.json`:
```json
{
  "sources": [
    {"name": "DappRadar", "url": "https://...", "type": "aggregator", "quality": "High", "has_api": false, "scrape_plan": "single_page"},
    ...
  ],
  "total_sources": 5
}
```

## Done
Phase 2 complete.
```

- [ ] **Step 2: Write phase-3-collect.md**

```markdown
# Phase 3: Collect Data

## Pre-check
```bash
cat {output_dir}/_state/sources.json > /dev/null 2>&1 && echo "GATE OK" || echo "GATE FAIL: Phase 2 not completed (sources.json missing)"
```
If GATE FAIL → STOP. Report failure. Ask user how to proceed.

## Instructions

1. Read `_state/sources.json` and `_state/config.json` (for columns).
2. Calculate credit budget: divide available credits equally across sources.
3. Dispatch scraper subagent per source (max 5 in parallel). Each agent receives:
   - Source URL, type, scrape plan
   - Column list from config.json
   - Max 5 Firecrawl requests per source
4. After EACH agent returns:
   - Parse the JSON block from agent response (look for ```json ... ``` at end)
   - Save immediately to `_state/raw_data_{source_slug}.json`
   - Report progress: "{N}/{total} sources collected"
5. If agent fails → save error to `_state/errors.json` with root cause
6. If rate limit → save all data, tell user: "Rate limit reached, data saved. Say 'continue' when ready."
7. Checkpoint (MANDATORY): show first 3 records per source, AskUserQuestion: "Data looks correct?"

## Save state

Update `.superscrape-session.json`: current_phase → "phase-3", add "phase-2" to completed.

Files saved incrementally during collection:
- `_state/raw_data_{source_slug}.json` — per source
- `_state/errors.json` — failed sources (if any)

## Done
Phase 3 complete.
```

- [ ] **Step 3: Commit**

```bash
git add skills/superscrape/phases/phase-2-discover.md skills/superscrape/phases/phase-3-collect.md
git commit -m "feat: add phase-2 (discover) and phase-3 (collect) files"
```

---

### Task 4: Create Phase 4 file

**Files:**
- Create: `skills/superscrape/phases/phase-4-normalize.md`

- [ ] **Step 1: Write phase-4-normalize.md**

```markdown
# Phase 4: Normalize & Validate

## Pre-check
```bash
ls {output_dir}/_state/raw_data_*.json 2>/dev/null | head -1 > /dev/null && echo "GATE OK" || echo "GATE FAIL: Phase 3 not completed (no raw_data files)"
```
If GATE FAIL → STOP. Report failure. Ask user how to proceed.

## Instructions

This phase runs in main context (not subagents) — needs full picture for cross-source analysis.

1. Load ALL `_state/raw_data_*.json` files.
2. Merge into single dataset. Deduplicate by primary key (name field).
3. Cross-validation: if item in 3+ sources with >30% numeric discrepancy → flag as "conflicting data".
4. Dead project detection: if official site returned 404 or source noted inactivity → flag.
5. Defense-in-depth validation (4 layers):
   - Format: all expected columns present, types correct
   - Duplicates: exact and near-duplicates removed
   - Ranges: numeric values within reasonable bounds
   - Cross-check: values consistent across sources
6. Fill gaps: mark missing data as N/A with explanation.
7. Dispatch **data-quality-reviewer** subagent (MANDATORY):
   - Pass: normalized dataset, expected columns, topic, source count
   - If response contains "VERDICT: Issues Found" → fix issues → re-dispatch (max 3 iterations)
   - Phase is NOT complete until response contains "VERDICT: Approved"
8. Analyze: identify leaders (with reasons), patterns, anomalies, market context.
9. Assign confidence levels per source: High/Medium/Low with justification.

## Save state

Update `.superscrape-session.json`: current_phase → "phase-4", add "phase-3" to completed.

Write `_state/normalized.json` following the schema:
```json
{
  "topic": "...",
  "columns": [...],
  "column_types": {"Name": "text", "Price": "numeric", ...},
  "records": [{...}, ...],
  "analysis": {
    "leaders": [{"name": "...", "reason": "..."}],
    "patterns": ["..."],
    "anomalies": ["..."],
    "market_context": "..."
  },
  "quality_review": "Approved",
  "sources_used": ["..."],
  "total_records": N,
  "collection_date": "YYYY-MM-DD"
}
```

## Done
Phase 4 complete.
```

- [ ] **Step 2: Commit**

```bash
git add skills/superscrape/phases/phase-4-normalize.md
git commit -m "feat: add phase-4 (normalize and validate) file"
```

---

### Task 5: Create Phase 5a, 5b, 5c files

**Files:**
- Create: `skills/superscrape/phases/phase-5a-report-and-data.md`
- Create: `skills/superscrape/phases/phase-5b-dashboard-choice.md`
- Create: `skills/superscrape/phases/phase-5c-dashboard-generate.md`

- [ ] **Step 1: Write phase-5a-report-and-data.md**

```markdown
# Phase 5a: Generate Report + Data Files

## Pre-check
```bash
python -c "import json; d=json.load(open('{output_dir}/_state/normalized.json')); assert d.get('quality_review')=='Approved'; print('GATE OK')" 2>&1 || echo "GATE FAIL: Phase 4 not completed (normalized.json missing or not approved)"
```
If GATE FAIL → STOP. Report failure. Ask user how to proceed.

## Instructions

Dispatch TWO subagents in parallel (MUST use Agent tool):

1. **report-writer** subagent:
   - Pass: topic, date, output_dir, column list, normalized data, sources, analysis, confidence map
   - Agent reads report-format.md template via `Read ${CLAUDE_PLUGIN_ROOT}/skills/superscrape/references/report-format.md`
   - Writes: `{output_dir}/report.md`

2. **dashboard-generator** subagent with `mode: "data-only"`:
   - Pass: output_dir, normalized data (records + columns + column_types)
   - Agent reads xlsx-generator.md via `Read ${CLAUDE_PLUGIN_ROOT}/skills/superscrape/references/xlsx-generator.md`
   - Writes: `{output_dir}/data.csv` + `{output_dir}/data.xlsx`

After both return, verify:
```bash
test -s {output_dir}/report.md && echo "report.md OK" || echo "FAIL: report.md missing"
python -c "import csv; r=list(csv.reader(open('{output_dir}/data.csv'))); print(f'CSV OK: {len(r)-1} rows')"
python -c "import openpyxl; wb=openpyxl.load_workbook('{output_dir}/data.xlsx'); print(f'XLSX OK: {wb.sheetnames}')"
```

## Save state

Update `.superscrape-session.json`: current_phase → "phase-5a", add "phase-4" to completed.

## Done
Phase 5a complete.
```

- [ ] **Step 2: Write phase-5b-dashboard-choice.md**

```markdown
# Phase 5b: Dashboard Choice

## Pre-check
```bash
test -s {output_dir}/report.md && test -s {output_dir}/data.xlsx && echo "GATE OK" || echo "GATE FAIL: Phase 5a not completed (report.md or data.xlsx missing)"
```
If GATE FAIL → STOP. Report failure. Ask user how to proceed.

## Instructions

Use AskUserQuestion with exactly these options:
- "Streamlit (for VPS)" — interactive dashboard with filters
- "HTML (for GitHub Pages)" — static, fast loading
- "Both"
- "No dashboard — report and Excel only"

## Save state

Update `.superscrape-session.json`: current_phase → "phase-5b", add "phase-5a" to completed.

Write `_state/dashboard_choice.json`:
```json
{"choice": "streamlit|html|both|none"}
```

## Done
Phase 5b complete.
```

- [ ] **Step 3: Write phase-5c-dashboard-generate.md**

```markdown
# Phase 5c: Generate Dashboard

## Pre-check
```bash
cat {output_dir}/_state/dashboard_choice.json 2>/dev/null && echo "GATE OK" || echo "GATE FAIL: Phase 5b not completed (dashboard_choice.json missing)"
```
If GATE FAIL → STOP. Report failure. Ask user how to proceed.

## Instructions

1. Read `_state/dashboard_choice.json`.
2. If choice is "none" → skip to Done (phase still completes, gate for 5d passes automatically).
3. Dispatch **dashboard-generator** subagent with `mode: "dashboard-only"`:
   - Pass: output_dir, choice (streamlit/html/both), topic, column list with types, analysis summary (leaders, patterns, KPI values)
   - Agent reads dashboard-template.md via `Read ${CLAUDE_PLUGIN_ROOT}/skills/superscrape/references/dashboard-template.md`
   - Agent reads data from `{output_dir}/data.csv`
   - For Streamlit: generates dashboard.py + requirements.txt + Dockerfile + docker-compose.yml + nginx.conf
   - For HTML: generates dashboard.html (self-contained)
4. Verify generated files are syntactically valid:
```bash
# If Streamlit:
python -c "import ast; ast.parse(open('{output_dir}/dashboard.py').read()); print('Streamlit syntax OK')"
# If HTML:
test -s {output_dir}/dashboard.html && echo "HTML OK"
```
5. Visual preview: start a local server with `preview_start` or `python -m http.server`, take a screenshot of the dashboard, show to user. Ask: "Dashboard looks good?"

## Save state

Update `.superscrape-session.json`: current_phase → "phase-5c", add "phase-5b" to completed.

## Done
Phase 5c complete.
```

- [ ] **Step 4: Commit**

```bash
git add skills/superscrape/phases/phase-5a-report-and-data.md skills/superscrape/phases/phase-5b-dashboard-choice.md skills/superscrape/phases/phase-5c-dashboard-generate.md
git commit -m "feat: add phase-5a (report+data), 5b (dashboard choice), 5c (dashboard generate)"
```

---

### Task 6: Create Phase 5d, 5e, and Phase 6 files

**Files:**
- Create: `skills/superscrape/phases/phase-5d-review.md`
- Create: `skills/superscrape/phases/phase-5e-deploy.md`
- Create: `skills/superscrape/phases/phase-6-verify.md`

- [ ] **Step 1: Write phase-5d-review.md**

```markdown
# Phase 5d: Review Report

## Pre-check
```bash
# Dashboard must exist if choice was not "none"
choice=$(python -c "import json; print(json.load(open('{output_dir}/_state/dashboard_choice.json'))['choice'])" 2>/dev/null)
if [ "$choice" = "none" ]; then
  echo "GATE OK (no dashboard, skipped 5c)"
elif [ -s {output_dir}/dashboard.py ] || [ -s {output_dir}/dashboard.html ]; then
  echo "GATE OK"
else
  echo "GATE FAIL: Phase 5c not completed (dashboard files missing)"
fi
```
If GATE FAIL → STOP. Report failure. Ask user how to proceed.

## Instructions

1. Dispatch **report-reviewer** subagent:
   - Pass: path to report.md, topic, expected record count, source count
   - Agent reads full report.md
2. Check response for "VERDICT:" string.
   - If "VERDICT: Approved" → done.
   - If "VERDICT: Issues Found" → fix issues in report.md → re-dispatch (max 3 iterations).
   - If no VERDICT found → re-ask agent for explicit verdict.

## Save state

Update `.superscrape-session.json`: current_phase → "phase-5d", add "phase-5c" to completed.

## Done
Phase 5d complete.
```

- [ ] **Step 2: Write phase-5e-deploy.md**

```markdown
# Phase 5e: Deploy Dashboard

## Pre-check
Report must be reviewed and approved. Check session file for phase-5d in completed_phases.
```bash
python -c "import json; s=json.load(open('{output_dir}/.superscrape-session.json')); assert 'phase-5d' in s['completed_phases']; print('GATE OK')" 2>&1 || echo "GATE FAIL: Phase 5d not completed"
```
If GATE FAIL → STOP. Report failure. Ask user how to proceed.

## Instructions

1. Read `_state/dashboard_choice.json`. If "none" → save deploy_skipped, go to Done.
2. **For Streamlit (VPS):**
   - AskUserQuestion: VPS IP, SSH username, Docker installed? (Yes/No), domain (optional)
   - Execute: `scp -r {output_dir}/ user@ip:/opt/dashboards/{topic}/`
   - Execute: `ssh user@ip "cd /opt/dashboards/{topic} && docker compose up -d"`
   - Verify: `ssh user@ip "curl -s -o /dev/null -w '%{http_code}' http://localhost:8501"` → expect 200
   - If no SSH access → generate `deploy.sh` script with all commands
3. **For HTML (GitHub Pages):**
   - AskUserQuestion: repo name (suggest: dashboard-{topic-slug}), public/private
   - Execute: `gh repo create {name} --public --source=. --push`
   - Copy dashboard.html → index.html in repo root
   - Enable Pages: `gh api repos/{owner}/{name}/pages -X POST --input - <<< '{"source":{"branch":"main","path":"/"},"build_type":"legacy"}'`
   - Wait for build: poll `gh api repos/{owner}/{name}/pages/builds --jq '.[0].status'` until "built"
   - If gh CLI not authorized → suggest `gh auth login`
4. **Both:** deploy Streamlit first, then HTML.
5. If user declines deploy → save "deploy_skipped".

## Save state

Update `.superscrape-session.json`: current_phase → "phase-5e", add "phase-5d" to completed.

Write `_state/deploy_result.json`:
```json
{"streamlit_url": "http://...", "github_pages_url": "https://...", "status": "deployed|skipped"}
```

## Done
Phase 5e complete.
```

- [ ] **Step 3: Write phase-6-verify.md**

```markdown
# Phase 6: Verify & Present Results

## Pre-check
```bash
python -c "import json; s=json.load(open('{output_dir}/.superscrape-session.json')); assert 'phase-5e' in s['completed_phases']; print('GATE OK')" 2>&1 || echo "GATE FAIL: Phase 5e not completed"
```
If GATE FAIL → STOP. Report failure. Ask user how to proceed.

## Instructions

### Verification checks (all must pass):

```bash
# 1. Report exists
test -s {output_dir}/report.md && echo "✅ report.md" || echo "❌ report.md missing"

# 2. CSV valid
python -c "import csv; r=list(csv.reader(open('{output_dir}/data.csv'))); print(f'✅ CSV: {len(r)-1} rows, {len(r[0])} cols')"

# 3. XLSX valid
python -c "import openpyxl; wb=openpyxl.load_workbook('{output_dir}/data.xlsx'); print(f'✅ XLSX: sheets={wb.sheetnames}, rows={wb.active.max_row}')"

# 4. Dashboard (if generated)
# Streamlit:
python -c "import ast; ast.parse(open('{output_dir}/dashboard.py').read()); print('✅ dashboard.py')" 2>/dev/null
# HTML:
test -s {output_dir}/dashboard.html && echo "✅ dashboard.html" 2>/dev/null

# 5. Deploy URL (if deployed)
# Check deploy_result.json for URLs
```

### Phase 5 completion gate:
- Confirm _state/dashboard_choice.json exists (5b was asked)
- Confirm phase-5d in completed_phases (review done)
- Confirm phase-5e in completed_phases (deploy done or skipped)

If ANY check fails → go back and complete the missing phase. Do NOT present results.

### Present to user:

Show evidence first (file sizes, row counts), then summary:
```
✅ Data collection complete!

📊 Topic: {topic}
📋 Records: {N} from {M} sources
📁 Files:
  - report.md (analytical report)
  - data.csv / data.xlsx (data)
  - dashboard.py / dashboard.html (dashboard, if generated)

🚀 Dashboard: {URL, if deployed}
```

### Cleanup:
Delete `.superscrape-session.json` — session complete.

## Done
Phase 6 complete. All done.
```

- [ ] **Step 4: Commit**

```bash
git add skills/superscrape/phases/phase-5d-review.md skills/superscrape/phases/phase-5e-deploy.md skills/superscrape/phases/phase-6-verify.md
git commit -m "feat: add phase-5d (review), 5e (deploy), 6 (verify) files"
```

---

## Chunk 2: Subagent Updates + Sync + Push

### Task 7: Update scraper agent

**Files:**
- Modify: `agents/scraper.md`

- [ ] **Step 1: Update scraper output format**

Replace the `## Output` section (from `## Output` header through the closing ``` of the code block) with strict JSON contract:

```markdown
## Output

Your response MUST end with a JSON code block containing the structured result:

```json
{
  "source": "DappRadar",
  "url": "https://dappradar.com/...",
  "status": "SUCCESS",
  "records_count": 15,
  "data": [
    {"Name": "Game1", "Genre": "FPS", "DAU": 50000},
    {"Name": "Game2", "Genre": "MOBA", "DAU": 30000}
  ],
  "issues": ["Page 3 returned 403, skipped"],
  "confidence": "High"
}
```

Status values: SUCCESS (all data collected), PARTIAL (some pages failed), FAIL (no data).
The orchestrator will parse this JSON and save as `_state/raw_data_{source_slug}.json`.
```

- [ ] **Step 2: Add credit limit rule**

Add to the Rules section:
```
- **Max 5 Firecrawl requests per source** — do not exceed. If more pages exist, prioritize highest-value pages.
```

- [ ] **Step 3: Commit**

```bash
git add agents/scraper.md
git commit -m "refactor: scraper agent strict JSON output + 5-request limit"
```

---

### Task 8: Update dashboard-generator agent

**Files:**
- Modify: `agents/dashboard-generator.md`

- [ ] **Step 1: Add mode parameter to Input section**

Replace the `## Input` section (from `## Input` header through the `## Process` header, exclusive) with:

```markdown
## Input

You will receive:
- **mode**: "data-only" (Phase 5a: CSV+XLSX only) or "dashboard-only" (Phase 5c: dashboards only)
- **output_dir**: path to write files
- **Normalized dataset** (inline data or file path to read)

For "data-only" mode:
- Read xlsx-generator.md via `Read ${CLAUDE_PLUGIN_ROOT}/skills/superscrape/references/xlsx-generator.md`

For "dashboard-only" mode additionally:
- **dashboard_choice**: "streamlit", "html", or "both"
- **topic**, **column list with types**, **analysis summary** (leaders, patterns, KPI values)
- Read dashboard-template.md via `Read ${CLAUDE_PLUGIN_ROOT}/skills/superscrape/references/dashboard-template.md`
- Read data from `{output_dir}/data.csv`
```

- [ ] **Step 2: Update Process section**

Replace the Process section with mode-aware logic:

```markdown
## Process

### If mode = "data-only":

1. Read xlsx-generator.md template
2. Generate Python script that creates data.csv + data.xlsx
3. Run script via Bash
4. Verify both files

### If mode = "dashboard-only":

1. Read dashboard-template.md template
2. Read data from {output_dir}/data.csv
3. Determine visualization types using decision table from template
4. Generate chosen dashboard(s):
   - Streamlit → dashboard.py + requirements.txt + Dockerfile + docker-compose.yml + nginx.conf
   - HTML → dashboard.html (self-contained, data embedded as JSON)
5. Verify generated files
```

- [ ] **Step 3: Commit**

```bash
git add agents/dashboard-generator.md
git commit -m "refactor: dashboard-generator with mode parameter (data-only/dashboard-only)"
```

---

### Task 9: Update reviewer agents

**Files:**
- Modify: `agents/data-quality-reviewer.md`
- Modify: `agents/report-reviewer.md`

- [ ] **Step 1: Add verdict format to data-quality-reviewer**

Add at end of Rules section:

```markdown
- Your response MUST end with exactly one of these lines (no markdown formatting):
  `VERDICT: Approved`
  or
  `VERDICT: Issues Found`
  The orchestrator searches for "VERDICT:" to determine gate passage. If missing, you will be re-asked.
```

- [ ] **Step 2: Add verdict format to report-reviewer**

Add the same verdict rule at end of Rules section:

```markdown
- Your response MUST end with exactly one of these lines (no markdown formatting):
  `VERDICT: Approved`
  or
  `VERDICT: Issues Found`
  The orchestrator searches for "VERDICT:" to determine gate passage. If missing, you will be re-asked.
```

- [ ] **Step 3: Commit**

```bash
git add agents/data-quality-reviewer.md agents/report-reviewer.md
git commit -m "refactor: reviewer agents add strict VERDICT: output format"
```

---

### Task 10: Sync to plugin cache, push, verify

**Files:**
- No new files — sync existing to cache

- [ ] **Step 1: Sync all files to plugin cache**

```bash
rsync -av --delete \
  --exclude='.git' --exclude='output' --exclude='docs' --exclude='.claude' --exclude='README.md' --exclude='node_modules' \
  "C:/Users/OF-1/Documents/Claude Workspace/Code/Superscrapper/" \
  "$HOME/.claude/plugins/cache/king-sheol/superscraper/1.0.0/"
```

- [ ] **Step 2: Verify file structure in cache**

```bash
find "$HOME/.claude/plugins/cache/king-sheol/superscraper/1.0.0/skills/superscrape/phases" -name "*.md" | sort
```

Expected: 11 phase files listed.

- [ ] **Step 3: Verify orchestrator line count**

```bash
wc -l "$HOME/.claude/plugins/cache/king-sheol/superscraper/1.0.0/skills/superscrape/SKILL.md"
```

Expected: ~80 lines.

- [ ] **Step 4: Push to GitHub**

```bash
cd "C:/Users/OF-1/Documents/Claude Workspace/Code/Superscrapper"
git push
```

- [ ] **Step 5: Commit plan**

```bash
git add docs/superpowers/plans/2026-03-18-superscraper-v2-phase-decomposition.md
git commit -m "docs: add v2 implementation plan"
git push
```
