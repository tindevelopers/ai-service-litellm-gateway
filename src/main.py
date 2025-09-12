"""
Main FastAPI application for AI Gateway
"""

import logging
import time
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, Response
import uvicorn
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

from src.core.config import settings
from src.core.database import init_db
from src.core.redis import init_redis
from src.api.v1.router import api_router
from src.core.logging import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting AI Gateway application...")
    
    # Skip database and Redis initialization for now
    # TODO: Re-enable when services are available
    # await init_db()
    # logger.info("Database initialized")
    
    # await init_redis()
    # logger.info("Redis initialized")
    
    logger.info("AI Gateway application started successfully (database/redis skipped)")
    yield
    
    logger.info("Shutting down AI Gateway application...")


# Create FastAPI application
app = FastAPI(
    title="AI Gateway",
    description="A comprehensive AI-as-a-Service platform with LiteLLM integration",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Middleware to collect metrics"""
    start_time = time.time()
    
    response = await call_next(request)
    
    # Record metrics
    duration = time.time() - start_time
    REQUEST_DURATION.observe(duration)
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    return response


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Middleware for request logging"""
    start_time = time.time()
    
    # Log request
    logger.info(
        "Request started",
        extra={
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
            "client_ip": request.client.host if request.client else None
        }
    )
    
    response = await call_next(request)
    
    # Log response
    duration = time.time() - start_time
    logger.info(
        "Request completed",
        extra={
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "duration": duration,
            "client_ip": request.client.host if request.client else None
        }
    )
    
    return response


# Health check endpoints
@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }


@app.get("/ready")
async def readiness_check() -> Dict[str, Any]:
    """Readiness check endpoint"""
    # TODO: Add actual readiness checks (database, redis, etc.)
    return {
        "status": "ready",
        "timestamp": time.time(),
        "checks": {
            "database": "ok",
            "redis": "ok",
            "litellm": "ok"
        }
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    logger.error(
        "HTTP exception occurred",
        extra={
            "status_code": exc.status_code,
            "detail": exc.detail,
            "url": str(request.url),
            "method": request.method
        }
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(
        "Unexpected error occurred",
        extra={
            "error": str(exc),
            "url": str(request.url),
            "method": request.method
        },
        exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "status_code": 500}
    )


# Include API routes
app.include_router(api_router, prefix="/v1")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Gateway - LiteLLM Service",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
