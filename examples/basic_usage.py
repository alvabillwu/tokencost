#!/usr/bin/env python3
"""
tokencost examples — run with:
  python examples/basic_usage.py

Or use the CLI directly:
  python -m tokencost.cli count --text "Hello, world!"
  python -m tokencost.cli list
  python -m tokencost.cli compare --input-tokens 1000 --output-tokens 500
"""

from tokencost.models import get_model, list_models
from tokencost.tokenizers import count_tokens, suggest_model


def example_count():
    """Count tokens in a prompt."""
    prompt = "You are a helpful assistant. Explain quantum computing in simple terms."
    tokens = count_tokens(prompt, "gpt-4o")
    print(f"Prompt: {prompt}")
    print(f"Tokens (GPT-4o): {tokens}")
    print(f"Chars: {len(prompt)}, Ratio: {tokens/len(prompt)*100:.0f}%")
    print()


def example_cost():
    """Estimate cost for a batch job."""
    model = get_model("claude-sonnet-4-6")
    input_tokens = 15000
    output_tokens = 3000

    inp_cost = (input_tokens / 1_000_000) * model.input_price_per_1m
    out_cost = (output_tokens / 1_000_000) * model.output_price_per_1m
    total = inp_cost + out_cost

    print(f"Model: {model.name}")
    print(f"Input:  {input_tokens:,} tokens → ${inp_cost:.6f}")
    print(f"Output: {output_tokens:,} tokens → ${out_cost:.6f}")
    print(f"Total per run: ${total:.6f}")
    print(f"1000 runs: ${total * 1000:.4f}")
    print()


def example_suggest():
    """Find the cheapest model for a task."""
    task = "Write a blog post about AI agents in 2026. " * 50
    budget = 0.50  # $0.50 USD
    suggestions = suggest_model(task, budget)

    print(f"Task: {count_tokens(task)} tokens")
    print(f"Budget: ${budget:.2f}")
    print("Best models:")
    for model_id, runs in suggestions[:5]:
        m = get_model(model_id)
        print(f"  {model_id} ({m.provider}): ~{runs:,} runs possible")
    print()


if __name__ == "__main__":
    example_count()
    example_cost()
    example_suggest()
