# PotionCheck Deployment

This repo is ready for a two-service deployment:

- `frontend`: Vite static site
- `backend`: FastAPI Docker service with Redis and a persistent SQLite disk

## Recommended: Render

1. Push this repository to GitHub.
2. In Render, create a new Blueprint from the repository. Render will detect `render.yaml`.
3. Fill the secret environment variables Render asks for:
   - `GROQ_API_KEY`: your Groq API key
   - `VITE_API_BASE_URL`: the public backend URL, for example `https://potioncheck-api.onrender.com`
   - `ALLOWED_ORIGINS`: the public frontend URL, for example `https://potioncheck-frontend.onrender.com`
   - `PRODUCTION_DOMAIN`: same as the public frontend URL
4. Deploy.

After the first deploy, if Render gives different service URLs, update:

- backend `ALLOWED_ORIGINS`
- backend `PRODUCTION_DOMAIN`
- frontend `VITE_API_BASE_URL`

## Manual Deploy Values

Backend:

```text
AI_PROVIDER=groq
GROQ_API_KEY=<your key>
GROQ_MODEL=llama-3.1-8b-instant
SECRET_KEY=<generate a long random string>
DATABASE_URL=sqlite+aiosqlite:////app/data/potioncheck.db
REDIS_URL=<your redis url>
ALLOWED_ORIGINS=<your frontend https url>
PRODUCTION_DOMAIN=<your frontend https url>
```

Frontend:

```text
VITE_APP_NAME=PotionCheck
VITE_API_BASE_URL=<your backend https url>
```

## Local Checks

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

cd frontend
npm ci
npm run build
```
