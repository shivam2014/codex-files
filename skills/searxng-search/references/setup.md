# SearXNG Setup

## Docker Compose (recommended)

Create `docker-compose.yml`:

```yaml
services:
  searxng:
    image: searxng/searxng:latest
    ports:
      - "127.0.0.1:8888:8080"
    environment:
      - SEARXNG_SECRET_KEY=<generate with: python3 -c "import secrets; print(secrets.token_hex(32))">
    volumes:
      - ./searxng-data:/etc/searxng:rw
    restart: unless-stopped
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
      - SETGID
      - SETUID
```

## Enable JSON format

In SearXNG `settings.yml` (`searxng-data/settings.yml`), ensure:

```yaml
search:
  formats:
    - html
    - json
```

## Test

```bash
curl -s 'http://localhost:8888/search?q=test&format=json' | head -c 200
```
