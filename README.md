<div align="center">

# 💼 Job Application Dashboard

### An Intelligent Automated Job Search & Application System

*13+ Job Portals · ATS Optimization · AI Cover Letters · Real-Time Browser Stream*

<br>

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-latest-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![Playwright](https://img.shields.io/badge/Playwright-latest-45ba4b?style=flat-square&logo=playwright&logoColor=white)](https://playwright.dev)
[![License](https://img.shields.io/badge/License-Private-6B7280?style=flat-square)](#license)

<br>

> A 5-phase AI pipeline that scrapes 13+ job portals, scores your resume against each job description, generates humanized cover letters, fills application forms with human-like pauses, and notifies you via Telegram — all controllable from a 5-tab React dashboard.

<br>

[Quick Start](#-quick-start) · [Pipeline](#-5-phase-pipeline) · [Dashboard](#-dashboard-tabs) · [ATS Engine](#-ats-optimization) · [Architecture](#-architecture)

</div>

---

<br>

## ✨ Features

<br>

| | Feature | Description |
|---|---|---|
| 🔍 | **Universal Scraper** | 13+ portals with hardcoded selectors + LLM auto-discovery for unknown sites |
| 📊 | **ATS Scoring** | PageIndex RAG scores your resume against each JD (0–100) |
| ✍️ | **Cover Letter AI** | Humanized, job-specific cover letters per application |
| 🤖 | **Form Filling** | Playwright-driven human-like form completion with configurable pauses |
| 👁️ | **Live Browser Stream** | 1 FPS JPEG screenshot stream of the browser during automation |
| ✅ | **Approval Queue** | Review ATS score + cover letter draft before each application fires |
| 📲 | **Telegram Bot** | Full pipeline control and job updates via `/status`, `/jobs`, `/stop` |
| ⏰ | **Daily Scheduling** | Automated daily search at configurable time (default 7 AM) |
| 🛠️ | **Career Tools** | Resume analyzer · LinkedIn optimizer · Hiring manager finder · Post generator |
| 🔀 | **Multi-Model** | Per-agent model selection — GPT-4o · Claude · Gemini |

<br>

---

<br>

## 🔄 5-Phase Pipeline

<br>

```
User enters keywords → Start Search
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 1 — SCRAPE                                           │
│  Universal Scraper hits 13+ portals                         │
│  Known portal → hardcoded selectors (100% reliable)         │
│  Cached domain → previously discovered selectors            │
│  Unknown site → GPT-4o inspects HTML once, result cached    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 2 — ATS SCORE                                        │
│  PageIndex indexes resume + each JD                         │
│  Scores resume vs JD (0–100)                                │
│  Identifies missing keywords                                │
│  LLM suggests natural rewrites (no stuffing)                │
│  Resume untouched until user approves edits                 │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 3 — COVER LETTER                                     │
│  Humanized, job-specific letter generated per application   │
│  User previews before any application fires                 │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 4 — APPLY                                            │
│  Playwright fills forms with human-like pauses              │
│  Uses tailored resume copy for that specific job only       │
│  Fires only after user approval in the queue                │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 5 — NOTIFY                                           │
│  Telegram message + email on each outcome                   │
│  Dashboard badges update in real-time via WebSocket         │
└─────────────────────────────────────────────────────────────┘
```

**Typical run time for 10 listings:** ~10–15 minutes *(intentional — human-like pacing avoids bot detection)*

<br>

---

<br>

## 🖥️ Dashboard Tabs

<br>

### Tab 1 — Search

- Enter keywords (min 3 characters)
- Click **Start Search** to launch the pipeline
- Phase progress bar advances in real-time
- **Stop** cancels the active run

### Tab 2 — Approve Queue

- Jobs awaiting your decision appear here
- Shows ATS score and flagged missing keywords
- Preview cover letter before committing
- **YES** to apply · **SKIP** to pass

### Tab 3 — Jobs

- Grid of all jobs from the latest run
- Filter by status: All · Applied · Pending · Skipped · Failed
- Click any card for full details + tailored resume copy

### Tab 4 — Activity

| Panel | Content |
|---|---|
| **Left 60%** | Live browser stream (1 FPS JPEG) · current URL · current action |
| **Right 40%** | Timestamped action log |

### Tab 5 — Settings

- API key management (reveal / hide)
- Per-agent model selection (GPT-4o · Claude · Gemini)
- Resume path and ATS threshold
- Portal health check — verify selectors are live

<br>

---

<br>

## 📊 ATS Optimization

<br>

The resume is **never modified** until you explicitly approve edits:

```
Original resume indexed via PageIndex
          │
          ▼
Each JD indexed separately
          │
          ▼
Resume scored vs JD (0–100)
          │
          ▼
Missing keywords identified
          │
          ▼
LLM suggests natural rewrites (no keyword stuffing)
          │
          ▼
User reviews diff in Activity tab
          │
          ▼
User approves in Approve Queue
          │
          ▼
Tailored copy created — used for that job only
Original resume never touched
```

<br>

---

<br>

## 🏗️ Architecture

<br>

### System Overview

```
http://localhost:8000
       │
       ▼
React Dashboard (5 tabs)
       │
       ▼
FastAPI REST API (23 routes)
WebSocket streams: /api/ws/status · /api/ws/browser
       │
       ▼
Orchestrator Pipeline (5 phases)
       │
       ▼
BrowserSession (Playwright)
  + Screenshot streaming (1 FPS)
       │
       ▼
Telegram Bot (daemon — shared state)
```

<br>

### State Architecture

All state persisted to `state/runs/*.json`:

| Object | Shared by |
|---|---|
| `state.confirmation` | Web API + Telegram bot (YES/SKIP decisions) |
| `state.run_status` | Active run tracking across both interfaces |
| `state.storage` | File-based JSON persistence |

<br>

### Event-Driven UI

WebSocket events drive real-time UI updates:

| Event | UI Effect |
|---|---|
| `phase_start` | PhaseProgress bar advances |
| `job_found` | New JobCard appears in grid |
| `ats_score` | Score badge updates in real-time |
| `confirmation_request` | Auto-switches to Approve Queue tab |
| `job_applied` | StatusBadge changes to "Applied" |

<br>

---

<br>

## 🚀 Quick Start

<br>

### Windows

```bat
install.bat
REM Edit .env with your API keys, then:
venv\Scripts\activate
python main.py
REM Open http://localhost:8000
```

### Mac / Linux

```bash
bash install.sh
# Edit .env with your API keys, then:
source venv/bin/activate
python main.py
# Open http://localhost:8000
```

<br>

---

<br>

## ⚙️ Configuration

Copy `.env.example` to `.env`:

**Required**

```env
OPENAI_API_KEY=         # GPT-4o and cover letters
TELEGRAM_BOT_TOKEN=     # optional — leave blank to skip
RESUME_PATH=            # path to your PDF resume
```

**Optional**

```env
ANTHROPIC_API_KEY=      # Claude models
GOOGLE_API_KEY=         # Gemini models
# SMTP credentials for email notifications
# Portal credentials (autofill if you log in manually on portals)
```

<br>

---

<br>

## 🔀 Multi-Model Configuration

Select a different LLM provider per agent to balance speed and cost:

| Agent | Recommended | Reason |
|---|---|---|
| **Scraper** | `gpt-4o-mini` or Claude Haiku | Fast and cheap |
| **ATS** | `gpt-4o` or Claude Sonnet | Best scoring quality |
| **Cover Letters** | `gpt-4o` or Claude Opus | Highest writing quality |
| **Application** | `gpt-4o-mini` | Fast form filling |

<br>

---

<br>

## 📡 Supported Job Portals

Hiredly · JobStreet · JobsDB · Kalibrr · LinkedIn · Indeed · Glassdoor · Remotive · and 5+ more

**Custom portals:**
1. Settings → Portals → Add Custom Portal
2. Paste a job listing URL
3. Click **Auto-detect** — GPT-4o discovers selectors and caches them in `config/portal_cache.json`

<br>

---

<br>

## 🛠️ Career Tools

| Tool | Description |
|---|---|
| **Resume Analyzer** | Generic quality check + scoring |
| **Interview Bullet Extractor** | Step-by-step context extraction |
| **LinkedIn Optimizer** | Rewrites profile sections per career goal |
| **Hiring Manager Finder** | Searches for relevant hiring manager posts |
| **LinkedIn Post Generator** | Creates 3 post options per topic |

<br>

---

<br>

## 📋 API Reference

### Status & Control

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/status` | Current run info + pending confirmations |
| `POST` | `/api/search` | Start pipeline with keywords |
| `POST` | `/api/stop` | Stop active run |

### Jobs & Approvals

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/jobs` | All jobs from latest run |
| `GET` | `/api/jobs/{id}` | Job detail + cover letter + ATS + resume edits |
| `GET` | `/api/confirm/pending` | Enriched list of pending approvals |
| `POST` | `/api/confirm/{id}` | Record YES / SKIP decision |

### Settings

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/settings` | Current settings (secrets masked) |
| `GET` | `/api/models` | Available LLM models and agents |
| `GET` | `/api/portals` | All configured portals |
| `POST` | `/api/prompts/reset` | Reset all prompts to defaults |

### Career Tools

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/career/resume/analyze` | Generic resume quality check |
| `POST` | `/api/career/resume/interview-bullet` | Context extraction |
| `POST` | `/api/career/linkedin/optimize` | Profile rewrite per goal |
| `POST` | `/api/career/hiring-managers` | Hiring manager post search |
| `POST` | `/api/career/linkedin/post` | Generate 3 post options |

### WebSocket

| Stream | Events |
|---|---|
| `/api/ws/status` | `phase_start` · `job_found` · `ats_score` · `confirmation_request` · `job_applied` |
| `/api/ws/browser` | Screenshot frames (1 FPS JPEG) + selector health checks |

<br>

---

<br>

## 🔧 Troubleshooting

<br>

**"Frontend not built"**

```bash
cd frontend && npm run build && cd ..
```

**Playwright selector failures**

- Settings → Health Check → Verify Selectors
- If a portal redesigned its layout, selectors may need updating
- System attempts LLM auto-discovery on selector failure

**WebSocket disconnects**

- Check DevTools → Network → WS tab
- Auto-reconnect uses exponential backoff: 1s → 2s → 4s → 30s
- Verify backend is running: `python main.py` shows `uvicorn running on 0.0.0.0:8000`

**API errors**

- Confirm all required keys are set in `.env`
- Verify resume file exists at `RESUME_PATH`
- Check backend terminal logs

<br>

---

<br>

## 💡 Prompt Editing

All AI prompts stored in `prompts.json` (auto-created on first run):

- Edit directly in **Settings → Prompt Library**
- Changes apply to the next run immediately
- Reset to defaults: `POST /api/prompts/reset`

<br>

---

<br>

## 📈 Performance

| Phase | Typical Duration |
|---|---|
| Scrape (10 listings) | 2–5 min |
| ATS Scoring | 2–3 min |
| Cover Letters | 1–2 min |
| Applications | 3–5 min |
| **Total** | **~10–15 min** |

Browser session consumes ~200–300 MB RAM. Runs comfortably on modern laptops.

<br>

---

<br>

<div align="center">

**Job Application Dashboard** · Smarter job searching

*FastAPI · React 18 · Playwright · LangGraph · PageIndex RAG · Tailwind CSS*

</div>

