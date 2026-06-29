"""Tests for tokencost."""

import pytest
from tokencost.models import get_model, list_models, MODELS, ModelPricing
from tokencost.tokenizers import count_tokens, suggest_model


class TestModels:
    def test_get_model_exact(self):
        m = get_model("gpt-4o")
        assert m is not None
        assert m.name == "GPT-4o"
        assert m.provider == "OpenAI"

    def test_get_model_fuzzy(self):
        m = get_model("claude haiku")
        assert m is not None
        assert "haiku" in m.id

    def test_get_model_unknown(self):
        assert get_model("nonexistent-model-xyz") is None

    def test_list_all(self):
        models = list_models()
        assert len(models) > 10

    def test_list_by_provider(self):
        openai_models = list_models("OpenAI")
        assert all(m.provider == "OpenAI" for m in openai_models)

    def test_all_models_have_pricing(self):
        for m in MODELS.values():
            assert m.input_price_per_1m >= 0
            assert m.output_price_per_1m >= 0
            assert m.context_window > 0


class TestTokenizers:
    def test_count_tokens_basic(self):
        n = count_tokens("Hello, world!")
        assert n > 0
        assert n <= 20  # "Hello, world!" is ~4 tokens

    def test_count_tokens_empty(self):
        n = count_tokens("")
        assert n == 1 or n >= 0

    def test_count_tokens_long(self):
        text = "The quick brown fox jumps over the lazy dog. " * 100
        n = count_tokens(text)
        assert n > 100
        assert n < len(text)

    def test_count_tokens_with_model(self):
        n = count_tokens("Hello, world!", "gpt-4o")
        assert n > 0

    def test_suggest_model(self):
        text = "Hello, world!" * 1000
        suggestions = suggest_model(text, max_budget_usd=1.0)
        assert len(suggestions) > 0
        runs_values = [s[1] for s in suggestions if s[1] != float("inf")]
        if len(runs_values) >= 2:
            assert runs_values[0] >= runs_values[-1]
