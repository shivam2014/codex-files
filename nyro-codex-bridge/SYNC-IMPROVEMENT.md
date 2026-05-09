# Improving Nyro's Codex CLI Sync

## Current Behavior (Broken)

When a user clicks **Sync Config** for Codex CLI on Nyro's Connect page, it:

1. Writes `config.toml` with a **single** `model = "deepseek-v4-flash-1"` entry
2. **Deletes** `nyro-models.json` if it exists
3. Result: Codex only shows one model in the dropdown

## Desired Behavior

The sync should instead:

1. Fetch **all routes** from Nyro's database
2. Generate a `nyro-models.json` with every route as a full `ModelInfo` entry
3. Write `config.toml` with `model_catalog_json` pointing at that file
4. **Keep** the `model = "..."` field for the default selection
5. Result: Codex shows all Nyro models in the dropdown

## Code Change

### File: `src-tauri/src/commands.rs`

**In the `sync_cli_config` function, `codex-cli` branch:**

```rust
"codex-cli" => {
    let auth_path = get_codex_auth_path(&home_dir);
    let config_path = get_codex_config_path(&home_dir);
    let models_path = get_codex_models_path(&home_dir);
    capture_backups_if_missing(
        &app,
        &tool,
        &[auth_path.clone(), config_path.clone(), models_path.clone()],
    )?;

    // ── Write auth.json (unchanged) ──
    let mut auth_json = if auth_path.exists() { /* ... */ };
    auth_obj.insert("OPENAI_API_KEY".to_string(), api_key.trim());
    write_json_file(&auth_path, &auth_json)?;

    // ── Write nyro-models.json (NEW) ──
    // Fetch all routes from Nyro's own database
    let all_routes = gw.admin().list_routes().await
        .map_err(|e| format!("failed to list routes: {e}"))?;

    let base_instructions = std::fs::read_to_string(
        home_dir.join(".codex").join("models_cache.json")
    ).ok().and_then(|c| {
        serde_json::from_str::<serde_json::Value>(&c).ok()
    }).and_then(|v| {
        v["models"][0]["base_instructions"].as_str().map(String::from)
    }).unwrap_or_default();

    let mut model_entries = Vec::new();
    for route in &all_routes {
        if !route.is_enabled { continue; }

        // Get capabilities if available
        let caps = gw.admin()
            .get_model_capabilities(&route.target_provider, &route.target_model)
            .await
            .ok();

        model_entries.push(serde_json::json!({
            "slug": route.virtual_model,
            "display_name": route.name,
            "description": format!("Nyro route: {} → {}/{}",
                route.virtual_model, route.target_provider, route.target_model),
            "default_reasoning_level": "medium",
            "supported_reasoning_levels": [
                {"effort": "low", "description": "Fast responses"},
                {"effort": "medium", "description": "Balanced"},
                {"effort": "high", "description": "Deeper reasoning"},
            ],
            "context_window": caps.as_ref().map(|c| c.context_window).unwrap_or(128000),
            "max_context_window": caps.as_ref().map(|c| c.context_window).unwrap_or(128000),
            "effective_context_window_percent": 95,
            "supports_parallel_tool_calls": caps.as_ref()
                .map(|c| c.tool_call).unwrap_or(true),
            "supports_search_tool": false,
            "input_modalities": caps.as_ref()
                .and_then(|c| serde_json::to_value(&c.input_modalities).ok())
                .unwrap_or(serde_json::json!(["text"])),
            "visibility": "list",
            "priority": 10,
            // Static fields cloned from a built-in template
            "shell_type": "shell_command",
            "supported_in_api": true,
            "additional_speed_tiers": [],
            "availability_nux": null,
            "upgrade": null,
            "base_instructions": &base_instructions,
            "truncation_policy": {"mode": "tokens", "limit": 10000},
            "supports_reasoning_summaries": true,
            "default_reasoning_summary": "auto",
            "support_verbosity": true,
            "default_verbosity": null,
            "apply_patch_tool_type": "freeform",
            "web_search_tool_type": "text",
            "supports_image_detail_original": false,
            "experimental_supported_tools": [],
        }));
    }

    let catalog = serde_json::json!({ "models": model_entries });
    write_json_file(&models_path, &catalog)?;

    // ── Write config.toml with model_catalog_json ──
    let config_toml = format!(
        r#"model_catalog_json = "{models_path}"
model_provider = "nyro"
model = "{normalized_model}"
model_reasoning_effort = "high"
disable_response_storage = true

[model_providers]
[model_providers.nyro]
name = "Nyro Gateway"
base_url = "{normalized_host}/v1"
wire_api = "responses"
requires_openai_auth = true
"#
    );
    write_text_file(&config_path, &config_toml)?;

    Ok(vec![
        auth_path.to_string_lossy().to_string(),
        config_path.to_string_lossy().to_string(),
        models_path.to_string_lossy().to_string(),
    ])
}
```

## Changes Required in `cliPreviewTemplate()` (Frontend)

The preview in `webui/src/pages/connect.tsx` should also reflect this:

```typescript
// BEFORE (current):
if (tool.id === "codex-cli") {
    return `# ~/.codex/auth.json
{ "OPENAI_API_KEY": "${apiKey}" }

# ~/.codex/config.toml
model_provider = "nyro"
model = "${codexModel}"
...
[model_providers.nyro]
base_url = "${codexBaseUrl}"
wire_api = "responses"
requires_openai_auth = true`;
}

// AFTER:
if (tool.id === "codex-cli") {
    return `# ~/.codex/auth.json
{ "OPENAI_API_KEY": "${apiKey}" }

# ~/.codex/config.toml
model_catalog_json = "${codexHome}/.codex/nyro-models.json"
model_provider = "nyro"
model = "${codexModel}"
...
[model_providers.nyro]
base_url = "${codexBaseUrl}"
wire_api = "responses"
requires_openai_auth = true

# ~/.codex/nyro-models.json will be auto-generated by sync
# Contains ALL Nyro routes as selectable models`;
}
```

## Benefits

| Before | After |
|--------|-------|
| Single model in dropdown | All Nyro routes in dropdown |
| `nyro-models.json` deleted | `nyro-models.json` populated with full metadata |
| User must manually add model_catalog_json | Sync does it automatically |
| Refresh requires re-running external script | Refresh = click Sync again |
