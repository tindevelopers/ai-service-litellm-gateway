"""
Unit tests for main application
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

# Mock the database and redis initialization
with patch('src.core.database.init_db', new_callable=AsyncMock), \
     patch('src.core.redis.init_redis', new_callable=AsyncMock):
    from src.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "AI Gateway" in data["message"]
    assert data["version"] == "1.0.0"


def test_health_endpoint():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["version"] == "1.0.0"


def test_ready_endpoint():
    """Test the readiness check endpoint"""
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert "checks" in data
    assert "database" in data["checks"]
    assert "redis" in data["checks"]


def test_models_endpoint():
    """Test the models list endpoint"""
    response = client.get("/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert data["object"] == "list"
    assert "data" in data
    assert len(data["data"]) > 0
    # Check that we have some expected models
    model_ids = [model["id"] for model in data["data"]]
    assert "gpt-4" in model_ids
    assert "gpt-3.5-turbo" in model_ids


def test_chat_completion_endpoint():
    """Test the chat completion endpoint"""
    request_data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": "Hello, how are you?"}
        ]
    }
    
    response = client.post("/v1/chat/completions", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert data["object"] == "chat.completion"
    assert "id" in data
    assert data["model"] == "gpt-3.5-turbo"
    assert len(data["choices"]) > 0
    assert data["choices"][0]["message"]["role"] == "assistant"
    assert "usage" in data


def test_support_classification_endpoint():
    """Test the support ticket classification endpoint"""
    request_data = {
        "message": "I'm having trouble with my billing. The charges seem incorrect."
    }
    
    response = client.post("/v1/support/classify", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "category" in data
    assert "priority" in data
    assert "confidence" in data
    assert 0 <= data["confidence"] <= 1
    assert "sentiment" in data


def test_support_response_endpoint():
    """Test the support response generation endpoint"""
    request_data = {
        "customer_message": "I need help with setting up my account",
        "category": "general",
        "priority": "medium"
    }
    
    response = client.post("/v1/support/respond", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "primary_response" in data
    assert "alternative_responses" in data
    assert len(data["alternative_responses"]) > 0
    assert "suggested_actions" in data

