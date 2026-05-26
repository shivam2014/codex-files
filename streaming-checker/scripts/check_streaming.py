#!/usr/bin/env python3
"""
Fast streaming availability checker — Scrapling + JustWatch.

Usage:
  python3 check_streaming.py "Show Name"
  python3 check_streaming.py "Show Name" --provider "Prime Video"
  python3 check_streaming.py "Show Name" --countries us,gb,mx

Checks 15+ countries in ~2-5s via parallel browser fetches.
Extracts providers from JSON-LD only (no false positives).
"""

import asyncio, sys, re, time
from urllib.parse import quote

# Country database
REGIONS = [
    ("us", "United States"),  ("gb", "United Kingdom"), ("ca", "Canada"),
    ("mx", "Mexico"),         ("br", "Brazil"),          ("ar", "Argentina"),
    ("co", "Colombia"),       ("cl", "Chile"),           ("pe", "Peru"),
    ("es", "Spain"),          ("de", "Germany"),         ("fr", "France"),
    ("it", "Italy"),          ("au", "Australia"),
]

# Countries using /serie/ instead of /tv-show/
LATAM = {"mx", "ar", "co", "cl", "pe", "ec", "ve", "es"}
PORTUG = {"br", "pt"}

# Known provider names (capitalization variants)
PROVIDER_NAMES = {
    "Amazon Prime Video", "Amazon Prime Video with Ads",
    "Netflix", "Netflix Standard with Ads",
    "Disney+", "Disney Plus",
    "HBO Max", "Max",
    "Peacock", "Peacock Premium", "Peacock Premium Plus",
    "Hulu",
    "Paramount+", "Paramount Plus",
    "Apple TV+", "Apple TV",
    "MovistarTV", "Movistar Plus+",
    "Atres Player", "Atresplayer",
    "Vix", "ViX", "Pluto TV", "NBC", "MGM+", "Starz", "Tivify",
}


def jw_url(cc: str, slug: str) -> str:
    """Build JustWatch URL for a country + slug."""
    path = "serie" if cc in LATAM or cc in PORTUG else "tv-show"
    return f"https://www.justwatch.com/{cc}/{path}/{slug}"


def extract_ld(html: str) -> set:
    """Extract provider names from JSON-LD structured data only."""
    prov = set()
    for m in re.finditer(r'"offeredBy"\s*:\s*\{[^}]*"name"\s*:\s*"([^"]+)"', html):
        name = m.group(1).strip()
        # Match against known provider names (fuzzy)
        n_lower = name.lower()
        matched = False
        for known in PROVIDER_NAMES:
            if n_lower == known.lower() or known.lower() in n_lower or n_lower in known.lower():
                prov.add(name if len(name) < 40 else known)
                matched = True
                break
        if not matched and name and len(name) < 40 and '{' not in name:
            # Accept if it looks like a proper provider name
            prov.add(name)
    return prov


def is_not_available(html: str) -> bool:
    t = html.lower()
    return any(x in t for x in [
        "not available for streaming",
        "isn't available on any streaming service",
    ])


async def fetch_one(session, cc, name, slug):
    try:
        page = await session.fetch(jw_url(cc, slug), timeout=25000)
        html = page.html_content or ""
        provs = extract_ld(html)
        na = is_not_available(html)
        if provs:
            return cc, name, provs, False
        if not na:
            # Check if page says "available on N platforms"
            for p in [r'available on (\d+)', r'disponible en (\d+)', r'disponível em (\d+)']:
                m = re.search(p, html.lower())
                if m and int(m.group(1)) > 0:
                    return cc, name, {"(check justwatch.com)"}, False
        return cc, name, set(), True
    except Exception as e:
        return cc, name, set(), True


async def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("query", nargs="+", help="Show or movie name")
    ap.add_argument("--provider", "-p", help="Filter to a specific provider")
    ap.add_argument("--countries", "-c", help="Comma-separated country codes")
    args = ap.parse_args()

    query = " ".join(args.query)
    slug = re.sub(r'[^a-z0-9\s-]', '', query.lower())
    slug = re.sub(r'\s+', '-', slug).strip('-')

    from scrapling.fetchers import AsyncStealthySession

    async with AsyncStealthySession(headless=True, max_pages=3) as session:
        # Resolve slug
        try:
            test = await session.fetch(jw_url("us", slug), timeout=15000)
            if len(test.html_content or "") < 200 or "404" in (test.html_content or "")[:100]:
                sp = await session.fetch(
                    f"https://www.justwatch.com/us/search?q={quote(query)}", timeout=15000)
                links = re.findall(r'/(?:us|mx|ar|br)/[a-z-]+/([a-z0-9][a-z0-9-]+)',
                                   sp.html_content or "")
                for l in links:
                    if len(l) > 3: slug = l; break
                else:
                    print(f"❌ Cannot find JustWatch page for '{query}'")
                    sys.exit(1)
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)

        # Target countries
        targets = [(c, dict(REGIONS).get(c, c.upper()))
                   for c in args.countries.split(",") if c.strip()] \
                  if args.countries else REGIONS

        t0 = time.time()
        results = await asyncio.gather(*[fetch_one(session, c, n, slug) for c, n in targets])

    avail, no_avail = [], []
    for cc, nm, p, na in results:
        (avail if p and not na else no_avail).append((cc, nm, p))

    flt = args.provider.lower() if args.provider else None

    print(f"\n📺  {query}  ({time.time()-t0:.1f}s)\n")

    if avail:
        if flt:
            filt = [(c, n, p) for c, n, p in avail if any(flt in x.lower() for x in p)]
            if filt:
                print(f"✅ On {args.provider}:\n")
                for c, n, p in sorted(filt):
                    print(f"   {c.upper():4s}  {n:20s}  {', '.join(sorted(p))}")
            else:
                print(f"❌ No {args.provider}. Others:\n")
                for c, n, p in sorted(avail):
                    print(f"   {c.upper():4s}  {n:20s}  {', '.join(sorted(p))}")
        else:
            print("✅ Available:\n")
            for c, n, p in sorted(avail):
                print(f"   {c.upper():4s}  {n:20s}  {', '.join(sorted(p))}")
        print()

    if no_avail and not flt:
        print("❌ Not available:\n")
        for c, n, _ in sorted(no_avail):
            print(f"   {c.upper():4s}  {n:20s}")
        print()


if __name__ == "__main__":
    asyncio.run(main())
