"""CLI entry point for tokencost."""

import argparse
import sys
from pathlib import Path

from .models import get_model, list_models, MODELS, ModelPricing
from .tokenizers import count_tokens, suggest_model
from .display import cost_table, model_card, bar_chart, summary, Color, _c


def cmd_count(args):
    """Count tokens in text or file."""
    text = ""
    if args.file:
        text = Path(args.file).read_text(encoding="utf-8")
    elif args.text:
        text = args.text
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        print("Error: provide text via --text, --file, or pipe", file=sys.stderr)
        sys.exit(1)

    model_id = args.model or None
    tokens = count_tokens(text, model_id)
    print(f"{_c(Color.GREEN + Color.BOLD, str(tokens))} tokens ({len(text):,} chars, ratio {tokens/len(text)*100:.0f}%)")


def cmd_estimate(args):
    """Estimate cost for a task with given input/output token counts."""
    model = get_model(args.model)
    if not model:
        print(f"Unknown model: {args.model}. Use 'list' to see available models.", file=sys.stderr)
        sys.exit(1)

    inp_cost = (args.input_tokens / 1_000_000) * model.input_price_per_1m
    out_cost = (args.output_tokens / 1_000_000) * model.output_price_per_1m
    total = inp_cost + out_cost

    if args.runs:
        inp_cost *= args.runs
        out_cost *= args.runs
        total *= args.runs
        print(f"Estimating {args.runs} runs with {model.name}:")
    else:
        print(f"Estimating 1 run with {model.name}:")

    print(f"  Input:  {args.input_tokens:,} tokens → ${inp_cost:.6f}")
    print(f"  Output: {args.output_tokens:,} tokens → ${out_cost:.6f}")
    print(summary(args.input_tokens, args.output_tokens, total))


def cmd_compare(args):
    """Compare cost across all models for a given token count."""
    inp = args.input_tokens
    out = args.output_tokens
    data = []
    for m in sorted(MODELS.values(), key=lambda x: x.input_price_per_1m):
        if m.type != "chat":
            continue
        inp_c = (inp / 1_000_000) * m.input_price_per_1m
        out_c = (out / 1_000_000) * m.output_price_per_1m
        data.append((m.id, inp, out, inp_c, out_c, inp_c + out_c, m.provider))

    print(f"Cost comparison for {inp:,} input + {out:,} output tokens:\n")
    print(cost_table(data))


def cmd_list(args):
    """List all known models and pricing."""
    provider = args.provider or None
    models = list_models(provider)
    if args.json:
        import json
        result = {}
        for m in models:
            result[m.id] = {
                "name": m.name,
                "provider": m.provider,
                "input_price_per_1m": m.input_price_per_1m,
                "output_price_per_1m": m.output_price_per_1m,
                "context_window": m.context_window,
                "type": m.type,
            }
        print(json.dumps(result, indent=2))
    else:
        for m in models:
            print(model_card(m))
            print()


def cmd_suggest(args):
    """Suggest the most cost-effective model for a budget."""
    text = ""
    if args.file:
        text = Path(args.file).read_text(encoding="utf-8")
    elif args.text:
        text = args.text
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        print("Error: provide text via --text, --file, or pipe", file=sys.stderr)
        sys.exit(1)

    budget = args.budget
    suggestions = suggest_model(text, budget)
    print(f"Models ranked by runs possible within ${budget:.2f} budget:\n")
    for model_id, runs in suggestions[:10]:
        m = MODELS[model_id]
        cost_per = (count_tokens(text, model_id) / 1_000_000) * m.input_price_per_1m
        bar = "█" * min(int(runs / 100), 30) if runs < 10000 else "█" * 30
        if runs == float("inf"):
            runs_str = "∞"
            bar = "█" * 30
        else:
            runs_str = f"{runs:,}"
        print(f"  {_c(Color.BOLD, model_id):<24} {bar} {_c(Color.GREEN, runs_str)} runs (${cost_per:.6f}/run)")


def main():
    parser = argparse.ArgumentParser(
        prog="tokencost",
        description="LLM Token Cost Calculator — count tokens, estimate costs, compare models",
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    # count
    p_count = sub.add_parser("count", help="Count tokens in text")
    p_count.add_argument("--text", help="Text to count")
    p_count.add_argument("--file", help="File to read")
    p_count.add_argument("--model", help="Model for accurate tokenization (e.g. gpt-4o)")

    # estimate
    p_est = sub.add_parser("estimate", help="Estimate cost")
    p_est.add_argument("--model", required=True, help="Model ID")
    p_est.add_argument("--input-tokens", type=int, required=True, help="Input token count")
    p_est.add_argument("--output-tokens", type=int, required=True, help="Expected output token count")
    p_est.add_argument("--runs", type=int, help="Number of runs to multiply by")

    # compare
    p_cmp = sub.add_parser("compare", help="Compare costs across models")
    p_cmp.add_argument("--input-tokens", type=int, required=True)
    p_cmp.add_argument("--output-tokens", type=int, required=True)

    # list
    p_list = sub.add_parser("list", help="List models & pricing")
    p_list.add_argument("--provider", help="Filter by provider (OpenAI, Anthropic, Google, Meta, etc.)")
    p_list.add_argument("--json", action="store_true", help="Output as JSON")

    # suggest
    p_sug = sub.add_parser("suggest", help="Suggest cheapest model for a budget")
    p_sug.add_argument("--text", help="Text to analyze")
    p_sug.add_argument("--file", help="File to read")
    p_sug.add_argument("--budget", type=float, required=True, help="Max budget in USD")

    args = parser.parse_args()

    if args.command == "count":
        cmd_count(args)
    elif args.command == "estimate":
        cmd_estimate(args)
    elif args.command == "compare":
        cmd_compare(args)
    elif args.command == "list":
        cmd_list(args)
    elif args.command == "suggest":
        cmd_suggest(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
