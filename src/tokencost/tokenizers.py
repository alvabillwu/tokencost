"""Token counting backends.

Supports multiple tokenization methods:
1. tiktoken (OpenAI models) — most accurate
2. Character-based estimate — universal fallback
3. Word-based estimate — quick rough estimate
"""

from functools import lru_cache
from typing import Optional


def _try_import_tiktoken():
    """Lazy-load tiktoken."""
    try:
        import tiktoken  # type: ignore
        return tiktoken
    except ImportError:
        return None


@lru_cache(maxsize=4)
def _get_tiktoken_encoding(name: str):
    tiktoken = _try_import_tiktoken()
    if tiktoken:
        try:
            return tiktoken.get_encoding(name)
        except Exception:
            return tiktoken.encoding_for_model(name)
    return None


# Model → tiktoken encoding mapping
TIKTOKEN_MAP = {
    "gpt-4": "o200k_base",
    "gpt-4o": "o200k_base",
    "gpt-4o-mini": "o200k_base",
    "gpt-5": "o200k_base",
    "gpt-3.5": "cl100k_base",
    "text-embedding": "cl100k_base",
}


def count_tokens(text: str, model_id: Optional[str] = None) -> int:
    """Count tokens in text, preferring tiktoken when available for the model.

    Args:
        text: The text to count tokens for.
        model_id: Optional model to select the right tokenizer.

    Returns:
        Estimated token count.
    """
    enc = None
    if model_id:
        for prefix, enc_name in TIKTOKEN_MAP.items():
            if model_id.startswith(prefix):
                enc = _get_tiktoken_encoding(enc_name)
                break

    if enc:
        return len(enc.encode(text))

    # Fallback: ~4 chars per token for English text (industry rule of thumb)
    # More accurate: 1 token ≈ 3.5 chars for code, ≈ 4 chars for prose
    return max(1, len(text) // 4)


def estimate_input_tokens(text: str, model_id: Optional[str] = None) -> int:
    """Best-effort input token count."""
    return count_tokens(text, model_id)


def estimate_output_tokens(text: str, model_id: Optional[str] = None) -> int:
    """Best-effort output token count (same algorithm, output tokens are priced differently)."""
    return count_tokens(text, model_id)


def suggest_model(text: str, max_budget_usd: float) -> list[tuple[str, int]]:
    """Suggest the cheapest model that can process the given text.

    Returns list of (model_id, estimated_runs_within_budget).
    """
    from .models import MODELS

    input_tokens = count_tokens(text)
    results = []
    for model_id, m in MODELS.items():
        if m.type != "chat":
            continue
        cost_per_run = (input_tokens / 1_000_000) * m.input_price_per_1m
        if cost_per_run > 0:
            runs = int(max_budget_usd / cost_per_run)
        else:
            runs = float("inf")  # type: ignore
        results.append((model_id, runs))
    results.sort(key=lambda x: x[1], reverse=True)
    return results
