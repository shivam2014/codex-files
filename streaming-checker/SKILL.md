---
name: streaming-checker
description: Check which streaming services and regions carry a TV show or movie. Use when a user asks where a title is available for streaming, which countries have it on a specific platform (e.g. Prime Video, Netflix), or to compare availability across regions.
---

# Streaming Checker

## Quick start

```bash
python3 scripts/check_streaming.py "Show Name"
python3 scripts/check_streaming.py "Show Name" --provider "Prime Video"
python3 scripts/check_streaming.py "Show Name" --countries us,gb,mx,br
```

Checks JustWatch across 15+ countries in ~2–5 seconds.

## How it works

Uses `AsyncStealthySession` (Scrapling) to fetch JustWatch show pages for multiple countries in parallel, then extracts provider names from JSON-LD structured data embedded in each page. JSON-LD is the authoritative source — no text heuristics, no false positives.

### Slug resolution

The script normalizes the query (lowercase, hyphens) and tests it on `justwatch.com/us/tv-show/{slug}`. If that 404s, it searches JustWatch and extracts the correct slug from search results.

### URL patterns

| Country group | Path |
|---|---|
| English-speaking | `justwatch.com/{cc}/tv-show/{slug}` |
| Spanish-speaking | `justwatch.com/{cc}/serie/{slug}` |
| Portuguese-speaking | `justwatch.com/{cc}/serie/{slug}` |

### Country codes (default)

`us gb ca mx br ar co cl pe es de fr it au`

## Usage examples

```bash
# Which countries have this show on Prime Video?
python3 check_streaming.py "the boys" --provider "Prime Video"

# Check specific countries only
python3 check_streaming.py "squid game" --countries us,gb,ca,au
python3 check_streaming.py "squid game" --countries us --provider "Netflix"

# Movie titles work too
python3 check_streaming.py "the matrix"
```

## Prerequisites

- Scrapling installed: `python3 -m pip install "scrapling[all]>=0.4.7"`
- Playwright Chromium: `python3 -m playwright install chromium`

Both are already installed on this machine.

## Notes

- Some titles use localized slugs (e.g. in Germany, France) that differ from the English name. If a country returns "Not available" but you expect it should have the title, the slug may differ — try searching JustWatch directly.
- The script uses `max_pages=3` (3 browser tabs) to parallelize. This can be increased for faster multi-country checks.
