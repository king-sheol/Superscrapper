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

Collect, normalize, and analyze data from multiple web sources. Produce structured analytical reports with XLSX and interactive dashboards.

## CRITICAL RULES (read before anything else)

1. **Language**: ALWAYS respond in the user's CONVERSATION language, not the topic language. If the user writes in Russian but the topic is "Web3 games" — ALL output (plans, reports, questions, checkpoints, TodoWrite labels, dashboard UI text) must be in Russian. Non-negotiable.

2. **Firecrawl is a CLI tool, NOT an MCP tool**: Do NOT use ToolSearch to find Firecrawl tools. Do NOT look for MCP tools. Firecrawl is invoked ONLY via `Bash` tool with CLI commands like `firecrawl search`, `firecrawl scrape`, etc. See the CLI Reference table below.

3. **NEVER use browser automation**: Do NOT use Claude_in_Chrome, WebFetch, WebSearch, or any browser/MCP browsing tools for data collection. ALL web access must go through Firecrawl CLI. The ONLY exception is `gh` CLI for GitHub operations in Phase 5d. **Even on resume after rate limit — NEVER fall back to WebSearch/WebFetch.** If Firecrawl credits are exhausted, STOP and tell the user.

4. **NEVER skip Phase 5 substeps**: Phase 5 has 5 mandatory substeps (5a→5b→5c→5d→5e). Each one is a separate TodoWrite item. Do NOT show final results until ALL are done.

5. **NEVER skip Phase 6**: You CANNOT present final results before Phase 6 verification is complete. Evidence before assertions.

6. **ALWAYS use subagents**: report-writer, dashboard-generator, data-quality-reviewer, report-reviewer MUST be dispatched as Agent subagents. Do NOT write report.md or generate files directly in the main context.

7. **ALWAYS save _state/ after each phase**: A phase is NOT complete until its `_state/*.json` file is written. See Intermediate Data Persistence below.

## Resume Protocol (MANDATORY on any resume / "продолжай")

When you receive "продолжай", "continue", or start working on an existing topic:

1. **Find the output directory**: Look for `output/YYYY-MM-DD-*/` in the working directory
2. **Check `_state/` files** in this order:
   ```
   _state/normalized.json  → exists? Skip to Phase 5
   _state/raw_data.json    → exists? Skip to Phase 4
   _state/sources.json     → exists? Skip to Phase 3 (confirm sources with user first)
   _state/config.json      → exists? Skip to Phase 2
   Nothing                 → Start from Phase 1
   ```
3. **Restore TodoWrite** based on the last completed phase
4. **Tell the user**: "Нашёл данные от предыдущего запуска ({file}). Продолжаю с фазы N."
5. **Continue strictly from that phase** — do NOT restart from scratch, do NOT skip ahead

**If _state/ files are empty or corrupted**: Tell the user what happened and ask whether to restart or try to recover.

## Phase 0: Firecrawl Onboarding (auto, before any work)

Before starting the workflow, **always** run this check:

```bash
firecrawl --status
```

Handle each case:

**Case 1: "command not found"** — Firecrawl CLI not installed:
```bash
npm install -g firecrawl-cli
```
If npm not found, tell the user to install Node.js first.

**Case 2: "Not authenticated"** — CLI installed but no API key:
1. Run `firecrawl login --browser` — this opens the browser for signup/login
2. Tell the user: "Откроется браузер для регистрации в Firecrawl. Создай аккаунт (или войди), скопируй API ключ."
3. If browser login fails, tell the user to:
   - Go to https://www.firecrawl.dev and sign up
   - Copy the API key from dashboard
   - Then run: `firecrawl login -k <API_KEY>`
4. After login, verify with `firecrawl --status` — must show "Authenticated"

**Case 3: "Authenticated"** — ready to go. Note the credits and concurrency limits from the output.

**Python check**: Also verify `python --version` (need 3.8+). If missing, tell the user.

Only proceed to Phase 1 after both Firecrawl and Python are confirmed ready.

## Firecrawl CLI Reference

Firecrawl is a CLI tool invoked via Bash. Always save output to `.firecrawl/` directory with `-o` flag.

| Action | CLI Command | Usage |
|--------|------------|-------|
| Web search | `firecrawl search "query" -o .firecrawl/file.json --json` | Find sources by topic. `--limit N`, `--scrape` to include content |
| Scrape page | `firecrawl scrape URL -o .firecrawl/file.md` | Extract content from URL. `--wait-for 3000` for JS, `--only-main-content` |
| Map site URLs | `firecrawl map URL --search "keyword" -o .firecrawl/urls.txt` | Discover URLs on a site, filter by keyword |
| Crawl site | `firecrawl crawl URL --wait --limit N -o .firecrawl/file.json` | Crawl multiple pages. `--max-depth`, `--include-paths` |
| AI agent | `firecrawl agent "task" --wait -o .firecrawl/file.json` | Autonomous extraction. `--urls`, `--schema` for structured output |

**Parallelization**: Run independent scrapes with `&` and `wait`:
```bash
firecrawl scrape URL1 -o .firecrawl/1.md &
firecrawl scrape URL2 -o .firecrawl/2.md &
wait
```

## Workflow

Follow these 6 phases strictly. Every phase has a GATE — you cannot proceed until the gate condition is met.

**At the very start**, initialize TodoWrite with ALL phases and substeps:
```
TodoWrite:
0. [in_progress] Phase 0: Firecrawl & Python check
1. [pending] Phase 1: Accept task & clarify columns
2. [pending] Phase 2: Discover sources
3. [pending] Phase 3: Collect data from sources
4. [pending] Phase 4: Normalize, validate & quality review
5a. [pending] Phase 5a: Generate report + data files (subagents)
5b. [pending] Phase 5b: Ask user about dashboard choice
5c. [pending] Phase 5c: Generate chosen dashboard(s) (subagent)
5d. [pending] Phase 5d: Deploy dashboard
5e. [pending] Phase 5e: Review report quality (subagent)
6. [pending] Phase 6: Verify & present results
```
Update TodoWrite as you progress. Mark each item completed ONLY when its gate is passed.

## Output Directory

All generated files go into a dated subdirectory:
```
{current-working-directory}/output/YYYY-MM-DD-{topic-slug}/
```
Where `{topic-slug}` is the topic in lowercase with spaces replaced by hyphens (e.g., `crm-systems`).

**Create this directory and `_state/` at the START of Phase 1** so intermediate data is persisted from the very beginning.

## Intermediate Data Persistence

**CRITICAL**: Agent temp files disappear between sessions. Save state to output directory DURING each phase, not just at the end:

| When | Save to file | Contents |
|------|-------------|----------|
| End of Phase 1 | `_state/config.json` | topic, data_type, columns list, scope |
| End of Phase 2 | `_state/sources.json` | approved sources with URLs, types, quality |
| **After EACH scraper agent returns** in Phase 3 | `_state/raw_data.json` | append/merge new data immediately |
| Before Phase 3 checkpoint | `_state/raw_data.json` | full dataset (must be saved BEFORE showing preview) |
| End of Phase 4 | `_state/normalized.json` | cleaned dataset + analysis + confidence map |

**Phase 3 incremental save is critical**: Do NOT wait until all agents finish. After each agent returns, immediately merge its data into `_state/raw_data.json`. This way, even if rate limit hits mid-Phase 3, collected data is preserved.

Format: JSON. Overwrite with latest state on each save.

**On resume**: See Resume Protocol above.

### Phase 1: Accept Task & Clarify

1. Parse the user's request to identify:
   - **Topic**: what to research
   - **Data type**: rating/comparison, price monitoring, market research, competitor analysis
   - **Scope**: how many items, which geography, time period

2. Determine columns for the data table. Three columns are always required:
   - Object name
   - Source (URL)
   - Collection date

3. If additional columns are not obvious from the request, use AskUserQuestion:
   ```
   "Какие метрики важны для сравнения? Вот мои предложения:"
   Options based on data type:
   - Rating/comparison: price, rating, features, pros/cons
   - Price monitoring: current price, historical price, discount, availability
   - Market research: market share, revenue, growth rate, geography
   - Competitor analysis: pricing, features, target audience, strengths/weaknesses
   ```

4. Confirm the final column list with the user before proceeding.

5. **Save state**: Create output directory and save config:
```bash
mkdir -p output/YYYY-MM-DD-{topic-slug}/_state
```
Write `_state/config.json` with: `{"topic": "...", "data_type": "...", "columns": [...], "scope": "..."}`

**GATE**: config.json saved → proceed to Phase 2.

### Phase 2: Source Discovery (2-3 agents in parallel)

Dispatch 2-3 agents in parallel using the Agent tool:

- **Agent 1**: Firecrawl `search` for the main topic — find aggregators, rating sites, official sources
- **Agent 2**: Firecrawl `search` for "API" + topic — find public APIs to use preferentially
- **Agent 3**: Firecrawl `search` for "обзор/рейтинг/сравнение/review/comparison" + topic

Each agent returns a list of potential sources with:
- URL
- Type (aggregator, official site, review site, API)
- Estimated data quality (High/Medium/Low)
- Whether it has an API

**Checkpoint**: Present the discovered sources to the user via AskUserQuestion:
```
"Нашёл N источников. Вот лучшие:"
- [source 1] — aggregator, ~500 entries, quality: High
- [source 2] — official API, structured data
- [source 3] — review site, ~100 entries
"Какие использовать? Добавить другие?"
```

Wait for user confirmation before proceeding.

**Save state**: Write `_state/sources.json` with the approved source list (URLs, types, quality).

**GATE**: sources.json saved + user confirmed → proceed to Phase 3.

### Phase 3: Data Collection (up to 5 scraper agents in parallel)

For each approved source, dispatch a **scraper** subagent (see agents/scraper.md):
- Each agent works with ONE source
- Uses Firecrawl CLI (search, scrape, map, agent)
- If a public API was found — use it preferentially via fetch
- Returns structured data matching the agreed column list

**Rate limiting**: instruct agents to pause between requests.

**Incremental save**: After EACH scraper agent returns, IMMEDIATELY merge its data into `_state/raw_data.json`. Do NOT wait for all agents to finish.

**Error handling** (Root Cause approach):
- If source is blocked: diagnose (HTTP code? timeout? rate limit? geo-block?)
- HTTP 404 → verify URL is correct, try `firecrawl map` on domain, find alternative
- Rate limit → increase pause, retry
- JS-only rendering → use Firecrawl with `--wait-for 3000`
- Geo-block → find alternative source
- No data → mark N/A with explanation
- Report all issues to the user

**Checkpoint** (MANDATORY — save data BEFORE showing this):
First save `_state/raw_data.json` with ALL collected data, then show preview:
```
"Собрал N записей из M источников. Вот первые 5:"
| Name | Price | Rating | Source | Date |
| ...  | ...   | ...    | ...    | ...  |
"Колонки верные? Данные выглядят правильно?"
```

**GATE**: raw_data.json saved + user confirmed preview → proceed to Phase 4.

### Phase 4: Normalize & Validate (sequential, orchestrator)

This phase runs in the main context (not subagents) because it needs the full picture.

1. **Merge** data from all scraper agents into a single dataset

2. **Defense-in-depth validation (4 layers)**:
   - Layer 1 (format): data types, encodings, units of measurement
   - Layer 2 (duplicates): deduplication by key fields
   - Layer 3 (ranges): numbers within reasonable bounds, dates valid
   - Layer 4 (cross-check): data from different sources consistent?

3. **Fill gaps**: mark missing data as N/A with explanation

4. **Dispatch data-quality-reviewer subagent** (MANDATORY — see agents/data-quality-reviewer.md):
   - Check completeness, consistency, anomalies
   - If Issues Found → fix and re-dispatch (max 3 iterations)
   - Phase 4 is NOT complete until data-quality-reviewer returns **Approved**

5. **Analyze**:
   - Identify leaders and why
   - Find patterns across data
   - Flag anomalies and outliers
   - Compare with market benchmarks where possible

6. **Assign confidence levels** to each source: High / Medium / Low with justification

**Save state**: Write `_state/normalized.json` with the full normalized dataset, analysis results, and confidence map.

**GATE**: normalized.json saved + data-quality-reviewer returned Approved → proceed to Phase 5.

### Phase 5: Generate Output

**5a: Report + Data (always, in parallel — use subagents)**

Dispatch two subagents simultaneously:

**Metadata to pass to BOTH agents:**
- `topic`: research topic (string)
- `date`: collection date (YYYY-MM-DD)
- `output_dir`: path to output directory
- `headers`: list of column names
- `data`: normalized dataset (all rows)
- `sources`: list of {url, reliability, justification} objects
- `analysis`: {leaders, patterns, anomalies, market_context} from Phase 4
- `confidence_map`: list of {source, level, reason} objects

**Agents (MUST use Agent tool, do NOT generate files directly):**
- **report-writer** subagent → `{output_dir}/report.md` (see agents/report-writer.md)
- **dashboard-generator** subagent → `{output_dir}/data.csv` + `{output_dir}/data.xlsx` (see agents/dashboard-generator.md)

Use the report format from `references/report-format.md`.
Use XLSX generation instructions from `references/xlsx-generator.md`.

**GATE**: report.md + data.csv + data.xlsx all exist → proceed to 5b.

**5b: Dashboard Choice (MANDATORY — do NOT skip)**

Immediately after 5a completes, you MUST ask the user about dashboards. Do NOT present final results yet. Do NOT generate any dashboard before asking.

Use AskUserQuestion:
```
"Отчёт и данные готовы. Какой дашборд сгенерировать?"
├── Streamlit (для VPS) — интерактивный, с фильтрами и графиками (Recommended)
├── HTML (для GitHub Pages) — статический, быстрая загрузка
├── Оба варианта
└── Без дашборда — только отчёт и Excel
```

If user chooses "Без дашборда", skip 5c and 5d and go directly to 5e.

**GATE**: user answered → proceed to 5c (or 5e if "Без дашборда").

**5c: Generate chosen dashboard(s) — use subagent**

Based on user choice, dispatch dashboard-generator subagent(s):
- Streamlit → dashboard.py + Dockerfile + docker-compose.yml + nginx.conf + requirements.txt
- HTML → dashboard.html (self-contained with embedded data, interactive: filters, search, sorting)
- Both → two agents in parallel

Use dashboard templates from `references/dashboard-template.md`.

**GATE**: chosen dashboard files exist → proceed to 5d.

**5d: Deploy Onboarding (MANDATORY if dashboard was generated — do NOT skip)**

Immediately after 5c, you MUST deploy the dashboard. Do NOT just show files and stop. The plugin does deployment itself, asking only for information it cannot determine.

**For Streamlit on VPS:**
1. AskUserQuestion: "Куда деплоить Streamlit-дашборд?"
   - IP/hostname сервера
   - SSH пользователь
   - Есть ли Docker на сервере? (Да / Нет / Не знаю)
   - Домен для дашборда (опционально)
2. Execute via Bash: scp files → ssh docker compose up → configure nginx → verify curl
3. Verify: curl the dashboard URL → must return 200 OK
4. Fallback if no SSH access: generate deploy.sh script + instructions

**For HTML on GitHub Pages:**
1. AskUserQuestion: "Куда деплоить HTML-дашборд?"
   - Создать новый репозиторий или использовать существующий?
   - Имя репо (предложить: dashboard-{topic-slug})
   - Public или Private?
2. Execute via Bash: `gh repo create` → copy dashboard.html as index.html → git init/add/commit/push → enable Pages via `gh api`
3. Wait for build: poll `gh api repos/{owner}/{repo}/pages/builds` until status is "built"
4. Verify: show the live URL to the user
5. Fallback if gh CLI not authorized: suggest `gh auth login` or manual instructions

**If BOTH dashboards were chosen:** deploy both sequentially (VPS first, then GitHub Pages).

**GATE**: dashboard deployed (or user explicitly declined) → proceed to 5e.

**5e: Report Review (MANDATORY)**

Dispatch **report-reviewer** subagent (see agents/report-reviewer.md):
- Check all sections present
- Numbers have context (good/bad, above/below market)
- Insights are specific, not generic
- If Issues Found → fix and re-dispatch (max 3 iterations)

**GATE**: report-reviewer returned Approved → proceed to Phase 6.

### Phase 6: Verification Before Completion (MANDATORY — NEVER skip)

**You CANNOT present final results before this phase is complete.**

**Evidence over claims** — verify every output:

- [ ] report.md exists and is not empty
- [ ] data.csv parses without errors: `python -c "import csv; r=csv.reader(open('data.csv')); print(f'{sum(1 for _ in r)-1} rows')"`
- [ ] data.xlsx is valid: `python -c "import openpyxl; wb=openpyxl.load_workbook('data.xlsx'); print(f'{wb.sheetnames}')"`
- [ ] If Streamlit: dashboard.py syntax check: `python -c "import ast; ast.parse(open('dashboard.py').read()); print('OK')"`
- [ ] If HTML: dashboard.html exists and is non-empty
- [ ] If deployed: URL returns 200 OK

**Verify Phase 5 completion gate**: Before presenting results, confirm:
- [ ] 5b was asked (dashboard choice)
- [ ] 5d was executed (deploy) or explicitly skipped by user
- [ ] 5e was executed (report review returned Approved)

If ANY of the above are missing — go back and complete them. Do NOT present results with incomplete phases.

**Show evidence to user**: first 3 rows of table + file list with sizes.

**Final summary in chat**:
```
✅ Сбор данных завершён!

📊 Тема: [topic]
📋 Записей: N из M источников
📁 Файлы:
  - report.md (аналитический отчёт)
  - data.csv / data.xlsx (данные)
  - dashboard.py / dashboard.html (дашборд)

🚀 Дашборд задеплоен: [URL]
```

## Scraping Error Handling (Root Cause Approach)

When a source is unavailable, do NOT just try another source. Systematically diagnose:

1. **Diagnose**: HTTP code? Timeout? Block? Empty response?
2. **Root cause**: robots.txt? Rate limit? JS-only? Geo-block? Auth required?
3. **Fix by cause**:
   - HTTP 404 → verify URL, try `firecrawl map` on domain, find alternative
   - Rate limit → increase pause, retry
   - JS-only → Firecrawl with `--wait-for 3000`
   - Geo-block → alternative source
   - Auth required → skip, note N/A
4. **Report to user** about problematic sources and decisions made

## Key Rules

- Numbers always include context (good/bad, above/below market average)
- Missing data → explicit N/A with explanation why
- Highlight anomalies and insights, don't just list facts
- Rate limiting: pause between requests, don't spam
- Use TodoWrite to track progress through all phases
- Use AskUserQuestion for all checkpoints — don't assume
