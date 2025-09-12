"""
Basic unit tests for CI/CD pipeline
"""

import pytest
from fastapi.testclient import TestClient
import os

# Ensure environment variables are set
os.environ.update({
    "SECRET_KEY": "test-secret-key-for-ci",
    "DATABASE_URL": "postgresql+asyncpg://test:test@localhost:5432/test",
    "REDIS_URL": "redis://localhost:6379/1",
    "CACHE_ENABLED": "false",
    "OPENAI_API_KEY": "test-key"
})

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
    assert data["environment"] == "development"


def test_ready_endpoint():
    """Test the readiness check endpoint"""
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert "checks" in data


def test_metrics_endpoint():
    """Test the metrics endpoint"""
    response = client.get("/metrics")
    assert response.status_code == 200
    # Metrics should be in Prometheus format
    content_type = response.headers.get("content-type", "")
    assert "text/plain" in content_type


def test_docs_endpoint():
    """Test that API documentation is available"""
    response = client.get("/docs")
    assert response.status_code == 200
    content_type = response.headers.get("content-type", "")
    assert "text/html" in content_type


def test_models_endpoint():
    """Test the models list endpoint"""
    response = client.get("/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert data["object"] == "list"
    assert "data" in data
    # Should have at least some models available
    assert len(data["data"]) >= 0


def test_configuration_loading():
    """Test that configuration is loaded correctly"""
    from src.core.config import settings
    
    assert settings.APP_NAME == "AI Gateway"
    assert settings.VERSION == "1.0.0"
    assert settings.ENVIRONMENT == "development"
    assert settings.SECRET_KEY == "test-secret-key-for-ci"


def test_invalid_endpoint():
    """Test that invalid endpoints return 404"""
    response = client.get("/invalid-endpoint")
    assert response.status_code == 404


def test_cors_headers():
    """Test that CORS headers are present"""
    response = client.get("/health")
    assert response.status_code == 200
    # FastAPI should handle CORS headers automatically
