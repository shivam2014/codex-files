#!/usr/bin/env python3
"""
searxng-camofox v1.0.0 — SearXNG search via Camoufox browser

Opens SearXNG search URLs in Camoufox anti-detection browser,
extracts result links from the accessibility snapshot.

Usage:
  python3 searxng-camofox.py "your query"
  python3 searxng-camofox.py "your query" --num 5
"""
import sys, json, urllib.parse, argparse, os, subprocess, re

VERSION = "1.0.0"

CAMOFOX_SCRIPT = os.path.expanduser(
    "~/.codex/skills/camofox-browser/scripts/camofox.sh"
)
SEARXNG_URL = os.environ.get("SEARXNG_URL", "http://localhost:8888")

def run_camofox(args):
    """Run camofox.sh command and return stdout."""
    cmd = [CAMOFOX_SCRIPT] + args
    env = os.environ.copy()
    env["CAMOFOX_HEADLESS"] = "true"
    result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=60)
    return result.stdout

def search(query, num=10):
    """Search via SearXNG in Camoufox browser, extract URLs."""
    # Build SearXNG search URL
    params = {
        "q": query,
        "language": "en",
        "safesearch": "0",
        "categories": "general",
    }
    url = f"{SEARXNG_URL}/search?" + urllib.parse.urlencode(params)

    # Close old tabs, open search URL
    run_camofox(["close-all"])
    result = run_camofox(["open", url])

    # Snapshot and extract result links
    snapshot = run_camofox(["snapshot"])

    # Parse out URLs from article links
    urls = []
    for line in snapshot.split("\n"):
        m = re.search(r'link "([^"]+)"', line)
        if m:
            u = m.group(1)
            # Filter out navigation/internal links
            if any(skip in u for skip in [
                "searx.space", "localhost", "/preferences", "/stats",
                "github.com/searxng", "Source code",
            ]):
                continue
            if u.startswith("http") and u not in urls:
                urls.append(u)

    return urls[:num]

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
        print(f"Results for: {args.query}\n")
        for i, u in enumerate(urls, 1):
            print(f"  {i:2d}. {u}")

if __name__ == "__main__":
    main()
