# Phase 5e: Deploy Dashboard (MANDATORY)

## Pre-check

No file gate — the orchestrator verifies that Phase 5d (report-reviewer VERDICT: Approved) is in completed_phases before dispatching this phase. If not, go back to Phase 5d.

## Instructions

### If choice = "none"

No deployment needed. Mark phase complete and proceed.

### If choice = "streamlit" or "both" — Deploy to VPS

1. **Ask for deployment info** via AskUserQuestion:
   - IP/hostname of the server
   - SSH user
   - Is Docker installed? (Yes / No / Don't know)
   - Domain for the dashboard (optional)

2. **Deploy**:
   ```bash
   scp -r {output_dir}/dashboard.py {output_dir}/Dockerfile {output_dir}/docker-compose.yml {output_dir}/nginx.conf {output_dir}/requirements.txt {output_dir}/data.csv user@host:/opt/dashboard/
   ssh user@host "cd /opt/dashboard && docker compose up -d"
   ```

3. **Configure nginx** if domain provided:
   ```bash
   ssh user@host "nginx -t && systemctl reload nginx"
   ```

4. **Verify**: `curl -s -o /dev/null -w "%{http_code}" http://host:8501` — must return 200.

5. **Fallback** if no SSH access: generate `deploy.sh` script with all commands and provide instructions.

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

Update `.superscrape-session.json` — add "5e" to completed_phases.

## Done

Dashboard deployed (or skipped if choice=none).

Phase 5e complete.
