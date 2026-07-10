# Portfolio Backend — Restructured

## What changed from the original `main.py` + `database.py`

1. **Fails loud, not silent.**
   - Missing `EDITOR_ACCESS_TOKEN` → app won't boot (was: falls back to open access).
   - Missing/broken Firebase in production → API returns `503` (was: silently
     writes to local disk, which is wiped on every Render redeploy).
   - Missing `ALLOWED_ORIGINS` → app won't boot (was: falls back to `"*"`).
2. **`ENVIRONMENT=local` is the only thing that enables the local-file
   fallback.** Set it to anything else (or leave default `production`) on Render.
3. **Constant-time token comparison** (`secrets.compare_digest`) instead of `==`.
4. **Seed data lives in `app/data/seed.json`**, not hardcoded in a Python module.
5. **Split into layers**: `core` (config/security), `db` (Firebase +
   repository), `models` (schemas), `api/routes` (HTTP layer).
6. **No Google OAuth.** Deliberately kept the bearer-token model — single
   admin, no need for the added complexity of OAuth redirect/token-exchange
   flows. See inline comment in `app/core/security.py` if you want the
   reasoning on record.

## Setup

```bash
cp .env.example .env
# fill in EDITOR_ACCESS_TOKEN (generate with the command in .env.example)
# and ALLOWED_ORIGINS at minimum. Leave ENVIRONMENT=local and
# FIREBASE_CREDENTIALS_JSON empty to use the local JSON fallback while developing.

pip install -r requirements.txt
python -m app.main
```

## Deploying to Render

Set these as **environment variables in the Render dashboard** (not in a file
committed to the repo):

| Variable | Notes |
|---|---|
| `ENVIRONMENT` | `production` |
| `FIREBASE_CREDENTIALS_JSON` | Full service account JSON, pasted as one line |
| `EDITOR_ACCESS_TOKEN` | `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `READONLY_ACCESS_TOKEN` | optional |
| `ALLOWED_ORIGINS` | your Cloudflare Pages `.pages.dev` URL(s) + custom domain, comma-separated |
| `PORT` | Render sets this automatically, `main.py` reads it |

Start command: `python -m app.main` (or `uvicorn app.main:app --host 0.0.0.0 --port $PORT`).

## Before you drop this into your repo

- Copy your built frontend into `static/` (same convention as before —
  `static/assets` gets mounted, `static/index.html` is the SPA fallback).
- The route paths are unchanged (`/api/resume`, `/api/blogs`, `/api/status`,
  `/api/auth/verify`) so your frontend shouldn't need updates.
- Delete `app/data/local/` before deploying if it exists — it's dev-only
  scratch data and shouldn't ship.
