from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_BASE_URL: str = ""
    DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR / 'data' / 'climbing_analysis.db'}"
    UPLOAD_DIR: str = str(BASE_DIR / "uploads")
    MODEL_DIR: str = str(BASE_DIR / "data" / "models")
    POSE_BACKEND: str = "mediapipe"
    MAX_VIDEO_SIZE_MB: int = 500
    FRAME_SAMPLE_RATE: int = 5
    CLAUDE_MODEL: str = "claude-sonnet-4-20250514"
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    model_config = {"env_file": str(BASE_DIR / ".env"), "env_file_encoding": "utf-8"}


settings = Settings()
