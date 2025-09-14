"""
Main API router for v1 endpoints
"""

from fastapi import APIRouter

from src.api.v1.endpoints import chat, models, auth, support

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(models.router, prefix="/models", tags=["models"])
api_router.include_router(support.router, prefix="/support", tags=["support"])

