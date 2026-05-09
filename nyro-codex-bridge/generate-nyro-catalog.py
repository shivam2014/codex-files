#!/usr/bin/env python3
"""
Generate a Codex model catalog combining built-in + Nyro models.
Output replaces the default dropdown entirely.
Usage:
    1. Make sure Nyro is running
    2. python3 generate-nyro-catalog.py
    3. Add to ~/.codex/config.toml:
         model_catalog_json = "/Users/shivam94/.cache/nyro-codex-models.json"
    4. Restart Codex
"""
import json, urllib.request, sys, os

CACHE_DIR = os.path.expanduser("~/.cache")
os.makedirs(CACHE_DIR, exist_ok=True)

NYRO_URL = "http://localhost:19530/v1/models"
CACHE_FILE = os.path.expanduser("~/.codex/models_cache.json")
OUTPUT = os.path.join(CACHE_DIR, "nyro-codex-models.json")

# Load built-in models as templates  
try:
    with open(CACHE_FILE) as f:
        cache = json.load(f)
    builtin_models = cache["models"]
    print(f"Built-in models: {len(builtin_models)}", file=sys.stderr)
except Exception as e:
    print(f"Error reading {CACHE_FILE}: {e}", file=sys.stderr)
    sys.exit(1)

template = builtin_models[0]

# Fetch Nyro models
nyro_entries = []
try:
    resp = urllib.request.urlopen(NYRO_URL, timeout=5)
    data = json.loads(resp.read())
    nyro_entries = data.get("data", [])
    print(f"Nyro models: {len(nyro_entries)}", file=sys.stderr)
except Exception as e:
    print(f"Warning: could not fetch Nyro models: {e}", file=sys.stderr)

nyro_models = []
for entry in nyro_entries:
    mid = entry["id"]
    ctx = entry.get("max_context_length", 128000)
    model = dict(template)
    model.update({
        "slug": mid, "display_name": mid,
        "description": f"Nyro: {mid}",
        "priority": 10, "visibility": "list",
        "context_window": ctx, "max_context_window": ctx,
        "availability_nux": None, "upgrade": None,
    })
    nyro_models.append(model)

all_models = builtin_models + nyro_models
with open(OUTPUT, "w") as f:
    json.dump({"models": all_models}, f, indent=2)

print(f"Wrote {len(all_models)} models ({len(nyro_models)} Nyro)", file=sys.stderr)
print(f"  to {OUTPUT}", file=sys.stderr)
