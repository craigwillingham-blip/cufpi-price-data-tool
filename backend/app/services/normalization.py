import re
from difflib import SequenceMatcher


def normalize_size(raw: str) -> str:
    """Normalize size strings like '16 oz' -> '16 oz'."""
    cleaned = raw.strip().lower()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


def normalize_name(raw: str) -> str:
    cleaned = raw.strip().lower()
    cleaned = re.sub(r"[^a-z0-9\s]", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()
