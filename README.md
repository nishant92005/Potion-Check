# PotionCheck

PotionCheck is a full-stack food safety and nutrition assistant. It helps users scan packaged food, extract or fetch ingredient data, analyze the product against a personal health profile, and receive a clear AI-powered verdict with ingredient-by-ingredient explanations.

The project combines a React frontend, a FastAPI backend, OpenFoodFacts product lookup, optional Google search enrichment through SerpAPI, Groq-powered LLM analysis, Ollama fallback, OCR support, Redis caching, SQLite persistence, and a RAG-style chatbot for previously scanned products.

## Key Features

- Barcode scanning and manual barcode entry.
- OpenFoodFacts product lookup by barcode.
- SerpAPI Google fallback when OpenFoodFacts cannot find a barcode product or when the product exists but ingredients are missing.
- AI ingredient analysis using Groq as the primary provider.
- Ollama fallback when Groq is unavailable, rate-limited, or misconfigured.
- Local rule-based safety fallback if external LLM analysis cannot complete.
- OCR upload flow for extracting ingredient text from food label images.
- Pasted ingredient text analysis.
- User profile personalization with allergies, health conditions, and diet type.
- Google login/signup using Google Identity Services plus People API profile lookup.
- Product health and safety scoring.
- Flagged ingredients with reasons, severity, and personalized warnings.
- Nutrition observations, sugar and sodium analysis, gym-friendliness, weight-loss suitability, and frequency advice.
- Scan history with delete options.
- Chatbot for asking questions about saved product analyses.
- Responsive frontend with animated UI, scanner pages, analysis reports, profile management, history, chatbot, about, and developer pages.

## Tech Stack

### Frontend

- React 18
- Vite
- React Router
- Zustand
- Axios
- Framer Motion
- Tailwind CSS
- Three.js and React Three Fiber
- html5-qrcode for camera and image barcode scanning
- Tesseract.js support on the client side where needed

### Backend

- FastAPI
- SQLAlchemy async ORM
- SQLite with `aiosqlite`
- Redis cache
- Pydantic settings
- Groq SDK
- Ollama HTTP API
- OpenFoodFacts API
- SerpAPI Google Search API
- ChromaDB for local vector persistence
- Pillow and pytesseract for OCR

## Project Structure

```text
Potion-Check/
  backend/
    app/
      api/              FastAPI route modules
      core/             settings, database, security
      models/           SQLAlchemy models
      schemas/          Pydantic schemas
      services/         AI, OCR, cache, OpenFoodFacts, SerpAPI, RAG services
    requirements.txt
    Dockerfile
    .env.example
  frontend/
    src/
      components/       shared UI components
      pages/            app pages
      services/         API clients
      stores/           Zustand stores
    package.json
    Dockerfile
  docs/                 project and SRS documentation generators/files
  docker-compose.yml
  render.yaml
```

## Main Backend Flow

1. The user scans, uploads, or enters a barcode in the frontend.
2. The frontend calls `POST /api/scanner/barcode/analyze`.
3. The backend first checks OpenFoodFacts for product data.
4. If OpenFoodFacts fails or returns a product without ingredients, the backend uses SerpAPI Google search to find likely product ingredient text.
5. The backend builds product context from OpenFoodFacts and SerpAPI search snippets.
6. The ingredient text, nutrition data, product context, and user profile are sent to the AI analysis service.
7. Groq is used first when configured.
8. If Groq is rate-limited or unavailable, Ollama is used as backup.
9. If Ollama is also unavailable, the backend returns a local rule-based analysis.
10. The scan and analysis are saved and returned to the frontend.

## API Overview

### Authentication

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/google`
- `GET /api/auth/me`
- `POST /api/auth/refresh`

### Profile

- `GET /api/profile/`
- `PUT /api/profile/`

### Scanner

- `POST /api/scanner/barcode`
- `POST /api/scanner/barcode/analyze`
- `POST /api/scanner/upload`
- `POST /api/scanner/text`

### Analysis

- `POST /api/analysis/`
- `GET /api/analysis/{analysis_id}`
- `GET /api/analysis/product/{barcode}`

### History

- `GET /api/history/`
- `DELETE /api/history/{scan_id}`
- `DELETE /api/history/all`

### Chatbot

- `GET /api/chatbot/products`
- `POST /api/chatbot/ask`

### Health

- `GET /api/health`

## Environment Variables

Create `backend/.env` from `backend/.env.example`.

```env
SECRET_KEY=replace_with_a_long_random_secret
AI_PROVIDER=groq
GROQ_API_KEY=your_groq_key
GROQ_MODEL=llama-3.1-8b-instant

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
OLLAMA_TIMEOUT_SECONDS=180

SERPAPI_API_KEY=your_serpapi_key
SERPAPI_BASE_URL=https://serpapi.com/search.json
SERPAPI_TIMEOUT_SECONDS=20

GOOGLE_CLIENT_ID=your_google_oauth_client_id
GOOGLE_CLIENT_SECRET=your_google_oauth_client_secret
GOOGLE_PEOPLE_API_URL=https://people.googleapis.com/v1/people/me

OPENFOODFACTS_BASE_URL=https://world.openfoodfacts.org
OPENFOODFACTS_USER_AGENT=PotionCheck/1.0 (contact: support@potioncheck.app)

DATABASE_URL=sqlite+aiosqlite:///./potioncheck.db
REDIS_URL=redis://localhost:6379/0

PRODUCTION_DOMAIN=https://your-frontend-domain.example
ALLOWED_ORIGINS=https://your-frontend-domain.example
```

Do not commit `backend/.env`. It contains private API keys.

For the frontend, create `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=your_google_oauth_client_id
```

Google login requests only basic profile and email scopes, then the backend verifies the account by calling People API.

## Local Development

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend runs at:

```text
http://localhost:8000
```

FastAPI docs are available at:

```text
http://localhost:8000/docs
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at:

```text
http://localhost:8080
```

## Docker Development

Run the full app with Redis:

```bash
docker compose up --build
```

Services:

- Frontend: `http://localhost:8080`
- Backend: `http://localhost:8000`
- Redis: `localhost:6379`

## AI Provider Behavior

PotionCheck is designed to keep the user flow working even when an external service is unavailable.

- `AI_PROVIDER=groq`: use Groq first, then Ollama, then local rules.
- `AI_PROVIDER=ollama`: use Ollama first, then local rules.
- `AI_PROVIDER=rules`: skip external LLMs and use local safety rules only.

The barcode ingredient source order is:

1. OpenFoodFacts ingredients.
2. SerpAPI Google search fallback only when OpenFoodFacts fails or lacks ingredients.
3. Return a clear API error if no usable ingredient text can be found.

## Data and Generated Files

The following files are local runtime data and should not be committed:

- `backend/.env`
- `backend/potioncheck.db`
- `backend/chroma_db/`
- `backend/uploads/`
- `backend/images/`
- log files
- virtual environments
- `node_modules/`

## Build Checks

Backend syntax check:

```bash
python -m compileall backend\app
```

Frontend production build:

```bash
cd frontend
npm run build
```

## Notes

- SerpAPI is intentionally used only as a fallback. Normal product lookups continue to rely on OpenFoodFacts first.
- The project stores scan history and analysis results for authenticated users.
- The chatbot uses saved scan context so users can ask follow-up questions about products they already analyzed.
- The local `.env` must be configured before Groq, Ollama, SerpAPI, Redis, or production CORS behavior can work correctly.
