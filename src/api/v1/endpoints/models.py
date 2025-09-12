"""
Models endpoint for listing available LLM models
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Dict, Any
import logging
import time

from src.services.litellm_service import get_litellm_service, LiteLLMService

logger = logging.getLogger(__name__)

router = APIRouter()


class ModelInfo(BaseModel):
    """Model information model"""
    id: str
    object: str = "model"
    created: int
    owned_by: str
    permission: List[Dict[str, Any]] = []


class ModelsResponse(BaseModel):
    """Models list response model"""
    object: str = "list"
    data: List[ModelInfo]


@router.get("", response_model=ModelsResponse)
async def list_models(
    litellm_service: LiteLLMService = Depends(get_litellm_service)
) -> ModelsResponse:
    """List available models (OpenAI-compatible endpoint)"""
    logger.info("Models list request")
    
    try:
        # Get available models from LiteLLM service
        available_models = await litellm_service.get_available_models()
        
        # Convert to OpenAI-compatible format
        models = []
        for model in available_models:
            models.append(ModelInfo(
                id=model["id"],
                created=int(time.time()),
                owned_by=model.get("provider", "unknown")
            ))
        
        logger.info(f"Returning {len(models)} available models")
        return ModelsResponse(data=models)
        
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        # Fallback to a basic list if there's an error
        fallback_models = [
            ModelInfo(
                id="gpt-3.5-turbo",
                created=int(time.time()),
                owned_by="openai"
            )
        ]
        return ModelsResponse(data=fallback_models)

