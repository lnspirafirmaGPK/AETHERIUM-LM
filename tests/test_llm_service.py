import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import litellm

from app.db import LLMConfig, ProviderType, SearchSpace
from app.services.llm_service import get_fast_llm, get_text_embedding, validate_llm_config


def test_get_fast_llm():
    mock_session = AsyncMock()

    mock_search_space = SearchSpace(id=1, fast_llm_id=100)
    mock_llm_config = LLMConfig(
        id=100,
        search_space_id=1,
        provider=ProviderType.OPENAI,
        model_name="gpt-3.5-turbo",
        api_key="sk-test",
        litellm_params={},
    )

    mock_result_ss = MagicMock()
    mock_result_ss.scalars.return_value.first.return_value = mock_search_space

    mock_result_lc = MagicMock()
    mock_result_lc.scalars.return_value.first.return_value = mock_llm_config

    mock_session.execute.side_effect = [mock_result_ss, mock_result_lc]

    with patch("app.services.llm_service.ChatLiteLLM") as mock_chat_litellm:
        llm = asyncio.run(get_fast_llm(mock_session, 1))

    assert llm is mock_chat_litellm.return_value
    assert mock_chat_litellm.call_args.kwargs["model"] == "openai/gpt-3.5-turbo"


def test_validate_llm_config():
    with patch("app.services.llm_service.ChatLiteLLM") as mock_chat_litellm:
        mock_instance = mock_chat_litellm.return_value

        mock_response = MagicMock()
        mock_response.content = "Test response"

        async def async_success(*args, **kwargs):
            return mock_response

        mock_instance.ainvoke = async_success

        is_valid, error = asyncio.run(
            validate_llm_config(
                provider="OPENAI",
                model_name="gpt-4",
                api_key="sk-test-key",
            )
        )
        assert is_valid is True
        assert error == ""

        async def async_auth_error(*args, **kwargs):
            raise litellm.AuthenticationError(
                "Auth failed", llm_provider="openai", model="gpt-4"
            )

        mock_instance.ainvoke = async_auth_error

        is_valid, error = asyncio.run(
            validate_llm_config(
                provider="OPENAI",
                model_name="gpt-4",
                api_key="sk-test-key",
            )
        )
        assert is_valid is False
        assert "Authentication failed" in error

        mock_instance.ainvoke = async_success

        class ProviderEnumLike:
            value = "OPENAI"

        is_valid, error = asyncio.run(
            validate_llm_config(
                provider=ProviderEnumLike(),
                model_name="gpt-4",
                api_key="sk-test-key",
            )
        )
        assert is_valid is True
        assert error == ""


def test_get_text_embedding_provider_aliases():
    with patch("app.services.llm_service.litellm_embedding") as mock_embedding:
        mock_embedding.return_value = {"data": [{"embedding": [0.1, 0.2, 0.3]}]}

        embedding = asyncio.run(
            get_text_embedding(
                text="hello",
                model_name="text-embedding-004",
                api_key="sk-test",
                provider=ProviderType.GOOGLE,
            )
        )

        assert embedding == [0.1, 0.2, 0.3]
        assert mock_embedding.call_args.kwargs["model"] == "gemini/text-embedding-004"

        embedding = asyncio.run(
            get_text_embedding(
                text="hello",
                model_name="openai/text-embedding-3-small",
                api_key="sk-test",
                provider=ProviderType.OPENAI,
            )
        )

        assert embedding == [0.1, 0.2, 0.3]
        assert mock_embedding.call_args.kwargs["model"] == "openai/text-embedding-3-small"


def test_get_text_embedding():
    with patch("app.services.llm_service.litellm_embedding") as mock_embedding:
        mock_embedding.return_value = {"data": [{"embedding": [0.1, 0.2, 0.3]}]}

        embedding = asyncio.run(
            get_text_embedding(
                text="hello",
                model_name="text-embedding-3-small",
                api_key="sk-test",
            )
        )

        assert isinstance(embedding, list)
        assert len(embedding) == 3
        assert embedding[0] == 0.1

        mock_embedding.return_value = {
            "data": [
                {"embedding": [0.1, 0.2, 0.3]},
                {"embedding": [0.4, 0.5, 0.6]},
            ]
        }

        embeddings = asyncio.run(
            get_text_embedding(
                text=["hello", "world"],
                model_name="text-embedding-3-small",
                api_key="sk-test",
            )
        )

        assert isinstance(embeddings, list)
        assert len(embeddings) == 2
        assert embeddings[0] == [0.1, 0.2, 0.3]
