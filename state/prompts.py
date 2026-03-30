"""Prompt library management — load, save, and edit all AI prompts."""

import logging
from pathlib import Path
import orjson

logger = logging.getLogger(__name__)

PROMPTS_PATH = Path(__file__).parent.parent / "prompts.json"


def _get_defaults() -> dict:
    """Get default prompts (hardcoded)."""
    return {
        # Application prompts
        "cover_letter_system": """You are writing a cover letter as a professional job seeker.

Guidelines:
- Write short, direct sentences. Avoid clichés like "I am excited to leverage my expertise".
- Use quantified achievements from the resume.
- Address the specific job requirements and company.
- Keep it under 400 words.
- Sign off conversationally with your name and contact info.""",

        "cover_letter_user": """Write a tailored cover letter for this job application.

Job Title: {job_title}
Company: {company_name}

Job Description:
{job_description}

Resume:
{resume_context}""",

        "ats_score": """Score this resume against the JD requirements.

Return ONLY valid JSON:
{
  "score": 75,
  "matched_keywords": ["Python", "AWS"],
  "missing_keywords": ["Kubernetes", "Apache Spark"],
  "areas_to_improve": ["Add cloud platform experience"]
}

JOB:
Title: {job_title}
Company: {company}
Required Skills: {required_skills}
Years Experience: {years_exp}

RESUME (first 1500 chars):
{resume_text}""",

        "resume_bullet_rewrite": """Rewrite resume bullets to naturally include keywords without stuffing.

DO NOT:
- Add keywords as a list
- Use keywords in awkward ways
- Change the person's actual experience
- Make things up

DO:
- Rewrite sentences to include keywords naturally
- Keep professional tone
- Each edit should be a full sentence replacement
- Total edits: 3-5 top sentences

Return JSON:
{
  "edits": [
    {"original": "...", "edited": "...", "reason": "added Kubernetes"}
  ],
  "edited_full_resume": "full resume text with edits applied"
}

RESUME:
{resume_text}

MISSING KEYWORDS (add these naturally):
{keywords_str}

JOB TITLE: {job_title}""",

        "jd_requirements_extract": """Extract structured requirements from this job description.

Return ONLY valid JSON, no markdown.

{
  "required_skills": ["skill1", "skill2"],
  "years_experience": 3,
  "education": "Bachelor's",
  "nice_to_have": ["skill3"]
}

JD TEXT:
{jd_text}""",

        # Career prompts
        "linkedin_optimize": """Analyze this LinkedIn profile and provide specific rewrites.

Profile Goal: {goal}

Return improvements in JSON format:
{
  "headline": {"issue": "...", "rewrite": "..."},
  "about": {"issue": "...", "rewrite": "..."},
  "experience_bullets": [...],
  "featured_section": "recommendation",
  "missing_skills": ["..."],
  "cta": "recommendation"
}

PROFILE TEXT:
{profile_text}""",

        "hiring_manager_search_a": """site:linkedin.com/posts "{role}" ("I'm hiring" OR "hiring a" OR "looking for a") {industry} -intitle:jobs after:{date}""",

        "hiring_manager_search_b": """site:linkedin.com/posts "{role}" ("DM me" OR "send me your resume" OR "email me") "hiring" {location} -intitle:jobs after:{date}""",

        "hiring_manager_search_c": """site:linkedin.com/posts "excited to announce" "growing the team" "{role}" -job -recruiter after:{date}""",

        "hiring_manager_dm": """Write a short, personalized LinkedIn DM (max 5 sentences) for this context:

Hiring manager post: {post_snippet}
My background: {user_background}
Role I'm interested in: {role}

Rules: Be direct. Mention one specific thing from their post. Show one concrete match. End with a soft ask (15-min call or review my profile). No cringe openers like "I hope this message finds you well."

Output only the DM text.""",

        "resume_optimizer_analyze": """Score each resume bullet for quality using the formula: [Action Verb] + [What You Did] + [Quantified Result with Context].

For each bullet:
- Score 0-100 (90-100: strong, 70-89: good, below 70: needs interview mode)
- Flag: missing metric, weak opening verb, no scope/scale, no timeframe

Return JSON:
{
  "overall_score": 0-100,
  "bullets_with_metrics_pct": 0-100,
  "weak_bullets": [{"original": "...", "issue": "no metric"}],
  "strong_bullets": ["..."],
  "recommendations": ["..."]
}

RESUME:
{resume_text}""",

        "resume_bullet_interview": """You are helping a job seeker improve a weak resume bullet by extracting real context.

Weak bullet: {bullet}
Step {step} of 3. Previous answers: {answers}

Step 1: Ask ONE question about project/task specifics (what was it? what tool/method?)
Step 2: Ask ONE question about scale/scope/team (how large? budget? timeline?)
Step 3: Ask ONE question about measurable outcome (what metric? over what period?)

Ask only the question for this step. Be direct, one sentence.""",

        "resume_bullet_compose": """Compose one strong resume bullet using the context provided.

Original weak bullet: {bullet}
Context from user: {answers}

Formula: [Strong action verb] + [specific what, with tool/method/team size/domain] + [quantified result with context and timeframe]

Rules:
- No vague metrics. Every number must have context.
- No: "passionate", "leverage", "synergy", "results-driven"
- If user provided no metric, compose the bullet but add: [FLAG: ask user to confirm the metric]
- Do NOT invent facts, companies, dates, or metrics.

Output only the bullet. Nothing else.""",

        "resume_generic_check": """Scan this resume for content that will hurt the candidate with recruiters.

Flag these problems:
1. Vague metrics without context
2. Generic AI-signature phrases: "passionate", "leverage", "synergy", "results-driven"
3. Scope-free claims: "managed projects"
4. Generic achievement framing: "improved efficiency"
5. Responsibility-focused bullets: "Responsible for", "Assisted with"

For each flag: quote the phrase, explain why a recruiter will dismiss it, ask the one question that makes it specific.

Return JSON:
{
  "flags": [
    {"phrase": "...", "problem": "...", "question": "..."}
  ],
  "total_flags": N
}

RESUME:
{resume_text}""",

        "interview_prep": """Generate interview prep for this specific role using ONLY the resume experiences.

For each of 8 likely questions (2 behavioral, 2 role-specific, 2 situational, 2 "tell me about"):
1. State the question
2. Give 3 bullet-point talking points from the resume (specific names, tools, metrics)
3. Suggest one "human touch" — an honest moment, a challenge faced, a nuance

Rules:
- Bullet points only. No full sentences or scripts.
- If resume lacks a strong example, flag it: "No strong example found"
- Output is notes to glance at, not text to read aloud.

Return JSON:
{
  "questions": [
    {
      "q": "Tell me about a time you led a team...",
      "talking_points": ["...", "...", "..."],
      "human_touch": "...",
      "flag": null
    }
  ]
}

JD:
{jd}

RESUME:
{resume}""",

        "linkedin_post_reintro": """Write a LinkedIn reintroduction post for someone with this background.

Background: {background}

Rules: Professional but personal. Hook in first line. 3-4 paragraphs. End with a soft CTA ("Let's connect!" or "Happy to chat about..."). No spam.

Output only the post text.""",

        "linkedin_post_lesson": """Write a LinkedIn 'lessons learned' post about {topic}.

Rules: Share a real moment/challenge. What did you learn? How does it apply to your role/industry? End with a question to engage readers.

Output only the post text.""",

        "linkedin_post_hot_take": """Write a contrarian LinkedIn hot take about {topic}.

Rules: Bold but not offensive. Back it up with 1-2 quick examples. Invite respectful disagreement. Don't name-call.

Output only the post text.""",

        "linkedin_post_insight": """Write a LinkedIn industry insight post about {topic}.

Rules: Share something non-obvious you've noticed in your field. 3-4 paragraphs. End with a question or invitation to debate.

Output only the post text.""",

        "linkedin_post_tool": """Write a LinkedIn post about using AI tools for {task}.

Rules: Specific tool + actual use case. What problem did it solve? What's one gotcha? Honest take (not just praise).

Output only the post text.""",
    }


def load_prompts() -> dict:
    """Load all prompts from prompts.json, or create from defaults if missing."""
    if PROMPTS_PATH.exists():
        try:
            return orjson.loads(PROMPTS_PATH.read_bytes())
        except Exception as e:
            logger.error(f"Failed to load prompts.json: {e}")
            defaults = _get_defaults()
            save_prompts(defaults)
            return defaults
    else:
        # First run — create from defaults
        defaults = _get_defaults()
        save_prompts(defaults)
        return defaults


def save_prompts(prompts: dict) -> None:
    """Save prompts to prompts.json atomically."""
    try:
        PROMPTS_PATH.parent.mkdir(parents=True, exist_ok=True)
        tmp = PROMPTS_PATH.with_suffix(".tmp")
        tmp.write_bytes(orjson.dumps(prompts, option=orjson.OPT_INDENT_2))
        tmp.replace(PROMPTS_PATH)
        logger.info("Prompts saved")
    except Exception as e:
        logger.error(f"Failed to save prompts: {e}")


def get_prompt(key: str) -> str:
    """Get a single prompt by key."""
    prompts = load_prompts()
    return prompts.get(key, "")


def update_prompt(key: str, value: str) -> None:
    """Update a single prompt and persist."""
    prompts = load_prompts()
    prompts[key] = value
    save_prompts(prompts)
    logger.info(f"Prompt updated: {key}")
