---
name: superscrape-dashboard
description: >
  Use when the user wants to regenerate or update a dashboard from existing data files (CSV/XLSX).
  Triggers on "пересоздай дашборд", "обнови дашборд", "regenerate dashboard", "new dashboard from data",
  or when the user has existing CSV/XLSX files and wants a visual dashboard without re-scraping.
---

# Superscrape Dashboard — Regenerate Dashboard from Existing Data

Create or recreate a Streamlit and/or HTML dashboard from existing CSV or XLSX data files.
Does NOT re-scrape sources — works with data already on disk.

## When to Use

- User has CSV/XLSX files from a previous superscrape run
- User wants to change dashboard type (switch from HTML to Streamlit or vice versa)
- User wants to update dashboard styling or chart types
- User wants to deploy an existing dashboard to VPS or GitHub Pages

## Workflow

### Step 1: Find Data Files

Look for data files in the current directory or ask the user:
- Check for `output/*/data.csv` or `output/*/data.xlsx`
- If not found, use AskUserQuestion: "Where are your data files? Provide the path to CSV or XLSX."

### Step 2: Analyze Data

Read the CSV/XLSX to understand:
- Column names and types (numeric, categorical, temporal)
- Number of records
- Topic (from filename or ask user)

### Step 3: Choose Dashboard Type

Use AskUserQuestion:
```
"Какой дашборд сгенерировать?"
├── Streamlit (для VPS)
├── HTML (для GitHub Pages)
├── Оба
```

### Step 4: Generate

Dispatch **dashboard-generator** subagent with:
- Data from the CSV/XLSX
- Dashboard type chosen by user
- Topic name

### Step 5: Deploy (if requested)

Follow the same deploy onboarding as the main superscrape skill:
- VPS: ask for SSH details, deploy automatically
- GitHub Pages: ask for repo name, deploy via gh CLI

### Step 6: Verify

Run verification checks on generated files.
Show the user evidence of successful generation.
