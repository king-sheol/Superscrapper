# Superscraper v2: Structural Optimization

> Date: 2026-03-18
> Status: Proposed
> Previous spec: 2026-03-17-superscraper-design.md
> Based on: Real test run (Web3 blockchain games, 2026-03-17)

## Problem Statement

Test run revealed 17 issues, root cause: monolithic SKILL.md (421 lines) overloads LLM context. Key failures:
- Phases 5b/5d/5e/6 skipped entirely
- Subagents not dispatched (bot did everything itself)
- After rate limit resume — complete context loss, data lost
- Browser tools used instead of Firecrawl CLI
- Dashboard and deploy onboarding never triggered
- Language rule ignored (English instead of Russian)

Previous fix approach (adding more rules/gates to the same file) made the problem worse — more text = more lost instructions.

### Issue Traceability Matrix

| # | Issue from test | Category | v2 Fix |
|---|----------------|----------|--------|
| C1 | WebSearch used instead of Firecrawl after resume | Critical | CRITICAL RULE #2-3 in orchestrator + per-phase pre-check |
| C2 | Data lost after rate limit (_state/ not saved) | Critical | Incremental save in Phase 3 + session file |
| C3 | Phase 5b skipped (no dashboard choice) | Critical | Separate phase file (impossible to skip) |
| C4 | Phase 5d skipped (no deploy) | Critical | Separate phase file + MANDATORY rule |
| C5 | Phase 5e skipped (no report review) | Critical | Separate phase file with gate check |
| C6 | Phase 6 skipped (no verification) | Critical | Gate: no results shown before Phase 6 |
| M1 | data-quality-reviewer not dispatched | Medium | Phase 4 gate requires quality_review=Approved |
| M2 | No data preview checkpoint in Phase 3 | Medium | Explicit step 8 in Phase 3 |
| M3 | DTF.ru 404 — no root cause diagnosis | Medium | errors.json + root cause in scraper agent |
| M4 | _state/config.json not saved | Medium | Phase 1 explicit save step |
| M5 | _state/sources.json not saved | Medium | Phase 2 explicit save step |
| M6 | Subagents not dispatched (bot did it itself) | Medium | CRITICAL RULE #5 + phase instructions |
| M7 | Dashboard in English (user wrote in Russian) | Medium | CRITICAL RULE #1 + language in config.json |
| L1 | ToolSearch for Firecrawl MCP tools | Low | CRITICAL RULE #2 |
| L2 | Browser opened on different device | Low | CRITICAL RULE #3 |
| L3 | Silent hang on rate limit | Low | Graceful message in Phase 3 step 7 |
| L4 | TodoWrite lost on resume | Low | Resume protocol re-initializes TodoWrite |

## Solution: Phase Decomposition

Split monolithic SKILL.md into orchestrator + 11 phase files. Each phase loaded via `Read` only when needed.

### New File Structure

```
skills/superscrape/
├── SKILL.md                          (~80 lines — orchestrator only)
├── phases/
│   ├── phase-0-onboarding.md         (~30 lines)
│   ├── phase-1-clarify.md            (~40 lines)
│   ├── phase-2-discover.md           (~45 lines)
│   ├── phase-3-collect.md            (~50 lines)
│   ├── phase-4-normalize.md          (~45 lines)
│   ├── phase-5a-report-and-data.md   (~35 lines)
│   ├── phase-5b-dashboard-choice.md  (~15 lines)
│   ├── phase-5c-dashboard-generate.md(~30 lines)
│   ├── phase-5d-review.md             (~25 lines)
│   ├── phase-5e-deploy.md            (~40 lines)
│   └── phase-6-verify.md             (~30 lines)
└── references/                       (unchanged)
    ├── report-format.md
    ├── xlsx-generator.md
    └── dashboard-template.md
```

### Orchestrator (SKILL.md) — ~80 lines

Contains ONLY:

1. **Frontmatter** — name, description, trigger phrases (unchanged)

2. **CRITICAL RULES** — compact table format:

| # | Rule |
|---|------|
| 1 | Response language = user's language |
| 2 | Firecrawl = CLI only via Bash. NEVER ToolSearch |
| 3 | BANNED: browser tools, WebFetch, WebSearch, Chrome MCP |
| 4 | Phase 5b (dashboard choice) and 5d (deploy) are MANDATORY |
| 5 | Subagents REQUIRED: scraper, report-writer, dashboard-generator, reviewers |
| 6 | Save _state/ after EVERY phase |
| 7 | NO final results before Phase 6 completes |

3. **Resume Protocol** (10 lines):
```
1. Search: ls output/*/.superscrape-session.json 2>/dev/null | head -1
2. If found → read current_phase → AskUserQuestion: "Resume from Phase X or start fresh?"
3. If resume → Read corresponding phase file from Phase Table → continue
4. If fresh or nothing found → new session, start Phase 0
5. On resume: re-initialize TodoWrite from session's completed_phases
```
Session file is ALWAYS inside output dir (never CWD). This is the single source of truth for resume. The `_state/` files are data storage; the session file tracks progress.

4. **Phase Table**:

| Phase | File | Gate (must be true before next phase) |
|-------|------|---------------------------------------|
| 0 | phases/phase-0-onboarding.md | firecrawl --status = authenticated |
| 1 | phases/phase-1-clarify.md | _state/config.json saved |
| 2 | phases/phase-2-discover.md | _state/sources.json saved |
| 3 | phases/phase-3-collect.md | ≥1 raw_data_*.json file exists |
| 4 | phases/phase-4-normalize.md | normalized.json with quality_review=Approved |
| 5a | phases/phase-5a-report-and-data.md | report.md + data.csv + data.xlsx exist |
| 5b | phases/phase-5b-dashboard-choice.md | _state/dashboard_choice.json saved |
| 5c | phases/phase-5c-dashboard-generate.md | dashboard file(s) exist |
| 5d | phases/phase-5d-review.md | report-reviewer verdict = Approved |
| 5e | phases/phase-5e-deploy.md | deploy done or user declined |
| 6 | phases/phase-6-verify.md | all checks passed |

5. **TodoWrite Template**:
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

6. **Output Directory Format**: `output/YYYY-MM-DD-{topic-slug}/`

7. **Dispatch loop** (centralized control flow — phases do NOT point to next phase):
```
After each phase completes:
1. Update .superscrape-session.json (mark phase completed, set next phase)
2. Update TodoWrite (mark current done, next in_progress)
3. Consult Phase Table → Read next phase file → execute it
```
Each phase file ends with "Phase X complete." — no "Read phase-Y.md" instruction. The orchestrator controls all transitions.

8. **Session start**: Read phases/phase-0-onboarding.md and begin.

### Phase File Template

Every phase file follows this structure:

```markdown
# Phase X: [Name]

## Pre-check
```bash
[gate verification command — executable, not prose]
```
If GATE FAIL → STOP. Report which gate condition failed. Do NOT re-run previous phase. Ask user how to proceed.

## Instructions
[20-40 lines of what to do]

## Save state
[what to write to _state/ and .superscrape-session.json]

## Done
Phase X complete. Return to orchestrator (SKILL.md dispatch loop) for next phase.
```

### Session File

`.superscrape-session.json` stored in output directory:

```json
{
  "output_dir": "output/2026-03-17-web3-esports-games",
  "topic": "Web3 blockchain games esports 2026",
  "language": "ru",
  "current_phase": "phase-3",
  "completed_phases": ["phase-0", "phase-1", "phase-2"],
  "firecrawl_credits_start": 525,
  "created_at": "2026-03-17T19:00:00Z"
}
```

Session file is always inside `{output_dir}/`. Resume searches `output/*/`.

**Note:** v2 is a clean break from v1 sessions. v1 used `_state/raw_data.json` (single file); v2 uses `_state/raw_data_{source}.json` (per-source). No migration — old sessions are not resumable.

### State Files

| File | Phase | Contents |
|------|-------|----------|
| `_state/config.json` | 1 | topic, columns, data type, language |
| `_state/sources.json` | 2 | confirmed sources with URLs, types |
| `_state/raw_data_{source}.json` | 3 | per-source data (incremental) |
| `_state/errors.json` | 3 | failed sources with root cause |
| `_state/normalized.json` | 4 | clean dataset + analysis + quality_review field |
| `_state/dashboard_choice.json` | 5b | user choice (streamlit/html/both/none) |
| `_state/deploy_result.json` | 5e | deploy URLs or "skipped" |

### normalized.json Schema

```json
{
  "topic": "Web3 blockchain games esports 2026",
  "columns": ["Name", "Genre", "Blockchain", ...],
  "column_types": {"Name": "text", "DAU": "numeric", "Genre": "categorical", ...},
  "records": [
    {"Name": "Game1", "Genre": "FPS", "DAU": 50000, ...},
    ...
  ],
  "analysis": {
    "leaders": [{"name": "Game1", "reason": "Highest DAU at 500K"}],
    "patterns": ["80% of games use Ethereum or Polygon"],
    "anomalies": ["Game5 claims 1M DAU but only 200 active wallets"],
    "market_context": "Average DAU for Web3 games is 15K"
  },
  "quality_review": "Approved",
  "sources_used": ["DappRadar", "PlayToEarn", ...],
  "total_records": 22,
  "collection_date": "2026-03-17"
}
```

---

## Phase-Specific Designs

### Phase 0: Onboarding

Check firecrawl CLI and Python:
1. `firecrawl --status` → if not found, `npm install -g firecrawl-cli`
2. If not authenticated → open browser for registration, help enter API key
3. `python --version` → if not found, inform user
4. Record starting credits count in session file

### Phase 1: Clarify

1. Parse user request → extract topic, scope, data type
2. Propose columns (3 mandatory: Name, Source URL, Collection Date + topic-specific)
3. AskUserQuestion: "Columns look right? Suggest additions"
4. If user suggests more → add them
5. AskUserQuestion: confirm final column list
6. Save config.json

### Phase 2: Discover Sources

1. Dispatch 2-3 parallel agents via Firecrawl search:
   - Agent 1: main topic search
   - Agent 2: "API" + topic
   - Agent 3: "review/comparison/rating" + topic
2. Compile unique sources, rank by quality
3. Credit economy check: run `firecrawl map` on top 3 sources. If map returns <5 URLs, the source likely has all data on one page → plan single `firecrawl scrape` instead of multi-page crawl. Each `firecrawl map` costs 1 credit.
4. AskUserQuestion: present sources table, get confirmation
5. Save sources.json

### Phase 3: Collect Data

1. Distribute Firecrawl credit budget equally across sources
2. Dispatch scraper agents in parallel (1 per source, max 5)
3. Each agent: max 5 Firecrawl requests per source
4. After EACH agent returns → immediately save `raw_data_{source}.json`
5. Progress updates in chat: "3/5 sources collected"
6. If agent fails → save to errors.json with root cause diagnosis
7. If rate limit hit → save all collected data, tell user: "Rate limit reached, data saved. Say 'continue' when ready"
8. Checkpoint: show preview (first 3 records per source), ask "Data looks correct?"

**Scraper agent output format** (strict JSON at end of response):
```json
{
  "source": "DappRadar",
  "status": "SUCCESS|PARTIAL|FAIL",
  "records_count": 15,
  "data": [...],
  "issues": [],
  "confidence": "High|Medium|Low"
}
```

### Phase 4: Normalize and Validate

1. Load all raw_data_*.json files
2. Merge, deduplicate by primary key (name)
3. Cross-validation: if item found in 3+ sources with >30% numeric discrepancy → flag as "conflicting data"
4. Dead project detection: if official site returns 404 or last activity >6 months → flag
5. Defense-in-depth validation (4 layers):
   - Format: all columns present, types correct
   - Duplicates: exact and near-duplicates removed
   - Ranges: numeric values within reasonable bounds
   - Cross-check: data consistent across sources
6. Dispatch data-quality-reviewer subagent
7. If Issues Found → fix → re-dispatch (max 3 iterations)
8. Save normalized.json WITH `quality_review: "Approved"` field
9. Analyze: leaders, patterns, anomalies, market context

### Phase 5a: Report and Data Files

1. Dispatch report-writer subagent (reads report-format.md template)
2. Dispatch dashboard-generator subagent with `mode: "data-only"` (CSV + XLSX only)
3. Both run in parallel
4. Verify: report.md exists, data.csv parseable, data.xlsx loadable

### Phase 5b: Dashboard Choice

1. Pre-check: report.md + data.xlsx exist
2. AskUserQuestion with 4 options:
   - Streamlit (for VPS)
   - HTML (for GitHub Pages)
   - Both
   - No dashboard
3. Save dashboard_choice.json

Entire phase = 1 question. Impossible to skip.

### Phase 5c: Dashboard Generate

1. Read dashboard_choice.json
2. If "none" → skip to 5e
3. Dispatch dashboard-generator subagent with:
   - normalized.json (data)
   - config.json (columns, types)
   - dashboard_choice.json (which type)
   - Analysis from Phase 4 (leaders, patterns — for KPI cards)
4. HTML dashboard: use template skeleton from references/dashboard-template.md, agent fills in data + chart config
5. Take screenshot via preview tools → show user before deploy
6. Verify: generated files are syntactically valid

### Phase 5d: Review (moved before deploy — review content before publishing)

1. Dispatch report-reviewer subagent
2. If Issues Found → fix report.md → re-dispatch (max 3 iterations)
3. Must reach verdict "Approved"

### Phase 5e: Deploy (after review — only deploy verified content)

1. Read dashboard_choice.json → determine what to deploy
2. For Streamlit:
   - AskUserQuestion: VPS IP + SSH username
   - Auto-execute: scp files → ssh docker compose up → verify with curl
   - If no SSH access → generate deploy.sh script
3. For HTML:
   - AskUserQuestion: repo name
   - Auto-execute: gh repo create → git init → push → enable Pages → verify URL
   - If no gh CLI → generate instructions
4. If user declines deploy → save "deploy_skipped"
5. Save deploy_result.json

### Phase 6: Verify and Present

1. Run verification checks (bash):
   - `python -c "import csv; csv.reader(open('data.csv'))"` → CSV valid
   - `python -c "from openpyxl import load_workbook; load_workbook('data.xlsx')"` → XLSX valid
   - `python -c "import ast; ast.parse(open('dashboard.py').read())"` → Streamlit syntax OK (if generated)
   - Check report.md has all 6 sections
2. Show evidence to user (not just "done"):
   - Record count: "22 records across 8 sources"
   - File sizes and paths
   - Dashboard URL (if deployed)
   - Screenshot of dashboard (if generated)
3. Present final summary with all file paths
4. Delete .superscrape-session.json (session complete)

---

## Quality Improvements (new in v2)

### Data Quality
- **Cross-validation**: items found in 3+ sources → compare numeric fields, flag >30% discrepancy
- **Dead project detection**: 404 on official site or last activity >6 months → mark and explain

### Dashboard Quality
- **Template skeleton**: HTML dashboard uses a fixed skeleton from references/, agent only injects data and chart configuration — prevents quality variance
- **Visual preview**: screenshot shown to user BEFORE deploy via preview tools

### Firecrawl Credit Economy
- **Budget tracking**: record starting credits in session file, distribute equally across sources
- **Map before scrape**: `firecrawl map` on source → if single page has all data, scrape once instead of crawling
- **Per-source limit**: max 5 Firecrawl requests per source

### UX Improvements
- **Progress in chat**: "3/5 sources collected" after each scraper agent
- **Graceful rate limit**: "Rate limit reached, data saved to _state/. Say 'continue' when ready" — not silent hang
- **Resume awareness**: always check for existing session before starting fresh

---

## Subagent Changes

### scraper.md
- Replace markdown table output with strict JSON block at end of response
- Add max 5 Firecrawl requests per source limit
- Keep: Firecrawl CLI only, root cause error handling, API-first strategy
- Exact output contract:
```
Your final message MUST end with a JSON code block:
```json
{
  "source": "DappRadar",
  "url": "https://dappradar.com/...",
  "status": "SUCCESS",
  "records_count": 15,
  "data": [
    {"Name": "Game1", "Genre": "FPS", ...},
    {"Name": "Game2", "Genre": "MOBA", ...}
  ],
  "issues": ["Page 3 returned 403, skipped"],
  "confidence": "High"
}
```
The orchestrator will parse this JSON block and save it as `_state/raw_data_{source_slug}.json`.
```

### dashboard-generator.md
- Add `mode` parameter: "data-only" (Phase 5a: CSV+XLSX) or "dashboard-only" (Phase 5c: dashboards)
- Input contract for "data-only" mode:
  - Prompt includes: output_dir path, normalized data (inline or file path)
  - Agent reads xlsx-generator.md via `Read ${CLAUDE_PLUGIN_ROOT}/skills/superscrape/references/xlsx-generator.md`
  - Generates: data.csv + data.xlsx
- Input contract for "dashboard-only" mode:
  - Prompt includes: output_dir path, dashboard_choice (streamlit/html/both), topic, column list with types, analysis summary (leaders, patterns, KPI values)
  - Agent reads dashboard-template.md via `Read ${CLAUDE_PLUGIN_ROOT}/skills/superscrape/references/dashboard-template.md`
  - Agent reads data from `{output_dir}/data.csv`
  - HTML dashboard: uses skeleton from references/, fills in data + chart config
  - Generates: dashboard.py and/or dashboard.html + deployment files
- Keep: verification step (syntax checks on generated files)

### data-quality-reviewer.md
- Add strict verdict as LAST LINE of response: `VERDICT: Approved` or `VERDICT: Issues Found`
- Orchestrator detection: search for string "VERDICT:" in agent response. If not found → re-ask agent for explicit verdict.
- Keep: 5 check categories, severity levels, max 3 iterations, read-only

### report-reviewer.md
- Add strict verdict as LAST LINE of response: `VERDICT: Approved` or `VERDICT: Issues Found`
- Same detection logic as data-quality-reviewer
- Keep: 7 check categories, max 3 iterations, read-only

### report-writer.md
- No changes

---

## What Does NOT Change

- references/ (report-format.md, xlsx-generator.md, dashboard-template.md)
- skills/superscrape-dashboard/ and skills/superscrape-update/
- commands/superscrape.md
- hooks/ (hooks.json, session-start)
- plugin.json, marketplace.json
- 6-phase workflow logic (same phases, just split into files)
- 5 subagent roles
- Firecrawl CLI approach
- Output format (report.md, data.csv, data.xlsx, dashboard.py/html)

---

## Implementation Plan

### Step 1: Create phase files
Write all 11 phase-*.md files based on current SKILL.md content, restructured per template.

### Step 2: Rewrite SKILL.md
Replace 421-line monolith with ~80-line orchestrator.

### Step 3: Update subagents
Add strict output format to scraper, reviewer verdict format, dashboard-generator metadata input.

### Step 4: Sync and test
Sync to plugin cache, push to GitHub, test with a real query.

### Step 5: Verify
Run /superscrape on a new topic, check all phases execute, all subagents dispatch, all gates pass.
