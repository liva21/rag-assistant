from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "Omi RAG Assistant"
    openai_api_key: str = ""
    huggingfacehub_api_token: str = ""
    ALLOWED_EXTENSIONS: list = [".pdf", ".docx", ".txt", ".md"]
    UPLOAD_DIR: str = "data/raw"
    MAX_FILE_SIZE_MB: int = 10
    max_file_size_bytes: int = 10 * 1024 * 1024

    class Config:
        env_file = ".env"
        extra = "ignore"

@lru_cache()
def get_settings():
    return Settings()
