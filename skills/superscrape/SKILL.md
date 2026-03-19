---
name: superscrape
description: >
  Use when the user asks to collect data, scrape information, research a topic, compare options,
  find market data, gather statistics, build a comparison table, analyze competitors, monitor prices,
  or any variation of "собери данные", "найди информацию", "сравни", "исследуй рынок", "парсинг",
  "scrape", "research", "compare". Also triggers on requests like "сделай обзор", "найди лучшие",
  "покажи рейтинг", "проанализируй рынок". Do NOT trigger for simple web searches or single-page reads.
---

# Superscrape v4 — Orchestrator

## CRITICAL RULES

| # | Rule |
|---|------|
| 1 | Language = user's language |
| 2 | Firecrawl = CLI only via Bash, never ToolSearch |
| 3 | FORBIDDEN: browser tools, WebFetch, WebSearch, Chrome MCP. EXCEPTION: dashboard-auditor may use preview tools (preview_start, preview_screenshot) for visual verification only. |
| 4 | Phase 5b (dashboard choice) and 5e (deploy) = MANDATORY |
| 5 | Subagents REQUIRED: scraper, dashboard-designer, reviewers |
| 6 | Save `_state/` after EVERY phase |
| 7 | NO final results until Phase 6 |
| 8 | Python open() ALWAYS with encoding='utf-8'. CSV with encoding='utf-8-sig'. No exceptions. |

## Resume Protocol

1. Check `.superscrape-session.json` in CWD, then in `output/*/`
2. If found: read `current_phase`, load corresponding phase file from `phases/`
3. If not found: new session, start Phase 0
4. If `version` field < 4: warn "Old session format (v{version}), recommend restart"
5. If multiple sessions found: show list via AskUserQuestion, let user pick

## Phase Table

| Phase | File | Gate |
|-------|------|------|
| 0 | `phases/phase-0-onboarding.md` | firecrawl OK |
| 1 | `phases/phase-1-clarify.md` | `_state/config.json` |
| 2 | `phases/phase-2-discover.md` | `_state/sources.json` |
| 3 | `phases/phase-3-collect.md` | >= 1 `raw_data_*.json` |
| 4 | `phases/phase-4-normalize.md` | `normalized.json` + quality_review: Approved |
| 5a | `phases/phase-5a-report-and-data.md` | `report.md` + `data.csv` + `data.xlsx` |
| 5b | `phases/phase-5b-dashboard-choice.md` | `_state/dashboard_choice.json` |
| 5c | `phases/phase-5c-dashboard-generate.md` | dashboard file(s) exist |
| 5d | `phases/phase-5d-review.md` | report-reviewer VERDICT: Approved |
| 5e | `phases/phase-5e-deploy.md` | deploy done or declined |
| 6 | `phases/phase-6-verify.md` | all checks passed |

## TodoWrite Init

```
Phase 0: Firecrawl & Python onboarding
Phase 1: Accept task & clarify columns
Phase 2: Discover sources
Phase 3: Collect data
Phase 4: Normalize & validate
Phase 5a: Generate report & data files
Phase 5b: Dashboard choice (MANDATORY)
Phase 5c: Generate dashboard
Phase 5d: Report review
Phase 5e: Deploy dashboard (MANDATORY)
Phase 6: Verify & present results
```

Set Phase 0 = in_progress, rest = pending. On resume, mark completed phases done.

## Output Directory

Format: `{cwd}/output/YYYY-MM-DD-{topic-slug}/`

```
output/YYYY-MM-DD-{topic-slug}/
  _state/           # intermediate JSON files
  .firecrawl/       # raw Firecrawl outputs
  .superscrape-session.json
  report.md
  data.csv
  data.xlsx
  dashboard.py / dashboard.html
```

## Session File Format

```json
{
  "version": 4,
  "output_dir": "output/YYYY-MM-DD-{topic-slug}",
  "topic": "...",
  "language": "...",
  "complexity": "SIMPLE|MEDIUM|COMPLEX",
  "current_phase": "phase-0",
  "completed_phases": [],
  "created_at": "ISO timestamp"
}
```

## Dispatch Loop

For each phase: read the phase file, execute, verify gate, mark TodoWrite complete, read next phase file. Substitute `{output_dir}` with actual path. Phase files do NOT reference the next phase -- the orchestrator controls all transitions.

---

Read `phases/phase-0-onboarding.md` and begin.
