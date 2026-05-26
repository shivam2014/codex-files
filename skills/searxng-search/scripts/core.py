#!/usr/bin/env python3
"""
searxng-search v1.0.0 — SearXNG search for Codex

Searches web via self-hosted SearxNG meta-search engine.
Aggregates Google, Bing, DuckDuckGo, Brave, and 70+ engines.

Usage:
  python3 core.py "query"
  python3 core.py "query" --num 5
  python3 core.py "AI news" --categories news
  python3 core.py "query" --lang en
  python3 core.py "query" --urls-only
  python3 core.py "query" --json

Environment:
  SEARXNG_URL   SearxNG endpoint (default: http://localhost:8888)
"""
import sys, json, urllib.parse, argparse, os, subprocess

VERSION = "1.0.0"

def _search_url():
    base = os.environ.get("SEARXNG_URL", "http://localhost:8888")
    return base.rstrip("/") + "/search"

def search(query, num=10, engines=None, lang=None, categories=None):
    """Execute search via SearXNG JSON API. Returns list of result dicts."""
    params = {"q": query, "format": "json", "pageno": 1}
    if engines:    params["engines"] = engines
    if lang:       params["language"] = lang
    if categories: params["categories"] = categories

    url = _search_url() + "?" + urllib.parse.urlencode(params)
    result = subprocess.run(
        ["curl", "-s", "--max-time", "15", url],
        capture_output=True, text=True, timeout=20
    )
    if result.returncode != 0:
        raise RuntimeError(f"curl failed: {result.stderr[:200]}")
    data = json.loads(result.stdout)
    return data.get("results", [])[:num]

def fmt_results(results, urls_only=False):
    """Format results for terminal display."""
    if urls_only:
        return "\n".join(r.get("url", "") for r in results)
    lines = []
    for i, r in enumerate(results, 1):
        title   = r.get("title", "").strip()
        url     = r.get("url", "")
        content = r.get("content", "").strip()
        engines = ",".join(r.get("engines", []))
        lines.append(f"[{i}] {title}")
        lines.append(f"    {url}")
        if content: lines.append(f"    {content[:300]}")
        if engines: lines.append(f"    [{engines}]")
        lines.append("")
    return "\n".join(lines).strip()

def main():
    p = argparse.ArgumentParser(description="SearXNG search for Codex")
    p.add_argument("query")
    p.add_argument("--num",        "-n", type=int, default=10, help="Max results (default 10)")
    p.add_argument("--engines",    "-e", help="Comma-separated: google,bing,duckduckgo,brave")
    p.add_argument("--lang",       "-l", help="Language filter: en, zh-CN, ja, ko")
    p.add_argument("--categories", "-c", help="Category: general,news,images,science")
    p.add_argument("--json",       "-j", action="store_true", help="Raw JSON output")
    p.add_argument("--urls-only",  "-u", action="store_true", help="URLs only")
    p.add_argument("--version",    "-V", action="version", version=f"searxng-search {VERSION}")
    args = p.parse_args()

    try:
        results = search(args.query, args.num, args.engines, args.lang, args.categories)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

    if not results:
        print(json.dumps({"error": "No results", "query": args.query}))
        sys.exit(1)

    if args.json:
        print(json.dumps({"query": args.query, "results": results}, ensure_ascii=False, indent=2))
    else:
        print(fmt_results(results, args.urls_only))

if __name__ == "__main__":
    main()
