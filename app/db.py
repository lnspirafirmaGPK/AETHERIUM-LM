import enum
from typing import Any, Dict, Optional

from sqlalchemy import Integer, String, JSON, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.config import config

# Create Async Engine
engine = create_async_engine(config.DATABASE_URL, echo=False)

# Create Async Session Factory
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

class ProviderType(enum.Enum):
    OPENAI = "OPENAI"
    ANTHROPIC = "ANTHROPIC"
    GROQ = "GROQ"
    COHERE = "COHERE"
    GOOGLE = "GOOGLE"
    OLLAMA = "OLLAMA"
    MISTRAL = "MISTRAL"
    AZURE_OPENAI = "AZURE_OPENAI"
    OPENROUTER = "OPENROUTER"
    COMETAPI = "COMETAPI"
    XAI = "XAI"
    BEDROCK = "BEDROCK"
    AWS_BEDROCK = "AWS_BEDROCK"
    VERTEX_AI = "VERTEX_AI"
    TOGETHER_AI = "TOGETHER_AI"
    FIREWORKS_AI = "FIREWORKS_AI"
    REPLICATE = "REPLICATE"
    PERPLEXITY = "PERPLEXITY"
    ANYSCALE = "ANYSCALE"
    DEEPINFRA = "DEEPINFRA"
    CEREBRAS = "CEREBRAS"
    SAMBANOVA = "SAMBANOVA"
    AI21 = "AI21"
    CLOUDFLARE = "CLOUDFLARE"
    DATABRICKS = "DATABRICKS"
    DEEPSEEK = "DEEPSEEK"
    ALIBABA_QWEN = "ALIBABA_QWEN"
    MOONSHOT = "MOONSHOT"
    ZHIPU = "ZHIPU"

class SearchSpace(Base):
    __tablename__ = "search_spaces"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    long_context_llm_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    fast_llm_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    strategic_llm_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

class LLMConfig(Base):
    __tablename__ = "llm_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    search_space_id: Mapped[int] = mapped_column(Integer, ForeignKey("search_spaces.id"), index=True)
    provider: Mapped[ProviderType] = mapped_column(SAEnum(ProviderType))
    model_name: Mapped[str] = mapped_column(String)
    api_key: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    api_base: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    custom_provider: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    litellm_params: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
