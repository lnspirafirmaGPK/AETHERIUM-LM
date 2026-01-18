import asyncio
import os
import sys
import logging
from unittest.mock import MagicMock, AsyncMock, patch

# Configure logging
logging.basicConfig(level=logging.INFO)

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db import SearchSpace, LLMConfig, ProviderType
from app.services.llm_service import get_fast_llm, validate_llm_config

async def test_get_fast_llm():
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

    llm = await get_fast_llm(mock_session, 1)

    assert llm is not None
    # ChatLiteLLM stores model string in .model
    assert llm.model == "openai/gpt-3.5-turbo"
    print("get_fast_llm test passed!")

async def test_validate_llm_config():
    print("Testing validate_llm_config logic...")

    # Mock ChatLiteLLM to avoid network calls
    with patch("app.services.llm_service.ChatLiteLLM") as MockChatLiteLLM:
        mock_instance = MockChatLiteLLM.return_value

        # Setup the mock to return a valid response
        mock_response = MagicMock()
        mock_response.content = "Test response"

        # Mock ainvoke to return a coroutine that returns mock_response
        async def async_mock(*args, **kwargs):
            return mock_response
        mock_instance.ainvoke = async_mock

        is_valid, error = await validate_llm_config(
            provider="OPENAI",
            model_name="gpt-4",
            api_key="sk-test-key"
        )

        assert is_valid is True
        assert error == ""
        print("validate_llm_config test passed!")

if __name__ == "__main__":
    async def main():
        await test_get_fast_llm()
        await test_validate_llm_config()

    asyncio.run(main())
