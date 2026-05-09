# Nyro Router: Current Architecture & Suggested Improvements

Based on my analysis of the Nyro source code (`nyro-mod/nyro-src`) and
the Codex integration experience, here's a walkthrough of the current
routing design, where the friction points are, and what I'd change.

---

## Current Architecture (What Nyro Does Today)

### Route Model

Nyro routes are database-backed objects with a flat target structure:

```
Route
├── id                  # UUID
├── name                # Human label ("DeepSeek Flash")
├── virtual_model       # Public model name clients send ("deepseek-v4-flash-1")
├── strategy            # "weighted" | "priority"
├── route_type          # "chat" | "embedding"
├── access_control      # Bool: require bound API key?
├── cache               # Per-route cache config (exact + semantic)
├── is_enabled
└── targets[]
    ├── provider_id     # Foreign key to Provider table
    ├── model           # Upstream model name
    ├── weight          # For weighted strategy
    └── priority        # For priority strategy
```

Matching is exact: `routes.iter().find(|r| r.virtual_model == request.model)`.

Two strategies:
- **Weighted**: Random shuffle with weight bias. Good for cost/load distribution.
- **Priority**: Ordered by priority field. Primary → Fallback → ... Good for HA.
  No health-check awareness — dead upstreams stay in the pool until a request
  fails.

### Data Flow

```
Client → POST /v1/responses { model: "deepseek-v4-flash-1" }
         ↓
       RouteCache.match_route("deepseek-v4-flash-1")
         ↓
       TargetSelector.select_ordered("weighted", targets)
         ↓
       ProxyClient → POST Provider.base_url/v1/... { model: "deepseek-chat" }
         ↓
       Response transcoded back to ingress protocol → Client
```

### What Stores Routes

| Source | Backend | When used |
|--------|---------|-----------|
| Admin API (port 19531) | SQLite / Postgres | Interactive mode |
| YAML config file | Static file | Standalone mode (no DB) |
| Presets | Hardcoded in binary | First-run onboarding |

---

## Friction Points (Discovered During Codex Integration)

### 1. Model Listing Is Too Sparse

`GET /v1/models` currently returns:

```json
{"id": "deepseek-v4-flash-1", "object": "model", "created": 0, "owned_by": "Nyro"}
```

But Codex, Claude, and other OpenAI-compatible clients expect — or at least
benefit from — full metadata:

```json
{
  "id": "deepseek-v4-flash-1",
  "object": "model",
  "created": 1700000000,
  "owned_by": "Nyro",
  "context_window": 1000000,
  "max_output_tokens": 32768,
  "capabilities": {
    "tool_call": true,
    "reasoning": true,
    "input_modalities": ["text"],
    "supports_parallel_tool_calls": true
  }
}
```

**Why it matters:** Codex's `OpenAiModelsManager` fetches `GET /models`
from the provider and expects to map the response into its internal
`ModelInfo` struct. When Nyro returns only `{id, object, created, owned_by}`,
Codex can't populate the 29 fields it needs, so the models get silently
dropped from the dropdown.

**Nyro actually has this data** — the provider model discovery endpoint
(`/api/v1/providers/:id/models`) and capability endpoint
(`/api/v1/providers/:id/model-capabilities`) already fetch capability info
from upstream APIs like models.dev. It's just not exposed through the
proxy's `/v1/models` endpoint.

### 2. No Model Capability Cache on Routes

When a route is created, Nyro stores `target_provider` and `target_model`
but doesn't snapshot what that model can do. This means:

- `/v1/models` can't answer "what context window does this model have?"
  without live-querying the provider at request time.
- The web UI fetches capabilities asynchronously via
  `/api/v1/providers/:id/model-capabilities?model=...` — this works but adds
  latency to the UI and can't be used for the proxy path.

### 3. Route Matching Has No Prefix / Wildcard

The matcher does exact string match only:

```rust
pub fn match_route<'a>(routes: &'a [Route], model: &str) -> Option<&'a Route> {
    routes.iter().find(|route| route.virtual_model == model)
}
```

This means you can't do:
- Prefix routing: `deepseek-*` → DeepSeek provider
- Version aliasing: `gpt-5` → `gpt-5.4` (latest)
- Dynamic routing: `claude-sonnet-4-*` → any available Claude Sonnet 4 target

Every model ID the client sends must exactly match a `virtual_model` in the
database. For gateway operators managing dozens of models, this is a lot of
bookkeeping.

### 4. Target Selection Is Passive (No Health Awareness)

Both `weighted` and `priority` strategies assume every target is healthy.
There's no:
- Periodic health check pinging upstream providers
- Circuit breaker after N failures
- Automatic removal of dead targets from the selection pool
- Degradation reporting through `/v1/models` or health endpoint

### 5. Protocol Negotiation Is Implicit

The route doesn't know what protocol upstream speaks — it relies on the
provider's `default_protocol` field and the provider's `endpoints` map.
This works but makes it hard to:
- Route to different protocol versions per model
- Support new protocols without changing the route schema
- Debug protocol mismatch issues (e.g., Anthropic vs OpenAI format)

---

## Suggested Improvements

### A. Enrich `/v1/models` With Capability Data

**What:** When Nyro builds the model list for `GET /v1/models`, merge in the
capability data Nyro already fetches from `models.dev` during provider setup.

**Where:** `crates/nyro-core/src/proxy/handler.rs` — `models_list()` function.

**BEFORE (current):**

```rust
let data = models
    .into_iter()
    .map(|model| {
        serde_json::json!({
            "id": model,
            "object": "model",
            "created": 0,
            "owned_by": "Nyro"
        })
    })
    .collect::<Vec<_>>();
```

**AFTER (suggested):**

```rust
let data = models
    .into_iter()
    .map(|model| {
        let caps = gw.admin().get_model_capabilities_for_route(&model).await;
        serde_json::json!({
            "id": model,
            "object": "model",
            "created": caps.created_at.unwrap_or(0),
            "owned_by": "Nyro",
            "context_window": caps.context_window,
            "max_output_tokens": caps.max_output_tokens,
            "capabilities": {
                "tool_call": caps.tool_call,
                "reasoning": caps.reasoning,
                "input_modalities": caps.input_modalities,
                "supports_parallel_tool_calls": caps.supports_parallel_tool_calls,
            }
        })
    })
    .collect::<Vec<_>>();
```

**Why:** Codex's `ModelsClient.list_models()` would receive enough metadata
to populate the dropdown. Claude and other OpenAI clients also benefit from
richer model info.

### B. Snapshot Capabilities on Route Create/Update

**What:** When a route is created or its target model changes, fetch
capabilities from `models.dev` (or probe the provider) and store them on
the route itself — a `capabilities` JSON column or a separate
`route_model_capabilities` table.

**Where:** `crates/nyro-core/src/admin/mod.rs` — `create_route()` and
`update_route()` handlers.

**BEFORE:**

```
No capability data stored on route.
```

**AFTER:**

```rust
// During route creation
let caps = fetch_model_capabilities(&provider, &target_model).await;
// Store alongside route
INSERT INTO route_capabilities (route_id, context_window, tool_call,
  reasoning, input_modalities, snapshot_at)
VALUES ($1, $2, $3, $4, $5, NOW());
```

**Why:** Makes `/v1/models` fast (no live queries) and gives the admin UI
immediate access to capability info without async loading.

### C. Add Prefix / Glob Matching to Route Matcher

**What:** Support wildcard suffixes (`deepseek-*`) and ordered lookup
(exact match → prefix match → fallback).

**Where:** `crates/nyro-core/src/router/matcher.rs`

**BEFORE:**

```rust
pub fn match_route<'a>(routes: &'a [Route], model: &str) -> Option<&'a Route> {
    routes.iter().find(|route| route.virtual_model == model)
}
```

**AFTER:**

```rust
pub fn match_route<'a>(routes: &'a [Route], model: &str) -> Option<&'a Route> {
    // 1. Try exact match first
    if let Some(route) = routes.iter().find(|r| r.virtual_model == model) {
        return Some(route);
    }
    // 2. Try prefix/wildcard match (deepseek-* → deepseek- prefix)
    let wildcard_routes: Vec<&Route> = routes.iter()
        .filter(|r| r.virtual_model.ends_with('*'))
        .collect();
    for route in &wildcard_routes {
        let prefix = route.virtual_model.trim_end_matches('*');
        if model.starts_with(prefix) {
            return Some(route);
        }
    }
    // 3. Fallback to default route (if any)
    routes.iter().find(|r| r.virtual_model == "*")
}
```

**Why:** Reduces route count — one `deepseek-*` route covers all DeepSeek
model IDs instead of needing N explicit entries. This is the pattern used
by most production gateways (Kong, Envoy, Azure).

### D. Add Health-Aware Target Selection

**What:** Track per-target health with exponential backoff. Remove unhealthy
targets from selection until they recover.

**Where:** New module `crates/nyro-core/src/router/health.rs` (already exists
as a stub).

```rust
pub struct HealthTracker {
    failures: HashMap<String, FailureState>,
    config: HealthConfig,
}

struct FailureState {
    consecutive_failures: u32,
    last_failure: Instant,
    backoff_until: Option<Instant>,
}

impl HealthTracker {
    pub fn record_failure(&mut self, target_id: &str) {
        let state = self.failures.entry(target_id.to_string()).or_default();
        state.consecutive_failures += 1;
        state.last_failure = Instant::now();
        let backoff = self.config.base_delay * 2u64.pow(state.consecutive_failures.min(6));
        state.backoff_until = Some(Instant::now() + backoff);
    }

    pub fn is_healthy(&self, target_id: &str) -> bool {
        match self.failures.get(target_id) {
            None => true,
            Some(state) => match state.backoff_until {
                Some(until) => Instant::now() >= until,
                None => true,
            }
        }
    }
}
```

Then integrate into `TargetSelector`:

```rust
pub fn select_ordered(strategy: &str, targets: &[RouteTarget],
                      health: &HealthTracker) -> Vec<SelectedTarget> {
    let healthy: Vec<_> = targets.iter()
        .filter(|t| health.is_healthy(&t.id))
        .collect();
    // ... existing weighted/priority logic on healthy subset
}
```

### E. Add Protocol Constraints to Routes

**What:** Let a route declare which protocol it expects, instead of
relying on the provider's default. This makes it possible to route the
same virtual model through different protocol adapters.

**Suggested schema addition:**

```
ALTER TABLE routes ADD COLUMN protocol_constraint TEXT;
```

When set, the proxy uses this protocol for all targets instead of the
provider's default. When unset, behavior is unchanged (uses provider default).

---

## Summary

| Area | Current | Suggested | Benefit |
|------|---------|-----------|---------|
| `/v1/models` | `{id, created, owned_by}` | Full capability metadata | Codex/Claude auto-discovery works |
| Capabilities | Live-fetched at UI time | Snapshot on route save | Fast API, offline-capable |
| Route matching | Exact string only | Prefix + wildcard + fallback | Fewer routes, flexible |
| Target health | None assumed | Circuit breaker + backoff | Reliable routing |
| Protocol binding | Implicit (provider default) | Optional per-route constraint | Multi-protocol, explicit |
