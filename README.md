# Trade Opportunities API

A FastAPI service that answers one question: *"What are the current trade opportunities for [sector] in India?"*

Give it a sector name. It searches for live market data, runs it through Google Gemini, and returns a structured markdown report you can save as a `.md` file. No database. No setup headaches.

**Live API:** `https://your-render-url.onrender.com`
> First request may take ~30 seconds on the free tier (Render cold start). Subsequent requests are fast.

---

## Quick Start — Zero to First Report in 3 Commands

```bash
git clone <your-repo-url> && cd trade-opportunities-api
cp .env.example .env          # then open .env and add your two keys
docker compose up --build
```

The API is now live at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

---

## Setup Instructions (Without Docker)

**Prerequisites:** Python 3.11+

```bash
# 1. Clone and enter the project
git clone <your-repo-url>
cd trade-opportunities-api

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Open .env and fill in GEMINI_API_KEY and JWT_SECRET (instructions below)

# 5. Start the server
uvicorn app.main:app --reload
```

---

## Getting Your Keys

### GEMINI_API_KEY
1. Go to [aistudio.google.com](https://aistudio.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the key — it starts with `AIza...`
4. Paste it into your `.env`

### JWT_SECRET
Any random string that's at least 32 characters. Generate one:
```bash
openssl rand -hex 32
# or on Windows PowerShell:
[System.Web.HttpUtility]::UrlEncode([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(32))
```

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | **Yes** | — | Google AI Studio key |
| `JWT_SECRET` | **Yes** | — | Random 32+ char string for signing tokens |
| `ALLOWED_ORIGINS` | No | `http://localhost:3000` | CORS allowed origins (use `*` for testing) |
| `JWT_EXPIRY_MINUTES` | No | `60` | How long a token stays valid |
| `RATE_LIMIT_ANALYZE` | No | `5/minute` | Rate cap on `/analyze` |
| `RATE_LIMIT_AUTH` | No | `10/minute` | Rate cap on `/auth/token` |

---

## API Documentation

### Authentication — Guest JWT Flow

The API uses stateless JWT auth. No account creation required — just pick any `client_id` string.

**Step 1: Get a token**
```bash
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"client_id": "my-session"}'
```
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

Token is valid for **60 minutes**. After that, request a new one.

---

### Core Endpoint — `GET /analyze/{sector}`

Accepts a sector name, fetches live market data, and returns a structured markdown report.

```bash
# Replace TOKEN with the access_token from the step above
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/analyze/pharmaceuticals
```

**Response:** `text/plain` — the full markdown report, which you can save directly as a `.md` file:
```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/analyze/pharmaceuticals > report.md
```

**Sample report output:**
```markdown
# Trade Opportunities Report: Pharmaceuticals

**Generated:** 2025-04-06 10:23 UTC
**Session:** my-session
**Sector:** pharmaceuticals

---

## Executive Summary
India's pharmaceutical sector exported $27.9 billion in FY2024...

## Current Market Trends
- Generic drug exports to the US grew 8.2% YoY in Q4 FY2024
- Africa emerging as high-growth destination with 23% increase in demand
...

## Key Trade Opportunities
## Target Export Markets
## Challenges & Risk Factors
## Recommended Next Steps
## Data Sources
```

**Valid sector names:** 2–50 characters, letters and spaces only. Examples:
`pharmaceuticals`, `technology`, `agriculture`, `textiles`, `automotive`, `renewable energy`

---

### All Endpoints

| Method | Endpoint | Auth | Rate Limit | Description |
|--------|----------|------|-----------|-------------|
| `POST` | `/auth/token` | None | 10/min per IP | Get a JWT token |
| `GET` | `/analyze/{sector}` | Bearer JWT | 5/min per client_id | Generate trade report |
| `GET` | `/health` | None | 30/min | Liveness check |
| `GET` | `/docs` | None | — | Interactive Swagger UI |

---

### Error Reference

| Scenario | HTTP | Response |
|----------|------|----------|
| No Authorization header | `401` | `{"detail": "Not authenticated"}` |
| Expired or invalid JWT | `401` | `{"detail": "invalid or expired token"}` |
| Sector has numbers/special chars | `400` | `{"detail": "sector must be 2-50 letters only..."}` |
| Rate limit exceeded | `429` | `{"detail": "Too Many Requests"}` |
| Gemini rate limited | `503` | `{"detail": "AI service temporarily busy..."}` |
| Gemini API key invalid | `500` | `{"detail": "AI service misconfigured..."}` |
| DDG search fails | `200` | Report with "No recent market data found" note |

---

## System Architecture

```
Client
  │
  ├─► POST /auth/token → JWT (HS256, 1hr expiry)
  │
  └─► GET /analyze/{sector}
        │
        ├── [SecurityHeaders + CORS Middleware]
        ├── [Rate Limiter — 5/min per client_id]
        ├── verify_token()       ← JWT validation
        ├── clean_sector()       ← regex input validation
        │
        ├── search.fetch_market_data()   ← DuckDuckGo (2 queries, threaded)
        ├── gemini.analyze()             ← Gemini 1.5 Flash (threaded)
        ├── report.build_report()        ← assembles final markdown
        └── session.record()             ← logs to in-memory store
              │
              ◄── text/plain markdown response
```

**Clean layer separation:**
- `app/routers/` — HTTP layer only. Calls services, returns responses. No business logic.
- `app/services/` — All business logic. No FastAPI imports.
- `app/auth/` — JWT encode/decode only.
- `app/middleware/` — Cross-cutting HTTP concerns (security headers, rate limiting).
- `app/prompts/` — Prompt templates only. Never accepts user input.
- `app/session/` — In-memory tracking with `asyncio.Lock` for thread safety.

---

## Security Features

| Threat | Control | Implementation |
|--------|---------|---------------|
| Unauthorized access | JWT Bearer auth | `python-jose` HS256, `Depends(verify_token)` on `/analyze` |
| LLM cost abuse / DDoS on analysis | Rate limiting | `slowapi` 5/min per `client_id` from JWT payload |
| Token endpoint brute force | Rate limiting | `slowapi` 10/min per IP on `/auth/token` |
| Prompt injection via sector name | Input validation | Regex `^[a-zA-Z\s\-]{2,50}$` — blocks numbers and special chars |
| XSS / Clickjacking | Security headers | `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection: 1` |
| Secret leakage | Config management | `pydantic-settings` reads `.env` only — no `os.environ` scattering |
| CORS abuse | CORS middleware | `allow_origins` from env var, not hardcoded wildcard |

---

## AI Integration (Gemini)

**Model:** `gemini-1.5-flash` (free tier — 15 req/min, no credit card needed)

**System instruction:** Outputs only structured markdown trade analysis. Rejects off-topic prompts.

**User prompt:** Appends the raw DuckDuckGo search results and requires Gemini to produce exactly 7 sections:
1. Executive Summary
2. Current Market Trends
3. Key Trade Opportunities
4. Target Export Markets
5. Challenges & Risk Factors
6. Recommended Next Steps
7. Data Sources

**Settings:** `temperature=0.3` (consistency for structured output), `max_output_tokens=2048`

The Gemini call runs in a thread pool (`asyncio.run_in_executor`) so it never blocks the ASGI event loop.

---

## Data Collection (DuckDuckGo)

For each sector request, two targeted queries are fired:
1. `"{sector} India export trade opportunities 2025"`
2. `"{sector} India market growth trends recent news"`

Each query fetches up to 5 results (title + body + source URL). The combined output is capped at 16,000 characters before being passed to Gemini. A 1-second pause sits between queries to avoid DuckDuckGo's aggressive rate limiting.

If DuckDuckGo returns nothing, the report still generates with a "limited data available" note rather than returning an error.

---

## Session Tracking

Every `/analyze` call is logged to an in-memory dictionary:
```python
{"sector": "pharmaceuticals", "ts": "2025-04-06T10:23:00Z", "status": "done"}
```
Per-client history is capped at 50 entries (older entries are evicted). Data resets on server restart — this is by design for the assignment scope.

---

## Docker Setup

```bash
cp .env.example .env   # fill in GEMINI_API_KEY and JWT_SECRET
docker compose up --build
```
App starts on port 8000. Dockerfile uses `python:3.11-slim` for a small image.

---

## Deployment on Render

1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your GitHub repo
4. Render detects `render.yaml` automatically — click **Deploy**
5. When prompted, paste your `GEMINI_API_KEY` and `JWT_SECRET`
6. Wait ~2 minutes for the build to complete
7. Your live API URL appears in the Render dashboard — add it to the top of this README

**Note:** Free tier instances sleep after 15 minutes of inactivity. The first request after sleep takes ~30 seconds. All subsequent requests are normal speed.

---

## Known Limitations

- **In-memory sessions** — lost on server restart. Trade-off for zero-dependency simplicity.
- **Gemini free tier** — 15 req/min globally. Our 5/min per client limit keeps us safe for a handful of concurrent users, not more.
- **DuckDuckGo scraping** — unofficial wrapper. Can return empty results or fail under heavy scraping load. Handled gracefully.
- **No token revocation** — JWT tokens are stateless. An issued token stays valid until it expires (1 hour).

---

## Tech Stack

| Layer | Choice | Why |
|-------|--------|-----|
| Framework | FastAPI 0.111 | Async-native, auto-docs, Pydantic validation |
| LLM | Gemini 1.5 Flash | Free tier, no credit card, structured output quality |
| Web Search | duckduckgo-search | No API key, zero cost, no evaluator setup friction |
| Auth | JWT via python-jose | Stateless, no database needed |
| Rate Limiting | slowapi | One decorator per route, FastAPI-native |
| Config | pydantic-settings | Type-safe `.env` loading |
