# Deployment Guide

This guide covers running the system in production (personal machine 24/7 or server).

## Pre-Deployment Checklist

- [ ] `.env` file has all required credentials (no placeholder values)
- [ ] `RESUME_PATH` points to an existing PDF resume
- [ ] Telegram bot token valid (test with `/start` command)
- [ ] SMTP credentials tested (send test email)
- [ ] All portal selectors verified: Settings → Health Check
- [ ] React frontend builds: `cd frontend && npm run build`
- [ ] System starts without errors: `python main.py`
- [ ] Web dashboard loads: http://localhost:8000
- [ ] WebSocket connects (check DevTools)

## Configuration for Continuous Running

### Environment Variables (.env)

**Critical:**
```
OPENAI_API_KEY=sk-...
RESUME_PATH=/path/to/resume.pdf
TELEGRAM_BOT_TOKEN=...
```

**Optional (defaults safe):**
```
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASS=
NOTIFICATION_EMAIL=
```

**Scheduler (for 7 AM daily runs):**
```
DAILY_SEARCH_KEYWORDS=Product Manager, AI Engineer
DAILY_RUN_HOUR=7
```

### Model Selection

Per-agent LLM choice (default: GPT-4o):
```
MODEL_SCRAPER=gpt-4o-mini         # fast, cheap
MODEL_ATS=gpt-4o                  # high quality
MODEL_COVER_LETTER=gpt-4o         # best writing
MODEL_APPLICATION=gpt-4o-mini     # fast form filling
MODEL_NOTIFIER=gpt-4o-mini        # summary emails
```

Cheaper alternative:
```
MODEL_SCRAPER=claude-3-5-haiku
MODEL_ATS=claude-3-5-sonnet       # still excellent
MODEL_COVER_LETTER=claude-3-5-sonnet
MODEL_APPLICATION=claude-3-5-haiku
MODEL_NOTIFIER=claude-3-5-haiku
```

## Running 24/7

### Option A: systemd (Linux/Mac)

Create `/etc/systemd/system/job-app.service`:
```ini
[Unit]
Description=Job Application Dashboard
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/Job Application
ExecStart=/path/to/Job Application/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable job-app
sudo systemctl start job-app
sudo systemctl status job-app
```

View logs:
```bash
sudo journalctl -u job-app -f
```

### Option B: Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task → "Job Application Dashboard"
3. Trigger: At startup (or daily at 7 AM for scheduled runs)
4. Action: Start a program
   - Program: `C:\path\to\Job Application\venv\Scripts\python.exe`
   - Arguments: `main.py`
   - Start in: `C:\path\to\Job Application`

### Option C: Docker (Optional)

If running on a server, Docker is recommended:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y chromium-browser
RUN playwright install chromium

EXPOSE 8000

CMD ["python", "main.py"]
```

Build and run:
```bash
docker build -t job-app .
docker run -d --name job-app \
  -e OPENAI_API_KEY=sk-... \
  -e TELEGRAM_BOT_TOKEN=... \
  -v /path/to/.env:/app/.env \
  -p 8000:8000 \
  job-app
```

## Monitoring

### Health Checks

Every 5 minutes, verify the system is alive:

```bash
curl http://localhost:8000/api/health
# Should return: {"status": "ok"}
```

Or via Telegram:
```
/status
# Shows current run phase or "idle"
```

### Logs

Backend logs printed to stdout:
- Watch in real-time: tail output from systemd/Docker
- Jobs saved to: `state/runs/<run_id>.json`
- Screenshots: `state/screenshots/` (if enabled)

### Resource Usage

- Memory: ~300-500 MB steady state, +100-200 MB during runs
- CPU: Idle most of time (spike during Playwright automation)
- Disk: ~10-50 MB per run (depends on screenshot count)
- Bandwidth: Minimal (API calls + WebSocket updates)

## Security

### .env Protection
- **Never** commit `.env` to git (in `.gitignore`)
- File contains API keys — restrict permissions:
  ```bash
  chmod 600 .env      # Linux/Mac
  ```
- On Windows: Right-click → Properties → Security → remove "Users" group

### API Keys
- Rotate keys every 3-6 months
- Use per-device keys if possible (OpenAI supports multiple keys)
- Monitor usage dashboard for unusual activity

### Network
- **Do NOT** expose port 8000 to the internet (unless behind HTTPS + auth)
- Use SSH tunnel if accessing from outside local network:
  ```bash
  ssh -L 8000:localhost:8000 user@server.com
  ```
- If exposing publicly, add reverse proxy (nginx):
  - Enable HTTPS
  - Add authentication
  - Rate limit `/api/search` to prevent abuse

## Troubleshooting

### System won't start
1. Check Python version: `python --version` (needs 3.11+)
2. Check venv activated: `which python` should show `.../venv/...`
3. Check requirements: `pip list | grep langchain` should show packages
4. Check .env: Ensure all required keys present
5. Check resume path: Ensure `RESUME_PATH` exists

### Telegram bot not responding
1. Verify token in `.env`: `TELEGRAM_BOT_TOKEN=...`
2. Token format: should start with digits, contain colon, not contain quotes
3. Test token: `curl https://api.telegram.org/bot{token}/getMe`
4. Check firewall: Bot needs outbound HTTPS to api.telegram.org

### Web dashboard 404
1. Verify React built: `ls frontend/dist/index.html` should exist
2. Rebuild if needed: `cd frontend && npm run build`
3. Restart backend: `python main.py`

### Playwright timeouts
1. Check portal still exists (not redesigned)
2. Manual selector verification in Settings
3. Portal may require login - manually log in once via browser
4. Check internet connection stability

### High memory usage
- Normal during apply phase (Playwright uses ~100-200 MB)
- Restart daily to clear accumulated state: `systemctl restart job-app`
- Reduce `max_jobs_per_run` in settings if running on low-memory device

## Backup & Recovery

### Daily Backups
```bash
# Cron job to backup state and prompts
0 2 * * * tar -czf /backup/job-app-$(date +\%Y\%m\%d).tar.gz /path/to/Job\ Application/state/ /path/to/Job\ Application/prompts.json
```

### Recovery
```bash
# Restore from backup
tar -xzf /backup/job-app-20260330.tar.gz -C /path/to/Job\ Application/
systemctl restart job-app
```

## Scaling (Advanced)

For multiple concurrent searches across multiple machines:
1. Shared state backend needed (Redis, PostgreSQL)
2. WebSocket broadcast to multiple clients
3. Browser session pooling (Playwright Grid)

Current system designed for single-machine, single-user operation.

---

Questions? Check README.md for architecture overview.
