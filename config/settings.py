from pydantic_settings import BaseSettings
from pathlib import Path

# Project root — one level above this file
PROJECT_ROOT = Path(__file__).parent.parent


class Settings(BaseSettings):
    """Application configuration from .env"""

    # LLM API keys
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    google_api_key: str = ""

    # Default LLM
    default_llm_provider: str = "anthropic"
    default_model: str = "claude-sonnet-4-6"

    # Telegram
    telegram_bot_token: str = ""
    telegram_allowed_users: str = ""

    # Email
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_pass: str = ""
    notification_email: str = ""

    # Portal credentials
    hiredly_email: str = ""
    hiredly_password: str = ""
    jobstreet_email: str = ""
    jobstreet_password: str = ""
    linkedin_email: str = ""
    linkedin_password: str = ""
    indeed_email: str = ""
    indeed_password: str = ""

    # Career platform paths (resolved relative to project root if not set)
    data_dir: str = str(PROJECT_ROOT / "data")
    scripts_dir: str = str(PROJECT_ROOT / "scripts")
    prompts_dir: str = str(PROJECT_ROOT / "prompts")
    templates_dir: str = str(PROJECT_ROOT / "templates")
    static_dir: str = str(PROJECT_ROOT / "static")
    node_path: str = "node"

    # Legacy paths (kept for v1 compatibility)
    resume_path: str = ""
    screenshots_dir: str = str(PROJECT_ROOT / "data" / "screenshots")
    ats_workspace_dir: str = str(PROJECT_ROOT / "rag" / "workspace")

    # Daily automation
    daily_search_keywords: str = ""
    daily_run_hour: int = 7

    # Model selection per agent
    model_scraper: str = "gpt-4o-mini"
    model_ats: str = "gpt-4o"
    model_cover_letter: str = "gpt-4o"
    model_application: str = "gpt-4o-mini"
    model_notifier: str = "gpt-4o-mini"

    # Behaviour
    max_jobs_per_run: int = 15
    confirmation_timeout_secs: int = 300
    target_ats_score: int = 90

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
