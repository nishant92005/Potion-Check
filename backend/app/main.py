from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import analysis, auth, health, history, profile, scanner
from app.core.config import settings
from app.core.database import init_db

app = FastAPI(title="PotionCheck API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=r"^http://(localhost|127\.0\.0\.1|0\.0\.0\.0|10\.\d+\.\d+\.\d+|172\.(1[6-9]|2\d|3[0-1])\.\d+\.\d+|192\.168\.\d+\.\d+):517[3-9]$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(scanner.router)
app.include_router(analysis.router)
app.include_router(history.router)
app.include_router(health.router)


@app.on_event("startup")
async def startup() -> None:
    await init_db()


@app.get("/")
async def root():
    return {"name": "PotionCheck API", "status": "alive"}
