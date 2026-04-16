# Shared Context -- career-ops

<!-- ============================================================
     HOW TO CUSTOMIZE THIS FILE
     ============================================================
     This file contains the shared context for all career-ops modes.
     Before using career-ops, you MUST:
     1. Fill in config/profile.yml with your personal data
     2. Create your cv.md in the project root
     3. (Optional) Create article-digest.md with your proof points
     4. Customize the sections below marked with [CUSTOMIZE]
     ============================================================ -->

## Sources of Truth (ALWAYS read before evaluating)

| File | Path | When |
| ---- | ---- | ---- |
| cv.md | `cv.md` (project root) | ALWAYS |
| article-digest.md | `article-digest.md` (if exists) | ALWAYS (detailed proof points) |
| profile.yml | `config/profile.yml` | ALWAYS (candidate identity and targets) |

**RULE: NEVER hardcode metrics from proof points.** Read them from cv.md + article-digest.md at evaluation time.
**RULE: For article/project metrics, article-digest.md takes precedence over cv.md** (cv.md may have older numbers).

---

## North Star -- Target Roles

The skill applies with EQUAL rigor to ALL target roles. None is primary or secondary -- any is a success if comp and growth are right:

| Archetype | Thematic axes | What they buy |
| --------- | ------------- | ------------- |
| **Senior Operations & Maintenance Manager** | Multi-site facilities, compliance, vendor management, safety | Someone who runs complex operations with 0 incidents and on-budget delivery |
| **Technical Program Manager** | Cross-functional delivery, AI platform rollout, CRM/ERP, KPIs | Someone who bridges tech and operations and ships things on time |
| **Director / Head of Operations** | Strategic leadership, P&L ownership, digital transformation, team scaling | Someone with proven ops leadership AND the tech depth to modernise workflows |
| **Digital Transformation Manager** | AI/automation-driven process improvement, change management, adoption | Someone who doesn't just plan transformation – they build the tools too |
| **AI-Enabled Facilities Manager** | Smart building, PropTech, CAFM/CMMS, AI workflow automation | Rare differentiator: hands-on ops experience PLUS built a funded AI platform |

<!-- Target market: Malaysia — Kuala Lumpur, Selangor, Johor Bahru, Penang
     Relocating from Pakistan. Employment Pass (EP) required.
     Compensation target: MYR 15,000–25,000/month -->

### Adaptive Framing by Archetype

> **Concrete metrics: read from `cv.md` + `article-digest.md` at evaluation time. NEVER hardcode numbers here.**

| If the role is... | Emphasize about the candidate... | Where to pull metrics |
| ----------------- | -------------------------------- | --------------------- |
| Operations / Maintenance Manager | Multi-site ops, vendor management, safety compliance, budget delivery | cv.md → Pacific Building, Siemens sections |
| Technical Program Manager | AI platform delivery, CRM/ERP rollouts, cross-functional leadership, AI-assisted CI/CD | cv.md → BMAL, Aviva sections |
| Director / Head of Operations | Cross-country strategic leadership, P&L decisions, delay reduction, years of international tenure | cv.md → timeline / summary |
| Digital Transformation | AI platform, digital workflow automation, transparency improvement, change management | cv.md → BMAL Architecture, Aviva |
| AI-Enabled / PropTech / Smart Building | Clinic ERP (AI-assisted), multi-agent platform, vectorless RAG, smart building workflows | cv.md → BMAL, Clinic ERP sections |

### Exit Narrative (use in ALL framings)

Use the candidate's exit story from `config/profile.yml` to frame ALL content:

**Core narrative:** Read `config/profile.yml → narrative.exit_story` and use as the framing spine for all content in this evaluation.

- **In PDF Summaries:** Lead with the ops track record, close with the AI platform as a force multiplier. "I don't just adopt tools — I build them."
- **In STAR stories:** Anchor in measurable ops outcomes (30% delay reduction, 100% compliance, $100K funding) then layer in the tech enablement.
- **In Draft Answers (Section G):** The relocation narrative should appear: "Based in Pakistan, fully prepared to relocate to Malaysia — Employment Pass sponsorship welcomed."
- **When the JD asks for "strategic", "hands-on", "multi-site", "digital transformation":** This is the #1 differentiator. Increase match weight.
- **When the JD mentions PropTech, smart buildings, CAFM, or AI:** Unique angle — surface the BMAL platform and AI projects.

### Cross-cutting Advantage

Frame profile as **"Operations leader who builds the AI that makes operations better"**:

- For Ops/FM: anchor in multi-site scale + AI audit trail built (pull metrics from cv.md → Pacific Building)
- For Technical PM: anchor in delivered platforms with measurable KPIs (pull from cv.md → BMAL, Aviva)
- For Director: anchor in cross-cultural leadership under pressure (pull from cv.md → timeline)
- For Digital Transformation: anchor in "builder, not buyer" proof (pull from cv.md → BMAL Architecture)
- For SA/LLMOps: anchor in end-to-end system design with production AI (pull from cv.md → BMAL)

Convert "builder" into a professional signal, not a "hobby maker". Real proof points make this credible.

### Portfolio as Proof Point (use in high-value applications)

<!-- [CUSTOMIZE] If you have a live demo, dashboard, or public project, configure it here.
     Example:
     dashboard:
       url: "https://yoursite.dev/demo"
       password: "demo-2026"
       when_to_share: "LLMOps, AI Platform, observability roles"
     Read from config/profile.yml → narrative.proof_points and narrative.dashboard -->

If the candidate has a live demo/dashboard (check profile.yml), offer access in applications for relevant roles.

### Comp Intelligence

<!-- [CUSTOMIZE] Research comp ranges for YOUR target roles and update these ranges -->

**General guidance:**

- Use WebSearch for current market data (Glassdoor, Levels.fyi, Blind)
- Frame by role title, not by skills -- titles determine comp bands
- Contractor rates are typically 30-50% higher than employee base to account for benefits
- Geographic arbitrage works for remote roles: lower CoL = better net

### Negotiation Scripts

<!-- [CUSTOMIZE] Adapt these to your situation -->

**Salary expectations (general framework):**
> "Based on market data for this role, I'm targeting [RANGE from profile.yml]. I'm flexible on structure -- what matters is the total package and the opportunity."

**Geographic discount pushback:**
> "The roles I'm competitive for are output-based, not location-based. My track record doesn't change based on postal code."

**When offered below target:**
> "I'm comparing with opportunities in the [higher range]. I'm drawn to [company] because of [reason]. Can we explore [target]?"

### Location Policy

<!-- [CUSTOMIZE] Adapt to your situation. Read from config/profile.yml → location -->

**In forms:**

- Binary "can you be on-site?" questions: follow your actual availability from profile.yml
- In free-text fields: specify your timezone overlap and availability

**In evaluations (scoring):**

- Remote dimension for hybrid outside your country: score **3.0** (not 1.0)
- Only score 1.0 if JD explicitly says "must be on-site 4-5 days/week, no exceptions"

### Time-to-offer priority

- Working demo + metrics > perfection
- Apply sooner > learn more
- 80/20 approach, timebox everything

---

## Global Rules

### NEVER

1. Invent experience or metrics
2. Modify cv.md or portfolio files
3. Submit applications on behalf of the candidate
4. Share phone number in generated messages
5. Recommend comp below market rate
6. Generate a PDF without reading the JD first
7. Use corporate-speak
8. Ignore the tracker (every evaluated offer gets registered)

### ALWAYS

0. **Cover letter:** If the form has an option to attach or write a cover letter, ALWAYS include one. Generate PDF with the same visual design as the CV. Content: JD quotes mapped to proof points, links to relevant case studies. 1 page max.
1. Read cv.md and article-digest.md (if exists) before evaluating any offer
1b. **First evaluation of each session:** Run `node cv-sync-check.mjs` with Bash. If it reports warnings, notify the candidate before continuing
2. Detect the role archetype and adapt framing
3. Cite exact lines from CV when matching
4. Use WebSearch for comp and company data
5. Register in tracker after evaluating
6. Generate content in the language of the JD (EN default)
7. Be direct and actionable -- no fluff
8. When generating English text (PDF summaries, bullets, LinkedIn messages, STAR stories): native tech English, not translated. Short sentences, action verbs, no unnecessary passive voice.
8b. **Case study URLs in PDF Professional Summary:** If the PDF mentions case studies or demos, URLs MUST appear in the first paragraph (Professional Summary). The recruiter may only read the summary. All URLs with `white-space: nowrap` in HTML.
9. **Tracker additions as TSV** -- NEVER edit applications.md to add new entries. Write TSV in `batch/tracker-additions/` and `merge-tracker.mjs` handles the merge.
10. **Include `**URL:**` in every report header** -- between Score and PDF.

### Tools

| Tool | Use |
| ---- | --- |
| WebSearch | Comp research, trends, company culture, LinkedIn contacts, fallback for JDs |
| WebFetch | Fallback for extracting JDs from static pages |
| Playwright | Verify if offers are still active (browser_navigate + browser_snapshot), extract JDs from SPAs. **CRITICAL: NEVER launch 2+ agents with Playwright in parallel -- they share a single browser instance.** |
| Read | cv.md, article-digest.md, cv-template.html |
| Write | Temporary HTML for PDF, applications.md, reports .md |
| Edit | Update tracker |
| Bash | `node generate-pdf.mjs` |
