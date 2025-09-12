"""
Chat completion endpoints (OpenAI-compatible)
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
import logging
import time

from src.services.litellm_service import get_litellm_service, LiteLLMService

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatMessage(BaseModel):
    """Chat message model"""
    role: str = Field(..., description="Message role: system, user, or assistant")
    content: str = Field(..., description="Message content")
    name: Optional[str] = Field(None, description="Optional name for the message")


class ChatCompletionRequest(BaseModel):
    """Chat completion request model"""
    model: str = Field(..., description="Model to use for completion")
    messages: List[ChatMessage] = Field(..., description="List of messages")
    temperature: Optional[float] = Field(0.7, ge=0, le=2, description="Sampling temperature")
    max_tokens: Optional[int] = Field(None, ge=1, description="Maximum tokens to generate")
    top_p: Optional[float] = Field(1.0, ge=0, le=1, description="Nucleus sampling parameter")
    frequency_penalty: Optional[float] = Field(0, ge=-2, le=2, description="Frequency penalty")
    presence_penalty: Optional[float] = Field(0, ge=-2, le=2, description="Presence penalty")
    stop: Optional[Union[str, List[str]]] = Field(None, description="Stop sequences")
    stream: Optional[bool] = Field(False, description="Whether to stream responses")
    user: Optional[str] = Field(None, description="User identifier")


class ChatCompletionChoice(BaseModel):
    """Chat completion choice model"""
    index: int
    message: ChatMessage
    finish_reason: str


class ChatCompletionUsage(BaseModel):
    """Chat completion usage model"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionResponse(BaseModel):
    """Chat completion response model"""
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: ChatCompletionUsage


@router.post("/completions", response_model=ChatCompletionResponse)
async def create_chat_completion(
    request: ChatCompletionRequest,
    litellm_service: LiteLLMService = Depends(get_litellm_service)
) -> ChatCompletionResponse:
    """Create a chat completion (OpenAI-compatible endpoint)"""
    logger.info(f"Chat completion request for model: {request.model}")
    
    try:
        # Convert messages to dict format for LiteLLM
        messages = [msg.model_dump() for msg in request.messages]
        
        # Call LiteLLM service
        response = await litellm_service.chat_completion(
            model=request.model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            top_p=request.top_p,
            frequency_penalty=request.frequency_penalty,
            presence_penalty=request.presence_penalty,
            stop=request.stop if isinstance(request.stop, list) else [request.stop] if request.stop else None,
            stream=request.stream,
            user=request.user
        )
        
        # Convert response to our response model
        choices = []
        for choice in response.get('choices', []):
            message_data = choice.get('message', {})
            choices.append(ChatCompletionChoice(
                index=choice.get('index', 0),
                message=ChatMessage(
                    role=message_data.get('role', 'assistant'),
                    content=message_data.get('content', ''),
                    name=message_data.get('name')
                ),
                finish_reason=choice.get('finish_reason', 'stop')
            ))
        
        usage_data = response.get('usage', {})
        usage = ChatCompletionUsage(
            prompt_tokens=usage_data.get('prompt_tokens', 0),
            completion_tokens=usage_data.get('completion_tokens', 0),
            total_tokens=usage_data.get('total_tokens', 0)
        )
        
        completion_response = ChatCompletionResponse(
            id=response.get('id', f"chatcmpl-{int(time.time())}"),
            created=response.get('created', int(time.time())),
            model=response.get('model', request.model),
            choices=choices,
            usage=usage
        )
        
        logger.info(f"Chat completion successful: {completion_response.id}")
        return completion_response
        
    except HTTPException:
        # Re-raise HTTP exceptions from the service
        raise
    except Exception as e:
        logger.error(f"Chat completion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

