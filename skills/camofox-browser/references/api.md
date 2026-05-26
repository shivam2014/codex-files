# Camofox Browser REST API (port 9377)

## Base URL
http://127.0.0.1:9377

## Endpoints

### Health
`GET /health` → `{"ok":true,"enabled":true,"running":true,"engine":"camoufox","browserConnected":true,"browserRunning":true}`

### Tabs

**Create tab:** `POST /tabs`
```json
{"userId": "agent", "sessionKey": "session-1", "url": "https://example.com"}
```
→ `{"tabId": "uuid", "url": "..."}`

**List tabs:** `GET /tabs?userId=agent`

**Navigate:** `POST /tabs/:tabId/navigate`
```json
{"userId": "agent", "url": "https://example.com"}
```

**Get snapshot (accessibility tree):** `GET /tabs/:tabId/snapshot?userId=agent`
→ `{"url": "...", "snapshot": "accessibility tree text with [e1], [e2] refs", "refsCount": N, "truncated": false}`

**Click element:** `POST /tabs/:tabId/click`
```json
{"userId": "agent", "ref": "e5"}
```

**Type into element:** `POST /tabs/:tabId/type`
```json
{"userId": "agent", "ref": "e4", "text": "search query"}
```

**Press key:** `POST /tabs/:tabId/press`
```json
{"userId": "agent", "key": "Enter"}
```

**Scroll:** `POST /tabs/:tabId/scroll`
```json
{"userId": "agent", "direction": "down", "amount": 300}
```

**Evaluate JS:** `POST /tabs/:tabId/evaluate`
```json
{"userId": "agent", "expression": "document.title"}
```
→ `{"result": "..."}`

**Screenshot:** `GET /tabs/:tabId/screenshot?userId=agent` → base64 PNG

**Back/Forward/Refresh:**
- `POST /tabs/:tabId/back` `{"userId": "agent"}`
- `POST /tabs/:tabId/forward` `{"userId": "agent"}`
- `POST /tabs/:tabId/refresh` `{"userId": "agent"}`

**Wait:** `POST /tabs/:tabId/wait`
```json
{"userId": "agent", "ms": 1000}
```

**Get page links:** `GET /tabs/:tabId/links?userId=agent`
**Get downloads:** `GET /tabs/:tabId/downloads?userId=agent`
**Get images:** `GET /tabs/:tabId/images?userId=agent`
**Get stats:** `GET /tabs/:tabId/stats?userId=agent`
