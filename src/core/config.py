"""
Application configuration using Pydantic Settings
"""

import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Basic app settings
    APP_NAME: str = "AI Gateway"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=False, env="DEBUG")
    PORT: int = Field(default=8080, env="PORT")
    HOST: str = Field(default="0.0.0.0", env="HOST")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Security
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALLOWED_HOSTS: List[str] = Field(default=["*"], env="ALLOWED_HOSTS")
    
    # Database
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    DATABASE_POOL_SIZE: int = Field(default=10, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")
    
    # Redis
    REDIS_URL: str = Field(..., env="REDIS_URL")
    REDIS_MAX_CONNECTIONS: int = Field(default=100, env="REDIS_MAX_CONNECTIONS")
    
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=3600, env="RATE_LIMIT_WINDOW")  # 1 hour
    
    # LiteLLM settings
    LITELLM_MASTER_KEY: Optional[str] = Field(default=None, env="LITELLM_MASTER_KEY")
    LITELLM_DATABASE_URL: Optional[str] = Field(default=None, env="LITELLM_DATABASE_URL")
    
    # LLM Provider API Keys
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    GOOGLE_API_KEY: Optional[str] = Field(default=None, env="GOOGLE_API_KEY")
    AZURE_API_KEY: Optional[str] = Field(default=None, env="AZURE_API_KEY")
    AZURE_API_BASE: Optional[str] = Field(default=None, env="AZURE_API_BASE")
    AZURE_API_VERSION: Optional[str] = Field(default=None, env="AZURE_API_VERSION")
    COHERE_API_KEY: Optional[str] = Field(default=None, env="COHERE_API_KEY")
    HUGGINGFACE_API_KEY: Optional[str] = Field(default=None, env="HUGGINGFACE_API_KEY")
    
    # Caching settings
    CACHE_TTL: int = Field(default=3600, env="CACHE_TTL")  # 1 hour
    CACHE_ENABLED: bool = Field(default=True, env="CACHE_ENABLED")
    SEMANTIC_CACHE_THRESHOLD: float = Field(default=0.95, env="SEMANTIC_CACHE_THRESHOLD")
    
    # Monitoring
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
    METRICS_PORT: int = Field(default=9090, env="METRICS_PORT")
    
    # Cost optimization
    DEFAULT_MODEL: str = Field(default="gpt-3.5-turbo", env="DEFAULT_MODEL")
    COST_TRACKING_ENABLED: bool = Field(default=True, env="COST_TRACKING_ENABLED")
    BUDGET_LIMIT_USD: Optional[float] = Field(default=None, env="BUDGET_LIMIT_USD")
    
    # Specialized services settings
    BLOG_DEFAULT_MODEL: str = Field(default="gpt-4", env="BLOG_DEFAULT_MODEL")
    SUPPORT_DEFAULT_MODEL: str = Field(default="gpt-3.5-turbo", env="SUPPORT_DEFAULT_MODEL")
    CLASSIFICATION_MODEL: str = Field(default="gpt-3.5-turbo", env="CLASSIFICATION_MODEL")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields for flexibility


# Create global settings instance
settings = Settings()

