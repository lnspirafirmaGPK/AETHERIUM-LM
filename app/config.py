import os
from typing import Dict, List, Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database Configuration
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"

    # Global LLM Configurations (Negative IDs)
    GLOBAL_LLM_CONFIGS: List[Dict] = [
        {
            "id": -1,
            "provider": "OPENAI",
            "model_name": "gpt-4o",
            "api_key": "sk-dummy-key",
            "litellm_params": {"temperature": 0.5}
        }
    ]

    # API Keys (optional, can be loaded from environment)
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None

    class Config:
        env_file = ".env"
        extra = "ignore"

config = Settings()
