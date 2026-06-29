# 🔢 tokencost

[![PyPI](https://img.shields.io/badge/pypi-v0.1.0-blue)](https://pypi.org/project/tokencost)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**LLM Token Cost Calculator & Visualizer** — count tokens, estimate costs, compare models across providers, all from the CLI.

## Features

- 🔢 **Token counting** — accurate with tiktoken for OpenAI models, smart estimate for others
- 💰 **Cost estimation** — input/output pricing for 20+ models across OpenAI, Anthropic, Google, Meta, DeepSeek, Alibaba
- 📊 **Model comparison** — side-by-side cost tables for any token count
- 💡 **Budget suggestions** — given text and budget, find the cheapest model
- 🎨 **Terminal UI** — color-coded tables and charts
- 🔌 **Pipe-friendly** — works with stdin/stdout for shell pipelines

## Quick Start

```bash
pip install tokencost
```

## Usage

### Count tokens
```bash
# Direct text
tokencost count --text "Hello, world!" --model gpt-4o

# From file
tokencost count --file prompt.txt

# From pipe
cat prompt.txt | tokencost count --model gpt-4o
```

### Estimate cost
```bash
# Single run
tokencost estimate --model claude-sonnet-4-6 --input-tokens 15000 --output-tokens 3000

# 1000 runs
tokencost estimate --model gpt-4o-mini --input-tokens 5000 --output-tokens 1000 --runs 1000
```

### Compare models
```bash
tokencost compare --input-tokens 10000 --output-tokens 5000
```

Output:
```
Model                    Input    Output         Cost  Provider
────────────────────────────────────────────────────────────────
gpt-5-nano              10,000      5,000    $0.0009  OpenAI
llama-4-scout           10,000      5,000    $0.0025  Meta
gpt-4o-mini             10,000      5,000    $0.0045  OpenAI
...
claude-opus-4-6         10,000      5,000    $0.5250  Anthropic
```

### Suggest cheapest model
```bash
tokencost suggest --file my_prompt.txt --budget 0.50
```

### List all models
```bash
tokencost list
tokencost list --provider OpenAI
tokencost list --json
```

## Supported Models (June 2026)

| Provider | Models |
|----------|--------|
| OpenAI | GPT-5, GPT-5 Mini/Nano, GPT-4.1 series, GPT-4o series |
| Anthropic | Claude Opus 4.6, Sonnet 4.6, Haiku 4.5 |
| Google | Gemini 2.5 Pro, Gemini 2.5 Flash |
| Meta | Llama 4 Maverick, Llama 4 Scout |
| DeepSeek | DeepSeek V3 |
| Alibaba | Qwen3 235B |

## Development

```bash
git clone https://github.com/alvabillwu/tokencost.git
cd tokencost
pip install -e ".[dev]"
pytest
```

## License

MIT © [alvabillwu](https://github.com/alvabillwu)
