"""Port of scripts/lib/fuzzy-match.mjs — company and role normalization."""

import re


def normalize_company(name: str) -> str:
    """Strip punctuation, lowercase, collapse whitespace."""
    s = name.lower()
    s = re.sub(r"[^\w\s]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    # Remove common suffixes
    for suffix in [" inc", " ltd", " llc", " corp", " co", " sdn bhd", " bhd"]:
        if s.endswith(suffix):
            s = s[: -len(suffix)].strip()
    return s


def normalize_role(role: str) -> str:
    """Normalize role title for comparison."""
    s = role.lower()
    s = re.sub(r"[^\w\s]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def role_match(a: str, b: str) -> bool:
    """True if ≥2 significant words (>3 chars) overlap between two roles."""
    def sig_words(s: str) -> set[str]:
        return {w for w in normalize_role(s).split() if len(w) > 3}

    common = sig_words(a) & sig_words(b)
    return len(common) >= 2


def company_match(a: str, b: str) -> bool:
    """True if normalized company names are equal."""
    return normalize_company(a) == normalize_company(b)
