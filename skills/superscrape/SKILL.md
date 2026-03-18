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

1. **Language**: ALWAYS respond in the same language the user used. If the user writes in Russian — ALL output (plans, reports, questions, checkpoints, TodoWrite labels, dashboard UI) must be in Russian. If in English — in English. This is non-negotiable.

2. **Firecrawl is a CLI tool, NOT an MCP tool**: Do NOT use ToolSearch to find Firecrawl tools. Do NOT look for MCP tools. Firecrawl is invoked ONLY via `Bash` tool with CLI commands like `firecrawl search`, `firecrawl scrape`, etc. See the CLI Reference table below.

3. **NEVER use browser automation**: Do NOT use Claude_in_Chrome, WebFetch, WebSearch, or any browser/MCP browsing tools for data collection. ALL web access must go through Firecrawl CLI. Browser tools cause silent freezes and are unreliable for scraping. The ONLY exception is `gh` CLI for GitHub operations in Phase 5d.

4. **NEVER skip deploy onboarding (Phase 5d)**: After generating a dashboard, you MUST ask the user where to deploy it and execute the deployment. Do NOT just show files and stop.

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

Follow these 6 phases strictly.

**At the very start**, initialize TodoWrite with all phases:
```
TodoWrite:
0. [in_progress] Phase 0: Firecrawl & Python onboarding check
1. [pending] Phase 1: Accept task & clarify columns
2. [pending] Phase 2: Discover sources
3. [pending] Phase 3: Collect data
4. [pending] Phase 4: Normalize & validate
5. [pending] Phase 5: Generate output (report + dashboard + deploy)
6. [pending] Phase 6: Verify & present results
```
Update TodoWrite as you progress through each phase.

## Output Directory

All generated files go into a dated subdirectory:
```
{current-working-directory}/output/YYYY-MM-DD-{topic-slug}/
```
Where `{topic-slug}` is the topic in lowercase with spaces replaced by hyphens (e.g., `crm-systems`).

Create this directory at the start of Phase 5 before any file generation.

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

### Phase 3: Data Collection (up to 5 scraper agents in parallel)

For each approved source, dispatch a **scraper** subagent (see agents/scraper.md):
- Each agent works with ONE source
- Uses Firecrawl CLI (search, scrape, map, agent)
- If a public API was found — use it preferentially via fetch
- Returns structured data matching the agreed column list

**Rate limiting**: instruct agents to pause between requests.

**Error handling** (Root Cause approach):
- If source is blocked: diagnose (HTTP code? timeout? rate limit? geo-block?)
- Rate limit → increase pause, retry
- JS-only rendering → use Firecrawl with JS rendering
- Geo-block → find alternative source
- No data → mark N/A with explanation
- Report all issues to the user

**Checkpoint**: After collection, show a preview:
```
"Собрал N записей из M источников. Вот первые 5:"
| Name | Price | Rating | Source | Date |
| ...  | ...   | ...    | ...    | ...  |
"Колонки верные? Данные выглядят правильно?"
```

### Phase 4: Normalize & Validate (sequential, orchestrator)

This phase runs in the main context (not subagents) because it needs the full picture.

1. **Merge** data from all scraper agents into a single dataset

2. **Defense-in-depth validation (4 layers)**:
   - Layer 1 (format): data types, encodings, units of measurement
   - Layer 2 (duplicates): deduplication by key fields
   - Layer 3 (ranges): numbers within reasonable bounds, dates valid
   - Layer 4 (cross-check): data from different sources consistent?

3. **Fill gaps**: mark missing data as N/A with explanation

4. **Dispatch data-quality-reviewer subagent** (see agents/data-quality-reviewer.md):
   - Check completeness, consistency, anomalies
   - If Issues Found → fix and re-dispatch (max 3 iterations)

5. **Analyze**:
   - Identify leaders and why
   - Find patterns across data
   - Flag anomalies and outliers
   - Compare with market benchmarks where possible

6. **Assign confidence levels** to each source: High / Medium / Low with justification

### Phase 5: Generate Output

**CRITICAL: Phase 5 has 5 mandatory substeps (5a→5b→5c→5d→5e). Do NOT skip any. Do NOT show final results until ALL substeps are done.**

When entering Phase 5, update TodoWrite to track each substep:
```
TodoWrite:
- [in_progress] 5a: Generate report + data files
- [pending] 5b: Ask user about dashboard choice
- [pending] 5c: Generate chosen dashboard(s)
- [pending] 5d: Deploy dashboard (if chosen)
- [pending] 5e: Review report quality
```

**5a: Report + Data (always, in parallel)**

First, create the output directory:
```bash
mkdir -p output/YYYY-MM-DD-{topic-slug}/
```

Then dispatch two agents simultaneously with this context:

**Metadata to pass to BOTH agents:**
- `topic`: research topic (string)
- `date`: collection date (YYYY-MM-DD)
- `output_dir`: path to output directory
- `headers`: list of column names
- `data`: normalized dataset (all rows)
- `sources`: list of {url, reliability, justification} objects
- `analysis`: {leaders, patterns, anomalies, market_context} from Phase 4
- `confidence_map`: list of {source, level, reason} objects

**Agents:**
- **report-writer** subagent → `{output_dir}/report.md` (see agents/report-writer.md)
- **dashboard-generator** subagent → `{output_dir}/data.csv` + `{output_dir}/data.xlsx` (see agents/dashboard-generator.md)

Use the report format from `references/report-format.md`.
Use XLSX generation instructions from `references/xlsx-generator.md`.

**5b: Dashboard Choice (MANDATORY — do NOT skip this step)**

Immediately after 5a completes, you MUST ask the user about dashboards. Do NOT present final results yet.

Use AskUserQuestion:
```
"Отчёт и данные готовы. Какой дашборд сгенерировать?"
├── Streamlit (для VPS) — интерактивный, с фильтрами и графиками (Recommended)
├── HTML (для GitHub Pages) — статический, быстрая загрузка
├── Оба варианта
└── Без дашборда — только отчёт и Excel
```

If user chooses "Без дашборда", skip 5c and 5d and go directly to 5e.

**5c: Generate chosen dashboard(s)**

Based on user choice, dispatch dashboard-generator subagent(s):
- Streamlit → dashboard.py + Dockerfile + docker-compose.yml + nginx.conf + requirements.txt
- HTML → dashboard.html (self-contained with embedded data)
- Both → two agents in parallel

Use dashboard templates from `references/dashboard-template.md`.

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

**5e: Report Review**

Dispatch **report-reviewer** subagent (see agents/report-reviewer.md):
- Check all sections present
- Numbers have context (good/bad, above/below market)
- Insights are specific, not generic
- If Issues Found → fix and re-dispatch (max 3 iterations)

### Phase 6: Verification Before Completion

**Evidence over claims** — verify every output:

- [ ] report.md exists and is not empty
- [ ] data.csv parses without errors: `python -c "import csv; r=csv.reader(open('data.csv')); print(f'{sum(1 for _ in r)-1} rows')"`
- [ ] data.xlsx is valid: `python -c "import openpyxl; wb=openpyxl.load_workbook('data.xlsx'); print(f'{wb.sheetnames}')"`
- [ ] dashboard.py syntax check: `python -c "import ast; ast.parse(open('dashboard.py').read()); print('OK')"`
- [ ] requirements.txt has all dependencies
- [ ] docker-compose.yml is valid YAML

**Show evidence to user**: first 3 rows of table + file list with sizes.

**Final summary in chat**:
```
✅ Сбор данных завершён!

📊 Тема: [topic]
📋 Записей: N из M источников
📁 Файлы:
  - report.md (аналитический отчёт)
  - data.csv / data.xlsx (данные)
  - dashboard.py (Streamlit-дашборд)

🚀 Запуск дашборда: streamlit run output/YYYY-MM-DD-topic/dashboard.py
🌐 Дашборд задеплоен: [URL if deployed]
```

## Scraping Error Handling (Root Cause Approach)

When a source is unavailable, do NOT just try another source. Systematically diagnose:

1. **Diagnose**: HTTP code? Timeout? Block? Empty response?
2. **Root cause**: robots.txt? Rate limit? JS-only? Geo-block? Auth required?
3. **Fix by cause**:
   - Rate limit → increase pause, retry
   - JS-only → Firecrawl with JS rendering
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
