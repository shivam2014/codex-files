---
name: searxng-search
description: "Web search via self-hosted SearxNG meta-search engine. Aggregates Google, Bing, DuckDuckGo, Brave, and 70+ engines with zero API key cost. Use when the user asks to search the web, research a topic, find recent information, or when web_fetch is insufficient."
---

# SearXNG Search

Web search powered by [SearxNG](https://github.com/searxng/searxng) — self-hosted meta search engine. Runs on `localhost:8888`. Zero API key, full privacy.

## Quick Start

```bash
python3 scripts/core.py "your query"
python3 scripts/core.py "your query" --num 5
python3 scripts/core.py "AI news" --categories news
python3 scripts/core.py "query" --lang en
python3 scripts/core.py "query" --urls-only
python3 scripts/core.py "query" --json
```

## Agent Workflow

1. **Search** — run `python3 scripts/core.py "topic"` for candidate URLs + snippets
2. **Evaluate** — if snippet has enough info, answer directly
3. **Deep-dive** — if snippet truncated, use `web_fetch` or `curl` on the URL for full content

## Parameters

| Flag | Short | Description | Default |
|------|-------|-------------|---------|
| `--num N` | `-n` | Max results | 10 |
| `--engines` | `-e` | Comma-sep: google,bing,duckduckgo,brave | all |
| `--lang` | `-l` | Language filter: en, zh-CN, ja, ko | none |
| `--categories` | `-c` | Category: general,news,images,science | general |
| `--json` | `-j` | Raw JSON output | off |
| `--urls-only` | `-u` | URLs only (pipe to web_fetch) | off |

## Configuration

Default SearXNG endpoint: `http://localhost:8888`
Override via `SEARXNG_URL` env var:
```bash
export SEARXNG_URL="http://localhost:8888"
```

## Setup (if SearXNG not running)

See `references/setup.md` for Docker Compose setup of SearXNG.
