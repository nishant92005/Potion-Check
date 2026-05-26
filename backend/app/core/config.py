from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    secret_key: str = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
    ai_provider: str = "groq"
    groq_api_key: str = ""
    groq_model: str = "llama-3.1-8b-instant"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    ollama_embedding_model: str = "nomic-embed-text"
    ollama_timeout_seconds: int = 180
    chroma_persist_dir: str = "./chroma_db"
    rag_chunk_size: int = 1100
    rag_chunk_overlap: int = 180
    rag_top_k: int = 5
    serpapi_api_key: str = ""
    serpapi_base_url: str = "https://serpapi.com/search.json"
    serpapi_timeout_seconds: int = 20
    google_client_id: str = ""
    google_client_secret: str = ""
    google_people_api_url: str = "https://people.googleapis.com/v1/people/me"
    openfoodfacts_base_url: str = "https://world.openfoodfacts.org"
    openfoodfacts_user_agent: str = "PotionCheck/1.0 (contact: support@potioncheck.app)"
    database_url: str = "sqlite+aiosqlite:///./potioncheck.db"
    redis_url: str = "redis://localhost:6379/0"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    production_domain: str = "https://potioncheck.app"
    allowed_origins: str = ""

    @property
    def cors_origins(self) -> list[str]:
        origins = [
            "http://localhost:5173",
            "https://localhost:5173",
            "http://127.0.0.1:5173",
            "https://127.0.0.1:5173",
            "http://localhost:5174",
            "https://localhost:5174",
            "http://127.0.0.1:5174",
            "https://127.0.0.1:5174",
            self.production_domain,
        ]
        origins.extend(origin.strip() for origin in self.allowed_origins.split(",") if origin.strip())
        return list(dict.fromkeys(origins))

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
