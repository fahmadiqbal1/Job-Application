"""
Runtime model selector for LangChain agents.

Supports OpenAI (GPT-4o, GPT-4o-mini), Anthropic (Claude 3.5 Sonnet/Haiku, Claude Opus),
and Google (Gemini 2.0/1.5 Flash, Gemini 1.5 Pro).

All three providers return BaseChatModel, fully compatible with create_react_agent.
"""

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models.chat_models import BaseChatModel


# Canonical list used to populate the settings UI dropdown
AVAILABLE_MODELS: list[dict] = [
    # OpenAI
    {"id": "gpt-4o", "label": "GPT-4o (OpenAI)", "provider": "openai"},
    {"id": "gpt-4o-mini", "label": "GPT-4o Mini (OpenAI)", "provider": "openai"},
    {"id": "gpt-4-turbo", "label": "GPT-4 Turbo (OpenAI)", "provider": "openai"},
    # Anthropic
    {
        "id": "claude-3-5-sonnet-20241022",
        "label": "Claude 3.5 Sonnet (Anthropic)",
        "provider": "anthropic",
    },
    {
        "id": "claude-3-5-haiku-20241022",
        "label": "Claude 3.5 Haiku (Anthropic)",
        "provider": "anthropic",
    },
    {
        "id": "claude-3-opus-20240229",
        "label": "Claude 3 Opus (Anthropic)",
        "provider": "anthropic",
    },
    # Google
    {"id": "gemini-2.0-flash", "label": "Gemini 2.0 Flash (Google)", "provider": "google"},
    {"id": "gemini-1.5-pro", "label": "Gemini 1.5 Pro (Google)", "provider": "google"},
    {"id": "gemini-1.5-flash", "label": "Gemini 1.5 Flash (Google)", "provider": "google"},
]


def get_llm(model_id: str, temperature: float = 0) -> BaseChatModel:
    """
    Factory that accepts any model ID string and returns the correct
    LangChain ChatModel instance, ready for use with create_react_agent.

    Args:
        model_id: e.g. "gpt-4o", "claude-3-5-sonnet-20241022", "gemini-2.0-flash"
        temperature: sampling temperature (default 0 for deterministic agents)

    Returns:
        A BaseChatModel instance compatible with create_react_agent.

    Raises:
        ValueError: if model_id is not recognized.
    """
    if model_id.startswith("gpt-") or model_id.startswith("o1") or model_id.startswith("o3"):
        return ChatOpenAI(model=model_id, temperature=temperature)

    if model_id.startswith("claude-"):
        return ChatAnthropic(model=model_id, temperature=temperature)

    if model_id.startswith("gemini-"):
        return ChatGoogleGenerativeAI(model=model_id, temperature=temperature)

    raise ValueError(
        f"Unrecognized model_id '{model_id}'. "
        f"Must start with 'gpt-', 'o1', 'o3', 'claude-', or 'gemini-'."
    )


def get_model_label(model_id: str) -> str:
    """Return the human-readable label for a model ID."""
    for model in AVAILABLE_MODELS:
        if model["id"] == model_id:
            return model["label"]
    return model_id  # fallback: return the ID itself
