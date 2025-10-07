from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application configuration from environment variables."""

    ARK_API_KEY: str = Field(..., description="Ark API key (required)")
    DOUBAO_API_ENDPOINT: str = Field(
        default="https://ark.cn-beijing.volces.com/api/v3",
        description="Doubao API endpoint",
    )
    DOUBAO_MODEL: str = Field(
        default="doubao-seed-1-6-250615",
        description="Doubao model name"
    )
    MAX_SESSIONS: int = Field(default=50, description="Maximum concurrent sessions")
    CONVERSATIONS_DIR: str = Field(
        default="./conversations", description="Directory for conversation history files"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
