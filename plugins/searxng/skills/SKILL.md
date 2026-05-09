---
name: searxng-web-search
description: "Use SearXNG (self-hosted on localhost:8888) for web search queries. Privacy-respecting metasearch aggregating Brave, DuckDuckGo, Wikipedia, and other engines."
---

# SearXNG Web Search

SearXNG is running at **http://localhost:8888**. Use it as the primary web search tool.

## 🚨 If Server is Not Reachable

If `http://localhost:8888` doesn't respond, start the services:

```bash
cd ~/qwen-gguf && ./start_llama_turboquant_stable.sh --no-llama
```

This starts both SearXNG (port 8888) and Camofox browser (port 9377) without the LLM.

## API Usage

```bash
# JSON search (programmatic)
curl -s "http://localhost:8888/search?q=<query>&format=json&categories=general"

# HTML search (human-readable page)
curl -s "http://localhost:8888/search?q=<query>"
```

## Common Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| `q` | query string | Search query |
| `format` | `json` | Get JSON results (preferred) |
| `categories` | `general`, `news`, `images`, `videos`, `files`, `music`, `it` | Category filter |
| `language` | `en`, `pl`, etc. | Language filter |
| `pageno` | 1, 2, 3... | Page number |
| `time_range` | `day`, `week`, `month`, `year` | Time filter |

## JSON Response Structure

When using `format=json`, the response contains:
- `query`: the search query
- `number_of_results`: total result count
- `results[]`: result objects with `url`, `title`, `content`, `engine`, `publishedDate`
- `answers[]`: direct answers
- `infoboxes[]`: knowledge panel info
- `suggestions[]`: related searches
- `unresponsive_engines[]`: engines that didn't respond

## Quick Examples

```bash
# Search web for AI news
curl -s "http://localhost:8888/search?q=latest+AI+developments&format=json&language=en" | python3 -c "import sys,json; d=json.load(sys.stdin); [print(f"{r['title']}\n  {r['url']}\n") for r in d['results'][:5]]"

# Search with time range
curl -s "http://localhost:8888/search?q=crypto+news&format=json&time_range=week&categories=news"
```
