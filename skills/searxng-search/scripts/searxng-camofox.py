#!/usr/bin/env python3
"""
searxng-camofox v1.1.0 — SearXNG search via Camoufox anti-detection browser

Opens SearXNG search URLs in Camoufox, extracts result links from snapshot.
Incorporates Camoufox best practices: session cleanliness, rate limiting,
fingerprint rotation, and error handling with retries.

Usage:
  python3 searxng-camofox.py "your query"
  python3 searxng-camofox.py "your query" --num 5
  python3 searxng-camofox.py "your query" --json
  python3 searxng-camofox.py "your query" --urls-only
"""
import sys, json, urllib.parse, argparse, os, subprocess, re, time, random

VERSION = "1.1.0"

CAMOFOX_SCRIPT = os.path.expanduser(
    "~/.codex/skills/camofox-browser/scripts/camofox.sh"
)
SEARXNG_URL = os.environ.get("SEARXNG_URL", "http://localhost:8888")
MAX_RETRIES = 2
RETRY_DELAY = 3  # seconds between retries (rate limiting)

def run_camofox(args):
    """Run camofox.sh command and return stdout. Raises on failure."""
    cmd = [CAMOFOX_SCRIPT] + args
    env = os.environ.copy()
    env["CAMOFOX_HEADLESS"] = "true"
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=60)
        return result.stdout
    except subprocess.TimeoutExpired:
        print(f"[searxng-camofox] Timeout running: {' '.join(args)}", file=sys.stderr)
        return ""
    except FileNotFoundError:
        print(f"[searxng-camofox] Camoufox script not found: {CAMOFOX_SCRIPT}", file=sys.stderr)
        return ""

def extract_urls(snapshot):
    """Parse result URLs from Camoufox snapshot output."""
    urls = []
    skip_patterns = [
        "searx.space", "localhost", "/preferences", "/stats",
        "github.com/searxng", "Source code", "Issue tracker",
        "Engine stats", "Public instances",
    ]
    for line in snapshot.split("\n"):
        m = re.search(r'link "([^"]+)"', line)
        if m:
            u = m.group(1)
            if any(skip in u for skip in skip_patterns):
                continue
            if u.startswith("http") and u not in urls:
                urls.append(u)
    return urls

def search(query, num=10):
    """Search via SearXNG in Camoufox. Retries with fingerprint rotation on empty results."""
    params = {
        "q": query,
        "language": "en",
        "safesearch": "0",
        "categories": "general",
    }
    url = f"{SEARXNG_URL}/search?" + urllib.parse.urlencode(params)

    for attempt in range(MAX_RETRIES + 1):
        # Step 1: Close stale tabs for clean session (session cleanliness)
        run_camofox(["close-all"])
        time.sleep(1)

        # Step 2: Open search URL in Camoufox
        result = run_camofox(["open", url])
        if not result:
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
                continue
            return []

        # Step 3: Snapshot and extract URLs
        time.sleep(random.uniform(0.5, 1.5))  # rate limiting: human-like delay
        snapshot = run_camofox(["snapshot"])
        urls = extract_urls(snapshot)

        if urls:
            return urls[:num]

        # No results — retry with fresh session (fingerprint rotation)
        if attempt < MAX_RETRIES:
            delay = RETRY_DELAY + random.uniform(0, 1)
            print(f"[searxng-camofox] No results (attempt {attempt+1}), retrying in {delay:.0f}s...",
                  file=sys.stderr)
            time.sleep(delay)

    return []

def main():
    parser = argparse.ArgumentParser(description="SearXNG search via Camoufox")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--num", "-n", type=int, default=10, help="Max results")
    parser.add_argument("--json", "-j", action="store_true", help="JSON output")
    parser.add_argument("--urls-only", "-u", action="store_true", help="URLs only")
    args = parser.parse_args()

    urls = search(args.query, args.num)

    if args.urls_only:
        for u in urls:
            print(u)
    elif args.json:
        print(json.dumps({"query": args.query, "results": urls}, indent=2))
    else:
        if urls:
            print(f"Results for: {args.query}\n")
            for i, u in enumerate(urls, 1):
                print(f"  {i:2d}. {u}")
        else:
            print(f"No results found for: {args.query}")
            print("Tip: Try the direct JSON API fallback:")
            print(f"  python3 scripts/core.py \"{args.query}\"")

if __name__ == "__main__":
    main()
