# Job Application Dashboard

Automated job search and application system combining resume optimization, ATS scoring, and intelligent form filling across 13+ job portals.

## Features

- **5-Tab Dashboard**: Real-time job search, approval queue, job details, live browser view, settings
- **13+ Job Portals**: Hiredly, JobStreet, JobsDB, Kalibrr, LinkedIn, Indeed, Glassdoor, Remotive, and more
- **ATS Optimization**: Resume scoring and natural keyword editing to improve job matching (no stuffing)
- **Smart Automation**: Human-like form filling with personalized cover letters
- **Dual Interface**: Both Telegram bot and web dashboard access same backend state
- **Real-Time Feedback**: Live browser stream (1 FPS), action log, phase progress tracking
- **Career Tools**: Resume quality analyzer, LinkedIn optimizer, hiring manager finder, post generator
- **Daily Scheduling**: Automated daily job searches at configurable time (default 7 AM)

## Quick Start

### Windows
```bash
install.bat
# Edit .env with your API keys, then:
venv\Scripts\activate
python main.py
# Open http://localhost:8000
```

### Mac/Linux
```bash
bash install.sh
# Edit .env with your API keys, then:
source venv/bin/activate
python main.py
# Open http://localhost:8000
```

## Configuration

Copy `.env.example` to `.env` and fill in:

**Required:**
- `OPENAI_API_KEY`: For GPT-4o and cover letters
- `TELEGRAM_BOT_TOKEN`: For Telegram bot (optional, leave blank to skip)
- `RESUME_PATH`: Path to your PDF resume

**Optional:**
- `ANTHROPIC_API_KEY`: For Claude models
- `GOOGLE_API_KEY`: For Gemini models
- SMTP credentials for email notifications
- Portal-specific credentials (autofill if you log in manually on portals)

## Architecture

```
http://localhost:8000  ← React dashboard (5 tabs)
          ↓
     FastAPI REST API (23 routes)
    WebSocket streams (status, screenshots)
          ↓
    Orchestrator Pipeline (5 phases)
    ├─ Phase 1: Universal Scraper (13 portals)
    ├─ Phase 2: ATS Agent (PageIndex RAG scoring)
    ├─ Phase 3: Cover Letter Agent (humanized)
    ├─ Phase 4: Application Agent (form filling)
    └─ Phase 5: Notifier (Telegram + email)
          ↓
    BrowserSession (Playwright, screenshot streaming)
          ↓
Telegram Bot (daemon, shared state)
```

All state persisted to `state/runs/*.json`
All prompts loaded from `prompts.json` (user-editable)
All settings loaded from `.env`

## Usage

### Dashboard Tab
- Enter job search keywords (min 3 characters)
- Click **Start Search** to launch 5-phase pipeline
- Watch phase progress in real-time
- Click **Stop** to cancel current run

### Approve Queue Tab
- Jobs awaiting your approval appear here
- Shows ATS score and missing keywords
- Preview cover letter before applying
- **YES** to apply, **SKIP** to pass

### Jobs Tab
- Grid of all jobs from latest run
- Filter by status: All, Applied, Pending, Skipped, Failed
- Click any card to see full details
- Copy tailored resume for manual applications

### Activity Tab
- **Left 60%**: Live browser stream (1 FPS JPEG)
  - Current URL display
  - Current action description
- **Right 40%**: Action log with timestamps

### Settings Tab
- API key management (reveal/hide)
- Per-agent model selection (GPT-4o, Claude, Gemini)
- Resume path and ATS threshold
- Portal health check

## API Endpoints

### Status & Control
- `GET /api/status` — current run info + pending confirmations
- `POST /api/search` — start pipeline with keywords
- `POST /api/stop` — stop active run

### Jobs & Confirmations
- `GET /api/jobs` — all jobs from latest run
- `GET /api/jobs/{id}` — job detail with cover letter, ATS, resume edits
- `GET /api/confirm/pending` — enriched list of pending approvals
- `POST /api/confirm/{id}` — record YES/SKIP decision

### Settings & Configuration
- `GET /api/settings` — current settings (secrets masked)
- `GET /api/models` — available LLM models and agents
- `GET /api/portals` — all configured portals

### Career Tools
- `POST /api/career/resume/analyze` — generic check + quality scores
- `POST /api/career/resume/interview-bullet` — step-by-step context extraction
- `POST /api/career/linkedin/optimize` — rewrite profile per goal
- `POST /api/career/hiring-managers` — search for hiring manager posts
- `POST /api/career/linkedin/post` — generate 3 post options

### WebSocket
- `/api/ws/status` — pipeline events (phase_start, job_found, ats_score, etc)
- `/api/ws/browser` — screenshot stream (1 FPS) + selector health checks

## Troubleshooting

### "Frontend not built"
```bash
cd frontend && npm run build && cd ..
```

### Playwright selector failures
- Settings → Health Check → Verify Selectors
- If portal redesigned, selectors may need updating
- System attempts LLM discovery if selectors fail

### WebSocket disconnects
- Check browser DevTools → Network → WS
- Verify backend is running: `python main.py` shows "uvicorn running on 0.0.0.0:8000"
- Auto-reconnect should kick in (1s → 2s → 4s → 30s backoff)

### API errors
- Check `.env` has all required keys filled
- Verify resume file exists at `RESUME_PATH`
- Check backend logs in terminal running `python main.py`

## Advanced

### Custom Portals
1. Settings → Portals → Add Custom Portal
2. Paste job listing URL
3. Click "Auto-detect" → system uses GPT-4o to discover selectors
4. Selectors cached in `config/portal_cache.json` for future runs

### Prompt Editing
- All AI prompts stored in `prompts.json` (auto-created on first run)
- Edit directly in Settings → Prompt Library (Phase 2 TBD)
- Changes apply to next run immediately
- Reset to defaults available via API: `POST /api/prompts/reset`

### Multi-Model Support
Select different LLM provider per agent:
- Scraper: `gpt-4o-mini` (fast, cheap) or Claude Haiku
- ATS: `gpt-4o` (best quality) or Claude Sonnet
- Cover Letters: `gpt-4o` or Claude Opus
- Application: `gpt-4o-mini` (fast form filling)

## Architecture Decisions

### Shared State Pattern
Telegram bot + web API both access same Python objects in `state/`:
- `state.confirmation` — YES/SKIP decisions (accessible from both interfaces)
- `state.run_status` — active run tracking
- `state.storage` — file-based JSON persistence

### Universal Scraper
Routes intelligently:
1. Known portal (hardcoded selectors) → 100% reliable
2. Cached domain → previously discovered selectors
3. Unknown → LLM discovery (GPT-4o inspects HTML once, result cached)

### ATS Optimization
Resume is **never** touched until user approves edits:
1. Original resume indexed via PageIndex
2. Each JD is indexed
3. Resume scored vs JD (0-100)
4. Missing keywords identified
5. LLM suggests natural rewrites
6. User sees diff in Activity tab
7. User approves in Approve Queue → tailored copy created
8. Tailored copy used for that specific job only

### Event-Driven UI
5-phase pipeline broadcasts WebSocket events:
- `phase_start` → PhaseProgress advances
- `job_found` → JobCard appears in grid
- `ats_score` → Badge updates in real-time
- `confirmation_request` → Auto-switches to ApproveQueue tab
- `job_applied` → StatusBadge changes to "Applied"

## Performance

Typical run (10 job listings):
- Scrape: 2-5 min (browser automation is slow, intentional for anti-bot)
- ATS: 2-3 min (PageIndex indexing + LLM scoring)
- Cover Letters: 1-2 min (LLM generation)
- Applications: 3-5 min (form filling with human-like pauses)
- **Total**: ~10-15 minutes per run

Browser consumes ~200-300 MB RAM. System runs comfortably on modern laptops.

## License

Private project. See individual LLM provider ToS for commercial use.

## Support

- Check logs: tail -f `state/runs/<run_id>.json`
- Telegram: `/status`, `/jobs`, `/stop` commands
- Dashboard: All functionality mirrored via web UI
- For issues: Check browser console (F12) and backend logs

---

**Built with**: LangGraph, Playwright, FastAPI, React 18, Tailwind CSS, PageIndex RAG
