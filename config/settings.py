from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    groq_api_key: str
    groq_model: str = "llama-3.3-70b-versatile"
    groq_classifier_model: str = "llama-3.1-8b-instant"
    embedding_model: str = "intfloat/multilingual-e5-base"

    # Qdrant Cloud (primary) — leave url/api_key empty to fall back to local file mode
    qdrant_url: str = ""
    qdrant_api_key: str = ""
    qdrant_collection: str = "healthcare_funds"
    # Local Qdrant fallback path (used when qdrant_url is empty)
    qdrant_local_path: str = "./vectorstore/qdrant_local"

    top_k_retrieval: int = 6
    scheduler_hour_ist: int = 10
    fastapi_host: str = "0.0.0.0"
    fastapi_port: int = 8002
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
