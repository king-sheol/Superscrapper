---
name: superscrape
description: >
  Use when the user asks to collect data, scrape information, research a topic, compare options,
  find market data, gather statistics, build a comparison table, analyze competitors, monitor prices,
  or any variation of "собери данные", "найди информацию", "сравни", "исследуй рынок", "парсинг",
  "scrape", "research", "compare". Also triggers on requests like "сделай обзор", "найди лучшие",
  "покажи рейтинг", "проанализируй рынок". Do NOT trigger for simple web searches or single-page reads.
---

# Superscrape — Orchestrator

## CRITICAL RULES

| # | Rule |
|---|------|
| 1 | **Language**: ALWAYS respond in the user's CONVERSATION language, not the topic language. All output (plans, reports, questions, TodoWrite labels, dashboard UI) follows this rule. |
| 2 | **Firecrawl = CLI only via Bash**. NEVER use ToolSearch to find Firecrawl tools. Commands: `firecrawl search`, `firecrawl scrape`, `firecrawl map`, `firecrawl crawl`, `firecrawl agent`. |
| 3 | **BANNED tools**: Claude_in_Chrome, WebFetch, WebSearch, Chrome MCP, any browser/MCP browsing tool. Even on resume after rate limit. If Firecrawl credits exhausted, STOP and tell the user. |
| 4 | **Phase 5b** (dashboard choice) and **5e** (deploy) are MANDATORY. Never skip them. Never show final results before all Phase 5 substeps complete. |
| 5 | **Subagents REQUIRED**: scraper, report-writer, dashboard-generator, data-quality-reviewer, report-reviewer. Do NOT write reports or generate files directly in main context. |
| 6 | **Save `_state/`** after EVERY phase. A phase is NOT complete until its state file is written. |
| 7 | **NO final results** before Phase 6 verification completes. Evidence before assertions. |

## Resume Protocol

On "продолжай" / "continue" / any resume:

1. Search for `output/*/.superscrape-session.json`
2. If multiple found — sort by `created_at`, show list via AskUserQuestion, let user pick which session
3. If one found — check `version` field: if missing or < 3, it's a v2 session — ask user to start fresh or continue with limited compat
4. If resumable — read `_state/` files to determine last completed phase, re-init TodoWrite from that point
5. If not found or user chooses fresh — start from Phase 0

## Firecrawl CLI Reference

| Action | Command | Key flags |
|--------|---------|-----------|
| Search | `firecrawl search "query" -o file.json --json` | `--limit N`, `--scrape` |
| Scrape | `firecrawl scrape URL -o file.md` | `--wait-for 3000`, `--only-main-content` |
| Map | `firecrawl map URL --search "kw" -o urls.txt` | — |
| Crawl | `firecrawl crawl URL --wait --limit N -o file.json` | `--max-depth`, `--include-paths` |

## Phase Table

| Phase | File | Gate condition |
|-------|------|----------------|
| 0 | `phases/phase-0-onboarding.md` | firecrawl authenticated + python 3.8+ + credits.json saved |
| 1 | `phases/phase-1-clarify.md` | `_state/config.json` saved |
| 2 | `phases/phase-2-discover.md` | `_state/sources.json` saved + user confirmed |
| 3 | `phases/phase-3-collect.md` | `_state/raw_data_*.json` saved + user confirmed preview |
| 4 | `phases/phase-4-normalize.md` | `_state/normalized.json` saved + quality review Approved |
| 5a | `phases/phase-5a-report-and-data.md` | report.md + data.csv + data.xlsx exist |
| 5b | `phases/phase-5b-dashboard-choice.md` | `_state/dashboard_choice.json` saved |
| 5c | `phases/phase-5c-dashboard-generate.md` | Dashboard files exist (or choice=none) |
| 5d | `phases/phase-5d-review.md` | report-reviewer returned Approved |
| 5e | `phases/phase-5e-deploy.md` | Dashboard deployed (or user declined) |
| 6 | `phases/phase-6-verify.md` | All files verified + Phase 5 completion gate passed |

## Key State Files

| File | Created in | Purpose |
|------|-----------|---------|
| credits.json | Phase 0 | initial Firecrawl credit count |
| config.json | Phase 1 | topic, columns, scope |
| sources.json | Phase 2 | approved source list |
| normalized.json | Phase 4 | clean merged dataset |

## TodoWrite Init

At start, init TodoWrite with one item per phase from the Phase Table above (Phase 0 = in_progress, rest = pending). On resume, mark completed phases done and set next phase to in_progress.

## Dispatch Loop

For each phase: read the phase file, execute its instructions, verify the gate condition, mark TodoWrite complete, then read the next phase file. The orchestrator controls all transitions — phase files do NOT reference the next phase.

**Note**: When reading a phase file, substitute `{output_dir}` with the actual output directory path from session file or Phase 1 config.

## Output Directory Format

```
{cwd}/output/YYYY-MM-DD-{topic-slug}/
  _state/          # intermediate JSON files
  .firecrawl/      # raw Firecrawl outputs
  report.md
  data.csv
  data.xlsx
  dashboard.py / dashboard.html
```

---

Read `phases/phase-0-onboarding.md` and begin.
