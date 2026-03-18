# Phase 0: Firecrawl & Python Onboarding

## Pre-check

None — this is the first phase.

## Instructions

### 1. Check Firecrawl CLI

```bash
firecrawl --status
```

Handle each case:

**"command not found"** — not installed:
```bash
npm install -g firecrawl-cli
```
If npm not found, tell the user to install Node.js first. Re-run `firecrawl --status` after install.

**"Not authenticated"** — installed but no API key:
1. Run `firecrawl login --browser` (opens browser for signup/login)
2. Tell the user to create an account or log in, then copy the API key
3. If browser login fails, instruct user to go to https://www.firecrawl.dev, sign up, copy API key, then run `firecrawl login -k <API_KEY>`
4. Verify with `firecrawl --status` — must show "Authenticated"

**"Authenticated"** — ready. Note the credits balance and concurrency limits from the output.

### 2. Check Python

```bash
python --version
```

Need Python 3.8+. If missing or too old, tell the user to install Python.

Then ensure openpyxl is available:
```bash
pip install openpyxl
```

### 3. Do NOT create output directory

Output directory creation is deferred to Phase 1 after the topic is known.

## Done

Both Firecrawl (authenticated) and Python (3.8+ with openpyxl) are confirmed ready.

Phase 0 complete.
