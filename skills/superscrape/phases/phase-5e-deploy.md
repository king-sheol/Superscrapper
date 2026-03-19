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

#### VPS Deploy — SSH Onboarding (one-time)

Before first deploy, check SSH access:

1. Check for existing SSH key:
```bash
test -f ~/.ssh/id_rsa.pub && echo "KEY EXISTS" || echo "NO KEY"
```

2. If NO KEY — generate one:
```bash
ssh-keygen -t rsa -b 4096 -N "" -f ~/.ssh/id_rsa
```

3. Check for saved server config:
```bash
cat ~/.superscrape-servers.json 2>/dev/null || echo "NO CONFIG"
```

4. If NO CONFIG — ask user for server details via AskUserQuestion:
   - IP address
   - SSH user (default: root)
   - SSH port (default: 22)

5. Test SSH key auth:
```bash
ssh -o BatchMode=yes -o ConnectTimeout=5 user@IP "echo ok" 2>/dev/null
```

6. If key auth fails — show user the public key and ask them to add it:
   ```
   ssh-copy-id user@IP
   ```

7. After key is confirmed working, save config:
```json
{
  "default": {
    "ip": "...",
    "user": "root",
    "port": 22,
    "app_dir": "/opt/streamlit-app",
    "key_configured": true
  }
}
```

#### VPS Deploy — Automatic (after onboarding)

Once SSH key is configured, deploy is fully automatic:
```bash
scp -o BatchMode=yes dashboard.py data.csv requirements.txt user@IP:/opt/streamlit-app/
ssh -o BatchMode=yes user@IP "cd /opt/streamlit-app && cp dashboard.py app.py && source venv/bin/activate && pip install -q streamlit-echarts streamlit-aggrid 2>/dev/null && systemctl restart streamlit"
```

Verify: `ssh -o BatchMode=yes user@IP "systemctl is-active streamlit"`
If active — deploy success. Show URL: http://IP:8501

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
