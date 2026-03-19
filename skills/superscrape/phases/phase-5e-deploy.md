# Phase 5e: Deploy Dashboard (MANDATORY)

**This phase is MANDATORY. Do not skip.**

## Pre-check

```bash
test -f {output_dir}/_state/phase5d_done.json && echo "GATE OK" || echo "GATE FAIL"
```

If GATE FAIL — return to previous phase.

## Instructions

### If choice = "none"

No deployment needed. Mark phase complete and proceed.

### If choice = "streamlit" or "both" — Deploy to VPS

### VPS Deploy Flow

**Step 0: Check for deprecated config**
```bash
cat ~/.superscrape-servers.json 2>/dev/null
```
If found → read VPS config, migrate to `~/.claude/superscraper.local.md`, warn:
"Migrated VPS config from deprecated ~/.superscrape-servers.json to ~/.claude/superscraper.local.md"

**Step 1: Read local config**
```bash
cat ~/.claude/superscraper.local.md 2>/dev/null
```
Parse YAML frontmatter for `vps_host`, `vps_user`, `ssh_key_configured`.

**Step 2: If configured → deploy automatically**
If has `vps_host` AND `ssh_key_configured: true`:
```bash
scp {output_dir}/dashboard.py {output_dir}/data.csv {output_dir}/requirements.txt {vps_user}@{vps_host}:/opt/streamlit-app/
ssh {vps_user}@{vps_host} "cd /opt/streamlit-app && source venv/bin/activate && pip install -q -r requirements.txt && cp dashboard.py app.py && systemctl restart streamlit"
```
Verify: `ssh {vps_user}@{vps_host} "systemctl is-active streamlit"` → should return "active"

**Step 3: If NOT configured → onboard**
a. AskUserQuestion: "VPS IP и SSH user? (например root@1.2.3.4)"
b. Check SSH key: `ls ~/.ssh/id_ed25519.pub 2>/dev/null`
c. If no key: `ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N ""`
d. Tell user: "Выполни эту команду в PowerShell:"
   `type C:\Users\{username}\.ssh\id_ed25519.pub | ssh {user}@{ip} "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"`
   "Введи пароль сервера когда попросит. После этого скажи 'готово'."
e. Wait for user confirmation
f. Verify: `ssh -o BatchMode=yes -o StrictHostKeyChecking=no {user}@{ip} "echo ok"` → should output "ok"
g. Save to `~/.claude/superscraper.local.md`:
```yaml
---
vps_host: "{ip}"
vps_user: "{user}"
ssh_key_configured: true
---
```
h. Proceed with Step 2 (deploy)

### If choice = "html" or "both" — Deploy to GitHub Pages

1. **Ask for deployment info** via AskUserQuestion:
   - Create new repository or use existing?
   - Repository name (suggest: `dashboard-{topic-slug}`)
   - Public or Private?

2. **Deploy**:
   ```bash
   gh repo create {repo-name} --public --clone
   cp {output_dir}/dashboard.html {repo-name}/index.html
   cd {repo-name} && git add . && git commit -m "Deploy dashboard" && git push
   gh api repos/{owner}/{repo}/pages -X POST -f source.branch=main -f source.path=/
   ```

3. **Wait for build**: Poll `gh api repos/{owner}/{repo}/pages/builds` until status is "built".

4. **Verify**: Show the live GitHub Pages URL to the user.

5. **Fallback** if gh CLI not authorized: suggest `gh auth login` or provide manual instructions.

### If choice = "both"

Deploy both sequentially: VPS first, then GitHub Pages.

## Save State

Write to `_state/phase5e_done.json`: `{ "deployed": true, "deploy_urls": [...] }` (or `{ "deployed": false, "reason": "user declined" }`)
Update `.superscrape-session.json`: current_phase -> "phase-6"

## Next

Read `phases/phase-6-verify.md` and continue.
