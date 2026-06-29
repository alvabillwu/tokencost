"""Model pricing data — updated June 2026.

Prices per 1M tokens (input / output). Sources:
- https://openai.com/pricing
- https://anthropic.com/pricing
- https://ai.google.dev/pricing
- https://deepinfra.com/pricing (open-source models)
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ModelPricing:
    id: str
    provider: str
    name: str
    input_price_per_1m: float  # USD
    output_price_per_1m: float  # USD
    context_window: int
    type: str = "chat"  # chat | embedding | image


# fmt: off
MODELS: dict[str, ModelPricing] = {
    # ── OpenAI ──
    "gpt-5":         ModelPricing("gpt-5", "OpenAI", "GPT-5", 1.25, 10.00, 262_144),
    "gpt-5-mini":    ModelPricing("gpt-5-mini", "OpenAI", "GPT-5 Mini", 0.15, 0.60, 262_144),
    "gpt-5-nano":    ModelPricing("gpt-5-nano", "OpenAI", "GPT-5 Nano", 0.03, 0.12, 262_144),
    "gpt-4.1":       ModelPricing("gpt-4.1", "OpenAI", "GPT-4.1", 2.00, 8.00, 1_048_576),
    "gpt-4.1-mini":  ModelPricing("gpt-4.1-mini", "OpenAI", "GPT-4.1 Mini", 0.40, 1.60, 1_048_576),
    "gpt-4.1-nano":  ModelPricing("gpt-4.1-nano", "OpenAI", "GPT-4.1 Nano", 0.10, 0.40, 1_048_576),
    "gpt-4o":        ModelPricing("gpt-4o", "OpenAI", "GPT-4o", 2.50, 10.00, 131_072),
    "gpt-4o-mini":   ModelPricing("gpt-4o-mini", "OpenAI", "GPT-4o Mini", 0.15, 0.60, 131_072),

    # ── Anthropic ──
    "claude-opus-4-6":    ModelPricing("claude-opus-4-6", "Anthropic", "Claude Opus 4.6", 15.00, 75.00, 200_000),
    "claude-sonnet-4-6":  ModelPricing("claude-sonnet-4-6", "Anthropic", "Claude Sonnet 4.6", 3.00, 15.00, 200_000),
    "claude-haiku-4-5":   ModelPricing("claude-haiku-4-5", "Anthropic", "Claude Haiku 4.5", 0.80, 4.00, 200_000),

    # ── Google ──
    "gemini-2.5-pro":  ModelPricing("gemini-2.5-pro", "Google", "Gemini 2.5 Pro", 1.25, 5.00, 2_097_152),
    "gemini-2.5-flash":ModelPricing("gemini-2.5-flash", "Google", "Gemini 2.5 Flash", 0.15, 0.60, 1_048_576),

    # ── Open-Source (via DeepInfra / Together) ──
    "llama-4-maverick":   ModelPricing("llama-4-maverick", "Meta", "Llama 4 Maverick", 0.20, 0.60, 131_072, type="chat"),
    "llama-4-scout":      ModelPricing("llama-4-scout", "Meta", "Llama 4 Scout", 0.10, 0.30, 131_072, type="chat"),
    "deepseek-v3":        ModelPricing("deepseek-v3", "DeepSeek", "DeepSeek V3", 0.27, 1.10, 131_072),
    "qwen3-235b":         ModelPricing("qwen3-235b", "Alibaba", "Qwen3 235B", 0.30, 0.80, 131_072),

    # ── Embedding ──
    "text-embedding-3-large": ModelPricing("text-embedding-3-large", "OpenAI", "Text Embedding 3 Large", 0.13, 0.00, 8191, type="embedding"),
    "text-embedding-3-small": ModelPricing("text-embedding-3-small", "OpenAI", "Text Embedding 3 Small", 0.02, 0.00, 8191, type="embedding"),
}
# fmt: on


def get_model(model_id: str) -> Optional[ModelPricing]:
    """Look up a model by exact id or fuzzy match."""
    ml = model_id.lower().replace(" ", "-")  # normalize spaces to hyphens
    if ml in MODELS:
        return MODELS[ml]
    for key, m in MODELS.items():
        if ml in key or ml.replace("-", "") in key.replace("-", ""):
            return m
    return None


def list_models(provider: Optional[str] = None) -> list[ModelPricing]:
    """List all known models, optionally filtered by provider."""
    if provider:
        return [m for m in MODELS.values() if m.provider.lower() == provider.lower()]
    return sorted(MODELS.values(), key=lambda m: m.input_price_per_1m)
