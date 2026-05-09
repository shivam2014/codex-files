---
name: camofox-browser
description: "Headless browser automation via Camofox (Firefox-based) running on localhost:9377. Navigate, click, type, scroll, extract page content with accessibility snapshots."
---

# Camofox Browser (localhost:9377)

Headless browser automation server. Firefox-based with anti-detection (Camoufox).

## 🚨 If Server is Not Reachable

If `http://localhost:9377` doesn't respond, start the services:

```bash
cd ~/qwen-gguf && ./start_llama_turboquant_stable.sh --no-llama
```

This starts both Camofox browser (port 9377) and SearXNG (port 8888).

## Health Check

```bash
curl -s http://localhost:9377/
# Returns: {"ok":true,"enabled":true,"running":false,"engine":"camoufox","browserConnected":false,"browserRunning":false}
```

## API Reference

### Create a Tab
```bash
curl -s -X POST http://localhost:9377/tabs \
  -H "Content-Type: application/json" \
  -d '{"userId": "codex", "sessionKey": "task1", "url": "https://example.com"}'
# Returns: {"tabId": "abc123", "url": "...", "title": "..."}
```

### Navigate
```bash
curl -s -X POST http://localhost:9377/tabs/<tabId>/navigate \
  -H "Content-Type: application/json" \
  -d '{"userId": "codex", "url": "https://google.com"}'
```

### Get Page Snapshot (Accessibility Tree)
```bash
curl -s "http://localhost:9377/tabs/<tabId>/snapshot?userId=codex"
# Returns structure like:
# [heading] Page Title
# [link e1] Click here
```

### Click Element
```bash
curl -s -X POST http://localhost:9377/tabs/<tabId>/click \
  -H "Content-Type: application/json" \
  -d '{"userId": "codex", "ref": "e1"}'
# Or by CSS selector:
# -d '{"userId": "codex", "selector": "button.submit"}'
```

### Type Text
```bash
curl -s -X POST http://localhost:9377/tabs/<tabId>/type \
  -H "Content-Type: application/json" \
  -d '{"userId": "codex", "ref": "e2", "text": "search query", "pressEnter": true}'
```

### Scroll
```bash
curl -s -X POST http://localhost:9377/tabs/<tabId>/scroll \
  -H "Content-Type: application/json" \
  -d '{"userId": "codex", "direction": "down", "amount": 500}'
```

### Navigation Controls
```bash
curl -s -X POST http://localhost:9377/tabs/<tabId>/back     -H "Content-Type: application/json" -d '{"userId": "codex"}'
curl -s -X POST http://localhost:9377/tabs/<tabId>/forward  -H "Content-Type: application/json" -d '{"userId": "codex"}'
curl -s -X POST http://localhost:9377/tabs/<tabId>/refresh  -H "Content-Type: application/json" -d '{"userId": "codex"}'
```

### Get Links
```bash
curl -s "http://localhost:9377/tabs/<tabId>/links?userId=codex&limit=50"
```

### Close Tab / Session
```bash
curl -s -X DELETE "http://localhost:9377/tabs/<tabId>?userId=codex"
curl -s -X DELETE "http://localhost:9377/sessions/codex"
```

## Search Macros (built-in)

Use with navigate: `{"macro": "@google_search", "query": "..."}`

| Macro | Site |
|-------|------|
| `@google_search` | Google |
| `@youtube_search` | YouTube |
| `@amazon_search` | Amazon |
| `@reddit_search` | Reddit |
| `@wikipedia_search` | Wikipedia |
| `@twitter_search` | Twitter/X |

## Standard Workflow

1. **POST /tabs** → get `tabId`
2. **POST /tabs/{tabId}/navigate** (or use macro)
3. **GET /tabs/{tabId}/snapshot** → page content with element refs
4. **POST /tabs/{tabId}/click** or **/type** using refs
5. Repeat snapshot + interact as needed
6. **DELETE /tabs/{tabId}** when done

## When to use

- Pages needing JavaScript rendering (SPA, React)
- Form filling and button clicking
- Sites with anti-bot protection
- Full page content extraction with interactive elements
