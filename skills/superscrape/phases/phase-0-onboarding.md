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

### 2. Save Initial Credit Count

After successful authentication, parse the credits from `firecrawl --status` output and save:

```bash
mkdir -p {output_dir}/_state 2>/dev/null || true
firecrawl --status 2>&1 | python -c "
import sys, json, re
text = sys.stdin.read()
m = re.search(r'(\d+)\s*credits', text, re.IGNORECASE)
credits = int(m.group(1)) if m else 0
json.dump({'initial_credits': credits, 'recorded_at': '$(date -Iseconds)'}, open('{output_dir}/_state/credits.json', 'w'))
print(f'Saved {credits} credits')
"
```

**Note**: If output_dir is not yet known (topic not decided), store the credit count in memory and write credits.json when creating `_state/` in Phase 1.

### 3. Check Python

```bash
python --version
```

Need Python 3.8+. If missing or too old, tell the user to install Python.

Then ensure openpyxl is available:
```bash
pip install openpyxl
```

### 4. Do NOT create output directory

Output directory creation is deferred to Phase 1 after the topic is known.

## Save State

Write to `_state/credits.json`: `{ "initial_credits": N, "recorded_at": "ISO" }`
Update `.superscrape-session.json`: current_phase -> "phase-1"

## Next

Read `phases/phase-1-clarify.md` and continue.
