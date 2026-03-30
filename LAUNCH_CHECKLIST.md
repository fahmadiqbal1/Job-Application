# Launch Checklist — Pre-Production

Run through this checklist before your first job search to ensure everything is configured correctly.

## Part 1: Installation ✓

- [ ] Ran `install.bat` (Windows) or `bash install.sh` (Mac/Linux) without errors
- [ ] `.env` file created from `.env.example`
- [ ] `frontend/dist/` directory exists (React built successfully)
- [ ] Python venv activated: `which python` shows `.../venv/...`
- [ ] `python main.py` starts without crashing
- [ ] See "uvicorn running on 0.0.0.0:8000" in terminal

## Part 2: Configuration ✓

### Required Environment Variables
- [ ] `OPENAI_API_KEY` set and valid (test with `curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"`)
- [ ] `RESUME_PATH` points to an existing PDF resume file
- [ ] `TELEGRAM_BOT_TOKEN` (optional, but recommended) — test with `/start` in Telegram

### Optional Configuration
- [ ] `USER_NAME`, `USER_EMAIL`, `USER_PHONE` filled in (used in cover letters)
- [ ] SMTP credentials (for email notifications, leave blank to skip)
- [ ] `DAILY_SEARCH_KEYWORDS` (leave blank if not using daily scheduler)
- [ ] `DAILY_RUN_HOUR` (default 7 AM is fine)

### Model Selection (Optional)
- [ ] Leave defaults or select preferred models per agent
- [ ] Test model availability: Settings tab shows all available models

## Part 3: Web Dashboard Access ✓

- [ ] Open http://localhost:8000 in browser
- [ ] See 5 tabs: Dashboard, Approve Queue, Jobs, Activity, Settings
- [ ] All tabs load without JavaScript errors (check DevTools console)
- [ ] Refresh page — state persists (no loss of data)

## Part 4: WebSocket & Real-Time Updates ✓

- [ ] Open browser DevTools → Network → WS filter
- [ ] Click Dashboard tab
- [ ] You should see WebSocket connections to:
  - `ws://localhost:8000/api/ws/status`
  - `ws://localhost:8000/api/ws/browser`
- [ ] WebSocket status should be "101 Switching Protocols" (green)
- [ ] If red, refresh and check backend logs for errors

## Part 5: Settings Validation ✓

### In Settings Tab
- [ ] API Key shown as `***` (masked for security)
- [ ] Model selector shows available models (should be non-empty)
- [ ] Portal list shows 13 portals (Hiredly, JobStreet, etc)
- [ ] Resume path is visible and correct
- [ ] ATS threshold shows (default 90)

### Portal Health Check
- [ ] Click "Verify Selectors" in Settings
- [ ] Wait for results (may take 1-2 minutes)
- [ ] At least 5 portals should show green (healthy)
- [ ] Any red portals indicate selector update needed (OK — will be auto-discovered)

## Part 6: Telegram Integration (Optional) ✓

If you filled in `TELEGRAM_BOT_TOKEN`:
- [ ] Start a DM with your bot
- [ ] Type `/start`
- [ ] Bot responds with menu (shows it's working)
- [ ] Type `/status`
- [ ] Bot responds with "Pipeline idle" (no active run)

If Telegram doesn't work:
- [ ] Verify token is correct: `https://api.telegram.org/bot{token}/getMe` should return bot info
- [ ] Check internet connection (bot needs outbound HTTPS)
- [ ] Leaving it blank is fine — web dashboard works without it

## Part 7: Test Run — Dashboard ✓

### First Search
1. Dashboard tab
2. Type keywords (e.g., "Product Manager Malaysia")
3. Click **Start Search**
4. Verify:
   - [ ] Phase progress bar appears
   - [ ] Phase changes from "Scraping" → "ATS" → "Cover Letter" → "Apply" → "Done"
   - [ ] Activity tab shows live browser stream after ~10 seconds
   - [ ] Action log updates with timestamps

### Wait 10-15 minutes
- [ ] First job appears in JobsTab (within 5 min if scraper finds jobs)
- [ ] ATS scores appear next to jobs
- [ ] Cover letters generated and shown in Approve Queue

### Approve Queue Tab
- [ ] At least 1 job in "Pending" state
- [ ] ATS score badge visible
- [ ] Cover letter preview shown
- [ ] YES/SKIP buttons clickable
- [ ] Click YES on one job
- [ ] Job disappears from queue and appears as "Applied" in Jobs tab

## Part 8: Final Verification ✓

### Browser Tests
- [ ] All 5 tabs load without errors
- [ ] Tab switching is instant (context state preserved)
- [ ] Can scroll job list and side panel independently
- [ ] StatusBadge colors correct (applied=green, pending=blue, etc)
- [ ] ATSScore colors correct (90+=green, 70+=yellow, <70=red)
- [ ] Responsive layout works on 1920x1080 and smaller screens

### API Tests
```bash
# In another terminal with venv activated:

# Status
curl http://localhost:8000/api/status

# Models
curl http://localhost:8000/api/models

# Portals
curl http://localhost:8000/api/portals

# Health
curl http://localhost:8000/api/health
```

All should return JSON without 500 errors.

### Memory & Performance
- [ ] Browser DevTools → Performance: no JavaScript errors
- [ ] No network failures (red XS in DevTools)
- [ ] Backend terminal shows logs, no repeated error spam
- [ ] System responsive during 1-2 minute API calls (no UI freezing)

## Part 9: Data Persistence ✓

### After first run completes:
- [ ] `state/runs/` directory contains `.json` files (one per run)
- [ ] Jobs persist after refresh: reload page → same jobs shown
- [ ] File size: typical run = 50-200 KB

### Prompts
- [ ] `prompts.json` exists at project root
- [ ] Contains all cover letter, ATS, career prompts
- [ ] Settings → (Prompt Library in Phase 2) would let you edit them

## Part 10: Emergency Procedures ✓

### Stop an Active Run
- [ ] In Dashboard: click **Stop** button
- [ ] Or Telegram: `/stop`
- [ ] Or kill backend: Ctrl+C in terminal, then `python main.py` again

### Restart Backend
```bash
# Ctrl+C to stop
# Then:
python main.py
```
Data in `state/` persists across restarts.

### Clear All State (Fresh Start)
```bash
# Back up first!
cp state/ state.backup/

# Then clear
rm -rf state/runs/*
rm prompts.json  # Will be recreated with defaults on next run
```

## Part 11: Production Readiness Checklist ✓

- [ ] All test run steps passed
- [ ] No console errors in browser DevTools
- [ ] No repeated error spam in backend logs
- [ ] System stays alive for >10 minutes without crashes
- [ ] Can stop and restart without data loss
- [ ] Felt comfortable with 5 tabs and all features

### Before Leaving Unattended
- [ ] Set up daily scheduler: `DAILY_SEARCH_KEYWORDS` + `DAILY_RUN_HOUR` configured
- [ ] Set up Telegram alerts: `/status` and `/jobs` commands working
- [ ] SMTP configured: test email received (if using notifications)
- [ ] Read DEPLOYMENT.md: set up systemd/cron for 24/7 operation
- [ ] Backup strategy: periodic backups of `state/` directory

## Part 12: Known Limitations ✓

- [ ] Understand that **no system is 100% reliable**: portals redesign, Playwright selectors change
- [ ] Understand that **browser automation is slow**: expect 10-15 min per 10 jobs (intentional anti-bot behavior)
- [ ] Understand that **confirmation is required**: you must approve each application before it's submitted
- [ ] Understand that **resume edits are suggestions**: you should review before accepting edits
- [ ] Understand that **daily scheduler is timezone-aware**: set `DAILY_RUN_HOUR` to your local time hour (0-23)

## Part 13: Getting Help ✓

If something doesn't work:

1. Check README.md → Troubleshooting section
2. Check DEPLOYMENT.md → Troubleshooting section
3. Check browser DevTools console for JavaScript errors
4. Check backend terminal for Python exceptions
5. Verify `.env` has required keys filled (OPENAI_API_KEY at minimum)
6. Verify `RESUME_PATH` points to existing PDF
7. Verify internet connection (test curl/wget)
8. Try clearing browser cache and hard-refresh (Ctrl+Shift+R)

## Sign-Off ✓

System is **READY FOR PRODUCTION** once ALL items above are checked.

You can now:
- ✅ Run job searches from Dashboard
- ✅ Approve applications from Approve Queue
- ✅ Monitor progress in Activity tab
- ✅ Schedule daily automated searches (if configured)
- ✅ Use Telegram bot for status updates (if configured)

---

## Optional: Career Tools (Phase 2 TBD)

The following are POST-LAUNCH features not critical for core functionality:

- Resume Quality Analyzer
- LinkedIn Profile Optimizer
- Hiring Manager Finder
- LinkedIn Post Generator
- Interview Prep Generator

These can be enabled later via API or dashboard UI once ready.

---

**Ready to start your automated job search?**

1. Dashboard → Type keywords → Click **Start**
2. Wait 2-5 minutes for jobs to appear
3. Go to Approve Queue and review applications
4. Click **YES** to apply or **SKIP** to pass
5. Activity tab shows live browser view while applying
6. Telegram/email gets notified when run completes

Good luck! 🚀
