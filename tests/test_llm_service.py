import asyncio
import os
import sys
import logging
from unittest.mock import MagicMock, AsyncMock, patch

import litellm

# Configure logging
logging.basicConfig(level=logging.INFO)

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db import SearchSpace, LLMConfig, ProviderType
from app.services.llm_service import get_fast_llm, validate_llm_config, get_text_embedding

def test_get_fast_llm():
    print("Testing get_fast_llm logic...")

    # Mock Session
    mock_session = AsyncMock()

    # Mock Search Space Result
    mock_search_space = SearchSpace(id=1, fast_llm_id=100)

    # Mock LLM Config Result
    mock_llm_config = LLMConfig(
        id=100,
        search_space_id=1,
        provider=ProviderType.OPENAI,
        model_name="gpt-3.5-turbo",
        api_key="sk-test",
        litellm_params={}
    )

    # Setup execute return values
    mock_result_ss = MagicMock()
    mock_result_ss.scalars.return_value.first.return_value = mock_search_space

    mock_result_lc = MagicMock()
    mock_result_lc.scalars.return_value.first.return_value = mock_llm_config

    # side_effect needs to be an iterable that yields return values
    mock_session.execute.side_effect = [mock_result_ss, mock_result_lc]

    llm = asyncio.run(get_fast_llm(mock_session, 1))

    assert llm is not None
    # ChatLiteLLM stores model string in .model
    assert llm.model == "openai/gpt-3.5-turbo"
    print("get_fast_llm test passed!")

def test_validate_llm_config():
    print("Testing validate_llm_config logic...")

    # Mock ChatLiteLLM to avoid network calls
    with patch("app.services.llm_service.ChatLiteLLM") as MockChatLiteLLM:
        mock_instance = MockChatLiteLLM.return_value

        # 1. Test Success
        mock_response = MagicMock()
        mock_response.content = "Test response"
        async def async_mock(*args, **kwargs):
            return mock_response
        mock_instance.ainvoke = async_mock

        is_valid, error = asyncio.run(validate_llm_config(
            provider="OPENAI",
            model_name="gpt-4",
            api_key="sk-test-key"
        ))
        assert is_valid is True
        assert error == ""

        # 2. Test AuthenticationError
        # Mock initialization to raise exception or ainvoke to raise it
        # validate_llm_config creates a new instance, so we need to mock ainvoke raising it
        async def async_mock_auth_error(*args, **kwargs):
             raise litellm.AuthenticationError("Auth failed", llm_provider="openai", model="gpt-4")
        mock_instance.ainvoke = async_mock_auth_error

        is_valid, error = asyncio.run(validate_llm_config(
            provider="OPENAI",
            model_name="gpt-4",
            api_key="sk-test-key"
        ))
        assert is_valid is False
        assert "Authentication failed" in error



        # 3. Test provider passed as Enum-like object
        mock_instance.ainvoke = async_mock

        class ProviderEnumLike:
            value = "OPENAI"

        is_valid, error = asyncio.run(validate_llm_config(
            provider=ProviderEnumLike(),
            model_name="gpt-4",
            api_key="sk-test-key"
        ))
        assert is_valid is True
        assert error == ""

        print("validate_llm_config test passed!")

def test_get_text_embedding():
    print("Testing get_text_embedding logic...")

    with patch("app.services.llm_service.litellm_embedding") as mock_embedding:
        # Mock response for string input
        mock_embedding.return_value = {
            "data": [
                {"embedding": [0.1, 0.2, 0.3]}
            ]
        }

        embedding = asyncio.run(get_text_embedding(
            text="hello",
            model_name="text-embedding-3-small",
            api_key="sk-test"
        ))

        assert isinstance(embedding, list)
        assert len(embedding) == 3
        assert embedding[0] == 0.1

        # Mock response for list input
        mock_embedding.return_value = {
            "data": [
                {"embedding": [0.1, 0.2, 0.3]},
                {"embedding": [0.4, 0.5, 0.6]}
            ]
        }

        embeddings = asyncio.run(get_text_embedding(
            text=["hello", "world"],
            model_name="text-embedding-3-small",
            api_key="sk-test"
        ))

        assert isinstance(embeddings, list)
        assert len(embeddings) == 2
        assert embeddings[0] == [0.1, 0.2, 0.3]

        print("get_text_embedding test passed!")

if __name__ == "__main__":
    test_get_fast_llm()
    test_validate_llm_config()
    test_get_text_embedding()
