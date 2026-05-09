# Nyro ↔ Codex Model Bridge

Connects [Nyro](https://github.com/nyro-ai/nyro) (local AI gateway) to
[Codex CLI](https://github.com/openai/codex) so every route you define in Nyro
shows up automatically in Codex's model dropdown.

## Problem

Codex's model dropdown (via `model/list`) is normally populated by the
`models_cache.json` file fetched from OpenAI's API — only GPT models appear.
When you configure a custom provider like Nyro, Codex does try to call
`GET {base_url}/models` for auto-discovery, but the response format (OpenAI's
minimal `{id, object, created}`) doesn't carry the 29-field `ModelInfo`
structure Codex requires, so the models are silently dropped.

## Solution

Codex exposes a config key `model_catalog_json` (documented at
[developers.openai.com/codex/config-reference](https://developers.openai.com/codex/config-reference)):

> `model_catalog_json` — string (path) — Optional path to a JSON model catalog
> loaded on startup. Profile-level `profiles.<name>.model_catalog_json` can
> override this per profile.

This **replaces** the built-in model list with whatever you put in the file.
So the script here merges both the built-in models (from `models_cache.json`)
and the Nyro models (from `GET /v1/models`) into a single catalog.

## Files

| File | Location | Purpose |
|------|----------|---------|
| `generate-nyro-catalog.py` | `~/.cache/generate-nyro-catalog.py` | Fetches Nyro + built-in models, writes merged catalog |
| `nyro-codex-models.json` | `~/.cache/nyro-codex-models.json` | The merged catalog consumed by Codex |
| `config.toml` snippet | see below | One-liner to wire the catalog into Codex |

## Setup

### 1. Install the script

```bash
cp generate-nyro-catalog.py ~/.cache/
```

### 2. Make sure Nyro is running

The script calls `GET http://localhost:19530/v1/models`. If Nyro isn't running,
it gracefully falls back to built-in models only.

### 3. Generate the catalog

```bash
python3 ~/.cache/generate-nyro-catalog.py
```

Expected output:
```
Built-in models: 8
Nyro models: 7
Wrote 15 models (7 Nyro)
  to /Users/shivam94/.cache/nyro-codex-models.json
```

### 4. Wire it into Codex

Add to `~/.codex/config.toml` at the **very top** (before any `[...]` table
headers):

```toml
model_catalog_json = "/Users/shivam94/.cache/nyro-codex-models.json"
model_provider = "nyro"
model = "deepseek-v4-flash-1"
model_reasoning_effort = "high"
disable_response_storage = true

[model_providers]
...
```

> **TOML placement is critical.** Once a `[table]` header appears, you cannot
> add top-level keys below it. `model_catalog_json` must come before the first
> `[...]` line.

### 5. Restart Codex

The catalog is read once at startup. Your Nyro routes appear alongside the
built-in OpenAI models in the dropdown.

## Updating (when Nyro routes change)

```bash
# Make sure Nyro is running
python3 ~/.cache/generate-nyro-catalog.py
# Restart Codex
```

No config changes needed — the output path stays the same.

## How It Works — Data Flow

```
Nyro :19530                    Script                          Codex :19530
┌──────────────┐              ┌──────────────────┐            ┌───────────────────┐
│ GET /v1/models│──JSON──→    │ 1. Fetch Nyro    │            │ ~/.codex/         │
│ { id,         │  7 models   │    routes         │            │   config.toml     │
│   max_context_│              │ 2. Load built-in │            │   model_catalog_  │
│   length }    │              │    models from   │            │   json = "..."    │
└──────────────┘              │    models_cache  │──reads──→  │                   │
                              │ 3. Merge →       │            │ ~/.cache/         │
                              │    ModelInfo[]    │──writes──→ │   nyro-codex-     │
                              │ 4. Save as        │            │   models.json     │
                              │    ModelsResponse │            │                   │
                              └──────────────────┘            │ StaticModels      │
                                                               │ Manager           │
                                                               │ → dropdown        │
                                                               └───────────────────┘
```

## Internals — Why This Works

Looking at Codex's Rust source (`model-provider/src/provider.rs`), the model
manager is selected like this:

```rust
fn models_manager(&self, codex_home: PathBuf,
                  config_model_catalog: Option<ModelsResponse>) {
    match config_model_catalog {
        Some(catalog) => Arc::new(StaticModelsManager::new(catalog)),
        //        ^^ When model_catalog_json is set,
        //           Codex uses this branch
        None => {
            let endpoint = OpenAiModelsEndpoint::new(...);
            Arc::new(OpenAiModelsManager::new(endpoint))
            //        ^^ Default: fetches /models from provider,
        }              //           but expects full ModelInfo format
    }
}
```

The default path (`OpenAiModelsManager`) calls `GET {base_url}/models` but
expects Codex's `ModelInfo` format — not the minimal OpenAI list format that
Nyro returns. The `StaticModelsManager` path avoids this by serving a
pre-built catalog that already has all required fields.

Each `ModelInfo` entry in the catalog must carry all 29 fields that Codex's
deserializer expects:

```
slug, display_name, description, default_reasoning_level,
supported_reasoning_levels, shell_type, visibility, supported_in_api,
priority, additional_speed_tiers, availability_nux, upgrade,
base_instructions, model_messages, supports_reasoning_summaries,
default_reasoning_summary, support_verbosity, default_verbosity,
apply_patch_tool_type, web_search_tool_type, truncation_policy,
supports_parallel_tool_calls, supports_image_detail_original,
context_window, max_context_window, effective_context_window_percent,
experimental_supported_tools, input_modalities, supports_search_tool
```

The script clones these from `models_cache.json` (which always has them) and
only overrides `slug`, `display_name`, `description`, `context_window`, and
`visibility` for Nyro entries.

## Troubleshooting

**Q: Codex stripped `model_catalog_json` from my config!**
A: Two possible causes:
1. You placed it after a `[table]` header — move it to the very top.
2. The catalog file failed to parse — check it with `python3 -m json.tool`.

**Q: No Nyro models in dropdown, only OpenAI ones.**
A: Nyro wasn't running when you ran the script. Re-run with Nyro up.

**Q: "No such file or directory" on startup.**
A: The catalog file was deleted. Re-run the generate script.

**Q: Can I debug what models Codex sees?**
A: Yes — this doesn't start a session, just prints the model catalog:
```bash
codex debug models -c 'model_catalog_json=/Users/shivam94/.cache/nyro-codex-models.json'
```
