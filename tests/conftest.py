"""
Test configuration and fixtures
"""

import pytest
import os
from unittest.mock import patch, AsyncMock, MagicMock

# Set test environment variables before importing the app
os.environ["SECRET_KEY"] = "test-secret-key-for-ci"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://test:test@localhost:5432/test"
os.environ["REDIS_URL"] = "redis://localhost:6379/1"
os.environ["CACHE_ENABLED"] = "false"
os.environ["OPENAI_API_KEY"] = "test-key"
os.environ["ANTHROPIC_API_KEY"] = "test-key"


@pytest.fixture(autouse=True)
def mock_external_services():
    """Mock external services for testing"""
    
    # Mock LiteLLM service methods
    with patch('src.services.litellm_service.litellm_service.chat_completion') as mock_chat, \
         patch('src.services.litellm_service.litellm_service.get_available_models') as mock_models:
        
        # Mock chat completion response
        mock_chat.return_value = {
            "id": "chatcmpl-test123",
            "object": "chat.completion",
            "created": 1234567890,
            "model": "gpt-3.5-turbo",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "This is a test response from the AI Gateway."
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30
            }
        }
        
        # Mock available models response
        mock_models.return_value = [
            {"id": "gpt-4", "provider": "openai"},
            {"id": "gpt-3.5-turbo", "provider": "openai"},
            {"id": "claude-3-haiku", "provider": "anthropic"}
        ]
        
        yield {
            "chat_completion": mock_chat,
            "get_models": mock_models
        }


@pytest.fixture(autouse=True)
def mock_database_redis():
    """Mock database and Redis initialization"""
    with patch('src.core.database.init_db', new_callable=AsyncMock), \
         patch('src.core.redis.init_redis', new_callable=AsyncMock), \
         patch('src.core.redis.get_redis', new_callable=AsyncMock):
        yield
