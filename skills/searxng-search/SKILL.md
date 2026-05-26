---
name: searxng-search
description: "Web search via self-hosted SearxNG meta-search engine through Camoufox anti-detection browser. Aggregates Google, Wikipedia, and other engines with zero API key cost. Use when the user asks to search the web, research a topic, find recent information, or when web_fetch is insufficient."
---

# SearXNG Search (Camoufox-Enhanced)

Web search powered by [SearxNG](https://github.com/searxng/searxng) — self-hosted meta search engine on `localhost:8888`. Zero API key, full privacy.

**Problem:** Direct SearXNG JSON API (`curl`/`httpx`) gets rate-limited/CAPTCHA-blocked by upstream engines because Python HTTP clients lack browser fingerprinting.

**Solution:** Route SearXNG through [Camoufox](https://github.com/redf0x1/camofox-browser) — a Firefox fork with C++-level fingerprint spoofing. Open SearXNG search URLs in Camoufox, then extract results from the accessibility snapshot. Google and Wikipedia consistently return results through this method.

## Prerequisites

- **SearXNG** running on `localhost:8888` (managed by `~/searxng/manager/searxng-manager.sh`)
- **Camoufox server** running on `localhost:9377` (managed by `~/qwen-gguf/start_llama_turboquant_stable.sh`)
- Camoufox CLI: `~/.codex/skills/camofox-browser/scripts/camofox.sh`

## Agent Workflow

### 1. Fast Path — Try Direct JSON API First

```bash
python3 scripts/core.py "your query"
```

If results are returned, use them directly (fast). If engines are all unresponsive/blocked, fall through to Camoufox path.

### 2. Reliable Path — Camoufox Browser

Open SearXNG search URL in Camoufox, then extract result URLs from snapshot:

```bash
# Step A: Close stale tabs for clean session
~/.codex/skills/camofox-browser/scripts/camofox.sh close-all

# Step B: Open search URL in Camoufox
~/.codex/skills/camofox-browser/scripts/camofox.sh open \
  "http://localhost:8888/search?q=URLENCODED_QUERY&language=en&safesearch=0&categories=general"

# Step C: Snapshot to get result links
~/.codex/skills/camofox-browser/scripts/camofox.sh snapshot 2>&1 | \
  grep -E "link.*http" | grep -v "searx\.space\|localhost\|/preferences\|/stats\|github.com/searxng\|Source code\|Issue tracker\|Engine stats\|Public instances"
```

### 3. Deep-dive

Open individual result URLs in Camoufox for full content:

```bash
~/.codex/skills/camofox-browser/scripts/camofox.sh open "https://example.com/article"
~/.codex/skills/camofox-browser/scripts/camofox.sh snapshot
```

## Helper Script

```bash
python3 scripts/searxng-camofox.py "your query"
python3 scripts/searxng-camofox.py "your query" --num 5
```

## Camoufox Best Practices (from redf0x1/camofox-browser + CapSolver integration guide)

These practices keep the Camoufox browser session stable and avoid detection/rate-limiting:

### 1. Session Cleanliness — Close Tabs Between Queries
Always close stale tabs before opening a new search. Leftover tabs accumulate cookies and DOM state that can trigger inconsistent behavior.
```bash
camofox close-all
```

### 2. Rate Limiting — Delay Between Consecutive Searches
When running multiple searches in sequence, add 2–5s delays between them to avoid triggering upstream rate limits:
```bash
sleep 3 && camofox open "..."
```

### 3. Fingerprint Consistency — Keep Session Per Query
Each `camofox open` creates a fresh page in the same browser context. The Camoufox server maintains consistent fingerprint within a session. When engines start blocking, close-all and retry — the new session gets a fresh fingerprint.

### 4. Error Handling — Retry on Empty Results
If snapshot returns no result links:
1. Wait 3s and re-snapshot (page may still be rendering)
2. Close-all and retry the search (fresh session, fresh fingerprint)
3. Fall back to `scripts/core.py` with different engines (e.g., `--engines google,wikipedia`)

### 5. Result Extraction
Extract result URLs from snapshot output:
```bash
snapshot 2>&1 | grep -E "link.*http" | grep -v "searx\.space\|localhost\|/preferences\|/stats\|github.com/searxng\|Source code\|Issue tracker\|Engine stats\|Public instances"
```

## Parameters (direct JSON API)

| Flag | Short | Description | Default |
|------|-------|-------------|---------|
| `--num N` | `-n` | Max results | 10 |
| `--engines` | `-e` | Comma-sep: google,bing,duckduckgo,brave | all |
| `--lang` | `-l` | Language filter: en | none |
| `--categories` | `-c` | Category: general,news,images,science | general |
| `--json` | `-j` | Raw JSON output | off |
| `--urls-only` | `-u` | URLs only (pipe to web_fetch) | off |

## Configuration

Default SearXNG endpoint: `http://localhost:8888`
Override via `SEARXNG_URL` env var:
```bash
export SEARXNG_URL="http://localhost:8888"
```

Camoufox endpoint: `http://localhost:9377`
Override via `CAMOFOX_BASE` env var.

## Engine Status

SearXNG upstream engines have varying reliability:
- **Google** — reliable, returns results (0.2–0.5s response)
- **Wikipedia** — reliable, returns results (0.4–0.8s response)
- **Brave** — frequently rate-limited ("too many requests")
- **DuckDuckGo** — frequently blocked (CAPTCHA)
- **AOL** — intermittent (HTTP protocol errors)
- **Startpage** — frequently blocked (CAPTCHA)

When direct JSON API returns 0 results with unresponsive engines, use the Camoufox path — Google/Wikipedia results render in the HTML page accessible via snapshot.

## Setup (if SearXNG not running)

See `references/setup.md` for Docker Compose setup of SearXNG.
