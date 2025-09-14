"""
LiteLLM service for handling multi-provider LLM requests
"""

import logging
import time
import hashlib
import json
from typing import Dict, List, Any, Optional, AsyncGenerator
from contextlib import asynccontextmanager

import litellm
from litellm import completion, acompletion, completion_cost
from fastapi import HTTPException

from src.core.config import settings
from src.core.redis import get_redis
from src.models.usage import Usage
from src.core.database import get_db

logger = logging.getLogger(__name__)

# Configure LiteLLM
litellm.set_verbose = settings.DEBUG
litellm.drop_params = True  # Drop unsupported parameters instead of failing

# Set API keys for providers
if settings.OPENAI_API_KEY:
    litellm.openai_key = settings.OPENAI_API_KEY
if settings.ANTHROPIC_API_KEY:
    litellm.anthropic_key = settings.ANTHROPIC_API_KEY
if settings.GOOGLE_API_KEY:
    litellm.google_key = settings.GOOGLE_API_KEY
if settings.COHERE_API_KEY:
    litellm.cohere_key = settings.COHERE_API_KEY
if settings.HUGGINGFACE_API_KEY:
    litellm.huggingface_key = settings.HUGGINGFACE_API_KEY

# Azure configuration
if settings.AZURE_API_KEY:
    litellm.azure_key = settings.AZURE_API_KEY
    if settings.AZURE_API_BASE:
        litellm.azure_api_base = settings.AZURE_API_BASE
    if settings.AZURE_API_VERSION:
        litellm.azure_api_version = settings.AZURE_API_VERSION


class LiteLLMService:
    """Service for handling LiteLLM operations"""
    
    def __init__(self):
        self.redis = None
        
    async def initialize(self):
        """Initialize the service"""
        if settings.CACHE_ENABLED:
            self.redis = await get_redis()
    
    def _generate_cache_key(self, model: str, messages: List[Dict], **kwargs) -> str:
        """Generate a cache key for the request"""
        # Create a deterministic hash of the request
        request_data = {
            "model": model,
            "messages": messages,
            **{k: v for k, v in kwargs.items() if k not in ['stream', 'user']}
        }
        request_str = json.dumps(request_data, sort_keys=True)
        return f"litellm:cache:{hashlib.md5(request_str.encode()).hexdigest()}"
    
    async def _get_cached_response(self, cache_key: str) -> Optional[Dict]:
        """Get cached response if available"""
        if not self.redis or not settings.CACHE_ENABLED:
            return None
            
        try:
            cached = await self.redis.get(cache_key)
            if cached:
                logger.info(f"Cache hit for key: {cache_key}")
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Cache retrieval error: {e}")
        
        return None
    
    async def _cache_response(self, cache_key: str, response: Dict):
        """Cache the response"""
        if not self.redis or not settings.CACHE_ENABLED:
            return
            
        try:
            await self.redis.setex(
                cache_key,
                settings.CACHE_TTL,
                json.dumps(response)
            )
            logger.info(f"Response cached with key: {cache_key}")
        except Exception as e:
            logger.warning(f"Cache storage error: {e}")
    
    async def _log_usage(self, model: str, response: Dict, user_id: Optional[str] = None):
        """Log usage statistics"""
        if not settings.COST_TRACKING_ENABLED:
            return
            
        try:
            usage = response.get('usage', {})
            prompt_tokens = usage.get('prompt_tokens', 0)
            completion_tokens = usage.get('completion_tokens', 0)
            total_tokens = usage.get('total_tokens', 0)
            
            # Calculate cost using LiteLLM's cost calculation
            try:
                cost = completion_cost(completion_response=response)
            except Exception as e:
                logger.warning(f"Cost calculation error: {e}")
                cost = 0.0
            
            # TODO: Store usage in database
            # For now, just log it
            logger.info(
                f"Usage logged - Model: {model}, Tokens: {total_tokens}, Cost: ${cost:.6f}",
                extra={
                    "model": model,
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens,
                    "cost_usd": cost,
                    "user_id": user_id
                }
            )
            
        except Exception as e:
            logger.error(f"Usage logging error: {e}")
    
    async def chat_completion(
        self,
        model: str,
        messages: List[Dict],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[List[str]] = None,
        stream: bool = False,
        user: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a chat completion using LiteLLM
        """
        start_time = time.time()
        
        # Prepare parameters
        params = {
            "model": model,
            "messages": messages,
            "stream": stream
        }
        
        # Add optional parameters if provided
        if temperature is not None:
            params["temperature"] = temperature
        if max_tokens is not None:
            params["max_tokens"] = max_tokens
        if top_p is not None:
            params["top_p"] = top_p
        if frequency_penalty is not None:
            params["frequency_penalty"] = frequency_penalty
        if presence_penalty is not None:
            params["presence_penalty"] = presence_penalty
        if stop is not None:
            params["stop"] = stop
        if user is not None:
            params["user"] = user
        
        # Add any additional kwargs
        params.update(kwargs)
        
        logger.info(f"Chat completion request: model={model}, messages={len(messages)}")
        
        try:
            # Check cache first (only for non-streaming requests)
            if not stream and settings.CACHE_ENABLED:
                cache_key = self._generate_cache_key(model, messages, **params)
                cached_response = await self._get_cached_response(cache_key)
                if cached_response:
                    await self._log_usage(model, cached_response, user)
                    return cached_response
            
            # Make the LiteLLM request
            if stream:
                # For streaming, we'll return the generator
                response = await acompletion(**params)
            else:
                response = await acompletion(**params)
                
                # Convert response to dict for consistency
                response_dict = response.model_dump() if hasattr(response, 'model_dump') else dict(response)
                
                # Cache the response
                if settings.CACHE_ENABLED:
                    await self._cache_response(cache_key, response_dict)
                
                # Log usage
                await self._log_usage(model, response_dict, user)
                
                duration = time.time() - start_time
                logger.info(f"Chat completion successful: {duration:.2f}s")
                
                return response_dict
                
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Chat completion error after {duration:.2f}s: {e}")
            
            # Map common LiteLLM errors to HTTP errors
            if "rate limit" in str(e).lower():
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            elif "invalid api key" in str(e).lower():
                raise HTTPException(status_code=401, detail="Invalid API key")
            elif "model not found" in str(e).lower():
                raise HTTPException(status_code=404, detail=f"Model '{model}' not found")
            elif "insufficient quota" in str(e).lower():
                raise HTTPException(status_code=402, detail="Insufficient quota")
            else:
                raise HTTPException(status_code=500, detail=f"LLM service error: {str(e)}")
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models"""
        try:
            # LiteLLM doesn't have a direct way to get all models
            # So we'll return a curated list of popular models
            models = [
                # OpenAI models
                {"id": "gpt-4", "object": "model", "provider": "openai"},
                {"id": "gpt-4-turbo", "object": "model", "provider": "openai"},
                {"id": "gpt-3.5-turbo", "object": "model", "provider": "openai"},
                {"id": "gpt-3.5-turbo-16k", "object": "model", "provider": "openai"},
                
                # Anthropic models
                {"id": "claude-3-opus-20240229", "object": "model", "provider": "anthropic"},
                {"id": "claude-3-sonnet-20240229", "object": "model", "provider": "anthropic"},
                {"id": "claude-3-haiku-20240307", "object": "model", "provider": "anthropic"},
                
                # Google models
                {"id": "gemini-pro", "object": "model", "provider": "google"},
                {"id": "gemini-pro-vision", "object": "model", "provider": "google"},
                
                # Cohere models
                {"id": "command", "object": "model", "provider": "cohere"},
                {"id": "command-light", "object": "model", "provider": "cohere"},
            ]
            
            # Filter models based on available API keys
            available_models = []
            for model in models:
                provider = model["provider"]
                if (
                    (provider == "openai" and settings.OPENAI_API_KEY) or
                    (provider == "anthropic" and settings.ANTHROPIC_API_KEY) or
                    (provider == "google" and settings.GOOGLE_API_KEY) or
                    (provider == "cohere" and settings.COHERE_API_KEY)
                ):
                    available_models.append(model)
            
            logger.info(f"Available models: {len(available_models)}")
            return available_models
            
        except Exception as e:
            logger.error(f"Error getting available models: {e}")
            raise HTTPException(status_code=500, detail="Error retrieving available models")
    
    def get_model_for_task(self, task: str) -> str:
        """Get the optimal model for a specific task"""
        task_models = {
            "support": settings.SUPPORT_DEFAULT_MODEL,
            "classification": settings.CLASSIFICATION_MODEL,
            "general": settings.DEFAULT_MODEL
        }
        
        return task_models.get(task, settings.DEFAULT_MODEL)


# Global service instance
litellm_service = LiteLLMService()


async def get_litellm_service() -> LiteLLMService:
    """Dependency to get LiteLLM service"""
    if litellm_service.redis is None:
        await litellm_service.initialize()
    return litellm_service
