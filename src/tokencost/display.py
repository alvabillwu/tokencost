"""Terminal display helpers — rich tables, colors, comparisons."""

import sys
from typing import Optional


# ANSI color codes
class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"


def _supports_color() -> bool:
    if not hasattr(sys.stdout, "isatty"):
        return False
    return sys.stdout.isatty()


def _c(color: str, text: str) -> str:
    """Wrap text in color if terminal supports it."""
    if _supports_color():
        return f"{color}{text}{Color.RESET}"
    return text


def bar_chart(parts: list[tuple[str, int, str]], width: int = 48) -> str:
    """Draw a horizontal stacked bar chart.

    Args:
        parts: List of (label, count, color) tuples. Colors from Color class.
        width: Total bar width in characters.

    Returns:
        Multi-line string with the chart.
    """
    total = sum(c for _, c, _ in parts)
    if total == 0:
        return "(empty)"

    lines = []
    bar = ""
    for label, count, color in parts:
        seg_width = max(1, int(count / total * width))
        bar += _c(color, "█" * seg_width)
    lines.append(bar)

    for label, count, color in parts:
        pct = count / total * 100
        lines.append(f"  {_c(color, '●')} {label}: {count:,} tokens ({pct:.1f}%)")

    return "\n".join(lines)


def cost_table(models_data: list[tuple]) -> str:
    """Render a price comparison table.

    Args:
        models_data: List of (model_name, input_tokens, output_tokens, input_cost, output_cost, total_cost, provider)
    """
    header = f"{'Model':<28} {'Input':>10} {'Output':>10} {'Cost':>12}  Provider"
    sep = "─" * len(header)
    rows = [header, sep]

    for name, inp_t, out_t, inp_c, out_c, total_c, provider in models_data:
        row = (
            f"{_c(Color.BOLD, name):<28} "
            f"{inp_t:>10,} "
            f"{out_t:>10,} "
            f"{_c(Color.YELLOW, f'${total_c:>10.4f}')}  "
            f"{_c(Color.DIM, provider)}"
        )
        rows.append(row)

    return "\n".join(rows)


def model_card(model) -> str:
    """Render a single model's pricing card."""
    lines = [
        f"{_c(Color.BOLD + Color.CYAN, model.name)} ({model.id})",
        f"  Provider:      {model.provider}",
        f"  Context:       {model.context_window:,} tokens",
        f"  Input price:   {_c(Color.YELLOW, f'${model.input_price_per_1m:.2f}')} / 1M tokens",
        f"  Output price:  {_c(Color.YELLOW, f'${model.output_price_per_1m:.2f}')} / 1M tokens",
        f"  Type:          {model.type}",
    ]
    return "\n".join(lines)


def summary(total_input: int, total_output: int, total_cost: float) -> str:
    """Print a one-line cost summary."""
    tokens_str = f"{total_input + total_output:,} tokens ({total_input:,} in / {total_output:,} out)"
    cost_str = f"${total_cost:.6f}"
    return (
        f"{_c(Color.GREEN + Color.BOLD, 'Total')}: "
        f"{tokens_str} → "
        f"{_c(Color.YELLOW + Color.BOLD, cost_str)}"
    )
