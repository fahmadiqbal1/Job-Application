from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Application configuration from .env"""

    # LLM API keys
    openai_api_key: str
    anthropic_api_key: str = ""
    google_api_key: str = ""

    # Telegram
    telegram_bot_token: str
    telegram_allowed_users: str = ""  # comma-separated user IDs

    # Email
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str
    smtp_pass: str
    notification_email: str

    # Portal credentials
    hiredly_email: str
    hiredly_password: str
    jobstreet_email: str
    jobstreet_password: str
    linkedin_email: str = ""
    linkedin_password: str = ""
    indeed_email: str = ""
    indeed_password: str = ""

    # Paths
    resume_path: str
    screenshots_dir: str
    ats_workspace_dir: str = "D:/Projects/Job Application/rag/workspace"

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
